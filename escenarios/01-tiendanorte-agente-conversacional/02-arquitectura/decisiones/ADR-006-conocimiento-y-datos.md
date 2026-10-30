# ADR-006 — Base de conocimiento, memoria y datos de conversación

| Campo | Valor |
|---|---|
| Estado | Aceptada · revisada el 2026-10-29 (memoria configurada en el Harness) |
| Fecha | 2026-10-29 |
| Relacionado | S-05, S-08, S-12, S-15; US-09, US-10, US-16, US-17, US-18; ADR-001, ADR-005 |

## Contexto
Hay cuatro necesidades de datos:
- Las políticas y FAQs las provee el cliente (S-12) y se responden solo desde ese contenido (US-09, US-27).
- El agente necesita memoria dentro de la sesión.
- Las transcripciones se guardan 90 días con PII enmascarada (S-15).
- La gerencia necesita métricas de contención, costo y motivos (US-17).

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| Conocimiento A — **Bedrock Managed Knowledge Base con fuente S3** ✅ | Sin vector store que operar; parseo, chunking y embeddings gestionados | Servicio propietario | $1 cada 1.000 retrieves; $5/GB-mes de datos crudos | Medio |
| Conocimiento B — KB administrada por nosotros (OpenSearch Serverless / S3 Vectors) | Control del chunking y del índice | Más operación y costo fijo | Medio | Medio |
| Conocimiento C — Políticas completas dentro del prompt (cacheadas) | Simple; sin retrieve | Escala mal si crece el contenido; más tokens por llamada | Bajo con caché | Bajo |
| Memoria A — **AgentCore Memory de corto plazo + DynamoDB como registro de negocio** ✅ | Integración nativa con Runtime; DynamoDB es la fuente de verdad portable | Dos lugares con historia (con roles distintos) | Muy bajo | Bajo-medio |
| Memoria B — Solo DynamoDB, con el historial pasado al agente en cada invocación | Un solo almacén | Hay que reconstruir el contexto a mano en cada turno | Muy bajo | Bajo |

## Decisión
**Conocimiento: Managed Knowledge Base**
- **Fuente:** un bucket **S3** versionado y cifrado (`politicas/`), donde la Célula IA publica los documentos que entrega el cliente (US-18). Cada publicación dispara la sincronización de la KB y queda registrada con su versión y fecha (US-18.2).
- **Consulta:** la tool `buscar_politica` usa `Retrieve`; los fragmentos son el `grounding_source` del guardrail (ADR-005).
- **Plan B:** si el volumen de políticas es chico (menos de ~20 páginas), se evalúa la opción C, que elimina un componente. La decisión se toma cuando lleguen los documentos.

**Memoria y datos:**
- **AgentCore Memory, solo corto plazo**, para el contexto del agente dentro de la sesión. Es un recurso propio asociado al Harness (`agentCoreMemoryConfiguration`), con TTL mínimo (24 h) y cifrado con KMS. **Sin memoria de largo plazo** en el MVP. El `actorId` es el remitente enmascarado.
- **DynamoDB:** fuente de verdad del negocio, en modo on demand y cifrada con KMS.

| Tabla | Contenido | TTL |
|---|---|---|
| `sesiones` | Estado, turnos, canal, identidad validada, motivo de cierre o derivación | 90 días |
| `transcripciones` | Mensajes **enmascarados** (DNI, email y teléfono parciales; tarjetas eliminadas en el ingreso) | **90 días** (S-15) |
| `cache` | Respuestas de las APIs del cliente | 2–5 minutos |
| `limites` | Contadores de rate limit por remitente | 1–15 minutos |

- **Métricas:** CloudWatch con métricas de negocio emitidas por el orquestador (sesiones, contención, derivaciones por motivo, cierres, intervenciones de guardrails, costo estimado por tokens) y un dashboard para la gerencia CX (US-17). Logs con retención de **30 días**, cifrados con KMS.

## Consecuencias
- **Positivas:**
  - Cero infraestructura de búsqueda.
  - La retención de 90 días se cumple con el TTL de DynamoDB, sin procesos manuales.
  - El dashboard sale de un solo lugar.
- **Negativas / trade-offs:**
  - La calidad de las respuestas de políticas depende de la calidad del contenido del cliente (riesgo de plazo, S-12).
  - El TTL de DynamoDB elimina con cierta demora (no es inmediato); se documenta en la política de datos.
- **Ruta de salida:**
  - Los documentos fuente viven en S3 y se pueden reindexar en cualquier motor vectorial.
  - DynamoDB guarda el historial completo de negocio, así que reemplazar AgentCore Memory no pierde información.
