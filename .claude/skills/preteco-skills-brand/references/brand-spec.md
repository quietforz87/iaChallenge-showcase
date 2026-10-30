# Preteco — Brand spec (v3, validado en CHECKPOINT 2 — 2026-10-20)

> Fuentes: `inputs/referencia.pdf` (Word 365 → PDF, 5 págs) y `https://preteco.com/` (CSS compilado
> + chunks Angular con estilos de componentes). La extracción se hizo por código en el workspace de
> construcción de la skill (no se incluye en la skill). Alcance: **.docx, PDF y HTML**.
>
> Origen de cada valor: **[PDF]** / **[WEB]** = leído literalmente por código · **[MEDIDO]** = derivado de
> la geometría del PDF · **[DECIDIDO]** = propuesta aprobada por el usuario el 2026-10-20 ·
> **[NUEVO]** = detalle derivado de tokens existentes, aceptado por el usuario al pasar a Fase 3.

---

## 1. Regla de conflictos

| Aspecto | Manda | Motivo |
| --- | --- | --- |
| Hex de colores | Sitio (CSS) | Valor exacto; el PDF puede venir de CMYK |
| Tipografía de documentos | PDF | Las web fonts pueden no existir en desktop |
| Layout y márgenes | PDF | El sitio no tiene equivalente de página |
| Tablas y callouts | PDF | Es el patrón de documentos vigente |
| HTML y piezas web | Sitio | Son piezas digitales |

Los colores que solo existen en el PDF (RGB, sin token en el CSS) se toman del PDF (§2.2).

---

## 2. Paleta

### 2.1 Escala primaria [WEB] (`:root --colors-primary-*`)

| Token | Hex | Uso |
| --- | --- | --- |
| primary-50 | `#FAFFE5` | Color de página en documentos [DECIDIDO]; texto sobre fondos oscuros en web |
| primary-100 | `#F5FFCC` | Texto secundario sobre oscuro (web) |
| primary-200 | `#EBFF99` | Acentos (web) |
| primary-300 | `#E0FF66` | — |
| primary-400 | `#D6FF33` | — |
| **primary-500** | **`#CBFF00`** | **Lima de marca**: logo sobre oscuro, regla de H1, texto del header de tabla, bordes web |
| primary-600 | `#A3CC00` | — (no se usa en gráficos sobre fondo claro: contraste 1,83:1) |
| primary-700 | `#7A9900` | Serie 2 de gráficos |
| primary-800 | `#526600` | Serie 3 de gráficos; bordes de cards (web) |
| primary-900 | `#293300` | Fondo de cards y modales (web) |
| primary-950 | `#141900` | Fondo del `body` (web) |

Colores web secundarios, solo para componentes HTML: `#9DA83B` (borde de botón) y `#414802` (hover).
Los rojos, azules y grises del CSS vienen de Quill y highlight.js: **no son de marca y no se usan**.

### 2.2 Colores de documento [PDF]

| Token | Hex | Uso |
| --- | --- | --- |
| doc-text | `#263000` | Texto de cuerpo, H1, H3, números de lista |
| doc-dark | `#334000` | Banda del header, H2, header de tabla, viñetas, logo sobre fondo claro, captions |
| doc-page | `#FAFFE5` | Color de página (= primary-50; el PDF tenía `#FBFFE5`) [DECIDIDO] |
| table-label | `#EAF2C2` | Columna de etiquetas en ficha de datos |
| table-band | `#F3F7DE` | Filas alternas; fondo de callouts y código |
| table-border | `#B9C98A` | Bordes de tabla, 0,5 pt; grupo "Otros" en gráficos |
| white | `#FFFFFF` | Celdas de valor y filas no bandeadas |

**Paleta cerrada.** En documentos no se usa ningún color fuera de §2.1 y §2.2.

### 2.3 Orden de colores para gráficos [DECIDIDO — opción B, 2026-10-20]

| Serie | Fondo claro (documentos) | Fondo oscuro (`#141900`, solo HTML) |
| --- | --- | --- |
| 1 | `#334000` | `#CBFF00` |
| 2 | `#7A9900` | `#7A9900` |
| 3 | `#526600` | `#EBFF99` |
| "Otros" | `#B9C98A` | `#526600` |

