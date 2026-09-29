# Implementation Plan: Siguiente paso al terminar el curso

**Branch**: `002-siguiente-paso` | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-siguiente-paso/spec.md`

## Summary

Después del primer link que registra el alumno, la web pregunta si tiene un negocio que ya vende. Si dice que sí, muestra el texto del siguiente paso y una casilla desmarcada para que le avisen. Todo depende de una bandera de configuración apagada por defecto y de tres textos de la instalación. La respuesta se suma a un contador sin alumno ni fecha; el aviso es un permiso nuevo (`siguiente_paso`) en el historial de consentimientos; el alumno lo maneja desde "Mis datos" y el autor ve tres números en su reporte. Sin IA, sin exportación y sin mails nuevos. Las decisiones están en [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12 (backend) y TypeScript con React 19 y Vite 8 (frontend), igual que el spec 001

**Primary Dependencies**: FastAPI, pydantic-settings y sqlite3; React, Vitest y Testing Library. Sin dependencias nuevas

**Storage**: la base SQLite del curso, con la migración 5 ([data-model.md](data-model.md))

**Testing**: pytest con tests primero (principio VI) y Vitest

**Target Platform**: el mismo servidor Linux del spec 001; la web se piensa primero para el celular

**Project Type**: web (backend y frontend)

**Performance Goals**: nada nuevo: una consulta y una escritura por respuesta

**Constraints**: apagado por defecto; sin costo por alumno; sin nombres de marca en el código del frontend (`frontend/tests/sitio.test.ts`); una base nueva y una migrada terminan con el mismo esquema

**Scale/Scope**: un endpoint nuevo, una migración, cambios chicos en seis rutas existentes y en dos pantallas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Se evalúa contra la constitución 1.1.0, que amplió el principio I el 28/9/2026 con el OK de Andrés.

| Principio | Cómo se cumple |
|---|---|
| I. En el eje de la marca | El siguiente paso aparece solo al terminar (después del primer link), apagado por defecto, sin precios y con un permiso propio, como pide el principio ampliado. Los textos para alumnos van en voseo y son borrador hasta el OK de Andrés. |
| II. Costo por alumno casi cero | No llama al tutor ni a servicios pagos (FR-011). |
| III. Datos mínimos y del alumno | Por alumno se guarda solo si ya contestó (parte de su avance) y el permiso de aviso (consentimientos). La respuesta va a un contador sin alumno ni fecha (FR-012). La lista no se exporta (FR-008). Todo se ve, se descarga y se borra desde "Mis datos". |
| IV. Contenido fechado y verificado | No agrega datos que se vencen. |
| V. La compu del alumno es sagrada | No toca el kit (FR-010). |
| VI. Tests primero y lo más simple que funcione | Backend con tests primero; pantallas con tests de Vitest. Solo se construye lo del spec. |

Resultado: pasa, sin excepciones. Después del diseño sigue pasando: el contador anónimo y la columna de avance no amplían los datos que el principio III permite guardar.

## Project Structure

### Documentation (this feature)

```text
specs/002-siguiente-paso/
├── spec.md
├── plan.md                  # este archivo
├── research.md              # decisiones
├── data-model.md            # migración 5
├── quickstart.md            # cómo validarlo de punta a punta
├── contracts/api.md         # cambios en la API
├── notas-para-el-plan.md    # dónde se engancha en el código
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
backend/vibe_tutor/
├── config.py        # SIGUIENTE_PASO y sus tres textos
├── db.py            # migración 5
├── dominio.py       # contador y "ya contestó"
├── alumnos.py       # POST /links, POST /siguiente-paso, consentimientos, mis datos, legal
├── contenido.py     # marcador {{SIGUIENTE_PASO}} y bloque {{#SIGUIENTE_PASO}}
├── admin.py         # reporte
└── main.py          # GET /config

backend/tests/       # test_siguiente_paso.py (nuevo) y ajustes en test_config, test_db,
                     # test_alumnos, test_admin, test_main, test_contenido y test_aprobacion

contenido/legal/     # consentimientos.md y privacidad.md
deploy/              # .env.example (y preparar-servidor.sh si lista claves opcionales)
docs/                # adaptar-el-curso.md, desarrollo-local.md y desplegar.md

frontend/src/
├── lib/api.ts
├── componentes/Configuracion.tsx
├── paginas/Mostrar.tsx
└── paginas/MisDatos.tsx

frontend/tests/      # paginas.test.tsx, configuracion.test.ts y api.test.ts
```

**Structure Decision**: la misma web del spec 001, con backend y frontend. No se agrega ningún módulo ni carpeta.

## Complexity Tracking

Sin violaciones de la constitución que justificar.
