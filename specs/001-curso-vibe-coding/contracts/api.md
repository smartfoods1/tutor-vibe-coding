# Contrato: API de la puerta web

**Fecha**: 2026-09-28 · Base: `https://<dominio>/api` · JSON en UTF-8 salvo donde se indica.

Convenciones:
- **Sesión**: cookie `__Host-vibe_sesion` (constante `auth.COOKIE`; JWT HS256, 30 días, `Secure`,
  `HttpOnly`, `SameSite=Strict`, `Path=/`, sin `Domain`), con `sub` = id del alumno. El prefijo
  `__Host-` hace que el navegador no la acepte de un subdominio ni sin `Secure`. Sin cookie válida:
  `401`. (Hasta el 28/9/2026 se llamó `vibe_sesion`: las sesiones con el nombre viejo se pierden y
  hay que entrar de nuevo.)
- **Anti CSRF**: en `POST`, `PUT`, `PATCH` y `DELETE`, si el pedido trae la cabecera
  `Sec-Fetch-Site` y no vale `same-origin` ni `none`, responde `403 {"detalle": "..."}` antes de
  llegar a la ruta (middleware `auth.AntiCSRF`, instalado en `main.crear_app`; para apps de test,
  `auth.instalar_csrf(app)`). Sin la cabecera (clientes que no son un navegador, como la baja en un
  clic de los proveedores de mail) el pedido pasa. Las lecturas (`GET`) no se miran.
- **Admin**: la sesión de un mail igual a `ADMIN_EMAIL`. Si no es admin: `403`.
- **Aprobación manual** (`APROBACION_MANUAL=true`, apagada por defecto): cada alumno tiene un
  `estado`, `pendiente` o `aprobado`. Con la aprobación manual, quien verifica su mail por primera
  vez queda `pendiente` hasta que quien administra lo aprueba (salvo `ADMIN_EMAIL`, que entra
  `aprobado`); sin ella, todos entran `aprobado`. Quien administra siempre cuenta como `aprobado`.
  Una sesión `pendiente` solo llega a `GET /yo`, `GET` y `DELETE /mis-datos`,
  `PUT /consentimientos`, `POST /auth/salir` y las rutas públicas (legal, galería, config, baja);
  en todas las demás rutas del alumno (módulos, sesiones y turnos del tutor, idea, taller, kit,
  links y voz) responde `403 {"detalle": "Tu pedido de acceso está pendiente. Te avisamos por mail
  cuando esté aprobado.", "estado": "pendiente"}` (dependencia `auth.alumno_aprobado`). El chequeo
  mira el estado guardado, no la configuración: si se apaga `APROBACION_MANUAL`, los pendientes
  siguen esperando hasta que se los aprueba.
- **Errores**: `{"detalle": "<mensaje en voseo para mostrar>"}` con el código HTTP que corresponda.
- **Tope**: cuando el tutor está bloqueado por tope, los endpoints del tutor responden `402` con
  `{"detalle": "tope", "alcance": "alumno" | "mes", "guia": "/api/modulos/<n>/guia"}`.
- Todo texto que escribe el alumno pasa por límites de largo; lo que pega o sube se trata como
  datos, nunca como instrucciones (FR-033).

## Salud, configuración y textos legales

| Método y ruta | Acceso | Respuesta |
|---|---|---|
| `GET /salud` | público | `200 {"ok": true}` |
| `GET /config` | público | `200 {"turnstile_site_key": "..." \| null, "aviso_prueba": true \| false, "autor_nombre": "..." \| null, "newsletter": "..." \| null, "modo_demo": true \| false, "aprobacion_manual": true \| false}`: lo que la web necesita antes de que haya sesión. `autor_nombre` sale de `AUTOR_NOMBRE` y `newsletter` de `NEWSLETTER_NOMBRE` (vacíos: `null`; sin newsletter, la web no muestra la casilla de novedades); `modo_demo` es `MODO_DEMO` (el tutor responde con un guion fijo sin llamar a Claude y la voz queda apagada); `aprobacion_manual` es `APROBACION_MANUAL` (quien administra aprueba cada inscripción) |
| `GET /legal/privacidad` | público | `200 {"version", "titulo", "texto_md"}` del aviso de privacidad, con `{{AUTOR}}` y `{{NEWSLETTER}}` ya reemplazados; si falta, `404` amable |
| `GET /legal/consentimientos` | público | `200 {"version", "textos": {"mails_curso", "transferencia", "novedades"}, "texto_md"}` con `{{AUTOR}}` y `{{NEWSLETTER}}` ya reemplazados; si falta, `404` amable |