Reglas:
- Máximo **3 series** por gráfico; si hay más, agrupar en "Otros" con `#B9C98A`.
- Las 3 series sobre fondo claro tienen contraste ≥ 3:1 contra `#FAFFE5` (10,9 · 3,2 · 6,3).
  Limitación conocida, aceptada por el usuario: las series 1 y 3 son tonos cercanos (diferencia 13,3 en el
  validador de paletas; mínimo recomendado 15).
- `#A3CC00` y `#CBFF00` no van como serie sobre fondo claro.
- Ejes y grillas: `#B9C98A`. Etiquetas: Titillium Web (documentos) o DM Sans (HTML), en `#263000`.

---

## 3. Tipografía

### 3.1 Documentos (.docx / PDF)

| Estilo nativo Word | Fuente | Tamaño | Peso | Color | Espaciado |
| --- | --- | --- | --- | --- | --- |
| Title | Titillium Web | 22 pt | Bold | `#263000` | Interlineado sencillo. **No se usa** (§4.1) |
| Subtitle | Titillium Web | 12 pt | Bold | `#334000` | **No se usa** (§4.1) |
| Heading 1 | Titillium Web | 15 pt | Bold | `#263000` | Antes 18 pt, después 6 pt; **borde inferior 1,5 pt `#CBFF00`**, separado 4 pt del texto [MEDIDO] |
| Heading 2 | Titillium Web | 12,5 pt | Bold | `#334000` | Antes 12 pt, después 4 pt [MEDIDO] |
| Heading 3 | Titillium Web | 11 pt | Bold | `#263000` | Antes 12 pt, después 4 pt (tamaño [DECIDIDO]; espaciado copiado de H2 [NUEVO]) |
| Normal | Titillium Web | **10,5 pt** | Regular | `#263000` | Interlineado sencillo; después 8 pt [MEDIDO] |
| List Bullet / List Number | Titillium Web | 10,5 pt | Regular | `#263000` | Sangría francesa 0,635 cm; después 4 pt entre ítems |
| Texto de tabla | Titillium Web | 10 pt | Regular (1ª columna Bold) | `#263000` | Sencillo; después 0 pt |
| Header de tabla | Titillium Web | 10,5 pt | Bold | `#CBFF00` | — |
| Caption | Titillium Web | 9 pt | Regular | `#334000` | "Figura N. …" / "Tabla N. …" [DECIDIDO] |
| Código | DM Mono | 9 pt | Regular | `#263000` | Fondo `#F3F7DE` [DECIDIDO] |
| Cierre destacado | Titillium Web | 11,5 pt | Bold | `#334000` | Para un cierre corto como "¡Éxitos!" |

- **Regla de espaciado (ECMA-376 / Word):** entre dos párrafos se usa el **mayor** valor entre el "después" del primero y el "antes" del segundo; no se suman. Los valores de esta tabla ya tienen eso en cuenta (corrección del 2026-10-20, a partir de la recreación del PDF).
- **Fallback:** Arial [DECIDIDO]. Las fuentes `Titillium Web` y `DM Mono` se declaran con ese nombre exacto.
- **Archivos:** `TitilliumWeb-Regular/Bold/Italic/BoldItalic.ttf` y `DMMono-Regular.ttf` (OFL 1.1, embebibles).
- **Patrón de redacción:** cada bullet empieza con una **frase clave en negrita** y sigue en regular.

### 3.2 Web / HTML [WEB]

| Token CSS | Valor |
| --- | --- |
| `--font-family-dm-sans` | `'DM Sans', sans-serif`: cuerpo y títulos |
| `--font-family-dm-mono` | `'DM Mono', monospace`: labels, badges, botones, código |
| `--font-size-h1 … h7` | 3rem · 2.5rem · 1.75rem · 1.65rem · 1.5rem · 1.25rem · 1.15rem |
| `--font-size-body` / `caption` / `button` | 1.25rem / .8rem / 1rem |
| `--font-weight-regular/semibold/bold` | 400 / 500 / 600 (700 en botones) |
| `--font-line-height-*` | body 150% · h2-h4 120% · h5 130% · h6 150% |

