---
version: "2026-09-29"
titulo: "Tus permisos"
estado: borrador
# Borrador para aprobación del autor y revisión de un abogado antes del lanzamiento (research §16).
# Es la versión argentina (Ley 25.326) de la instalación del autor: si forkeás, adaptala a tu país,
# tu responsable y tus proveedores. No es asesoramiento legal.
# Textos cortos de las casillas de la inscripción. mails_curso y transferencia son obligatorias;
# novedades es opcional y va desmarcada por defecto (FR-002). La casilla de novedades se muestra
# solo si NEWSLETTER_NOMBRE tiene valor; si está vacío, el backend saca los bloques de newsletter.
# {{AUTOR}} y {{NEWSLETTER}} los reemplaza el backend (AUTOR_NOMBRE y NEWSLETTER_NOMBRE).
# Los bloques de aprobación se muestran solo con APROBACION_MANUAL=true (quien administra aprueba cada
# inscripción; ver privacidad.md).
# El proveedor del servidor está en Brasil según el registro RIPE de su IP (ver privacidad.md).
mails_curso: "Acepto recibir los mails del curso: el acceso, un solo recordatorio si me quedo a mitad de camino y uno cuando registre mi página por primera vez. Me puedo dar de baja cuando quiera. Obligatorio para hacer el curso."
transferencia: "Acepto que mis datos pasen por los proveedores que hacen andar el curso: Anthropic (el tutor), Google (la voz), Resend (los mails) y Cloudflare (el control anti-robots), en Estados Unidos, y Hostinger (el servidor), en Brasil. Esos países no tienen, para la autoridad argentina, una protección de datos adecuada. Obligatorio: sin esto el curso no funciona."
novedades: "Quiero recibir las novedades que {{AUTOR}} publica en {{NEWSLETTER}}. Mi mail se suma a esa lista, que puede estar fuera de la Argentina. Es opcional y lo puedo cambiar cuando quiera."
---

Para inscribirte te pedimos tus permisos, cada uno por separado. Acá está qué significa cada uno. El detalle completo está en el aviso de privacidad.

{{#APROBACION}}
## Tu pedido de acceso

En este curso, quien lo administra aprueba cada inscripción. Cuando verificás tu mail, tu cuenta queda pendiente hasta que se apruebe: mientras tanto no usa el tutor ni la voz, y el mail de bienvenida te llega recién cuando se aprueba. Si tu pedido no se aprueba, tus datos se borran: quien administra el curso lo puede rechazar y borrarlo a mano, y si nadie lo aprueba, se borra solo a los 90 días.

{{/APROBACION}}
## Mails del curso (obligatorio)

El curso te manda tres mails como mucho: la bienvenida con el acceso{{#APROBACION}} (cuando se aprueba tu pedido){{/APROBACION}}, un solo recordatorio si guardaste tu idea y no seguiste, y uno cuando registres tu página por primera vez. Si después registrás otro link, no te llega otro mail. Son el único contacto del curso con vos, por eso este permiso es obligatorio para inscribirte.

Cada mail trae un link para darte de baja. La baja no te saca del curso: seguís entrando con tu mail, y los mails con el código para entrar te siguen llegando cada vez que los pedís. Si te arrepentís, desde "Mis datos" te podés volver a dar de alta.

## Proveedores fuera de la Argentina (obligatorio)

El curso funciona con proveedores de otros países. Anthropic hace andar al tutor, Google la voz, Resend el envío de los mails y Cloudflare el control que frena a los robots en la inscripción, cuando esté activado; los cuatro están en Estados Unidos. La base de datos del curso está en un servidor de Hostinger ubicado en Brasil.

Ni Estados Unidos ni Brasil figuran en la lista de países con una protección de datos adecuada que publica la autoridad argentina. Por eso la ley pide tu permiso expreso para que tus datos pasen por ahí. Sin este permiso el tutor, la voz y los mails no funcionan, y no podemos darte el curso.

Si más adelante no querés que tus datos sigan pasando por estos proveedores, borrá tus datos desde "Mis datos".

## Tu página en la galería (opcional, cuando la registres)

Esto no se elige al inscribirte, sino al registrar tu página. Ahí vas a poder elegir dos cosas, las dos desmarcadas: mostrarla en la galería del curso y que {{AUTOR}} la use en su contenido. La galería muestra el título y el link, sin tu mail ni tu nombre, y tu página aparece recién cuando el curso la revisa y la aprueba. Desde "Mis datos" podés sacarla de la galería, cambiar lo que elegiste sobre el uso de tu página como contenido o borrar el link, cuando quieras.

{{#NEWSLETTER}}
## Novedades (opcional)

Las novedades que publica {{AUTOR}} llegan por {{NEWSLETTER}}. Si marcás esta casilla, tu mail se suma a esa lista. {{NEWSLETTER}} puede estar fuera de la Argentina y tiene su propio aviso de privacidad. Es opcional: si no la marcás, no pasa nada con tu curso.

La podés cambiar cuando quieras desde "Mis datos". Los mails se suman a {{NEWSLETTER}} a mano, de vez en cuando: si ya te llegan las novedades, para dejar de recibirlas date de baja también desde cualquier mail de {{NEWSLETTER}}.
{{/NEWSLETTER}}
