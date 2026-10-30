# Arquitectura de despliegue (resumen) — TiendaNorte

> Guía de [`despliegue-resumen.drawio`](despliegue-resumen.drawio). Versión resumida de [`despliegue.drawio`](despliegue.drawio), pensada para insertar en documentos. Agrupa componentes; el detalle está en la versión completa y en los ADR.

- **Exportado:** `export/despliegue-resumen.drawio.png` [[COMPLETAR: exportar PNG]]
- **Versión / fecha:** v0.1 · 2026-10-29

1. **①** Los clientes usan WhatsApp o el chat web.
2. **②** WhatsApp se conecta a AWS con **End User Messaging Social**, y el chat web con **API Gateway + WAF**.
3. **③** Una capa de **entrada y salida** (Lambda + cola SQS FIFO) absorbe los picos y entrega los mensajes en orden al **orquestador de sesión**. El orquestador aplica los controles de **Bedrock Guardrails** y guarda el estado en **DynamoDB**.
4. **④** El orquestador invoca al agente en **AgentCore Harness**.
5. **⑤** El agente razona con modelos de **Bedrock** (Claude Haiku / Sonnet).
6. **⑥** El agente consulta datos con las tools de **AgentCore Gateway** (MCP) y las políticas en la **Knowledge Base**.
7. **⑦** Las tools llegan a las APIs de e-commerce, ERP y CRM de TiendaNorte, en solo lectura.

**Derivación:** cuando hace falta una persona, el orquestador deriva la conversación a la plataforma de atención humana con todo el contexto (rojo punteado).

**Convenciones:**
- Flecha doble: ida y vuelta (mensaje y respuesta).
- Servicios transversales (observabilidad, cifrado, secretos y auditoría) indicados al pie del diagrama.
