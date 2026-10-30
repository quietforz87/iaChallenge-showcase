# Entendimiento del problema — Escenario 01 · TiendaNorte

## Situación actual

> Para negocio: en campañas, el equipo de atención no da abasto con preguntas repetitivas, el cliente
> espera demasiado y se pierden ventas.

- TiendaNorte vende electrodomésticos y electrónica online y en 15 sucursales.
- Atiende consultas por **WhatsApp** y **chat web** con un equipo humano.
- En **Black Friday y Hot Sale** el tráfico se multiplica **x5–x8**. La mayoría de las consultas son repetitivas: estado de pedido, stock, cambios y devoluciones.
- Los tiempos de respuesta se disparan y hay **ventas perdidas** por falta de respuesta a tiempo.

## Necesidad

Un **agente conversacional** en WhatsApp y chat web que:
1. Resuelva solo las consultas frecuentes.
2. Derive a un humano, con contexto, lo que no puede resolver.
3. Absorba los picos de campaña sin degradarse.
4. Esté **en producción en ~2 meses** (próxima campaña grande).

Con estas restricciones: sin equipo de infraestructura, sensibilidad al costo y sin quedar atados a un único proveedor (ver brief, B.2).

## Actores

| Actor | Rol |
|---|---|
| Cliente final | Consulta por WhatsApp o por el chat del e-commerce. |
| Agente IA | Identifica al cliente, entiende la intención, consulta los sistemas y responde o deriva. |
| Agente humano | Retoma, en la plataforma de atención, las conversaciones derivadas (S-02). |
| Sistemas del cliente | E-commerce, ERP y CRM, que proveen pedidos, stock y contexto (ver `integraciones.md`). |
| Célula IA | Construye y opera el servicio (S-16). |
| Gerencia CX | Dueña de negocio: define políticas, límites de sesión y contenido de FAQs (S-08, S-12). |

## Casos de uso del MVP

| # | Caso de uso | Resolución | Fuente | Supuestos |
|---|---|---|---|---|
| CU-01 | Estado de pedido online | Identifica con Nº de pedido + dato y responde estado, fechas y tracking. | E-commerce + ERP | S-06, S-10 |
| CU-02 | Stock de producto | Busca el producto e informa disponibilidad online y por sucursal; si hay stock, sugiere compra o retiro. | ERP | S-09 |
| CU-03 | Cambios y devoluciones | Informa política, plazos y pasos. **No deriva**. | Base de conocimiento | S-05, S-12 |
| CU-04 | Derivación a humano | Transfiere con contexto ante pedido explícito, fallo o molestia, y para consultas fuera de alcance. | Plataforma de atención | S-02, S-13, S-14 |
| CU-05 | Cierre de sesión | Cierra por timeout (15 min) o por límite de turnos (10). | Agente IA | S-08 |

## Indicadores

| Objetivo | Indicador | Meta |
|---|---|---|
| Descargar al equipo humano | Contención (sesiones sin derivar / sesiones totales) | ≥ 60% (S-17) |
| Medir costo | Costo por 1.000 sesiones, operación base vs. pico | A calcular en `02-arquitectura/costos.md` (S-07) |
| Sostener el pico | Tasa de error / throttling durante la campaña | [[COMPLETAR: meta a acordar con negocio]] |

## Fuera del MVP
- Iniciar trámites de cambio o devolución (S-05).
- Pedidos de sucursal y tracking en vivo del operador logístico (S-10).
- Asesoramiento de productos, reclamos y facturación: se derivan (S-13).
