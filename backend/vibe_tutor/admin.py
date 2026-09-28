"""Reporte para quien opera el curso, exportación de la lista de novedades y moderación de la galería
(contracts/api.md, sección Admin; research §9)."""

import csv
import io
import logging
import sqlite3
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, StrictBool

from vibe_tutor import auth, contenido, costos
from vibe_tutor.config import Settings, get_settings

ETAPAS = ("inscriptos", "modulo_1", "modulo_2", "modulo_3", "kits", "links")
_ETAPA_DE = {
    ("inscripcion", None): "inscriptos",
    ("modulo_completo", "modulo=1"): "modulo_1",
    ("modulo_completo", "modulo=2"): "modulo_2",
    ("modulo_completo", "modulo=3"): "modulo_3",
    ("kit", None): "kits",
    ("link", None): "links",
}
VENTANA_RECIENTE = timedelta(days=30)
MENSAJE_SIN_LINK = "Ese link no existe."
_COLUMNAS_MODERACION = "id, url, titulo, mostrar_galeria, aprobado, creado"
# Un mail que empieza así se leería como fórmula al abrir el CSV en una planilla.
_INICIO_DE_FORMULA = ("=", "+", "-", "@", "\t", "\r")

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(auth.solo_admin)])


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).strftime(costos.FORMATO_UTC)


def _etapa(tipo: str, detalle: str | None) -> str | None:
    return _ETAPA_DE.get((tipo, detalle if tipo == "modulo_completo" else None))


def _vacio() -> dict[str, set]:
    return {etapa: set() for etapa in ETAPAS}


def _contar(grupo: dict[str, set]) -> dict[str, int]:
    return {etapa: len(personas) for etapa, personas in grupo.items()}


def embudo(con: sqlite3.Connection, momento: datetime) -> dict:
    """Personas que llegaron a cada etapa, según los eventos (en total, últimos 30 días y por fuente).

    Los eventos de quien borró sus datos quedan sin alumno: cuentan en el total, cada uno como una
    persona, pero no en el desglose por fuente.
    """
    desde = _iso(momento - VENTANA_RECIENTE)
    total, reciente, fuentes = _vacio(), _vacio(), {}
    filas = con.execute(
        "SELECT e.id, e.alumno_id, e.tipo, e.detalle, e.creado, a.fuente FROM eventos e"
        " LEFT JOIN alumnos a ON a.id = e.alumno_id"
        " WHERE e.tipo IN ('inscripcion', 'modulo_completo', 'kit', 'link')"
    )
    for fila in filas:
        etapa = _etapa(fila["tipo"], fila["detalle"])
        if etapa is None:
            continue
        persona = fila["alumno_id"] if fila["alumno_id"] is not None else f"borrado-{fila['id']}"
        es_reciente = fila["creado"] >= desde
        grupos = [total] + ([reciente] if es_reciente else [])
        if fila["alumno_id"] is not None:
            del_total, del_reciente = fuentes.setdefault(fila["fuente"], (_vacio(), _vacio()))
            grupos += [del_total] + ([del_reciente] if es_reciente else [])
        for grupo in grupos:
            grupo[etapa].add(persona)
    por_fuente = [
        {"fuente": fuente, "total": _contar(del_total), "ultimos_30_dias": _contar(del_reciente)}
        for fuente, (del_total, del_reciente) in fuentes.items()
    ]
    por_fuente.sort(key=lambda g: (-g["total"]["inscriptos"], g["fuente"] is None, g["fuente"] or ""))
    return {"total": _contar(total), "ultimos_30_dias": _contar(reciente), "por_fuente": por_fuente}


def gasto(con: sqlite3.Connection, settings: Settings, momento: datetime) -> dict:
    estado = costos.estado_tope(
        con, None, tope_alumno=settings.tope_alumno_usd, tope_mensual=settings.tope_mensual_usd, ahora=momento
    )
    total, alumnos = con.execute(
        "SELECT COALESCE(SUM(costo_usd), 0), COUNT(DISTINCT alumno_id) FROM uso WHERE alumno_id IS NOT NULL"
    ).fetchone()
    tope = estado["tope_mensual"]
    return {
        "mes_usd": estado["gastado_mes"],
        "tope_mensual_usd": tope,
        "porcentaje_tope": round(100 * estado["gastado_mes"] / tope, 1) if tope > 0 else None,
        "aviso_80": estado["aviso"],
        "bloqueado": estado["bloqueado"],
        "tope_alumno_usd": float(settings.tope_alumno_usd),
        "promedio_por_alumno_usd": round(total / alumnos, 4) if alumnos else 0.0,
        "alumnos_con_gasto": alumnos,
    }


