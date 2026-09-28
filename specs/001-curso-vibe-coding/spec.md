# Feature Specification: Curso gratuito de vibe coding para la tribu

**Feature Branch**: `001-curso-vibe-coding`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "Un tutor como el de un proyecto anterior del autor con el tema introducción y configuración básica de Claude Code, Codex y el concepto de vibe coding: cómo pensar como vibe coder." Definido con Andrés el 27/9/2026: gratis para la tribu, versión en el eje de la marca (de lo que imaginás a algo que existe, para gente que no programa), resultado = la idea del alumno publicada con un link, abierto siempre, voz de Andrés grabada y sin vivos, puerta web + kit en la herramienta.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Construir y publicar su idea con el kit (Priority: P1)

Una persona que nunca programó abre el kit en su computadora con Codex (plan gratis de ChatGPT) o con Claude Code (Claude Pro). La herramienta hace de tutor: sabe cuál es su idea y dónde quedó, propone un paso por vez y explica antes de actuar. En la primera sesión publica una versión mínima de su idea con un link público. En las siguientes la mejora con el ciclo pedir, predecir, mirar y ajustar, aprende a volver atrás cuando algo se rompe y termina con la versión final publicada.

**Why this priority**: es el resultado que definió Andrés (la idea del alumno publicada con un link) y lo único que el curso promete. Se puede probar sin la web: con kits armados a mano para las 5 personas del piloto.

**Independent Test**: entregarle a una persona sin experiencia un kit con su idea ya escrita, en Mac o Windows, con Codex gratis o Claude Pro, y verificar que termina con un link público que funciona sin más ayuda que el curso.

**Acceptance Scenarios**:

1. **Given** un kit con la idea del alumno abierto por primera vez en Codex o en Claude Code, **When** el alumno escribe "empecemos", **Then** el tutor se presenta, resume la idea en dos frases y propone el primer paso sin pedirle nada técnico.
2. **Given** la primera sesión en la herramienta, **When** el alumno sigue los pasos, **Then** antes de terminar esa sesión tiene una versión mínima de su idea publicada, con un link que abre cualquiera sin cuenta.
3. **Given** un alumno que usa Codex con el plan gratis, **When** llega el momento de publicar, **Then** publica sin terminal y sin pagar, siguiendo los pasos que le da el tutor.
4. **Given** un alumno en la lección 5, **When** va a pedir un cambio, **Then** el tutor lo invita a anotar qué espera ver y, después del cambio, a comparar lo esperado con lo que pasó.
5. **Given** algo que se rompió después de un cambio, **When** el alumno lo cuenta, **Then** el tutor explica qué pasó en palabras simples y le muestra cómo volver a la versión anterior.
6. **Given** una acción que requiere instalar software o tocar algo fuera de la carpeta del proyecto, **When** el tutor la necesita, **Then** explica qué va a hacer y pide permiso antes; nunca toca nada fuera de la carpeta.
7. **Given** un alumno que retoma otro día, **When** abre el kit, **Then** el tutor sabe dónde quedó y sigue desde ahí.
8. **Given** el comienzo de una lección del kit, **When** el tutor la abre, **Then** le indica al alumno dónde escuchar el audio de Andrés de ese módulo.

---

### User Story 2 - Pasar la puerta: inscribirse, pensar como vibe coder y dejar su idea en una página (Priority: P2)

Desde el celular, después de ver contenido de Andrés, una persona se inscribe con su mail, escucha el audio de Andrés y conversa con el tutor, por texto o por voz, sobre qué es el vibe coding y qué le da miedo. En el módulo 2 el tutor la entrevista sobre su idea hasta dejarla en una página: qué es, para quién, qué siente cuando la imagina funcionando y cuál es la versión más chica que ya valdría la pena.

**Why this priority**: acá la persona se inscribe y deja su idea escrita, y acá vive la marca. Entrega valor sin instalar ni pagar nada.

