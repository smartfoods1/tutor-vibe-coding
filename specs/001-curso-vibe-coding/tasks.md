---

description: "Lista de tareas del curso gratuito de vibe coding para la tribu"
---

# Tasks: Curso gratuito de vibe coding para la tribu

**Input**: Design documents from `specs/001-curso-vibe-coding/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: por la Constitución VI, todo cambio del backend se escribe con tests primero (tienen que
fallar antes de implementar). Los cambios del kit se validan con sesiones reales en Claude Code y
en Codex. El frontend lleva tests de sus piezas con lógica (SSE, formulario, captura).

**Organization**: las tareas van agrupadas por historia de usuario, en el orden de prioridad del
spec, para que cada una se pueda terminar y probar por separado.

**Tareas de Andrés**: las marcadas "(Andrés)" las hace él; las que tocan servicios externos o el
VPS se ejecutan recién con su OK en ese momento.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia del spec a la que pertenece (US1 a US5)

## Path Conventions

Aplicación web según [plan.md](plan.md): `backend/vibe_tutor/`, `backend/tests/`,
`frontend/src/`, `frontend/tests/`, más `contenido/` y `deploy/` en la raíz del repo.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: estructura del repo y fork del proyecto anterior andando

- [X] T001 Crear la estructura de carpetas del plan (`backend/`, `frontend/`, `contenido/{prompts,web,kit,mails,legal,audios,ejemplos,investigacion}`, `deploy/`, `.github/workflows/`) y explicar qué va en cada una en `contenido/README.md`
- [X] T002 Copiar el backend de un proyecto anterior del autor a `backend/`, renombrar el paquete a `vibe_tutor` y ajustar `backend/pyproject.toml` (nombre `vibe-tutor`, sin las dependencias exclusivas de ese proyecto, con `PyYAML`)
- [X] T003 Quitar del fork lo exclusivo del proyecto anterior y dejar `pytest` en verde en `backend/`. Nota del 28/9: `tutor.py`, `api.py`, `prompts.py` y `herramientas.py` dependían de eso, así que también salieron con sus tests; vuelven en la fase 4 (T043 a T046) adaptados desde el backend del proyecto anterior, con tests primero. Queda andando: login, costos, base, voz y `main.py` mínimo (78 tests)
- [X] T004 [P] Crear el frontend con Vite, React 19, TypeScript, Tailwind 4, vite-plugin-pwa y vitest en `frontend/` (`package.json`, `vite.config.ts`, `index.html`, `src/main.tsx`) con un test de humo en `frontend/tests/humo.test.tsx`
- [X] T005 [P] Escribir `deploy/.env.example` con los nombres de todas las variables (claves de Anthropic, Gemini, Resend y Turnstile, `MAIL_FROM`, `JWT_SECRET`, `ADMIN_EMAIL`, `TOPE_ALUMNO_USD`, `TOPE_MENSUAL_USD`, `DATA_DIR`, `CONTENIDO_DIR`, `DOMINIO`), sin valores
- [X] T006 [P] Crear el CI en `.github/workflows/tests.yml`: `pytest` del backend (sin la marca `real`), `npm test` del frontend y los tests de contenido, en cada PR y en cada push a `main`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: pruebas de viabilidad, base del backend y currículo. Bloquea todas las historias.

**CRITICAL**: no se escribe ninguna lección ni módulo hasta pasar T012 y T023.

### Pruebas de viabilidad (quickstart §0)

- [X] T007 Armar el kit mínimo de prueba a mano en `contenido/ejemplos/kit-minimo/` según [contracts/kit.md](contracts/kit.md): `AGENTS.md`, `CLAUDE.md` con `@AGENTS.md` y `@bitacora.md`, `bitacora.md`, `cuaderno.md`, `mi-idea.md` de ejemplo, un borrador de la lección 4, las tres skills en `.claude/skills/` y `.agents/skills/`, `.claude/settings.json` y `sitio/index.html`
- [ ] T008 Prueba V2 en Claude Code (app de escritorio, Pro): guion de 10 turnos del quickstart en dos variantes (solo `AGENTS.md`; `AGENTS.md` más un estilo de salida propio), más el modo de permisos con que arranca, la carga de `@AGENTS.md` y `@bitacora.md` y si `/rewind` funciona; resultados en `specs/001-curso-vibe-coding/viabilidad.md`
- [ ] T009 Prueba V2 en Codex (app de ChatGPT, modo Codex): guion de 10 turnos, si pide confianza en la carpeta, si carga `AGENTS.md` y `.agents/skills`, y si lee `bitacora.md` solo con la instrucción; resultados en `specs/001-curso-vibe-coding/viabilidad.md`
- [ ] T010 Prueba V1 (Andrés crea una cuenta gratis nueva de ChatGPT): lección 4 completa con el kit mínimo en la app de escritorio; cuántos pedidos entran antes del límite y cuándo se renueva; si hay skills y vista previa de HTML en el plan gratis; resultados en `specs/001-curso-vibe-coding/viabilidad.md`
- [ ] T011 Prueba V3 en Mac y en Windows sin nada instalado, con una persona que no programa (Andrés consigue a quien tenga Windows): publicar con Netlify Drop y con la página pública de Claude siguiendo solo instrucciones escritas, abrir cada link en incógnito sin cuenta, y descomprimir el zip con el Explorador de Windows; resultados en `specs/001-curso-vibe-coding/viabilidad.md`
- [ ] T012 Decidir con V1 a V3 y registrar la decisión fechada en `specs/001-curso-vibe-coding/viabilidad.md`; si algo falla, actualizar antes de seguir `spec.md`, `research.md` (§11 a §13 bis) y `contracts/kit.md`

### Base del backend

- [X] T013 [P] Tests del esquema en `backend/tests/test_db.py`: la migración crea todas las tablas de [data-model.md](data-model.md), con claves foráneas activas, CASCADE y SET NULL al borrar un alumno
- [X] T014 Implementar el esquema de data-model.md en `backend/vibe_tutor/db.py` (migración nueva y `PRAGMA foreign_keys = ON` en `conectar`)
- [X] T015 [P] Tests en `backend/tests/test_costos.py`: precios de `claude-sonnet-5`, `gemini-2.5-flash` y `gemini-3.8-flash-tts` (con el aumento desde el 1/1/2027), gasto por alumno, gasto del mes en hora de Argentina y estado del tope por alumno y por mes
- [X] T016 Adaptar `backend/vibe_tutor/costos.py`: tabla de precios con fecha de vigencia, `registrar` con `alumno_id` y `estado_tope` por alumno y por mes (research §5 y §10)
- [X] T017 [P] Tests en `backend/tests/test_config.py` y adaptar `backend/vibe_tutor/config.py` a las variables de `deploy/.env.example` (archivo en `VIBE_ENV_FILE`, modelo `claude-sonnet-5`, topes de US$1 y US$50)
- [X] T018 [P] Tests de contenido en `backend/tests/test_contenido.py`: esquema de `machete.yaml` (ids únicos, fuente `https://`, fecha válida y no futura, nada que diga "gratis" con `probado: false`) y lectura de guías y lecciones desde disco en cada pedido
- [X] T019 Implementar `backend/vibe_tutor/contenido.py`: carga de `contenido/`, validación del machete, filtro por herramienta y sistema, y fecha de verificación más vieja
- [X] T020 Cargar `contenido/machete.yaml` con los datos verificados de research.md (planes, instalación, publicación, límites y las líneas de ayuda de §15), con fuente, fecha y `probado` según `viabilidad.md`

