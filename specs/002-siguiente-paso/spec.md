# Feature Specification: Siguiente paso al terminar el curso

**Feature Branch**: `002-siguiente-paso`

**Created**: 2026-09-28

**Status**: Draft

**Input**: User description: "Que quien termine el curso pueda enterarse de un siguiente paso: al registrar su link, la web pregunta si tiene un negocio que ya vende y, si dice que sí, le ofrece que le avisen cuando abra un curso nuevo del autor. Sin precio, con un permiso propio, configurable y apagado por defecto." Definido con Andrés el 28/9/2026. En su instalación, el siguiente paso es un curso pago que abre más adelante; este spec no lo describe.

## Clarifications

### Session 2026-09-28

- Q: ¿"Mis datos" muestra la fecha del aviso? → A: No en la pantalla, igual que el permiso de novedades: muestra si está prendido y la fecha viaja en la descarga (ajuste durante la implementación).
- Q: ¿Cuándo cuenta un "sí"? → A: Al confirmar. Quien toca "Sí" y se va sin confirmar no suma y no vuelve a ver la pregunta, igual que con "Ahora no".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enterarse del siguiente paso al terminar (Priority: P1)

La primera vez que el alumno registra el link de su idea (FR-023 del spec 001; en la práctica, al final del curso, porque la lección 7 lo manda a registrarlo), la web le hace una pregunta corta: si tiene un negocio que ya vende. Si contesta que sí, ve un texto breve que cuenta que hay un siguiente paso y le ofrece que le avisen cuando abra, con una casilla desmarcada. Si contesta que no, o no contesta, el curso termina como hoy.

**Why this priority**: es lo único que ve el alumno y la razón de la función. Sin esto no hay nada que medir.

**Independent Test**: con la función prendida y en modo demo, registrar un primer link, contestar "sí", marcar la casilla y comprobar que el pedido de aviso quedó guardado con su fecha.

**Acceptance Scenarios**:

1. **Given** la función prendida y un alumno que registra su primer link, **When** confirma el registro, **Then** ve la pregunta "¿Tenés un negocio que ya vende?" con las respuestas "sí" y "no" y puede cerrarla sin contestar.
2. **Given** que contestó "sí", **When** ve el texto del siguiente paso, **Then** la casilla de aviso aparece desmarcada, el texto no muestra precios y puede seguir sin marcarla.
3. **Given** que marcó la casilla, **When** confirma, **Then** queda guardado su pedido de aviso con fecha y con la versión del texto que aceptó, separado de los demás permisos.
4. **Given** que contestó "no" o cerró la pregunta, **When** sigue, **Then** no ve el texto del siguiente paso y el curso termina igual que hoy.
5. **Given** la función apagada, que es el valor por defecto, **When** registra su primer link, **Then** no ve ni la pregunta ni el texto.
6. **Given** un alumno que ya registró un link, **When** registra otro o cambia uno, **Then** no se le vuelve a preguntar.

---

### User Story 2 - Manejar el aviso desde "Mis datos" (Priority: P2)

El alumno ve en "Mis datos" si pidió el aviso y lo puede sacar en un clic. El aviso viaja en la descarga de sus datos y se borra con todo lo demás.

**Why this priority**: sin esto, el aviso rompe la promesa del curso de que cada persona controla sus datos (principio III).

**Independent Test**: pedir el aviso, sacarlo desde "Mis datos" y comprobar que ya no cuenta; descargar los datos y ver el aviso; borrar todo y comprobar que no queda.

**Acceptance Scenarios**:

1. **Given** un alumno que pidió el aviso, **When** entra a "Mis datos", **Then** ve que lo tiene prendido y lo puede sacar. La fecha viaja en la descarga, como la de los demás permisos.
2. **Given** la función prendida y un alumno sin aviso, **When** entra a "Mis datos", **Then** lo puede pedir desde ahí, aunque no haya contestado la pregunta.
3. **Given** que sacó el aviso, **When** el autor mira el reporte, **Then** ya no cuenta como aviso activo.
4. **Given** que descarga sus datos, **When** abre el archivo, **Then** aparece el estado del aviso con sus fechas.
5. **Given** que borra todos sus datos, **When** termina el borrado, **Then** no queda el aviso.

---

### User Story 3 - Los números para el autor (Priority: P3)

El autor ve en su reporte cuántos alumnos contestaron la pregunta, cuántos dijeron que tienen un negocio que ya vende y cuántos tienen el aviso activo. Con eso decide si el siguiente paso tiene demanda antes de construirlo.

**Why this priority**: es la medición que justifica la función, pero el alumno no la ve y puede llegar después de las historias 1 y 2.

**Independent Test**: con alumnos de prueba que contestan de distintas formas y uno que saca el aviso, el reporte muestra los tres números correctos.

**Acceptance Scenarios**:

1. **Given** alumnos que contestaron "sí", "no" o nada, y algunos con aviso, **When** el autor abre el reporte, **Then** ve los tres números y cada uno coincide con los datos.
2. **Given** la función prendida con algún texto sin configurar, **When** el autor abre el reporte, **Then** ve un aviso de que la función está inactiva por falta de textos.

---

### Edge Cases

