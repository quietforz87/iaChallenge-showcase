"""PDF directo con la marca Preteco (reportlab). Usar solo si no hay LibreOffice para convertir un .docx.

Uso:
    import sys; sys.path.insert(0, "<SKILL_DIR>/scripts")
    from preteco_pdf import build_pdf, H1, H2, H3, P, Bullets, Numbered, Table, Ficha, Callout, Code, Figure

    build_pdf("salida.pdf", [
        H1("1. Resumen ejecutivo"),
        P("Texto con <b>negrita</b> inline."),
        Bullets([("Plazo:", " 8 semanas."), "Ítem sin frase clave."]),
        Table(["Fase", "Semanas"], [["Descubrimiento", "1"]], widths_cm=[12.59, 3]),
    ], title="Propuesta")

Replica el template.dotx: Letter, márgenes 3/2,5/3/3 cm, fondo #FAFFE5, bandas de header y footer
a sangre, número de página, Titillium Web embebida. Sin portada: el primer flowable debe ser H1.
"""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, ListFlowable,
                                ListItem, PageTemplate, Paragraph, Preformatted, Spacer)
from reportlab.platypus import Table as RLTable
from reportlab.platypus import TableStyle
from reportlab.platypus.flowables import HRFlowable

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"

DOC_TEXT, DOC_DARK, LIMA = HexColor("#263000"), HexColor("#334000"), HexColor("#CBFF00")
PAGE_BG, LABEL, BAND, BORDER = HexColor("#FAFFE5"), HexColor("#EAF2C2"), HexColor("#F3F7DE"), HexColor("#B9C98A")
WHITE = HexColor("#FFFFFF")
USABLE_W = 15.59 * cm
PAGE_W, PAGE_H = LETTER

_fonts_ok = False


def _register_fonts():
    global _fonts_ok
    if _fonts_ok:
        return
    f = ASSETS / "fonts"
    pdfmetrics.registerFont(TTFont("Titillium", f / "TitilliumWeb-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Titillium-Bold", f / "TitilliumWeb-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Titillium-Italic", f / "TitilliumWeb-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Titillium-BoldItalic", f / "TitilliumWeb-BoldItalic.ttf"))
    pdfmetrics.registerFont(TTFont("DMMono", f / "DMMono-Regular.ttf"))
    pdfmetrics.registerFontFamily("Titillium", normal="Titillium", bold="Titillium-Bold",
                                  italic="Titillium-Italic", boldItalic="Titillium-BoldItalic")
    _fonts_ok = True


# Interlineado "sencillo" de Titillium = 1,521 × tamaño (métrica win del archivo)
def _lead(size):
    return round(size * 1.521, 2)


def _styles():
    _register_fonts()
    base = dict(fontName="Titillium", textColor=DOC_TEXT)
    return {
        "body": ParagraphStyle("body", fontSize=10.5, leading=_lead(10.5), spaceAfter=8, **base),
        "h1": ParagraphStyle("h1", fontName="Titillium-Bold", fontSize=15, leading=_lead(15),
                             textColor=DOC_TEXT, spaceBefore=18, spaceAfter=0),
        "h2": ParagraphStyle("h2", fontName="Titillium-Bold", fontSize=12.5, leading=_lead(12.5),
                             textColor=DOC_DARK, spaceBefore=12, spaceAfter=4),
        "h3": ParagraphStyle("h3", fontName="Titillium-Bold", fontSize=11, leading=_lead(11),
                             textColor=DOC_TEXT, spaceBefore=12, spaceAfter=4),
        "li": ParagraphStyle("li", fontSize=10.5, leading=_lead(10.5), spaceAfter=4, **base),
        "cell": ParagraphStyle("cell", fontSize=10, leading=_lead(10), **base),
        "cell_b": ParagraphStyle("cell_b", fontName="Titillium-Bold", fontSize=10, leading=_lead(10),
                                 textColor=DOC_TEXT),
        "th": ParagraphStyle("th", fontName="Titillium-Bold", fontSize=10.5, leading=_lead(10.5),
                             textColor=LIMA),
        "th_c": ParagraphStyle("th_c", fontName="Titillium-Bold", fontSize=10.5, leading=_lead(10.5),
                               textColor=LIMA, alignment=TA_CENTER),
        "caption": ParagraphStyle("caption", fontSize=9, leading=_lead(9), textColor=DOC_DARK,
                                  spaceBefore=4, spaceAfter=8, fontName="Titillium"),
        "callout": ParagraphStyle("callout", fontSize=10, leading=_lead(10), **base),
        "code": ParagraphStyle("code", fontName="DMMono", fontSize=9, leading=13, textColor=DOC_TEXT),
        "pagenum": ParagraphStyle("pagenum", fontSize=9, textColor=DOC_TEXT, alignment=TA_RIGHT,
                                  fontName="Titillium"),
    }


