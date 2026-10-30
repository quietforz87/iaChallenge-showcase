# Modelo de costos y escalado — Escenario 01 · TiendaNorte

> Para negocio: operar el asistente cuesta **alrededor de USD 47 cada 1.000 sesiones**, más un piso fijo
> de **~USD 20 por mes**. El gasto crece en proporción al uso: si la solución tiene éxito, cada sesión
> adicional cuesta unos 5 centavos, y cada consulta resuelta sin intervención humana, unos 8 centavos.
> La mitad del costo variable es la mensajería de WhatsApp a través de AWS End User Messaging Social (ADR-007).
> El agente corre en AgentCore Harness (ADR-001), sin red privada que pagar como costo fijo.

- **Unidad de cálculo:** 1.000 sesiones/mes (S-07). Una sesión dura hasta la derivación, 15 minutos de inactividad o 10 turnos (S-08).
- **Fuentes de precios** (consultadas el 2026-10-29, en USD, sin impuestos):
  - [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/): Guardrails y Managed Knowledge Base.
  - [AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/): Runtime, Gateway y Memory.
  - [End User Messaging pricing](https://aws.amazon.com/end-user-messaging/pricing/): WhatsApp.
  - Tarifas de Claude: lista de Anthropic, que coincide con el perfil `global.` de Bedrock según fuentes secundarias.
  - **Antes de enviar la propuesta, verificar en la página oficial** las tarifas de Bedrock para Claude, en particular la de lectura de caché.

## 1. Parámetros del modelo

| ID | Parámetro | Valor supuesto | Cómo se valida |
|---|---|---|---|
| C-01 | Turnos promedio por sesión | 5 (máximo 10) | Métricas de la primera campaña |
| C-02 | Llamadas al LLM por turno | 1,8 (decisión + respuesta con datos) | Trazas del agente |
| C-03 | Tokens de entrada por llamada | 2.000 sin caché + 3.000 en caché (system prompt y tools) | `usage` de Converse |
| C-04 | Tokens de salida por llamada | 250 en Haiku / 300 en Sonnet (incluye razonamiento con effort bajo) | `usage` de Converse |
| C-05 | Sesiones que escalan a Sonnet 5.5 | 15% (4 de 9 llamadas en Sonnet) | Métrica de escalamiento (ADR-002) |
| C-06 | Unidades de texto en Guardrails (`ApplyGuardrail`) | Por turno: entrada 1 · salida 1 · grounding 3. Por retrieve: 2 (prompt attack sobre los fragmentos). 1 unidad = 1.000 caracteres | Métricas de Guardrails |
| C-07 | Retrieves a la base de conocimiento por sesión | 0,6 | Trazas de tools |
| C-08 | Costo de cómputo del agente (AgentCore Harness, que corre sobre la infraestructura de Runtime) por sesión | USD 0,0067: ejemplo publicado por AWS para un agente de soporte en Runtime, tomado como valor de referencia | Facturación real de la PoC (la microVM por sesión de Harness puede variarlo) |
| C-09 | Mensajes de WhatsApp por sesión | 5 entrantes + 6 salientes (saludo, respuestas, aviso de cierre o derivación) | Métricas de End User Messaging |
| C-10 | Sesiones por WhatsApp | 70%; el resto por chat web (S-20) | Volúmenes por canal del cliente (P-05) |

## 2. Tarifas utilizadas

| Componente | Tarifa |
|---|---|
| Claude Haiku 5.5 (prompts < 100K) | Entrada $0,10 / M · salida $0,50 / M · escritura de caché $0,125 / M · lectura de caché $0,01 / M (supuesto: 10% de la entrada) |
| Claude Sonnet 5.5 | Entrada $2,00 / M · salida $10,00 / M · escritura de caché $2,50 / M · lectura de caché $0,20 / M |
| Bedrock Guardrails | Filtros de contenido $0,15 · temas denegados $0,15 · información sensible $0,10 · grounding $0,10 (cada 1.000 unidades de texto; regex sin costo) |
| Managed Knowledge Base | $1,00 cada 1.000 Retrieve · $5 por GB-mes de datos crudos |
| AgentCore Runtime (v2 por consumo; base de Harness) | $0,1276 por vCPU-hora · $0,0169 por GB-hora · la CPU no cobra durante la espera de I/O |
| AgentCore Gateway | $0,005 cada 1.000 invocaciones |
| AgentCore Memory (corto plazo) | $1,00 por GB ingerido (mínimo de 12 KB por evento) · $0,20 por GB recuperado |
| End User Messaging Social (WhatsApp) | **$0,005 por mensaje saliente · $0,001 por mensaje entrante**, más la tarifa de Meta (que AWS factura según el tarifario de Meta) |

## 3. Costo variable cada 1.000 sesiones

| Componente | Cálculo resumido | USD / 1.000 sesiones | % |
|---|---|---|---|
| Mensajería WhatsApp (End User Messaging Social) | 70% × (5 × $0,001 + 6 × $0,005) | **24,50** | 52% |
| LLM (Haiku 5.5 + escalamiento a Sonnet 5.5) | 85% × $0,0036 + 15% × $0,0400 por sesión | **9,04** | 19% |
| AgentCore Harness (cómputo) | C-08 | **6,70** | 14% |
| Bedrock Guardrails (`ApplyGuardrail`) | 5 turnos × $0,0011 + 0,6 retrieves × $0,0003 | **5,70** | 12% |
| Knowledge Base (Retrieve) | 0,6 × $0,001 | 0,60 | 1% |
| Serverless + observabilidad (API Gateway, SNS, Lambda, SQS, DynamoDB, CloudWatch) | Estimación por requests y logs | 0,60 | 1% |
| AgentCore Memory | 10 eventos × 12 KB | 0,15 | <1% |
| AgentCore Gateway | ~5 invocaciones por sesión | 0,03 | <1% |
| **Total variable** | | **≈ 47,30** (USD 0,047 por sesión) | 100% |

> La tarifa de **Meta** no se suma porque las respuestas del MVP son **mensajes de servicio dentro de la ventana de atención que abre el cliente**, que según la política vigente de Meta no tienen cargo. Hay que verificarlo en el tarifario de Meta que publica AWS. Los mensajes de plantilla (por ejemplo, notificaciones proactivas) quedan fuera del MVP (US-W6).

## 4. Costo fijo mensual (independiente del volumen)

| Componente | USD / mes | Nota |
|---|---|---|
| AWS WAF (web ACL + reglas, chat web) | ~10 | |
| CloudWatch (dashboard + alarmas) | ~4 | |
| AWS KMS (3 claves) | 3 | |
| Secrets Manager / credenciales | ~2 | |
| Almacenamiento de la Knowledge Base (< 0,1 GB) | < 1 | |
| **Total fijo** | **≈ 20** | Harness sin modo VPC (ADR-001): sin endpoints privados ni NAT. End User Messaging Social no tiene cargo fijo |

## 5. Cómo escala el gasto

| Escenario | Sesiones/mes | Variable | Fijo | **Total/mes** | Costo por sesión |
|---|---|---|---|---|---|
| Unidad de cálculo | 1.000 | $47 | $20 | **$67** | $0,067 |
| Campaña sobre esa base (x8) | 8.000 | $378 | $20 | **$398** | $0,050 |
| Operación media (supuesto de referencia) | 45.000 | $2.129 | $20 | **$2.148** | $0,048 |
| Éxito / alto volumen | 150.000 | $7.095 | $20 | **$7.115** | $0,047 |

- **Lineal y sin escalones:** todos los componentes variables cobran por uso. No hay servidores encendidos ni capacidad reservada; en los meses sin campaña se paga solo lo que se usa.
- **El costo por sesión baja con el volumen:** el piso fijo es chico y se diluye rápido. Arriba de ~5.000 sesiones/mes el costo unitario se estabiliza en ~USD 0,05.
- **Costo por consulta resuelta sin humano:** con contención del 60% (S-17), ~USD 0,08.
- **Sensibilidad al prompt caching:** si el loop gestionado de Harness no aplica caché de prompts (a validar en la PoC), el LLM pasa de ~$9 a ~$13 y el total variable a **~USD 51 cada 1.000 sesiones**.
- **Sensibilidad al canal:** cada 10 puntos de sesiones que pasan de chat web a WhatsApp suman ~USD 3,50 cada 1.000 sesiones.

### Palancas de ahorro (en orden de impacto)
1. **Menos mensajes salientes por sesión:** agrupar en un solo mensaje lo que hoy saldría en varios (saludo + respuesta, respuesta + aviso de cierre). Cada mensaje saliente menos por sesión de WhatsApp ahorra ~USD 3,50 cada 1.000 sesiones.
2. **Guardrails selectivos:** temas denegados solo en la entrada y grounding solo en los turnos con datos. Ahorro estimado: −30% a −40% del rubro. Además, un mensaje bloqueado en la entrada no invoca al Harness.
3. **Tasa de escalamiento a Sonnet:** cada 5 puntos menos de escalamiento ahorran ~USD 1,8 cada 1.000 sesiones.
4. **Prompt caching:** prefijo estable (system prompt y tools); verificar en la PoC que Harness lo aproveche (`cacheReadInputTokens > 0` en los eventos `metadata`).
5. **Cierre temprano** de sesiones resueltas (despedida detectada), para reducir turnos y mensajes por sesión.
6. **Volumen alto sostenido:** comparar el costo de End User Messaging con la WhatsApp Cloud API directa (ADR-007, opción A). La ruta de salida está documentada.

### No incluido
- **Tarifas de Meta por mensajes de plantilla**, si en etapas posteriores se envían mensajes proactivos.
- **Plataforma de atención humana** (S-02).
- **Servicio mensual de operación de la Célula IA** (S-16): se cotiza en la propuesta comercial.
- **Desarrollo e implementación:** ver `03-estimacion/`.
- **Ambientes no productivos:** desarrollo y QA, estimados en un 10–20% adicional del costo fijo. Usan un número de WhatsApp de prueba.

## 6. Capacidad en el pico (requerimientos a las APIs y cuotas)

Supuestos de concentración para una campaña:
- El mes de campaña tiene x8 sesiones.
- El 50% se concentra en 4 días.
- La hora pico concentra el 15% del día.
- El minuto pico es 3 veces el promedio de la hora pico.

| Magnitud (cada 1.000 sesiones/mes de base) | Valor en el minuto pico |
|---|---|
| Turnos de clientes | ~38 por minuto |
| Llamadas a tools (APIs del cliente) | **~0,5 req/s** → mínimo exigido: **1 req/s cada 1.000 sesiones/mes de base** (margen x2) |
| Llamadas al LLM | ~68 por minuto |
| Cuota TPM reservada (entrada sin caché + `maxTokens` 1.024) | ~0,2 M TPM |
| Mensajes salientes de WhatsApp | ~0,5 por segundo |

- **Escala lineal:** con una base de 45.000 sesiones/mes, el pico requiere ~45 req/s a las APIs, antes de la caché, ~9 M TPM de cuota de LLM y ~20 mensajes/s salientes de WhatsApp.
- **Throughput de WhatsApp:** depende del **nivel de mensajería y del throughput del número que asigna Meta**. Hay que verificar el nivel actual del número de TiendaNorte y los límites de la cuenta de End User Messaging Social antes de la campaña (P-12).
- **Caché de stock y pedidos** (ADR-003): reduce la carga real sobre el ERP.
- **Cuotas de Bedrock:** se revisan y, si hace falta, se solicita aumento al menos **3 semanas antes** de la campaña (ver la skill `amazon-bedrock`, `references/quota-health.md`).

## 7. Estimación en AWS Pricing Calculator

- **Enlace:** [TiendaNorte - Asistente virtual IA - 1000 sesiones por mes](https://calculator.aws/#/estimate?id=93d4b868060b93c5c70f89ff7fd2f50cb11943aa) (creada el 2026-10-30).
- **Parámetros:** unidad de cálculo de 1.000 sesiones/mes, región `us-east-1`, **sin Free Tier**.
- **Incluye:** Claude Haiku 5.5 y Sonnet 5.5 (Bedrock, perfil global, caché 60%); AgentCore Runtime (representa a Harness), Gateway y Memory; Lambda; SQS FIFO; SNS; API Gateway; DynamoDB; S3; WAF; KMS; Secrets Manager; CloudWatch.
- **No incluido, porque la calculadora no tiene esos servicios:** hay que sumarlo al total de la calculadora con los valores de la sección 3.

| Componente | USD cada 1.000 sesiones |
|---|---|
| AWS End User Messaging Social (WhatsApp) | ~24,50 |
| Bedrock Guardrails (`ApplyGuardrail`) | ~5,70 |
| Managed Knowledge Base (Retrieve + almacenamiento) | ~1,10 |
| EventBridge Scheduler | Despreciable |

- **Aproximaciones:**
  - **Modelos:** la calculadora exige solicitudes por minuto enteras, así que se cargó el mínimo de solicitudes y se escalaron los tokens por solicitud para que el total mensual coincida con C-02 a C-05.
  - **Harness:** se modela como AgentCore Runtime (300 s por sesión, 80% de espera de I/O, 1 vCPU, 2 GB), por lo que puede diferir de C-08.
- **Mantenimiento:** el enlace apunta a una copia guardada. Si cambian los parámetros de este documento, hay que generar una estimación nueva y actualizar el enlace.

