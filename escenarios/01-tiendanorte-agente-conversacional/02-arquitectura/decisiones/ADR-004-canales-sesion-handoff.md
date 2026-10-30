# ADR-004 — Canales, gestión de sesión y derivación a humano

| Campo | Valor |
|---|---|
| Estado | Aceptada · **modificada por ADR-007** (entrada y salida de WhatsApp vía End User Messaging Social; P-11 resuelto) |
| Fecha | 2026-10-29 |
| Relacionado | S-02, S-03, S-08, S-13, S-14; US-01 a US-04, US-11 a US-15, US-29; GR-04, GR-09; ADR-007 |

## Contexto
Los mensajes llegan por webhooks de WhatsApp Business API y del chat del e-commerce (S-03). Hay que cumplir lo siguiente:
- Absorber picos x5–x8 sin perder mensajes (US-01.4) y respetar el orden dentro de cada conversación.
- Aplicar límites de sesión: 15 minutos y 10 turnos (S-08).
- Derivar a una plataforma de atención que todavía no está definida (S-02).
- Cuando una persona toma la conversación, el asistente deja de responder (US-15.2).

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — Webhook → Lambda que invoca al agente de forma síncrona | Simple | Los webhooks tienen timeouts cortos; un pico genera reintentos y mensajes duplicados o perdidos | Mínimo | Bajo |
| B — **Webhook → API Gateway + WAF → Lambda de ingreso → SQS FIFO → Lambda orquestador** ✅ | Responde 200 de inmediato; la cola absorbe el pico; FIFO por conversación preserva el orden; reintentos y DLQ | Un salto asíncrono más (latencia +100–300 ms) | Muy bajo | Bajo: patrón estándar de colas |
| C — Amazon Connect como hub omnicanal | Bandeja de agentes incluida | Reemplaza la plataforma que provee el cliente (S-02); lock-in alto | Medio | Alto |

## Decisión
Se adopta la **opción B**:

> **Nota (ADR-007):** para **WhatsApp**, la entrada es *End User Messaging Social → SNS standard → Lambda de ingreso* y la salida usa `SendWhatsAppMessage`. API Gateway + WAF queda solo para el **chat web**. El resto de esta decisión no cambia.

1. **API Gateway (HTTP API) + AWS WAF** (chat web): filtrado, bot control y rate limit por IP.
2. **Lambda de ingreso:**
   - Valida la firma del webhook del chat web, o el origen SNS del evento de WhatsApp, y deduplica por ID de mensaje (ADR-007).
   - Normaliza el mensaje a un formato común (canal, remitente, texto, adjuntos).
   - **Enmascara números de tarjeta, CVV y claves con regex** antes de persistir o encolar (GR-04, US-25.1).
   - Aplica el **rate limit por remitente** con un contador en DynamoDB (GR-09, US-29).
   - Rechaza audio e imágenes con el mensaje de US-01.3.
3. **SQS FIFO** con `MessageGroupId = canal + remitente`: orden por conversación, deduplicación por ID de mensaje y DLQ con alarma.
4. **Lambda orquestador** (dueño de la sesión, tabla `sesiones` en DynamoDB):
   - Lee el estado (`IA`, `HUMANO`, `CERRADA`), el contador de turnos y la última actividad.
   - Si pasaron más de 15 minutos, cierra la sesión anterior con resultado `timeout` y abre otra (US-03).
   - Si el estado es `HUMANO`, **reenvía el mensaje a la plataforma de atención** y no invoca al agente (US-15.2).
   - Si no, aplica el **guardrail de entrada** (`ApplyGuardrail`, ADR-005) e invoca al **Harness** (ADR-001) con el `runtimeSessionId`, el modelo de la sesión (ADR-002) y el token de sesión firmado (ADR-003).
   - Lee el stream de respuesta: el texto y los resultados de las tools. Aplica el **guardrail de salida con grounding** y revisa si la tool `derivar_a_humano` marcó la sesión.
   - Al llegar al turno 10, envía la respuesta más el aviso de cierre y cierra con `límite de turnos`, sin derivar (US-04).
   - Persiste la transcripción enmascarada y emite métricas (contención, motivo de cierre o derivación).
5. **Lambda de salida y derivación:**
   - Envía la respuesta por el canal correspondiente: `SendWhatsAppMessage` (End User Messaging Social) o la API del chat del e-commerce.
   - Cuando la sesión quedó marcada para derivar (tool `derivar_a_humano`, guardrail bloqueado dos veces o API no disponible), crea la conversación en la plataforma de atención con historial, resumen, intención, motivo y pedido validado (US-15.1). Después cambia el estado a `HUMANO`.
6. **EventBridge Scheduler (cada 5 minutos):** invoca un barrido que cierra las sesiones vencidas, para que las métricas de timeout no dependan de un nuevo mensaje.
7. **Vuelta al asistente:** cuando la plataforma de atención cierra la conversación (webhook o API), el estado vuelve a `CERRADA` y el próximo mensaje abre una sesión nueva con el asistente (US-15.3, a confirmar).

**Parámetros configurables:** timeout, máximo de turnos, límites de rate y textos estándar. Se guardan en **AppConfig o en un parámetro SSM** y se leen en caliente, sin redeploy (US-19).

## Punto P-11 (resuelto por ADR-007)
Con End User Messaging Social, el WABA publica todos sus eventos en un único destino de la cuenta AWS de la solución. Por lo tanto, **nuestra solución es la dueña del canal de WhatsApp**. Mientras atiende una persona, el orquestador reenvía los mensajes a la plataforma de atención y publica las respuestas de esa persona.

La plataforma de atención tiene que poder integrarse **por API** (canal personalizado). Si eso no fuera posible, se reevalúa con el cliente; una opción es Amazon Connect como destino de eventos (ADR-007).

## Consecuencias
- **Positivas:**
  - Ningún mensaje se pierde en el pico.
  - Los límites de sesión y la derivación son deterministas y medibles.
  - La plataforma de atención queda encapsulada en un solo conector.
- **Negativas / trade-offs:**
  - El orquestador concentra lógica de negocio crítica: necesita buena cobertura de pruebas.
  - La plataforma de atención tiene que soportar la integración por API (P-11).
- **Ruta de salida:** SQS, Lambda y DynamoDB tienen equivalentes directos en otras nubes (colas, funciones y una base clave-valor). El formato común de mensaje aísla a los canales.
