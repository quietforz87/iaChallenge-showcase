---
name: preteco-skills-brand
description: Marca Preteco para Word, PDF y HTML. Usar SOLO si el usuario la pide explícitamente (marca, estilo o template Preteco, o esta skill por nombre). Nunca activar por defecto.
disable-model-invocation: true
---

# Marca Preteco para .docx, PDF y HTML

## Cuándo aplicar

**Solo por pedido explícito.** Aplicá esta skill únicamente si el usuario:
- pide la marca, el estilo, el formato o el template de Preteco ("con la marca Preteco", "en formato Preteco",
  "usá el template de Preteco"), o
- invoca esta skill por su nombre (`preteco-skills-brand`, `/preteco-skills-brand`).

No la apliques por defecto: un pedido de Word, PDF o HTML sin esa mención se resuelve sin la marca, aunque
el contenido hable de Preteco o de sus clientes.

Si el pedido explícito llega a mitad de una conversación, aplicala a los archivos que se generen a partir de
ese momento y a los que el usuario pida rehacer.

Fuera de alcance: .pptx, .xlsx e imágenes sueltas.

## Reglas globales (no negociables)

1. **Sin portada.** Ningún documento lleva portada, Title o Subtitle. El contenido arranca en la página 1 con un
   Heading 1. La portada se maneja por fuera.
2. **Paleta cerrada.** Solo se usan los hex de la tabla de abajo o de `references/brand-spec.md` §2. No inventes tonos.
3. **Documentos (.docx y PDF):** Titillium Web, que ya va embebida. **HTML:** DM Sans y DM Mono.
4. **Word siempre parte de `assets/template.dotx`**, con estilos nativos (Heading 1-3, List Bullet, etc.).
5. **Nunca** se recolorea, deforma ni redibuja el logo.

## Tokens esenciales

| Uso | Documentos (.docx / PDF) | HTML |
| --- | --- | --- |
| Fondo de página | `#FAFFE5` | `#141900` |
| Texto | `#263000` | `#FAFFE5` |
| Acento de marca | `#CBFF00` (regla del H1, texto del header de tabla) | `#CBFF00` (títulos, bordes dashed) |
| Verde oscuro | `#334000` (H2, header de tabla, viñetas) | `#293300` (cards) |
| Tablas | bordes `#B9C98A`, bandas `#F3F7DE`, etiquetas `#EAF2C2` | bordes `#526600` |
| Gráficos (máx. 3 series) | `#334000`, `#7A9900`, `#526600` | `#CBFF00`, `#7A9900`, `#EBFF99` |
| Fuente | Titillium Web, cuerpo de 10,5 pt (código: DM Mono) | DM Sans (labels y código: DM Mono) |

## Procedimiento por formato

`<SKILL_DIR>` es la carpeta que contiene este archivo.

| Formato | Leer | Herramienta |
| --- | --- | --- |
| **.docx** | `references/docx.md` | `scripts/preteco_docx.py`: `new_document()` + helpers |
| **PDF** | `references/pdf-html.md` § PDF | .docx → `scripts/docx_to_pdf.py`; sin LibreOffice, `scripts/preteco_pdf.py` |
| **HTML** | `references/pdf-html.md` § HTML | `assets/preteco.css` inline + logo SVG inline |

Leé el archivo de referencia del formato **antes** de escribir código. Ante cualquier duda de valores,
la fuente de verdad es `references/brand-spec.md`.

Inicio mínimo para .docx:

```python
import sys; sys.path.insert(0, "<SKILL_DIR>/scripts")
from preteco_docx import new_document, add_table, add_callout, add_caption
doc = new_document()
doc.add_heading("1. Resumen ejecutivo", level=1)
```

## Logo

| Archivo | Uso |
| --- | --- |
| `assets/header-band.png` / `footer-band.png` | Ya están en el template y en `preteco_pdf.py`: **no agregar otro logo** en documentos |
| `assets/logo-lima.svg` / `.png` | Sobre fondos oscuros: barra superior del HTML |
| `assets/logo-oscuro.svg` / `.png` | Sobre fondos claros, solo si el usuario lo pide expresamente |

## QA antes de entregar

1. `python <SKILL_DIR>/scripts/check_brand.py <archivo.docx|archivo.pdf>` y corregir **todo** FAIL.
2. Si hay LibreOffice, renderizar la página 1 a PNG y compararla con `examples/`.
3. Para HTML, revisar a mano:
   - No hay hex fuera de `preteco.css`.
   - El logo está inline.
   - Los bordes son dashed en lima.
   - La única fuente es DM Sans o DM Mono.
