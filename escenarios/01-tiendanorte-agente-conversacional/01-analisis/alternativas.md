# Alternativas de solución — Escenario 01 · TiendaNorte

> Para negocio: evaluamos tres maneras de construir el agente en AWS. Elegimos la que llega a
> producción en 2 meses sin equipo de infraestructura y deja una salida documentada si se quiere
> cambiar de proveedor.
> Insumo de `02-arquitectura/decisiones/ADR-001-plataforma-agente.md`.

## Componentes comunes a las tres
- **Adaptadores de canal:** webhooks de WhatsApp Business API y del chat del e-commerce (S-03).
- **Conector de handoff** hacia la plataforma de atención del cliente (S-02, S-14).
- **Base de conocimiento** con las FAQs y políticas provistas por el cliente (S-12).
- **DynamoDB** para sesiones y transcripciones enmascaradas (S-08, S-15); **CloudWatch** para métricas de contención (S-17).
- **Caché, circuit breaker y respuesta degradada** frente a las APIs del cliente (ver `integraciones.md`).

## A — Serverless con orquestación propia (máxima portabilidad)
- **Infraestructura:** API Gateway → SQS → Lambda con un framework de agente open source (Strands Agents / LangGraph).
- **LLM:** Bedrock Converse detrás de una interfaz propia `LLMProvider`. Ruteo de modelo: Haiku / Nova para clasificar y resolver casos simples, Sonnet para los complejos. Prompt caching.
- **Tools y RAG:** las tools son funciones propias contra las APIs del cliente. El RAG usa Bedrock Knowledge Base o S3 Vectors.

| A favor | En contra |
|---|---|
| Bajo lock-in: se puede cambiar el LLM y llevar el cómputo a otra nube | Más código propio: memoria, trazas, guardrails y escalado |
| Menor costo variable | Mayor esfuerzo y riesgo para el plazo de 2 meses |
| Control total del comportamiento | |

## B — Agente gestionado en Bedrock AgentCore (máximo time-to-market) ✅ elegida
- **Agente:** AgentCore Runtime (o Harness) con el agente escrito en Strands Agents (open source).
- **AgentCore Gateway:** expone las APIs de e-commerce, ERP y CRM como tools **MCP**.
- **AgentCore Memory** guarda el estado de la sesión, y la observabilidad viene incluida.
- **Conocimiento y seguridad:** Bedrock Managed Knowledge Base, y Bedrock Guardrails para PII y temas fuera de alcance.
- **Canales:** adaptadores en Lambda.

| A favor | En contra |
|---|---|
| Menos código de infraestructura; escalado y operación gestionados | Lock-in medio en AgentCore (Runtime, Memory, Gateway) |
| El camino más rápido a producción | Costo por uso de servicios gestionados algo mayor |
| Cero operación de servidores (encaja con el cliente) | Servicio más nuevo, con menos casos de referencia |

**Disciplina de portabilidad tomada de A:**
- Tools expuestas por MCP.
- LLM detrás de `LLMProvider`.
- Prompts y políticas versionados en el repo.
- Ruta de salida documentada en el ADR: llevar el agente Strands a Lambda o a contenedores, con memoria en DynamoDB.

## C — Flujos deterministas con Amazon Lex V2 + LLM para FAQs (máxima previsibilidad)
- **Flujos:** Lex V2 modela intenciones y slots de pedido, stock e identificación, con fulfillment en Lambda.
- **FAQs:** el QnAIntent de Lex con Bedrock Knowledge Base responde FAQs y políticas.

| A favor | En contra |
|---|---|
| No inventa datos transaccionales; comportamiento auditable | Lock-in alto (modelado propietario de intents) |
| Bajo costo por sesión | Rígido ante consultas encadenadas o mal formuladas, lo que pone en riesgo la contención ≥ 60% |
| | Cada intención nueva se modela a mano |

## Comparativa

| Criterio (brief B.2) | A | B | C |
|---|---|---|---|
| Time-to-market (2 meses) | Medio | **Alto** | Medio |
| Escalabilidad en pico x5–x8 | Alta | Alta | Alta |
| Operación mínima | Media | **Alta** | Alta |
| Costo por sesión | **Bajo** | Medio | Bajo |
| Evitar lock-in | **Alto** | Medio (mitigado) | Bajo |
| Contención ≥ 60% | Alta | Alta | Media |

## Decisión
Se continúa con **B + disciplina de portabilidad** (checkpoint 2026-10-29). En la revisión de arquitectura se definió ejecutar el agente en **AgentCore Harness**; la portabilidad del LLM pasa a la configuración del Harness, que reemplaza a `LLMProvider` (ver ADR-001 y ADR-002). Se formaliza en ADR-001 en la etapa
de arquitectura, con el costo cada 1.000 sesiones (S-07) en `02-arquitectura/costos.md`.
