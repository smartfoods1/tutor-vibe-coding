# Seguridad

## Cómo reportar una vulnerabilidad

**No la cuentes en un issue público.** Reportala en privado con el reporte privado de
vulnerabilidades de GitHub (Security Advisories):

1. Entrá a la pestaña **Security** del repositorio.
2. Tocá **Report a vulnerability** ([link directo](https://github.com/smartfoods1/tutor-vibe-coding/security/advisories/new)).
3. Contá qué encontraste, cómo reproducirlo, qué impacto tiene y, si la tenés, una idea de cómo
   arreglarlo.

El reporte queda visible solo para quienes mantienen el proyecto. Es un proyecto sin fines de
lucro, mantenido a pulmón: intentamos responder dentro de los 7 días y, cuando haya un arreglo,
publicamos el aviso con crédito para vos, si lo querés.

Si no ves el botón **Report a vulnerability**, abrí un issue que diga solo «Contacto de seguridad»,
sin ningún detalle del problema, y te respondemos por dónde seguir en privado.

## Qué entra

- El backend (`backend/`): autenticación, sesiones, límites, topes de costo, manejo de datos de
  alumnos, voz y armado del kit.
- El frontend (`frontend/`) y las cabeceras de seguridad de `deploy/`.
- Los scripts de despliegue (`deploy/`).
- El kit (`contenido/kit/`): por ejemplo, instrucciones que hagan que Claude Code o Codex toquen
  archivos fuera de la carpeta del alumno, instalen algo sin pedir permiso o pidan contraseñas.
- El tutor de la web: formas de hacerle ignorar sus reglas con texto pegado o con una captura, de
  sacarle datos de otros alumnos o de gastar más allá de los topes.

## Qué no entra

- Los servicios de terceros (Anthropic, Google, Resend, Cloudflare, Netlify y otros): reportalos a
  cada empresa.
- Instalaciones de otras personas: avisale a quien la opera.
- Ataques de denegación de servicio por volumen, ingeniería social y problemas que requieren
  acceso físico o de administrador al servidor.

## Cómo probar

Probá siempre sobre una instalación propia, en tu compu (ver
[docs/desarrollo-local.md](docs/desarrollo-local.md)). No uses cuentas, datos ni instalaciones de
otras personas, y no accedas a datos de alumnos reales.

## Si operás una instalación

Las recomendaciones para el servidor (claves propias con límite de gasto, Turnstile, firewall,
backups y un usuario de despliegue sin root) están en [docs/desplegar.md](docs/desplegar.md).
Nunca dejes `DEV_CODIGO_FIJO` ni `MODO_DEMO=true` en producción.