S = None


def _s():
    global S
    if S is None:
        S = _styles()
    return S


# --- Flowables de marca ------------------------------------------------------
def H1(text):
    """Heading 1: 15 pt Bold #263000 + regla inferior 1,5 pt lima a 4 pt del texto."""
    kt = KeepTogether([Paragraph(text, _s()["h1"]), Spacer(0, 4),
                       HRFlowable(width="100%", thickness=1.5, color=LIMA, spaceBefore=0, spaceAfter=6)])
    kt.keepWithNext = 1  # el título nunca queda solo al pie de página
    return kt


def H2(text):
    p = Paragraph(text, _s()["h2"])
    p.keepWithNext = 1
    return p


def H3(text):
    p = Paragraph(text, _s()["h3"])
    p.keepWithNext = 1
    return p


def P(text):
    return Paragraph(text, _s()["body"])


def _item_para(item):
    if isinstance(item, tuple):
        lead, rest = item
        return Paragraph(f"<b>{lead}</b>{rest}", _s()["li"])
    return Paragraph(item, _s()["li"])


def Bullets(items):
    """items: str o (frase_clave, resto). Viñeta • #334000, sangría francesa 0,635 cm."""
    return ListFlowable([ListItem(_item_para(i), leftIndent=0.635 * cm) for i in items],
                        bulletType="bullet", start="•", bulletColor=DOC_DARK, bulletFontName="Titillium",
                        bulletFontSize=10.5, leftIndent=0.635 * cm, bulletOffsetY=0)


def Numbered(items):
    return ListFlowable([ListItem(_item_para(i), leftIndent=0.635 * cm) for i in items],
                        bulletType="1", bulletFormat="%s.", bulletColor=DOC_TEXT, bulletFontName="Titillium",
                        bulletFontSize=10.5, leftIndent=0.635 * cm)


def _base_table_style():
    st = [
        ("FONTNAME", (0, 0), (-1, -1), "Titillium"),  # celdas de texto plano (p. ej. la vacía del span)
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0.18 * cm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0.18 * cm),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), DOC_DARK),
    ]
    return st


def Table(header, rows, widths_cm=None):
    """Variante B: header #334000/lima, 1ª columna Bold, filas alternadas blanco/#F3F7DE."""
    s = _s()
    n = len(header)
    widths = [w * cm for w in (widths_cm or [15.59 / n] * n)]
    data = [[Paragraph(str(h), s["th"]) for h in header]]
    for r in rows:
        data.append([Paragraph(str(v), s["cell_b"] if i == 0 else s["cell"]) for i, v in enumerate(r)])
    st = _base_table_style()
    for i in range(1, len(data)):
        st.append(("BACKGROUND", (0, i), (-1, i), WHITE if i % 2 == 1 else BAND))
    t = RLTable(data, colWidths=widths, repeatRows=1, minRowHeights=[0.7 * cm] * len(data))
    t.setStyle(TableStyle(st))
    return t


