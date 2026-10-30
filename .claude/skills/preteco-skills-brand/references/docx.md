# Word (.docx) — reglas operativas

Valores de origen: `brand-spec.md`. Este archivo dice **cómo** aplicarlos.

## 1. Partir siempre del template

```python
import sys
sys.path.insert(0, "<SKILL_DIR>/scripts")   # carpeta que contiene este SKILL.md
from preteco_docx import (new_document, add_table, add_ficha, add_callout,
                          add_code, add_caption, add_toc, restart_numbering)

doc = new_document()          # abre assets/template.dotx y vacía el cuerpo
doc.add_heading("1. Resumen ejecutivo", level=1)
doc.add_paragraph("…")
doc.save("propuesta.docx")   # en la carpeta de salida del entorno
```

- `new_document()` es obligatorio. **Nunca** `Document()` vacío: sin el template no hay bandas,
  fuentes embebidas, color de página ni estilos de marca.
- El template ya trae página Letter, márgenes, color de página `#FAFFE5`, header y footer con bandas,
  número de página, fuentes embebidas (Titillium Web, DM Mono) y colores del tema. **No** los
  redefinas por código.
- Requiere `python-docx`. Si no está instalado: `pip install python-docx`.

## 2. Sin portada

- La **primera línea del documento es un Heading 1**. No hay Title, Subtitle, página de portada,
  logo agrandado ni bloque de datos al inicio. La portada se maneja por fuera.
- Si el usuario pide datos del proyecto (cliente, fecha, versión), van en una `add_ficha(...)`
  **después** del primer Heading 1, como parte del contenido.

## 3. Mapeo de niveles a estilos nativos

| Contenido | Llamada | Estilo nativo |
| --- | --- | --- |
| Título de sección | `doc.add_heading(t, level=1)` | Heading 1 (15 pt, regla lima) |
| Subsección | `doc.add_heading(t, level=2)` | Heading 2 (12,5 pt, `#334000`) |
| Sub-subsección | `doc.add_heading(t, level=3)` | Heading 3 (11 pt) |
| Párrafo | `doc.add_paragraph(t)` | Normal |
| Viñeta | `doc.add_paragraph(t, style="List Bullet")` | List Bullet (`•` `#334000`) |
| Viñeta de 2º nivel | `style="List Bullet 2"` | List Bullet 2 (`–`) |
| Lista numerada | `style="List Number"` | List Number |
| Callout | `add_callout(doc, texto, label="Importante")` | Intense Quote |
| Código | `add_code(doc, codigo)` | HTML Preformatted (DM Mono 9 pt) |
| Epígrafe | `add_caption(doc, "Tabla" \| "Figura", texto)` | Caption, con numeración SEQ |
| Índice | `add_toc(doc)` | TOC Heading + campo TOC |

Prohibido:
- Simular títulos con negrita o tamaño en un párrafo Normal.
- Crear estilos nuevos o renombrar estilos.
- Cambiar fuente, color o tamaño con formato directo (`run.font.color`, `run.font.size`, `run.font.name`).
  Las únicas excepciones son la negrita inline y las que aplican los helpers.
- Usar párrafos vacíos para separar: el espaciado sale de los estilos.
- Insertar saltos de página manuales para "acomodar". Solo se permiten si el usuario los pide.

## 4. Redacción y numeración

- Los Heading 1 llevan número en el texto ("1. Resumen ejecutivo", "2. …"), como en el documento de referencia.
  Los Heading 2 y 3 van sin número.
- Viñetas: empezar con una **frase clave en negrita** seguida de dos puntos y texto regular:
  ```python
  p = doc.add_paragraph(style="List Bullet")
  p.add_run("Plazo:").bold = True
  p.add_run(" 8 semanas hasta producción.")
  ```
- Cada lista numerada nueva reinicia en 1: llamar `restart_numbering(doc, primer_parrafo)` en su primer ítem
  (python-docx continúa la numeración de la lista anterior si no).

## 5. Tablas

