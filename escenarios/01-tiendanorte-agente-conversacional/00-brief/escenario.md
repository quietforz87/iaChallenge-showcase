# Escenario 01 — TiendaNorte: agente conversacional de atención al cliente

Este brief tiene dos partes:
- **Parte A — Enunciado original:** tal como se recibió en preventa. **No modificar.**
- **Parte B — Directivas del escenario:** requisitos y criterios que guían todo el trabajo del caso.
  Prevalecen sobre `CLAUDE.md` y las plantillas. Los supuestos e interpretaciones van en `01-analisis/`.

---

# Parte A — Enunciado original

## Desafío

A partir de un escenario elaborá una propuesta técnica de solución de IA.

## Escenario

TiendaNorte es una cadena de electrodomésticos y electrónica con tienda online y 15 sucursales físicas. Tu interlocutor
es el gerente de Experiencia del Cliente.

El problema: durante campañas de ventas (Black Friday, Hot Sale) el equipo de atención al cliente por WhatsApp y chat web se satura de consultas repetitivas (estado de pedido, stock,
cambios y devoluciones). Los tiempos de respuesta se disparan y hay ventas que se pierden porque el cliente no obtiene respuesta a tiempo.

Lo que piden: un agente conversacional que resuelva las consultas más frecuentes por WhatsApp y chat web, y que derive a un agente humano los casos que no puede resolver.

De qué disponen: plataforma de e-commerce con API disponible, CRM comercial, y un ERP con acceso a stock e información de pedidos vía API (con algunas limitaciones documentadas). WhatsApp Business API ya contratada.

Necesidad: El tráfico de consultas se multiplica entre 5 y 8 veces durante campañas puntuales. Necesitan tener algo funcionando en producción en un plazo acotado (próxima campaña grande en 2 meses).

Limitaciones: No cuentan con equipo de infraestructura propio, hoy todo su stack corre en servicios cloud gestionados. Es una decisión sensible al costo y quieren entender cómo escala el gasto si la solución tiene éxito, y evitar quedar atados a un único proveedor.

## Qué debe incluir la propuesta

Tu documento debe cubrir, como mínimo:

1. Resumen ejecutivo — en pocas líneas, cuál es tu propuesta y por qué.
2. Entendimiento del problema — cómo interpretás la necesidad del cliente y qué supuestos hiciste donde faltaba información.
3. Solución propuesta — la arquitectura de la solución, incluyendo un diagrama tanto de flujo como de despliegue.
4. Alcance — qué incluye el MVP y qué quedaría para una etapa posterior.
5. Estimación de esfuerzo — definir fases a alto nivel y dejar un placeholder para completar estimación de tiempos.
6. Riesgos y supuestos — qué podría complicar la implementación y qué estás dando por sentado.

## Formato

- Documento en formato MD.
- Los gráficos se deben realizar en Draw.io.

---

# Parte B — Directivas del escenario

## B.1 Entregable

- **Documento:** `04-entregable/propuesta-tecnica.md`, en Markdown.
- **Secciones obligatorias** (mínimo, en este orden):
  1. **Resumen ejecutivo** — en pocas líneas, qué se propone y por qué.
  2. **Entendimiento del problema** — interpretación de la necesidad y supuestos donde faltaba información.
  3. **Solución propuesta** — arquitectura, con **diagrama de flujo** y **diagrama de despliegue**.
  4. **Alcance** — qué incluye el MVP y qué queda para etapas posteriores.
  5. **Estimación de esfuerzo** — fases a alto nivel + placeholder (`[[COMPLETAR: ...]]`) para los tiempos.
  6. **Riesgos y supuestos** — qué podría complicar la implementación y qué se da por sentado.
- **Diagramas:** en draw.io.
  - `02-arquitectura/diagramas/flujo.drawio` — flujo conversacional: intención → resolución →
    derivación a humano.
  - `02-arquitectura/diagramas/despliegue.drawio` — despliegue sobre servicios cloud gestionados.
- **Audiencia:** gerente de Experiencia del Cliente (negocio) y equipo de delivery (técnico).

## B.2 Criterios de diseño

