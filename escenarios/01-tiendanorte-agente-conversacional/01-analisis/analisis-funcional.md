# Análisis funcional — Escenario 01 · TiendaNorte

> Para negocio: quiénes usan la solución, qué necesita hacer cada uno y cómo vamos a comprobar que
> funciona. Es la base para el alcance del MVP y para las pruebas de aceptación.

- **Fuentes:** `entendimiento.md` (casos de uso CU-01 a CU-05), `supuestos.md` (S-01 a S-17) y el brief.
- **Convenciones:**
  - Personas `PER-xx`, épicas `EP-xx`, historias `US-xx`, criterios `US-xx.n`.
  - Los criterios usan el formato *Dado / Cuando / Entonces*.
  - La prioridad sigue MoSCoW: **M**ust · **S**hould · **C**ould · **W**on't (en el MVP).

---

## 1. Personas

### PER-01 — Comprador online en campaña
| | |
|---|---|
| **Perfil** | Compró online en Black Friday / Hot Sale. Usa sobre todo WhatsApp desde el celular. |
| **Objetivo** | Saber dónde está su pedido y cuándo llega, sin esperar. |
| **Dolor actual** | Demoras de horas en la respuesta durante la campaña; reenvía mensajes y se frustra. |
| **Qué valora** | Respuesta inmediata, datos concretos (estado, fecha, tracking) y no repetir información. |
| **Casos de uso** | CU-01, CU-04 |

### PER-02 — Cliente que evalúa una compra
| | |
|---|---|
| **Perfil** | Vio una oferta y quiere confirmar disponibilidad antes de comprar o ir a una sucursal. Usa el chat web y WhatsApp. |
| **Objetivo** | Saber si hay stock online o en una sucursal cercana para comprar ahora. |
| **Dolor actual** | Sin respuesta a tiempo, compra en otro lado: es la **venta perdida** que describe el brief. |
| **Qué valora** | Rapidez, disponibilidad por sucursal y un link directo para comprar. |
| **Casos de uso** | CU-02, CU-04 |

### PER-03 — Cliente en postventa
| | |
|---|---|
| **Perfil** | Recibió un producto y quiere cambiarlo o devolverlo. |
| **Objetivo** | Entender si puede hacerlo, en qué plazo y qué pasos seguir. |
| **Dolor actual** | Las políticas están dispersas; consulta a un humano para algo informativo. |
| **Qué valora** | Respuestas claras y consistentes con la política vigente. |
| **Casos de uso** | CU-03 |

### PER-04 — Agente humano de atención
| | |
|---|---|
| **Perfil** | Integra el equipo de atención de TiendaNorte y trabaja en la plataforma de atención del cliente (S-02). |
| **Objetivo** | Atender solo los casos que requieren una persona, con el contexto completo. |
| **Dolor actual** | Saturación por consultas repetitivas; pregunta otra vez lo que el cliente ya dijo. |
| **Qué valora** | Resumen de la conversación, motivo de la derivación y datos ya validados. |
| **Casos de uso** | CU-04 |

### PER-05 — Gerente de Experiencia del Cliente
| | |
|---|---|
| **Perfil** | Dueño de negocio de la solución; es el interlocutor de la propuesta. |
| **Objetivo** | Reducir la carga humana en campaña, sostener la experiencia y controlar el costo. |
| **Dolor actual** | No tiene visibilidad de volúmenes ni de resolución en tiempo real durante la campaña. |
| **Qué valora** | Contención ≥ 60% (S-17), costo por sesión y contenido de políticas bajo su control. |
| **Casos de uso** | Métricas, contenido, parámetros de sesión |

### PER-06 — Operador del servicio (Célula IA)
| | |
|---|---|
| **Perfil** | Integrante de la Célula IA que opera la solución después del go-live (S-16). |
| **Objetivo** | Mantener el servicio estable en el pico, detectar degradaciones y mejorar las respuestas. |
| **Dolor actual** | — (rol nuevo) |
| **Qué valora** | Alertas tempranas, trazas por sesión y despliegue seguro de cambios de prompts y FAQs. |
| **Casos de uso** | Operación y mejora continua |

---

## 2. Épicas