| Necesidad | Helper | Resultado |
| --- | --- | --- |
| Datos tabulares (N columnas) | `add_table(doc, header, rows, widths_cm=[...])` | Header `#334000` con texto lima Bold; 1ª columna Bold; filas alternadas `#FFFFFF` / `#F3F7DE` |
| Pares etiqueta / valor | `add_ficha(doc, "Título", [(etiqueta, valor), ...])` | Header combinado centrado en MAYÚSCULAS; etiqueta `#EAF2C2` Bold (36% del ancho); valor blanco |

- Ancho total = **15,59 cm**. `widths_cm` tiene que sumar 15,59. La columna más larga va con texto descriptivo.
- Bordes de 0,5 pt `#B9C98A`, alto mínimo de fila 0,7 cm y texto de 10 pt: los pone el estilo, no se tocan.
- Las filas no se parten y el header se repite en cada página. Las tablas que entran en una página se
  mantienen enteras. Si una tabla ocupa más de una página, usar `keep_together=False`.
- Las tablas citadas en el texto llevan `add_caption(doc, "Tabla", "…")` **debajo**.
- Nada de tablas para maquetar (columnas de texto, cajas). Para destacar algo, `add_callout`.

## 6. Figuras, diagramas y gráficos

- Insertar a ancho útil: `doc.add_picture(ruta, width=Cm(15.59))`, centrar el párrafo y agregar
  `add_caption(doc, "Figura", "…")` debajo.
- **Diagramas:**
  - Fondo `#FAFFE5`.
  - Nodo principal con relleno `#334000`, borde 1,5 pt `#CBFF00` y texto lima.
  - Nodos secundarios con relleno blanco, borde `#B9C98A` y texto `#263000`.
  - Flechas en `#334000`.
  - Fuente Titillium Web (archivos en `assets/fonts/`).
  - Texto de al menos 8 pt **al tamaño final** en la página.
- **Gráficos** (matplotlib → PNG a 200 dpi), sobre fondo claro:
  - Series en este orden: `#334000`, `#7A9900`, `#526600`.
  - **Máximo 3 series**; el resto se agrupa en "Otros" con `#B9C98A`.
  - `#A3CC00` y `#CBFF00` nunca van como serie sobre fondo claro.
  - Ejes y grilla en `#B9C98A`; etiquetas en `#263000` con Titillium Web.
  - Fondo de la figura `#FAFFE5`. Para registrar la fuente:
  ```python
  from matplotlib import font_manager, rcParams
  for f in ("TitilliumWeb-Regular.ttf", "TitilliumWeb-Bold.ttf"):
      font_manager.fontManager.addfont(f"<SKILL_DIR>/assets/fonts/{f}")
  rcParams.update({"font.family": "Titillium Web", "axes.edgecolor": "#B9C98A",
                   "axes.labelcolor": "#263000", "xtick.color": "#263000", "ytick.color": "#263000",
                   "axes.prop_cycle": __import__("cycler").cycler(color=["#334000", "#7A9900", "#526600"]),
                   "figure.facecolor": "#FAFFE5", "axes.facecolor": "#FAFFE5", "grid.color": "#B9C98A"})
  ```

## 7. Índice

- Solo si el documento supera las **6 páginas** o tiene **más de 5 Heading 1**.
- `add_toc(doc)` va **al principio**. Es la única excepción a "primera línea = Heading 1": el título
  "Índice" usa TOC Heading, que se ve igual que un H1.
- El campo está marcado como pendiente de actualizar: Word lo regenera al abrir el documento.
- Para PDF, convertir **siempre** con `scripts/docx_to_pdf.py`: `soffice --convert-to pdf` deja el
  texto de relleno en lugar de las entradas del índice.

## 8. Antes de entregar

1. Ejecutar `python <SKILL_DIR>/scripts/check_brand.py salida.docx` y corregir todo **FAIL**.
2. Si hay LibreOffice disponible, renderizar y mirar al menos la primera página:
   `python3 <SKILL_DIR>/scripts/docx_to_pdf.py salida.docx` y después `pdftoppm -r 60 -png -f 1 -l 1 salida.pdf pagina`.
   Comparar contra `examples/`.
