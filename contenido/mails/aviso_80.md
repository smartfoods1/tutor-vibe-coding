---
asunto: "Aviso: el tutor llegó al 80% del tope del mes"
estado: borrador
# Para quien administra el curso (ADMIN_EMAIL). Sin pie legal ni link de baja. Una vez por mes.
---

Hola.

El gasto del tutor de la web llegó al 80% del tope de este mes.

Gasto del mes, en dólares: {{GASTO_MES}}
Tope del mes, en dólares: {{TOPE_MES}}
Alumnos con actividad este mes: {{ALUMNOS_ACTIVOS}}

Si el gasto llega al tope, el tutor deja de responder a todos hasta el mes que viene. Los alumnos siguen con la guía escrita de cada módulo, sin perder el avance.

Si querés subir el tope, se cambia TOPE_MENSUAL_USD en /etc/vibe-tutor/.env y se reinicia el servicio. Es tu decisión: sube el costo del mes.

El detalle está en el reporte: {{ENLACE_REPORTE}}

Este aviso sale una sola vez por mes.
