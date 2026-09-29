# Modelo de datos: Siguiente paso

**Fecha**: 2026-09-28. Parte del modelo del spec 001 ([data-model.md](../001-curso-vibe-coding/data-model.md)); acá solo lo que cambia.

## alumnos

| Campo | Tipo | Reglas |
|---|---|---|
| siguiente_paso_respondido | INTEGER NOT NULL DEFAULT 0 | 0 o 1. Pasa a 1 cuando contesta la pregunta. No dice qué contestó. |

## consentimientos

`tipo` suma `siguiente_paso`: el pedido de aviso del siguiente paso. Es opcional, se pide solo con la función activa y se saca en cualquier momento. Como los demás, vale la fila más reciente y `version_texto` guarda la versión del texto legal.

## respuestas_siguiente_paso (nueva)

| Campo | Tipo | Reglas |
|---|---|---|
| respuesta | TEXT NOT NULL PRIMARY KEY | `si` o `no` (SQLite acepta NULL en una clave de texto si no se lo prohíbe) |
| total | INTEGER NOT NULL DEFAULT 0 | 0 o más; se suma de a uno con un UPSERT |

No tiene alumno ni fecha, a propósito (FR-012). Borrar a un alumno no la toca.

## Migración 5

1. `ALTER TABLE alumnos ADD COLUMN siguiente_paso_respondido INTEGER NOT NULL DEFAULT 0 CHECK (siguiente_paso_respondido IN (0, 1))`.
2. Recrea `consentimientos` con `tipo IN ('mails_curso', 'transferencia', 'novedades', 'siguiente_paso')`: mismas filas, ids, fechas e índice, y conserva el contador de ids (`sqlite_sequence`), como la migración 4.
3. Crea `respuestas_siguiente_paso`.

Una base nueva corre las cinco migraciones en orden y termina con el mismo esquema que una migrada.

## Borrado y descarga

- Al borrar sus datos, se van la fila del alumno (con `siguiente_paso_respondido`) y sus permisos (CASCADE). Los totales de `respuestas_siguiente_paso` quedan.
- La descarga de "Mis datos" suma `siguiente_paso_respondido` al alumno; el historial de permisos ya incluye las filas de `siguiente_paso`.
