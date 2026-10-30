# Propuesta técnica — Asistente virtual de atención al cliente para TiendaNorte

| Campo | Valor |
|---|---|
| Cliente | TiendaNorte · Gerencia de Experiencia del Cliente |
| Preparado por | Célula IA — AI Solutions Engineering |
| Versión | 0.2 · borrador · 2026-10-30 |

## 1. Resumen ejecutivo

En cada Black Friday y Hot Sale, las consultas por WhatsApp y chat web de TiendaNorte se multiplican entre 5 y 8 veces. Son mayormente repetitivas (dónde está mi pedido, si hay stock, cómo hago un cambio), pero saturan al equipo de atención: las respuestas tardan horas y se pierden ventas porque nadie confirmó a tiempo si el producto estaba disponible.

Proponemos un **asistente virtual con IA** en **WhatsApp y en el chat del sitio** que resuelve solo las tres consultas más frecuentes con datos reales del e-commerce y del ERP, y que **pasa a una persona, con todo el contexto**, lo que no puede o no debe resolver. Se construye sobre servicios **gestionados y serverless de AWS** (Amazon Bedrock con modelos Claude, Bedrock AgentCore y AWS End User Messaging para WhatsApp): escala solo en las campañas y no requiere equipo de infraestructura.

El plan llega a **producción antes de la próxima campaña** (unos dos meses) y el gasto acompaña al uso: **alrededor de USD 47 cada 1.000 conversaciones** más un piso de **unos USD 20 por mes**. La meta es que **al menos el 60% de las consultas se resuelva sin intervención humana**, para que el equipo se concentre en los casos que de verdad lo necesitan.

## 2. Entendimiento del problema

> Para negocio: el cuello de botella no es la complejidad de las consultas, sino su volumen en pocos días del año.

TiendaNorte vende electrodomésticos y electrónica online y en 15 sucursales. Cuenta con un e-commerce con API, un CRM, un ERP que expone stock y pedidos por API (con limitaciones documentadas a relevar) y la WhatsApp Business API contratada. Como no tiene equipo de infraestructura, la solución tiene que operarse sola, costar en proporción al uso y no atar a la empresa a un único proveedor.

El asistente resuelve de punta a punta las tres consultas que explican la mayor parte del volumen: el **estado de un pedido online**, previa identificación con el número de pedido y un segundo dato (DNI, email o teléfono); la **disponibilidad de un producto** online y en cada sucursal, con el link de compra para no perder la venta; y los **cambios y devoluciones**, que en esta etapa se responden con la política vigente. Un reclamo, un tema fuera de alcance, un cliente molesto o el pedido de hablar con alguien se derivan a una persona. Donde la información de preventa es incompleta trabajamos con supuestos explícitos; los cinco de mayor impacto están en la sección 6.

## 3. Solución propuesta

> Para negocio: el cliente escribe como siempre y lo atiende un asistente que conoce sus pedidos, el stock y las políticas de TiendaNorte.

### Cómo funciona una conversación

Cada mensaje pasa por **controles de entrada** que detectan manipulaciones, contenido ofensivo y datos sensibles como tarjetas. El asistente entiende qué necesita el cliente y elige el camino: lo identifica antes de mostrar un pedido, consulta el stock en el ERP o busca la política en la base de conocimiento. Antes de responder, un **control de salida** verifica que todo esté respaldado por los sistemas o por las políticas oficiales. La sesión se cierra a los 15 minutos sin actividad o a los 10 turnos, y la derivación a una persona puede ocurrir en cualquier momento.

![Flujo de atención (resumen)](../02-arquitectura/diagramas/export/flujo-resumen.drawio.png)

### Arquitectura

Los mensajes de WhatsApp llegan por **AWS End User Messaging Social** y los del chat web por **API Gateway con WAF**. Una **cola SQS FIFO** absorbe los picos y entrega cada conversación en orden a un **orquestador de sesión** que controla turnos, tiempos, guardrails y derivación. El agente se define por configuración en **AgentCore Harness**, sin código de orquestación propio, y razona con **Claude Haiku 5.5**, que escala a **Claude Sonnet 5.5** solo en los casos complejos. Las consultas a los sistemas pasan por **AgentCore Gateway** con herramientas de solo lectura, y las políticas viven en una **Knowledge Base gestionada**.

![Arquitectura de despliegue](placeholder-despliegue)

