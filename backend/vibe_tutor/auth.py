import hashlib
import hmac
import json
import logging
import re
import secrets
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from vibe_tutor import contenido, db, dominio, mails
from vibe_tutor.config import Settings, get_settings

# El prefijo __Host- obliga al navegador a aceptarla solo con Secure, Path=/ y sin Domain: ningún
# subdominio puede pisarla ni leerla.
COOKIE = "__Host-vibe_sesion"
DURACION_SESION = timedelta(days=30)
VIGENCIA_CODIGO = timedelta(minutes=10)
MAX_INTENTOS = 5
# Tope de códigos errados por mail, sumando todos sus códigos: con más de 10 fallos en 24 h ningún
# código de ese mail vale hasta que los fallos salen de la ventana.
MAX_FALLOS_MAIL = 10
VENTANA_FALLOS = timedelta(hours=24)
METODOS_QUE_CAMBIAN = frozenset({"POST", "PUT", "PATCH", "DELETE"})
SITIOS_PROPIOS = frozenset({"same-origin", "none"})
RESEND_URL = "https://api.resend.com/emails"
SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
ACCION_TURNSTILE = "inscripcion"
ASUNTO = "Tu código para entrar al curso"
HOSTS_LOCALES = frozenset({"localhost", "127.0.0.1"})
IPS_LOCALES = frozenset({"127.0.0.1", "::1"})
PATRON_EMAIL = re.compile(r"[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}")

MENSAJE_TURNSTILE = "No pudimos comprobar que no seas un robot. Recargá la página y probá de nuevo."
MENSAJE_MAIL = "Revisá el mail: no parece una dirección válida."
MENSAJE_MAILS_CURSO = "Para hacer el curso necesitamos mandarte mails del curso."
MENSAJE_TRANSFERENCIA = (
    "El curso funciona con proveedores en Estados Unidos y Brasil; sin ese permiso no podemos darte el curso."
)
MENSAJE_CODIGO = "El código no es válido o ya venció. Pedí uno nuevo."
MENSAJE_OTRO_SITIO = "Este pedido no salió de la página del curso. Abrí el curso desde su dirección y probá de nuevo."

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@dataclass(frozen=True)
class Alumno:
    id: int
    email: str
    es_admin: bool


class Consentimientos(BaseModel):
    mails_curso: bool = False
    transferencia: bool = False
    novedades: bool = False


class PedidoCodigo(BaseModel):
    email: str = Field(max_length=320)
    turnstile: str | None = Field(default=None, max_length=4096)
    consentimientos: Consentimientos = Field(default_factory=Consentimientos)
    fuente: str | None = Field(default=None, max_length=64, pattern=r"^[a-z0-9-]*$")


class Verificacion(BaseModel):
    email: str = Field(max_length=320)
    codigo: str = Field(max_length=64)


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).isoformat(timespec="seconds")


def _hash(sal: str, codigo: str) -> str:
    return hashlib.sha256((sal + codigo).encode()).hexdigest()


def conexion(settings: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    con = db.conectar(settings.data_dir / db.ARCHIVO)
    try:
        db.migrar(con)
        yield con
    finally:
        con.close()


def _ip(request: Request) -> str:
    return request.client.host if request.client else ""


def _contar(con: sqlite3.Connection, condicion: str, parametros: tuple) -> int:
    return con.execute(f"SELECT count(*) FROM codigos WHERE {condicion}", parametros).fetchone()[0]


def _crear_codigo(
    con: sqlite3.Connection, settings: Settings, email: str, ip: str, pendiente: dict
) -> str | None:
    momento = ahora()
    hace_una_hora = _iso(momento - timedelta(hours=1))
    with con:
        con.execute("BEGIN IMMEDIATE")
        if (
            _contar(con, "email = ? AND creado > ?", (email, hace_una_hora)) >= settings.max_codigos_mail_hora
            or _contar(con, "ip = ? AND creado > ?", (ip, hace_una_hora)) >= settings.max_codigos_ip_hora
            or _contar(con, "creado > ?", (_iso(momento - timedelta(days=1)),)) >= settings.max_codigos_dia
        ):
            log.warning("pedido de código sin enviar por límite (ip %s)", ip)
            return None
        codigo = f"{secrets.randbelow(1_000_000):06d}"
        sal = secrets.token_hex(16)
        con.execute("UPDATE codigos SET usado = 1 WHERE email = ? AND usado = 0", (email,))
        con.execute(
            "INSERT INTO codigos (email, hash, sal, vence, ip, pendiente_json, creado) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                email,
                _hash(sal, codigo),
                sal,
                _iso(momento + VIGENCIA_CODIGO),
                ip,
                json.dumps(pendiente, ensure_ascii=False),
                _iso(momento),
            ),
        )
    return codigo


