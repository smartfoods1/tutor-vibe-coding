---
version: "2026-09-29"
titulo: "Aviso de privacidad"
estado: borrador
# Borrador para aprobación del autor y revisión de un abogado antes del lanzamiento (research §16).
# {{AUTOR}} y {{NEWSLETTER}} los reemplaza el backend (AUTOR_NOMBRE y NEWSLETTER_NOMBRE).
# Los bloques de aprobación se muestran solo con APROBACION_MANUAL=true (quien administra aprueba cada
# inscripción; los pedidos que nadie aprueba se borran a los 90 días, decisión del autor del 29/9/2026).
# Cubre lo que pide el art. 6 de la Ley 25.326 y la leyenda del art. 3 de la Resolución AAIP 14/2018.
# Fuentes (consultadas el 2026-09-28):
# - Ley 25.326, arts. 5, 6, 7, 12, 14 y 16 (texto actualizado en InfoLEG):
#   https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm
# - Decreto 1558/2001, Anexo I, art. 12 (el consentimiento expreso habilita la transferencia a países
#   sin protección adecuada): https://servicios.infoleg.gob.ar/infolegInternet/anexos/70000-74999/70368/norma.htm
# - Resolución AAIP 14/2018, arts. 2 y 3 (información del art. 6 visible antes de recolectar y texto
#   textual de la leyenda; deroga la Disposición 10/2008):
#   https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-14-2018-307621/texto
# - Países con legislación adecuada: Disposición DNPDP 60-E/2016, art. 3, y Resolución AAIP 34/2019
#   (suma al Reino Unido). No incluyen a Estados Unidos ni a Brasil:
#   https://www.argentina.gob.ar/normativa/nacional/norma-267922/texto
#   https://www.argentina.gob.ar/normativa/nacional/norma-320275/texto
# - Ubicación del servidor: servidor de Hostinger en Brasil, según el registro RIPE de su IP,
#   consultado el 2026-09-28. Conviene confirmarlo en el panel de Hostinger.
# - Plazos de conservación: data-model.md (Retención y borrado) y la decisión del autor del 28/9/2026.
# Pendiente: si el curso admite menores de edad (no está definido); revisión de un abogado.
---

<!--
Este aviso es el borrador para Argentina (Ley 25.326) de la instalación del autor. No es
asesoramiento legal: adaptalo a tu país, tu responsable y tus proveedores.
Las partes marcadas como bloque de newsletter se muestran solo si la instalación tiene
newsletter (NEWSLETTER_NOMBRE); si no, el backend las saca. Las marcadas como bloque de
aprobación se muestran solo si quien administra aprueba cada inscripción (APROBACION_MANUAL).
-->

Este aviso explica qué datos tuyos guarda el curso, para qué, con quién se comparten, cuánto tiempo se guardan y cómo podés verlos, descargarlos o borrarlos. Leelo antes de inscribirte.

## Quién es responsable de tus datos

Los datos del curso forman una base de datos propia del curso.

**Responsable y domicilio:** [A completar antes del lanzamiento: responsable y domicilio]

**Contacto para consultas sobre tus datos:** [A completar antes del lanzamiento: un mail para consultas sobre datos personales]

**Inscripción en el Registro Nacional de Bases de Datos:** [A completar antes del lanzamiento: número de inscripción]

## Para qué usamos tus datos

