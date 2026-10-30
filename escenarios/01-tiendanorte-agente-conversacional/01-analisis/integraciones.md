# Integraciones — Escenario 01 · TiendaNorte

> Para negocio: el agente necesita consultar pedidos y stock en los sistemas actuales; acá se fija qué
> le pedimos a esos sistemas para que la solución funcione bien en campaña.

## Sistemas

| Sistema | Uso en la solución | Mecanismo | Estado de la información | Supuestos |
|---|---|---|---|---|
| WhatsApp Business API | Canal WhatsApp (entrada y salida de mensajes) | **AWS End User Messaging Social**: WABA vinculada, eventos a SNS y envío con `SendWhatsAppMessage` (ADR-007) | Ya contratada; requiere migrar la WABA y los números | S-03, S-18 |
| Chat del e-commerce | Canal web | API/webhooks de la plataforma de e-commerce | Por confirmar si expone webhooks | S-03 |
| Plataforma e-commerce | Estado de pedidos online, catálogo y links de producto | API REST | API disponible | S-10 |
| ERP | Stock online y por sucursal; información de pedidos | API REST | Limitaciones no conocidas | S-04, S-09 |
| CRM comercial | Contexto del cliente (opcional en el MVP) | API (a confirmar) | Sin detalle | — |
| Plataforma de atención humana | Recibir conversaciones derivadas con contexto | API (a confirmar) | A definir por el cliente | S-02 |

## Mínimos operativos requeridos a las APIs del cliente (S-04)

| Requisito | Mínimo | Motivo |
|---|---|---|
| Endpoints | Pedido por ID (estado, fechas, tracking); stock por SKU en canal online y por sucursal; búsqueda de SKU por nombre o código | Cubrir CU-01 y CU-02 |
| Latencia | p95 ≤ 2 s por request | Mantener la respuesta total del agente en pocos segundos |
| Throughput en pico | ≥ 1 req/s por cada 1.000 sesiones/mes de operación base (ej.: 45 req/s para 45.000 sesiones/mes), antes de caché — ver `02-arquitectura/costos.md` §6 | Evitar throttling durante la campaña |
| Frescura del stock | ≤ 15 min | Evitar prometer stock inexistente; si no se cumple, el agente informa "disponibilidad aproximada" |
| Disponibilidad | ≥ 99,5% en campaña, sin ventanas de mantenimiento en esas fechas | El agente depende de estas APIs para contener |
| Seguridad | HTTPS; OAuth2 o API key rotable; acceso de solo lectura | Mínimo privilegio |
| Plataforma de atención | API para crear o transferir una conversación con historial y metadatos (canal, intención, motivo de derivación) | Handoff con contexto (S-02, S-14) |

## Mitigaciones de la solución
- **Caché** de stock y de pedidos con TTL corto, para reducir la carga sobre el ERP en el pico.
- **Circuit breaker y respuesta degradada:** si una API falla, el agente avisa y deriva a un humano (S-14).
- **Cola de entrada**, para absorber ráfagas de mensajes sin perder eventos.