def Ficha(title, pairs, label_ratio=0.36):
    """Variante A: header combinado centrado en MAYÚSCULAS; etiqueta #EAF2C2 Bold; valor blanco."""
    s = _s()
    data = [[Paragraph(title.upper(), s["th_c"]), ""]]
    for k, v in pairs:
        data.append([Paragraph(str(k), s["cell_b"]), Paragraph(str(v), s["cell"])])
    st = _base_table_style() + [
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 1), (0, -1), LABEL),
        ("BACKGROUND", (1, 1), (1, -1), WHITE),
    ]
    t = RLTable(data, colWidths=[USABLE_W * label_ratio, USABLE_W * (1 - label_ratio)], repeatRows=1,
                minRowHeights=[0.7 * cm] * len(data))
    t.setStyle(TableStyle(st))
    return KeepTogether([t, Spacer(0, 8)])


def Callout(text, label=None):
    """Fondo #F3F7DE, borde izquierdo 3 pt lima, padding vertical 4 pt."""
    s = _s()
    body = (f'<font color="#334000"><b>{label}:</b></font> ' if label else "") + text
    t = RLTable([[Paragraph(body, s["callout"])]], colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Titillium"),
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (0, 0), (0, -1), 3, LIMA),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([Spacer(0, 8), t, Spacer(0, 8)])


def Code(code):
    s = _s()
    t = RLTable([[Preformatted(code.rstrip("\n"), s["code"])]], colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DMMono"),
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LEFTPADDING", (0, 0), (-1, -1), 0.18 * cm),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([t, Spacer(0, 8)])


_counters = {}


def Caption(kind, text):
    """kind = 'Figura' o 'Tabla'; numeración automática por tipo."""
    _counters[kind] = _counters.get(kind, 0) + 1
    st = _s()["caption"]
    if kind == "Figura":
        st = ParagraphStyle("caption_c", parent=st, alignment=TA_CENTER)
    return Paragraph(f"{kind} {_counters[kind]}. {text}", st)


def Figure(path, caption=None, width_cm=15.59):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(path)).getSize()
    w = width_cm * cm
    img = Image(str(path), width=w, height=w * ih / iw)
    img.hAlign = "CENTER"
    parts = [img]
    if caption:
        parts.append(Caption("Figura", caption))
    return KeepTogether(parts)


# --- Página ------------------------------------------------------------------
def _decorate(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAGE_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # Banda header: 633,9 x 53,8 pt desde el borde superior izquierdo (sangra a la derecha)
    canvas.drawImage(str(ASSETS / "header-band.png"), 0, PAGE_H - 53.8, width=633.9, height=53.8)
    # Banda footer a ancho completo
    fh = PAGE_W * 143 / 1692
    canvas.drawImage(str(ASSETS / "footer-band.png"), 0, 0, width=PAGE_W, height=fh)
    # Número de página: 9 pt, a la derecha, sobre la banda
    canvas.setFont("Titillium", 9)
    canvas.setFillColor(DOC_TEXT)
    canvas.drawRightString(PAGE_W - 3 * cm, 2.0 * cm, str(doc.page))
    canvas.restoreState()


def build_pdf(path, story, title="", author="Preteco"):
    """Genera el PDF. `story` es una lista de flowables; el primero debe ser H1 (sin portada)."""
    _register_fonts()
    _counters.clear()
    doc = BaseDocTemplate(str(path), pagesize=LETTER, leftMargin=3 * cm, rightMargin=3 * cm,
                          topMargin=3 * cm, bottomMargin=2.5 * cm, title=title, author=author,
                          # Sin esto reportlab declara Helvetica (no embebida) en cada página
                          initialFontName="Titillium", initialFontSize=10.5, initialLeading=_lead(10.5))
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="preteco", frames=[frame], onPage=_decorate)])
    doc.build(story)
    return path
