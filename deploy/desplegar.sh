#!/usr/bin/env bash
# Despliega la web del curso en tu servidor: tests, build, subida, nginx y servicio (solo si
# cambiaron, con vuelta atrás), reinicio y chequeos de humo por HTTPS.
#
# Uso (desde cualquier carpeta): deploy/desplegar.sh
# Lee VIBE_SERVIDOR (usuario@servidor) y VIBE_DOMINIO de deploy/despliegue.env (copiá
# deploy/despliegue.env.example) o del entorno, que tiene prioridad sobre el archivo.
# Antes hay que correr una vez deploy/preparar-servidor.sh en el servidor (docs/desplegar.md).
# No toca ningún otro servicio: compara la lista de servicios del servidor antes y después.
set -euo pipefail

RAIZ=$(cd "$(dirname "$0")/.." && pwd)
CONFIG="$RAIZ/deploy/despliegue.env"

error() {
    echo "error: $*" >&2
    exit 1
}

# --- Configuración: lo que venga del entorno pisa a lo del archivo ---
servidor_entorno=${VIBE_SERVIDOR:-}
dominio_entorno=${VIBE_DOMINIO:-}
if [ -f "$CONFIG" ]; then
    set -a
    # shellcheck source=/dev/null
    . "$CONFIG"
    set +a
fi
VIBE_SERVIDOR=${servidor_entorno:-${VIBE_SERVIDOR:-}}
VIBE_DOMINIO=${dominio_entorno:-${VIBE_DOMINIO:-}}

como_completar="copiá deploy/despliegue.env.example a deploy/despliegue.env y completalo, o exportala antes de correr el script"
[ -n "$VIBE_SERVIDOR" ] || error "falta VIBE_SERVIDOR (usuario@servidor): $como_completar"
[ -n "$VIBE_DOMINIO" ] || error "falta VIBE_DOMINIO (el dominio del curso): $como_completar"
case "$VIBE_SERVIDOR $VIBE_DOMINIO" in
    *tu-servidor* | *tudominio.com*)
        error "deploy/despliegue.env todavía tiene los valores de ejemplo: poné tu servidor y tu dominio" ;;
esac
[[ "$VIBE_SERVIDOR" =~ ^[A-Za-z0-9_][A-Za-z0-9._@-]*$ ]] \
    || error "VIBE_SERVIDOR no parece usuario@servidor (o un alias de ~/.ssh/config): $VIBE_SERVIDOR"
