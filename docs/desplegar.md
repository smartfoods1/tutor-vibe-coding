# Desplegar el curso en tu servidor

Esta guía te lleva de un servidor vacío al curso funcionando con HTTPS en tu dominio. Son dos
scripts: `deploy/preparar-servidor.sh`, que corre una sola vez en el servidor, y
`deploy/desplegar.sh`, que corre desde tu compu cada vez que querés publicar cambios.

## Cómo queda armado

```text
Internet ──HTTPS──> nginx (puertos 80 y 443, certificado de Let's Encrypt)
                     ├── /            frontend compilado      /var/www/vibe-tutor/
                     ├── /audios/     audios de los módulos   /srv/vibe-tutor/contenido/audios/
                     └── /api/  ───>  servicio vibe-tutor (uvicorn en 127.0.0.1:8340)
                                        ├── código       /opt/vibe-tutor/ (con su .venv)
                                        ├── contenido    /srv/vibe-tutor/contenido/
                                        ├── base SQLite  /srv/vibe-tutor/data/vibe.db
                                        └── config       /etc/vibe-tutor/.env
```

El servicio corre con su propio usuario de sistema (`vibe-tutor`), sin permisos de escritura fuera
de `/srv/vibe-tutor/data` y con topes de memoria y CPU para no afectar a otros servicios del
servidor. Los scripts no tocan otros sitios de nginx ni otros servicios: `desplegar.sh` compara la
lista de servicios antes y después, y corta si cambió.

## Requisitos

**Servidor**

- Linux con systemd y apt. Probado en Ubuntu 24.04, que ya trae Python 3.12 (en otras versiones
  instalá Python 3.12 antes).
- 1 GB de RAM alcanza para empezar (el servicio tiene un tope de 512 MB).
- Acceso por SSH con clave, como root o con un usuario con sudo sin contraseña.
- Puertos 80 y 443 abiertos.

**Tu compu**

- bash, ssh, scp, rsync, curl y git.
- El entorno de desarrollo andando (Python con `backend/.venv` y Node): `desplegar.sh` corre los
  tests y compila el frontend antes de subir nada. Ver [desarrollo-local.md](desarrollo-local.md).

## 1. DNS

En el panel de tu dominio, creá un registro `A` para el subdominio del curso (por ejemplo
`curso.tudominio.com`) que apunte a la IP del servidor, y un `AAAA` si el servidor tiene IPv6.
Comprobalo antes de seguir:

```bash
dig +short curso.tudominio.com
```

Tiene que devolver la IP del servidor. Sin esto, certbot no puede emitir el certificado.

## 2. Cuentas y claves

Usá cuentas y claves propias del curso, y ponele a cada una un límite de gasto en su panel: es la
segunda barrera, además de los topes del propio curso.

