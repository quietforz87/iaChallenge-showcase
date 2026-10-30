# Despliegue — TiendaNorte · Agente conversacional en AWS

> Guía complementaria de [`despliegue.drawio`](despliegue.drawio).

- **Exportado:** `export/despliegue.drawio.png` [[COMPLETAR: exportar PNG]]
- **Versión / fecha:** v0.1 · 2026-10-29

## Recorrido de un mensaje
1. **①** El cliente escribe por WhatsApp o por el chat del e-commerce.
2. **②** Los mensajes de WhatsApp llegan a **AWS End User Messaging Social** (WABA vinculada), que los publica en un **tópico SNS standard**. El chat web envía un webhook a **API Gateway (HTTP API) protegido con AWS WAF**.
3. **③** La **Lambda de ingreso** valida, deduplica, normaliza, enmascara datos sensibles y encola en **SQS FIFO**.
4. **④** La **Lambda orquestadora** toma el mensaje en orden y gestiona la sesión en **DynamoDB**.
5. **⑤** El orquestador aplica **Bedrock Guardrails** a la entrada (`ApplyGuardrail`) e invoca al agente en **AgentCore Harness**.
6. **⑥** El Harness ejecuta el loop con **Bedrock** (Haiku 5.5 / Sonnet 5.5). Al terminar, el orquestador aplica el guardrail de salida con grounding.
7. **⑦–⑧** El agente usa las tools vía **AgentCore Gateway (MCP)**. Las **Lambda tools** consultan las APIs del cliente por HTTPS, usan la **caché en DynamoDB** y consultan la **Managed Knowledge Base** (fuente **S3**).
8. **⑨–⑩** La **Lambda de salida y derivación** responde por WhatsApp con `SendWhatsAppMessage` o por la API del chat del e-commerce. Si corresponde, **deriva** a la plataforma de atención con contexto (rojo punteado).
9. **EventBridge Scheduler** dispara cada 5 minutos el cierre de las sesiones vencidas.

## Componentes
| Componente | Propósito | Notas |
|---|---|---|
| AWS End User Messaging Social | Conexión con WhatsApp Business (WABA de TiendaNorte) para recibir y enviar mensajes | ADR-007; USD 0,005 saliente / 0,001 entrante |
| SNS standard (KMS) | Destino de eventos del WABA; filter policy que descarta eventos de estado | Las colas FIFO no están soportadas como destino; el orden lo da la SQS FIFO |
| API Gateway (HTTP) + AWS WAF | Recibir los webhooks del chat web | Rate limit por IP, bot control |
| Lambda de ingreso | Validar origen o firma, deduplicar, normalizar, enmascarar tarjetas y aplicar rate limit por remitente | GR-04, GR-09 |
| SQS FIFO (+ DLQ) | Absorber picos y preservar el orden por conversación | `MessageGroupId` = canal + remitente |
| Lambda orquestador | Estado de sesión, turnos, timeout, enrutamiento IA / humano, métricas | ADR-004 |
| DynamoDB | `sesiones`, `transcripciones` (TTL 90 días), `cache`, `limites` | On demand, KMS |
| AgentCore Harness | Agente gestionado por configuración (modelo, prompt, tools del Gateway, memoria, límites); microVM aislada por sesión | Autenticación IAM; sin modo VPC; `allowedTools` acotado; endpoints por ambiente |
| Bedrock Guardrails | `ApplyGuardrail` desde el orquestador (entrada y salida con grounding) y desde `buscar_politica` | ADR-005 |
| AgentCore Memory | Contexto de corto plazo de la sesión | TTL 24 h, KMS |
| Amazon Bedrock | Claude Haiku 5.5 / Sonnet 5.5 (perfil `global.`), invocados por el Harness | ADR-002 |
| AgentCore Gateway | Exponer las tools por MCP; gestionar credenciales | ADR-003 |
| Lambda tools | Adaptadores de solo lectura con validación de identidad, caché y circuit breaker | ADR-003 |
| Managed Knowledge Base + S3 | Políticas y FAQs del cliente | ADR-006 |
| Lambda de salida y derivación | Responder por el canal (`SendWhatsAppMessage` / API del chat); crear la derivación en la plataforma de atención | ADR-004, ADR-007 |
| EventBridge Scheduler | Invoca al orquestador cada 5 minutos para cerrar sesiones vencidas | US-03; en el diagrama, dentro de los servicios transversales |
| CloudWatch · KMS · Secrets Manager · CloudTrail | Observabilidad, cifrado, credenciales y auditoría | Transversales |

## Decisiones de diseño
- ADR-001 a ADR-007 en `../decisiones/`.

### Simplificaciones del diagrama
- **EventBridge Scheduler:** no se dibuja su conexión con el orquestador; aparece en los servicios transversales.
- **Tools hacia otros servicios:** no se dibujan las conexiones de las Lambda tools con DynamoDB `sesiones` (token, identidad, derivación) ni con Bedrock Guardrails (fragmentos de la KB).
- **Ingreso a DynamoDB:** no se dibuja la conexión de la Lambda de ingreso con DynamoDB (tabla `limites`).

## Convenciones del diagrama
- **Líneas:**
  - ① → ⑩: recorrido de un mensaje.
  - Sólida: flujo principal.
  - Punteada: asíncrono.
  - Rojo punteado: derivación a humano.
- **Íconos:** oficiales de AWS (`mxgraph.aws4`). Los sistemas externos se representan como servidores genéricos.
