# Estimación de esfuerzo — Escenario 01 · TiendaNorte

> Para negocio: el trabajo se organiza en **8 fases**. Empieza con una prueba de concepto de dos semanas
> que confirma los puntos técnicos de mayor riesgo y termina con el acompañamiento de la campaña.
> Varias fases avanzan en paralelo para llegar a producción **antes de la próxima campaña (~2 meses)**.
> Los tiempos y el esfuerzo de cada fase quedan como **placeholders** para completar con el equipo de
> delivery, según lo pide el brief (B.1).

- **Fuentes:**
  - Alcance funcional: `01-analisis/analisis-funcional.md` (US-01 a US-31).
  - Arquitectura: `02-arquitectura/` (ADR-001 a ADR-007).
  - Supuestos: `01-analisis/supuestos.md`.
- **Restricción de plazo:** producción en ~2 meses desde el kickoff (brief B.2). Fecha de la campaña: [[COMPLETAR: fecha de la próxima campaña]].

---

## 1. Supuestos de la estimación

| ID | Supuesto | Impacto si no se cumple |
|---|---|---|
| E-01 | El cliente entrega **acceso a sandboxes** de las APIs de e-commerce y ERP, con la documentación de sus limitaciones, **durante F0** (P-02, P-10) | Bloquea F3 y corre el camino crítico |
| E-02 | Las **FAQs y políticas** validadas llegan **antes de la mitad de F3** (S-12, P-04) | El agente no puede responder políticas; no se cumple la contención |
| E-03 | La **plataforma de atención** queda definida, con API disponible, **al cierre de F0** (S-02, P-11) | F5 no puede empezar; la derivación queda en riesgo |
| E-04 | La **WABA y los números** se pueden migrar a End User Messaging Social, y el cliente aporta PIN y accesos a Meta Business **durante F1** (S-18, P-12) | Sin canal WhatsApp en producción. Plan B: número nuevo, con impacto en la comunicación al cliente final |
| E-05 | Existe una **cuenta AWS de TiendaNorte** con acceso para la Célula IA **en la primera semana** (S-19, P-13) | Retrasa F1 |
| E-06 | **AgentCore Harness** está disponible en `us-east-1` con las capacidades de ADR-001, y la PoC (F0) confirma los riesgos técnicos | Fallback a AgentCore Runtime con un agente Strands propio (ADR-001, opción B), con más esfuerzo en F3 |
| E-07 | La gerencia CX tiene disponibilidad para validaciones y UAT: [[COMPLETAR: horas por semana]] | UAT incompleto o tardío |
| E-08 | No hay cambios de alcance sobre el MVP definido (sección 4 del análisis funcional) | Re-estimación |

---

## 2. Fases

**Vista general** (las fases F2–F5 avanzan en paralelo):