[[ "$VIBE_DOMINIO" =~ ^[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?$ ]] \
    || error "VIBE_DOMINIO no parece un dominio (va sin https:// ni barras): $VIBE_DOMINIO"

SSH=(ssh -o ConnectTimeout=10 "$VIBE_SERVIDOR")
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cd "$RAIZ"

# --- El servidor está preparado? (y si el usuario no es root, se usa sudo sin contraseña) ---
echo "== servidor $VIBE_SERVIDOR"
uid_remoto=$("${SSH[@]}" "id -u") || error "no pude entrar por SSH a $VIBE_SERVIDOR"
if [ "$uid_remoto" = 0 ]; then
    SUDO=""
    RSYNC_REMOTO="rsync"
else
    SUDO="sudo -n"
    RSYNC_REMOTO="sudo -n rsync"
fi
"${SSH[@]}" "$SUDO test -f /etc/vibe-tutor/.env && $SUDO test -x /opt/vibe-tutor/.venv/bin/python" \
    || error "el servidor no está preparado (o falta sudo sin contraseña): corré antes deploy/preparar-servidor.sh (docs/desplegar.md)"
RSYNC=(rsync -rlptz --delete -e "ssh -o ConnectTimeout=10" --rsync-path="$RSYNC_REMOTO")

echo "== tests"
[ -x backend/.venv/bin/pytest ] || error "no encuentro backend/.venv: prepará el entorno del backend (docs/desarrollo-local.md)"
(cd backend && .venv/bin/pytest -q)
(cd frontend && npm test --silent && npm run build --silent)

echo "== servicios antes"
"${SSH[@]}" "timeout 20 systemctl list-units --type=service --state=running --no-legend --plain" \
    | awk '{print $1}' | grep -v '^vibe-tutor.service$' | sort > "$TMP/antes"

echo "== subida"
"${RSYNC[@]}" \
    --exclude .venv --exclude __pycache__ --exclude .pytest_cache --exclude .ruff_cache --exclude tests \
    --exclude '*.egg-info' --exclude '.env*' --exclude /data/ --exclude '*.db*' \
    backend/ "$VIBE_SERVIDOR:/opt/vibe-tutor/"
"${RSYNC[@]}" \
    --exclude investigacion --exclude ejemplos --exclude curriculo.md --exclude VERSION \
    contenido/ "$VIBE_SERVIDOR:/srv/vibe-tutor/contenido/"
version="$(date +%F)-$(git rev-parse --short HEAD 2>/dev/null || echo sin-git)"
if git rev-parse --git-dir >/dev/null 2>&1 && ! git diff --quiet; then
    version="$version-con-cambios"
fi
echo "$version" | "${SSH[@]}" "$SUDO tee /srv/vibe-tutor/contenido/VERSION >/dev/null"
"${RSYNC[@]}" frontend/dist/ "$VIBE_SERVIDOR:/var/www/vibe-tutor/"

echo "== nginx y servicio (solo si cambiaron)"
sed "s/__DOMINIO__/$VIBE_DOMINIO/g" deploy/nginx-vibe-tutor.conf.plantilla > "$TMP/nginx-vibe-tutor.conf"
if grep -q "__DOMINIO__" "$TMP/nginx-vibe-tutor.conf"; then
    error "la plantilla de nginx quedó con __DOMINIO__ sin reemplazar"
fi
tmp_remoto=$("${SSH[@]}" "mktemp -d /tmp/vibe-tutor-despliegue.XXXXXX")
scp -q -o ConnectTimeout=10 "$TMP/nginx-vibe-tutor.conf" deploy/nginx-vibe-tutor-cabeceras.conf \
    deploy/vibe-tutor.service "$VIBE_SERVIDOR:$tmp_remoto/"
"${SSH[@]}" "timeout 60 $SUDO bash -s -- '$tmp_remoto' '$VIBE_DOMINIO'" <<'REMOTO'
set -e
origen=$1
dominio=$2
trap 'rm -rf "$origen"' EXIT
if [ ! -f "/etc/letsencrypt/live/$dominio/fullchain.pem" ]; then
    echo "no hay certificado para $dominio en el servidor: corré deploy/preparar-servidor.sh, que lo pide con certbot"
    exit 1
fi
cambiados=()
instalar() {
    if ! cmp -s "$1" "$2"; then
        if [ -f "$2" ]; then cp "$2" "$2.anterior"; else rm -f "$2.anterior"; fi
        install -m 644 "$1" "$2"
        cambiados+=("$2")
    fi
}
instalar "$origen/nginx-vibe-tutor-cabeceras.conf" /etc/nginx/snippets/vibe-tutor-cabeceras.conf
instalar "$origen/nginx-vibe-tutor.conf" /etc/nginx/sites-available/vibe-tutor
if [ ! -e /etc/nginx/sites-enabled/vibe-tutor ]; then
    ln -s /etc/nginx/sites-available/vibe-tutor /etc/nginx/sites-enabled/vibe-tutor
    cambiados+=(/etc/nginx/sites-enabled/vibe-tutor)
fi
if [ "${#cambiados[@]}" -gt 0 ]; then
    if nginx -t 2>/dev/null; then
        systemctl reload nginx
        echo "nginx recargado"
    else
        for f in "${cambiados[@]}"; do
            if [ -f "$f.anterior" ]; then cp "$f.anterior" "$f"; else rm -f "$f"; fi
        done
        nginx -t || true
        echo "la configuración nueva de nginx no pasó nginx -t: quedó la anterior"
        exit 1
    fi
fi
if ! cmp -s "$origen/vibe-tutor.service" /etc/systemd/system/vibe-tutor.service; then
    install -m 644 "$origen/vibe-tutor.service" /etc/systemd/system/vibe-tutor.service
    systemctl daemon-reload
    echo "servicio actualizado"
fi
REMOTO

echo "== dependencias y reinicio"
"${SSH[@]}" "timeout 300 $SUDO /opt/vibe-tutor/.venv/bin/pip install -q -e /opt/vibe-tutor"
"${SSH[@]}" "timeout 30 $SUDO bash -c 'systemctl enable -q vibe-tutor && systemctl restart vibe-tutor'"
for intento in $(seq 1 20); do
    if "${SSH[@]}" "timeout 5 curl -fsS http://127.0.0.1:8340/api/salud" >/dev/null 2>&1; then
        break
    fi
    if [ "$intento" = 20 ]; then
        echo "la API no arrancó; últimas líneas del servicio:"
        "${SSH[@]}" "timeout 10 $SUDO journalctl -u vibe-tutor -n 40 --no-pager"
        exit 1
    fi
    sleep 1
done

echo "== servicios después"
"${SSH[@]}" "timeout 20 systemctl list-units --type=service --state=running --no-legend --plain" \
    | awk '{print $1}' | grep -v '^vibe-tutor.service$' | sort > "$TMP/despues"
if ! diff -u "$TMP/antes" "$TMP/despues"; then
    echo "OJO: cambió la lista de otros servicios del servidor"
    exit 1
fi

echo "== humo por HTTPS"
curl -fsS "https://$VIBE_DOMINIO/api/salud"; echo
curl -fsS "https://$VIBE_DOMINIO/api/config"; echo
curl -fsS -o /dev/null -w "portada %{http_code}\n" "https://$VIBE_DOMINIO/"
curl -fsS -o /dev/null -w "ruta del frontend %{http_code}\n" "https://$VIBE_DOMINIO/inicio"
curl -sS -o /dev/null -w "yo sin sesión %{http_code} (esperado 401)\n" "https://$VIBE_DOMINIO/api/yo"
curl -sSI "https://$VIBE_DOMINIO/" | grep -ciE "^(content-security-policy|strict-transport-security):" \
    | xargs -I{} echo "cabeceras de seguridad CSP y HSTS: {} de 2"
echo "listo: https://$VIBE_DOMINIO"