**Independent Test**: inscribirse desde un celular con un mail nuevo, completar los módulos 1 y 2, y verificar que la idea en una página se puede descargar y que el inscripto quedó registrado con sus consentimientos.

**Acceptance Scenarios**:

1. **Given** una persona nueva en la página de inscripción, **When** deja su mail, **Then** recibe un código de un solo uso y entra sin crear contraseña.
2. **Given** la inscripción, **When** la persona la completa, **Then** se le piden por separado dos consentimientos: mails del curso (necesario) y recibir las novedades de Andrés (opcional, desmarcado por defecto y solo si la instalación tiene newsletter), y recibe el mail de bienvenida con el acceso.
3. **Given** el módulo 1, **When** empieza, **Then** escucha un audio de Andrés de 2 a 3 minutos, con transcripción, y el tutor conversa por texto o por voz, en voseo, sin presentarse como Andrés.
4. **Given** el final de la entrevista del módulo 2, **When** el tutor la cierra, **Then** el alumno ve "mi idea en una página" y la puede editar y descargar.
5. **Given** una idea que necesita logins, pagos o datos compartidos entre usuarios, **When** el tutor la achica, **Then** propone una versión que entra en una página y guarda el resto como "qué sigue".
6. **Given** un alumno que vuelve otro día desde otro dispositivo, **When** entra con su mail, **Then** retoma donde quedó.

---

### User Story 3 - Armar su taller con ayuda (Priority: P3)

El alumno elige herramienta con el tutor según lo que ya tiene (ChatGPT gratis: Codex; Claude Pro: Claude Code) y su sistema (Mac o Windows). Instala la app de escritorio siguiendo los pasos que le da el tutor, manda una captura si se traba y descarga el kit personalizado, con su idea adentro.

**Why this priority**: la instalación es donde más gente abandona. Sin esta historia, la historia 1 depende de que alguien arme cada kit a mano.

**Independent Test**: con una computadora sin nada instalado, completar el módulo 3 y verificar que el kit descargado abre en la herramienta elegida y trae la idea del alumno.

**Acceptance Scenarios**:

1. **Given** el módulo 3, **When** el alumno cuenta qué tiene y qué computadora usa, **Then** el tutor recomienda una herramienta y dice su costo real; dice "gratis" solo si está verificado.
2. **Given** un alumno trabado en la instalación, **When** sube una captura, **Then** el tutor la lee y le da el próximo paso concreto, y la captura no queda guardada.
3. **Given** una captura que muestra datos sensibles (contraseñas, claves), **When** el tutor la lee, **Then** advierte al alumno y no repite esos datos.
4. **Given** la instalación terminada, **When** el alumno descarga el kit, **Then** el kit trae su idea, las instrucciones para la herramienta elegida, las lecciones 4 a 7 y la fecha de verificación de los datos que se vencen.
5. **Given** un alumno que solo tiene celular, o que usa Linux, **When** llega al módulo 3, **Then** el tutor le explica qué necesita para seguir y su avance queda guardado.
6. **Given** un alumno que terminó su idea, **When** pasan 3 días sin que descargue el kit, **Then** recibe un mail que le recuerda dónde quedó.

---

### User Story 4 - Mostrar lo que hizo (Priority: P4)

Al terminar, el alumno registra su link en la web del curso, elige si se puede mostrar en público o usar como contenido de Andrés, y decide si su página lleva la línea "Hecho en [curso]".

**Why this priority**: mide el resultado que importa (links publicados) y difunde el curso con el trabajo de los alumnos.

**Independent Test**: registrar un link desde un alumno de prueba y verificar que el consentimiento queda guardado y que llega el mail "contame qué hiciste".

**Acceptance Scenarios**:

