"""Mails del curso (contracts/mails.md): plantillas de contenido/mails, envío por Resend y baja firmada.

Cada mail sale una sola vez por (alumno_id, clave). El alumno recibe como mucho tres mails del
curso en toda su vida: bienvenida, recordatorio y contame, cada uno una sola vez (el contame sale
con el primer link que registra, clave "contame"). Los del curso respetan la baja (`mails_curso`),
van solo a alumnos aprobados (con APROBACION_MANUAL, la bienvenida sale al aprobar) y llevan el pie
legal con el link de baja y las cabeceras de baja en un clic (RFC 8058). El aviso del 80% y el de
pedidos de acceso van a quien administra el curso (ADMIN_EMAIL) y no tienen baja. En el modo demo
ningún mail sale: se registra en el log el asunto y el destinatario.
"""

import base64
import hashlib
import hmac
import html
import logging
import re
import sqlite3
from collections.abc import Iterator
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from vibe_tutor import contenido, costos, db, dominio
from vibe_tutor.config import Settings, get_settings

RESEND_URL = "https://api.resend.com/emails"
PIE_LEGAL = "legal/pie-mails.md"
CON_BAJA = frozenset({"bienvenida", "recordatorio", "contame"})
# Avisos a quien administra el curso: van a ADMIN_EMAIL, sin alumno, sin pie legal ni baja.
PARA_ADMIN = frozenset({"aviso_80", "pedidos"})
_COMUNES = frozenset({"ENLACE_CURSO", "ENLACE_MODULO_3"}) | contenido.MARCADORES_DEL_CURSO
MARCADORES: dict[str, frozenset[str]] = {
    "bienvenida": _COMUNES | {"ENLACE_BAJA"},
    "recordatorio": _COMUNES | {"ENLACE_BAJA"},
    "contame": _COMUNES | {"ENLACE_BAJA", "LINK_ALUMNO", "TITULO_LINK"},
    "aviso_80": _COMUNES | {"GASTO_MES", "TOPE_MES", "ALUMNOS_ACTIVOS", "ENLACE_REPORTE"},
    "pedidos": _COMUNES | {"PENDIENTES", "ENLACE_ADMIN"},
}
# Nombres que usan quienes llaman a enviar() para los datos del link (alumnos.py manda link y titulo).
_ALIAS = {"LINK": "LINK_ALUMNO", "URL": "LINK_ALUMNO", "TITULO": "TITULO_LINK"}
CLAVE_CONTAME = "contame"
PROPOSITO_BAJA = "baja"
MENSAJE_TOKEN = "El link para darte de baja no es válido. Abrilo de nuevo desde el último mail del curso."

_MARCADOR = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
_COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)
_URL = re.compile(r"https?://[^\s<>\"']+")
_TOKEN = re.compile(r"([1-9][0-9]{0,17})\.([A-Za-z0-9_-]{43})")
_FIN_DE_URL = ".,;:!?)»"
_ESTILO = "font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5;color:#222"

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["mails"])


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).strftime(costos.FORMATO_UTC)


def clave_pedidos(momento: datetime) -> str:
    """Clave del aviso de pedidos de acceso: una por hora de Argentina (`pedidos:AAAA-MM-DDTHH`),
    así sale como mucho un aviso por hora aunque lleguen muchos pedidos."""
    return f"pedidos:{momento.astimezone(costos.ZONA_ARGENTINA):%Y-%m-%dT%H}"


def _abrir(settings: Settings) -> sqlite3.Connection:
    con = db.conectar(settings.data_dir / db.ARCHIVO)
    db.migrar(con)
    return con


# --- token de baja ---------------------------------------------------------------------------------