### Currículo (el método del proyecto anterior)

- [X] T021 Investigación en paralelo para el currículo, un informe con fuentes por tema en `contenido/investigacion/`: cómo aprende a construir con IA un adulto que nunca programó y dónde se traba; cómo piensa un vibe coder según fuentes primarias; miedo a la tecnología y aprendizaje en adultos de 30 a 60 años; qué enseñan los cursos del panorama (investigación de producto del 27/9, en las notas del autor, no incluidas)
- [X] T022 Fact-check adversarial de los informes de T021 y escritura del mapa del curso en `contenido/curriculo.md`. Nota del 28/9: el fact-check adversarial se hizo dentro de T021 (dos verificadores por afirmación, crítico de completitud y anexo `contenido/investigacion/05-anexo-huecos-y-contradicciones.md`). El mapa quedó escrito el 28/9 con tres borradores, tres jueces, una síntesis y dos revisiones adversariales (evidencia, y spec más constitución). Los módulos 3, 4 y 7 y la portada siguen en borrador hasta V1 a V3. La sección "Decisiones de Andrés" lista 14 tensiones con el spec y los contratos que no se aplicaron: esperan a T023
- [ ] T023 (Andrés) Aprobar `contenido/curriculo.md` y dejar la fecha de aprobación en el archivo
- [ ] T024 [P] Escribir el prompt base del tutor en `contenido/prompts/base.md` (persona, voseo, no es Andrés, un paso por vez, alcance de una página, protocolo de malestar de research §15, lo pegado son datos) y los casos de prueba del tutor de la web en `backend/tests/fixtures/guion_puerta.yaml`. Nota del 28/9: el prompt base quedó escrito como borrador pendiente de aprobación (T023); falta el fixture