| Capa | Qué resuelve | Servicios |
|---|---|---|
| Canales | Mensajes de WhatsApp y del chat web | End User Messaging Social · API Gateway + WAF |
| Entrada y sesión | Picos, orden por conversación y control de sesión | Lambda · SQS FIFO · DynamoDB |
| Agente e IA | Entender, buscar datos y redactar | AgentCore Harness · Claude Haiku / Sonnet 5.5 |
| Controles | Manipulación, datos sensibles y respuestas sin respaldo | Bedrock Guardrails + controles en código |
| Integraciones | Pedidos, stock y políticas en solo lectura | AgentCore Gateway (MCP) · Knowledge Base |

El diseño prioriza la **seguridad**: un pedido solo se muestra si el cliente se identificó en la sesión, lo valida el código y no el modelo, y los datos personales se guardan enmascarados por 90 días. También prioriza la **portabilidad**: el modelo se cambia por configuración, las integraciones usan el estándar abierto MCP y cada servicio propietario tiene documentada su ruta de salida. Y busca la **operación mínima**: no hay servidores que mantener y volver a una versión anterior es inmediato. A las APIs del cliente les pedimos responder en 2 segundos o menos, mantener el stock con no más de 15 minutos de atraso y estar disponibles el 99,5% del tiempo en campaña; la caché amortigua lo que falte.

### Costos y escalabilidad

> Para negocio: se paga por uso y el costo por conversación baja a medida que crece el volumen.

El costo variable ronda los **USD 47 cada 1.000 conversaciones**: la mitad es mensajería de WhatsApp (USD 24,50), y el resto se reparte entre modelos de IA (USD 9), ejecución del agente (USD 6,70) y guardrails (USD 5,70). El fijo es de **unos USD 20 por mes**. Con una contención del 60%, cada consulta resuelta sin una persona cuesta **unos 8 centavos de dólar**.

| Escenario | Conversaciones por mes | Costo total por mes | Costo por conversación |
|---|---|---|---|
| Unidad de cálculo | 1.000 | USD 67 | USD 0,067 |
| Mes de campaña (x8) | 8.000 | USD 398 | USD 0,050 |
| Operación media | 45.000 | USD 2.148 | USD 0,048 |
| Alto volumen | 150.000 | USD 7.115 | USD 0,047 |