| Fase | Objetivo | Entregables principales | Perfiles | Duración | Esfuerzo (h) |
|---|---|---|---|---|---|
| **F0 — Descubrimiento y PoC técnica** | Cerrar las preguntas abiertas y validar los riesgos técnicos de Harness y End User Messaging | Respuestas P-01 a P-13; informe de PoC; backlog priorizado; plan de migración de la WABA | SE, TL, AE, PM | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F1 — Fundaciones** | Cuentas, seguridad y entrega continua listas para construir | Cuentas `dev` / `qa` / `prod`; IaC base; CI/CD; KMS, IAM, logging y alarmas base | TL, DevOps | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F2 — Canales y gestión de sesión** | Recibir y responder mensajes por los dos canales con control de sesión | End User Messaging + SNS, API Gateway + WAF, Lambdas de ingreso, orquestador y salida, SQS FIFO, tablas DynamoDB | BE, TL | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F3 — Agente, tools y conocimiento** | Que el agente resuelva estado de pedido, stock y políticas | Configuración de Harness; AgentCore Gateway con 6 tools; token de sesión; caché y circuit breaker; Managed KB; system prompt | AE, BE | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F4 — Guardrails y evaluación** | Que el agente sea seguro y su calidad sea medible | Guardrail versionado; `ApplyGuardrail` en entrada, salida y KB; set de evaluación; calibración de umbrales; gate de CI | AE, QA | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F5 — Derivación a humano** | Pasar a una persona con todo el contexto | Conector con la plataforma de atención; estado `HUMANO`; reenvío de mensajes; vuelta al asistente | BE | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F6 — Pruebas integrales y UAT** | Demostrar que soporta la campaña y que negocio lo aprueba | Prueba de carga x8; pruebas de seguridad; tablero de métricas; UAT firmado; runbooks | QA, DevOps, AE, PM | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **F7 — Go-live e hypercare de campaña** | Producción estable antes y durante la campaña | Migración de la WABA; salida gradual; congelamiento de cambios; guardia reforzada en la campaña; informe post-campaña | TL, AE, DevOps, PM | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |
| **Contingencia** | Absorber riesgos de la sección 5 | — | — | [[COMPLETAR: % sobre el total]] | [[COMPLETAR: horas]] |
| **Total** | | | | [[COMPLETAR: semanas]] | [[COMPLETAR: horas]] |

Después del go-live sigue la **transición al servicio mensual de operación** de la Célula IA (S-16). Se cotiza aparte, ver la sección 6.

### F0 — Descubrimiento y PoC técnica
- **Actividades:**
  - Talleres con la gerencia CX y TI para cerrar P-01 a P-13 y actualizar los supuestos (S-xx).
  - Relevamiento de las APIs reales del ERP y del e-commerce contra los mínimos operativos (`integraciones.md`).
  - **PoC de Harness:** un Harness mínimo con Gateway y una tool simulada. Se mide la latencia de arranque de la microVM, se verifica el prompt caching y se evalúa si el Gateway propaga contexto de sesión a las tools (riesgos de ADR-001 y ADR-003).
  - **PoC de End User Messaging:** un número de prueba vinculado, recepción por SNS y envío con `SendWhatsAppMessage`.
  - Plan de migración de la WABA productiva (ventana fuera de campaña).
- **Criterio de salida:** riesgos técnicos validados (o fallback decidido), plataforma de atención definida y backlog priorizado.
- **Dependencias del cliente:** E-01, E-03, E-05.

### F1 — Fundaciones
- **Actividades:**
  - Cuentas y organización de AWS.
  - IaC (CDK o Terraform: [[COMPLETAR: definir con delivery]]).
  - Pipelines de CI/CD para Lambdas y para la configuración de Harness con endpoints por ambiente.
  - Claves KMS, roles IAM de mínimo privilegio y CloudTrail.
  - Logs con retención de 30 días y alarmas base.
  - Solicitud temprana de **aumento de cuotas** de Bedrock (`costos.md` §6).
- **Criterio de salida:** un despliegue "hola mundo" pasa por el pipeline hasta `qa`.
- **Dependencias del cliente:** E-04 (inicio de la gestión de la WABA), E-05.

### F2 — Canales y gestión de sesión
- **Historias:** US-01 a US-04, US-19, US-25.1, US-29.
- **Actividades:**
  - Ingreso de WhatsApp (SNS con filter policy, deduplicación) y del chat web (firma del webhook).
  - Enmascarado de tarjetas y rate limit por remitente.
  - SQS FIFO con DLQ.
  - Orquestador: estados, turnos, timeout y barrido con EventBridge Scheduler.
  - Salida por los dos canales.
  - Parámetros en AppConfig o SSM.
- **Criterio de salida:** eco de extremo a extremo en los dos canales con límites de sesión funcionando en `qa`.

