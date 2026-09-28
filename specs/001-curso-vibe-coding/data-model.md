# Data Model: Curso gratuito de vibe coding para la tribu

**Fecha**: 2026-09-28 · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Una sola base SQLite (modo WAL) en `/srv/vibe-tutor/data/vibe.db`, con migraciones numeradas por
`PRAGMA user_version` como en el proyecto anterior. Todas las fechas se guardan en UTC con formato
ISO 8601 (`2026-09-28T14:00:00+00:00`); los cortes por mes se calculan en hora de Argentina.

El contenido del curso (guías de módulos, lecciones del kit, machete, mails, audios) no vive en la
base: son archivos versionados en `contenido/` (ver [plan.md](plan.md)).

## Entidades

### alumnos

Persona inscripta y verificada. Solo existe después de validar el código del mail.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| email | TEXT UNIQUE NOT NULL | normalizado (minúsculas, sin espacios), máx. 320 |
| creado | TEXT NOT NULL | |
| ultima_actividad | TEXT NOT NULL | se actualiza en cada turno, descarga o registro |
| herramienta | TEXT NULL | `codex` o `claude` (FR-010) |
| sistema | TEXT NULL | `mac`, `windows` u `otro` (US3, escenario 5) |
| modulo_actual | INTEGER NOT NULL DEFAULT 1 | 1 a 7 |
| fuente | TEXT NULL | de dónde llegó (`?ref=` de la landing, por ejemplo `hecho-en` o una palabra clave), máx. 64 |
| estado | TEXT NOT NULL DEFAULT `aprobado` | migración 4 (29/9): `pendiente` o `aprobado`. Con `APROBACION_MANUAL`, quien verifica su mail por primera vez queda `pendiente` (salvo `ADMIN_EMAIL`) hasta que quien administra lo aprueba; los alumnos anteriores a la migración quedaron `aprobado` |

Transiciones de `estado`: `pendiente` → `aprobado` al aprobar el pedido desde el admin (evento
`aprobacion` y mail de bienvenida). Un `pendiente` no vuelve a `aprobado` solo ni al revés: si se
rechaza el pedido o pasan 90 días sin aprobarlo, se borra el alumno con sus datos.

Transiciones de `modulo_actual`: sube cuando se completa el módulo anterior (herramienta
`marcar_avance`, o botón "ya lo hice" de la guía escrita). Del 3 al 4 sube cuando descarga el kit.
Del 4 al 7 no hay registro automático (el alumno trabaja en su herramienta); el 7 se marca al
registrar un link.

### consentimientos

Historial de permisos; vale la fila más reciente de cada tipo (FR-002, FR-023, FR-029).

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NOT NULL FK alumnos | ON DELETE CASCADE |
| tipo | TEXT NOT NULL | `mails_curso`, `transferencia`, `novedades` (migración 3: renombra el tipo que usaba la primera versión) |
| valor | INTEGER NOT NULL | 0 o 1 |
| version_texto | TEXT NOT NULL | versión del texto legal mostrado (por ejemplo `2026-10-01`) |
| creado | TEXT NOT NULL | |

`mails_curso = 1` y `transferencia = 1` (consentimiento expreso para procesar datos con
proveedores en Estados Unidos, Ley 25.326 art. 12; ver research §16) son obligatorios para
inscribirse. La baja por mail agrega una fila con `valor = 0`. `novedades` es opcional y se pide
solo si la instalación tiene newsletter (`NEWSLETTER_NOMBRE`); si no, queda en 0.
Los consentimientos de mostrar un link viven en `links` porque son por link.

### codigos

Como en el proyecto anterior, más el origen para limitar abusos por IP (FR-003) y los datos de inscripción
pendientes, que se aplican solo al verificar.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| email | TEXT NOT NULL | |
| hash, sal | TEXT NOT NULL | SHA-256 de sal + código de 6 dígitos |
| vence | TEXT NOT NULL | 10 minutos |
| intentos | INTEGER NOT NULL DEFAULT 0 | máximo 5 |
| fallos | INTEGER NOT NULL DEFAULT 0 | migración 2 (28/9): más de 10 fallos sumando los códigos del mail en 24 h bloquean ese mail hasta que pase la ventana |
| usado | INTEGER NOT NULL DEFAULT 0 | |
| ip | TEXT NOT NULL | para el límite por origen |
| pendiente_json | TEXT NULL | consentimientos y fuente elegidos en el formulario; se borra al verificar o a las 24 h |
| creado | TEXT NOT NULL | |

Los códigos vencidos se purgan a las 24 h (no guardan datos de alguien que nunca verificó).

### avance

Un registro por módulo completado (FR-024).