Carga [DECIDIDO]: Google Fonts, `DM Sans:wght@400;500;600;700` y `DM Mono:wght@400;500`.

---

## 4. Layout de documento [PDF / MEDIDO / DECIDIDO]

| Parámetro | Valor |
| --- | --- |
| Tamaño de página | **Letter**, 21,59 × 27,94 cm [DECIDIDO] |
| Color de página | `#FAFFE5` |
| Márgenes | Superior 3,0 cm · inferior 2,5 cm · izquierdo 3,0 cm · derecho 3,0 cm (ancho útil 15,59 cm) |
| Header | Banda a sangre de 1,90 cm de alto, fondo `#334000`, logo lima a la izquierda. Imagen `assets/header-band.png`, anclada en (0,0) y con ancho de página completo. **En todas las páginas** |
| Footer | Banda a sangre de 1,82 cm de alto, fondo `#CBFF00`, con "www.preteco.com" y las ciudades. Imagen `assets/footer-band.png`, anclada al borde inferior y con **ancho de página completo** (corrige el defecto del PDF). **En todas las páginas** |
| Números de página | Campo `PAGE`, alineado a la derecha, sobre la banda del footer [DECIDIDO]; Titillium Web 9 pt `#263000` [NUEVO] |

### 4.1 Portada — **no se genera nunca** [DECIDIDO]

- **Ningún documento lleva portada, ni .docx ni PDF.** La portada se maneja por fuera de la skill.
- El documento arranca directamente en el contenido: la primera línea es un **Heading 1**.
- No hay bloque de apertura: ni Title, ni Subtitle, ni ficha de datos al inicio, ni página de portada, ni logo agrandado.
- Los estilos `Title` y `Subtitle` existen en el template (son nativos) pero **no se usan**.
- El header y el footer de marca **sí** van en todas las páginas, incluida la primera. No son portada.
- Los datos que el PDF de referencia ponía en la ficha de apertura (proceso, fecha, cliente) no se agregan
  por defecto. Si el usuario los pide, van como ficha de datos (§5.1, variante A) dentro del contenido.

---

## 5. Componentes

### 5.1 Tablas [PDF]

Común a todas:
- Ancho = ancho útil, 15,59 cm. Bordes de 0,5 pt `#B9C98A` en todos los lados y entre celdas.
- Padding de celda: 0,18 cm a izquierda y derecha. Alto mínimo de fila: 0,7 cm. Las filas **no se parten** entre páginas (`cantSplit`); la fila de encabezado se repite. Una tabla que entra en una página se mantiene entera (keep-with-next en todas las filas menos la última).
- **Fila de encabezado:** fondo `#334000`, texto Titillium Web Bold 10,5 pt `#CBFF00`, marcada como fila de encabezado repetible.
- Cuerpo: 10 pt `#263000`; primera columna en **Bold**.

**Variante A, ficha de datos** (etiqueta / valor): una fila de encabezado combinada, centrada y en
MAYÚSCULAS. La columna de etiqueta ocupa el 36% del ancho, con fondo `#EAF2C2` y Bold; la de valor va con fondo `#FFFFFF`.

**Variante B, tabla de contenido** (N columnas): encabezado alineado a la izquierda y filas de cuerpo
**alternadas estrictamente**: `#FFFFFF`, `#F3F7DE`, `#FFFFFF`… [DECIDIDO]

Las tablas llevan Caption "Tabla N. …" debajo cuando se citan en el texto.

### 5.2 Listas [DECIDIDO]

- **Viñetas:** `•` en `#334000`, sangría izquierda 0, texto a 0,635 cm. En el segundo nivel: `–` en `#334000`, texto a 1,27 cm [NUEVO].
- **Numeradas:** `1.` en Titillium Web 10,5 pt `#263000` (corrige el defecto del PDF, que usaba 12 pt en negro).
- Separación entre ítems: 4 pt (sin `contextualSpacing`).

### 5.3 Callouts, código, figuras e índice [DECIDIDO]

- **Callout:** estilo nativo **Intense Quote**, con fondo `#F3F7DE`, borde izquierdo de 3 pt `#CBFF00` sobre el margen y
  4 pt de padding vertical. Texto de 10 pt `#263000`; el rótulo opcional ("Nota", "Importante") va en Bold `#334000` [NUEVO].
