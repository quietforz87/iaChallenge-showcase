# Preguntas abiertas para el cliente — Escenario 01 · TiendaNorte

> Para validar en la próxima reunión. Cada respuesta cierra o corrige un supuesto.

| # | Pregunta | Supuesto | Destinatario | Prioridad |
|---|---|---|---|---|
| P-01 | ¿Qué plataforma de atención humana van a usar? ¿Tiene API para transferir conversaciones con historial? | S-02 | Gerencia CX | Alta |
| P-02 | ¿Cuáles son las limitaciones documentadas de la API del ERP (rate limit, frescura del stock, stock por sucursal, ventanas de mantenimiento)? | S-04, S-09 | TI / proveedor ERP | Alta |
| P-03 | ¿El chat del e-commerce expone webhooks o una API para integrar un bot? | S-03 | Proveedor e-commerce | Alta |
| P-04 | ¿Cuándo pueden entregar las FAQs y políticas validadas (cambios, devoluciones, envíos, garantías)? ¿En qué formato? | S-12 | Gerencia CX | Alta |
| P-05 | ¿Qué volumen de consultas tuvieron en la última campaña y en un mes normal, por canal? | S-07 | Gerencia CX | Media |
| P-06 | ¿Confirman 10 turnos y 15 minutos como límites de sesión? | S-08 | Gerencia CX | Media |
| P-07 | ¿El CRM tiene API? ¿Aporta contexto útil para el MVP? | — | TI | Baja |
| P-08 | ¿El área legal valida la retención de 90 días con PII enmascarada y el procesamiento fuera del país? | S-11, S-15 | Legal | Media |
| P-09 | ¿El segundo dato para identificar al cliente (DNI, email o teléfono) está disponible en el pedido online? | S-06 | TI / e-commerce | Media |
| P-10 | ¿Cuánto tiempo y qué ambientes de prueba (sandbox) tienen disponibles las APIs del ERP y del e-commerce? | S-04 | TI | Alta |
| P-11 | ~~¿Quién recibe los mensajes de WhatsApp mientras atiende una persona?~~ **Resuelta por ADR-007:** la solución es la dueña del canal. Validar con el cliente que la plataforma de atención admita integración por API (canal personalizado). | S-02 | TI / Gerencia CX | Alta |
| P-12 | ¿Con qué proveedor está hoy la WABA de WhatsApp? ¿Tienen los PIN de los números? ¿Cuál es el nivel de mensajería y el throughput actual del número? ¿Cuándo hay una ventana sin campaña para migrar a End User Messaging Social? | S-18 | TI / proveedor actual | Alta |
| P-13 | ¿En qué cuenta AWS se despliega la solución (cuenta de TiendaNorte o de la Célula IA)? ¿Quién paga AWS y las tarifas de Meta que factura AWS? | S-19 | Gerencia CX / Finanzas | Alta |
