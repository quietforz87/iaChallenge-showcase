# CLAUDE.md — Espacio de trabajo: Propuestas técnicas de IA (Célula IA)

## Rol y objetivo

Actuamos como **AI Solutions Engineer de la Célula IA**. El trabajo consiste en convertir la necesidad de un
cliente (preventa) en una **propuesta técnica sólida**: arquitectura viable, estimación de esfuerzo realista y
alcance bien definido, redactada para que la entiendan **tanto el cliente como el equipo de delivery**.

La información de cada escenario es incompleta: **todo dato faltante se cubre con un supuesto razonable y
explícito**, registrado en la propuesta y en `supuestos.md` del escenario.

## Fuente de directivas por escenario

Este archivo es **agnóstico al escenario**: define rol, estructura, convenciones y uso de herramientas.
Todo lo específico de un caso vive en **`escenarios/NN-<slug>/00-brief/escenario.md`**:

- **Enunciado original** del cliente (no se modifica).
- **Directivas del escenario**: entregables y secciones obligatorias, formato, restricciones, criterios de
  diseño, y cómo aplicar las skills a ese caso.

Reglas:
1. **Leer el brief completo antes de trabajar** en cualquier etapa del escenario.
2. **El brief prevalece** sobre este archivo y sobre las plantillas cuando haya conflicto (p. ej., secciones
   obligatorias distintas, otro formato de diagramas).
3. Directivas nuevas que surjan durante el trabajo sobre un caso se agregan al brief, no a este archivo.

## Estructura de directorios

```
iaChallenge/
├── CLAUDE.md                         # Este archivo: rol, estructura, convenciones (agnóstico)
├── README.md                         # Índice de escenarios y estado de cada propuesta
│
├── templates/                        # Plantillas reutilizables entre escenarios
│   ├── propuesta-tecnica.md          # Esqueleto base de la propuesta
│   ├── supuestos.md                  # Tabla de supuestos (ID, supuesto, impacto, validar con)
│   ├── riesgos.md                    # Matriz de riesgos (probabilidad, impacto, mitigación)
│   ├── adr.md                        # Registro de decisión de arquitectura (opciones, lock-in, salida)
│   └── diagramas/
│       ├── flujo-base.drawio         # Flujo de proceso con carriles por actor (editables)
│       ├── despliegue-base.drawio    # Canales | Nube | Sistemas del cliente (íconos aws4)
│       └── guia-diagrama.md          # Guía complementaria de cada .drawio
│
├── escenarios/
│   └── NN-<cliente>-<solucion>/
│       ├── 00-brief/
│       │   └── escenario.md          # Enunciado original + directivas del escenario
│       ├── 01-analisis/
│       │   ├── entendimiento.md      # Interpretación del problema, actores, casos de uso
│       │   ├── analisis-funcional.md # Personas, épicas, user stories y criterios de aceptación
│       │   ├── supuestos.md          # Supuestos explícitos (fuente única, se referencian por ID)
│       │   ├── preguntas-cliente.md  # Preguntas abiertas para validar con el cliente
│       │   ├── riesgos.md            # Riesgos (fuente única, se referencian por ID)
│       │   ├── integraciones.md      # Sistemas existentes, APIs y limitaciones conocidas
│       │   └── alternativas.md       # Alternativas de solución evaluadas y elección (insumo de ADR-001)
│       ├── 02-arquitectura/
│       │   ├── decisiones/           # ADRs: ADR-001-<tema>.md (opciones, decisión, trade-offs)
│       │   ├── arquitectura.md       # Visión consolidada: componentes, criterios, seguridad, ambientes
│       │   ├── costos.md             # Modelo de costos y escalado (operación base vs. pico)
│       │   ├── well-architected.md   # (Opcional) Revisión WA "quick" basada en descripción
│       │   └── diagramas/
│       │       ├── flujo.drawio      # Diagrama de flujo del proceso / solución
│       │       ├── flujo.md          # Guía complementaria
│       │       ├── despliegue.drawio # Diagrama de despliegue
│       │       ├── despliegue.md     # Guía complementaria
│       │       ├── *-resumen.drawio  # Versiones resumidas (+ .md) para insertar en documentos
│       │       └── export/           # Exportados: <nombre>.drawio.png / .drawio.svg
│       ├── 03-estimacion/
│       │   └── estimacion.md         # Fases, entregables y placeholders de tiempos/esfuerzo
│       ├── 04-entregable/
│       │   ├── propuesta-tecnica.md  # Propuesta consolidada generada (fuente de la versión con marca)
│       │   ├── propuesta-tecnica.docx# Versión con marca generada a partir del .md
│       │   └── img/                  # Figuras e imágenes de reserva usadas en el .docx
│       └── 05-humanized/             # ENTREGA FINAL: archivos que genera y edita el usuario
│                                     #   a partir de 04-entregable (documento final, diagramas pegados)
│
├── scripts/                         # Scripts de soporte del espacio de trabajo
├── skills-lock.json                  # Origen y hash de las skills instaladas desde repositorios
└── .claude/skills/                   # Skills del proyecto (única copia): amazon-bedrock,
                                      #   aws-architecture-diagram, aws-well-architected-review,
                                      #   preteco-skills-brand (local, no está en skills-lock.json)
```