**Checkpoint**: viabilidad decidida, base del backend en verde y currículo aprobado.

---

## Phase 3: User Story 1 - Construir y publicar su idea con el kit (Priority: P1) - MVP

**Goal**: una persona sin experiencia abre el kit en Codex o en Claude Code y termina con su idea
publicada con un link, sin más ayuda que el curso.

**Independent Test**: quickstart §2 con kits armados por línea de comandos y el piloto del kit
(SC-001, SC-002, SC-006).

### Tests for User Story 1

> Escribir primero y verificar que fallen.

- [X] T025 [P] [US1] Tests del armado en `backend/tests/test_kit.py`: archivos obligatorios de contracts/kit.md, `mi-idea.md` del alumno, skills idénticas en `.claude/` y `.agents/` y sin enlaces simbólicos, frontmatter solo con `name` y `description`, `AGENTS.md` de menos de 8 KiB y 200 líneas, machete filtrado con su fecha en `curso/VERSION`, nombres sin acentos ni espacios

### Implementation for User Story 1

- [X] T026 [P] [US1] Escribir `contenido/kit/AGENTS.md` con los 10 puntos de contracts/kit.md y lo aprendido en `viabilidad.md`
- [X] T027 [P] [US1] Escribir `contenido/kit/CLAUDE.md`, `contenido/kit/.claude/settings.json` (permisos de contracts/kit.md) y las plantillas `contenido/kit/bitacora.md`, `contenido/kit/cuaderno.md` y `contenido/kit/sitio/index.html`
- [X] T028 [P] [US1] Escribir las skills `guardar-version`, `volver-version` y `publicar` en `contenido/kit/skills/<nombre>/SKILL.md` (fuente única; el armado las copia a las dos carpetas)
- [X] T029 [P] [US1] Escribir `contenido/kit/LEEME-codex.txt` y `contenido/kit/LEEME-claude.txt`: cómo abrir la carpeta en cada app, en Mac y en Windows, y qué contestar si la app pide confianza
- [X] T030 [US1] Escribir las lecciones `contenido/kit/curso/leccion-4-primera-victoria.md`, `leccion-5-construir.md`, `leccion-6-cuando-se-rompe.md` y `leccion-7-terminar-y-mostrar.md` según `contenido/curriculo.md`, con la línea opcional "Hecho en [curso]" (`?ref=hecho-en`) y el paso de registrar el link
- [X] T031 [US1] Implementar `backend/vibe_tutor/kit.py`: armado del zip en memoria desde `contenido/kit/`, personalización (idea, herramienta, sistema, LEEME, machete filtrado, `VERSION`) y la línea de comandos `python -m vibe_tutor.kit --idea --herramienta --sistema --salida`
- [ ] T032 [US1] Escribir la plantilla `contenido/ejemplos/plantilla-idea.md` y dos ideas de ejemplo en `contenido/ejemplos/`; validar el kit armado con el guion de 10 turnos en Claude Code y en Codex (9 de 10 o más en cada una) y anotarlo en `specs/001-curso-vibe-coding/viabilidad.md`
- [ ] T033 [P] [US1] Escribir los puntos a cubrir de los audios 4 a 7 en `contenido/audios/guion-modulo-4.md` a `guion-modulo-7.md`; (Andrés) grabarlos como `contenido/audios/modulo-4.mp3` a `modulo-7.mp3`; transcribirlos a `contenido/audios/modulo-4.md` a `modulo-7.md` para que Andrés los revise
- [ ] T034 [US1] (Andrés) Aprobar `contenido/kit/AGENTS.md` y las lecciones 4 a 7, con la fecha en cada archivo
- [ ] T035 [US1] Piloto del kit en octubre: (Andrés) 5 personas de la tribu, con Mac y Windows y con Codex gratis y Claude Pro, escriben su idea con `contenido/ejemplos/plantilla-idea.md`; se les arma el kit por línea de comandos y hacen los módulos 4 a 7; medir SC-001, SC-002 y SC-006 y anotar dónde se trabaron en `specs/001-curso-vibe-coding/piloto.md`
- [ ] T036 [US1] Ajustar el kit, las lecciones y el machete con lo aprendido en el piloto y volver a correr `backend/tests/test_kit.py`