| Criterio | Origen en el enunciado | Implicancia para la propuesta |
|---|---|---|
| **Time-to-market** | Producción en ~2 meses (próxima campaña grande) | MVP acotado y realista; priorizar lo que reduce carga en campaña |
| **Escalabilidad elástica** | Tráfico x5–x8 en campañas puntuales | Servicios serverless/gestionados que escalen solos; validar cuotas de LLM y límites de APIs del cliente en pico |
| **Operación mínima** | Sin equipo de infraestructura; stack en cloud gestionado | Nada de servidores autoadministrados; operación sin guardias de infraestructura |
| **Sensibilidad al costo** | Quieren entender cómo escala el gasto si tiene éxito | Modelo de costos con costo por conversación, operación base vs. campaña, y palancas de ahorro |
| **Evitar vendor lock-in** | No quedar atados a un único proveedor | Abstracción sobre el proveedor de LLM y los canales; justificar en ADR toda dependencia propietaria con su ruta de salida |
| **Derivación a humano** | Derivar lo que el agente no resuelve | Handoff con contexto de la conversación hacia el equipo de atención existente |
| **Omnicanal** | WhatsApp y chat web | Un único motor conversacional detrás de adaptadores por canal |

## B.3 Casos de uso foco del MVP

Consultas repetitivas que saturan al equipo en campañas:
- Estado de pedido.
- Stock (online y por sucursal).
- Cambios y devoluciones (políticas y estado de la gestión).

## B.4 Sistemas del cliente a integrar

| Sistema | Uso esperado | Notas del enunciado |
|---|---|---|
| Plataforma e-commerce | Pedidos online, catálogo | API disponible |
| ERP | Stock e información de pedidos | API con **limitaciones documentadas** (a relevar) |
| CRM comercial | Identificación y contexto del cliente | Sin detalle de API (supuesto a explicitar) |
| WhatsApp Business API | Canal WhatsApp | Ya contratada |
| Chat web | Canal web | Sin detalle de la herramienta actual (supuesto a explicitar) |

## B.5 Aplicación de las skills en este caso

- **`aws-architecture-diagram`:**
  - En el diagrama de despliegue, los sistemas externos a la derecha son e-commerce, ERP, CRM y Meta/WhatsApp.
  - El flujo conversacional usa carriles Cliente / Agente IA / Integraciones / Agente humano.
  - La derivación a humano va en rojo punteado.
- **`amazon-bedrock`** (si se evalúa Bedrock como motor de IA):
  - **Modelo:** ruteo por costo. Un modelo chico y barato (Haiku / Nova) clasifica la intención y responde los casos simples; uno de mayor capacidad (Sonnet) queda para los casos complejos.
  - **Costo:** prompt caching para el system prompt y las políticas, y cuotas dimensionadas para el pico x5–x8.
  - **Tools:** las APIs de e-commerce, ERP y CRM se exponen como tools vía MCP (AgentCore Gateway o equivalente).
  - **RAG:** las FAQs y las políticas de cambios y devoluciones van en una base de conocimiento.
  - **Portabilidad:** el proveedor del LLM es intercambiable por configuración (AgentCore Harness admite varios proveedores) y la configuración del agente es portable a un agente Strands propio. Cada uso de AgentCore o de una KB administrada se registra en un ADR con su ruta de salida.
- **`aws-well-architected-review`:** quick review por descripción antes de entregar, con foco en
  costo, confiabilidad en pico y seguridad de datos personales de clientes.

## B.6 Directivas surgidas en el trabajo del caso

| Fecha | Directiva | Origen | Impacto |
|---|---|---|---|
| 2026-10-29 | La solución se construye sobre **AWS** | Rondas de análisis (S-01) | Toda la arquitectura |
| 2026-10-29 | Alternativa elegida: **B, agente gestionado en Bedrock AgentCore + disciplina de portabilidad** | Checkpoint de análisis | ADR-001 a ADR-006 |
| 2026-10-29 | La integración de **WhatsApp Business** se hace con **AWS End User Messaging Social** | Revisión de arquitectura | ADR-007; modifica ADR-004; costos; S-18 a S-20 |
| 2026-10-29 | El agente se plantea con **AgentCore Harness** (configuración, sin código de orquestación propio) | Revisión de arquitectura | ADR-001 revisado; ADR-002 a ADR-006; costos; diagramas |
