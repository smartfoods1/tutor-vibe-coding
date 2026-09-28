#!/usr/bin/env bash
# Preparación única del servidor para la web del curso (Ubuntu 24.04 o parecido, con systemd).
# Corre como root EN el servidor, con el dominio como argumento. Desde tu compu, en la raíz del repo:
#
#   set -a; . deploy/despliegue.env; set +a
#   ssh "$VIBE_SERVIDOR" "mkdir -p vibe-tutor-preparar"
#   scp deploy/preparar-servidor.sh deploy/.env.example deploy/vibe-tutor.service "$VIBE_SERVIDOR:vibe-tutor-preparar/"
#   ssh -t "$VIBE_SERVIDOR" "sudo bash vibe-tutor-preparar/preparar-servidor.sh $VIBE_DOMINIO"
#
# Opcional: un mail como segundo argumento hace que certbot corra sin preguntas (y con eso aceptás
# los términos de Let's Encrypt). Sin ese mail, certbot pregunta en la terminal.
#
# Qué hace: instala lo que falte (nginx, certbot, ffmpeg, rsync, Python 3.12), crea el usuario
# vibe-tutor y sus carpetas, crea /etc/vibe-tutor/.env desde .env.example con un JWT_SECRET nuevo,
# deja el servicio instalado, arma un sitio de nginx solo con el puerto 80 y pide el certificado
# con certbot. No lee claves de ningún otro lado ni toca otros sitios. Es idempotente: lo que ya
# existe queda como está, así que se puede correr de nuevo sin miedo.
set -euo pipefail

APP=vibe-tutor
AQUI=$(cd "$(dirname "$0")" && pwd)
ENV_ARCHIVO=/etc/$APP/.env
SITIO=/etc/nginx/sites-available/$APP
OBLIGATORIAS=(ANTHROPIC_API_KEY GEMINI_API_KEY RESEND_API_KEY MAIL_FROM ADMIN_EMAIL)
RECOMENDADAS=(TURNSTILE_SITE_KEY TURNSTILE_SECRET AUTOR_NOMBRE)

error() {
    echo "error: $*" >&2
    exit 1
}

[ "$(id -u)" = 0 ] || error "corré este script como root (con sudo)"
DOMINIO=${1:-}
MAIL_CERTBOT=${2:-}
[ -n "$DOMINIO" ] || error "falta el dominio. Uso: bash preparar-servidor.sh curso.tudominio.com [tu@mail]"
[[ "$DOMINIO" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]] \
    || error "no parece un dominio (va sin https:// ni barras): $DOMINIO"
for archivo in .env.example vibe-tutor.service; do
    [ -f "$AQUI/$archivo" ] || error "falta $archivo junto al script: subilo con scp (ver docs/desplegar.md)"
done

echo "== programas"
faltan=()
command -v nginx >/dev/null || faltan+=(nginx)
if ! command -v certbot >/dev/null; then
    faltan+=(certbot python3-certbot-nginx)
elif ! certbot plugins 2>/dev/null | grep -i nginx >/dev/null; then
    faltan+=(python3-certbot-nginx)
fi
command -v ffmpeg >/dev/null || faltan+=(ffmpeg)
command -v rsync >/dev/null || faltan+=(rsync)
command -v curl >/dev/null || faltan+=(curl)
command -v openssl >/dev/null || faltan+=(openssl)
if ! command -v python3.12 >/dev/null; then
    faltan+=(python3.12 python3.12-venv)
elif ! python3.12 -c "import ensurepip, venv" 2>/dev/null; then
    faltan+=(python3.12-venv)
fi
if [ "${#faltan[@]}" -gt 0 ]; then
    command -v apt-get >/dev/null \
        || error "faltan estos programas y no encuentro apt-get para instalarlos: ${faltan[*]}"
    echo "instalando: ${faltan[*]}"
    apt-get update -q
    DEBIAN_FRONTEND=noninteractive apt-get install -y -q "${faltan[@]}" \
        || error "no se pudo instalar ${faltan[*]}. El backend necesita Python 3.12 (viene en Ubuntu 24.04): instalalo y volvé a correr el script"