1. **Given** la lección 7, **When** el alumno termina, **Then** el tutor del kit le indica cómo registrar el link en la web del curso.
2. **Given** el registro del link, **When** el alumno lo completa, **Then** elige por separado, con las dos opciones desmarcadas por defecto, si se muestra en una galería y si Andrés lo puede usar como contenido.
3. **Given** la línea "Hecho en [curso]", **When** el alumno no la pide, **Then** su página no la lleva; si la pide, la línea lleva a la página de inscripción.
4. **Given** un link registrado, **When** se guarda, **Then** el alumno recibe el mail "contame qué hiciste".

---

### User Story 5 - Operar el curso sin estar encima (Priority: P5)

Andrés ve el embudo (inscriptos, módulos, kits, links) y el gasto del tutor contra los topes, aprueba las actualizaciones de los datos que se vencen y exporta a la lista de novedades a quienes lo aceptaron.

**Why this priority**: el curso es siempre abierto y sin vivos. Tiene que poder operarse en minutos por semana y decidirse con la regla de los 30 días.

**Independent Test**: con datos de prueba, pedir el reporte, simular el 80% del tope mensual, aprobar un cambio del machete y exportar la lista de novedades.

**Acceptance Scenarios**:

1. **Given** el curso andando, **When** Andrés pide el reporte, **Then** ve inscriptos, módulos 1 a 3 completados, kits descargados, links registrados y gasto del mes.
2. **Given** el gasto del tutor en el 80% del tope mensual, **When** se cruza ese umbral, **Then** Andrés recibe un aviso.
3. **Given** un tope alcanzado (del alumno o del mes), **When** el alumno escribe, **Then** el tutor pasa a la guía escrita sin perder el avance y le explica qué pasa.
4. **Given** un dato vencido que detecta la revisión mensual, **When** se le propone el cambio a Andrés con su fuente, **Then** no llega a los alumnos hasta que él lo aprueba.
5. **Given** alumnos que aceptaron recibir las novedades de Andrés, **When** Andrés pide la exportación, **Then** obtiene un archivo listo para importar en su plataforma de newsletter que incluye solo a esas personas.
6. **Given** un alumno que pide borrar sus datos, **When** confirma, **Then** se borran su conversación, su idea, su avance, sus links y sus consentimientos, y deja de recibir mails.

---

### Edge Cases

- El alumno llega al límite del plan gratis de Codex a mitad de una sesión: el tutor anota dónde quedó, explica cuándo va a poder seguir y qué alternativas tiene (esperar a que se renueve el límite o pasar al plan Go).
- OpenAI saca Codex del plan gratis: el machete se actualiza, la web deja de decir "gratis" y el curso sigue siendo completable por al menos un camino, con su costo dicho de frente.
- El alumno elige Claude Code con el plan gratis de Claude: el tutor le explica que necesita Pro y le ofrece el camino de Codex.
- Se agotan las publicaciones del hosting gratuito (unas 20 por mes): el curso enseña a probar en la propia computadora y publicar poco; el tutor evita publicar de nuevo sin cambios.
- La idea usa datos de salud, datos de otras personas o contenido íntimo: el tutor advierte que un link público lo puede ver cualquiera y propone versiones sin datos personales.
- El alumno pierde la carpeta del kit: la vuelve a descargar desde la web, con su idea. El curso le enseña que su sitio es una carpeta que puede guardar y mudar.
- El mail con el código no llega: el alumno puede pedir reenvío (con límite) y recibe ayuda para buscarlo en spam.
- Uso abusivo (inscripciones en masa, intentos de gastar el tutor, instrucciones escondidas en capturas o en texto pegado): límites por mail y por origen, topes de costo, y el tutor trata lo pegado como datos, no como órdenes.
- Un alumno expresa un malestar serio: el tutor responde con cuidado, no diagnostica y ofrece recursos de ayuda profesional de Argentina.

## Requirements *(mandatory)*

### Functional Requirements

**Inscripción y acceso**

