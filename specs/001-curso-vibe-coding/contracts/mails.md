# Contrato: mails del curso

**Fecha**: 2026-09-28 · Proveedor: Resend (el mismo del proyecto anterior) · Remitente: un
subdominio del dominio propio del curso (`curso.example.com` en estos documentos), verificado en
Resend.

Todos los textos van en voseo, sin emojis, en texto plano y HTML simple. Los textos viven en
`contenido/mails/*.md` y los aprueba Andrés como el resto del contenido.

## Mails

| Tipo | Disparador | Destinatario | Frecuencia | Baja |
|---|---|---|---|---|
| Código de acceso | `POST /auth/codigo` | quien lo pide | con los límites de FR-003 | no (transaccional) |
| `bienvenida` | primera verificación del alumno | alumno | una vez en la vida | sí |
| `recordatorio` | tarea periódica: alumno en el módulo 3 o más (`modulo_actual >= 3`), idea guardada, sin kit descargado y 3 días desde la última versión de la idea | alumno con `mails_curso = 1` | una vez en la vida | sí |
| `contame` | `POST /links`, con el primer link que el alumno registra teniendo los mails aceptados | alumno con `mails_curso = 1` | una vez en la vida (clave `contame`) | sí |
| `aviso_80` | tarea periódica: gasto del mes ≥ 80% del tope | Andrés (`ADMIN_EMAIL`) | una vez por mes | no |

Cada alumno recibe como mucho tres mails del curso en toda su vida: `bienvenida`, `recordatorio`
y `contame`, cada uno una sola vez (así se cumple lo que dicen los textos legales). La clave de
cada mail en la tabla `mails` es su tipo (`bienvenida`, `recordatorio`, `contame`); `aviso_80`
usa `aviso_80:<AAAA-MM>`.

### Contame, una sola vez

- `POST /links` responde `{"id", "mail"}`: `mail` es `true` si el alumno acepta los mails del curso
  y nunca se le mandó un contame (`mails.contame_pendiente`). Solo en ese caso encola el envío,
  con la URL y el título del link recién registrado.
- `mails.enviar(..., "contame", "contame")` no manda nada (`omitido`) si ya hay un contame
  `enviado` para ese alumno con cualquier clave (incluidas las viejas `contame:<id>` de antes del
  28/9/2026) o si el alumno no tiene ningún link registrado (por ejemplo, porque lo borró).
- Si el envío falla, el reintento de la tarea periódica usa la misma clave y toma de la base el
  último link del alumno. Un contame que quedó `fallido` cuenta como pendiente: el próximo link lo
  vuelve a intentar.

## Contenido mínimo de cada mail

- **Código**: el código de 6 dígitos, que vence en 10 minutos y "si no lo pediste, ignorá este
  mail". Sin links de seguimiento.
- **Bienvenida**: el link para entrar, qué hay en el curso en tres líneas y cómo darse de baja.
- **Recordatorio**: dónde quedó ("tu idea está lista; el paso que sigue es armar tu taller"), el
  link directo al módulo 3 y la baja.
- **Contame**: una pregunta abierta ("contame qué hiciste y cómo te fue"); se responde al mail. Si
  el alumno no marcó `uso_contenido`, el mail no le pide permiso de nuevo.
- **Aviso 80%**: gasto del mes, tope, alumnos activos en el mes y el link al reporte.

## Pie legal (Ley 25.326)

Los mails `bienvenida`, `recordatorio` y `contame` llevan al pie, de forma destacada, cómo darse de
baja y la transcripción del art. 27 inc. 3 de la Ley 25.326 y del art. 27 párrafo 3 del Decreto
1558/2001, como pide la Disposición 4/2009 para los mails que pueden considerarse publicitarios. El
texto exacto vive en `contenido/legal/pie-mails.md` y lo revisa el abogado junto con el aviso de
privacidad (research §16).

## Baja (FR-025)

- Cada mail del curso lleva un link de baja con un token firmado y las cabeceras
  `List-Unsubscribe` y `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058) apuntando a
  `/api/baja`. El token es `<alumno_id>.<firma>`, donde la firma es HMAC-SHA256 con el secreto del
  servidor (`JWT_SECRET`) sobre `baja:<alumno_id>` (propósito `baja`, en base64url sin relleno). El
  propósito va dentro de lo firmado para que la firma no sirva para otra cosa; no depende del tipo
  de mail y no vence.
- La baja en un clic la hacen los servidores del proveedor de mail, que no mandan la cabecera
  `Sec-Fetch-Site`: el anti CSRF de la API (ver [api.md](api.md)) no la frena.
- La baja agrega `mails_curso = 0` al historial de consentimientos y registra el evento
  `baja_mails`. Los códigos de acceso se siguen mandando, porque los pide el propio alumno.
- Un alumno dado de baja puede volver a darse de alta desde "Mis datos".

## Fallas

- Si Resend falla, el mail queda como `fallido` en la tabla `mails` y la tarea periódica lo
  reintenta hasta 3 veces en 24 horas (a los 15 minutos, a las 2 horas y a las 12 horas del primer
  intento). El reintento pasa por las mismas reglas: si mientras tanto el alumno se dio de baja,
  borró sus datos o ya recibió un contame, no sale. El código de acceso no se reintenta: el alumno
  lo vuelve a pedir.
- Nunca se reenvía un mail ya `enviado` con la misma `clave`.