| Épica | Descripción | Personas |
|---|---|---|
| EP-01 | Canales y sesión | PER-01, PER-02, PER-03 |
| EP-02 | Identificación del cliente | PER-01 |
| EP-03 | Estado de pedido | PER-01 |
| EP-04 | Consulta de stock | PER-02 |
| EP-05 | Cambios y devoluciones (informativo) | PER-03 |
| EP-06 | Derivación a humano | PER-01..04 |
| EP-07 | Privacidad y datos | PER-05 |
| EP-08 | Gestión y operación | PER-05, PER-06 |
| EP-09 | Guardrails del agente | PER-01..03, PER-05, PER-06 |

---

## 3. User stories y criterios de aceptación

### EP-01 — Canales y sesión

#### US-01 · Conversar por WhatsApp — **M**
**Como** cliente (PER-01/02/03), **quiero** escribirle al número de WhatsApp de TiendaNorte y recibir
respuesta del asistente, **para** resolver mi consulta sin esperar a una persona.
*Refs: S-03, S-08*

- **US-01.1** Dado un cliente que escribe al número de WhatsApp, cuando envía su primer mensaje, entonces recibe un saludo que aclara que habla con un asistente virtual, lista en qué puede ayudar e incluye el aviso de privacidad.
- **US-01.2** Dado un mensaje entrante, cuando el asistente responde, entonces la respuesta llega por el mismo canal y conversación.
- **US-01.3** Dado un cliente que envía audio, imagen u otro formato no soportado, cuando el asistente lo recibe, entonces le pide que escriba su consulta en texto.
- **US-01.4** Dado un pico de campaña (x5–x8 del tráfico base), cuando llegan mensajes concurrentes, entonces ningún mensaje se pierde y todos reciben respuesta.

#### US-02 · Conversar por el chat web — **M**
**Como** cliente (PER-02), **quiero** usar el chat del sitio de TiendaNorte, **para** consultar sin salir de la página.
*Refs: S-03*

- **US-02.1** Dado un visitante del sitio, cuando abre el chat del e-commerce y escribe, entonces lo atiende el mismo asistente, con las mismas capacidades que en WhatsApp.
- **US-02.2** Dada una respuesta con un link de producto, cuando se muestra en el chat web, entonces el link es clickeable y abre la ficha del producto.

#### US-03 · Cierre de sesión por inactividad — **M**
**Como** gerente CX (PER-05), **quiero** que una sesión se cierre tras un período de inactividad, **para** acotar el costo y medir sesiones de forma consistente.
*Refs: S-08*

- **US-03.1** Dada una sesión activa, cuando pasan 15 minutos (parametrizable) sin mensajes del cliente, entonces la sesión se cierra y se registra con resultado "timeout".
- **US-03.2** Dada una sesión cerrada por timeout, cuando el cliente vuelve a escribir, entonces se inicia una nueva sesión con un saludo breve.

#### US-04 · Límite de turnos por sesión — **M**
**Como** gerente CX (PER-05), **quiero** limitar la cantidad de turnos por sesión, **para** evitar conversaciones improductivas y controlar el costo.
*Refs: S-08, S-14*

- **US-04.1** Dada una sesión, cuando el cliente llega a su turno 10 (parametrizable), entonces el asistente responde ese turno, informa que la conversación se cierra e invita a iniciar una nueva consulta.
- **US-04.2** Dado el cierre por límite de turnos, entonces **no** se deriva a un humano y la sesión se registra con resultado "límite de turnos".

### EP-02 — Identificación del cliente

#### US-05 · Identificarme para consultar un pedido — **M**
**Como** comprador online (PER-01), **quiero** identificarme con mi número de pedido y un dato personal, **para** que solo yo pueda ver la información de mi compra.
*Refs: S-06, S-14*

- **US-05.1** Dado un cliente que pregunta por su pedido, cuando no se identificó, entonces el asistente le pide el número de pedido y un segundo dato (DNI, email o teléfono).
- **US-05.2** Dado un número de pedido y un dato que coinciden con el pedido, cuando se validan, entonces el cliente queda identificado para el resto de la sesión y no se le vuelve a pedir.
- **US-05.3** Dado un número de pedido y un dato que no coinciden, cuando se validan, entonces el asistente informa que no pudo verificar los datos **sin revelar cuál falló** y permite reintentar.
- **US-05.4** Dados 2 intentos fallidos de identificación, entonces el asistente deriva a un humano con motivo "identificación fallida" (ver US-12).
- **US-05.5** Dado un cliente no identificado, cuando pide datos de un pedido, entonces el asistente nunca muestra información de ese pedido.