- **FR-001**: Cualquier persona MUST poder inscribirse con su mail y entrar con un código de un solo uso, sin contraseña.
- **FR-002**: La inscripción MUST pedir por separado el consentimiento para los mails del curso y, opcional y desmarcado por defecto, el consentimiento para recibir las novedades de Andrés (solo si la instalación tiene newsletter, `NEWSLETTER_NOMBRE`).
- **FR-003**: El sistema MUST limitar inscripciones, pedidos de código y uso del tutor por mail y por origen para frenar abusos.
- **FR-004**: El alumno MUST poder retomar desde cualquier dispositivo con su mail, en el punto donde quedó.

**Web: módulos 1 a 3**

- **FR-005**: Cada uno de los 7 módulos MUST abrir con un audio de Andrés de 2 a 3 minutos, con transcripción. En los módulos 4 a 7 el kit indica dónde escucharlo.
- **FR-006**: El tutor de la web MUST conversar por texto y por voz (dictado y respuesta hablada) en español rioplatense, y MUST NOT presentarse como Andrés ni imitar su voz.
- **FR-007**: El módulo 1 MUST cubrir qué es y qué no es el vibe coding, el reparto de roles (el alumno piensa y decide, la máquina escribe) y el miedo como tema, y cerrar con el alumno contando con sus palabras qué le gustaría hacer.
- **FR-008**: El módulo 2 MUST producir "mi idea en una página" a partir de una entrevista (qué es, para quién, qué siente al imaginarla funcionando, cuál es la versión más chica que ya valdría la pena). El alumno la puede ver, editar y descargar.
- **FR-009**: Cuando la idea no entra en una página que funciona (logins, pagos, datos compartidos entre usuarios), el tutor MUST proponer una versión que entre y guardar el resto como "qué sigue".
- **FR-010**: El módulo 3 MUST recomendar una herramienta según lo que el alumno ya tiene y su sistema (Mac o Windows), decir el costo real verificado y guiar la instalación paso a paso.
- **FR-011**: El tutor MUST poder leer una captura de pantalla que el alumno sube cuando se traba. La captura MUST NOT quedar guardada después de la respuesta.
- **FR-012**: Los módulos 1 y 2 MUST poder completarse desde un celular.

**Kit: módulos 4 a 7**

- **FR-013**: El alumno MUST poder descargar un kit personalizado con su idea, las instrucciones para la herramienta elegida, las lecciones 4 a 7 y la fecha de verificación de los datos que se vencen.
- **FR-014**: Abierto en Claude Code o en Codex, el kit MUST hacer que la herramienta actúe como tutor: lee la idea y dónde quedó el alumno, propone un paso por vez, explica antes de actuar y anota el avance al final de cada sesión.
- **FR-015**: Las mismas lecciones MUST servir para las dos herramientas. Las diferencias se limitan a cómo publicar y a los nombres de las funciones de cada una.
- **FR-016**: La lección 4 MUST llevar al alumno a publicar una versión mínima de su idea, con link público, dentro de su primera sesión en la herramienta.
- **FR-017**: En las lecciones 5 y 6 el tutor MUST invitar al alumno a anotar qué espera ver antes de cada pedido y a compararlo después con lo que pasó (el cuaderno).
- **FR-018**: La lección 6 MUST enseñar a volver a una versión anterior y a leer un error como información.
- **FR-019**: El kit MUST prohibirle a la herramienta tocar nada fuera de la carpeta del proyecto, instalar software sin pedir permiso y pedir contraseñas o claves, y MUST exigirle que explique cada comando antes de correrlo.
- **FR-020**: El alumno MUST poder publicar con un link que abre cualquiera sin cuenta: con Claude Pro, desde la propia herramienta; con Codex, incluido el plan gratis, mediante un hosting gratuito que no requiere terminal.
- **FR-021**: Las lecciones MUST cargarse solo cuando hacen falta, para no gastar el plan del alumno.
- **FR-022**: La lección 7 MUST ofrecer, solo si el alumno lo pide, agregar a su página la línea "Hecho en [curso]" con un link a la inscripción.