### F3 — Agente, tools y conocimiento
- **Historias:** US-05 a US-10, US-28.
- **Actividades:**
  - Configuración declarativa del Harness: modelo, prompt, `allowedTools`, límites y memoria.
  - Tools Lambda: `validar_identidad`, `consultar_pedido`, `buscar_producto`, `consultar_stock`, `buscar_politica` y `derivar_a_humano`.
  - Token de sesión firmado, caché y circuit breaker.
  - Managed KB con fuente S3 y proceso de publicación de políticas (US-18).
  - Escalamiento a Sonnet decidido por el orquestador (ADR-002).
- **Criterio de salida:** los casos CU-01 a CU-03 se resuelven contra los sandboxes del cliente.
- **Dependencias del cliente:** E-01, E-02.

### F4 — Guardrails y evaluación
- **Historias:** US-21 a US-27, US-30, US-31.
- **Actividades:**
  - Configuración de Bedrock Guardrails: filtros, temas denegados, PII y grounding.
  - Integración de `ApplyGuardrail` en el orquestador y en `buscar_politica`.
  - **Set de evaluación:** conversaciones reales anonimizadas o sintéticas, ataques de prompt, temas denegados y falsos positivos.
  - Calibración de umbrales.
  - Gate de evaluación en CI.
- **Criterio de salida:** las métricas del set de evaluación cumplen los umbrales acordados ([[COMPLETAR: umbrales de US-13.2, US-22.4, US-27.3 y US-30.3]]).

### F5 — Derivación a humano
- **Historias:** US-11 a US-15.
- **Actividades:**
  - Conector con la plataforma de atención: crear la conversación con historial, resumen, intención y motivo.
  - Reenvío de mensajes en estado `HUMANO` y publicación de las respuestas de la persona por el canal.
  - Cierre y vuelta al asistente (US-15.3).
- **Criterio de salida:** derivación de extremo a extremo probada con agentes reales del cliente en `qa`.
- **Dependencias del cliente:** E-03.

### F6 — Pruebas integrales y UAT
- **Historias:** US-16, US-17, US-20, más la validación de todo el alcance.
- **Actividades:**
  - **Prueba de carga x8** sobre la base acordada, verificando cuotas de Bedrock, throughput de WhatsApp y APIs del cliente.
  - Pruebas de seguridad y privacidad (enmascarado, TTL, accesos).
  - Tablero de métricas de la gerencia CX (US-17).
  - Alarmas y runbooks de operación.
  - UAT con la gerencia CX.
- **Criterio de salida:** UAT firmado y prueba de carga aprobada.

### F7 — Go-live e hypercare de campaña
- **Actividades:**
  - Migración de la WABA productiva en la ventana acordada.
  - Salida gradual, por ejemplo un porcentaje del tráfico o una franja horaria: [[COMPLETAR: estrategia de salida con el cliente]].
  - **Congelamiento de cambios** antes de la campaña: [[COMPLETAR: días previos]].
  - Guardia reforzada durante la campaña.
  - Informe post-campaña con contención, costo real contra el estimado y mejoras.
- **Criterio de salida:** la campaña se opera con contención medida y con el informe entregado.

---

## 3. Secuencia y camino crítico

- **Camino crítico:** **F0 → F1 → F2 + F3 → F4 → F6 → F7**.
- **En paralelo:**
  - F5 empieza en cuanto se define la plataforma de atención (E-03).
  - La gestión de la WABA (E-04) corre en paralelo desde F1 y tiene que terminar antes de F7.
- **Ítems de largo plazo**, que se inician en la primera semana porque dependen de terceros:
  - Migración y verificación de la WABA con Meta.
  - Aumento de cuotas de Bedrock.
  - Accesos a los sandboxes del cliente.

