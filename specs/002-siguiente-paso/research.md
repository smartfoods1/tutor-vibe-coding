# Research: Siguiente paso al terminar el curso

**Fecha**: 2026-09-28. Relevamiento del código en [notas-para-el-plan.md](notas-para-el-plan.md).

## 1. Cuándo se pregunta

- **Decision**: después del primer link que registra el alumno. Es el primero si, al registrarlo, el alumno tiene un solo evento `link`.
- **Rationale**: el código no tiene un "link final": cualquier registro lleva al módulo 7, y un alumno puede tener hasta cinco links. En la práctica pasa al terminar, porque la lección 7 es la que manda a registrarlo. Los eventos `link` no se borran al borrar un link, así que borrar y volver a registrar no repite la pregunta.
- **Alternatives considered**: marcar un link como "final" (cambia el flujo del spec 001 y agrega una decisión más para el alumno); preguntar en cada registro (contradice FR-002).

## 2. Una sola vez por alumno

- **Decision**: columna `alumnos.siguiente_paso_respondido` (0 o 1). La pregunta solo sale con el primer link; si el alumno la cierra sin contestar, no vuelve a salir.
- **Rationale**: frena respuestas repetidas (doble clic o pedidos armados a mano) sin guardar qué contestó. Es parte del avance del alumno, que el principio III ya permite guardar.
- **Alternatives considered**: un evento por alumno (lleva fecha exacta y se podría cruzar con la respuesta); un token firmado de un solo uso (necesita guardar estado igual).

## 3. La respuesta, sin saber de quién es

- **Decision**: tabla `respuestas_siguiente_paso` con dos filas, `si` y `no`, y un total que se suma con un UPSERT. Sin alumno y sin fecha.
- **Rationale**: FR-012 pide contar sin guardar quién contestó. Sin fecha no hay forma de cruzar un total con el momento en que un alumno contestó. Borrar a un alumno no cambia el total, porque ya no es de nadie.
- **Alternatives considered**: eventos anónimos en `eventos` (tienen fecha: en un día con una sola respuesta se sabría de quién es); guardar la respuesta con el alumno (amplía los datos del principio III).

## 4. El permiso de aviso

- **Decision**: tipo nuevo `siguiente_paso` en `consentimientos`, con `version_texto = version_legal()` como los demás. La migración recrea la tabla, como la 3, y conserva el contador de ids, como la 4.
- **Rationale**: reusa el historial que ya sirve para "Mis datos", la descarga y el borrado en cascada.
- **Alternatives considered**: una tabla aparte (duplica el manejo de permisos); una columna en `alumnos` (pierde el historial con fechas).

## 5. Configuración

- **Decision**: `SIGUIENTE_PASO` (bandera, apagada por defecto), `SIGUIENTE_PASO_NOMBRE` (cómo se nombra el siguiente paso en los textos legales), `SIGUIENTE_PASO_PREGUNTA` y `SIGUIENTE_PASO_TEXTO`. La función está activa solo con la bandera prendida y los tres textos con valor (`Settings.hay_siguiente_paso`). Con la bandera prendida y algún texto vacío, queda inactiva y el reporte dice cuáles faltan.
- **Rationale**: FR-001 y FR-009. Sigue el precedente de `APROBACION_MANUAL` y deja lo propio de cada instalación fuera del repo.
- **Alternatives considered**: textos en `contenido/` con marcadores (el texto del siguiente paso es de cada instalación, no del curso).

## 6. Textos legales

- **Decision**: `contenido/legal/consentimientos.md` suma el texto corto `siguiente_paso` y una sección dentro de `{{#SIGUIENTE_PASO}}`; `privacidad.md` suma bloques en finalidades, datos que se guardan, permisos opcionales, conservación y derechos. El marcador `{{SIGUIENTE_PASO}}` se reemplaza por `SIGUIENTE_PASO_NOMBRE`. Los dos textos pasan a la versión `2026-09-30`.
- **Rationale**: FR-013. La versión nueva deja registrado qué texto aceptó cada persona. Siguen en borrador hasta el OK de Andrés y la revisión de un abogado.

## 7. Pantallas

- **Decision**: la pregunta va en la pantalla de "link registrado" de `Mostrar.tsx`, debajo de lo que ya muestra. "Sí" muestra el texto y la casilla desmarcada; "No" registra la respuesta; "Ahora no" la cierra sin llamar a nada. "Mis datos" suma una casilla como la de novedades, visible si la función está activa o si el alumno tiene el aviso prendido, para que siempre lo pueda sacar. Los textos llegan por `GET /config`.
- **Rationale**: la pantalla ya es el cierre del curso, y el código del frontend no puede llevar nombres de marca (`sitio.test.ts`).

## 8. Reporte

- **Decision**: clave `siguiente_paso` en `GET /admin/reporte`, que el admin ya muestra sin cambios en el frontend.

## 9. Fuera de alcance

Mandar el aviso cuando abre el siguiente paso (se hace con ese siguiente paso, desde el mismo sistema), exportar la lista y preguntarle a quien registró links antes de prender la función.
