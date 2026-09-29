# Tutor de vibe coding

Curso gratis de vibe coding con tutor de IA, para gente que nunca programó: lleva a cada persona de
una idea que tiene en la cabeza a una página propia, publicada con un link. Lo armó Andrés
(@specialandres) para su público original y es código abierto para que cualquiera lo forkee y arme
su propio curso. "Vibe Tutor" es el nombre de trabajo; el nombre público sale de la configuración.

## Cómo está armado

| Carpeta | Qué hay |
|---|---|
| `backend/` | FastAPI (Python 3.12): inscripción, tutor de los módulos 1 a 3, costos y topes, mails, armado del kit |
| `frontend/` | React + Vite + TypeScript, pensado primero para el celular |
| `contenido/` | Todo lo que ven los alumnos: prompts, guías, kit, machete, mails, textos legales, investigación y currículo (ver `contenido/README.md`) |
| `deploy/` | Servicio, plantilla de nginx y scripts de despliegue |
| `docs/` | Desarrollo local, despliegue y cómo adaptar el curso (`docs/desarrollo-local.md`, `docs/desplegar.md`, `docs/adaptar-el-curso.md`) |
| `specs/` | Especificación, plan, contratos y tareas con spec-kit |
| `.specify/memory/constitution.md` | La constitución: los principios que mandan sobre todo lo demás |

Los módulos 1 a 3 pasan en la web; los módulos 4 a 7, en la compu del alumno, con un kit que
convierte a Claude Code o a Codex en tutor.

## Convenciones

- Todo texto va en español rioplatense, con voseo y sin emojis: el de los alumnos y también el del
  repo.
- Los datos que se vencen (instalación, planes, precios, cómo publicar, líneas de ayuda) viven solo
  en `contenido/machete.yaml`, con fuente oficial, fecha de verificación y `probado`. No se escriben
  de memoria en otro lado, y "gratis" se dice solo con `probado: true`. El machete es CC0 porque
  viaja dentro de cada kit.
- Lo propio de cada instalación va en configuración, no en el repo: `AUTOR_NOMBRE`,
  `NEWSLETTER_NOMBRE` y `MODO_DEMO` en el `.env` del backend, `VITE_NOMBRE_CURSO` en el frontend y
  el servidor y el dominio en `deploy/despliegue.env`. En `contenido/` se escribe `{{AUTOR}}` y
  `{{NEWSLETTER}}`, que reemplaza el backend.
- Nunca se versionan secretos, datos de alumnos ni audios.
- Backend con TDD (Constitución VI): primero el test, que tiene que fallar; después el código.
- Los cambios del kit se validan con una sesión real en Claude Code y en Codex antes de publicarse.
- Para cambios grandes (una función nueva, un módulo, un cambio de diseño), flujo spec-kit:
  constitución, specify, clarify, plan, tasks, implement. Para arreglos chicos no hace falta.
- El contenido para alumnos es borrador hasta que lo aprueba quien mantiene el curso.

## Tests

Desde la raíz del repo (cada línea entre paréntesis, para que el `cd` no se arrastre a la
siguiente):

```bash
(cd backend && python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]" && .venv/bin/pytest)
(cd frontend && npm ci && npm test)
```

Ningún test llama a servicios pagos. La marca `real` queda reservada para tests contra las APIs
pagas (hoy no hay ninguno); no corren por defecto. Para probar todo en local sin claves de API,
`MODO_DEMO=true`: el tutor responde con un guion fijo y la voz queda apagada. El paso a paso está
en `docs/desarrollo-local.md`.

## Licencias

Código (`backend/`, `frontend/`, `deploy/`, `.github/` y tests): MIT. Contenido del curso y
documentación de diseño (`contenido/` salvo `kit/`, `ejemplos/` y `machete.yaml`; `specs/`,
`.specify/memory/` y `docs/`): CC BY 4.0. `contenido/kit/`, `contenido/ejemplos/` y
`contenido/machete.yaml` (viaja en cada kit): CC0 1.0. El resto de `.specify/` y los comandos de
spec-kit conservan la licencia MIT de github/spec-kit.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/001-curso-vibe-coding/plan.md` (el curso) and, for the feature in progress,
`specs/002-siguiente-paso/plan.md`
<!-- SPECKIT END -->