**Mostrar y medir**

- **FR-023**: El alumno MUST poder registrar su link publicado en la web y elegir por separado, con las dos opciones desmarcadas por defecto, si se muestra en una galería y si Andrés lo puede usar como contenido.
- **FR-024**: El sistema MUST registrar con fecha, para el embudo: inscripciones, módulos 1 a 3 completados, kits descargados y links registrados.

**Mails**

- **FR-025**: El sistema MUST mandar tres mails automáticos, todos con baja en un clic: bienvenida con el acceso; recordatorio si el alumno terminó su idea pero no descargó el kit a los 3 días; y "contame qué hiciste" al registrar el link.

**Operación y costos**

- **FR-026**: El tutor de la web MUST tener un tope de costo por alumno y un tope mensual. Al 80% del tope mensual MUST avisarle a Andrés. Al llegar a cualquiera de los dos, MUST pasar a la guía escrita sin perder el avance.
- **FR-027**: Andrés MUST poder ver un reporte con el embudo y el gasto del mes.
- **FR-028**: Todo dato que se vence MUST mostrarse con su fecha de verificación. Una revisión mensual MUST proponer cambios con su fuente, y ningún cambio llega a los alumnos sin la aprobación de Andrés.
- **FR-029**: Andrés MUST poder exportar, en un formato que su plataforma de newsletter importa (una columna de mails), solo a los alumnos que aceptaron recibir sus novedades.

**Privacidad y cuidado**

- **FR-030**: El alumno MUST poder ver, descargar y borrar todos sus datos. Al borrarlos deja de recibir mails.
- **FR-031**: Los datos de alumnos MUST NOT copiarse fuera del sistema del curso ni compartirse con terceros, salvo la exportación consentida a la lista de novedades y los proveedores necesarios para operar (IA, mail, hosting).
- **FR-032**: Ante un malestar serio que exprese un alumno, el tutor MUST responder con cuidado, no diagnosticar y ofrecer recursos de ayuda profesional de Argentina.
- **FR-033**: El tutor MUST tratar el texto pegado y las capturas como datos, nunca como instrucciones.

### Key Entities *(include if feature involves data)*

- **Alumno**: persona inscripta. Mail, fecha de inscripción, herramienta elegida, sistema de su computadora, estado.
- **Consentimiento**: permiso dado por el alumno, con fecha. Mails del curso, novedades de Andrés, mostrar su link, uso como contenido.
- **Avance**: en qué módulo está el alumno y cuándo completó cada uno.
- **Idea**: "mi idea en una página" del alumno, con sus versiones y lo que quedó para "qué sigue".
- **Conversación**: mensajes entre el alumno y el tutor de la web. Las capturas no se guardan.
- **Kit**: cada descarga, con la versión del curso y la fecha de verificación de los datos que incluye.
- **Link publicado**: la dirección que registra el alumno, con sus consentimientos.
- **Consumo**: costo del tutor por alumno y por mes, contra los topes.
- **Dato del machete**: dato que se vence, con su fuente oficial, fecha de verificación y estado de aprobación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el piloto, al menos 4 de 5 personas sin experiencia terminan con su idea publicada y un link que funciona, sin más ayuda que la del curso.
- **SC-002**: En el piloto, al menos 4 de 5 personas publican su versión mínima dentro de la primera sesión en la herramienta, en 90 minutos o menos desde que abren el kit.
- **SC-003**: Una persona completa los módulos 1 y 2 desde el celular en 40 minutos o menos.
- **SC-004**: Para la mediana del piloto, el camino completo, de la inscripción a la idea publicada, lleva 6 horas de trabajo activo o menos.
- **SC-005**: El tutor de la web le cuesta a Andrés US$0,50 o menos por alumno en promedio y nunca supera el tope mensual.
- **SC-006**: En el piloto, ningún alumno tiene que compartir una contraseña o clave, y no se modifica ningún archivo fuera de la carpeta del proyecto.
- **SC-007**: Ningún dato que se vence lleva más de 45 días sin verificar cuando un alumno lo ve.
- **SC-008**: Mientras la web diga que el curso se puede hacer gratis, al menos una persona del piloto lo completó sin pagar nada.
- **SC-009**: A los 30 días del lanzamiento hay 100 inscriptos o más (si no, se trabaja la difusión) y al menos el 5% de los inscriptos registró su link (si no, se trabaja el curso).