**Checkpoint**: el kit funciona solo, en las dos herramientas; ya se puede usar a mano con alumnos.

---

## Phase 4: User Story 2 - Pasar la puerta (Priority: P2)

**Goal**: desde el celular, inscribirse, entender cómo piensa un vibe coder y dejar la idea en
una página.

**Independent Test**: quickstart §3 (SC-003).

### Tests for User Story 2

- [X] T037 [P] [US2] Tests de inscripción en `backend/tests/test_auth.py`: cualquier mail recibe código; Turnstile inválido da `400` (con respx); los límites por mail y por IP responden `200` sin enviar; faltan `mails_curso` o `transferencia` da `422`; los consentimientos se aplican recién al verificar; verificar crea al alumno, registra `inscripcion` y encola una sola bienvenida; cookie `vibe_sesion` con el id; `ADMIN_EMAIL` es admin
- [X] T038 [P] [US2] Tests de API en `backend/tests/test_api.py`: `/yo`, `/modulos/{n}/guia`, `/modulos/{n}/sesion` (solo el módulo actual o uno anterior), `/sesiones/{id}` (solo el dueño), `/modulos/{n}/completar` e `/idea` (GET, PUT que versiona, descarga)
- [X] T039 [P] [US2] Tests del tutor con cliente falso en `backend/tests/test_tutor.py`: prompt en dos bloques con caché y el estado del alumno en el primer mensaje; esfuerzo `low`, y `medium` al guardar o cerrar; tope chequeado antes de cada turno (evento `tope`); herramientas `guardar_idea` y `marcar_avance` (eventos `idea` y `avance`); `refusal` con mensaje amable; costo sumado al alumno; casos de `backend/tests/fixtures/guion_puerta.yaml`
- [X] T040 [P] [US2] Tests de voz en `backend/tests/test_voz.py`: costo con los precios nuevos y con `alumno_id`, y `402` con el tope alcanzado

### Implementation for User Story 2

