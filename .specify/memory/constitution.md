<!--
Sync Impact Report
- Version change: 1.0.2 → 1.0.3 (PATCH, 2026-09-28)
- Motivo: revisión final antes de publicar el repositorio. Salen detalles que no hacen al curso y
  que cualquier fork heredaría: notas internas de estrategia de marca, prácticas de operación del
  autor y el nombre de su proyecto anterior.
- Principio I: la razón ya no cita notas de estrategia de la cuenta; dice por qué vale el curso
  (parte de la idea propia de cada persona).
- Principio III: la regla de los datos de alumnos queda dicha para cualquier instalación: nunca se
  copian fuera del sistema del curso, salvo la exportación consentida a la lista de novedades.
- Principio VI: el proyecto anterior del autor ya no se nombra.
- Restricciones técnicas: salen dos oraciones sobre prácticas de operación del autor, que no son
  del proyecto; queda que el despliegue no toca ningún otro servicio del servidor.
- Ninguno cambia la intención de un principio.
- Plantillas: sin cambios.

Historial:
- Version change: 1.0.1 → 1.0.2 (PATCH, 2026-09-28)
  Motivo: el repositorio pasa a ser público (código abierto, un solo commit sin historial) para
  que cualquiera lo forkee y arme su propio curso, y la instalación del autor sigue andando con los
  mismos archivos: lo propio del autor pasa a configuración que no se versiona.
  Restricciones técnicas: el repositorio pasa de privado a público (código MIT, contenido
  CC BY 4.0, kit CC0); los secretos, los datos de alumnos y los audios nunca se versionan.
  Principio II: la razón habla del curso gratis a secas, no como pieza de captación.
  Principio III: los datos de alumnos no se copian fuera del sistema del curso, y la única
  exportación consentida es a la lista de novedades del autor (consentimiento `novedades`; el
  servicio se configura con `NEWSLETTER_NOMBRE`).
  Principio VI: el fork es del backend de un proyecto anterior del autor.
  Preámbulo: el nombre público del curso sale de la configuración de cada instalación.
  Ninguno cambia la intención de un principio: aclaran cómo se cumplen con el repo abierto.
  Plantillas: sin cambios.
- Version change: 1.0.0 → 1.0.1 (PATCH, 2026-09-28)
  Principio modificado: V. La compu del alumno es sagrada. El tercer punto pasa de "el kit asume
  los permisos por defecto" a "el kit endurece los permisos desde su carpeta, nunca los afloja".
  Motivo: desde agosto de 2026 las sesiones nuevas de Claude Pro arrancan en modo automático (ver
  specs/001-curso-vibe-coding/research.md §13 bis). Aclara cómo se cumple el principio; no cambia
  su intención. Plantillas: sin cambios.
- Version change: plantilla sin completar → 1.0.0 (ratificación inicial, 2026-09-27)
- Principios definidos: I. En el eje de la marca · II. Costo por alumno casi cero para el operador ·
  III. Datos mínimos y del alumno · IV. Contenido fechado y verificado · V. La compu del alumno
  es sagrada · VI. Tests primero y lo más simple que funcione
- Secciones agregadas: Restricciones técnicas y operativas · Flujo de trabajo y aprobaciones
- Secciones eliminadas: ninguna
- Plantillas:
  - .specify/templates/plan-template.md (el Constitution Check toma los gates de este archivo; sin cambios)
  - .specify/templates/spec-template.md (sin secciones obligatorias nuevas; sin cambios)
  - .specify/templates/tasks-template.md (la nota de tests ahora remite al principio VI)
- TODO diferidos: ninguno
-->

# Vibe Tutor Constitution

Curso gratuito de vibe coding para la tribu de @specialandres, su público original: de lo que
imaginás a algo que existe, para gente que no programa. "Vibe Tutor" es el nombre de trabajo; el
nombre público lo define cada instalación en su configuración.

## Core Principles

### I. En el eje de la marca

- El curso enseña primero una forma de pensar y después las herramientas. Claude Code y Codex
  son el medio, no el tema.
- Toda lección se aplica a la idea propia del alumno. Ningún ejercicio usa un ejemplo genérico
  cuando se puede usar su idea.
- Todo texto para alumnos va en español rioplatense, con voseo, sin emojis, cercano y claro.
- El tutor nunca se presenta como Andrés ni imita su voz. La voz real de Andrés aparece solo en
  sus audios grabados.
- Nada de postura de gurú ni de promesas de negocio. El curso acompaña: no vende, no diagnostica.
- Si un alumno expresa un malestar serio, el tutor responde con cuidado, no diagnostica y deriva a
  ayuda profesional.