- Darte acceso al curso con un código que te llega por mail, sin contraseña.
- Que el tutor te acompañe en los módulos 1 a 3 y retome donde quedaste.
- Guardar tu idea y tu avance, y armar tu carpeta del curso con tu idea adentro.
- Mandarte los mails del curso, tres como mucho: la bienvenida{{#APROBACION}} (cuando se aprueba tu pedido de acceso){{/APROBACION}}, un solo recordatorio si te quedás a mitad de camino y uno cuando registres tu página por primera vez.
{{#NEWSLETTER}}
- Si lo aceptás, sumarte a la lista de {{NEWSLETTER}} donde {{AUTOR}} publica sus novedades.
{{/NEWSLETTER}}
- Si registrás tu página y lo elegís, mostrarla en la galería del curso (recién cuando el curso la revisa y la aprueba) o que {{AUTOR}} la use en su contenido.
- Saber cómo funciona el curso con números generales (cuántas personas se inscriben, terminan cada módulo, bajan su carpeta y registran un link) y controlar lo que cuesta el tutor.
- Frenar abusos, como pedidos de códigos en masa.

No vendemos tus datos ni los usamos para publicidad de otros. Tus datos no salen del sistema del curso, salvo en los casos que se explican más abajo.

{{#APROBACION}}
## Tu pedido de acceso

En este curso, quien lo administra aprueba cada inscripción. Cuando verificás tu mail, tu cuenta queda como un pedido de acceso pendiente, con tu mail, de dónde llegaste y los permisos que diste.

- Mientras tu pedido está pendiente, tu cuenta no usa el tutor ni la voz, así que no se manda nada tuyo a Anthropic ni a Google. Desde "Mis datos" igual podés ver, descargar o borrar lo que guardamos.
- El mail de bienvenida te llega cuando se aprueba tu pedido.
- Si tu pedido no se aprueba, tus datos se borran: quien administra el curso lo puede rechazar y borrarlo a mano, y si nadie lo aprueba, se borra solo a los 90 días de tu inscripción.

{{/APROBACION}}
## Qué datos guardamos

- Tu mail.
- De dónde llegaste al curso, si el link por el que entraste lo indica.
- Los permisos que diste o sacaste, con su fecha y la versión del texto que aceptaste.
{{#APROBACION}}
- Si tu pedido de acceso está pendiente o ya se aprobó.
{{/APROBACION}}
- Tu avance: qué módulos terminaste, cuándo, y un resumen corto de cada módulo que escribe el tutor, sin datos personales ni de salud.
- Tu idea en una página y lo que quedó para "qué sigue", con todas sus versiones.
- Tus conversaciones con el tutor: lo que escribís o dictás y lo que te responde.
- La herramienta y el tipo de computadora que elegiste, y cada vez que bajaste tu carpeta del curso.
- Los links que registres, lo que elegiste sobre mostrarlos y si el curso aprobó que aparezcan en la galería.
- Qué mails del curso te mandamos.
- Datos técnicos: lo que cuesta cada respuesta del tutor y la dirección IP desde la que pedís un código, para frenar abusos.

Lo que no guardamos:

- Las capturas de pantalla: se usan solo para responderte en ese momento.
- El audio de tu voz cuando dictás: se pasa a texto y no se guarda.
- Contraseñas: el curso no las usa, y el tutor nunca te va a pedir una.

## Qué es obligatorio y qué pasa si no lo das

- **Tu mail es obligatorio.** Sin mail no te podemos mandar el código para entrar. Si está mal escrito, el código no te llega.
- **Aceptar los mails del curso es obligatorio para inscribirte.** Son el único contacto del curso con vos. Después te podés dar de baja cuando quieras, sin perder el curso.
- **Aceptar que tus datos pasen por proveedores fuera de la Argentina es obligatorio.** Sin eso, el tutor, la voz y los mails no funcionan, y no podemos darte el curso. Está explicado más abajo.
{{#NEWSLETTER}}
- **Recibir las novedades que publica {{AUTOR}} es opcional.** Si no lo aceptás, no pasa nada con tu curso.
{{/NEWSLETTER}}
- **Mostrar tu página en la galería o dejar que {{AUTOR}} la use en su contenido es opcional.** Las dos opciones vienen desmarcadas, y las podés cambiar después desde "Mis datos".
- **Todo lo que le contás al tutor es voluntario.** Nadie puede obligarte a dar datos sensibles, como los de tu salud. No hace falta que cuentes datos de salud ni datos de otras personas. Si los contás, el tutor no los pone en tu idea ni en los resúmenes, pero quedan en la conversación hasta que se borra (ver los plazos más abajo).

## Con quién se comparten

Estos proveedores hacen andar el curso y reciben datos solo para eso:

- **Anthropic** (Estados Unidos): el modelo de inteligencia artificial del tutor. Recibe lo que escribís, las capturas que mandás, tu idea y el resumen de tu avance, para poder responderte.
- **Google** (Estados Unidos): la voz. Recibe el audio cuando dictás, para pasarlo a texto, y las respuestas del tutor cuando elegís escucharlas.
- **Resend** (Estados Unidos): el envío de los mails. Recibe tu mail y el texto de cada mail.
- **Cloudflare** (Estados Unidos): el control que frena a los robots en la inscripción, cuando esté activado. Recibe datos técnicos de tu navegador y tu dirección IP.
- **Hostinger** (empresa con sede en Lituania): el servidor donde vive la base del curso, que está en Brasil.

Cada proveedor puede guardar por un tiempo lo que recibe, según sus propias condiciones.

Solo si lo aceptás:

{{#NEWSLETTER}}
- **{{NEWSLETTER}}** (puede estar fuera de la Argentina): tu mail se suma a la lista donde {{AUTOR}} publica sus novedades. Desde ahí te podés dar de baja cuando quieras, y {{NEWSLETTER}} tiene su propio aviso de privacidad.
{{/NEWSLETTER}}
- **La galería del curso:** si elegís mostrar tu página, el curso la revisa antes de publicarla ahí, y aparece recién cuando la aprueba. Se ven el título y el link, sin tu mail ni tu nombre.
- **El contenido del autor:** si lo aceptás, {{AUTOR}} puede mostrar tu página en su contenido, sin tu mail.

Quien administra el curso puede acceder a la base para mantenerla, resolver problemas y ver los números generales del curso.

## Tus datos fuera de la Argentina

Estados Unidos y Brasil no figuran en la lista de países con un nivel de protección de datos adecuado que publica la autoridad argentina. Por eso, antes de inscribirte, te pedimos un permiso expreso y separado para que tus datos pasen por esos proveedores (Ley 25.326, artículo 12, y Decreto 1558/2001, artículo 12). Sin ese permiso no podemos darte el curso. Si más adelante no querés que tus datos sigan pasando por ellos, borrá tus datos desde "Mis datos".

## Cuánto tiempo guardamos tus datos

- **Conversaciones con el tutor:** se borran 30 días después de que terminás el módulo. Las de un módulo que no terminaste, 12 meses después de tu última actividad en el curso. Queda solo el resumen del módulo, sin datos personales ni de salud.
- **Tu idea, tu avance, tus links y tus permisos:** hasta que los borres.
{{#APROBACION}}
- **Pedidos de acceso que no se aprueban:** se borran cuando quien administra el curso los rechaza o, si nadie los aprueba, a los 90 días de la inscripción.
{{/APROBACION}}
- **Códigos de acceso y la dirección IP desde la que los pediste:** se borran a las 24 horas.
- **Capturas y audio de tu voz:** no se guardan.
- **Registros técnicos del servidor:** [A confirmar en el despliegue: cuánto tiempo guarda el servidor sus registros técnicos, como las direcciones IP de las visitas]

Cuando borrás tus datos, se borra todo lo tuyo y dejás de recibir mails. Quedan, sin ningún dato que te identifique, el costo de uso del tutor y los números generales del curso (por ejemplo, "una persona se inscribió").

## Cookies

El curso usa una sola cookie propia, "__Host-vibe_sesion", para mantener tu sesión abierta durante 30 días. No usa cookies de publicidad ni de seguimiento. Cuando esté activado, el control anti-robots de Cloudflare usa datos técnicos de tu navegador para verificar que no sos un robot.

## Tus derechos y cómo ejercerlos

- **Acceso:** desde "Mis datos" podés ver y descargar todos tus datos, cuando quieras y sin costo. La ley te garantiza el acceso gratuito a intervalos no menores a seis meses, salvo que acredites un interés legítimo para pedirlo antes; si lo pedís por el contacto de arriba, la respuesta tiene que llegar dentro de los diez días corridos.
- **Rectificación:** tu idea la corregís vos desde la web. Si otro dato está mal, pedilo por el contacto de arriba.
- **Supresión:** desde "Mis datos" podés borrar todos tus datos. Si lo pedís por el contacto de arriba, se hace dentro de los cinco días hábiles.
- **Sacar un permiso:** te das de baja de los mails con el link que va al pie de cada mail o desde "Mis datos", y ahí mismo podés volver a darte de alta. {{#NEWSLETTER}}El permiso para las novedades lo cambiás desde "Mis datos"; si ya te llegan, date de baja también desde cualquier mail de {{NEWSLETTER}}, porque tu mail ya está en esa lista. {{/NEWSLETTER}}Lo que elegiste al registrar tu página (la galería y el uso como contenido) también lo cambiás desde "Mis datos", donde podés sacar un link de la galería o borrarlo.

LA AGENCIA DE ACCESO A LA INFORMACIÓN PÚBLICA, en su carácter de Órgano de Control de la Ley N° 25.326, tiene la atribución de atender las denuncias y reclamos que interpongan quienes resulten afectados en sus derechos por incumplimiento de las normas vigentes en materia de protección de datos personales.

## Cambios a este aviso

Si este aviso cambia, cambian la versión y la fecha. Si cambia algo de lo que aceptaste, te lo vamos a volver a pedir.