else
    echo "están todos"
fi

echo "== usuario y carpetas"
id "$APP" >/dev/null 2>&1 || useradd --system --home-dir /opt/$APP --shell /usr/sbin/nologin "$APP"
install -d -o root -g root -m 755 /opt/$APP /var/www/$APP /srv/$APP /srv/$APP/contenido
install -d -o "$APP" -g "$APP" -m 750 /srv/$APP/data
install -d -o root -g "$APP" -m 750 /etc/$APP

echo "== configuración ($ENV_ARCHIVO)"
if [ -f "$ENV_ARCHIVO" ]; then
    echo "ya existe: no la toco"
else
    # Copia .env.example sin el bloque "Local": completa JWT_SECRET, DOMINIO y las rutas, deja a la
    # vista las claves que hay que llenar y comenta las demás vacías (así rigen sus valores por
    # defecto). El secreto viaja por el entorno de awk, nunca por la línea de comandos.
    (
        umask 027
        VT_JWT=$(openssl rand -hex 32) VT_DOMINIO=$DOMINIO VT_DATA=/srv/$APP/data VT_CONTENIDO=/srv/$APP/contenido \
            VT_VISIBLES="${OBLIGATORIAS[*]} ${RECOMENDADAS[*]} NEWSLETTER_NOMBRE" \
            awk -v fecha="$(date +%F)" '
            BEGIN {
                completar["JWT_SECRET"] = ENVIRON["VT_JWT"]
                completar["DOMINIO"] = ENVIRON["VT_DOMINIO"]
                completar["DATA_DIR"] = ENVIRON["VT_DATA"]
                completar["CONTENIDO_DIR"] = ENVIRON["VT_CONTENIDO"]
                n = split(ENVIRON["VT_VISIBLES"], lista, " ")
                for (i = 1; i <= n; i++) visibles[lista[i]] = 1
                print "# Configuración del curso. La creó deploy/preparar-servidor.sh el " fecha " a partir de"
                print "# deploy/.env.example. Permisos 640, dueño root, grupo vibe-tutor."
                print "# Las líneas sin # son las que hay que completar; las que empiezan con \"# CLAVE=\" usan el"
                print "# valor por defecto (para cambiarlo, sacale el # y poné el tuyo). Los valores con espacios o"
                print "# con < > van entre comillas. Después de editarlo: sudo systemctl restart vibe-tutor"
                print ""
            }
            /^# --- Local ---/ { exit }
            !empezado && !/^# --- / { next }
            { empezado = 1 }
            /^[A-Z][A-Z0-9_]*=/ {
                clave = substr($0, 1, index($0, "=") - 1)
                valor = substr($0, index($0, "=") + 1)
                if (clave in completar) { print clave "=" completar[clave]; next }
                if (valor == "" && !(clave in visibles)) { print "# " $0; next }
            }
            { print }
        ' "$AQUI/.env.example" > "$ENV_ARCHIVO.nuevo"
    )
    grep -q "^JWT_SECRET=[0-9a-f]\{64\}$" "$ENV_ARCHIVO.nuevo" \
        || { rm -f "$ENV_ARCHIVO.nuevo"; error "no se pudo generar JWT_SECRET: revisá .env.example"; }
    chown root:"$APP" "$ENV_ARCHIVO.nuevo"
    chmod 640 "$ENV_ARCHIVO.nuevo"
    mv "$ENV_ARCHIVO.nuevo" "$ENV_ARCHIVO"
    echo "creada (los valores no se muestran)"
fi

echo "== entorno de Python"
if [ -x /opt/$APP/.venv/bin/python ]; then
    echo "ya existe /opt/$APP/.venv"
else
    python3.12 -m venv /opt/$APP/.venv
    echo "creado /opt/$APP/.venv"
fi

echo "== servicio"
if cmp -s "$AQUI/vibe-tutor.service" /etc/systemd/system/$APP.service; then
    echo "ya está instalado"
