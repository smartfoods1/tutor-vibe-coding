# Contrato: cambios en la API por el siguiente paso

**Fecha**: 2026-09-28. Mismas convenciones que el [contrato del spec 001](../../001-curso-vibe-coding/contracts/api.md): sesión, anti CSRF, aprobación manual y errores `{"detalle": "..."}` en voseo.

"Función activa" quiere decir `SIGUIENTE_PASO=true` y los tres textos con valor (`Settings.hay_siguiente_paso`).

## `GET /config` (público)

Suma `"siguiente_paso": {"nombre": "...", "pregunta": "...", "texto": "..."} | null`. Es `null` si la función no está activa.

## `GET /legal/consentimientos` (público)

`textos` suma `siguiente_paso`: el texto corto de la casilla, con `{{AUTOR}}` y `{{SIGUIENTE_PASO}}` reemplazados. La sección de `{{#SIGUIENTE_PASO}}` aparece en `texto_md` solo con la función activa.

## `POST /links` (sesión, aprobado)

Todo igual y la respuesta suma un campo: `201 {"id": 7, "mail": true | false, "pregunta_siguiente_paso": true | false}`.

`pregunta_siguiente_paso` es `true` solo si la función está activa, este es el primer link del alumno (tiene un solo evento `link`) y todavía no contestó (`siguiente_paso_respondido = 0`).

## `POST /siguiente-paso` (sesión, aprobado) — nuevo

```json
{"respuesta": "si", "aviso": true}
```

- `respuesta`: `"si"` o `"no"`. `aviso`: booleano, `false` por defecto.
- `409 {"detalle"}` si la función no está activa, si el alumno no registró ningún link o si ya contestó.
- `422 {"detalle"}` si `respuesta` no es `"si"` ni `"no"`, o si `aviso` es `true` con `"no"`.
- `200 {"consentimientos": {"mails_curso": ..., "novedades": ..., "siguiente_paso": ...}}`. El objeto de adentro tiene el mismo formato que la respuesta de `PUT /consentimientos`, que lo devuelve sin envolver.
- Efecto, en una sola transacción: `siguiente_paso_respondido = 1`, suma 1 al total de esa respuesta en `respuestas_siguiente_paso` y, si `aviso` es `true`, agrega la fila `siguiente_paso = 1` con `version_legal()`.
- Una sesión pendiente recibe el `403` de la aprobación manual, como las demás rutas del alumno.

## `GET /yo` y `PUT /consentimientos` (sesión)

- `consentimientos` suma `siguiente_paso` (`true` o `false`, siempre presente).
- `PUT` acepta `"siguiente_paso": true | false`. `true` solo con la función activa; si no, `409 {"detalle"}`. `false` se acepta siempre, para que el aviso se pueda sacar aunque la función se apague.

## `GET /mis-datos` (sesión)

El alumno suma `siguiente_paso_respondido`. El historial de permisos ya trae las filas de `siguiente_paso`.

## `GET /admin/reporte` (admin)

Suma:

```json
"siguiente_paso": {
  "activo": true,
  "falta_configurar": [],
  "contestaron": 12,
  "con_negocio": 5,
  "avisos_activos": 4
}
```

- `falta_configurar`: los nombres de las claves vacías (`SIGUIENTE_PASO_NOMBRE`, `SIGUIENTE_PASO_PREGUNTA`, `SIGUIENTE_PASO_TEXTO`) cuando la bandera está prendida; vacía si está apagada o completa.
- `contestaron`: total de `si` más total de `no`. `con_negocio`: total de `si`.
- `avisos_activos`: alumnos que existen y cuyo último permiso `siguiente_paso` vale 1.
