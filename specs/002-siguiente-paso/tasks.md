# Tasks: Siguiente paso al terminar el curso

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/api.md](contracts/api.md), [quickstart.md](quickstart.md) y [notas-para-el-plan.md](notas-para-el-plan.md).

**Tests**: primero el test, que tiene que fallar; después el código (principio VI).

Formato: `[P]` = se puede hacer en paralelo (otros archivos, sin depender de tareas pendientes); `[USn]` = historia del spec.

## Phase 1: Setup

- [x] T001 Enmienda del principio I, versión 1.1.0, en `.specify/memory/constitution.md` (aprobada por Andrés el 28/9/2026)
- [x] T002 Rama `002-siguiente-paso` y `.specify/feature.json` apuntando a `specs/002-siguiente-paso`

## Phase 2: Foundational (bloquea las historias)

- [x] T003 Tests de configuración en `backend/tests/test_config.py`: `SIGUIENTE_PASO` apagada por defecto, `hay_siguiente_paso` solo con la bandera y los tres textos, lista de claves faltantes, y las cuatro claves en `deploy/.env.example`
- [x] T004 Campos `siguiente_paso`, `siguiente_paso_nombre`, `siguiente_paso_pregunta` y `siguiente_paso_texto`, y las propiedades `hay_siguiente_paso` y `siguiente_paso_faltantes`, en `backend/vibe_tutor/config.py`
- [x] T005 [P] Las cuatro claves, vacías y con comentarios de ejemplo, en `deploy/.env.example`
- [x] T006 Tests de la migración 5 en `backend/tests/test_db.py`: columnas de `TABLAS`, misma base nueva y migrada, filas, ids y contador de `consentimientos` conservados, y el `CHECK` que acepta `siguiente_paso`
- [x] T007 Migración 5 en `backend/vibe_tutor/db.py` según [data-model.md](data-model.md)
- [x] T008 [P] Tests del marcador `{{SIGUIENTE_PASO}}` y del bloque `{{#SIGUIENTE_PASO}}` en `backend/tests/test_contenido.py`
- [x] T009 Marcador y bloque en `backend/vibe_tutor/contenido.py`
- [x] T010 [P] Test de `GET /config` con `siguiente_paso` (activa y `null`) en `backend/tests/test_main.py`
- [x] T011 `siguiente_paso` en `GET /config` de `backend/vibe_tutor/main.py`

## Phase 3: User Story 1 - Enterarse del siguiente paso al terminar (P1)

**Goal**: la pregunta después del primer link, el texto y la casilla, y el permiso guardado.

**Independent Test**: escenarios 1 a 5 de [quickstart.md](quickstart.md).

- [x] T012 [US1] Tests en `backend/tests/test_siguiente_paso.py` (nuevo): `pregunta_siguiente_paso` en `POST /links` (primer link, segundo link, función inactiva, ya contestó); `POST /siguiente-paso` con sus `409` y `422`, sus efectos (marca, total, permiso con versión) y el `403` de una sesión pendiente
- [x] T013 [US1] Ayudas del contador y de "ya contestó" en `backend/vibe_tutor/dominio.py`
- [x] T014 [US1] `pregunta_siguiente_paso` en `registrar_link` y la ruta `POST /siguiente-paso` en `backend/vibe_tutor/alumnos.py`
- [x] T015 [US1] Texto corto `siguiente_paso` y sección `{{#SIGUIENTE_PASO}}` en `contenido/legal/consentimientos.md` (versión `2026-09-30`); `siguiente_paso` en `TEXTOS_CONSENTIMIENTO` y ajuste de `backend/tests/test_alumnos.py` (textos legales)
- [x] T016 [P] [US1] Tipos y funciones en `frontend/src/lib/api.ts` y `siguientePaso` en `frontend/src/componentes/Configuracion.tsx`, con `frontend/tests/configuracion.test.ts` y `frontend/tests/api.test.ts`
- [x] T017 [US1] Tests de la pregunta en `frontend/tests/paginas.test.tsx` (describe `Mostrar`): aparece solo con `pregunta_siguiente_paso`; "Sí" con casilla desmarcada y sin precios; "No"; "Ahora no" sin llamadas; función inactiva
- [x] T018 [US1] La pregunta en la pantalla de link registrado de `frontend/src/paginas/Mostrar.tsx`