| Campo | Tipo | Reglas |
|---|---|---|
| alumno_id | INTEGER FK alumnos | PK compuesta con `modulo`; ON DELETE CASCADE |
| modulo | INTEGER | 1 a 3 (los del 4 al 6 no se registran; el 7 se deriva de `links`) |
| completado | TEXT NOT NULL | |
| resumen | TEXT NULL | 2 a 5 líneas que el tutor deja para el módulo siguiente, máx. 1.000 caracteres |
| via | TEXT NOT NULL | `tutor` o `guia_escrita` |

### ideas

"Mi idea en una página" y lo que quedó para "qué sigue" (FR-008, FR-009). Versionada: la
versión más alta es la vigente.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NOT NULL FK alumnos | ON DELETE CASCADE |
| version | INTEGER NOT NULL | 1, 2, 3… UNIQUE (alumno_id, version) |
| texto_md | TEXT NOT NULL | máx. 6.000 caracteres |
| que_sigue_md | TEXT NULL | máx. 3.000 caracteres |
| autor | TEXT NOT NULL | `tutor` o `alumno` (edición manual) |
| creado | TEXT NOT NULL | |

### sesiones

Una conversación con el tutor por alumno y por módulo (1 a 3). Se retoma la abierta en vez de
crear otra.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NOT NULL FK alumnos | ON DELETE CASCADE |
| modulo | INTEGER NOT NULL | 1 a 3 |
| inicio | TEXT NOT NULL | |
| fin | TEXT NULL | se completa al cerrar el módulo |
| costo_usd | REAL NOT NULL DEFAULT 0 | |

### mensajes

Como en el proyecto anterior: bloques de la API guardados en JSON, en orden.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| sesion_id | INTEGER NOT NULL FK sesiones | ON DELETE CASCADE |
| orden | INTEGER NOT NULL | UNIQUE (sesion_id, orden) |
| rol | TEXT NOT NULL | `user` o `assistant` |
| contenido_json | TEXT NOT NULL | los bloques `image` nunca se guardan: se reemplazan por el texto `[captura de pantalla enviada]` (FR-011) |
| creado | TEXT NOT NULL | |

### uso

Costo de cada llamada a un proveedor de IA, como en el proyecto anterior, más el alumno para el tope
individual (FR-026).

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NULL FK alumnos | ON DELETE SET NULL (el gasto del mes se conserva sin dato personal) |
| sesion_id | INTEGER NULL FK sesiones | ON DELETE SET NULL |
| creado | TEXT NOT NULL | |
| proveedor | TEXT NOT NULL | `anthropic` o `gemini` |
| modelo | TEXT NOT NULL | |
| input_tokens, output_tokens, cache_write, cache_read | INTEGER NOT NULL DEFAULT 0 | |
| costo_usd | REAL NOT NULL DEFAULT 0 | |

Reglas de tope:
- Gasto del alumno = `SUM(costo_usd) WHERE alumno_id = ?` (toda su vida). Si llega a
  `TOPE_ALUMNO_USD` (US$1), el tutor queda bloqueado para ese alumno.
- Gasto del mes = suma del mes calendario en hora de Argentina. Al 80% de `TOPE_MENSUAL_USD`
  (US$50) se avisa a Andrés una sola vez por mes; al 100% el tutor queda bloqueado para todos.
- El bloqueo se chequea antes de cada turno, no solo al abrir la sesión.

### kits

Cada descarga del kit (FR-013, FR-024).

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NOT NULL FK alumnos | ON DELETE CASCADE |
| creado | TEXT NOT NULL | |
| version_curso | TEXT NOT NULL | versión de `contenido/` (fecha + commit corto) |
| fecha_machete | TEXT NOT NULL | fecha de verificación más vieja de los datos incluidos |
| herramienta | TEXT NOT NULL | `codex` o `claude` |
| sistema | TEXT NOT NULL | `mac` o `windows` |

### links

Link publicado que registra el alumno (FR-023).

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NOT NULL FK alumnos | ON DELETE CASCADE |
| url | TEXT NOT NULL | `https://` obligatorio, máx. 500 |
| titulo | TEXT NULL | máx. 120 |
| mostrar_galeria | INTEGER NOT NULL DEFAULT 0 | |
| uso_contenido | INTEGER NOT NULL DEFAULT 0 | |
| aprobado | INTEGER NOT NULL DEFAULT 0 | migración 2 (28/9): la galería muestra solo links con `mostrar_galeria = 1` y `aprobado = 1`; aprueba Andrés desde el admin |
| creado | TEXT NOT NULL | |

### mails

Registro de mails del curso para no repetirlos y para la regla de frecuencia (FR-025).

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NULL FK alumnos | ON DELETE CASCADE; NULL para avisos a Andrés |
| tipo | TEXT NOT NULL | `bienvenida`, `recordatorio`, `contame`, `aviso_80`, `pedidos` (migración 4: aviso de pedidos de acceso a quien administra) |
| clave | TEXT NOT NULL | evita duplicados: `bienvenida`, `recordatorio`, `contame` (una vez en la vida, con el primer link), `aviso_80:<AAAA-MM>`, `pedidos:<AAAA-MM-DDTHH>` (hora de Argentina: uno por hora como mucho) |
| estado | TEXT NOT NULL | `enviado` o `fallido` |
| creado | TEXT NOT NULL | |

