"""Tarea periódica del curso (data-model.md, contracts/mails.md): recordatorio, aviso del 80%,
reintentos de mails fallidos y retención de datos (también de los pedidos de acceso que nadie aprobó).

`correr_una_vez` hace todo lo que toca la base (se prueba con un reloj inyectado) y devuelve los
mails que hay que mandar; `bucle` la corre cada 15 minutos y manda esos mails con `mails.enviar`.
"""

import asyncio
import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from vibe_tutor import costos, db, mails
from vibe_tutor.config import Settings

INTERVALO = timedelta(minutes=15)
ESPERA_RECORDATORIO = timedelta(days=3)
# Un mail fallido se reintenta cuando su primer intento (`mails.creado`) cae en una de estas
# franjas de INTERVALO de ancho. Como entre dos vueltas pasan al menos 15 minutos, cada franja se
# usa una vez como mucho: hasta 3 reintentos, todos dentro de las 24 h del primer intento.
REINTENTOS = (timedelta(minutes=15), timedelta(hours=2), timedelta(hours=12))
VENTANA_REINTENTOS = timedelta(hours=24)
RETENCION_SESIONES = timedelta(days=30)
INACTIVIDAD_SESIONES = timedelta(days=365)
VIDA_CODIGOS = timedelta(hours=24)
# Un pedido de acceso (APROBACION_MANUAL) que nadie aprobó se borra a los 90 días de la inscripción.
VIDA_PENDIENTES = timedelta(days=90)
PAUSA_ENTRE_MAILS = 0.6  # segundos; Resend limita los pedidos por segundo

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Envio:
    alumno_id: int | None
    tipo: str
    clave: str


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).strftime(costos.FORMATO_UTC)


def recordatorios(con: sqlite3.Connection, ahora: datetime) -> list[Envio]:
    """Aprobado, ya en el módulo 3 o más, idea guardada hace 3 días o más, sin kit, con mails del curso
    y sin recordatorio previo (el mail lleva al módulo 3: a quien no llegó no le sirve)."""
    filas = con.execute(
        """
        SELECT a.id FROM alumnos a
        WHERE a.estado = 'aprobado'
          AND a.modulo_actual >= 3
          AND (SELECT creado FROM ideas WHERE alumno_id = a.id ORDER BY version DESC LIMIT 1) <= ?
          AND NOT EXISTS (SELECT 1 FROM kits WHERE alumno_id = a.id)
          AND NOT EXISTS (SELECT 1 FROM mails WHERE alumno_id = a.id AND clave = 'recordatorio')
          AND (SELECT valor FROM consentimientos
               WHERE alumno_id = a.id AND tipo = 'mails_curso' ORDER BY id DESC LIMIT 1) = 1
        ORDER BY a.id
        """,
        (_iso(ahora - ESPERA_RECORDATORIO),),
    ).fetchall()
    return [Envio(fila["id"], "recordatorio", "recordatorio") for fila in filas]


def aviso_80(con: sqlite3.Connection, settings: Settings, ahora: datetime) -> list[Envio]:
    """Aviso a quien administra el curso cuando el gasto del mes llega al 80% del tope, una vez por mes."""
    estado = costos.estado_tope(
        con, None, tope_alumno=settings.tope_alumno_usd, tope_mensual=settings.tope_mensual_usd, ahora=ahora
    )
    if not estado["aviso"]:
        return []
    clave = f"aviso_80:{ahora.astimezone(costos.ZONA_ARGENTINA):%Y-%m}"
    if con.execute("SELECT 1 FROM mails WHERE alumno_id IS NULL AND clave = ?", (clave,)).fetchone():
        return []
    return [Envio(None, "aviso_80", clave)]


def reintentos(con: sqlite3.Connection, ahora: datetime) -> list[Envio]:
    filas = con.execute(
        "SELECT alumno_id, tipo, clave, creado FROM mails WHERE estado = 'fallido' AND creado > ? ORDER BY id",
        (_iso(ahora - VENTANA_REINTENTOS),),
    ).fetchall()
    envios = []
    for fila in filas:
        transcurrido = ahora - datetime.fromisoformat(fila["creado"])
        if any(desde <= transcurrido < desde + INTERVALO for desde in REINTENTOS):
            envios.append(Envio(fila["alumno_id"], fila["tipo"], fila["clave"]))
    return envios