- [X] T041 [US2] Adaptar `backend/vibe_tutor/auth.py`: alta abierta, Turnstile con `siteverify` (chequea `hostname` y `action`), límite por IP, consentimientos pendientes en `codigos.pendiente_json`, alta del alumno al verificar y admin por `ADMIN_EMAIL`
- [X] T042 [US2] Implementar `backend/vibe_tutor/mails.py`: envío por Resend con httpx, cabeceras de baja de RFC 8058, token de baja firmado, registro en `mails` con `clave` única y el mail de bienvenida ([contracts/mails.md](contracts/mails.md))
- [X] T043 [P] [US2] Implementar `backend/vibe_tutor/prompts.py`: bloque base y guía del módulo con caché; estado del alumno (idea vigente, resumen del módulo anterior, herramienta y sistema) después del punto de caché
- [X] T044 [P] [US2] Implementar `guardar_idea` (versiona `ideas`, con límites de largo) y `marcar_avance` (resumen sin datos personales ni de salud, sube `modulo_actual`, evento `modulo_completo`) en `backend/vibe_tutor/herramientas.py`
- [X] T045 [US2] Traer y adaptar `backend/vibe_tutor/tutor.py` desde el backend del proyecto anterior, con sus tests: sesión por alumno y módulo, `claude-sonnet-5` con pensamiento adaptativo y esfuerzo `low` o `medium`, sin betas de respaldo ni compactación, topes antes de cada turno, costo por alumno y eventos `idea`, `avance` y `tope`
- [X] T046 [US2] Implementar `backend/vibe_tutor/alumnos.py` (`/yo`, `/modulos/{n}/guia`, `/modulos/{n}/completar`, `/idea`, `/idea.md`, `/consentimientos`) y traer y adaptar `backend/vibe_tutor/api.py` desde el backend del proyecto anterior (sesiones por módulo y turno con SSE) según [contracts/api.md](contracts/api.md)
- [X] T047 [US2] Adaptar `backend/vibe_tutor/voz.py`: prompt de transcripción del curso, pensamiento apagado, `gemini-3.8-flash-tts` con una voz distinta de la de Andrés, costo por alumno y `402` con el tope alcanzado
- [X] T048 [P] [US2] Escribir `contenido/web/modulo-1.md` y `contenido/web/modulo-2.md` (guías para el tutor, según el currículo) y `contenido/web/guia-modulo-1.md` y `contenido/web/guia-modulo-2.md` (guías escritas, con la plantilla de la idea)
- [X] T049 [P] [US2] Escribir `contenido/legal/privacidad.md` y `contenido/legal/consentimientos.md` a partir del borrador de research §16, con el responsable y el domicilio que defina Andrés
- [X] T050 [P] [US2] Escribir `contenido/mails/bienvenida.md` y el pie legal `contenido/legal/pie-mails.md`
- [X] T051 [US2] Implementar `frontend/src/lib/api.ts` (cliente de la API y lector de SSE), con tests en `frontend/tests/api.test.ts`
- [X] T052 [US2] Implementar las páginas `Landing` (lee `?ref=`, Turnstile, consentimientos separados), `Entrar`, `Inicio` y `Privacidad` en `frontend/src/paginas/`, con tests del formulario en `frontend/tests/landing.test.tsx`
- [X] T053 [US2] Implementar la página `Modulo` y los componentes `Chat` (SSE), `Microfono` (dictado), `Reproductor` (audio de Andrés con transcripción; la voz del tutor viene apagada) y `AvisoTope` (pasa a la guía escrita) en `frontend/src/`
- [X] T054 [US2] Implementar la página `MiIdea` (ver, editar, descargar) en `frontend/src/paginas/MiIdea.tsx`
- [ ] T055 [P] [US2] Escribir los puntos a cubrir de los audios 1 y 2 en `contenido/audios/guion-modulo-1.md` y `guion-modulo-2.md`; (Andrés) grabarlos; transcribirlos a `contenido/audios/modulo-1.md` y `modulo-2.md` para su revisión
- [ ] T056 [US2] Validar la historia 2 con el quickstart §3 desde un celular y anotar el tiempo de los módulos 1 y 2 (SC-003) en `specs/001-curso-vibe-coding/piloto.md`

**Checkpoint**: la puerta inscribe y entrega la idea en una página, sin depender del kit.

---

## Phase 5: User Story 3 - Armar su taller con ayuda (Priority: P3)

**Goal**: elegir herramienta, instalar con el tutor al lado y bajar el kit personalizado.

**Independent Test**: quickstart §4 en una computadora limpia.

### Tests for User Story 3

- [X] T057 [P] [US3] Tests del turno con imagen en `backend/tests/test_tutor.py`: la imagen viaja solo en la llamada y en la base queda "[captura de pantalla enviada]"; formatos y tamaño máximo; `consultar_machete` filtra por herramienta y sistema
- [X] T058 [P] [US3] Tests de `/taller` y `/kit` en `backend/tests/test_api.py`: `409` sin idea o sin taller; `otro` no habilita el kit; la descarga registra `kits` y el evento `kit`, y sube al módulo 4
- [X] T059 [P] [US3] Tests del recordatorio en `backend/tests/test_tareas.py`: idea sin kit a los 3 días da un solo recordatorio en la vida del alumno y respeta la baja

### Implementation for User Story 3

