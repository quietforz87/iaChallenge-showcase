# PDF y HTML — reglas operativas

Valores de origen: `brand-spec.md`. Para Word, ver `docx.md`.

---

## PDF

### Elegir la ruta

| Situación | Ruta |
| --- | --- |
| Hay LibreOffice (`soffice` en el PATH) | **A: .docx → PDF** (preferida) |
| No hay LibreOffice | **B: PDF directo** con `scripts/preteco_pdf.py` (reportlab) |
| El usuario pide editar o rellenar un PDF existente | Fuera del alcance de la marca: no re-maquetar |

Para saber si está: `which soffice`.

### Ruta A — convertir un .docx (preferida)

1. Generar el documento como .docx siguiendo **todas** las reglas de `docx.md` (template, estilos nativos, sin portada).
2. Convertir con el script de la skill, que actualiza índice y campos antes de exportar:
   ```bash
   python3 <SKILL_DIR>/scripts/docx_to_pdf.py documento.docx <carpeta_salida>
   ```
   Usa el python del sistema que trae el módulo `uno` (paquete `python3-uno`). Sin `uno`, cae a
   `soffice --convert-to pdf`, que **no** actualiza el índice. Si el documento tiene índice y el script
   avisa que falta `uno`, generá el documento sin índice.
3. Las fuentes ya van embebidas en el template: el PDF sale con Titillium Web y DM Mono aunque no
   estén instaladas en el sistema. No instales fuentes ni cambies nada en este paso.
4. Si el usuario pidió solo el PDF, entregar solo el PDF.

### Ruta B — PDF directo (sin LibreOffice)

```python
import sys
sys.path.insert(0, "<SKILL_DIR>/scripts")
from preteco_pdf import build_pdf, H1, H2, H3, P, Bullets, Numbered, Table, Ficha, Callout, Code, Caption, Figure

build_pdf("resumen.pdf", [
    H1("1. Resumen"),
    P("Texto con <b>negrita</b> inline."),
    Bullets([("Plazo:", " 8 semanas."), "Ítem sin frase clave."]),
    Table(["Fase", "Semanas"], [["Descubrimiento", "1"]], widths_cm=[12.59, 3]),
    Caption("Tabla", "Esfuerzo por fase."),
], title="Resumen")
```

- Requiere `reportlab` (si falta: `pip install reportlab`).
- Replica el template: Letter, márgenes 3 / 2,5 / 3 / 3 cm, fondo `#FAFFE5`, bandas de header y footer,
  número de página y Titillium Web y DM Mono embebidas desde `assets/fonts/`.
- **Solo** se usan los flowables del helper. No uses `getSampleStyleSheet()` ni fuentes estándar de
  reportlab (Helvetica, Times, Courier): no están embebidas y no son de marca.
- `widths_cm` de `Table` tiene que sumar 15,59.

### Reglas comunes a las dos rutas

- **Sin portada:** el contenido arranca con un H1 en la página 1. No hay texto de 20 pt o más.
- Bandas de header y footer en **todas** las páginas.
- Un PDF de una página ("one-pager", resumen) sigue las mismas reglas: H1 de arranque y cuerpo de
  10,5 pt. Si no entra en una página, recortar texto; no achicar la letra ni los márgenes.
- Verificar antes de entregar:
  ```bash
  python <SKILL_DIR>/scripts/check_brand.py salida.pdf
  ```
  El check exige fuentes embebidas y permitidas, colores en paleta, banda de header en cada página y
  que no haya bloque de portada.

---

## HTML

Las piezas web siguen el **sitio** (preteco.com): tema oscuro, DM Sans y DM Mono, y bordes punteados en lima.
No usan Titillium Web ni el layout de documento.

### Base obligatoria

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>…</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>/* pegar acá el contenido completo de assets/preteco.css */</style>
</head>
<body>
  <nav class="pt-nav"><!-- SVG inline de assets/logo-lima.svg --></nav>
  <main class="pt-container">…</main>
  <footer class="pt-footer"><span>www.preteco.com</span><span>Buenos Aires | Córdoba | Montevideo | La Paz | Santa Cruz de la Sierra | Bogotá</span></footer>
</body>
</html>
```

- Pegar `assets/preteco.css` **inline**, completo y sin modificar los tokens. Agregar reglas propias
  solo debajo y usando `var(--colors-primary-*)`. **Ningún hex** fuera de los de ese archivo.
- El logo va **inline** como SVG, copiado de `assets/logo-lima.svg`. Altura de 27 px, sobre fondo oscuro.
  No usar el logo oscuro en HTML salvo en una sección de fondo claro.

### Tokens y componentes (clases de `preteco.css`)

| Elemento | Regla |
| --- | --- |
| Fondo de página | `--colors-primary-950` `#141900` |
| Texto | `--colors-primary-50` `#FAFFE5` |
| Títulos h1-h3 | `--colors-primary-500` `#CBFF00`, DM Sans |
| Labels, badges, código | DM Mono |
| Card | `.pt-card`: fondo `#293300`, borde 1 px **dashed** lima, radio 12 px |
| Botón primario | `.pt-button`: transparente, borde 2 px **dashed** lima, hover con fondo lima y texto `#141900` |
| Badge | `.pt-badge`: fondo lima, texto `#141900`, DM Mono |
| Tabla | `.pt-table`: header `#293300` con texto lima, bordes `#526600`, filas pares `rgba(41,51,0,.5)` |
| Callout | `.pt-callout`: fondo `#293300`, borde izquierdo 3 px lima |
| Código | `pre.pt-code` |
| Footer | `.pt-footer`: fondo lima, texto `#141900` |

- El rasgo distintivo de la marca son los **bordes dashed en lima**. No reemplazarlos por sombras ni gradientes.
- Prohibido: gradientes, sombras de color, otros acentos (azul, violeta, rojo), fuentes que no sean DM Sans o DM Mono,
  y lima como fondo de bloques grandes de texto (solo footer, badges y hover).

### Gráficos en HTML

- Sobre fondo oscuro, series en este orden: `var(--chart-1)` … `var(--chart-5)`, es decir
  `#CBFF00`, `#7A9900`, `#EBFF99`, `#526600`, `#F5FFCC`.
- **Máximo 3 series.** Grilla `var(--chart-grid)`; etiquetas en DM Sans `#FAFFE5`.
- Con librerías (Chart.js, Recharts, etc.), pasar los hex explícitos en ese orden.

### HTML que se va a imprimir o exportar a PDF

- Si el destino final es un **documento** (informe, propuesta), no hacer HTML: seguir la ruta de PDF de arriba.
- El HTML con tema oscuro es para pantalla (landings, one-pagers web, dashboards, artifacts).