### EP-03 — Estado de pedido

#### US-06 · Consultar el estado de mi pedido online — **M**
**Como** comprador online (PER-01), **quiero** saber el estado de mi pedido, **para** saber cuándo me llega sin tener que esperar a una persona.
*Refs: S-10, CU-01*

- **US-06.1** Dado un cliente identificado, cuando consulta su pedido, entonces el asistente informa estado, fecha de compra, fecha estimada de entrega o retiro y, si existe, código o link de tracking.
- **US-06.2** Dado un pedido con varios productos en estados distintos, cuando se informa, entonces se detalla el estado de cada uno.
- **US-06.3** Dado un número de pedido de compra en sucursal (fuera del MVP), cuando no se encuentra en el canal online, entonces el asistente informa que solo puede consultar pedidos online y ofrece derivar a un humano.
- **US-06.4** Dado que la API de pedidos no responde o excede el tiempo máximo, cuando el asistente consulta, entonces informa que no puede consultarlo ahora y deriva a un humano con motivo "sistema no disponible".

### EP-04 — Consulta de stock

#### US-07 · Consultar disponibilidad de un producto — **M**
**Como** cliente que evalúa una compra (PER-02), **quiero** saber si un producto tiene stock online y en sucursales, **para** decidir dónde y cuándo comprarlo.
*Refs: S-09, CU-02*

- **US-07.1** Dado un cliente que nombra un producto, cuando hay una coincidencia clara en el catálogo, entonces el asistente informa disponibilidad online y en las sucursales con stock.
- **US-07.2** Dado un nombre ambiguo (por ejemplo "heladera Samsung"), cuando hay varias coincidencias, entonces el asistente muestra hasta 3 opciones para que el cliente elija.
- **US-07.3** Dado un cliente que menciona una sucursal o una localidad, cuando hay stock, entonces el asistente prioriza esa sucursal en la respuesta.
- **US-07.4** Dado un producto con stock online, cuando se informa, entonces se incluye el link de compra del e-commerce.
- **US-07.5** Dado un producto sin stock en ningún canal, cuando se informa, entonces el asistente lo comunica claramente y no promete fechas de reposición.
- **US-07.6** Dado que el dato de stock tiene más de 15 minutos de antigüedad, cuando se informa, entonces el asistente aclara que la disponibilidad es aproximada.
- **US-07.7** Dado que la API de stock no responde, entonces el asistente informa que no puede consultarlo ahora y deriva a un humano con motivo "sistema no disponible".

#### US-08 · No inventar productos ni precios — **M**
**Como** gerente CX (PER-05), **quiero** que el asistente solo informe productos y datos que existen en los sistemas, **para** no generar expectativas falsas ni reclamos.
*Refs: S-13*

- **US-08.1** Dado un producto que no existe en el catálogo, cuando el cliente lo consulta, entonces el asistente informa que no lo encontró y no sugiere productos inventados.
- **US-08.2** Dada cualquier respuesta con stock, estado o link, entonces todo dato proviene de una consulta a los sistemas en esa sesión, nunca del conocimiento general del modelo.

### EP-05 — Cambios y devoluciones (informativo)

#### US-09 · Conocer la política de cambios y devoluciones — **M**
**Como** cliente en postventa (PER-03), **quiero** saber si puedo cambiar o devolver un producto y cómo hacerlo, **para** hacer el trámite correctamente.
*Refs: S-05, S-12, CU-03*

- **US-09.1** Dado un cliente que pregunta por cambios o devoluciones, cuando el asistente responde, entonces la respuesta se basa exclusivamente en las políticas cargadas por el cliente e incluye plazos, condiciones y pasos.
- **US-09.2** Dada una pregunta que la base de conocimiento no cubre, cuando el asistente no encuentra la respuesta, entonces lo dice explícitamente y no improvisa una política.
- **US-09.3** Dado el flujo de cambios y devoluciones, cuando el asistente termina de informar, entonces **no** ofrece derivar a un humano.
- **US-09.4** Dado un cliente que, en el mismo flujo, pide explícitamente hablar con una persona, entonces aplica US-11 (el pedido explícito siempre prevalece).