- [X] T060 [US3] Turno con imagen (multipart) en `backend/vibe_tutor/api.py` y `backend/vibe_tutor/tutor.py`: base64 solo en la llamada en curso y el marcador de texto en la base
- [X] T061 [US3] Herramienta `consultar_machete` y registro del taller (herramienta y sistema) en `backend/vibe_tutor/herramientas.py`
- [X] T062 [US3] Endpoints `/taller` y `/kit` en `backend/vibe_tutor/alumnos.py`, usando `backend/vibe_tutor/kit.py`
- [X] T063 [US3] Implementar `backend/vibe_tutor/tareas.py` con la tarea periódica (cada 15 minutos) y el recordatorio, y arrancarla en `backend/vibe_tutor/main.py` en lugar de la tarea periódica del proyecto anterior
- [X] T064 [P] [US3] Escribir `contenido/web/modulo-3.md`, `contenido/web/guia-modulo-3.md` y `contenido/mails/recordatorio.md`
- [X] T065 [US3] Implementar la página `Taller` con el componente `SubirCaptura` (achica a 1.440 px con canvas; test en `frontend/tests/captura.test.ts`) y la descarga del kit con el LEEME de la herramienta elegida en `frontend/src/paginas/Taller.tsx`
- [ ] T066 [P] [US3] Escribir los puntos del audio 3 en `contenido/audios/guion-modulo-3.md`; (Andrés) grabarlo; transcribirlo a `contenido/audios/modulo-3.md`
- [ ] T067 [US3] Validar la historia 3 con el quickstart §4 en una computadora limpia y anotarlo en `specs/001-curso-vibe-coding/piloto.md`

**Checkpoint**: la puerta lleva de la idea al kit instalado sin intervención de Andrés.

---

## Phase 6: User Story 4 - Mostrar lo que hizo (Priority: P4)

**Goal**: registrar el link, elegir si se muestra y difundir el curso con el trabajo de los
alumnos.

**Independent Test**: quickstart §5.

### Tests for User Story 4

- [X] T068 [P] [US4] Tests de `/links` y `/galeria` en `backend/tests/test_api.py`: `https://` obligatorio, las dos opciones desmarcadas por defecto, la galería muestra solo los links con `mostrar_galeria`, el alumno pasa al módulo 7, y el mail `contame` sale una vez por link y como mucho uno por día
- [X] T069 [P] [US4] Tests de la fuente en `backend/tests/test_auth.py`: `?ref=` viaja del formulario al código y queda en `alumnos.fuente` al verificar

### Implementation for User Story 4

- [X] T070 [US4] Endpoints `/links` y `/galeria` en `backend/vibe_tutor/alumnos.py` y el mail `contame` en `backend/vibe_tutor/mails.py`, con el texto en `contenido/mails/contame.md`
- [X] T071 [US4] Registrar la fuente de inscripción de punta a punta (landing, `POST /auth/codigo`, alta del alumno) en `backend/vibe_tutor/auth.py`
- [X] T072 [US4] Implementar las páginas `Mostrar` y `Galeria` en `frontend/src/paginas/`
- [ ] T073 [US4] Validar la historia 4 con el quickstart §5 y anotarlo en `specs/001-curso-vibe-coding/piloto.md`

**Checkpoint**: cada alumno que termina deja un link medible y, si quiere, difunde el curso.

---

## Phase 7: User Story 5 - Operar el curso sin estar encima (Priority: P5)

**Goal**: Andrés ve el embudo y el gasto, aprueba el machete y exporta la lista de novedades; los alumnos
controlan sus datos.

**Independent Test**: quickstart §6.

### Tests for User Story 5

- [X] T074 [P] [US5] Tests de `backend/tests/test_admin.py`: solo admin; reporte con el embudo total y de los últimos 30 días, por fuente, gasto del mes contra el tope, gasto promedio por alumno y datos del machete con más de 45 días; CSV de novedades con una sola columna y solo los que aceptaron
- [X] T075 [P] [US5] Tests de `backend/tests/test_tareas.py`: aviso del 80% una sola vez por mes; reintento de mails fallidos (hasta 3 en 24 horas); retención (sesión borrada 30 días después de su `fin`, sin terminar a los 12 meses de inactividad, códigos a las 24 horas)
- [X] T076 [P] [US5] Tests de `/mis-datos` y `/baja` en `backend/tests/test_api.py`: exportación completa; borrado en cascada con `uso` y `eventos` sin `alumno_id`; baja con token por GET y por POST (RFC 8058); token inválido da `400`

### Implementation for User Story 5

