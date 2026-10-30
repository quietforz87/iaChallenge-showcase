# ADR-001 — Plataforma de ejecución del agente

| Campo | Valor |
|---|---|
| Estado | Aceptada · **revisada el 2026-10-29**: AgentCore Harness reemplaza a AgentCore Runtime con código Strands propio (directiva de la revisión de arquitectura) |
| Fecha | 2026-10-29 |
| Relacionado | S-01, S-16; alternativa B de `01-analisis/alternativas.md`; ADR-002 a ADR-006 |

## Contexto
El checkpoint de análisis eligió la **alternativa B**: un agente gestionado en Bedrock AgentCore, con la disciplina de portabilidad de la alternativa A. La primera versión de este ADR elegía **AgentCore Runtime con código Strands propio**, porque necesitaba hooks para varios controles deterministas. La revisión de arquitectura definió usar **AgentCore Harness**: el agente se declara como **configuración** (modelo, system prompt, tools, memoria y límites) y AgentCore ejecuta el loop con Strands, sin código de orquestación ni contenedor propio.

Este ADR registra cómo se cumplen con Harness los controles deterministas que exige el análisis funcional, sin hooks dentro del loop:

| Necesidad | Con Runtime + Strands (v1) | **Con Harness (v2)** |
|---|---|---|
| Conteo de turnos, timeout y cierre (US-03, US-04) | Orquestador | **Orquestador** (sin cambios, ADR-004) |
| Tope de tools por turno (US-28.4) | Hook | **`maxIterations`** por invocación, más `maxTokens` y `timeoutSeconds` |
| Ruteo de modelo (ADR-002) | `LLMProvider` en código | **Override de `model` por invocación**, que decide el orquestador |
| Guardrails de entrada y salida, grounding (US-22 a US-27) | `guardContent` en cada llamada | **`ApplyGuardrail` desde el orquestador** antes y después de invocar, y dentro de la tool de conocimiento (ADR-005) |
| Identidad validada fuera del modelo (US-28.2) | `sessionId` inyectado por hook | **Token de sesión firmado** que verifica cada Lambda tool (ADR-003) |
| Señal de derivación (US-11 a US-14) | Valor de retorno del agente | **Tool `derivar_a_humano`**, que registra el motivo en la sesión; el orquestador lo lee al terminar el turno |
| Solo las tools de negocio | Código | **`allowedTools`**: solo las tools del Gateway. Las built-in `shell` y `file_operations` quedan deshabilitadas |

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — **AgentCore Harness** ✅ | Cero código de orquestación y sin contenedor; cambio de modelo, prompt o tools por configuración y sin redeploy; **versiones inmutables con endpoints** y rollback instantáneo; varios proveedores de modelo (Bedrock, OpenAI, Gemini, LiteLLM); memoria integrada | Sin hooks dentro del loop, así que los controles se trasladan al orquestador y a las tools; cada sesión levanta una microVM, con latencia de arranque a medir; la entrada de `InvokeHarness` es de confianza total, por lo que solo la llama el orquestador; servicio en *preview* (CLI `@aws/agentcore@preview`) | Por uso (infraestructura de Runtime) | Medio: la definición del agente queda en el formato de Harness |
| B — AgentCore Runtime + Strands propio (v1 de este ADR) | Control total del loop con hooks | Hay que construir, versionar y desplegar un contenedor ARM64 y escribir el agente | Por uso | Bajo-medio |
| C — Lambda con framework propio | Máxima portabilidad | Hay que resolver memoria, trazas y aislamiento a mano | Bajo | Bajo |

## Decisión
Se adopta la **opción A: AgentCore Harness**, con esta configuración base, versionada en el repo como archivo declarativo:

| Campo de Harness | Valor |
|---|---|
| `model` | `bedrockModelConfig`: Claude Haiku 5.5 (perfil `global.`), `maxTokens` 1024, `apiFormat` `converse_stream` |
| `systemPrompt` | Instrucciones de rol, tono, alcance y compromisos comerciales (GR-02, GR-06, GR-10), versionadas |
| `tools` / `allowedTools` | Solo `agentcore_gateway`, con las tools de ADR-003; ninguna built-in, browser ni code interpreter |
| `skills` | Ninguna en el MVP |
| `memory` | `agentCoreMemoryConfiguration` con un recurso de AgentCore Memory propio (corto plazo, KMS, TTL 24 h; ADR-006) |
| `maxIterations` / `maxTokens` / `timeoutSeconds` | 4 / 1024 / 30 s, explícitos (US-28.4). Valores iniciales a calibrar |
| Autenticación de entrada | **SigV4 (IAM)**, sin `authorizerConfiguration`. Solo el rol del orquestador tiene `InvokeHarness` + `InvokeAgentRuntime` |
| Red | **Sin modo VPC**: el agente no accede a recursos privados (Gateway, Bedrock y Memory son endpoints de AWS). Se evita el NAT que exige el modo VPC para descargar la imagen de ECR Public |
| Versionado | Un **endpoint con nombre** por ambiente (`dev`, `qa`, `prod`) que apunta a una versión inmutable. El rollback consiste en volver a apuntar el endpoint |

**Reglas de invocación (frontera de confianza):**
- El orquestador construye la llamada a `InvokeHarness`: `runtimeSessionId` de 33 caracteres o más por sesión de negocio, `messages` con el texto del cliente ya filtrado, `model` según ADR-002, `actorId` igual al remitente enmascarado.
- **Nunca reenvía campos de override que vengan del canal**, en particular `model`, `skills`, `tools` y `systemPrompt`.
- El rol de ejecución del Harness es de mínimo privilegio:
  - Modelos acotados a los perfiles de inferencia usados.
  - Solo el Gateway y la memoria propios.
  - `sts:AssumeRole` denegado.
  - Trust policy con `aws:SourceAccount` y `aws:SourceArn`.

## Consecuencias
- **Positivas:**
  - Menos código: no hay agente, contenedor ni pipeline de imagen que mantener. Cambiar prompt, modelo o tools es crear una versión y apuntar el endpoint.
  - Encaja con un cliente sin equipo de infraestructura y con la operación por la Célula IA (S-16).
  - Elimina el costo fijo de red del modo VPC (ver `costos.md`).
- **Negativas / trade-offs:**
  - Los controles deterministas dependen del **orquestador** y de las **Lambda tools** (más lógica ahí, con buena cobertura de pruebas).
  - Hay que medir la **latencia de arranque** de la microVM en la primera interacción de cada sesión (riesgo a registrar).
  - No hay control sobre el *prompt caching* dentro del loop gestionado (a validar en la PoC; impacto en `costos.md` §5).
  - El servicio está en *preview*: hay que confirmar disponibilidad general y SLA antes de producción.
- **Ruta de salida:**
  - La configuración (prompt, tools MCP, modelo y límites) es portable a un agente **Strands** propio: el mismo framework que usa Harness por dentro. Ese agente puede correr en AgentCore Runtime (opción B), ECS o Lambda.
  - Las tools siguen siendo MCP (ADR-003), y los guardrails y la sesión viven en el orquestador. Ninguna de esas piezas depende de Harness.