#### US-10 · Consultar otras FAQs de la base de conocimiento — **S**
**Como** cliente, **quiero** consultar envíos, garantías y otras preguntas frecuentes cargadas por TiendaNorte, **para** no depender de una persona en temas informativos.
*Refs: S-12, S-13*

- **US-10.1** Dada una pregunta cubierta por la base de conocimiento, cuando el asistente responde, entonces se basa solo en ese contenido.
- **US-10.2** Dada una pregunta no cubierta, entonces se trata como fuera de alcance (US-14).

### EP-06 — Derivación a humano

#### US-11 · Pedir hablar con una persona — **M**
**Como** cliente, **quiero** poder pedir hablar con una persona en cualquier momento, **para** no quedar atrapado con el asistente.
*Refs: S-14*

- **US-11.1** Dado un cliente que pide hablar con una persona (con distintas formulaciones), cuando el asistente lo detecta, entonces transfiere la conversación a la plataforma de atención sin intentar retenerlo.
- **US-11.2** Dada una transferencia, cuando se completa, entonces el cliente recibe un mensaje que confirma la derivación.
- **US-11.3** Dada una transferencia, cuando no hay agentes disponibles, entonces la plataforma de atención gestiona la espera y los horarios (S-02); el asistente no promete tiempos.

#### US-12 · Derivación por fallo del asistente — **M**
**Como** cliente, **quiero** que me pasen con una persona cuando el asistente no puede ayudarme, **para** no perder tiempo.
*Refs: S-14*

- **US-12.1** Dados 2 intentos consecutivos en los que el asistente no entiende la intención, entonces deriva a un humano con motivo "intención no comprendida".
- **US-12.2** Dada una identificación fallida (US-05.4) o una API no disponible (US-06.4, US-07.7), entonces deriva con el motivo correspondiente.

#### US-13 · Derivación por molestia o reclamo — **M**
**Como** gerente CX (PER-05), **quiero** que un cliente molesto o con un reclamo pase a una persona, **para** proteger la experiencia y la marca.
*Refs: S-14*

- **US-13.1** Dado un mensaje con enojo o frustración evidente, o un reclamo, cuando el asistente lo detecta, entonces deriva a un humano con motivo "molestia / reclamo".
- **US-13.2** Dado un caso de prueba del set de evaluación con molestia explícita, entonces se deriva en al menos el [[COMPLETAR: % a acordar]] de los casos.

#### US-14 · Derivación de consultas fuera de alcance — **M**
**Como** cliente, **quiero** que una consulta que el asistente no atiende llegue a una persona, **para** obtener respuesta igual.
*Refs: S-13*

- **US-14.1** Dada una consulta fuera de los casos del MVP (asesoramiento, facturación, reclamos, pedidos de sucursal), cuando el asistente la identifica, entonces informa que lo va a atender una persona y deriva con motivo "fuera de alcance".
- **US-14.2** Dada una consulta sin relación con TiendaNorte o un intento de manipular al asistente, entonces el asistente se niega cortésmente y vuelve a su propósito, sin derivar (detalle en US-22 y US-23).

#### US-15 · Recibir la conversación derivada con contexto — **M**
**Como** agente humano (PER-04), **quiero** recibir la conversación derivada con su historial y un resumen, **para** no volver a preguntarle al cliente lo que ya dijo.
*Refs: S-02*

- **US-15.1** Dada una derivación, cuando llega a la plataforma de atención, entonces incluye canal, historial de mensajes, resumen breve, intención detectada, motivo de derivación y, si existe, el número de pedido validado.
- **US-15.2** Dada una derivación, cuando el agente humano toma el caso, entonces continúa la conversación en el mismo canal y el asistente deja de responder en esa conversación.
- **US-15.3** Dada una conversación tomada por un humano, cuando el humano la cierra, entonces la próxima interacción del cliente vuelve a iniciar con el asistente [[COMPLETAR: confirmar comportamiento con la plataforma de atención]].

### EP-07 — Privacidad y datos

#### US-16 · Proteger los datos personales — **M**
**Como** gerente CX (PER-05), **quiero** que los datos personales de los clientes estén protegidos, **para** cumplir la normativa y evitar riesgos.
*Refs: S-15, S-11*