Los dos textos legales resuelven sus bloques condicionales antes de servirse: lo que está entre
`{{#NEWSLETTER}}` y `{{/NEWSLETTER}}` se muestra solo si hay newsletter, y lo que está entre
`{{#APROBACION}}` y `{{/APROBACION}}` (que el acceso lo aprueba quien administra, que mientras
está pendiente la cuenta no usa el tutor, que si no se aprueba los datos se borran a mano o a los
90 días y que la bienvenida llega al aprobar), solo con `APROBACION_MANUAL`. Versión vigente de los
dos: `2026-09-29`.

## Inscripción y acceso (FR-001 a FR-004)

### `POST /auth/codigo` (público)

```json
{
  "email": "persona@ejemplo.com",
  "turnstile": "<token de Cloudflare Turnstile>",
  "consentimientos": {"mails_curso": true, "transferencia": true, "novedades": false},
  "fuente": "hecho-en"
}
```

- Verifica el token de Turnstile contra Cloudflare; si falla: `400`.
- Límites: 5 códigos por mail por hora y 20 por IP por hora (configurables). Al pasarse, igual
  responde `200` sin enviar nada, para no revelar si el mail existe.
- Si el mail es nuevo y `mails_curso` o `transferencia` no son `true`: `422` con el motivo
  ("Para hacer el curso necesitamos mandarte mails del curso" o "El tutor funciona con proveedores
  en Estados Unidos; sin ese permiso no podemos darte el curso"). Ver [research.md](../research.md)
  §16.
- Guarda consentimientos y fuente como pendientes en el código; recién se aplican al verificar.
- Respuesta: siempre `200 {"ok": true}`.

### `POST /auth/verificar` (público)

```json
{"email": "persona@ejemplo.com", "codigo": "123456"}
```

- Válido: crea el alumno si no existe (con sus consentimientos y fuente), registra el evento
  `inscripcion`, setea la cookie y responde `200 {"ok": true, "nuevo": true | false, "estado":
  "pendiente" | "aprobado"}`.
- Sin `APROBACION_MANUAL`, el alumno nuevo queda `aprobado` y se encola el mail de bienvenida.
- Con `APROBACION_MANUAL`, el alumno nuevo queda `pendiente` (salvo `ADMIN_EMAIL`, que queda
  `aprobado` y recibe la bienvenida): no se manda la bienvenida y se encola el aviso a quien
  administra, `mails.enviar(settings, None, "pedidos", "pedidos:<AAAA-MM-DDTHH>", {"pendientes": n})`
  con la hora de Argentina en la clave, así sale como mucho uno por hora (ver [mails.md](mails.md)).
- Quien ya existía entra con el estado que tiene (`nuevo: false`), sin mails ni avisos.
- Inválido o vencido: `401`. Cada código admite 5 intentos.
- Tope de fallos por mail: cada intento errado suma un fallo al código (`codigos.fallos`). Si los
  códigos de ese mail creados en las últimas 24 horas suman más de 10 fallos, ningún código de ese
  mail vale hasta que esos fallos salen de la ventana: responde `401` igual que un código inválido,
  sin mirar el código (no hay forma de saber si se acertó). Otros mails no se ven afectados.

### `POST /auth/salir` (sesión)

Borra la cookie. `200 {"ok": true}`.

## Estado del alumno

### `GET /yo` (sesión)

```json
{
  "email": "persona@ejemplo.com",
  "es_admin": false,
  "modulo_actual": 2,
  "avance": [{"modulo": 1, "completado": "2026-11-03T20:10:00+00:00", "via": "tutor"}],
  "idea": {"version": 3, "actualizada": "2026-11-03T20:40:00+00:00"} ,
  "taller": {"herramienta": null, "sistema": null},
  "tope": {"bloqueado": false, "alcance": null},
  "consentimientos": {"mails_curso": true, "novedades": false},
  "audios": [{"modulo": 1, "url": "/audios/modulo-1.mp3", "transcripcion": "/audios/modulo-1.md"}],
  "estado": "aprobado"
}
```

`estado` es `pendiente` mientras quien administra no aprobó la inscripción (ver Aprobación manual
en las convenciones); quien administra siempre ve `aprobado`. `/yo` responde también a una sesión
`pendiente`.

## Módulos 1 a 3 (FR-005 a FR-012)

### `GET /modulos/{n}/guia` (sesión, n = 1..3)

La guía escrita del módulo (se usa también cuando el tutor está bloqueado por tope):
`{"modulo": n, "titulo": "...", "guia_md": "...", "audio": {...}}`. Sale de
`contenido/web/guia-modulo-<n>.md`; si falta, `404` con un mensaje amable. Un módulo que todavía
no está abierto da `403`; uno fuera de la web (4 a 7), `404`.

Para `n = 3`, el backend agrega al final de `guia_md` una sección `## Datos del día` con los datos
del machete de los temas `planes`, `instalar`, `ver`, `publicar` y `limites` (en ese orden, con un
`###` por tema), filtrados por la herramienta y el sistema del alumno si ya los eligió (sin
herramienta, de las dos; con sistema `otro` o sin sistema, de Mac y de Windows). Cada dato va con
su fecha de verificación y su fuente ("Verificado el 28/9/2026 · Fuente: https://..."). Así la guía
escrita no lleva datos que se vencen escritos a mano. Si el machete no se puede leer, la sección
dice que los datos no están disponibles y la guía responde igual `200`.

### `POST /modulos/{n}/sesion` (sesión)

Abre o retoma la conversación del módulo `n`. Solo se puede abrir el módulo actual o uno
anterior. `200 {"id": 42, "retomada": false}` o `402` por tope.

### `GET /sesiones/{id}` (sesión, dueño)

Mensajes visibles: `{"id", "modulo", "pendiente": true | false, "mensajes": [{"rol": "tutor" | "alumno", "texto": "..."}]}`.
Las capturas aparecen como el texto "[captura de pantalla enviada]". `pendiente` es `true` cuando
el último mensaje guardado es del alumno y el tutor todavía no respondió (por ejemplo, porque el
turno anterior falló): la web ofrece "Reintentar", que es un `POST .../turno` sin texto ni imagen.
Si la sesión es de otro alumno: `404`.

### `POST /sesiones/{id}/turno` (sesión, dueño)

`multipart/form-data` con `texto` (opcional, máx. 4.000 caracteres) e `imagen` (opcional, PNG/JPEG/
WebP, máx. 5 MB; el cliente la achica antes a 1.440 px en el lado largo, unos 1.700 tokens). Al
menos uno de los dos, salvo que la sesión esté `pendiente` (reintento).

Respuesta: `text/event-stream` con estos eventos:

| Evento | Datos |
|---|---|
| `pensando` | `{}` |
| `texto` | `{"delta": "..."}` |
| `herramienta` | `{"nombre": "guardar_idea", "estado": "inicio" \| "fin", "error": false}` |
| `avance` | `{"modulo_completado": 2, "modulo_actual": 3}` (cuando el tutor marca el módulo) |
| `idea` | `{"version": 4}` (cuando el tutor guarda la idea) |
| `taller` | `{"herramienta": "codex" \| "claude", "sistema": "mac" \| "windows" \| "otro"}` (cuando el tutor usa `registrar_taller`; la web actualiza lo que muestra del taller y del kit sin recargar) |
| `fin` | `{"stop_reason": "end_turn"}` |
| `tope` | `{"alcance": "alumno" \| "mes", "guia": "/api/modulos/2/guia"}` |
| `error` | `{"mensaje": "...", "reintentable": true}` |

La imagen solo viaja en la llamada en curso; en la base queda el marcador de texto (FR-011). El
costo del turno se suma al alumno y al mes; el tope se chequea antes de llamar al modelo.

### `POST /modulos/{n}/completar` (sesión)

Para quien usa la guía escrita: marca el módulo con `via = guia_escrita`. `200` con el nuevo
`modulo_actual`. Para `n = 2` exige que haya una idea guardada (`409` si no).

## Idea (FR-008, FR-009)

| Método y ruta | Acceso | Cuerpo / respuesta |
|---|---|---|
| `GET /idea` | sesión | `200 {"version", "texto_md", "que_sigue_md", "autor", "creado"}` o `404` |
| `PUT /idea` | sesión | `{"texto_md", "que_sigue_md"}` → nueva versión con `autor = alumno`; `200 {"version"}` |
| `GET /idea.md` | sesión | descarga `mi-idea.md` (`text/markdown`) |
| `GET /idea/plantilla` | sesión | `200 {"texto_md": "..."}`: la plantilla de "mi idea en una página", leída de `contenido/web/plantilla-idea.md` sin el frontmatter. Es la única plantilla: la usan la web y la guía escrita. Si falta el archivo, `404` con un mensaje amable |

## Taller y kit (FR-010, FR-013)

### `PUT /taller` (sesión)

`{"herramienta": "codex" | "claude", "sistema": "mac" | "windows" | "otro"}` → `200`. Con
`sistema = otro`, el kit no se habilita y la respuesta trae qué hace falta para seguir.

### `GET /kit` (sesión)

Arma y descarga el kit personalizado (`application/zip`, nombre `mi-proyecto-<slug>.zip`).
Requiere idea guardada y taller elegido con `mac` o `windows`; si falta algo: `409` con qué falta.
Registra la descarga en `kits`, el evento `kit` y sube `modulo_actual` a 4 si estaba en 3.
Contenido del zip: ver [kit.md](kit.md).

### `GET /kit/pasos` (sesión)

Los pasos para abrir el kit y seguir en la computadora, para la pantalla "Cómo seguir en tu computadora"
(FR-034): `200 {"herramienta": "claude" | "codex", "sistema": "mac" | "windows", "texto_md": "..."}`.
`texto_md` es el `LEEME-<herramienta>.txt` de la plantilla del kit pasado a markdown (`kit.pasos`): los
títulos en mayúsculas pasan a `##`, lo que hay que escribir en la herramienta va entre comillas de
código y "Kit armado el <fecha>" pasa a "Los pasos para". Solo lee: no arma el kit ni registra nada, y no
pide la idea. Sin herramienta o sin computadora Mac o Windows: `409` con qué falta. Con la plantilla rota:
`503`.

## Mostrar lo que hizo (FR-022, FR-023)

### `POST /links` (sesión)

```json
{"url": "https://mi-idea.netlify.app", "titulo": "Mi registro de sueños", "mostrar_galeria": false, "uso_contenido": false}
```

- `409 {"detalle"}` si el alumno todavía no bajó el kit (`modulo_actual < 4`) o si ya tiene 5
  links (borrando uno se libera lugar).
- `422 {"detalle"}` si la URL no empieza con `https://`, no tiene un dominio, lleva usuario
  (`@`), espacios o más de 500 caracteres; si el título pasa de 120 caracteres; o si la URL o el
  título traen caracteres de control o de formato (categorías Unicode `Cc` y `Cf`: saltos de
  línea, tabulaciones, nulos, espacios invisibles, marcas de dirección del texto).
- `201 {"id": 7, "mail": true | false}`. Registra el evento `link` y pone `modulo_actual = 7`.
  `mail` dice si el mail "contame qué hiciste" se va a mandar: es `true` cuando el alumno acepta
  los mails del curso (`mails_curso` vigente) y nunca se le mandó un contame. El contame sale una
  sola vez en la vida del alumno, con el primer link que registra con los mails aceptados (clave
  `contame`, ver [mails.md](mails.md)).

### `GET /links` (sesión)

Los links propios, del más viejo al más nuevo:
`[{"id", "url", "titulo", "mostrar_galeria", "uso_contenido", "aprobado", "creado"}]`
(`mostrar_galeria`, `uso_contenido` y `aprobado` son `true` o `false`).

### `PATCH /links/{id}` (sesión, dueño)

`{"mostrar_galeria"?: bool, "uso_contenido"?: bool}` → `200` con el link, en el mismo formato de
`GET /links`. Sin ningún campo: `422`. Si el link es de otro alumno o no existe: `404`. La URL y el
título no se cambian: para eso se borra y se registra de nuevo. Cambiar `mostrar_galeria` no toca
`aprobado`.

### `DELETE /links/{id}` (sesión, dueño)

Borra el link: `200 {"ok": true}`. Si es de otro alumno o no existe: `404`.

### `GET /galeria` (público)

Solo links con `mostrar_galeria = 1` **y** `aprobado = 1` (la galería es moderada: quien
administra aprueba cada link, ver Admin), los más nuevos primero y como mucho 200:
`[{"titulo": "...", "url": "..."}]`, sin mails ni nombres.

## Datos del alumno (FR-002, FR-030)

| Método y ruta | Acceso | Qué hace |
|---|---|---|
| `PUT /consentimientos` | sesión | `{"novedades": true \| false}` → agrega fila al historial; sin newsletter en la instalación, `novedades` queda en 0 |
| `GET /mis-datos` | sesión | descarga un JSON con todos sus datos (alumno con su `estado`, consentimientos, avance, ideas, conversaciones, kits, links con `aprobado`, mails) |
| `DELETE /mis-datos` | sesión | `{"confirmar": "BORRAR"}` → borra todo, cierra la sesión; `200` |
| `GET /baja?t=<token>` | público | baja de mails del curso con token firmado (sin sesión, propósito `baja`, ver [mails.md](mails.md)); `200 {"ok": true}`; token inválido: `400` |
| `POST /baja?t=<token>` | público | igual que el GET, para la baja en un clic de RFC 8058 (los proveedores de mail no mandan `Sec-Fetch-Site`, así que el anti CSRF no la frena) |

## Voz

| Método y ruta | Acceso | Qué hace |
|---|---|---|
| `POST /voz/transcribir` | sesión | audio del micrófono (máx. 15 MB) → `{"texto": "..."}`; cuenta en el tope |
| `POST /voz/hablar` | sesión | `{"texto": "..."}` (máx. 600 caracteres por frase) → `audio/mpeg`; cuenta en el tope |

Con el tutor bloqueado por tope, los dos responden `402`.

Techos de `POST /voz/transcribir`:

- Más de 30 transcripciones de un alumno en la última hora: `429 {"detalle"}`. Cuentan todos los
  pedidos que pasan el tope, también los que después fallan (el costo de un pedido fallido de
  Gemini no se registra). La cuenta vive en la memoria del proceso (el servicio corre en uno solo)
  y se reinicia con el servicio.
- Archivo de más de 15 MB: `413`. Vacío o ilegible: `422`.
- El audio se convierte a MP3 mono de 16 kHz cortado a 200 segundos (`-t 200` en ffmpeg), aunque
  el archivo diga otra duración. Si el MP3 resultante pasa de 15 MB: `413`, antes de armar el
  pedido a Gemini.
- Gemini caído: `502`.

En todo el servidor corren como mucho 2 audios a la vez (un `asyncio.Semaphore(2)` alrededor de la
conversión con ffmpeg y del pedido a Gemini, para transcribir y para hablar); los demás esperan
su turno.

## Admin (FR-026 a FR-029)

| Método y ruta | Qué devuelve |
|---|---|
| `GET /admin/reporte` | embudo (inscriptos, módulos 1 a 3 completados, kits, links; totales y últimos 30 días; por `fuente`), gasto del mes contra el tope, gasto promedio por alumno, datos del machete con más de 45 días y `pendientes` (cantidad de pedidos de acceso sin aprobar). Un pendiente cuenta como inscripto desde que verifica su mail |
| `GET /admin/novedades.csv` | CSV de una sola columna, `email`, con los alumnos cuyo último consentimiento `novedades` es 1, en el formato que importa la plataforma de newsletter del autor (ver [research.md](../research.md) §9) |
| `GET /admin/links` | los links que sus dueños quieren mostrar (`mostrar_galeria = 1`), pendientes primero y dentro de cada grupo los más nuevos arriba: `[{"id", "url", "titulo", "mostrar_galeria", "aprobado", "creado"}]`, sin mails ni nombres |
| `PUT /admin/links/{id}` | `{"aprobado": true \| false}` → `200` con el link en el formato de `GET /admin/links`; si no existe, `404`; sin booleano, `422`. Aprobar pone el link en la galería pública (si su dueño sigue queriendo mostrarlo); desaprobar lo saca |
| `GET /admin/pedidos` | los pedidos de acceso (alumnos con `estado = pendiente`), los más viejos primero: `[{"id", "email", "creado", "fuente"}]` |
| `POST /admin/pedidos/{id}/aprobar` | pasa al alumno a `aprobado`, registra el evento `aprobacion`, encola la bienvenida (`mails.enviar(settings, id, "bienvenida", "bienvenida")`, respeta la baja si la dio mientras esperaba) y responde `200 {"ok": true}`; si no existe, `404`; si ya estaba aprobado, `409` |
| `DELETE /admin/pedidos/{id}` | rechaza el pedido: borra al alumno `pendiente` con todos sus datos (en cascada, más sus códigos) y registra un evento `borrado` anónimo; `200 {"ok": true}`. Si no existe, `404`; si está `aprobado`, `409` (a un aprobado no se lo borra desde acá). Quien fue rechazado puede volver a inscribirse y queda otra vez `pendiente` |

Todas las rutas de admin responden `401` sin sesión y `403` si la sesión no es de `ADMIN_EMAIL`.

## Archivos estáticos (nginx)

- `/` y rutas del frontend: la app (PWA).
- `/audios/modulo-<n>.mp3` y `/audios/modulo-<n>.md`: audios del autor y sus transcripciones,
  públicos (el kit los enlaza para los módulos 4 a 7).
