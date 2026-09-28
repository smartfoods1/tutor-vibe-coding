# Implementation Plan: Curso gratuito de vibe coding para la tribu

**Branch**: `main` (sin rama de feature) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-curso-vibe-coding/spec.md`

## Summary

Un curso gratis y siempre abierto que lleva a gente que nunca programó de lo que imagina a una
página propia publicada con link. Tiene dos piezas:

1. **La puerta** (web, módulos 1 a 3): inscripción con código por mail, audios de Andrés, un tutor
   con voz que enseña cómo piensa un vibe coder, entrevista la idea hasta dejarla en una página y
   acompaña la instalación con capturas. Parte del backend de un proyecto anterior del autor
   (FastAPI en Python) pasado de un usuario a muchos alumnos, con avance y costo por alumno, y un
   frontend nuevo pensado primero para el celular.
2. **El kit** (módulos 4 a 7): una carpeta que se arma para cada alumno con su idea adentro. Abierta
   en Claude Code o en Codex, la propia herramienta hace de tutor y el alumno construye y publica
   con su plan (que puede ser el gratis de ChatGPT).

El contenido (guías, lecciones, machete con fechas, mails, audios) vive versionado en el repo y se
actualiza con aprobación de Andrés. El trabajo arranca por tres pruebas de viabilidad y sigue con
el contenido, el kit (probado por 5 personas en octubre), la puerta y el lanzamiento en noviembre.

## Technical Context

**Language/Version**: Python 3.12 (backend, fork de un proyecto anterior del autor); TypeScript 5 con React 19 y
Vite (frontend nuevo); Markdown y HTML estático (contenido y kit).

**Primary Dependencies**: backend: FastAPI, uvicorn, anthropic (SDK de Python ≥ 1.8), httpx,
PyJWT, pydantic-settings, python-multipart, jsonschema, PyYAML (heredadas del proyecto anterior
salvo PyYAML). Frontend: React 19, React Router, Vite, Tailwind 4,
react-markdown, vite-plugin-pwa. Servicios: Claude Sonnet 5 (tutor), Gemini (voz), Resend (mails),
Cloudflare Turnstile (anti-bots), Netlify y la página pública de Claude (publicación de los
alumnos). Detalle y alternativas en [research.md](research.md).

**Storage**: SQLite en modo WAL (`/srv/vibe-tutor/data/vibe.db`), migraciones por
`PRAGMA user_version` como en el proyecto anterior. Contenido en archivos versionados (`contenido/`). Ver
[data-model.md](data-model.md).

**Testing**: pytest + pytest-asyncio + respx (backend, heredado del proyecto anterior, con marca `real` para
llamadas pagas que se corren a mano); vitest + Testing Library (frontend); tests de contenido
(esquema del machete, estructura y tamaño del kit); validación del kit con sesiones reales en las
dos herramientas según [quickstart.md](quickstart.md). CI en GitHub Actions en cada PR.

**Target Platform**: VPS Linux (Ubuntu) con systemd, nginx y certbot, igual que el proyecto
anterior. Clientes: navegadores de celular (Safari iOS, Chrome Android) y de escritorio. El kit corre
en la app de escritorio de Claude y en la de ChatGPT (modo Codex), en Mac y Windows.

**Project Type**: aplicación web (backend + frontend) más un paquete de contenido descargable (kit).

**Performance Goals**: primer texto del tutor en menos de 3 s (mediana); transcripción de un audio
de 30 s en menos de 5 s; la landing carga en menos de 3 s en 4G; el kit se arma en menos de 2 s.

**Constraints**: costo promedio del tutor ≤ US$0,50 por alumno, con topes de US$1 por alumno y
US$50 por mes (aviso al 80%); las capturas nunca se guardan; los módulos 1 y 2 funcionan en el
celular; los secretos viven solo en `/etc/vibe-tutor/.env`; el despliegue no toca ningún otro
servicio del servidor; las instrucciones del kit entran holgadas en el límite de 32 KiB de Codex.

**Scale/Scope**: 200 a 300 inscripciones por mes al principio, menos de 20 conversaciones
simultáneas, 7 módulos (3 en la web, 4 en el kit), 5 historias
de usuario, 33 requisitos funcionales.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cómo lo cumple este plan | Estado |
|---|---|---|
| I. En el eje de la marca | Prompt base en voseo y sin emojis; el tutor no dice ser Andrés y usa una voz de síntesis distinta; toda lección trabaja sobre `mi-idea.md`; protocolo de malestar con recursos verificados de Argentina (research §15) | Cumple |
| II. Costo por alumno casi cero | Sonnet 5 con esfuerzo bajo y caché; tope por alumno y por mes chequeado antes de cada turno; guía escrita al llegar al tope; los módulos 4 a 7 corren en el plan del alumno | Cumple |
| III. Datos mínimos y del alumno | Tablas limitadas a lo que pide el spec; capturas solo en la llamada en curso; nada se copia fuera del sistema del curso; exportar y borrar; exportación a la lista de novedades solo con consentimiento; consentimiento expreso de transferencia internacional y aviso de privacidad según la Ley 25.326 (research §16) | Cumple |
| IV. Contenido fechado y verificado | `machete.yaml` con fuente, fecha y `probado`; test que impide "gratis" sin prueba; revisión mensual que abre un PR; publicar = aprobar el PR | Cumple |
| V. La compu del alumno es sagrada | Reglas de seguridad en `AGENTS.md`; `.claude/settings.json` endurece los permisos de Claude (nunca los afloja); `versiones/` como red de seguridad; la prueba V2 mide que la herramienta pide permiso y no sale de la carpeta (research §13 bis) | Cumple |
| VI. Tests primero y simplicidad | TDD en el backend reutilizando los tests del proyecto anterior; kit validado en las dos herramientas; fork en vez de plataforma; sin skills ni compactación en esta versión | Cumple |
| Restricciones técnicas | Repo público (código MIT, contenido CC BY 4.0, kit CC0), sin secretos, datos de alumnos ni audios; `.env.example` sin valores; usuario, puerto y servicio propios en el servidor; kit con una sola fuente de instrucciones; modelos elegidos con costo estimado; ningún `gemini-2.0-flash` | Cumple |
| Flujo y aprobaciones | Pruebas de viabilidad antes de escribir el curso; piloto de 5 personas antes de lanzar; regla de los 30 días; Andrés aprueba spec, plan y contenido | Cumple |

**Re-check después del diseño (Phase 1)**: sin violaciones. La tabla de complejidad queda vacía.

## Project Structure

### Documentation (this feature)

```text
specs/001-curso-vibe-coding/
├── plan.md              # Este archivo
├── research.md          # Phase 0: decisiones y datos verificados
├── data-model.md        # Phase 1: entidades y reglas
├── quickstart.md        # Phase 1: cómo validar de punta a punta
├── contracts/
│   ├── api.md           # API de la puerta
│   ├── kit.md           # Estructura y reglas del kit
│   └── mails.md         # Mails del curso
├── checklists/
│   └── requirements.md  # Control de calidad del spec
└── tasks.md             # Phase 2 (/speckit-tasks; no lo crea este plan)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml
├── vibe_tutor/
│   ├── main.py            # app FastAPI y tarea periódica (del proyecto anterior)
│   ├── config.py          # variables de /etc/vibe-tutor/.env (del proyecto anterior)
│   ├── db.py              # conexión y migraciones (del proyecto anterior; esquema nuevo de data-model.md)
│   ├── auth.py            # código por mail abierto a todos + Turnstile + límites por IP (del proyecto anterior)
│   ├── costos.py          # precios y topes por alumno y por mes (del proyecto anterior)
│   ├── voz.py             # transcripción y voz del tutor con Gemini (del proyecto anterior)
│   ├── tutor.py           # ciclo del tutor por alumno y módulo, con capturas (del proyecto anterior)
│   ├── prompts.py         # prompt base + guía del módulo + estado del alumno (nuevo)
│   ├── herramientas.py    # guardar_idea, marcar_avance, consultar_machete (nuevo)
│   ├── contenido.py       # lee contenido/ y valida machete.yaml (nuevo)
│   ├── kit.py             # arma el zip personalizado; también por línea de comandos (nuevo)
│   ├── mails.py           # mails del curso, baja firmada (nuevo)
│   ├── tareas.py          # recordatorios, aviso del 80%, reintentos, retención (nuevo)
│   ├── alumnos.py         # /yo, idea, taller, kit, links, mis-datos, baja (nuevo)
│   ├── admin.py           # reporte y CSV de novedades (nuevo)
│   └── api.py             # sesiones y turnos con SSE (del proyecto anterior)
└── tests/                 # pytest: contratos de la API, tutor con cliente falso, costos, kit, contenido