- **US-16.1** Dada una transcripción almacenada, entonces DNI, email y teléfono están enmascarados.
- **US-16.2** Dada una transcripción con más de 90 días, entonces se elimina automáticamente.
- **US-16.3** Dados los logs técnicos de la plataforma, entonces no contienen PII sin enmascarar, o están cifrados y con acceso restringido.
- **US-16.4** Dado cualquier cliente, el asistente nunca revela datos de otro cliente ni datos completos sensibles (por ejemplo la dirección completa); los muestra parcialmente.

### EP-08 — Gestión y operación

#### US-17 · Ver métricas de la operación — **M**
**Como** gerente CX (PER-05), **quiero** un tablero con volumen, contención y motivos de derivación, **para** evaluar el resultado de la campaña.
*Refs: S-17, S-07*

- **US-17.1** Dado el tablero, entonces muestra por día y por canal: sesiones, % de contención, derivaciones por motivo, cierres por timeout y por límite de turnos.
- **US-17.2** Dado el tablero, entonces muestra el costo estimado por 1.000 sesiones y el acumulado del mes.
- **US-17.3** Dado el tablero durante una campaña, entonces los datos se actualizan con no más de [[COMPLETAR: minutos]] de demora.

#### US-18 · Actualizar FAQs y políticas — **M**
**Como** gerente CX (PER-05), **quiero** que las políticas que responde el asistente se puedan actualizar, **para** reflejar cambios de campaña.
*Refs: S-12, S-16*

- **US-18.1** Dado un documento de política nuevo o modificado entregado por el cliente, cuando la Célula IA lo publica, entonces el asistente lo usa en un plazo máximo de [[COMPLETAR: horas hábiles]].
- **US-18.2** Dada una política publicada, entonces queda registrada la versión vigente y la fecha de publicación.

#### US-19 · Parametrizar límites de sesión — **S**
**Como** gerente CX (PER-05), **quiero** ajustar timeout y límite de turnos, **para** equilibrar experiencia y costo.
*Refs: S-08*

- **US-19.1** Dado un cambio de los valores de timeout o de turnos, cuando la Célula IA lo aplica, entonces rige para las sesiones nuevas sin redesplegar la solución.

#### US-20 · Monitorear y alertar degradaciones — **M**
**Como** operador del servicio (PER-06), **quiero** alertas ante errores, latencia alta o caída de integraciones, **para** actuar antes de que afecte la campaña.
*Refs: S-04, S-16*

- **US-20.1** Dada una API del cliente con tasa de error o latencia sobre el umbral, entonces se genera una alerta al operador en menos de [[COMPLETAR: minutos]].
- **US-20.2** Dado un throttling del servicio de LLM, entonces se genera una alerta y queda registrado.
- **US-20.3** Dada una sesión, entonces existe una traza consultable (mensajes enmascarados, tools invocadas, latencias, resultado) para diagnóstico.

#### US-21 · Evaluar la calidad antes de cada cambio — **S**
**Como** operador del servicio (PER-06), **quiero** un set de conversaciones de prueba que se evalúe en cada cambio de prompts o de contenido, **para** no degradar la calidad en producción.
*Refs: S-16, S-17*

- **US-21.1** Dado un cambio de prompts, modelo o contenido, cuando se corre el set de evaluación, entonces el cambio solo se publica si no baja el % de respuestas correctas ni el % de derivaciones correctas respecto de la versión vigente.

### EP-09 — Guardrails del agente

> Para negocio: son las reglas que el asistente no puede romper, sin importar lo que le escriban. Protegen
> al cliente, a la marca y a los sistemas de TiendaNorte.

#### Catálogo de guardrails

Cada guardrail se aplica en una de cuatro capas:
- **Entrada:** sobre el mensaje del cliente, antes de que lo procese el modelo.
- **Salida:** sobre la respuesta, antes de enviarla.
- **Herramientas:** sobre las consultas a los sistemas.
- **Sesión:** sobre el uso del canal.

El mecanismo previsto es referencial y se define en la etapa de arquitectura (ADR).