UNIQUE (alumno_id, clave), y un índice único parcial sobre `clave` para las filas sin alumno
(`idx_mails_sin_alumno`). Máximo un recordatorio por alumno en toda su vida.

### eventos

Embudo para el reporte y la regla de los 30 días (FR-024, SC-009). No guarda datos personales en
`detalle`.

| Campo | Tipo | Reglas |
|---|---|---|
| id | INTEGER PK | |
| alumno_id | INTEGER NULL FK alumnos | ON DELETE SET NULL (al borrar un alumno, el evento queda anónimo) |
| tipo | TEXT NOT NULL | `inscripcion`, `modulo_completo`, `kit`, `link`, `baja_mails`, `borrado`, `aprobacion` (migración 4: quien administra aprobó el pedido de acceso) |
| detalle | TEXT NULL | por ejemplo `modulo=2`, `herramienta=codex`, `fuente=hecho-en` |
| creado | TEXT NOT NULL | |

## Relaciones

```text
alumnos 1─* consentimientos
alumnos 1─* avance
alumnos 1─* ideas
alumnos 1─* sesiones 1─* mensajes
alumnos 1─* uso (SET NULL al borrar)
alumnos 1─* kits
alumnos 1─* links
alumnos 1─* mails
alumnos 1─* eventos (SET NULL al borrar)
```

`PRAGMA foreign_keys = ON` en cada conexión, para que funcionen los CASCADE y los SET NULL.

## Migraciones

| Número | Qué hace |
|---|---|
| 1 | Esquema inicial |
| 2 | `links.aprobado` (galería moderada) y `codigos.fallos` |
| 3 | El consentimiento opcional pasa a llamarse `novedades` (recrea `consentimientos`) |
| 4 | `alumnos.estado` (aprobación manual; los existentes quedan `aprobado`), `mails.tipo` suma `pedidos` y `eventos.tipo` suma `aprobacion`. Como SQLite no cambia un CHECK, recrea `mails` y `eventos` con las mismas filas, ids, fechas e índices, y conserva el contador de ids (`sqlite_sequence`) para no reusar los de filas borradas |

Una base nueva corre las cuatro migraciones en orden, así termina con el mismo esquema que una
migrada (hay un test que lo compara).

## Retención y borrado (FR-030, FR-031)

- Borrado a pedido: se borra la fila de `alumnos` y, en cascada, consentimientos, avance, ideas,
  sesiones, mensajes, kits, links y mails. En `uso` y `eventos` queda la fila sin `alumno_id`. Se
  registra un evento `borrado` anónimo.
- Conversaciones (decidido por Andrés el 28/9/2026, research §16): la tarea diaria borra cada
  sesión (y sus `mensajes`) 30 días después de su `fin`, es decir, de completar el módulo; las
  sesiones sin terminar se borran 12 meses después de la última actividad del alumno. Queda el
  `resumen` del módulo en `avance`, que el tutor escribe sin datos personales ni de salud. La idea,
  el avance y los links quedan hasta que el alumno los borre.
- Códigos: se purgan a las 24 h de creados.
- Pedidos de acceso sin aprobar (`alumnos.estado = pendiente`, solo con `APROBACION_MANUAL`): se
  borran cuando quien administra rechaza el pedido (`DELETE /admin/pedidos/{id}`) o, si nadie lo
  aprueba, la tarea periódica los borra a los 90 días de `creado`. En los dos casos se va el alumno
  con todos sus datos (en cascada) y queda un evento `borrado` anónimo.
- Capturas: nunca se guardan (ni en disco ni en la base).

## Contenido versionado (fuera de la base)

### Dato del machete (`contenido/machete.yaml`)

| Campo | Reglas |
|---|---|
| id | slug único, por ejemplo `codex-instalar-windows` |
| tema | `instalar`, `planes`, `publicar`, `ver`, `volver-atras`, `limites`, `ayuda` |
| aplica_a | lista con `codex` o `claude` o las dos |
| sistema | lista con `mac` o `windows` o las dos |
| texto | el dato o los pasos, en voseo, máx. 1.500 caracteres |
| fuente | URL oficial |
| verificado | fecha `AAAA-MM-DD` de la última verificación |
| probado | `true` si se comprobó en una prueba real (Constitución IV: "gratis" exige `true`) |

Validaciones (tests de contenido, corren en cada PR): ids únicos, fuente con `https://`, fecha
válida no futura, y que ningún dato que prometa que algo no se paga ("gratis", "gratuito",
"sin pagar", "sin costo") tenga `probado: false`. El reporte de Andrés
marca los datos con más de 45 días (SC-007).
