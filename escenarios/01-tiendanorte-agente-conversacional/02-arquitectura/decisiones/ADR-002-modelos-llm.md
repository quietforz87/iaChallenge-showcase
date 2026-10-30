# ADR-002 — Modelos de lenguaje, ruteo y portabilidad del LLM

| Campo | Valor |
|---|---|
| Estado | Aceptada · revisada el 2026-10-29 (Harness: ruteo por override de `model`) |
| Fecha | 2026-10-29 |
| Relacionado | S-07, S-11, S-17; US-08, US-27; ADR-001, ADR-005 |

## Contexto
El costo por sesión depende sobre todo de los tokens. La mayoría de los turnos son simples: clasificar la intención, pedir datos y redactar una respuesta corta con datos de una tool. Una minoría requiere más razonamiento: consultas encadenadas, ambigüedad o reformulación. No hay restricción de residencia (S-11), así que se pueden usar perfiles de inferencia cross-region. Cambiar de modelo o de proveedor tiene que ser posible sin reescribir el agente.

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — Un solo modelo grande (Claude Sonnet 5.5) | Máxima calidad; un solo prompt para mantener | ~20 veces más caro por token que Haiku 5.5 | Alto | Bajo (detrás de la interfaz) |
| B — Un solo modelo chico (Claude Haiku 5.5) | Costo mínimo y baja latencia | Riesgo en consultas complejas, que impacta en la contención (S-17) | Mínimo | Bajo |
| C — **Ruteo: Haiku 5.5 por defecto, escalamiento a Sonnet 5.5** ✅ | Costo cercano a B con red de seguridad de calidad | Dos modelos para evaluar; la caché de prompts es por modelo | Bajo | Bajo |
| D — Amazon Nova Micro / Lite | Costo muy bajo | Menor calidad en español rioplatense y en uso de tools (a validar) | Mínimo | Bajo |

## Decisión
Se adopta la **opción C**:

| Uso | Modelo | Configuración |
|---|---|---|
| Por defecto (todas las sesiones) | **Claude Haiku 5.5** | Effort `low`, `maxTokens` 1024 |
| Escalamiento | **Claude Sonnet 5.5** | Effort `low` o `medium`, `maxTokens` 1024 |

- **Invocación:** perfiles de inferencia **cross-region `global.`** de Bedrock, que tienen la tarifa más baja y más capacidad. Los IDs vigentes se confirman con `aws bedrock list-inference-profiles` al implementar.
- **Cuándo se escala a Sonnet 5.5 (el resto de la sesión):**
  - Una respuesta de Haiku se bloquea por grounding (US-27).
  - El modelo no logra clasificar la intención en el primer intento.
  - La consulta encadena más de una intención.
  - Haiku rechaza la solicitud.
- **Quién decide el escalamiento:** el **orquestador**, que conoce el resultado del guardrail, el resultado de la tool y el historial de la sesión. Sonnet 5.5 se aplica con el **override de `model` en `InvokeHarness`**, sin redeploy (ADR-001). El modelo vigente de cada sesión queda registrado en DynamoDB.
- **Abstracción del modelo (reemplaza a `LLMProvider`):** con Harness no hay código de agente propio. La portabilidad del LLM la da la configuración del Harness, que admite **Bedrock (Converse), OpenAI, Gemini y cualquier proveedor compatible con LiteLLM**. Los IDs de modelo y sus parámetros viven en la configuración versionada del orquestador, no en código.
- **Prompt caching:** el system prompt y las definiciones de tools son estables, pero **el control de los puntos de caché dentro del loop gestionado está a validar en la PoC**. `costos.md` incluye la sensibilidad sin caché.
- **Atribución de costos:** **application inference profiles** con tags (`Proyecto=tiendanorte-agente`, `Modelo=…`).
- **Calidad:** el set de evaluación (US-21) corre contra ambos modelos. Antes de cerrar el MVP se valida Nova (opción D) como alternativa de costo.

## Consecuencias
- **Positivas:**
  - Costo de LLM estimado en ~$9 cada 1.000 sesiones (ver `costos.md`).
  - Cambiar de modelo es un cambio de configuración más una corrida de evaluación.
- **Negativas / trade-offs:**
  - Hay que mantener los criterios de escalamiento y medir su tasa: el supuesto es 15% de sesiones.
  - Cada escalamiento paga una escritura de caché en el otro modelo.
  - Si Harness no aplica prompt caching, el costo de LLM sube ~45% (de ~$9 a ~$13 cada 1.000 sesiones).
- **Ruta de salida:**
  - Cambiar de proveedor de modelo es un cambio de la configuración del Harness: OpenAI, Gemini o LiteLLM hacia Anthropic API directa, Azure, Vertex o un modelo open-weight.
  - Si se sale de Harness, el agente Strands equivalente soporta los mismos proveedores (ADR-001).
