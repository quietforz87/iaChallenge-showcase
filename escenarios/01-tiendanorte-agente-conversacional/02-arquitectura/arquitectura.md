# Arquitectura de la solución — Escenario 01 · TiendaNorte

> Para negocio: un asistente virtual en WhatsApp y en el chat web, construido sobre servicios gestionados
> de AWS que escalan solos en las campañas. El agente se define por configuración en AgentCore Harness,
> sin código de orquestación propio. Consulta pedidos y stock en los sistemas actuales, responde
> políticas desde el contenido que provee TiendaNorte y deriva a una persona, con todo el contexto,
> cuando no puede resolver.

## 1. Visión general

| Capa | Componentes | Decisión |
|---|---|---|
| Canales | WhatsApp vía **AWS End User Messaging Social** (WABA vinculada) · chat del e-commerce | S-03, ADR-007 |
| Ingreso y sesión | WhatsApp: End User Messaging → SNS standard → Lambda de ingreso · Chat web: API Gateway + WAF → Lambda de ingreso · luego SQS FIFO → Lambda orquestador → DynamoDB | ADR-004, ADR-007 |
| Agente | **AgentCore Harness**: agente declarado por configuración (modelo, prompt, tools del Gateway, memoria y límites), versionado con endpoints por ambiente, invocado solo por el orquestador (IAM) + AgentCore Memory (corto plazo) | ADR-001, ADR-006 |
| Modelos | Bedrock: **Claude Haiku 5.5** por defecto, escalamiento a **Claude Sonnet 5.5** con override de modelo por invocación; Harness admite otros proveedores | ADR-002 |
| Guardrails | Bedrock Guardrails con `ApplyGuardrail` en el orquestador (entrada, y salida con grounding) y en la tool de conocimiento + controles deterministas en código (token de sesión, límites) | ADR-005 |
| Tools | AgentCore Gateway (MCP) → Lambda tools de solo lectura, con caché y circuit breaker | ADR-003 |
| Conocimiento | Bedrock Managed Knowledge Base ← S3 (políticas y FAQs del cliente) | ADR-006 |
| Salida y derivación | Lambda de salida → `SendWhatsAppMessage` / API del chat · conector a la plataforma de atención | ADR-004, ADR-007 |
| Operación | CloudWatch (métricas de negocio, alarmas, trazas) · KMS · Secrets Manager · CloudTrail | ADR-005, ADR-006 |

## 2. Diagramas

### 2.1 Diagrama de flujo
![Flujo conversacional](diagramas/export/flujo.drawio.png)

- Fuente: [`flujo.drawio`](diagramas/flujo.drawio), con dos páginas:
  - Vista general para negocio.
  - Secuencia técnica de un turno.
- Guía del diagrama: [`flujo.md`](diagramas/flujo.md).
- [[COMPLETAR: exportar PNG]]

### 2.2 Diagrama de despliegue
![Despliegue](diagramas/export/despliegue.drawio.png)

- Fuente: [`despliegue.drawio`](diagramas/despliegue.drawio).
- Guía del diagrama: [`despliegue.md`](diagramas/despliegue.md).
- [[COMPLETAR: exportar PNG]]

## 3. Cómo se cumplen los criterios del brief (B.2)

