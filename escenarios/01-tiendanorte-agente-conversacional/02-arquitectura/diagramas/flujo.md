# Flujo conversacional — TiendaNorte

> Guía complementaria de [`flujo.drawio`](flujo.drawio).

- **Exportado:** `export/flujo.drawio.png` [[COMPLETAR: exportar PNG]]
- **Versión / fecha:** v0.1 · 2026-10-29
- **Páginas:**
  - *Vista general (negocio)*.
  - *Secuencia técnica de un turno*.

## Página 1 — Vista general

Carriles: Cliente · Asistente virtual (IA) · Sistemas de TiendaNorte · Atención humana.

1. **①** El cliente escribe por WhatsApp o por el chat web.
2. **②** Pasan los **controles de entrada**: intentos de manipulación, contenido ofensivo, datos sensibles y límites de uso (GR-01 a GR-04, GR-09).
3. **③** El asistente **entiende qué necesita** y toma un camino:
   - **Cambios y devoluciones:** busca la política vigente en la base de conocimiento. Es **solo informativo y no deriva** (S-05).
   - **Pedido:** identifica al cliente con Nº de pedido + DNI, email o teléfono (US-05). Con 2 intentos fallidos, deriva.
   - **Stock:** consulta disponibilidad online y por sucursal.
   - **Otro tema, pedido de hablar con una persona, molestia o fallo:** deriva a atención humana (línea roja punteada) con historial, resumen y motivo (US-11 a US-15).
4. **④** Con el cliente validado, consulta el pedido en el e-commerce y el ERP (solo lectura).
5. **⑤** **Redacta la respuesta** y aplica los **controles de salida**: grounding, PII y compromisos comerciales (GR-05 a GR-07).
6. **⑥** El cliente recibe la respuesta.
7. **⑦** Si sigue la conversación, vuelve al paso ①. Si no, la sesión se cierra por **15 minutos sin actividad o 10 turnos** (S-08). Llegar a los 10 turnos cierra la sesión, no deriva.

## Página 2 — Secuencia técnica de un turno

| Paso | Componente | Acción |
|---|---|---|
| 1 | WhatsApp: End User Messaging Social → SNS → Lambda de ingreso · Chat: API Gateway + WAF → Lambda de ingreso | Valida origen o firma, descarta eventos de estado, deduplica, enmascara tarjetas y aplica rate limit por remitente |
| 2–3 | SQS FIFO → Lambda orquestador | Orden por conversación; lee la sesión (estado, turno, timeout). Si el estado es `HUMANO`, reenvía a la plataforma |
| 4 | Orquestador → Bedrock Guardrails | `ApplyGuardrail` de entrada sobre el mensaje del cliente; si se bloquea, responde el mensaje estándar sin invocar al agente |
| 5 | Orquestador → AgentCore Harness | `InvokeHarness` con `runtimeSessionId`, modelo de la sesión y token de sesión firmado |
| 6 | Harness → Bedrock | Loop gestionado: Converse con Haiku 5.5 o Sonnet 5.5 |
| 7–8 | Harness → AgentCore Gateway → Lambda tools → APIs del cliente | Tool MCP; la Lambda verifica el token de sesión, la identidad y los parámetros; usa la caché y el circuit breaker |
| 9 | Harness → Orquestador | Stream con la respuesta y los resultados de las tools (`toolResult`) |
| 10 | Orquestador → Bedrock Guardrails | `ApplyGuardrail` de salida con grounding contra los resultados de las tools y la KB |
| 11 | Orquestador → Lambda de salida → canal | Envía la respuesta (`SendWhatsAppMessage` o API del chat); persiste la transcripción enmascarada; turno + 1 |
| — | Orquestador → plataforma de atención | Si la sesión quedó marcada (tool `derivar_a_humano`, bloqueos o API caída): crea la conversación con contexto y pasa el estado a `HUMANO` |

## Decisiones de diseño
- ADR-001: AgentCore Harness.
- ADR-004: canales, sesión y derivación.
- ADR-005: guardrails.
- ADR-003: tools e identidad.
- ADR-007: WhatsApp vía AWS End User Messaging Social.

## Convenciones del diagrama
- **Líneas:**
  - Sólida: flujo principal.
  - Punteada: respuesta o caso condicional.
  - Roja punteada: derivación a humano.
- **Colores:**
  - Amarillo: controles.
  - Azul: pasos del asistente.
  - Violeta: sistemas.
  - Rojo: atención humana.