## Assumptions

- **Público**: hispanohablantes, Argentina primero, de 30 a 60 años, que nunca programaron. Tienen celular y, para los módulos 4 a 7, una computadora Mac o Windows.
- **Estado de las herramientas, verificado el 27/9/2026 con fuentes oficiales** (detalle y fuentes en las notas del autor, no incluidas):
  - Codex está incluido en el plan gratis de ChatGPT, solo en la app de escritorio, "subject to rollout" y sin límites publicados; puede ser temporal. El plan Go cuesta US$8 (US$6 visto desde Argentina).
  - Claude Code requiere Claude Pro (US$20 por mes, US$17 en plan anual). La app de escritorio no pide terminal y publica páginas con un link público que abre cualquiera sin cuenta (una sola página, sin backend, hasta 16 MB).
  - Existe un hosting gratuito que publica sin terminal arrastrando una carpeta (Netlify Drop, cuenta con Google, unas 20 publicaciones por mes en el plan gratis).
- **Alcance de las ideas**: una página que funciona. Fuera de esta versión: logins, pagos y datos compartidos entre usuarios en los proyectos de los alumnos.
- **Fuera de esta versión del curso**: encuentros en vivo, comunidad o foro, certificados, Linux, otros idiomas y cualquier cobro.
- **Topes iniciales del tutor de la web**: US$1 por alumno en toda su vida y US$50 por mes, igual que en el proyecto anterior. Andrés los puede ajustar.
- **Retención de datos** (ajustada por Andrés el 28/9/2026, por la Ley 25.326): cada conversación con el tutor se borra 30 días después de terminar su módulo, y las de módulos sin terminar, 12 meses después de la última actividad del alumno; queda un resumen del módulo sin datos personales. La idea, el avance y los links se guardan hasta que el alumno los borre; las capturas, nunca.
- **Dependencias**: el backend de un proyecto anterior del autor (el frontend hay que rehacerlo), un dominio propio para el curso (`curso.example.com` en estos documentos; el registro DNS lo crea Andrés) y, si la instalación la tiene, su plataforma de newsletter.
- **A cargo de Andrés**: grabar los 7 audios, conseguir 5 personas de la tribu para el piloto, aprobar el contenido y definir el nombre público del curso ("Vibe Tutor" es un nombre de trabajo; el nombre público sale de la configuración del frontend, `VITE_NOMBRE_CURSO`, y "[curso]" se reemplaza por ese nombre).
- **Calendario objetivo**: pruebas de viabilidad y contenido a principios de octubre de 2026, piloto en octubre, lanzamiento en noviembre.
- **Pruebas de viabilidad, antes de escribir el curso**. Si alguna falla, se ajusta este spec antes de seguir:
  1. Codex con una cuenta gratis real completa una sesión de construcción (la lección 4) sin toparse con el límite; se mide cuánto rinde el plan.
  2. Un kit mínimo hace que Claude Code y Codex actúen como tutor (un paso por vez, explicar antes de actuar, no salir de la carpeta) en al menos 9 de 10 turnos de prueba en cada herramienta.
  3. Una persona publica desde una computadora sin nada instalado, en Mac y en Windows, con el hosting gratuito y con la página pública de Claude, siguiendo solo instrucciones escritas.