def _firma(settings: Settings, alumno_id: int) -> str:
    mensaje = f"{PROPOSITO_BAJA}:{alumno_id}".encode()
    digest = hmac.new(settings.jwt_secret.encode(), mensaje, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def token_baja(settings: Settings, alumno_id: int) -> str:
    """Token firmado (HMAC-SHA256 con jwt_secret) para el link de baja: `<alumno_id>.<firma>`, sin vencimiento."""
    return f"{alumno_id}.{_firma(settings, alumno_id)}"


def leer_token_baja(settings: Settings, token: str | None) -> int | None:
    """Devuelve el alumno_id del token de baja, o None si no es válido."""
    encontrado = _TOKEN.fullmatch(token or "")
    if not encontrado:
        return None
    alumno_id = int(encontrado.group(1))
    if not hmac.compare_digest(encontrado.group(2), _firma(settings, alumno_id)):
        return None
    return alumno_id


# --- armado del mail -------------------------------------------------------------------------------


def _dinero(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",")


def _alumnos_activos_del_mes(con: sqlite3.Connection, momento: datetime) -> int:
    inicio = momento.astimezone(costos.ZONA_ARGENTINA).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return con.execute(
        "SELECT count(*) FROM alumnos WHERE ultima_actividad >= ? AND estado = ?", (_iso(inicio), dominio.APROBADO)
    ).fetchone()[0]


def _link(con: sqlite3.Connection, alumno_id: int, clave: str) -> sqlite3.Row | None:
    """El link del mail contame: el último que registró el alumno (con la clave vieja
    `contame:<id>`, ese link)."""
    _, _, link_id = clave.partition(":")
    if link_id.isdigit():
        return con.execute(
            "SELECT url, titulo FROM links WHERE id = ? AND alumno_id = ?", (int(link_id), alumno_id)
        ).fetchone()
    return con.execute(
        "SELECT url, titulo FROM links WHERE alumno_id = ? ORDER BY id DESC LIMIT 1", (alumno_id,)
    ).fetchone()


def _valores(
    con: sqlite3.Connection, settings: Settings, alumno_id: int | None, tipo: str, clave: str, datos: dict | None
) -> dict[str, str]:
    base = f"https://{settings.dominio}"
    valores = {"ENLACE_CURSO": f"{base}/", "ENLACE_MODULO_3": f"{base}/modulo/3"}
    if tipo in CON_BAJA:
        valores["ENLACE_BAJA"] = f"{base}/baja?t={token_baja(settings, alumno_id)}"
    if tipo == "contame":
        link = _link(con, alumno_id, clave)
        if link is not None:
            valores["LINK_ALUMNO"] = link["url"]
            valores["TITULO_LINK"] = link["titulo"] or ""
    if tipo == "aviso_80":
        momento = ahora()
        valores["GASTO_MES"] = _dinero(costos.mes_actual(con, momento))
        valores["TOPE_MES"] = _dinero(settings.tope_mensual_usd)
        valores["ALUMNOS_ACTIVOS"] = str(_alumnos_activos_del_mes(con, momento))
        valores["ENLACE_REPORTE"] = f"{base}/admin"
    if tipo == "pedidos":
        # Sin datos (el reintento de la tarea periódica), la cuenta sale de la base.
        valores["PENDIENTES"] = str(dominio.contar_pendientes(con))
        valores["ENLACE_ADMIN"] = f"{base}/admin"
    for nombre, valor in (datos or {}).items():
        if valor is not None:
            nombre = str(nombre).upper()
            valores[_ALIAS.get(nombre, nombre)] = str(valor)
    if tipo == "contame":
        valores.setdefault("TITULO_LINK", "")  # sin título, la plantilla deja esa línea vacía
    return valores


def _reemplazar(texto: str, valores: dict[str, str]) -> str:
    return _MARCADOR.sub(lambda m: valores.get(m.group(1), m.group(0)), texto)


def _parrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n[ \t]*\n", texto.strip()) if p.strip()]


def _html_parrafo(parrafo: str) -> str:
    partes, pos = [], 0
    for encontrado in _URL.finditer(parrafo):
        url = encontrado.group(0).rstrip(_FIN_DE_URL)
        partes.append(html.escape(parrafo[pos : encontrado.start()]))
        partes.append(f'<a href="{html.escape(url)}">{html.escape(url)}</a>')
        pos = encontrado.start() + len(url)
    partes.append(html.escape(parrafo[pos:]))
    return "<p>" + "".join(partes).replace("\n", "<br>\n") + "</p>"


def a_html(cuerpo: str, pie: str = "") -> str:
    """HTML simple: texto escapado, un <p> por párrafo, saltos como <br> y links clicables."""
    bloques = [_html_parrafo(p) for p in _parrafos(cuerpo)]
    if pie.strip():
        bloques.append("<hr>")
        bloques.extend(_html_parrafo(p) for p in _parrafos(pie))
    return f'<div style="{_ESTILO}">\n' + "\n".join(bloques) + "\n</div>"


def _leer_plantilla(settings: Settings, ruta: str) -> tuple[dict, str]:
    """Frontmatter y cuerpo de una plantilla, sin los comentarios HTML (notas internas que no salen)."""
    meta, cuerpo = contenido.separar_frontmatter(contenido.leer(settings.contenido_dir, ruta))
    return meta, _COMENTARIO.sub("", cuerpo)


def _armar(
    con: sqlite3.Connection, settings: Settings, alumno_id: int | None, tipo: str, clave: str, datos: dict | None
) -> tuple[str, str, str, dict | None] | None:
    """Devuelve (asunto, texto, html, cabeceras) o None si la plantilla no alcanza para mandarlo."""
    try:
        meta, cuerpo = _leer_plantilla(settings, f"mails/{tipo}.md")
        pie = _leer_plantilla(settings, PIE_LEGAL)[1] if tipo in CON_BAJA else ""
    except contenido.ErrorContenido as error:
        log.error("no se puede armar el mail %s: %s", tipo, error)
        return None
    asunto = " ".join(str(meta.get("asunto") or "").split())
    if not asunto:
        log.error("la plantilla del mail %s no tiene asunto", tipo)
        return None
    valores = _valores(con, settings, alumno_id, tipo, clave, datos)
    asunto, cuerpo, pie = (
        _reemplazar(contenido.reemplazar_marcadores(texto, settings), valores) for texto in (asunto, cuerpo, pie)
    )
    faltan = sorted(set(_MARCADOR.findall("\n".join((asunto, cuerpo, pie)))))
    if faltan:
        log.error("el mail %s (%s) quedó con marcadores sin valor: %s", tipo, clave, ", ".join(faltan))
        return None
    texto = "\n\n".join(_parrafos(cuerpo) + _parrafos(pie)) + "\n"
    cabeceras = None
    if tipo in CON_BAJA:
        cabeceras = {
            "List-Unsubscribe": f"<https://{settings.dominio}/api/baja?t={token_baja(settings, alumno_id)}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
    return asunto, texto, a_html(cuerpo, pie), cabeceras


async def _mandar(
    settings: Settings, destinatario: str, asunto: str, texto: str, html_: str, cabeceras: dict | None
) -> bool:
    if settings.modo_demo:
        log.info("modo demo: no se manda el mail %r a %s", asunto, destinatario)
        return True
    cuerpo = {"from": settings.mail_from, "to": [destinatario], "subject": asunto, "text": texto, "html": html_}
    if cabeceras:
        cuerpo["headers"] = cabeceras
    try:
        async with httpx.AsyncClient(timeout=10) as cliente:
            respuesta = await cliente.post(
                RESEND_URL, headers={"Authorization": f"Bearer {settings.resend_api_key}"}, json=cuerpo
            )
    except httpx.HTTPError as error:
        log.error("Resend no respondió: %s", type(error).__name__)
        return False
    if respuesta.is_success:
        return True
    try:
        nombre = respuesta.json().get("name")
    except ValueError:
        nombre = None
    log.error("Resend rechazó el mail: HTTP %s %s", respuesta.status_code, nombre or "")
    return False


# --- envío -------------------------------------------------------------------------------------------


def _contame_enviado(con: sqlite3.Connection, alumno_id: int) -> bool:
    """Si ya salió un "contame" a este alumno, con cualquier clave (una sola vez en la vida)."""
    fila = con.execute(
        "SELECT 1 FROM mails WHERE alumno_id = ? AND tipo = 'contame' AND estado = 'enviado'", (alumno_id,)
    ).fetchone()
    return fila is not None


def contame_pendiente(con: sqlite3.Connection, alumno_id: int) -> bool:
    """Si al registrar un link hay que mandar el mail contame: acepta los mails del curso y nunca
    se le mandó uno. (Un contame que quedó fallido cuenta como pendiente.)"""
    return dominio.consentimiento(con, alumno_id, "mails_curso") and not _contame_enviado(con, alumno_id)


def _reservar(con: sqlite3.Connection, alumno_id: int | None, tipo: str, clave: str) -> int | None:
    """Anota el mail como `fallido` antes de mandarlo; None si otro envío ya lo reservó."""
    try:
        with con:
            cursor = con.execute(
                "INSERT INTO mails (alumno_id, tipo, clave, estado, creado) VALUES (?, ?, ?, 'fallido', ?)",
                (alumno_id, tipo, clave, _iso(ahora())),
            )
    except sqlite3.IntegrityError:
        return None
    return int(cursor.lastrowid)


async def _enviar(settings: Settings, alumno_id: int | None, tipo: str, clave: str, datos: dict | None) -> str:
    if tipo not in MARCADORES:
        log.error("tipo de mail desconocido: %s", tipo)
        return "fallido"
    if tipo in PARA_ADMIN:
        alumno_id = None
    elif alumno_id is None:
        log.error("el mail %s necesita un alumno", tipo)
        return "fallido"
    con = _abrir(settings)
    try:
        previo = con.execute(
            "SELECT id, estado FROM mails WHERE alumno_id IS ? AND clave = ?", (alumno_id, clave)
        ).fetchone()
        if previo is not None and previo["estado"] == "enviado":
            return "omitido"
        if alumno_id is None:
            destinatario = settings.admin_email
        else:
            fila = dominio.alumno(con, alumno_id)
            if fila is None or fila["estado"] != dominio.APROBADO:
                return "omitido"
            if not dominio.consentimiento(con, alumno_id, "mails_curso"):
                return "omitido"
            if tipo == "contame" and (_contame_enviado(con, alumno_id) or _link(con, alumno_id, clave) is None):
                return "omitido"
            destinatario = fila["email"]
        mail_id = previo["id"] if previo is not None else _reservar(con, alumno_id, tipo, clave)
        if mail_id is None:
            return "omitido"
        mensaje = _armar(con, settings, alumno_id, tipo, clave, datos)
        enviado = mensaje is not None and await _mandar(settings, destinatario, *mensaje)
        estado = "enviado" if enviado else "fallido"
        with con:
            con.execute("UPDATE mails SET estado = ? WHERE id = ?", (estado, mail_id))
        if not enviado:
            log.warning("el mail %s (%s) quedó fallido", tipo, clave)
        return estado
    finally:
        con.close()


async def enviar(
    settings: Settings, alumno_id: int | None, tipo: str, clave: str, datos: dict | None = None
) -> str:
    """Manda un mail del curso una sola vez por (alumno_id, clave) y devuelve el estado.

    Abre su propia conexión a la base, respeta la baja (`mails_curso`) y manda solo a alumnos
    aprobados, salvo en los avisos a quien administra (`aviso_80` y `pedidos`, sin alumno),
    registra el resultado en `mails` y nunca levanta excepciones: devuelve "enviado",
    "fallido" u "omitido". El contame (clave CLAVE_CONTAME) sale una sola vez en la vida del
    alumno y solo si tiene un link registrado. `datos` puede traer valores de marcadores (por
    nombre, por ejemplo `LINK_ALUMNO`, o `link` y `titulo` para el mail contame); lo que falte se
    toma de la base (para el contame, el último link del alumno).
    """
    try:
        return await _enviar(settings, alumno_id, tipo, clave, datos)
    except Exception:
        log.exception("no se pudo procesar el mail %s (%s)", tipo, clave)
        return "fallido"


# --- baja --------------------------------------------------------------------------------------------


def _conexion(settings: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    con = _abrir(settings)
    try:
        yield con
    finally:
        con.close()


@router.api_route("/baja", methods=["GET", "POST"])
def baja(
    t: str = "",
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(_conexion),
) -> dict:
    """Baja de los mails del curso con el token del mail, sin sesión (también la de un clic, RFC 8058)."""
    alumno_id = leer_token_baja(settings, t)
    if alumno_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, MENSAJE_TOKEN)
    if dominio.alumno(con, alumno_id) is not None and dominio.consentimiento(con, alumno_id, "mails_curso"):
        version = contenido.version_legal(settings.contenido_dir)
        dominio.agregar_consentimiento(con, alumno_id, "mails_curso", False, version)
        dominio.registrar_evento(con, alumno_id, "baja_mails")
    return {"ok": True}
