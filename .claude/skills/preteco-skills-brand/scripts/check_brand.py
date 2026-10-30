"""QA de marca Preteco para .docx y .pdf generados.

Uso:  python check_brand.py salida.docx [otra.pdf ...]
Sale con código 1 si hay algún FAIL. Los WARN son para revisar a mano.

Checks (brand-spec.md):
  .docx — sin portada (el primer párrafo con texto es Heading 1; Title/Subtitle no se usan),
          solo estilos nativos permitidos, colores dentro de la paleta, fuentes permitidas,
          banda de header presente, títulos simulados con negrita en lugar de Heading.
  .pdf  — fuentes embebidas y permitidas, colores de texto en paleta, sin bloque de
          portada (texto ≥ 20 pt), banda de header en todas las páginas.
"""
import re
import sys
import zipfile
from pathlib import Path

PALETTE = {
    # Escala primaria (web)
    "FAFFE5", "F5FFCC", "EBFF99", "E0FF66", "D6FF33", "CBFF00", "A3CC00", "7A9900",
    "526600", "293300", "141900",
    # Documento
    "263000", "334000", "EAF2C2", "F3F7DE", "B9C98A", "FFFFFF",
}
FONTS = {"Titillium Web", "DM Mono", "Arial"}
PDF_FONT_PREFIXES = ("TitilliumWeb", "Titillium Web", "DMMono", "DM Mono", "Arial")
STYLES_OK = {
    "Normal", "Heading1", "Heading2", "Heading3", "ListBullet", "ListBullet2", "ListNumber",
    "ListNumber2", "Caption", "IntenseQuote", "HTMLPreformatted", "TOCHeading", "TOC1", "TOC2",
    "TableGrid", "Header", "Footer", "Hyperlink", "ListParagraph",
}
STYLES_FORBIDDEN = {"Title", "Subtitle"}


class Report:
    def __init__(self, path):
        self.path, self.fails, self.warns = path, [], []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def print(self):
        status = "FAIL" if self.fails else "OK"
        print(f"\n[{status}] {self.path}")
        for m in self.fails:
            print(f"  FAIL  {m}")
        for m in self.warns:
            print(f"  WARN  {m}")
        if not self.fails and not self.warns:
            print("  Todos los checks pasaron.")


