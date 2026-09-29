# Quickstart: validar el siguiente paso

**Fecha**: 2026-09-28. Todo en local y en modo demo, sin claves de API, como indica [docs/desarrollo-local.md](../../docs/desarrollo-local.md).

## Preparación

En `backend/.env.local` (no se versiona), además de lo habitual del modo demo:

```bash
SIGUIENTE_PASO=true
SIGUIENTE_PASO_NOMBRE=el curso de prueba
SIGUIENTE_PASO_PREGUNTA=¿Tenés un negocio que ya vende?
SIGUIENTE_PASO_TEXTO=En marzo abre un curso para construir el sistema que lo gestiona.
```

Levantar backend y frontend como dice la guía, inscribirse con un mail de prueba y llegar al módulo 4 (el kit bajado).

## Escenarios

1. **Apagada** (sin `SIGUIENTE_PASO`): registrar un link en "Mostrar". La pantalla es la de siempre, sin pregunta (SC-001).
2. **Sí con aviso**: con la función prendida, alumno nuevo, primer link. Aparece la pregunta. "Sí" muestra el texto y la casilla desmarcada, sin precios. Marcarla y confirmar. En "Mis datos" figura el aviso con su fecha. En el reporte del admin: `contestaron` 1, `con_negocio` 1 y `avisos_activos` 1.
3. **No**: otro alumno, primer link, "No". No aparece el texto. El reporte suma 1 a `contestaron` y nada a `con_negocio`.
4. **Ahora no**: otro alumno cierra la pregunta. No cambia ningún número.
5. **Segundo link**: cualquiera de los tres registra otro link. No hay pregunta.
6. **Sacar el aviso**: el alumno del escenario 2 lo saca desde "Mis datos". `avisos_activos` baja a 0. Con la función apagada, la casilla sigue visible mientras el aviso esté prendido, y se puede sacar.
7. **Falta un texto**: vaciar `SIGUIENTE_PASO_TEXTO` y reiniciar. No aparece la pregunta y el reporte muestra `falta_configurar` con esa clave.
8. **Descargar y borrar**: la descarga de "Mis datos" trae `siguiente_paso_respondido` y el historial del aviso. Después de borrar todo, los totales del reporte no cambian y el aviso ya no cuenta.

## Tests

```bash
(cd backend && .venv/bin/pytest)
(cd frontend && npm test)
```