- [X] T077 [US5] Implementar `backend/vibe_tutor/admin.py` (reporte y CSV de novedades)
- [X] T078 [US5] Sumar a `backend/vibe_tutor/tareas.py` el aviso del 80%, los reintentos de mails, la retención y la purga de códigos
- [X] T079 [US5] Endpoints `/mis-datos` (GET y DELETE) y `/baja` en `backend/vibe_tutor/alumnos.py`
- [X] T080 [US5] Implementar las páginas `Admin`, `MisDatos` y `Baja` en `frontend/src/paginas/`
- [ ] T081 [US5] Escribir la skill de la revisión mensual en `.claude/skills/revisar-machete/SKILL.md` (compara cada dato con su fuente oficial y abre un PR con los cambios y las fuentes) y, con el OK de Andrés, programarla como rutina mensual
- [ ] T082 [US5] Escribir `deploy/contenido-pull.service` y `deploy/contenido-pull.timer` (cada 15 minutos, `git pull --ff-only` de `contenido/` con una clave de despliegue de solo lectura) y, con el OK de Andrés, crear la clave en GitHub
- [ ] T083 [US5] Validar la historia 5 con el quickstart §6 y anotarlo en `specs/001-curso-vibe-coding/piloto.md`

**Checkpoint**: el curso se opera en minutos por semana y el contenido se actualiza con un PR.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: despliegue, seguridad, costo real, piloto completo y lanzamiento

- [X] T084 Escribir `deploy/vibe-tutor.service`, la plantilla de nginx (`deploy/nginx-vibe-tutor.conf.plantilla`) y `deploy/desplegar.sh` (build del frontend, rsync, reinicio, chequeos de humo del quickstart §8 y comparación de servicios del servidor antes y después)
- [X] T085 Con el OK de Andrés, primer despliegue en el servidor de prueba, con un dominio provisorio y certbot, usuario `vibe-tutor` y `/etc/vibe-tutor/.env`; anotar los chequeos de humo en `specs/001-curso-vibe-coding/piloto.md`
- [ ] T086 [P] (Andrés) Crear el widget de Turnstile (dominio de prueba y definitivo) y verificar el subdominio remitente en Resend; registrar los nombres de variables usados en `deploy/.env.example`
- [X] T087 [P] Revisión de seguridad del login, la subida de imágenes, el SSE, el admin y la baja, con los hallazgos corregidos y anotados en `specs/001-curso-vibe-coding/seguridad.md`. Nota del 28/9: revisión adversarial con 3 lentes (seguridad, contrato, contenido) y un verificador por hallazgo: 18 confirmados y 14 menores, todos arreglados; el detalle quedó en las notas del autor (no incluidas)
- [ ] T088 Prueba de costo con el modelo real (`pytest -m real -k costo_modulos` en `backend/tests/test_costo_real.py`); si pasa de US$0,50 por alumno, ajustar esfuerzo, caché o voz y registrar la decisión en `research.md` §10
- [ ] T089 Piloto completo, módulos 1 a 7: (Andrés) 5 personas de la tribu; medir SC-001 a SC-006 y anotar resultados y ajustes en `specs/001-curso-vibe-coding/piloto.md`
- [ ] T090 (Andrés) Tareas de research §19: nombre del curso y registro DNS, responsable y domicilio para el aviso, inscripción en el Registro Nacional de Bases de Datos, revisión del abogado y Resend Pro; marcar cada una en `research.md` §19
- [ ] T091 Migrar al dominio definitivo: actualizar `VIBE_DOMINIO` en `deploy/despliegue.env` (la plantilla de nginx lo toma de ahí), certbot, Turnstile, el remitente de Resend y `DOMINIO` en `/etc/vibe-tutor/.env`, y repetir los chequeos de humo
- [ ] T092 Correr el quickstart completo en producción y anotar el resultado en `specs/001-curso-vibe-coding/piloto.md`
- [ ] T093 Plan de difusión del lanzamiento (fuera del repo)
- [ ] T094 Programar el chequeo de la regla de los 30 días con el reporte del admin y anotar su resultado fechado en `specs/001-curso-vibe-coding/piloto.md` y en las notas del autor
- [ ] T095 Publicar el repo como código abierto (`tutor-vibe-coding`, un solo commit sin historial): lo propio del autor pasa a configuración que no se versiona (`AUTOR_NOMBRE`, `NEWSLETTER_NOMBRE`, `MODO_DEMO`, `VITE_NOMBRE_CURSO`, `deploy/despliegue.env`); `contenido/` usa los marcadores `{{AUTOR}}` y `{{NEWSLETTER}}`; el consentimiento pasa a `novedades` (migración 3) y el CSV a `/api/admin/novedades.csv`; `/api/config` suma `autor_nombre`, `newsletter` y `modo_demo`; licencias MIT (código), CC BY 4.0 (contenido y diseño) y CC0 (kit y ejemplos); el material privado de los audios queda en las notas del autor. Constitución 1.0.3

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: arranca ya. T002 parte del backend de un proyecto anterior del autor.
- **Foundational (Phase 2)**: depende del Setup y bloquea todas las historias. Dentro de la fase,
  la viabilidad (T007 a T012) y la base del backend (T013 a T020) van en paralelo; el currículo
  (T021 a T023) espera a T012, porque la viabilidad puede cambiar el diseño del kit.