Razón: un curso técnico genérico ya existe gratis; este vale por partir de la idea propia de cada
persona.

### II. Costo por alumno casi cero para el operador

- Ninguna función puede generarle a Andrés un costo sin techo por alumno. El curso es gratis y
  abierto siempre, así que la cantidad de alumnos no tiene techo.
- El tutor de la web tiene tope por alumno y tope mensual, con aviso a Andrés al 80%. Al llegar a
  un tope, el curso pasa a la guía escrita sin perder el avance del alumno; nunca se cae.
- La construcción (módulos 4 a 7) corre en la herramienta y el plan del propio alumno.

Razón: un curso gratis que cuesta por uso se vuelve un pasivo justo cuando funciona.

### III. Datos mínimos y del alumno

- Se guarda solo lo necesario: mail, consentimientos, avance, la idea, el link publicado y la
  conversación con el tutor. Las capturas de pantalla se procesan y no se guardan.
- Los datos de alumnos nunca se copian fuera del sistema del curso, salvo la exportación a la
  lista de novedades del autor de quien lo aceptó de forma explícita.
- El alumno puede ver, descargar y borrar todos sus datos.
- Nada del alumno se muestra ni se usa como contenido sin su consentimiento explícito.
- El tutor nunca pide contraseñas, claves ni datos de pago.

Razón: la tribu es sensible y las ideas pueden ser íntimas; la confianza es el activo.

### IV. Contenido fechado y verificado

- Todo dato que se vence (pasos de instalación, planes, precios, nombres de modelos, pasos para
  publicar) vive en el machete con fecha de verificación y fuente oficial.
- El curso no promete nada que no se haya comprobado en una prueba real. "Gratis" se afirma solo
  si se probó con una cuenta gratis.
- Una revisión mensual propone actualizaciones. Nada se publica a los alumnos sin el OK de Andrés.

Razón: Claude Code y Codex cambian cada pocas semanas; un curso siempre abierto se pudre si no.

### V. La compu del alumno es sagrada

- Las instrucciones del kit prohíben tocar nada fuera de la carpeta del proyecto.
- La herramienta pide permiso antes de instalar cualquier cosa y explica cada comando antes de
  correrlo.
- El kit endurece desde su propia carpeta los permisos de la herramienta cuando esta lo permite,
  nunca los afloja, y nunca le pide al alumno desactivarlos.

Razón: el alumno nunca abrió una terminal; un solo susto le confirma que "esto no es para mí".

### VI. Tests primero y lo más simple que funcione

- Todo cambio del backend de la web se escribe con tests primero (rojo, verde, refactor).
- Todo cambio del kit se valida con una sesión real en las dos herramientas antes de publicarse.
- Solo se construye lo que está en el spec aprobado. Se hace un fork del backend de un proyecto
  anterior del autor, no una plataforma compartida, hasta que exista un tercer curso que la
  justifique.

Razón: lo que no se prueba se rompe en la cara de un alumno que no sabe qué pasó.

## Restricciones técnicas y operativas

- El repositorio es público: código MIT, contenido CC BY 4.0, kit CC0; los secretos, los datos de
  alumnos y los audios nunca se versionan.
- Los secretos viven solo en el servidor (fuera del repo); el repo tiene un `.env.example` sin valores.
- El despliegue no toca ningún otro servicio del servidor.
- La web funciona primero en el celular: los módulos 1 y 2 se completan desde un teléfono.
- El kit sirve igual para Claude Code y para Codex desde una sola fuente de instrucciones.
- Los modelos de IA se eligen en el plan con costo estimado por alumno; los de Gemini, si se usan,
  nunca son `gemini-2.0-flash`.

## Flujo de trabajo y aprobaciones

- Flujo spec-kit: constitución → spec → clarify → plan → tasks → implement. Andrés aprueba el spec,
  el plan y el contenido del curso antes de publicarse.
- Antes de escribir el curso se corren las pruebas de viabilidad definidas en el spec.
- Antes del lanzamiento, 5 personas de la tribu completan el curso (Mac y Windows, herramienta
  gratis y paga).
- A los 30 días del lanzamiento se aplica la regla de decisión del spec y se anota el resultado
  con fecha.

## Governance

- Esta constitución manda sobre cualquier otra práctica del proyecto. Cada plan pasa el
  Constitution Check; toda excepción se justifica por escrito en el plan.
- Las enmiendas las aprueba Andrés, se registran en el Sync Impact Report y suben la versión:
  MAJOR si quitan o redefinen un principio, MINOR si agregan uno o lo amplían, PATCH si aclaran.

**Version**: 1.0.3 | **Ratified**: 2026-09-27 | **Last Amended**: 2026-09-28