La estimación de referencia está en [AWS Pricing Calculator](https://calculator.aws/#/estimate?id=93d4b868060b93c5c70f89ff7fd2f50cb11943aa). Como la calculadora no tiene WhatsApp, Guardrails ni la Knowledge Base, esos montos se suman con los valores de esta sección. Antes del pico se dimensionan las cuotas de Bedrock y se valida todo con una prueba de carga x8.

## 4. Alcance

> Para negocio: el MVP resuelve el problema concreto de la campaña; lo demás queda en un roadmap que se prioriza con datos reales de uso.

### 4.1 Qué hacemos ahora (MVP)

| Capacidad | Qué incluye | Límite |
|---|---|---|
| Canales | Un mismo asistente en WhatsApp y en el chat del sitio | Solo texto |
| Estado de pedido | Estado, fechas y tracking, previa identificación del cliente | Solo pedidos online |
| Stock | Disponibilidad online y en las 15 sucursales, con link de compra | Sin reserva de stock |
| Cambios, devoluciones y FAQs | Política vigente y preguntas frecuentes cargadas por TiendaNorte | Solo informativo |
| Derivación a una persona | Transferencia con historial, resumen y motivo | Usa la plataforma de atención de TiendaNorte |
| Seguridad y operación | Guardrails, datos personales enmascarados y acompañamiento en campaña | Operación mensual posterior, aparte |

### 4.2 Qué no hace el MVP

1. **Iniciar cambios o devoluciones:** requiere escribir en los sistemas del cliente.
2. **Compras de sucursal y tracking del operador logístico:** suman integraciones.
3. **Avisos proactivos del pedido:** requieren plantillas de WhatsApp con costo de Meta.
4. **Recomendación de productos:** amplía el alcance y el riesgo comercial.
5. **Audio, imágenes y autogestión de FAQs:** no son necesarios para las consultas de campaña.

Tampoco forman parte del proyecto la plataforma de atención, la redacción de las políticas, los cambios en el e-commerce, el ERP o el CRM, y los costos de AWS y Meta, que corren por cuenta de TiendaNorte.

### 4.3 Roadmap futuro

Después de la campaña, la **Fase 2** amplía la autogestión: el asistente pasa a iniciar cambios y devoluciones, a responder por compras de sucursal y por el envío en vivo del operador logístico, a avisar de forma proactiva cuando un pedido sale y a usar el contexto del CRM para personalizar la atención. Cada una de estas evoluciones depende de algo que hoy no existe o no está relevado, como APIs de escritura, la API del operador logístico o plantillas aprobadas por Meta, y por eso conviene encararlas con la base ya en producción.

La **Fase 3** apunta al crecimiento comercial: recomendación de productos y asistencia a la venta, soporte para audio e imágenes en WhatsApp y una herramienta para que el área de CX publique sus propias FAQs. El orden de ambas fases no es fijo: lo define el informe post-campaña, en especial los motivos de derivación registrados durante la campaña. Si la mayoría de las conversaciones que pasan a una persona son por cambios y devoluciones, esa evolución va primero.

### 4.4 Cómo se acepta el MVP

El MVP se acepta cuando la gerencia CX aprueba el UAT, la contención supera el 60% en el set de evaluación y la prueba de carga x8 termina sin mensajes perdidos.

## 5. Estimación de esfuerzo

| Fase | Objetivo | Entregables principales |
|---|---|---|
| F0 · Descubrimiento y PoC | Validar supuestos y riesgos técnicos | Supuestos validados, PoC, plan de migración de WhatsApp |
| F1 · Fundaciones | Cuentas, seguridad y entrega continua | Ambientes, infraestructura como código, pipelines |
| F2 · Canales y sesión | Recibir y responder en ambos canales | WhatsApp y chat web integrados, cola, orquestador |
| F3 · Agente y conocimiento | Resolver pedidos, stock y políticas | Agente, 6 herramientas, Knowledge Base |
| F4 · Guardrails y evaluación | Seguridad y calidad medibles | Guardrails calibrados, set de evaluación |
| F5 · Derivación a humano | Pasar a una persona con contexto | Conector con la plataforma de atención |
| F6 · Pruebas y UAT | Demostrar capacidad de campaña | Prueba de carga x8, aprobación de negocio |
| F7 · Go-live y acompañamiento | Producción estable en campaña | Salida gradual, guardia, informe post-campaña |

Las fases de canales, agente y guardrails avanzan en paralelo y la derivación arranca en cuanto se define la plataforma de atención. La migración de WhatsApp, las cuotas de Bedrock y los accesos a los entornos de prueba se inician la primera semana, porque dependen de terceros. El equipo de la Célula IA reúne perfiles de solutions engineering, arquitectura, IA, backend, DevOps, QA y gestión; del lado de TiendaNorte necesitamos referentes de CX, TI, la plataforma de atención y Meta Business.

## 6. Riesgos y supuestos

Estos son los cinco riesgos de mayor impacto; el registro completo incluye quince, cada uno con su contingencia.

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| No llegar a producción antes de la campaña | Alta | Alto | MVP acotado, fases en paralelo y salida parcial como contingencia |
| APIs del ERP por debajo de los mínimos | Alta | Medio | Relevamiento en F0, caché y corte automático ante fallas |
| AgentCore Harness sin las capacidades o el SLA necesarios | Media | Alto | PoC en F0 y alternativa sobre AgentCore Runtime |
| Demora en la migración de WhatsApp a AWS | Media | Alto | Gestión desde F1 y número alternativo como plan B |
| Plataforma de atención sin integración por API | Media | Alto | Definición en F0, con Amazon Connect como alternativa |

La propuesta se apoya en estos cinco supuestos principales, que validamos en F0.

| Supuesto principal | Validar con |
|---|---|
| TiendaNorte provee la plataforma de atención, con API para las derivaciones | Gerencia CX |
| Las APIs del ERP y del e-commerce cumplen los mínimos de la sección 3 | TI / proveedor ERP |
| Las políticas y FAQs validadas llegan antes de la mitad de F3 | Gerencia CX |
| La cuenta y el número de WhatsApp se pueden migrar a AWS | TI / proveedor actual |
| La solución se despliega en una cuenta AWS de TiendaNorte | Gerencia CX / Finanzas |

## 7. Próximos pasos

Proponemos una reunión de validación con Experiencia del Cliente y TI para confirmar estos supuestos, definir la plataforma de atención y relevar el ERP. Con esas respuestas cerramos la estimación de tiempos con delivery, actualizamos las tarifas y quedamos listos para el kickoff, iniciando desde la primera semana la migración de WhatsApp, las cuotas y los accesos.