| Criterio | Cómo lo resuelve la arquitectura |
|---|---|
| Time-to-market (2 meses) | Todo es gestionado. El agente es configuración de Harness (sin código de orquestación ni contenedor) y las tools son Lambdas simples |
| Escalabilidad x5–x8 | La cola SQS absorbe ráfagas. Lambda, AgentCore y Bedrock escalan por demanda. La caché protege al ERP. Las cuotas de LLM se dimensionan antes de la campaña (`costos.md` §6) |
| Operación mínima | Sin servidores ni parches. Versiones inmutables del Harness con rollback por endpoint. Alarmas sobre métricas de negocio y técnicas |
| Sensibilidad al costo | 100% pago por uso, ~USD 47 cada 1.000 sesiones (la mitad es mensajería de WhatsApp) más ~USD 20 fijos (`costos.md`). Modelo chico por defecto y palancas documentadas |
| Evitar lock-in | Configuración del agente portable a un agente Strands propio (el framework que usa Harness por dentro); proveedor de modelo intercambiable por configuración; tools en **MCP**; guardrails y sesión fuera del Harness; datos y documentos en DynamoDB y S3; WhatsApp con payload en formato Meta (salida posible a la Cloud API directa); ruta de salida en cada ADR |
| Derivación a humano | Señal explícita del agente y conector único hacia la plataforma de atención, con historial, resumen y motivo (ADR-004) |
| Omnicanal | Formato de mensaje común; un solo agente para los dos canales |

## 4. Seguridad y privacidad

- **Accesos:**
  - Mínimo privilegio por componente, con un rol IAM por Lambda y por agente.
  - Las tools son de **solo lectura**.
  - El Harness solo se invoca con IAM, desde el orquestador. Nunca se reenvían overrides que vengan del canal.
  - El Harness solo tiene habilitadas las tools del Gateway: sin `shell` ni `file_operations`.
  - Las tools verifican un token de sesión firmado (ADR-003).
- **Datos personales:**
  - Las tarjetas se enmascaran en el ingreso.
  - Las transcripciones se guardan enmascaradas, con TTL de 90 días.
  - El logging de invocaciones del modelo está deshabilitado.
  - Los logs se cifran con KMS y tienen 30 días de retención (S-15, US-16).
- **Cifrado:** KMS en DynamoDB, Memory, S3, logs y guardrail. TLS 1.2 o superior en todas las integraciones.
- **Secretos:** en credential providers de AgentCore Identity y Secrets Manager. Nunca en variables de entorno.
- **Auditoría:** CloudTrail en las APIs de control de Bedrock y AgentCore, con alarmas ante cambios en guardrails.

## 5. Ambientes y entrega

| Ambiente | Uso | Notas |
|---|---|---|
| `dev` | Desarrollo e integración con sandboxes del cliente | Endpoint `dev` del Harness; número de WhatsApp de prueba |
| `qa` | Set de evaluación, pruebas de carga (x8) y UAT con la gerencia CX | Datos de prueba, sin PII real |
| `prod` | Producción | Cuenta AWS separada |

- **Infraestructura como código:** CDK o Terraform [[COMPLETAR: definir con delivery]].
- **CI/CD:**
  - Nueva versión del Harness a partir de la configuración versionada y despliegue de las Lambdas.
  - **Corrida del set de evaluación como gate** antes de apuntar el endpoint de `prod` a la versión nueva (US-21).

## 6. Decisiones y pendientes

| ID | Tema | Estado |
|---|---|---|
| ADR-001 | Plataforma del agente: **AgentCore Harness** | Aceptada (revisada: reemplaza a Runtime + Strands) |
| ADR-002 | Modelos: Haiku 5.5 con escalamiento a Sonnet 5.5 por override de modelo | Aceptada (revisada) |
| ADR-003 | Tools: AgentCore Gateway (MCP) + Lambdas de solo lectura | Aceptada |
| ADR-004 | Canales, sesión y derivación | Aceptada; modificada por ADR-007 |
| ADR-005 | Guardrails: `ApplyGuardrail` fuera del loop + controles en código | Aceptada (revisada) |
| ADR-006 | Knowledge Base gestionada, Memory de corto plazo, DynamoDB | Aceptada |
| ADR-007 | WhatsApp vía AWS End User Messaging Social | Aceptada (revisión de arquitectura) |
| P-11 | Dueño del canal de WhatsApp mientras atiende una persona | Resuelta por ADR-007: la solución; la plataforma se integra por API |
| P-12 | Migración de la WABA y de los números actuales a End User Messaging Social | Abierta |
| P-13 | Cuenta AWS donde se despliega (y a la que se factura WhatsApp) | Abierta |