frontend/
├── package.json
├── vite.config.ts
├── index.html
├── src/
│   ├── paginas/           # Landing, Entrar, Inicio, Modulo, MiIdea, Taller, Mostrar, MisDatos,
│   │                      # Galeria, Privacidad, Baja, Admin
│   ├── componentes/       # Chat (SSE), Microfono, Reproductor, SubirCaptura, AvisoTope
│   └── lib/api.ts         # cliente de la API
└── tests/                 # vitest + Testing Library

contenido/
├── prompts/base.md        # persona del tutor, reglas, protocolo de malestar
├── web/                   # modulo-1..3.md (guía para el tutor) y guia-modulo-1..3.md (guía escrita)
├── kit/                   # plantilla del kit (ver contracts/kit.md)
├── machete.yaml           # datos que se vencen, con fuente y fecha
├── mails/                 # textos de los mails
├── legal/                 # privacidad y textos de consentimiento, con versión
└── audios/                # modulo-1..7.mp3 y sus transcripciones .md (no se versionan)

deploy/
├── desplegar.sh                     # build del frontend, rsync al VPS, tests de humo
├── preparar-servidor.sh             # preparación única del servidor (usuario, carpetas, nginx, certbot)
├── vibe-tutor.service               # systemd
├── contenido-pull.service           # actualiza contenido/ desde GitHub (clave de solo lectura; T082)
├── contenido-pull.timer
├── nginx-vibe-tutor.conf.plantilla  # sitio de nginx, con __DOMINIO__
├── nginx-vibe-tutor-cabeceras.conf  # cabeceras de seguridad
├── despliegue.env.example           # VIBE_SERVIDOR y VIBE_DOMINIO (despliegue.env no se versiona)
└── .env.example                     # nombres de variables, sin valores

.github/workflows/tests.yml         # pytest, vitest y tests de contenido en cada PR
.claude/skills/revisar-machete/     # instrucciones de la revisión mensual del machete
```

**Structure Decision**: aplicación web en dos proyectos (`backend/` y `frontend/`) más `contenido/`
como carpeta de datos versionados que leen el backend y el armado del kit, y `deploy/` con todo lo
del servidor. El backend conserva la forma del proyecto anterior para reutilizar su código y sus
tests.

## Complexity Tracking

Sin violaciones de la constitución.