def _fallos_recientes(con: sqlite3.Connection, email: str, momento: datetime) -> int:
    fila = con.execute(
        "SELECT COALESCE(SUM(fallos), 0) FROM codigos WHERE email = ? AND creado > ?",
        (email, _iso(momento - VENTANA_FALLOS)),
    ).fetchone()
    return int(fila[0])


def _consumir_codigo(con: sqlite3.Connection, email: str, codigo: str) -> dict | None:
    """Devuelve los datos pendientes del código si acierta; None si no vale.

    Con más de MAX_FALLOS_MAIL fallos del mail en VENTANA_FALLOS no se mira el código: vale None
    igual que uno errado, así no se puede seguir probando ni saber si se acertó.
    """
    momento = ahora()
    with con:
        con.execute("BEGIN IMMEDIATE")
        if _fallos_recientes(con, email, momento) > MAX_FALLOS_MAIL:
            log.warning("código rechazado sin mirarlo: el mail pasó el tope de fallos")
            return None
        filas = con.execute(
            """
            UPDATE codigos SET intentos = intentos + 1
            WHERE id = (SELECT max(id) FROM codigos WHERE email = ?)
              AND usado = 0 AND intentos < ? AND vence > ?
            RETURNING id, hash, sal, intentos, pendiente_json
            """,
            (email, MAX_INTENTOS, _iso(momento)),
        ).fetchall()
        if not filas:
            return None
        fila = filas[0]
        acierto = hmac.compare_digest(fila["hash"], _hash(fila["sal"], codigo))
        if not acierto:
            con.execute("UPDATE codigos SET fallos = fallos + 1 WHERE id = ?", (fila["id"],))
        if acierto or fila["intentos"] >= MAX_INTENTOS:
            con.execute("UPDATE codigos SET usado = 1, pendiente_json = NULL WHERE id = ?", (fila["id"],))
    if not acierto:
        return None
    return json.loads(fila["pendiente_json"] or "{}")


def _es_local(request: Request) -> bool:
    return request.url.hostname in HOSTS_LOCALES and _ip(request) in IPS_LOCALES


def _codigo_dev_valido(settings: Settings, request: Request, codigo: str) -> bool:
    fijo = settings.dev_codigo_fijo
    return bool(fijo) and _es_local(request) and hmac.compare_digest(codigo.encode(), fijo.encode())


def emitir_token(settings: Settings, alumno_id: int) -> str:
    momento = ahora()
    datos = {
        "sub": str(alumno_id),
        "iat": int(momento.timestamp()),
        "exp": int((momento + DURACION_SESION).timestamp()),
    }
    return jwt.encode(datos, settings.jwt_secret, algorithm="HS256")


def _leer_token(settings: Settings, token: str) -> int | None:
    try:
        datos = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            options={"require": ["sub", "iat", "exp"], "verify_exp": False, "verify_iat": False},
        )
    except jwt.InvalidTokenError:
        return None
    vence = datos["exp"]
    if not isinstance(vence, int | float) or vence <= ahora().timestamp():
        return None
    sub = datos["sub"]
    if not isinstance(sub, str) or not sub.isdigit():
        return None
    return int(sub)


def poner_cookie(response: Response, settings: Settings, alumno_id: int) -> None:
    response.set_cookie(
        COOKIE,
        emitir_token(settings, alumno_id),
        max_age=int(DURACION_SESION.total_seconds()),
        path="/",
        secure=True,
        httponly=True,
        samesite="strict",
    )


def borrar_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE, path="/", secure=True, httponly=True, samesite="strict")