### Flujo de trabajo por escenario

1. `00-brief` → guardar el enunciado tal cual llegó y redactar las directivas del escenario.
2. `01-analisis` → entender el problema y explicitar supuestos y preguntas abiertas.
3. `02-arquitectura` → decidir con ADRs, modelar costos y dibujar los diagramas.
4. `03-estimacion` → fases a alto nivel y placeholders de tiempos.
5. `04-entregable` → consolidar todo en `propuesta-tecnica.md` partiendo de `templates/`, ajustado a las
   secciones que exija el brief, y generar a partir de ahí las versiones con marca (por ejemplo, `.docx`).
6. `05-humanized` → el usuario deja acá los archivos que produce en procedimientos posteriores para la
   **entrega final** (revisión manual, diagramas pegados, ajustes de redacción). Reglas para Claude:
   - **Solo lectura:** se puede leer como referencia, pero no se crean, modifican, mueven ni borran
     archivos en esta carpeta, salvo que el usuario lo pida expresamente.
   - Si `05-humanized` y `04-entregable` difieren, **la versión de `05-humanized` es la final**: avisar
     las diferencias en lugar de sobrescribir.
   - Los archivos de bloqueo de Office (`~$*`) están ignorados en `.gitignore`.

## Convenciones

- **Idioma:** español rioplatense neutro, tono profesional; términos técnicos en inglés cuando son estándar
  (LLM, RAG, webhook, handoff).
- **Formato:** Markdown. Diagramas en **draw.io** (`.drawio`) salvo que el brief indique otra cosa; se
  versiona la fuente y se exporta a `export/` (PNG o SVG) para embeberlos con rutas relativas en el MD.
- **Nombres de archivo:** `kebab-case`, sin acentos ni espacios. Escenarios con prefijo numérico `NN-`.
- **IDs:** supuestos `S-01`…, riesgos `R-01`…, decisiones `ADR-001`…; la propuesta los referencia por ID.
- **Placeholders:** `[[COMPLETAR: descripción]]` para datos que se completan después, así se pueden
  buscar con `grep -rn "\[\[COMPLETAR" escenarios/`.
- **Doble audiencia:** cada sección técnica abre con 1–2 líneas en lenguaje de negocio antes del detalle.
- **Decisiones:** toda elección relevante de tecnología se justifica (opciones evaluadas, trade-offs,
  costo y grado de dependencia del proveedor).
- **Herramientas ≠ arquitectura:** que haya skills de AWS no implica que la solución deba ser AWS; la
  plataforma se decide por las directivas del brief y se justifica en un ADR.