| ID | Guardrail | Capa | Acción ante una violación | Mecanismo previsto | Historia |
|---|---|---|---|---|---|
| GR-01 | Ataques de prompt (inyección, jailbreak, pedido de revelar instrucciones) | Entrada | Bloquear y responder con un mensaje estándar; no derivar | Filtro de prompt attack del servicio de guardrails + instrucciones del sistema | US-22 |
| GR-02 | Temas denegados (política, religión, salud, asesoría legal o financiera, competidores, temas ajenos a TiendaNorte) | Entrada / Salida | Negarse cortésmente y volver al propósito | Temas denegados configurables | US-23 |
| GR-03 | Contenido ofensivo (insultos, odio, sexual, violencia) | Entrada / Salida | Entrada: responder con límite respetuoso; si persiste o es un reclamo, derivar (US-13). Salida: bloquear | Filtros de contenido con umbral configurable | US-24 |
| GR-04 | Datos sensibles provistos por el cliente (tarjeta, CVV, contraseñas, claves bancarias) | Entrada | Enmascarar antes de procesar y almacenar; avisar que no debe compartirlos | Filtro de información sensible (PII / regex) | US-25 |
| GR-05 | PII en la respuesta (datos completos o de terceros) | Salida | Enmascarar parcialmente o bloquear | Filtro de información sensible + reglas de presentación | US-16.4, US-25 |
| GR-06 | Compromisos comerciales no respaldados (descuentos, precios no informados por el sistema, plazos, excepciones a la política) | Salida | Reformular sin compromiso o informar solo lo que dicen los sistemas y las políticas | Instrucciones del sistema + temas denegados + evaluación | US-26 |
| GR-07 | Respuestas no fundamentadas (alucinaciones) | Salida | Bloquear y responder "no tengo esa información"; si se repite, aplica US-12 | Verificación de grounding contra el resultado de las tools / la base de conocimiento | US-27, US-08, US-09 |
| GR-08 | Uso indebido de herramientas | Herramientas | Rechazar la invocación y registrarla | Validación de parámetros e identidad en la capa de tools (no delegada al modelo) | US-28 |
| GR-09 | Abuso del canal (flood, mensajes muy largos, automatización) | Sesión | Limitar y responder con un mensaje de espera; bloquear temporalmente si persiste | Rate limit por remitente + tamaño máximo de mensaje | US-29 |
| GR-10 | Tono y marca | Salida | — (calidad, se mide con evaluación) | Instrucciones del sistema + set de evaluación | US-30 |

#### US-22 · Resistir intentos de manipulación — **M**
**Como** gerente CX (PER-05), **quiero** que el asistente no pueda ser manipulado para salirse de su función, **para** evitar respuestas que dañen la marca o expongan información interna.
*Refs: GR-01*

- **US-22.1** Dado un mensaje que pide ignorar instrucciones, cambiar de rol o "actuar como" otro sistema, cuando el asistente lo recibe, entonces mantiene su rol y responde con el mensaje estándar de alcance.
- **US-22.2** Dado un pedido de revelar las instrucciones del sistema, la configuración, las herramientas o los datos internos, entonces el asistente no los revela.
- **US-22.3** Dado contenido proveniente de los sistemas (por ejemplo un nombre de producto o una nota de pedido) con instrucciones embebidas, entonces el asistente lo trata como dato y no lo ejecuta como instrucción.
- **US-22.4** Dado el set de evaluación de ataques de prompt, entonces se bloquea al menos el [[COMPLETAR: % a acordar]] de los casos sin afectar más del [[COMPLETAR: %]] de consultas legítimas (falsos positivos).

#### US-23 · Mantenerse dentro del dominio de TiendaNorte — **M**
**Como** gerente CX (PER-05), **quiero** que el asistente solo hable de temas de TiendaNorte, **para** evitar opiniones o asesoramiento que no corresponden.
*Refs: GR-02, S-13*

- **US-23.1** Dada una consulta sobre un tema denegado (política, religión, salud, asesoría legal o financiera), entonces el asistente se niega cortésmente y ofrece ayuda dentro de su alcance.
- **US-23.2** Dada una consulta que compara con competidores o pide opinión sobre ellos, entonces el asistente no opina sobre otras empresas.
- **US-23.3** Dada una consulta de TiendaNorte que está fuera de los casos del MVP, entonces **no** aplica este guardrail sino la derivación de US-14.
- **US-23.4** La lista de temas denegados es configurable por la Célula IA a pedido de la gerencia CX.

