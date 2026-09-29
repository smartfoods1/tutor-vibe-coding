# Notas para el plan: dónde se engancha el siguiente paso (28/9/2026)

Relevamiento del código hecho antes del plan, para no repetirlo. Los números de línea son del 28/9/2026 y pueden correrse.

## Registro de links

- `backend/vibe_tutor/alumnos.py`, `registrar_link` (`POST /api/links`, :468-496): exige `modulo_actual >= 4`, tope de 5 links, registra el evento `link`, sube al módulo 7 y decide el mail "contame". No existe un "link final": cualquier registro lleva al 7.
- El "primer link" se puede deducir de los eventos `link` del alumno, que no se borran al borrar un link.
- Frontend: `frontend/src/paginas/Mostrar.tsx`, pantalla `listo` (:51-81), el lugar natural para la pregunta. Cliente: `registrarLink` en `frontend/src/lib/api.ts` (:547).
- La lección 7 (`contenido/kit/curso/leccion-7-terminar-y-mostrar.md`, paso 10) manda a registrar el link; la lección 4 no tiene paso de registro.

## Permisos y "Mis datos"

- Tabla `consentimientos` (`backend/vibe_tutor/db.py`:22-30, recreada en la migración 3, :156-173): historial que solo suma filas; vale la última por tipo. El `CHECK` de `tipo` obliga a una migración que recree la tabla (como la 3) para sumar un tipo nuevo.
- Ayudas: `dominio.consentimiento` y `dominio.agregar_consentimiento` (`dominio.py`:57-72).
- `PUT /api/consentimientos` (`alumnos.py`:547-566) con `TIPOS_CONSENTIMIENTO` (:38); `GET` y `DELETE /api/mis-datos` (:569-631).
- Frontend: `frontend/src/paginas/MisDatos.tsx`; `CasillaNovedades` (:202-224) es el modelo para la casilla nueva.
- `eventos.tipo` también tiene `CHECK` (`db.py`:204): contar las respuestas de forma anónima necesita tipos nuevos y otra migración. La última migración es la 4 (`db.py`:174-215).

## Configuración

- `backend/vibe_tutor/config.py`, `Settings` (:13-77). Precedente de función apagada por defecto: `aprobacion_manual` (:52).
- `GET /api/config` en `backend/vibe_tutor/main.py` (:58-68); en el frontend, `frontend/src/componentes/Configuracion.tsx`.
- `deploy/.env.example`: `backend/tests/test_config.py` (:153-175) exige que cada campo aparezca sin comentar y vacío. También listan claves `deploy/preparar-servidor.sh` (:24-25, :86) y `docs/adaptar-el-curso.md`, `docs/desplegar.md` y `docs/desarrollo-local.md`.

## Textos legales

- `contenido/legal/consentimientos.md`: versión en el frontmatter, un texto corto por tipo y bloques condicionales como `{{#NEWSLETTER}}`. `contenido/legal/privacidad.md` enumera los permisos en varias secciones.
- `contenido.py`: `_BLOQUES` (:212-215) para un bloque condicionado a la función; `version_legal` (:166-172). `GET /api/legal/consentimientos` (`alumnos.py`:647-656) con `TEXTOS_CONSENTIMIENTO` (:39).

## Reporte del autor

- `backend/vibe_tutor/admin.py`, `GET /reporte` (:137-148). Las claves nuevas se muestran solas en `Admin.tsx` a través de `VistaDatos`. Esta lista no se exporta (FR-008).

## Tests que cambian

- Igualdades exactas: `backend/tests/test_alumnos.py` (:137, :864, :870, :889, :1040-1049), `test_main.py` (:25-32), `test_config.py` (:53-72), `frontend/tests/configuracion.test.ts` (:5-37).
- `backend/tests/test_db.py`: `TABLAS` (:10-37) y la equivalencia entre base nueva y migrada (:177-188).
- `backend/tests/test_aprobacion.py`: toda ruta nueva de alumno usa `alumno_aprobado` o se lista en `PERMITIDAS` o `PUBLICAS`.
- Frontend: `frontend/tests/paginas.test.tsx` (Mostrar :368-448, MisDatos :450-590, Admin :693-790). `frontend/tests/sitio.test.ts` (:93-98) prohíbe nombres de marca en el código del frontend: los textos propios llegan por configuración.

## Del spec 001 para citar

FR-002, FR-023, FR-024, FR-027, FR-029, FR-030 y FR-031; `data-model.md` (consentimientos :39-56, links :169-182, eventos :200-211, migraciones :229-239); `contracts/api.md` (`POST /links` :204-220, `PUT /consentimientos` :245-253, reporte :284); `research.md` §9 y §16.
