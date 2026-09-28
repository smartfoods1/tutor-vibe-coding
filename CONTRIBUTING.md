# Cómo contribuir

Gracias por querer mejorar el curso. Este proyecto existe para que gente que nunca programó llegue
a publicar algo propio, y cada cambio se mide contra eso: si lo hace más claro, más seguro o más
barato de sostener para quien lo da, suma.

## Antes de empezar

- Leé el [código de conducta](CODE_OF_CONDUCT.md).
- Para un problema de seguridad, no abras un issue: seguí [SECURITY.md](SECURITY.md).
- Para una duda sobre cómo usar, adaptar o desplegar el curso, preguntá en
  [Discussions](https://github.com/smartfoods1/tutor-vibe-coding/discussions).
- Para algo chico (un error, una frase confusa, un dato vencido), abrí un issue o mandá el pull
  request directo. Para algo grande, abrí primero un issue de idea y conversémoslo.
- Levantá el proyecto en tu compu con [docs/desarrollo-local.md](docs/desarrollo-local.md). Con
  el modo demo no necesitás claves.

## Cambios de contenido

El contenido vive en `contenido/` y es lo que más impacto tiene. Algunas reglas:

- **Todo dato que se vence va al machete, con fuente y fecha.** Precios, planes, pasos de
  instalación, límites y líneas de ayuda van en `contenido/machete.yaml`, con `fuente` (la página
  oficial), `verificado` (la fecha en que lo miraste) y `probado` (`true` solo si alguien lo hizo
  de verdad). En el pull request contá cómo lo verificaste. El machete es CC0, como el kit: viaja
  dentro de cada kit que baja un alumno.
- **Nada es "gratis" sin haberlo probado.** Un test impide que un dato diga "gratis", "sin costo"
  o parecidos si no tiene `probado: true`.
- **Las decisiones pedagógicas llevan su evidencia.** Si cambiás algo del recorrido, citá la
  fuente como lo hace `contenido/curriculo.md` (por ejemplo, "03 [5]" es la fuente 5 del informe
  03) o marcalo como apuesta. Si sumás una fuente nueva, agregala al informe que corresponda en
  `contenido/investigacion/`, con su estado de verificación.
- **Idioma.** Todo texto para alumnos va en español rioplatense, con voseo, sin emojis, con
  oraciones cortas y una palabra técnica por vez (con su equivalente en inglés cuando aparece en
  pantalla).
- **El kit es corto a propósito.** Las instrucciones del kit (`contenido/kit/AGENTS.md` y
  `CLAUDE.md`) tienen un límite de tamaño que los tests controlan. Si sumás algo, sacá otra cosa o
  llevalo a una lección.
- **Marcadores.** No borres ni renombres `{{AUTOR}}`, `{{NEWSLETTER}}`, `{{AYUDA}}`,
  `{{URL_CURSO}}` y compañía: los completa el backend.

Corré los tests del backend después de cualquier cambio de contenido: también revisan el
contenido.

## Cambios de código

### Backend: tests primero

El backend se trabaja con TDD: primero un test que falla y muestra el comportamiento que querés,
después el código mínimo que lo hace pasar, y recién entonces la limpieza.

Desde la raíz del repo:

```bash
cd backend
.venv/bin/pytest            # toda la suite
.venv/bin/pytest -k kit     # una parte
```

Los tests no llaman a servicios pagos: Claude, Gemini, Resend y Turnstile se simulan (con `respx`
o con clientes falsos). Si algo solo se puede probar contra la API real, marcalo con
`@pytest.mark.real` para que no corra por defecto. Hoy no hay ninguno: el tuyo se corre a mano con
`.venv/bin/pytest -m real`.

### Frontend

Desde la raíz del repo:

```bash
cd frontend
npm test          # Vitest y Testing Library
npm run build     # también revisa los tipos
```

Pensá primero en el celular, mantené la CSP estricta (nada de scripts ni estilos en línea) y
probá con el teclado.

### Estilo

- El código usa nombres en español, como el resto del proyecto. Los mensajes de commit, también.
- Lo más simple que funcione: sin dependencias nuevas si se puede evitar.
- Ningún secreto en el repo. La configuración nueva va a `Settings`
  (`backend/vibe_tutor/config.py`) y a `deploy/.env.example`, sin valores reales; un test
  controla que los dos coincidan.

## Cambios grandes: spec-kit

El proyecto se diseñó con [spec-kit](https://github.com/github/spec-kit) y su especificación está
en `specs/`. Para una funcionalidad nueva, un módulo nuevo o un cambio de diseño, seguí el mismo
flujo con los comandos de `.claude/skills/` en Claude Code: `/speckit-specify` (qué y para quién),
`/speckit-clarify` (dudas antes del plan), `/speckit-plan`, `/speckit-tasks` e
`/speckit-implement`. Los principios que no se negocian están en la constitución,
`.specify/memory/constitution.md`: costo casi cero por alumno, datos mínimos, contenido fechado y
la compu del alumno como algo sagrado.

## Reportar problemas del tutor sin datos de alumnos

Si el tutor (el de la web o el del kit) respondió mal, nos sirve mucho saberlo, pero **nunca
pegues datos de alumnos**: ni mails, ni nombres, ni sus ideas, ni capturas, ni conversaciones
exportadas.

En cambio, contá:

- En qué módulo pasó y con qué herramienta (web, Claude Code o Codex).
- Qué escribió la persona, con tus palabras o con un ejemplo inventado que provoque lo mismo.
- Qué respondió el tutor y qué esperabas.
- Si lo pudiste repetir en tu instalación local, con el modo demo apagado.

Si operás una instalación y un alumno te reporta algo, pedile permiso antes de compartir cualquier
cosa, y aun así anonimizalo.

## Pull requests

1. Hacé un fork y una rama con un nombre que diga qué cambia.
2. Mantené el cambio chico y enfocado.
3. Asegurate de que pasen los tests del backend y del frontend. GitHub Actions los corre en cada
   pull request; en tu fork arrancan apagadas hasta que las habilitás en la pestaña Actions.
4. En la descripción, contá qué cambia, por qué y, si es contenido, la fuente y la fecha.

Al contribuir aceptás que tu aporte se publique con la licencia de la carpeta que tocaste: MIT
para el código, CC BY 4.0 para el contenido y la documentación, y CC0 para `contenido/kit/`,
`contenido/ejemplos/` y `contenido/machete.yaml`.
