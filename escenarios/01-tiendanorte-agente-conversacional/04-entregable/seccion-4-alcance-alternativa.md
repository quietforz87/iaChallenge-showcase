# Sección 4 · Alcance — versión alternativa

> Propuesta de reemplazo para la sección 4 de `propuesta-tecnica.md` (v0.2).

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
