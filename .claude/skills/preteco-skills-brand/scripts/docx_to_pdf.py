"""Convierte un .docx de marca a PDF con LibreOffice actualizando índice y campos.

Uso:  python3 docx_to_pdf.py entrada.docx [carpeta_salida]

`soffice --convert-to pdf` NO actualiza el campo TOC: el índice sale con el texto de relleno.
Este script abre el documento por UNO, actualiza índices y campos (TOC, SEQ, PAGE) y exporta.
Si el módulo `uno` no está disponible, cae a `soffice --convert-to pdf` y avisa si hay índice.
Ejecutar con el python del sistema que trae `uno` (en Debian/Ubuntu: paquete python3-uno).
"""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path


def _has_toc(docx: Path) -> bool:
    with zipfile.ZipFile(docx) as z:
        return " TOC " in z.read("word/document.xml").decode("utf-8")


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _plain_convert(docx: Path, outdir: Path) -> Path:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                   check=True, capture_output=True, timeout=300)
    return outdir / (docx.stem + ".pdf")


def _uno_convert(docx: Path, outdir: Path) -> Path:
    import uno
    from com.sun.star.beans import PropertyValue

    def prop(name, value):
        p = PropertyValue()
        p.Name, p.Value = name, value
        return p

    port = _free_port()
    profile = tempfile.mkdtemp(prefix="lo-profile-")
    proc = subprocess.Popen([
        "soffice", "--headless", "--invisible", "--nologo", "--norestore",
        f"-env:UserInstallation=file://{profile}",
        f"--accept=socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        local = uno.getComponentContext()
        resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
        ctx = None
        for _ in range(60):
            try:
                ctx = resolver.resolve(f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext")
                break
            except Exception:
                time.sleep(0.5)
        if ctx is None:
            raise RuntimeError("No se pudo conectar con LibreOffice")
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(docx.resolve())), "_blank", 0,
                                           (prop("Hidden", True),))
        # Dos pasadas: el índice cambia la paginación y los números de página del propio índice
        for _ in range(2):
            idx = doc.getDocumentIndexes()
            for i in range(idx.getCount()):
                idx.getByIndex(i).update()
            doc.getTextFields().refresh()
            doc.refresh()
        out = outdir / (docx.stem + ".pdf")
        doc.storeToURL(uno.systemPathToFileUrl(str(out.resolve())), (prop("FilterName", "writer_pdf_Export"),))
        doc.close(True)
        return out
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


def convert(docx, outdir=None) -> Path:
    docx = Path(docx)
    outdir = Path(outdir) if outdir else docx.parent
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        import uno  # noqa: F401
    except ImportError:
        if _has_toc(docx):
            print("AVISO: sin módulo 'uno' el índice NO se actualiza en el PDF. "
                  "Instalá python3-uno o generá el documento sin índice.", file=sys.stderr)
        return _plain_convert(docx, outdir)
    return _uno_convert(docx, outdir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    print(convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