async def _turnstile_valido(settings: Settings, token: str | None, ip: str) -> bool:
    if not settings.turnstile_secret:
        return True
    if not token:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as cliente:
            respuesta = await cliente.post(
                SITEVERIFY_URL,
                data={"secret": settings.turnstile_secret, "response": token, "remoteip": ip},
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
    except (httpx.HTTPError, ValueError) as error:
        log.error("no se pudo verificar Turnstile: %s", type(error).__name__)
        return False
    return (
        datos.get("success") is True
        and datos.get("hostname") == settings.dominio
        and datos.get("action") == ACCION_TURNSTILE
    )


async def enviar_codigo(settings: Settings, email: str, codigo: str) -> None:
    if settings.modo_demo:
        log.info("modo demo: no se manda el mail %r a %s", ASUNTO, email)
        return
    texto = (
        f"Tu código para entrar al curso es {codigo}. "
        "Vence en 10 minutos. Si no lo pediste, ignorá este mail."
    )
    html = (
        "<p>Tu código para entrar al curso es:</p>"
        f'<p style="font-size:28px;letter-spacing:6px"><strong>{codigo}</strong></p>'
        "<p>Vence en 10 minutos. Si no lo pediste, ignorá este mail.</p>"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as cliente:
            respuesta = await cliente.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={"from": settings.mail_from, "to": [email], "subject": ASUNTO, "text": texto, "html": html},
            )
            respuesta.raise_for_status()
    except httpx.HTTPError as error:
        log.error("Resend no envió el código de acceso: %s", type(error).__name__)


def alumno_actual(
    request: Request,
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> Alumno:
    token = request.cookies.get(COOKIE)
    alumno_id = _leer_token(settings, token) if token else None
    fila = dominio.alumno(con, alumno_id) if alumno_id is not None else None
    if fila is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tu sesión venció. Entrá de nuevo con tu mail.")
    email = fila["email"]
    return Alumno(id=fila["id"], email=email, es_admin=email == dominio.normalizar_email(settings.admin_email))


class AntiCSRF:
    """Rechaza con 403 los pedidos que cambian datos (POST, PUT, PATCH, DELETE) cuando el navegador
    avisa con Sec-Fetch-Site que vienen de otro sitio. Sin esa cabecera (clientes que no son un
    navegador, como el pedido de baja en un clic de los proveedores de mail) el pedido pasa."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] in METODOS_QUE_CAMBIAN:
            sitio = Headers(scope=scope).get("sec-fetch-site")
            if sitio is not None and sitio.strip().lower() not in SITIOS_PROPIOS:
                respuesta = JSONResponse({"detalle": MENSAJE_OTRO_SITIO}, status_code=status.HTTP_403_FORBIDDEN)
                await respuesta(scope, receive, send)
                return
        await self.app(scope, receive, send)


def instalar_csrf(app: FastAPI) -> None:
    """Instala AntiCSRF en la app (main.crear_app lo hace; las apps de test lo pueden llamar)."""
    app.add_middleware(AntiCSRF)


def solo_admin(alumno: Alumno = Depends(alumno_actual)) -> Alumno:
    if not alumno.es_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Esta sección es solo para quien administra el curso.")
    return alumno


@router.post("/codigo")
async def pedir_codigo(
    pedido: PedidoCodigo,
    request: Request,
    tareas: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    email = dominio.normalizar_email(pedido.email)
    if not PATRON_EMAIL.fullmatch(email):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_MAIL)
    ip = _ip(request)
    if not await _turnstile_valido(settings, pedido.turnstile, ip):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, MENSAJE_TURNSTILE)
    if dominio.alumno_por_email(con, email) is None:
        if not pedido.consentimientos.mails_curso:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_MAILS_CURSO)
        if not pedido.consentimientos.transferencia:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_TRANSFERENCIA)
    pendiente = {"consentimientos": pedido.consentimientos.model_dump(), "fuente": pedido.fuente or None}
    codigo = _crear_codigo(con, settings, email, ip, pendiente)
    if codigo is not None:
        tareas.add_task(enviar_codigo, settings, email, codigo)
    return {"ok": True}


def _alta(con: sqlite3.Connection, settings: Settings, email: str, pendiente: dict) -> int:
    consentimientos = dict(pendiente.get("consentimientos") or {})
    if not settings.hay_newsletter:
        consentimientos["novedades"] = False  # sin newsletter no hay casilla que aceptar
    fuente = pendiente.get("fuente")
    alumno_id = dominio.crear_alumno(con, email, fuente=fuente)
    version = contenido.version_legal(settings.contenido_dir)
    for tipo in ("mails_curso", "transferencia", "novedades"):
        dominio.agregar_consentimiento(con, alumno_id, tipo, bool(consentimientos.get(tipo)), version)
    dominio.registrar_evento(con, alumno_id, "inscripcion", f"fuente={fuente}" if fuente else None)
    return alumno_id


@router.post("/verificar")
def verificar(
    datos: Verificacion,
    request: Request,
    response: Response,
    tareas: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    email = dominio.normalizar_email(datos.email)
    codigo = datos.codigo.strip()
    if _codigo_dev_valido(settings, request, codigo):
        pendiente: dict | None = {"consentimientos": {"mails_curso": True, "transferencia": True}}
    else:
        pendiente = _consumir_codigo(con, email, codigo)
    if pendiente is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, MENSAJE_CODIGO)
    existente = dominio.alumno_por_email(con, email)
    if existente is not None:
        alumno_id = int(existente["id"])
    else:
        consentimientos = pendiente.get("consentimientos") or {}
        if not (consentimientos.get("mails_curso") and consentimientos.get("transferencia")):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, MENSAJE_CODIGO)
        alumno_id = _alta(con, settings, email, pendiente)
        tareas.add_task(mails.enviar, settings, alumno_id, "bienvenida", "bienvenida")
    dominio.tocar_actividad(con, alumno_id)
    poner_cookie(response, settings, alumno_id)
    return {"ok": True, "nuevo": existente is None}


@router.post("/salir")
def salir(response: Response) -> dict:
    borrar_cookie(response)
    return {"ok": True}
