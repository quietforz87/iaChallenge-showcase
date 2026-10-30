# ADR-005 — Implementación de los guardrails

| Campo | Valor |
|---|---|
| Estado | Aceptada · revisada el 2026-10-29 (Harness: guardrails aplicados con `ApplyGuardrail` fuera del loop) |
| Fecha | 2026-10-29 |
| Relacionado | GR-01 a GR-10, US-22 a US-31 (`01-analisis/analisis-funcional.md`); S-15; ADR-001, ADR-003, ADR-004 |

## Contexto
El análisis funcional define 10 guardrails en cuatro capas: entrada, salida, herramientas y sesión. Hay que decidir qué los implementa. La regla de fondo es que lo **determinista** no puede depender del modelo, y que todo contenido **no confiable** debe evaluarse: el mensaje del cliente, los resultados de las tools y los fragmentos de la base de conocimiento.

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — Solo instrucciones en el system prompt | Sin costo extra | No es verificable y es vulnerable a la inyección de prompts | — | — |
| B — **Bedrock Guardrails + controles deterministas en código** ✅ | Filtros gestionados y versionados (contenido, prompt attack, temas denegados, PII, grounding); lo crítico queda en código testeable | Costo por unidad de texto evaluada; hay que calibrar umbrales | ~$7,5 cada 1.000 sesiones | Medio: la configuración de filtros es propietaria; las reglas se documentan en un formato neutro |
| C — Moderación propia con otro LLM | Portable | Más latencia, más costo y más código | Medio | Bajo |

## Decisión
Se adopta la **opción B**:

| Guardrail | Implementación |
|---|---|
| GR-01 Ataques de prompt | Bedrock Guardrails, **filtro de prompt attack**: con `ApplyGuardrail` sobre el mensaje del cliente en el orquestador, y sobre los fragmentos de la KB en `buscar_politica`. Además, salidas estructuradas y saneadas en las tools (ADR-003) |
| GR-02 Temas denegados | Bedrock Guardrails, **denied topics** con frases de ejemplo en español rioplatense |
| GR-03 Contenido ofensivo | Bedrock Guardrails, **content filters** (odio, insultos, sexual, violencia, conducta indebida), en entrada y salida |
| GR-04 Datos sensibles del cliente | **Regex en la Lambda de ingreso**, antes de cualquier persistencia, más el filtro de información sensible de Guardrails (`ANONYMIZE` para email y teléfono, `BLOCK` para tarjetas) |
| GR-05 PII en la respuesta | Guardrails, filtro de información sensible en la salida, más presentación parcial de datos en las tools |
| GR-06 Compromisos comerciales | System prompt, denied topic "descuentos y excepciones", y casos en el set de evaluación |
| GR-07 Respuestas no fundamentadas | Guardrails, **contextual grounding** con `ApplyGuardrail` sobre la respuesta final. Los resultados de las tools, que el orquestador toma del stream del Harness (`toolResult`), y los fragmentos de la KB se pasan como `grounding_source`. Umbrales iniciales de 0,7 (grounding y relevancia), a calibrar con evaluación |
| GR-08 Uso indebido de tools | **Código**: token de sesión firmado, validación de identidad y de esquema en las Lambda tools (ADR-003), solo lectura por IAM, `allowedTools` y `maxIterations` en el Harness (ADR-001) |
| GR-09 Abuso del canal | **Código**: rate limit por remitente en la Lambda de ingreso, tamaño máximo de mensaje y WAF (ADR-004) |
| GR-10 Tono y marca | System prompt y set de evaluación (LLM-as-a-judge) |

Reglas de configuración:
- **Modo de integración `ApplyGuardrail` (standalone):** el Harness gestiona el loop, así que no hay acceso a `guardContent` en cada llamada al modelo. Los guardrails se aplican en tres puntos que controlamos:
  1. **Entrada:** el orquestador evalúa el mensaje del cliente antes de invocar al Harness. Si se bloquea, responde con el mensaje estándar y **no invoca** al agente, lo que ahorra costo.
  2. **Contenido recuperado:** `buscar_politica` evalúa los fragmentos de la KB antes de devolverlos.
  3. **Salida:** el orquestador evalúa la respuesta completa, con grounding contra los resultados de las tools, antes de enviarla.
- **Sin streaming hacia el canal:** WhatsApp no lo usa, así que se evalúa la respuesta completa antes de enviarla.
- **No se usa el guardrail forzado a nivel de cuenta** (`PutEnforcedGuardrailConfiguration`): duplicaría la evaluación en cada llamada interna del loop y no permite grounding con fuente.
- **Versión numerada en producción:** nunca `DRAFT`. `trace` queda deshabilitado en producción.
- **Uso obligatorio:** el único camino al Harness es el orquestador (IAM), y el orquestador siempre aplica los guardrails. Hay pruebas automatizadas que verifican que ningún mensaje llega al canal sin pasar por el guardrail de salida.
- **Cifrado:** el guardrail se cifra con una clave KMS propia.
- **Logging de invocaciones del modelo y trazas detalladas del Harness acotadas:** los logs guardan PII sin enmascarar aunque Guardrails la anonimice en la respuesta. La traza útil para operar se registra enmascarada desde el orquestador (US-31).
- **Calibración:** cada intervención se registra con guardrail, capa, acción y sesión. Las métricas y alarmas se alimentan de ese registro (US-31). Antes del go-live se calibra con el set de evaluación: ataques, temas denegados, falsos positivos legítimos.

## Consecuencias
- **Positivas:** defensa en profundidad. Lo crítico (identidad, abuso, datos de tarjeta) no depende del modelo, y lo semántico queda en un servicio gestionado y versionado.
- **Negativas / trade-offs:**
  - El costo de Guardrails es comparable al del LLM.
  - **Palanca de ahorro:** aplicar temas denegados solo en la entrada y grounding solo en los turnos con datos.
  - Los umbrales necesitan calibración continua (operación, S-16).
- **Ruta de salida:**
  - Las políticas (temas, ejemplos, umbrales, regex) se versionan en el repo en un formato neutro.
  - `ApplyGuardrail` se puede reemplazar por otro servicio de moderación o por un clasificador propio sin cambiar el contrato con el agente.