- **US1 (Phase 3)**: depende de la fase 2. Es el MVP y se prueba en octubre con kits armados por
  línea de comandos.
- **US2 (Phase 4)**: depende de la fase 2; puede avanzar en paralelo con US1 salvo el contenido,
  que comparte el currículo.
- **US3 (Phase 5)**: depende de US2 (inscripción, tutor, idea) y usa `kit.py` de US1.
- **US4 (Phase 6)**: depende de US2; toma el paso de registrar el link de la lección 7 (US1).
- **US5 (Phase 7)**: depende de US2; la revisión del machete (T081, T082) puede hacerse antes.
- **Polish (Phase 8)**: depende de las historias que entren al lanzamiento. T085 puede adelantarse
  después de US2 para probar en el celular con HTTPS.

### Within Each User Story

- Tests primero y en rojo; después modelos, servicios, endpoints, frontend y contenido.
- El contenido de cada historia (guías, lecciones, mails, audios) necesita el currículo aprobado
  (T023) y la aprobación de Andrés antes de publicarse.

### Parallel Opportunities

- Setup: T004, T005 y T006 en paralelo después de T001.
- Foundational: los tests T013, T015, T017 y T018 en paralelo; las pruebas V2 en las dos
  herramientas (T008, T009) en paralelo.
- US1: T026 a T029 en paralelo (archivos distintos del kit), mientras T025 queda en rojo.
- US2: los cuatro bloques de tests (T037 a T040) en paralelo; `prompts.py` y `herramientas.py`
  (T043, T044) en paralelo; el contenido (T048 a T050) en paralelo con el backend.

---

## Parallel Example: User Story 1

```bash
# Tests primero, en rojo:
Task: "Tests del armado en backend/tests/test_kit.py"

# Archivos del kit en paralelo:
Task: "Escribir contenido/kit/AGENTS.md"
Task: "Escribir contenido/kit/CLAUDE.md, .claude/settings.json y las plantillas"
Task: "Escribir las skills en contenido/kit/skills/"
Task: "Escribir contenido/kit/LEEME-codex.txt y LEEME-claude.txt"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Fases 1 y 2: fork andando, viabilidad decidida y currículo aprobado.
2. Fase 3: el kit completo, validado en las dos herramientas.
3. **STOP and VALIDATE**: piloto del kit con 5 personas en octubre (T035).
4. Con el kit validado, el curso ya puede darse a mano a grupos chicos mientras se construye la
   puerta.

### Incremental Delivery

1. Setup + Foundational → base lista.
2. US1 → piloto del kit (MVP).
3. US2 → la puerta inscribe y entrega la idea (se puede abrir con kits armados a mano).
4. US3 → la puerta lleva hasta el kit sin intervención.
5. US4 y US5 → medición, difusión y operación.
6. Fase 8 → despliegue definitivo, piloto completo y lanzamiento en noviembre.

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes.
- Cada tarea referencia la historia del spec para trazabilidad.
- Commit después de cada tarea o grupo lógico; nada se despliega ni se publica sin el OK de Andrés.
- Nada de datos que se vencen escritos de memoria: todo sale de `contenido/machete.yaml`.