#### US-24 · Filtrar contenido ofensivo — **M**
**Como** cliente y como gerente CX, **quiero** que el asistente nunca responda con contenido ofensivo y maneje con respeto los mensajes agresivos, **para** proteger la experiencia y la marca.
*Refs: GR-03, S-14*

- **US-24.1** Dada cualquier respuesta generada, cuando contiene contenido ofensivo, entonces se bloquea y se reemplaza por un mensaje estándar.
- **US-24.2** Dado un mensaje del cliente con insultos, cuando es el primero, entonces el asistente responde con un límite respetuoso y continúa ayudando.
- **US-24.3** Dados insultos reiterados o un reclamo, entonces se aplica la derivación por molestia (US-13).

#### US-25 · Proteger datos sensibles que comparte el cliente — **M**
**Como** cliente, **quiero** que si comparto por error datos de mi tarjeta o una contraseña no queden expuestos, **para** no correr riesgos.
*Refs: GR-04, GR-05, S-15*

- **US-25.1** Dado un mensaje con un número de tarjeta, un CVV o una contraseña, cuando se recibe, entonces el dato se enmascara antes de procesarlo, almacenarlo o enviarlo a la plataforma de atención.
- **US-25.2** Dado ese caso, entonces el asistente avisa que no debe compartir esos datos y que TiendaNorte nunca los pide por chat.
- **US-25.3** Dada cualquier respuesta, entonces el asistente nunca solicita datos de tarjeta, contraseñas ni códigos de verificación.
- **US-25.4** Dada una respuesta con datos del cliente identificado, entonces se muestran parcialmente (por ejemplo email `j***@dominio.com` o los últimos 4 dígitos del teléfono).

#### US-26 · No asumir compromisos comerciales — **M**
**Como** gerente CX (PER-05), **quiero** que el asistente no prometa descuentos, precios, plazos ni excepciones que no estén respaldados, **para** evitar reclamos y obligaciones no deseadas.
*Refs: GR-06, S-05*

- **US-26.1** Dado un pedido de descuento, de mejor precio o de una excepción a la política, entonces el asistente no lo concede ni lo insinúa e informa la política vigente.
- **US-26.2** Dado un precio, un plazo de entrega o una fecha de reposición, entonces solo se informa si proviene de los sistemas; si no, el asistente no lo estima.
- **US-26.3** Dada una consulta sobre una garantía o un derecho del consumidor, entonces el asistente responde solo con el texto de las políticas cargadas y no lo interpreta legalmente.

#### US-27 · Responder solo con información fundamentada — **M**
**Como** gerente CX (PER-05), **quiero** que cada respuesta con datos esté respaldada por los sistemas o por la base de conocimiento, **para** que el cliente reciba información correcta.
*Refs: GR-07, US-08, US-09*

- **US-27.1** Dada una respuesta sobre pedidos, stock o políticas, cuando la verificación de grounding detecta información no respaldada por el resultado de las herramientas o por los documentos recuperados, entonces la respuesta se bloquea y el asistente informa que no tiene esa información.
- **US-27.2** Dadas 2 respuestas bloqueadas por grounding en la misma sesión, entonces se deriva por fallo del asistente (US-12).
- **US-27.3** Dado el set de evaluación, entonces la tasa de respuestas no fundamentadas es menor al [[COMPLETAR: %]].

#### US-28 · Usar las herramientas de forma segura — **M**
**Como** operador del servicio (PER-06), **quiero** que el asistente solo pueda consultar lo que corresponde, con los permisos mínimos, **para** proteger los datos y los sistemas de TiendaNorte.
*Refs: GR-08, S-04, S-06*

- **US-28.1** Dada cualquier herramienta disponible para el asistente, entonces es de **solo lectura**; no existe ninguna herramienta que modifique datos en el MVP.
- **US-28.2** Dada una consulta de pedido, entonces la capa de herramientas verifica que el pedido corresponde al cliente identificado en la sesión, **independientemente** de lo que indique el modelo.
- **US-28.3** Dados parámetros inválidos o fuera de formato (por ejemplo un número de pedido mal formado), entonces la herramienta los rechaza sin llamar al sistema del cliente.
- **US-28.4** Dado un turno, entonces el asistente no puede invocar más de [[COMPLETAR: N]] herramientas, para evitar bucles y costo descontrolado.
- **US-28.5** Dada cualquier invocación rechazada, entonces queda registrada para revisión (US-31).