else
    install -m 644 "$AQUI/vibe-tutor.service" /etc/systemd/system/$APP.service
    systemctl daemon-reload
    echo "instalado; lo habilita y lo arranca el primer deploy/desplegar.sh"
fi

echo "== nginx (puerto 80)"
if [ -f "$SITIO" ]; then
    echo "ya existe $SITIO: no lo toco"
else
    cat > "$SITIO" <<NGINX
# Sitio inicial (solo puerto 80) que dejó deploy/preparar-servidor.sh para que certbot pida el
# certificado. El primer deploy/desplegar.sh lo reemplaza por deploy/nginx-vibe-tutor.conf.plantilla.
server {
    listen 80;
    listen [::]:80;
    server_name $DOMINIO;
    root /var/www/$APP;

    location / {
        return 404;
    }
}
NGINX
    chmod 644 "$SITIO"
    ln -sf "$SITIO" /etc/nginx/sites-enabled/$APP
    if ! nginx -t; then
        rm -f /etc/nginx/sites-enabled/$APP "$SITIO"
        error "nginx -t falló con el sitio inicial y lo saqué: revisá la configuración de nginx del servidor"
    fi
    if systemctl is-active --quiet nginx; then systemctl reload nginx; else systemctl start nginx; fi
    echo "creado $SITIO"
fi

echo "== certificado HTTPS"
certificado_ok=1
explicar_certbot() {
    echo "Para pedirlo a mano, cuando el DNS ya apunte acá:"
    echo "  sudo certbot --nginx -d $DOMINIO"
    echo "Si falla, revisá que el registro DNS de $DOMINIO apunte a este servidor y que los puertos 80 y"
    echo "443 estén abiertos en el firewall. Después podés volver a correr este script."
}
if [ -f "/etc/letsencrypt/live/$DOMINIO/fullchain.pem" ]; then
    echo "ya hay certificado para $DOMINIO"
else
    if ! getent hosts "$DOMINIO" >/dev/null; then
        echo "ojo: $DOMINIO todavía no resuelve a ninguna dirección; certbot va a fallar hasta que el DNS esté listo"
    fi
    if [ -n "$MAIL_CERTBOT" ]; then
        certbot --nginx -d "$DOMINIO" --non-interactive --agree-tos -m "$MAIL_CERTBOT" --redirect \
            || { certificado_ok=0; explicar_certbot; }
    elif [ -t 0 ]; then
        certbot --nginx -d "$DOMINIO" || { certificado_ok=0; explicar_certbot; }
    else
        certificado_ok=0
        echo "no hay una terminal para las preguntas de certbot (usá ssh -t o pasá tu mail como segundo argumento)."
        explicar_certbot
    fi
fi

echo
echo "== qué falta"
faltantes=()
vacias=()
leer_valor() { grep -E "^$1=" "$ENV_ARCHIVO" | tail -1 | cut -d= -f2- | tr -d "\"' "; }
for clave in "${OBLIGATORIAS[@]}"; do
    [ -n "$(leer_valor "$clave")" ] || faltantes+=("$clave")
done
for clave in "${RECOMENDADAS[@]}"; do
    [ -n "$(leer_valor "$clave")" ] || vacias+=("$clave")
done
if [ "${#faltantes[@]}" -gt 0 ]; then
    echo "Completá en $ENV_ARCHIVO: ${faltantes[*]}"
    echo "  sudo nano $ENV_ARCHIVO   (los valores con espacios o < > van entre comillas)"
fi
if [ "${#vacias[@]}" -gt 0 ]; then
    echo "Recomendado completar: ${vacias[*]} (sin Turnstile el antibots queda apagado)"
fi
if [ "$certificado_ok" = 1 ] && [ "${#faltantes[@]}" -eq 0 ]; then
    echo "El servidor está listo. Falta el primer despliegue: desde tu compu, deploy/desplegar.sh"
else
    echo "Cuando esté todo, desde tu compu: deploy/desplegar.sh"
fi
[ "$certificado_ok" = 1 ] || exit 1
