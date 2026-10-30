# ADR-007 — Integración de WhatsApp mediante AWS End User Messaging Social

| Campo | Valor |
|---|---|
| Estado | Aceptada (directiva de la Célula IA, revisión de arquitectura del 2026-10-29) |
| Fecha | 2026-10-29 |
| Relacionado | S-02, S-03, S-18, S-19, S-20; ADR-004 (modifica los pasos 1, 2 y 5); P-11, P-12, P-13 |

## Contexto
ADR-004 suponía recibir el webhook de Meta (WhatsApp Cloud API) en API Gateway y responder con la API de Meta. En la revisión de arquitectura se definió usar **AWS End User Messaging Social**, el servicio de AWS para WhatsApp Business: la cuenta de WhatsApp Business (WABA) de TiendaNorte se vincula a la cuenta AWS de la solución.

Según la documentación de AWS:
- **Mensajes entrantes:** el WABA publica todos los eventos (mensajes recibidos y estados de los enviados) en **un único destino por WABA**, que puede ser un **tópico SNS standard** o una instancia de Amazon Connect. **Los tópicos SNS FIFO no están soportados.**
- **Respuestas:** se envían con la API `SendWhatsAppMessage`, con el payload en formato de mensaje de Meta. Los adjuntos se descargan y suben con las APIs de media del servicio.
- **Vinculación de la WABA:** se hace por *embedded signup*. Hay que **ceder el control de la WABA a AWS** (AWS lo devuelve a pedido) y contar con los **PIN de todos los números** que se migran.
- **Región:** el servicio está disponible en `us-east-1`, la misma región de la solución.
- **Costo:** AWS cobra **USD 0,005 por mensaje saliente** y **USD 0,001 por mensaje entrante**, más la tarifa de Meta, que AWS factura según el tarifario de Meta.

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — WhatsApp Cloud API de Meta directa (webhook propio en API Gateway) | Sin tarifa por mensaje adicional a la de Meta; portable | Webhook público para operar, validación de firma, tokens de Meta para rotar; facturación separada con Meta | Solo Meta | Bajo |
| B — **AWS End User Messaging Social** ✅ | Integración nativa con AWS: IAM, SNS, CloudTrail y KMS; sin webhook público para WhatsApp ni tokens de Meta que gestionar; facturación consolidada en AWS; Meta verifica la entrega | Tarifa por mensaje de AWS; un único destino de eventos por WABA; hay que migrar la WABA y los números | USD 0,005 saliente / 0,001 entrante, más Meta | Medio: el transporte es propietario, pero el formato de mensaje es el de Meta |
| C — Proveedor BSP de WhatsApp (por ejemplo, la plataforma de atención) | Puede traer bandeja de agentes incluida | Agrega un tercero en el camino crítico; tarifas propias; depende de S-02 | Variable | Medio-alto |

## Decisión
Se adopta la **opción B**. Cambios sobre ADR-004:

1. **Entrada de WhatsApp:**
   - El WABA tiene como destino un **tópico SNS standard** cifrado con KMS. El tópico invoca a la **Lambda de ingreso**: invocación asíncrona con reintentos y DLQ.
   - Una *filter policy* del tópico descarta los **eventos de estado** (enviado, entregado, leído) que no se usan en el MVP. Los de error (`failed`) se envían a métricas.
2. **Orden y deduplicación:**
   - SNS standard no garantiza orden ni entrega única. Por eso la Lambda de ingreso **deduplica por el ID de mensaje de WhatsApp** (condición en DynamoDB) y encola en la **SQS FIFO**, con `MessageGroupId = canal + remitente`.
   - Desde ahí, el flujo de ADR-004 no cambia.
   - Si llegan desordenados dos mensajes casi simultáneos del mismo cliente, se procesan en el orden de llegada a la cola (riesgo aceptado: impacto bajo en una conversación de soporte).
3. **Salida de WhatsApp:** la Lambda de salida usa `SendWhatsAppMessage` con permisos IAM acotados al número de teléfono de la WABA.
4. **Chat web:** sin cambios. Sigue entrando por **API Gateway + WAF** y responde por la API del chat del e-commerce.
5. **Derivación a humano (P-11):**
   - Como el destino de eventos del WABA es único y apunta a la solución, **nuestra solución es la dueña del canal de WhatsApp**. Mientras atiende una persona, el orquestador reenvía los mensajes a la plataforma de atención y publica sus respuestas con `SendWhatsAppMessage`.
   - La plataforma de atención tiene que integrarse **por API** (canal personalizado o *custom channel*), no como dueña del número.
   - Si el cliente eligiera **Amazon Connect** como plataforma de atención, existe la alternativa nativa de usar Connect como destino de eventos. Se evalúa en ese caso.

## Consecuencias
- **Positivas:**
  - Desaparece el webhook público de WhatsApp y la gestión de tokens de Meta.
  - Todo queda auditado con CloudTrail y gobernado por IAM.
  - Meta fees y AWS se facturan juntos.
  - Resuelve el diseño de la derivación (P-11).
- **Negativas / trade-offs:**
  - **Costo:** suma ~USD 0,035 por sesión de WhatsApp (5 mensajes entrantes y 6 salientes). Con un 70% de sesiones por WhatsApp (S-20) son **~USD 24,50 cada 1.000 sesiones**, lo que **duplica el costo variable** (ver `costos.md`).
  - **Migración:** hay que migrar la WABA y los números actuales (S-18, P-12), con riesgo de corte del canal durante la migración. Se planifica fuera de campaña.
  - **Orden:** el orden lo asegura la cola FIFO a partir del ingreso, no SNS.
- **Ruta de salida:**
  - El payload de mensajes es el formato de Meta, así que pasar a la **WhatsApp Cloud API directa** (opción A) cambia solo el transporte de la Lambda de ingreso y de salida.
  - El control de la WABA se puede devolver a TiendaNorte según los términos del servicio.