def machete(settings: Settings, hoy: date) -> dict:
    """Datos del machete verificados hace más de 45 días (SC-007)."""
    try:
        datos = contenido.cargar_machete(settings.contenido_dir, hoy)
    except contenido.ErrorContenido as error:
        return {"total": 0, "vencidos": [], "error": str(error)}
    vencidos = sorted(contenido.vencidos(datos, hoy), key=lambda d: d.verificado)
    return {
        "total": len(datos),
        "vencidos": [
            {
                "id": dato.id,
                "tema": dato.tema,
                "verificado": dato.verificado.isoformat(),
                "dias": (hoy - dato.verificado).days,
                "fuente": dato.fuente,
            }
            for dato in vencidos
        ],
        "error": None,
    }


@router.get("/reporte")
def reporte(
    settings: Settings = Depends(get_settings), con: sqlite3.Connection = Depends(auth.conexion)
) -> dict:
    momento = ahora()
    return {
        "generado": _iso(momento),
        "embudo": embudo(con, momento),
        "gasto": gasto(con, settings, momento),
        "machete": machete(settings, momento.astimezone(costos.ZONA_ARGENTINA).date()),
    }


@router.get("/novedades.csv")
def novedades(con: sqlite3.Connection = Depends(auth.conexion)) -> Response:
    """Una columna `email` con quienes aceptaron (último consentimiento) las novedades por mail, para
    sumarlos a mano a la lista de NEWSLETTER_NOMBRE."""
    filas = con.execute(
        """
        SELECT a.email FROM alumnos a
        WHERE (SELECT valor FROM consentimientos
               WHERE alumno_id = a.id AND tipo = 'novedades' ORDER BY id DESC LIMIT 1) = 1
        ORDER BY a.id
        """
    )
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow(["email"])
    for fila in filas:
        if fila["email"].startswith(_INICIO_DE_FORMULA):
            log.warning("mail salteado en el CSV de novedades porque empieza como una fórmula")
            continue
        escritor.writerow([fila["email"]])
    return Response(
        salida.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="novedades.csv"', "Cache-Control": "no-store"},
    )


# --- moderación de la galería ------------------------------------------------------------------------


class Aprobacion(BaseModel):
    aprobado: StrictBool


def _link_moderado(fila: sqlite3.Row) -> dict:
    datos = dict(fila)
    datos["mostrar_galeria"] = bool(datos["mostrar_galeria"])
    datos["aprobado"] = bool(datos["aprobado"])
    return datos


@router.get("/links")
def links_para_moderar(con: sqlite3.Connection = Depends(auth.conexion)) -> list[dict]:
    """Los links que sus dueños quieren mostrar en la galería: primero los pendientes, los más nuevos arriba."""
    filas = con.execute(
        f"SELECT {_COLUMNAS_MODERACION} FROM links WHERE mostrar_galeria = 1 ORDER BY aprobado, id DESC"
    )
    return [_link_moderado(fila) for fila in filas]


@router.put("/links/{link_id}")
def moderar_link(link_id: int, datos: Aprobacion, con: sqlite3.Connection = Depends(auth.conexion)) -> dict:
    with con:
        cambiados = con.execute(
            "UPDATE links SET aprobado = ? WHERE id = ?", (int(datos.aprobado), link_id)
        ).rowcount
    if not cambiados:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_SIN_LINK)
    log.info("link %s %s para la galería", link_id, "aprobado" if datos.aprobado else "sacado")
    fila = con.execute(f"SELECT {_COLUMNAS_MODERACION} FROM links WHERE id = ?", (link_id,)).fetchone()
    return _link_moderado(fila)