- **Código:** estilo nativo **HTML Preformatted**, en DM Mono 9 pt sobre fondo `#F3F7DE`, con sangría de 0,18 cm y sin bordes.
- **Figuras:** centradas; Caption "Figura N. …" debajo, 9 pt `#334000`, con numeración automática (campo SEQ).
- **Diagramas** [NUEVO]: fondo `#FAFFE5`. El nodo principal lleva relleno `#334000`, borde de 1,5 pt `#CBFF00` y texto lima;
  los nodos secundarios, relleno `#FFFFFF`, borde `#B9C98A` y texto `#263000` / `#334000`. Flechas en `#334000`.
  Titillium Web, con texto de **al menos 8 pt al tamaño final** dentro del documento. Se inserta a ancho útil con Caption "Figura N.".
- **Índice (TOC):** solo si el documento tiene más de 6 páginas o más de 5 Heading 1. Va al inicio, con el título
  "Índice" en estilo nativo **TOC Heading** (mismo look que H1, pero no entra en el propio índice); campo TOC sobre Heading 1-2.

### 5.4 Web / HTML [WEB]

- Tema oscuro: `body` con fondo `#141900` y texto `#FAFFE5`; acento `#CBFF00`.
- Cards: fondo `#293300`, borde de 1 px **dashed** `#CBFF00`, radio de 12 px, padding de 2.5rem 2rem.
- Botón primario: fondo transparente, borde de 2 px **dashed** `#CBFF00`, texto `#FAFFE5` en DM Sans 16 px peso 700,
  radio de 8 px, padding de 12 × 30 px. En hover pasa a fondo `#CBFF00` con texto `#141900`.
- Badge: fondo `#CBFF00`, texto `#141900`, radio de 12 px, DM Mono.
- Tablas HTML [NUEVO]: header con fondo `#293300` y texto `#CBFF00`; bordes de 1 px `#526600`; filas alternas
  transparente / `rgba(41,51,0,.5)` (= `#293300` al 50%, valor que usa el sitio [WEB]).
- Rasgo distintivo: **bordes dashed en lima**.

---

### 5.5 Implementación en Word (template.dotx)

| Elemento | Estilo nativo |
| --- | --- |
| Cuerpo | Normal (formato en docDefaults, para que los estilos de tabla lo puedan pisar) |
| Títulos | Heading 1 / Heading 2 / Heading 3 |
| Viñetas | List Bullet / List Bullet 2 |
| Numeradas | List Number / List Number 2 |
| Tablas | Table Grid (header, primera columna y bandas como formato condicional; el helper también aplica el relleno por celda) |
| Callout | Intense Quote |
| Código | HTML Preformatted |
| Captions | Caption |
| Índice | TOC Heading + campo TOC |
| Links | Hyperlink, en `#334000` [NUEVO] |
| Número de página | Footer, alineado a la derecha |

- Modo de compatibilidad: Word 2013+ (15).
- Las fuentes Titillium Web (4 estilos) y DM Mono van **embebidas** en el .dotx.
- Los colores del tema replican el orden de gráficos de §2.3 (accent1…accent5, más accent6 = `#CBFF00`), así que un gráfico nativo de Word sale con los colores de la marca.

## 6. Logo

| Variante | Archivo en la skill | Uso |
| --- | --- | --- |
| Lima `#CBFF00` | `assets/logo-lima.svg` / `.png` | Sobre fondos oscuros (`#334000`, `#141900`, `#293300`) |
| Oscuro `#334000` | `assets/logo-oscuro.svg` / `.png` | Sobre fondos claros (`#FAFFE5`, blanco) [usuario] |
| Banda de header | `assets/header-band.png` | Header de .docx y PDF |
| Banda de footer | `assets/footer-band.png` | Footer de .docx y PDF |

- En documentos, el logo aparece **solo** dentro de la banda del header. No se repite en el cuerpo.
- En HTML va el logo lima en la barra superior, sobre `#141900`.
- Proporción 108:27 (4:1). Nunca se deforma, recolorea fuera de estas dos variantes ni se aplica sobre `#CBFF00`.