## Phase 4: User Story 2 - Manejar el aviso desde "Mis datos" (P2)

**Goal**: ver, pedir y sacar el aviso; descargarlo y borrarlo.

**Independent Test**: escenarios 6 y 8 de [quickstart.md](quickstart.md).

- [x] T019 [US2] Tests en `backend/tests/test_alumnos.py`: `siguiente_paso` en `GET /yo` y en `PUT /consentimientos` (`true` con la función inactiva da `409`; `false` siempre), y `siguiente_paso_respondido` en `GET /mis-datos`
- [x] T020 [US2] `siguiente_paso` en `TIPOS_CONSENTIMIENTO`, `CambioConsentimientos` y la descarga, en `backend/vibe_tutor/alumnos.py`
- [x] T021 [P] [US2] Bloques `{{#SIGUIENTE_PASO}}` en `contenido/legal/privacidad.md` (finalidades, datos, permisos opcionales, conservación y derechos; versión `2026-09-30`)
- [x] T022 [US2] Tests de la casilla en `frontend/tests/paginas.test.tsx` (describe `MisDatos`): visible con la función activa o con el aviso prendido; prender y sacar
- [x] T023 [US2] Casilla del aviso en `frontend/src/paginas/MisDatos.tsx`

## Phase 5: User Story 3 - Los números para el autor (P3)

**Goal**: los tres números y el aviso de textos faltantes en el reporte.

**Independent Test**: escenarios 2, 3, 6 y 7 de [quickstart.md](quickstart.md), mirando el reporte.

- [x] T024 [US3] Tests en `backend/tests/test_admin.py`: `siguiente_paso` con totales, avisos activos (sin retirados ni borrados) y `falta_configurar`
- [x] T025 [US3] `siguiente_paso` en `GET /admin/reporte` de `backend/vibe_tutor/admin.py`

## Phase 6: Polish

- [x] T026 [P] La función y sus claves en `docs/adaptar-el-curso.md`, `docs/desarrollo-local.md` y `docs/desplegar.md`, y en `deploy/preparar-servidor.sh` si lista claves opcionales
- [x] T027 Correr los tests del backend y del frontend completos, y los escenarios de [quickstart.md](quickstart.md) en modo demo (28/9: 737 del backend y 178 del frontend en verde, build del frontend OK; recorrido de punta a punta en el navegador con ancho de celular: pregunta después del primer link, "Sí" con casilla desmarcada, permiso guardado con versión 2026-09-30, casilla marcada en "Mis datos" y 1/1/1 en el reporte)
- [ ] T028 Andrés aprueba los tres textos de su instalación, los textos de la pantalla y los textos legales nuevos (siguen en borrador hasta su OK y la revisión de un abogado). Para el abogado: si la función se apaga después de usarse, los bloques del aviso de privacidad desaparecen pero los avisos guardados siguen
- [x] T029 Despliegue con la función apagada, con OK de Andrés y un respaldo de la base antes de la migración 5 (28/9: commit 6d12998; respaldo `/srv/vibe-tutor/data/vibe-antes-migracion-5.db`; base en la versión 5 con integridad ok y los mismos datos; `siguiente_paso` en `null`)
- [ ] T030 Prender la función para el lanzamiento del curso gratis, con OK de Andrés

## Dependencies

- Phase 2 bloquea todo lo demás. Dentro de cada historia, el test va antes que el código.
- US2 y US3 dependen del permiso y del contador de US1 (migración 5 y T013), no de sus pantallas.
- Backend y frontend se pueden hacer en paralelo con el contrato de [contracts/api.md](contracts/api.md).