def check_docx(path: Path) -> Report:
    rep = Report(path)
    z = zipfile.ZipFile(path)
    doc = z.read("word/document.xml").decode("utf-8")
    body = doc[doc.find("<w:body>"):]

    # 1. Sin portada: primer párrafo con texto = Heading 1
    paras = re.findall(r"<w:p[ >].*?</w:p>", body, re.S)
    first = None
    for p in paras:
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
        if text:
            first = (p, text)
            break
    if first is None:
        rep.fail("El documento no tiene texto.")
    else:
        m = re.search(r'<w:pStyle w:val="([^"]+)"', first[0])
        style = m.group(1) if m else "Normal"
        if style != "Heading1":
            rep.fail(f"Sin portada: el documento debe arrancar con Heading 1; arranca con "
                     f"{style!r}: {first[1][:60]!r}")

    # 2. Estilos
    used = set(re.findall(r'<w:(?:pStyle|rStyle|tblStyle) w:val="([^"]+)"', body))
    for s in sorted(used & STYLES_FORBIDDEN):
        rep.fail(f"Estilo {s!r} no se usa (no hay portada).")
    for s in sorted(used - STYLES_OK - STYLES_FORBIDDEN):
        rep.warn(f"Estilo {s!r} fuera de la lista esperada (¿estilo custom?).")

    # 3. Colores (texto, rellenos, bordes) en document, header y footer
    parts = [n for n in z.namelist() if re.match(r"word/(document|header\d*|footer\d*)\.xml$", n)]
    bad = {}
    for n in parts:
        xml = z.read(n).decode("utf-8")
        for attr in ("w:val", "w:fill", "w:color"):
            for tag, val in re.findall(rf"<w:(color|shd|top|left|bottom|right|insideH|insideV)\b[^>]*{attr}=\"([0-9A-Fa-f]{{6}})\"", xml):
                v = val.upper()
                if v not in PALETTE:
                    bad.setdefault(v, set()).add(f"{n}:{tag}")
    for v, where in sorted(bad.items()):
        rep.fail(f"Color fuera de paleta #{v} en {', '.join(sorted(where))[:120]}")

    # 4. Fuentes declaradas en runs
    fonts = set(re.findall(r'<w:rFonts [^>]*w:ascii="([^"]+)"', body))
    for f in sorted(fonts - FONTS):
        rep.fail(f"Fuente no permitida {f!r} (usar Titillium Web; código: DM Mono).")

    # 5. Header con banda
    headers = [n for n in z.namelist() if re.match(r"word/header\d*\.xml$", n)]
    if not any("<wp:anchor" in z.read(n).decode("utf-8") for n in headers):
        rep.fail("Falta la banda de header (el documento no parte de template.dotx).")

    # 6. Títulos simulados: párrafo Normal corto, todo en negrita (fuera de tablas)
    body_no_tables = re.sub(r"<w:tbl>.*?</w:tbl>", "", body, flags=re.S)
    for p in re.findall(r"<w:p[ >].*?</w:p>", body_no_tables, re.S):
        if "<w:pStyle" in p or "<w:numPr>" in p:
            continue
        runs = re.findall(r"<w:r>(.*?)</w:r>|<w:r [^>]*>(.*?)</w:r>", p, re.S)
        texts = [(a or b) for a, b in runs]
        text = "".join("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", t)) for t in texts).strip()
        if 0 < len(text) < 80 and texts and all("<w:b/>" in t for t in texts if "<w:t" in t):
            rep.warn(f"¿Título simulado con negrita? Usar Heading 1-3: {text[:60]!r}")

    # 7. Párrafos vacíos consecutivos (espaciado manual)
    empties = 0
    for p in paras:
        has_text = re.search(r"<w:t[^>]*>[^<]+</w:t>", p) or "<w:drawing" in p or "fldChar" in p
        empties = 0 if has_text else empties + 1
        if empties == 2:
            rep.warn("Hay párrafos vacíos consecutivos: el espaciado lo dan los estilos.")
            break
    return rep


def check_pdf(path: Path) -> Report:
    import pymupdf

    rep = Report(path)
    d = pymupdf.open(path)
    fonts = {}
    for page in d:
        for f in page.get_fonts(full=True):
            fonts[f[3].split("+")[-1]] = f[1]  # nombre -> ext ("n/a" = no embebida)
    for name, ext in sorted(fonts.items()):
        if ext == "n/a":
            rep.fail(f"Fuente no embebida: {name}")
        if not name.startswith(PDF_FONT_PREFIXES):
            rep.fail(f"Fuente no permitida: {name}")
    bad, big = {}, []
    for page in d:
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    if not s["text"].strip():
                        continue
                    c = f"{s['color']:06X}"
                    if c not in PALETTE:
                        bad.setdefault(c, s["text"].strip()[:30])
                    if s["size"] >= 20:
                        big.append((page.number + 1, round(s["size"], 1), s["text"].strip()[:40]))
        imgs = [r for img in page.get_images(full=True) for r in page.get_image_rects(img[0])]
        if not any(r.y0 <= 1 and r.width >= 0.9 * page.rect.width for r in imgs):
            rep.fail(f"Página {page.number + 1}: falta la banda de header a sangre.")
    for c, sample in sorted(bad.items()):
        rep.fail(f"Color de texto fuera de paleta #{c}: {sample!r}")
    for pg, size, text in big[:3]:
        rep.fail(f"Texto de {size} pt en pág. {pg} ({text!r}): parece un bloque de portada; no se usa.")
    return rep


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    reports = []
    for a in argv:
        p = Path(a)
        if p.suffix.lower() == ".docx":
            reports.append(check_docx(p))
        elif p.suffix.lower() == ".pdf":
            reports.append(check_pdf(p))
        else:
            print(f"Ignorado (solo .docx/.pdf): {p}")
    for r in reports:
        r.print()
    return 1 if any(r.fails for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