| Hito | Condición | Fecha objetivo |
|---|---|---|
| H0 — Kickoff | Firma de la propuesta y accesos iniciales | [[COMPLETAR: fecha]] |
| H1 — PoC aprobada | Fin de F0: riesgos técnicos validados y plataforma de atención definida | [[COMPLETAR: fecha]] |
| H2 — Primera conversación de punta a punta en `qa` | Fin de F2 y avance de F3 | [[COMPLETAR: fecha]] |
| H3 — MVP funcional completo | Fin de F3, F4 y F5 | [[COMPLETAR: fecha]] |
| H4 — UAT y prueba de carga aprobados | Fin de F6 | [[COMPLETAR: fecha]] |
| H5 — Go-live | WABA migrada y producción habilitada | [[COMPLETAR: fecha]] |
| H6 — Congelamiento de cambios | Antes de la campaña | [[COMPLETAR: fecha]] |
| H7 — Cierre de hypercare | Informe post-campaña entregado | [[COMPLETAR: fecha]] |

---

## 4. Equipo propuesto

| Rol | Sigla | Responsabilidad | Dedicación |
|---|---|---|---|
| AI Solutions Engineer | SE | Alcance, supuestos, relación técnica con el cliente, control de cambios | [[COMPLETAR]] |
| Tech Lead / Arquitecto | TL | Arquitectura, decisiones técnicas, revisión de código, go-live | [[COMPLETAR]] |
| AI Engineer | AE | Configuración del Harness, prompts, KB, guardrails, set de evaluación | [[COMPLETAR]] |
| Backend Engineer (×[[COMPLETAR: N]]) | BE | Lambdas de canales, orquestador, tools, conector de derivación | [[COMPLETAR]] |
| DevOps / Cloud Engineer | DevOps | IaC, CI/CD, seguridad, observabilidad, prueba de carga | [[COMPLETAR]] |
| QA Engineer | QA | Plan de pruebas, set de evaluación, pruebas integrales y de carga | [[COMPLETAR]] |
| Project Manager | PM | Plan, riesgos, dependencias del cliente, seguimiento | [[COMPLETAR]] |

**Del lado del cliente** (dedicación a acordar):
- Referente de negocio de la gerencia CX: políticas, UAT y límites de sesión.
- Referente de TI: APIs, accesos y cuentas.
- Responsable de la plataforma de atención.
- Administrador de Meta Business: WABA.

---

## 5. Factores de riesgo para la estimación

| Factor | Fases afectadas | Tratamiento en la estimación |
|---|---|---|
| Limitaciones reales del ERP peores que los mínimos (S-04) | F3, F6 | Contingencia; caché más agresiva; PoC en F0 |
| Harness en *preview*: latencia de arranque, caché o capacidades insuficientes (E-06) | F0, F3 | Decisión en H1; fallback a Runtime + Strands con [[COMPLETAR: esfuerzo adicional]] |
| Migración de la WABA demorada por Meta o por el proveedor actual (E-04) | F7 | Iniciar en F1; plan B con número nuevo |
| Plataforma de atención sin API adecuada (E-03) | F5 | Definición en F0; alternativa Amazon Connect (ADR-007) |
| Contenido de políticas tardío o de baja calidad (E-02) | F3, F4 | Fecha límite comprometida por el cliente; plantilla de redacción provista por la Célula IA |
| Calibración de guardrails con muchos falsos positivos | F4 | Iteraciones de calibración incluidas en F4 |
| Cuotas de Bedrock insuficientes para el pico | F6, F7 | Solicitud en F1 |

Contingencia propuesta: [[COMPLETAR: % sobre el total]].

---

## 6. Fuera de esta estimación
- **Servicio mensual de operación** después del hypercare (S-16): monitoreo, ajuste de prompts, actualización de FAQs y soporte. Se cotiza aparte: [[COMPLETAR: modalidad y alcance del servicio]].
- **Etapas posteriores** al MVP: US-W1 a US-W7.
- **Costos de nube y mensajería:** ver `02-arquitectura/costos.md`.
- **Licencias o costos de la plataforma de atención humana** (S-02).
- **Redacción de las políticas y FAQs:** las provee el cliente (S-12).