def retencion(con: sqlite3.Connection, ahora: datetime) -> dict[str, int]:
    """Borra conversaciones terminadas hace 30 días; las que quedaron abiertas en un módulo que se
    completó hace más de 30 días (se reabrió después de completarlo) cuando su último mensaje (o su
    inicio, si no tiene) tiene más de 30 días; las abandonadas tras 12 meses sin actividad; los
    códigos de más de 24 h, y los pedidos de acceso pendientes de más de 90 días (con todos sus datos
    y un evento `borrado` anónimo por cada uno). Los mensajes se van en cascada; `uso` queda sin
    sesión."""
    limite = _iso(ahora - RETENCION_SESIONES)
    with con:
        terminadas = con.execute("DELETE FROM sesiones WHERE fin IS NOT NULL AND fin < ?", (limite,)).rowcount
        reabiertas = con.execute(
            """
            DELETE FROM sesiones
            WHERE fin IS NULL
              AND EXISTS (SELECT 1 FROM avance
                          WHERE avance.alumno_id = sesiones.alumno_id AND avance.modulo = sesiones.modulo
                            AND avance.completado < ?)
              AND COALESCE((SELECT max(creado) FROM mensajes WHERE sesion_id = sesiones.id), sesiones.inicio) < ?
            """,
            (limite, limite),
        ).rowcount
        abandonadas = con.execute(
            "DELETE FROM sesiones WHERE fin IS NULL"
            " AND alumno_id IN (SELECT id FROM alumnos WHERE ultima_actividad < ?)",
            (_iso(ahora - INACTIVIDAD_SESIONES),),
        ).rowcount
        codigos = con.execute("DELETE FROM codigos WHERE creado < ?", (_iso(ahora - VIDA_CODIGOS),)).rowcount
        pendientes = con.execute(
            "DELETE FROM alumnos WHERE estado = 'pendiente' AND creado < ?", (_iso(ahora - VIDA_PENDIENTES),)
        ).rowcount
        con.executemany("INSERT INTO eventos (alumno_id, tipo) VALUES (NULL, 'borrado')", [()] * pendientes)
    borrados = {
        "sesiones_terminadas": terminadas,
        "sesiones_reabiertas": reabiertas,
        "sesiones_abandonadas": abandonadas,
        "codigos": codigos,
        "pendientes": pendientes,
    }
    if any(borrados.values()):
        log.info("retención: %s", borrados)
    return borrados


def _paso(nombre: str, funcion: Callable, *args) -> list[Envio]:
    try:
        return funcion(*args) or []
    except Exception:
        log.exception("la tarea periódica falló en: %s", nombre)
        return []


def correr_una_vez(settings: Settings, ahora: datetime | None = None) -> list[Envio]:
    """Una vuelta de la tarea: aplica la retención y devuelve los mails que hay que mandar."""
    ahora = ahora or datetime.now(timezone.utc)
    if ahora.tzinfo is None:
        ahora = ahora.replace(tzinfo=timezone.utc)
    con = db.conectar(settings.data_dir / db.ARCHIVO)
    try:
        db.migrar(con)
        envios = _paso("recordatorio", recordatorios, con, ahora)
        envios += _paso("aviso del 80%", aviso_80, con, settings, ahora)
        envios += _paso("reintentos", reintentos, con, ahora)
        _paso("retención", retencion, con, ahora)
        return envios
    finally:
        con.close()


async def dormir(segundos: float) -> None:
    await asyncio.sleep(segundos)


async def mandar(settings: Settings, envios: list[Envio]) -> list[str]:
    estados = []
    for numero, envio in enumerate(envios):
        if numero:
            await dormir(PAUSA_ENTRE_MAILS)
        estados.append(await mails.enviar(settings, envio.alumno_id, envio.tipo, envio.clave))
    return estados


async def una_vuelta(settings: Settings) -> None:
    try:
        envios = await asyncio.to_thread(correr_una_vez, settings)
        await mandar(settings, envios)
    except Exception:
        log.exception("falló una vuelta de la tarea periódica")


async def bucle(settings: Settings) -> None:
    """Corre para siempre cada 15 minutos; la arranca main.py si settings.tareas_activas."""
    while True:
        await una_vuelta(settings)
        await dormir(INTERVALO.total_seconds())