#### US-29 · Prevenir el abuso del canal — **S**
**Como** operador del servicio (PER-06), **quiero** limitar el uso abusivo del canal, **para** proteger el costo y la disponibilidad durante la campaña.
*Refs: GR-09, S-07*

- **US-29.1** Dado un remitente que envía más de [[COMPLETAR: N]] mensajes por minuto, entonces se limita el procesamiento y se responde con un mensaje de espera.
- **US-29.2** Dado un mensaje que supera [[COMPLETAR: N]] caracteres, entonces se procesa solo hasta el máximo y se pide al cliente que resuma su consulta.
- **US-29.3** Dado un abuso sostenido, entonces el remitente se bloquea temporalmente durante [[COMPLETAR: minutos]] y queda registrado.

#### US-30 · Mantener el tono de la marca — **S**
**Como** gerente CX (PER-05), **quiero** que el asistente hable con el tono de TiendaNorte, **para** una experiencia coherente con la marca.
*Refs: GR-10*

- **US-30.1** Dada cualquier respuesta, entonces está en español rioplatense, con trato de "vos", cordial y breve (pensada para leer en el celular) [[COMPLETAR: validar guía de tono con la marca]].
- **US-30.2** Dada una respuesta, entonces el asistente no usa jerga técnica, no se presenta como una persona y no expresa opiniones personales.
- **US-30.3** Dado el set de evaluación, entonces la calificación de tono (revisión humana o LLM-as-a-judge) alcanza al menos [[COMPLETAR: puntaje]].

#### US-31 · Registrar y revisar intervenciones de guardrails — **S**
**Como** operador del servicio (PER-06), **quiero** ver cuándo y por qué intervino un guardrail, **para** ajustar umbrales y detectar ataques o falsos positivos.
*Refs: GR-01..GR-10, S-15*

- **US-31.1** Dada una intervención de guardrail, entonces se registra el guardrail, la capa, la acción y la sesión, con PII enmascarada.
- **US-31.2** Dado el tablero de operación, entonces muestra las intervenciones por tipo y por día.
- **US-31.3** Dado un pico anómalo de intervenciones (posible ataque o falso positivo masivo), entonces se genera una alerta al operador (US-20).

---

## 4. Fuera del MVP (Won't)

| ID | Historia | Motivo | Refs |
|---|---|---|---|
| US-W1 | Iniciar un trámite de cambio o devolución desde el chat | Requiere escribir en ERP / e-commerce | S-05 |
| US-W2 | Consultar pedidos hechos en sucursal | Acota el alcance | S-10 |
| US-W3 | Tracking en vivo del operador logístico | Integración adicional | S-10 |
| US-W4 | Recomendar productos según necesidad | Amplía alcance y riesgo | S-13 |
| US-W5 | Mensajes de voz e imágenes | No requerido en el MVP | — |
| US-W6 | Notificaciones proactivas (por ejemplo "tu pedido salió") | Fuera del pedido del cliente | — |
| US-W7 | Edición de FAQs por el cliente sin intervención de la Célula IA | La Célula IA opera el servicio | S-16 |

---

## 5. Trazabilidad

| Caso de uso | Historias |
|---|---|
| CU-01 Estado de pedido | US-05, US-06 |
| CU-02 Stock | US-07, US-08 |
| CU-03 Cambios y devoluciones | US-09, US-10 |
| CU-04 Derivación a humano | US-11, US-12, US-13, US-14, US-15 |
| CU-05 Cierre de sesión | US-03, US-04 |
| Transversales (canales, datos, operación) | US-01, US-02, US-16 a US-21 |
| Guardrails (GR-01 a GR-10) | US-22 a US-31 |

| Criterio del brief (B.2) | Historias |
|---|---|
| Escalabilidad x5–x8 | US-01.4, US-20 |
| Sensibilidad al costo | US-03, US-04, US-17.2 |
| Derivación a humano | US-11 a US-15 |
| Omnicanal | US-01, US-02 |
| Operación mínima | US-18, US-19, US-20, US-21, US-31 |
| Sensibilidad al costo (abuso / bucles) | US-28.4, US-29 |