| Servicio | Para qué | Qué necesitás |
|---|---|---|
| [Anthropic](https://console.anthropic.com) | El tutor de la web (Claude) | Una API key (`ANTHROPIC_API_KEY`) y un límite de gasto mensual en la consola |
| [Google AI Studio](https://aistudio.google.com) | Dictado y voz del tutor (Gemini) | Una API key (`GEMINI_API_KEY`) de un proyecto con facturación y límite de gasto |
| [Resend](https://resend.com) | Códigos de acceso y mails del curso | Un dominio verificado (conviene un subdominio, como `mail.tudominio.com`, con los registros DNS que te da Resend) y una API key con permiso de envío (`RESEND_API_KEY`). El remitente (`MAIL_FROM`) tiene que ser de ese dominio |
| [Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/) | Antibots en la inscripción. Opcional pero recomendado | Un widget para el dominio del curso: te da la site key (`TURNSTILE_SITE_KEY`) y la secret key (`TURNSTILE_SECRET`) |

Sin Turnstile el curso funciona, pero cualquiera puede pedir códigos de acceso (siguen los límites
por mail, por IP y por día). En producción conviene activarlo.

## 3. Datos del despliegue en tu compu

```bash
cp deploy/despliegue.env.example deploy/despliegue.env
```

Completá `deploy/despliegue.env` (git lo ignora):

```bash
VIBE_SERVIDOR=root@tu-servidor
VIBE_DOMINIO=curso.tudominio.com
```

En `VIBE_SERVIDOR` va `usuario@servidor`, con la IP o el nombre del servidor, o un alias de
`~/.ssh/config`. También podés exportar esas dos variables en la terminal: pisan a las del archivo.

## 4. Preparar el servidor (una sola vez)

Desde la raíz del repo, en tu compu:

```bash
set -a; . deploy/despliegue.env; set +a
ssh "$VIBE_SERVIDOR" "mkdir -p vibe-tutor-preparar"
scp deploy/preparar-servidor.sh deploy/.env.example deploy/vibe-tutor.service "$VIBE_SERVIDOR:vibe-tutor-preparar/"
ssh -t "$VIBE_SERVIDOR" "sudo bash vibe-tutor-preparar/preparar-servidor.sh $VIBE_DOMINIO"
```

Si entrás como root y el servidor no tiene sudo, sacá el `sudo`. El script:

1. Instala lo que falte: nginx, certbot con su complemento para nginx, ffmpeg, rsync y Python 3.12.
2. Crea el usuario de sistema `vibe-tutor` y las carpetas de la sección anterior.
3. Crea `/etc/vibe-tutor/.env` a partir de `deploy/.env.example`, con permisos 640, y completa solo
   `JWT_SECRET` (con `openssl rand -hex 32`), `DOMINIO`, `DATA_DIR` y `CONTENIDO_DIR`. No lee
   claves de ningún otro lado.
4. Crea el entorno de Python en `/opt/vibe-tutor/.venv` e instala el servicio de systemd (lo
   habilita y lo arranca el primer despliegue).
5. Arma un sitio de nginx provisorio, solo con el puerto 80, y corre `certbot --nginx -d
   <tu dominio>` para pedir el certificado. certbot te pregunta un mail y que aceptes sus términos.
   Si preferís que no pregunte, pasale tu mail como segundo argumento al script (con eso aceptás
   los términos de Let's Encrypt).
6. Al final te dice qué claves faltan completar.

Es idempotente: lo que ya existe queda como está. Si algo falla (por ejemplo, el DNS todavía no
apuntaba), arreglalo y volvé a correrlo. Si certbot no pudo, podés pedirlo a mano en el servidor
con `sudo certbot --nginx -d curso.tudominio.com`. La renovación del certificado es automática
(certbot deja un timer de systemd).

## 5. Completar la configuración

En el servidor:

```bash
sudo nano /etc/vibe-tutor/.env
```

Completá, como mínimo, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `RESEND_API_KEY`, `MAIL_FROM` (entre
comillas, por ejemplo `MAIL_FROM="Mi curso <hola@mail.tudominio.com>"`) y `ADMIN_EMAIL` (tu mail:
con él entrás a `/admin` y te llegan los avisos de gasto). Después, lo recomendable:
`TURNSTILE_SITE_KEY`, `TURNSTILE_SECRET`, `AUTOR_NOMBRE` y, si tenés newsletter,
`NEWSLETTER_NOMBRE`. Cada variable está explicada en [deploy/.env.example](../deploy/.env.example).

Dos que **nunca** van en producción: `MODO_DEMO=true` y `DEV_CODIGO_FIJO`.

Mientras pruebes con pocas personas, la web muestra arriba «Versión de prueba: el curso todavía no
se lanzó». El día que abras la inscripción, sumá `AVISO_PRUEBA=false` y reiniciá el servicio.

Si querés decidir a mano quién entra (por ejemplo, en un piloto chico o para que el link no se
viralice y se lleve el presupuesto), sumá `APROBACION_MANUAL=true`. Cada persona que se inscribe
queda pendiente y no usa el tutor hasta que la aprobás en `/admin`, en "Pedidos de acceso"; te
llega un mail de aviso como mucho una vez por hora. Al aprobar le sale la bienvenida; al rechazar
se borran sus datos. Los pendientes que nadie aprueba se borran solos a los 90 días.

Si al terminar el curso querés contar que viene algo más (otro curso, por ejemplo), sumá
`SIGUIENTE_PASO=true` con sus tres textos: `SIGUIENTE_PASO_NOMBRE`, `SIGUIENTE_PASO_PREGUNTA` y
`SIGUIENTE_PASO_TEXTO`. Viene apagado. Con la función prendida, después del primer link la web
pregunta si la persona tiene un negocio que ya vende y, si dice que sí, le ofrece un aviso para
cuando abra; en `/admin` ves cuántos contestaron, cuántos tienen un negocio y cuántos pidieron el
aviso. Si falta un texto, queda apagada y `/admin` te dice cuál. Qué hace cada clave y cómo cuida
los datos está en [adaptar-el-curso.md](adaptar-el-curso.md), paso 9.

Cuando cambies este archivo con el servicio andando: `sudo systemctl restart vibe-tutor`.

El nombre del curso no va en el servidor: se toma de `frontend/.env` en tu compu cuando
`desplegar.sh` compila el frontend (copiá `frontend/.env.example` y cambiá `VITE_NOMBRE_CURSO`).

## 6. Desplegar

Desde la raíz del repo, en tu compu:

```bash
deploy/desplegar.sh
```

El script:

1. Verifica que el servidor esté preparado.
2. Corre los tests del backend y del frontend, y compila el frontend. Si algo falla, no sube nada.
3. Anota los servicios que están corriendo en el servidor.
4. Sube el backend, el contenido (sin la investigación, los ejemplos ni el currículo) y el frontend
   con rsync, y anota la versión en `contenido/VERSION`.
5. Arma el sitio de nginx desde `deploy/nginx-vibe-tutor.conf.plantilla` con tu dominio y lo
   instala junto con las cabeceras de seguridad solo si cambiaron. Si la configuración nueva no
   pasa `nginx -t`, vuelve a la anterior y corta.
6. Actualiza el servicio si cambió, instala las dependencias de Python y reinicia. Espera a que la
   API conteste; si no, te muestra las últimas líneas del registro.
7. Compara la lista de servicios con la del paso 3.
8. Hace los chequeos de humo por HTTPS.

Las migraciones de la base corren solas cuando arranca el backend. Si la versión nueva suma una
migración (por ejemplo, la 5, del siguiente paso), hacé antes un backup de la base (ver "Backup de
la base", más abajo).

## 7. Chequeos de humo

Al final, `desplegar.sh` muestra algo así:

| Chequeo | Esperado |
|---|---|
| `GET /api/salud` | `{"ok":true}` |
| `GET /api/config` | la configuración pública (site key de Turnstile, nombre del autor, newsletter, modo demo) |
| La portada y `/inicio` | `200` |
| `GET /api/yo` sin sesión | `401` |
| Cabeceras CSP y HSTS | `2 de 2` |

Después probalo como alumno: inscribite con tu mail desde el celular, fijate que llegue el código
(y que no caiga en spam), hacé el módulo 1 y entrá a `/admin` con el mail de `ADMIN_EMAIL`.

En `/admin` también aprobás los links que los alumnos quieren mostrar en la galería: ninguno
aparece ahí sin tu OK.

## Topes de costo

El tutor de la web es lo único que te cuesta por alumno (los módulos 4 a 7 corren en el plan de
cada alumno). El backend calcula el costo de cada llamada con los precios de
`backend/vibe_tutor/costos.py` y lo compara contra dos topes:

- `TOPE_ALUMNO_USD` (por defecto US$1): lo máximo que puede gastar un alumno en toda su vida.
- `TOPE_MENSUAL_USD` (por defecto US$50): lo máximo del curso en el mes.

Al 80% del tope mensual te llega un mail. Cuando se alcanza cualquiera de los dos, el alumno pasa a
la guía escrita del módulo y no pierde su avance. Si cambian los precios de los modelos, o si
cambiás `MODELO` o `TTS_MODELO`, actualizá `costos.py`: si no, las cuentas quedan mal. El gasto del
mes se ve en `/admin`.

## Backup de la base

Todo lo de los alumnos está en `/srv/vibe-tutor/data/vibe.db` (SQLite en modo WAL). Para copiarla
con el servicio andando, usá el backup de SQLite, no `cp`:

```bash
sudo apt install sqlite3
sudo install -d -m 700 /root/backups
sudo sqlite3 /srv/vibe-tutor/data/vibe.db ".backup '/root/backups/vibe-$(date +%F).db'"
```

Para hacerlo todos los días y guardar dos semanas, un cron de root (`sudo crontab -e`):

```text
30 4 * * * sqlite3 /srv/vibe-tutor/data/vibe.db ".backup '/root/backups/vibe-$(date +\%F).db'" && find /root/backups -name 'vibe-*.db' -mtime +14 -delete
```

Los backups tienen datos personales (mails, ideas, conversaciones): guardalos cifrados si salen del
servidor y borralos a tiempo, porque cuando un alumno pide borrar sus datos también tienen que
desaparecer de las copias. Guardá aparte una copia de `/etc/vibe-tutor/.env`: sin `JWT_SECRET` las
sesiones abiertas se invalidan (no se pierde nada más).

Para restaurar: `sudo systemctl stop vibe-tutor`, copiá el backup sobre `vibe.db` (borrá
`vibe.db-wal` y `vibe.db-shm` si quedaron), `sudo chown vibe-tutor:vibe-tutor
/srv/vibe-tutor/data/vibe.db` y `sudo systemctl start vibe-tutor`.

## Recomendaciones

- **Claves propias y con límite de gasto** en cada proveedor, solo para el curso. Si una clave se
  filtra, revocala en el panel del proveedor y cambiala en `/etc/vibe-tutor/.env`.
- **Un usuario de despliegue sin root, si se puede.** `desplegar.sh` detecta que no sos root y usa
  `sudo -n`, así que ese usuario necesita sudo sin contraseña. En la práctica sigue siendo un acceso
  poderoso, pero te deja desactivar el ingreso de root por SSH (`PermitRootLogin no`) y el ingreso
  con contraseña (`PasswordAuthentication no`).
- **Firewall** con solo SSH, 80 y 443 abiertos (por ejemplo, `ufw allow OpenSSH`, `ufw allow
  'Nginx Full'`, `ufw enable`) y actualizaciones de seguridad automáticas (`unattended-upgrades`).
- **Turnstile activado** y el `ADMIN_EMAIL` en una casilla que leas: por ahí llegan los avisos.
- **Textos legales revisados** para tu país antes de abrir la inscripción. Ver
  [adaptar-el-curso.md](adaptar-el-curso.md).

## Problemas comunes

- **"el servidor no está preparado"**: falta correr `preparar-servidor.sh`, o tu usuario no tiene
  sudo sin contraseña.
- **"no hay certificado para …"**: certbot no pudo emitirlo. Revisá el DNS y los puertos 80 y 443,
  y corré de nuevo `preparar-servidor.sh` o `sudo certbot --nginx -d <tu dominio>`.
- **"la API no arrancó", o el chequeo de `/api/config` falla con error 500**: casi siempre es una
  clave que falta o está mal escrita en `/etc/vibe-tutor/.env`. El servicio puede arrancar igual,
  pero su registro dice "no se pudo leer la configuración" y nombra la variable: lo ves con
  `sudo journalctl -u vibe-tutor -n 50`. Arreglala y reiniciá con `sudo systemctl restart
  vibe-tutor`.
- **Error 502 en el navegador**: el servicio está caído. `sudo systemctl status vibe-tutor`.
- **No llegan los mails**: revisá que el dominio de `MAIL_FROM` esté verificado en Resend y mirá
  los envíos en su panel.
