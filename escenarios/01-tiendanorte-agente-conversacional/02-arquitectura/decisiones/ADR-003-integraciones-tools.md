# ADR-003 — Integración con los sistemas del cliente (tools)

| Campo | Valor |
|---|---|
| Estado | Aceptada · revisada el 2026-10-29 (Harness: token de sesión firmado y tool de derivación) |
| Fecha | 2026-10-29 |
| Relacionado | S-04, S-06, S-09, S-10; US-05, US-06, US-07, US-28; GR-08; `01-analisis/integraciones.md` |

## Contexto
El agente consulta pedidos y stock en el e-commerce y el ERP, que tiene limitaciones desconocidas (S-04). Opcionalmente también consulta contexto en el CRM. Hay cuatro requisitos:
- Las tools deben ser de **solo lectura**.
- Deben validar que el pedido pertenezca al cliente identificado **sin depender del modelo** (US-28.2).
- Deben proteger al ERP del pico con caché y circuit breaker.
- Deben ser reutilizables con otro agente o proveedor (lock-in).

## Opciones evaluadas
| Opción | Pros | Contras | Costo | Lock-in |
|---|---|---|---|---|
| A — Tools como funciones dentro del agente | Simple; una pieza menos | Las credenciales y la lógica de integración quedan acopladas al agente; no se reutilizan | Mínimo | Bajo |
| B — **AgentCore Gateway con targets Lambda, expuestos como MCP** ✅ | Estándar **MCP**; credenciales gestionadas (Identity / Secrets Manager); cada tool es una Lambda testeable con su caché y su circuit breaker | Un componente gestionado más | Muy bajo (~$0,005 cada 1.000 invocaciones) | Bajo: MCP es un estándar abierto |
| C — Gateway con targets OpenAPI directos a las APIs del cliente | Sin código de adaptación | No hay dónde validar identidad, cachear ni aplicar el circuit breaker | Muy bajo | Bajo |

## Decisión
Se adopta la **opción B**. AgentCore Gateway expone como MCP las tools de la tabla. Cada tool es una **Lambda adaptadora**.

| Tool | Sistema | Uso | Historia |
|---|---|---|---|
| `validar_identidad(pedido, dato)` | E-commerce | Valida Nº de pedido + DNI / email / teléfono y marca la sesión como identificada en DynamoDB | US-05 |
| `consultar_pedido(pedido)` | E-commerce + ERP | Estado, fechas y tracking, solo si el pedido pertenece a la sesión identificada | US-06 |
| `buscar_producto(texto)` | E-commerce (catálogo) | Hasta 3 coincidencias con SKU y link | US-07.2 |
| `consultar_stock(sku, sucursal?)` | ERP | Stock online y por sucursal, con antigüedad del dato | US-07 |
| `buscar_politica(consulta)` | Bedrock Knowledge Base | Fragmentos de políticas y FAQs (Retrieve), filtrados con `ApplyGuardrail` (prompt attack) antes de devolverlos | US-09, US-10, US-22.3 |
| `derivar_a_humano(motivo, resumen)` | DynamoDB `sesiones` | Marca la sesión para derivar, con motivo y resumen; el orquestador ejecuta la derivación al cerrar el turno (ADR-004) | US-11 a US-15 |

Reglas de las Lambda tools:
- **Token de sesión firmado (GR-08):**
  - Con Harness no hay hooks para inyectar contexto en las tools. Por eso el orquestador emite un **token de sesión** firmado con KMS (por ejemplo, un JWT de 15 minutos con `sessionId` y canal). Lo incluye en el mensaje de cada invocación, y las tools lo reciben como parámetro obligatorio.
  - Cada Lambda **verifica la firma y la vigencia**, y opera **solo sobre la sesión del token**: `consultar_pedido` rechaza cualquier pedido que no haya sido validado en esa sesión por `validar_identidad`.
  - El modelo puede transportar el token, pero no puede fabricar uno ni usar el de otra sesión. Aun con una inyección de prompt exitosa, solo puede ver lo que el cliente de esa sesión ya validó.
  - **A validar en la PoC:** si AgentCore Gateway propaga a los targets el contexto de la invocación (sesión o `actorId`), ese mecanismo reemplaza al token como parámetro.
- **Validación de parámetros:** cada parámetro se valida con un esquema estricto antes de llamar al sistema del cliente (US-28.3).
- **Caché en DynamoDB:** con TTL **de 2 a 5 minutos para stock** y **de 5 minutos para pedidos**. Se devuelve la antigüedad del dato para el aviso de "disponibilidad aproximada" (US-07.6).
- **Circuit breaker:** timeout de 2 s por llamada. Si se abre, responde `SISTEMA_NO_DISPONIBLE` y el agente deriva (US-06.4, US-07.7).
- **Credenciales y acceso:** las credenciales de las APIs del cliente se guardan en un credential provider de AgentCore Identity (respaldado por Secrets Manager). El acceso es HTTPS y de solo lectura.
- **Fuera del VPC:** las Lambda tools corren fuera del VPC y llegan a las APIs del cliente por internet. No hace falta NAT.
- **Salidas estructuradas:** las tools devuelven JSON con campos acotados. Los textos libres de los sistemas, como nombres de producto o notas de pedido, se sanean y truncan, para reducir la inyección indirecta (GR-01).

## Consecuencias
- **Positivas:**
  - La seguridad de datos de pedidos no depende del comportamiento del modelo.
  - El ERP queda protegido en el pico por la caché.
  - Cada tool tiene su propia prueba de contrato.
- **Negativas / trade-offs:**
  - La caché introduce hasta 5 minutos de desfase, comunicado en la respuesta.
  - Cinco Lambdas para mantener.
- **Ruta de salida:** las Lambdas son adaptadores HTTP comunes. Las mismas definiciones de tools se pueden servir desde cualquier servidor MCP (por ejemplo un contenedor propio) si se deja AgentCore Gateway.
