# Riesgos — Escenario 01 · TiendaNorte

> Riesgos identificados en preventa. Este archivo es la fuente única: la propuesta los referencia por ID (`R-xx`).
> Fuentes: ADR-001 a ADR-007, `02-arquitectura/costos.md`, `03-estimacion/estimacion.md` y `supuestos.md`.

## Escala

| Nivel | Probabilidad | Impacto |
|---|---|---|
| Alta / Alto | Es probable que ocurra durante el proyecto | Compromete plazo, presupuesto u objetivo del MVP |
| Media / Medio | Puede ocurrir | Obliga a reprogramar o recortar alcance parcial |
| Baja / Bajo | Poco probable | Afecta poco y se absorbe dentro del plan |

**Severidad** = Probabilidad × Impacto:
- **Crítica:** Alta × Alto.
- **Alta:** Alta × Medio, o Media × Alto.
- **Media:** Media × Medio, o Baja × Alto.
- **Baja:** el resto.

## Matriz

| ID | Categoría | Riesgo | Causa | Prob. | Impacto | Severidad | Mitigación | Contingencia | Responsable |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Plazo | No llegar a producción antes de la campaña | Plazo de ~2 meses con dependencias de terceros (Meta, proveedor del ERP, plataforma de atención) | Alta | Alto | **Crítica** | MVP acotado; fases en paralelo; ítems de largo plazo desde la primera semana; decisiones en H1 | Salida parcial: un solo canal o un subconjunto de casos de uso; congelamiento de alcance | Célula IA / Cliente |
| R-02 | Integración | Las APIs del ERP no cumplen los mínimos operativos (latencia, throughput, frescura, stock por sucursal) | Limitaciones documentadas pero desconocidas (S-04) | Alta | Medio | **Alta** | Relevamiento y prueba en F0; caché con TTL corto; circuit breaker | Stock solo online; aviso de "disponibilidad aproximada"; derivación ante caída | Cliente (TI) |
| R-03 | Proveedor | AgentCore Harness (en *preview*) no ofrece las capacidades, la estabilidad o el SLA necesarios | Servicio nuevo (ADR-001) | Media | Alto | **Alta** | PoC en F0 con criterio de aceptación explícito; configuración portable | Fallback a AgentCore Runtime con un agente Strands propio (ADR-001, opción B), con esfuerzo adicional en F3 | Célula IA |
| R-04 | Calidad IA | Latencia alta en la primera respuesta de cada sesión (arranque de la microVM de Harness) | Una microVM por sesión (ADR-001) | Media | Medio | Media | Medición en la PoC; objetivo de latencia acordado con negocio | Mensaje inicial inmediato desde el orquestador mientras arranca la sesión | Célula IA |
| R-05 | Plazo | La migración de la WABA y del número de WhatsApp a End User Messaging Social se demora o no es posible | Dependencia de Meta y del proveedor actual; PIN de los números (S-18) | Media | Alto | **Alta** | Gestión desde F1; ventana fuera de campaña; número de prueba para desarrollo | Número nuevo comunicado a los clientes, o salida inicial solo con chat web | Cliente / Célula IA |
| R-06 | Integración | La plataforma de atención no permite integrar conversaciones por API | Plataforma todavía no definida (S-02) | Media | Alto | **Alta** | Definición y validación técnica en F0 (P-11) | Amazon Connect como plataforma o destino de eventos (ADR-007); bandeja mínima como alcance adicional | Cliente |
| R-07 | Plazo / Calidad | Las políticas y FAQs llegan tarde o con baja calidad | Las provee el cliente (S-12) | Media | Alto | **Alta** | Fecha límite comprometida (E-02); plantilla de redacción provista por la Célula IA | Publicar solo las políticas validadas y derivar el resto | Cliente (CX) |
| R-08 | Calidad IA | La contención queda por debajo del 60% | Consultas más variadas que lo supuesto; contenido incompleto; umbrales de guardrails muy estrictos | Media | Medio | Media | Set de evaluación con conversaciones reales; métricas por motivo de derivación; iteración semanal | Ampliar FAQs y casos; recalibrar umbrales en el hypercare | Célula IA |
| R-09 | Calidad IA | Respuestas incorrectas o inventadas (stock, plazos, políticas) | Naturaleza probabilística del LLM | Baja | Alto | Media | Datos solo desde tools y KB; grounding con `ApplyGuardrail`; compromisos comerciales denegados; evaluación como gate | Bloqueo y derivación; corrección del prompt y de la política con una nueva versión del Harness | Célula IA |
| R-10 | Seguridad / Privacidad | Manipulación del asistente (inyección de prompts) o abuso del canal | Exposición pública del canal | Media | Medio | Media | Guardrails de entrada y de la KB; tools de solo lectura con token de sesión firmado; rate limit y WAF | Bloqueo temporal del remitente; ajuste de filtros | Célula IA |
| R-11 | Seguridad / Privacidad | Exposición de datos personales de clientes | Transcripciones y logs con PII | Baja | Alto | Media | Enmascarado en el ingreso; KMS; TTL de 90 días; logging de invocaciones deshabilitado; mínimo privilegio | Procedimiento de incidente y notificación según la normativa vigente | Célula IA / Cliente (Legal) |
| R-12 | Operación | Cuotas de Bedrock o throughput de WhatsApp insuficientes en el pico | Picos x5–x8 (`costos.md` §6) | Media | Alto | **Alta** | Solicitud de cuotas en F1; verificación del nivel de mensajería del número; prueba de carga x8 en F6 | Cola SQS como amortiguador; mensaje de espera; prioridad a respuestas cortas | Célula IA |
| R-13 | Costo | El costo real supera la estimación | Más mensajes o turnos por sesión; Harness sin prompt caching; más escalamiento a Sonnet | Media | Medio | Media | Métricas de costo por sesión desde el día 1; AWS Budgets con alarmas; palancas de `costos.md` | Ajuste de límites de sesión y agrupación de mensajes | Célula IA |
| R-14 | Proveedor | Dependencia de servicios propietarios de AWS mayor que la aceptable | Harness, Gateway, End User Messaging, Managed KB | Baja | Medio | Baja | Ruta de salida documentada en cada ADR; tools MCP; formato de mensajes de Meta; datos en S3 y DynamoDB | Migración por componente, empezando por el de mayor costo (mensajería) | Célula IA |
| R-15 | Plazo | Baja disponibilidad de los referentes del cliente para validaciones y UAT | Campaña en preparación en paralelo | Media | Medio | Media | Agenda de validaciones acordada en el kickoff (E-07) | Validación asincrónica con fechas límite; escalamiento al sponsor | Cliente |