- **Varios links:** un alumno puede registrar hasta cinco. La pregunta aparece solo después del primero, aunque después lo borre y registre otro.
- **Función prendida sin todos los textos:** se comporta como apagada y el reporte lo avisa (FR-001).
- **Función apagada después de que hubo pedidos:** la pregunta deja de aparecer; los avisos que ya existen siguen visibles en "Mis datos", se pueden sacar y siguen contando en el reporte.
- **Cambia el texto del permiso:** los avisos anteriores conservan el texto que cada persona aceptó.
- **Alumnos que registraron su link antes de prender la función:** no ven la pregunta ni reciben nada; pueden pedir el aviso desde "Mis datos" si entran.
- **Alumno que se da de baja de los mails del curso:** conserva su aviso hasta que lo saque; el aviso es un permiso aparte.
- **Modo demo:** la función anda igual, para poder probarla sin claves.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La función MUST venir apagada por defecto y prenderse solo por la configuración de cada instalación, junto con sus tres textos: la pregunta, el texto del siguiente paso y el texto del permiso de aviso. Si está prendida pero falta alguno, MUST comportarse como apagada y el reporte del autor MUST decirlo.
- **FR-002**: Con la función prendida, después de que el alumno registra su primer link (FR-023 del spec 001), la web MUST preguntarle una sola vez si tiene un negocio que ya vende, con las respuestas "sí" y "no" y la opción de no contestar.
- **FR-003**: Solo si contesta "sí", la web MUST mostrar el texto del siguiente paso con una casilla de aviso desmarcada por defecto. Ni la pregunta ni el texto MUST mostrar precios.
- **FR-004**: El pedido de aviso MUST guardarse como un permiso propio, separado de los permisos de la inscripción y de las novedades, con su fecha y la versión del texto que la persona aceptó, igual que los demás permisos.
- **FR-005**: Contestar, no contestar o no pedir el aviso MUST NOT cambiar nada más del curso: el registro del link, la galería, los mails y el avance siguen igual.
- **FR-006**: En "Mis datos", el alumno MUST poder ver y sacar el aviso en todo momento, y pedirlo mientras la función esté prendida. El aviso MUST viajar en la descarga de sus datos y borrarse con el resto (FR-030 del spec 001).
- **FR-007**: El reporte del autor (FR-027 del spec 001) MUST mostrar cuántos alumnos contestaron la pregunta, cuántos dijeron que tienen un negocio y cuántos tienen el aviso activo.
- **FR-008**: La lista de avisos MUST NOT copiarse fuera del sistema del curso ni exportarse (FR-031 del spec 001). El aviso, cuando corresponda, sale desde el mismo sistema.
- **FR-009**: Lo propio de cada instalación (qué es el siguiente paso y cómo se cuenta) MUST vivir en su configuración. El texto legal del permiso es genérico, vive con los demás textos legales y solo aparece con la función prendida. El repo trae la función apagada.
- **FR-010**: La función MUST NOT aparecer en el kit ni en las lecciones.
- **FR-011**: La función MUST NOT llamar al tutor ni a ningún servicio pago (principio II).
- **FR-012**: La respuesta sobre el negocio MUST contarse sin guardar quién contestó: solo decide si se muestra el texto del siguiente paso y suma a los números del autor (principio III).
- **FR-013**: Con la función prendida, el aviso de privacidad y los textos de los permisos MUST describir el nuevo permiso: para qué es, que es opcional y cómo sacarlo.

### Key Entities *(include if feature involves data)*

- **Respuesta sobre el negocio**: se cuenta de forma anónima, cuántos "sí" y cuántos "no" con su fecha; no queda asociada al alumno.
- **Pedido de aviso**: permiso propio del alumno, con fecha de alta, fecha de baja si lo sacó y la versión del texto que aceptó. Activo o retirado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con la función apagada, el recorrido de un alumno que termina el curso es idéntico al del spec 001.
- **SC-002**: Contestar la pregunta y decidir el aviso le lleva al alumno menos de 30 segundos.
- **SC-003**: El 100% de los pedidos de aviso se pueden ver, sacar, descargar y borrar desde "Mis datos".
- **SC-004**: Ningún alumno ve el texto del siguiente paso sin haber contestado "sí".
- **SC-005**: El autor lee los tres números en su reporte sin consultas a mano.
- **SC-006**: En el piloto, ninguna de las personas que ven la pregunta dice haber sentido que el curso le quiso vender algo.

## Assumptions

- El siguiente paso lo define cada instalación; este spec no lo describe ni le pone precio.
- Mandar el aviso cuando el siguiente paso abre queda fuera de alcance: se construye junto con ese siguiente paso, desde el mismo sistema del curso, nunca exportando la lista.
- La respuesta sobre el negocio es autodeclarada y no se verifica.
- La función usa lo que ya existe del spec 001: los permisos, "Mis datos", el reporte del autor y la configuración por instalación.
- Para no ampliar los datos que guarda el curso (principio III), la respuesta sobre el negocio no se guarda con el alumno.
- **Dependencia:** el principio I de la constitución dice "El curso acompaña: no vende". Ofrecer un siguiente paso, aunque sea sin precio y con permiso propio, necesita una enmienda aprobada por Andrés antes del plan. Propuesta (MINOR, amplía el principio): "El curso no vende ni diagnostica. Al terminar, una instalación puede ofrecer un siguiente paso, apagado por defecto, sin precios y con un permiso propio".
