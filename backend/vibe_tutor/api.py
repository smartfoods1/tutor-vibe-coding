"""Sesiones del tutor de la web y turnos con SSE (contracts/api.md, módulos 1 a 3).

El resto de las rutas del alumno (/yo, guías, idea, taller, kit) vive en alumnos.py.
"""

import json
import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import aclosing
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from vibe_tutor import auth, db, dominio, prompts
from vibe_tutor import tutor as modulo_tutor
from vibe_tutor.config import Settings, get_settings
from vibe_tutor.tutor import EventoSSE, Imagen, TopeAlcanzado, Tutor

log = logging.getLogger("vibe_tutor.api")

MAX_TEXTO = 4000
CABECERAS_SSE = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
MENSAJE_FALLA = "El servidor tuvo un problema con esta respuesta. Tu mensaje quedó guardado: tocá Reintentar."
MENSAJE_SIN_SESION = "Esa conversación no existe."
MENSAJE_SIN_MODULO = "Ese módulo no tiene tutor en la web."
MENSAJE_MODULO_CERRADO = "Ese módulo todavía no está abierto: terminá antes el anterior."
MENSAJE_TEXTO_LARGO = "El mensaje supera los 4.000 caracteres: acortalo."
MENSAJE_VACIO = "Escribí un mensaje o mandá una captura."
MENSAJE_IMAGEN_GRANDE = "La captura supera los 5 MB. Probá con una más chica."
MENSAJE_IMAGEN_FORMATO = "La captura tiene que ser una imagen PNG, JPEG o WebP."

# Quien espera que aprueben su inscripción (APROBACION_MANUAL) no usa el tutor: 403 "pendiente".
Alumno = Annotated[auth.Alumno, Depends(auth.alumno_aprobado)]
Con = Annotated[sqlite3.Connection, Depends(auth.conexion)]

router = APIRouter(prefix="/api", tags=["tutor"])


def obtener_tutor(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> Tutor:
    """Un solo tutor por app: guarda los candados de cada conversación."""
    tutor = getattr(request.app.state, "tutor", None)
    if tutor is None:
        ruta = settings.data_dir / db.ARCHIVO
        tutor = Tutor(settings, lambda: db.conectar(ruta))
        request.app.state.tutor = tutor
    return tutor


TutorDep = Annotated[Tutor, Depends(obtener_tutor)]


def _textos(bloques: list[dict]) -> list[str]:
    return [
        b["text"].strip()
        for b in bloques
        if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str) and b["text"].strip()
    ]


def mensajes_visibles(filas: list[tuple[str, list[dict]]]) -> list[dict]:
    """Los mensajes que ve el alumno: sin el estado inicial, el pensamiento ni las herramientas."""
    visibles: list[dict] = []
    for indice, (rol, contenido) in enumerate(filas):
        if indice == 0 and rol == "user":
            continue
        quien = "tutor" if rol == "assistant" else "alumno"
        textos = _textos(contenido)
        if not textos:
            continue
        if visibles and visibles[-1]["rol"] == quien:
            visibles[-1]["texto"] = "\n\n".join([visibles[-1]["texto"], *textos])
        else:
            visibles.append({"rol": quien, "texto": "\n\n".join(textos)})
    return visibles


def _sesion_propia(con: sqlite3.Connection, sesion_id: int, alumno_id: int) -> sqlite3.Row:
    fila = con.execute("SELECT id, alumno_id, modulo FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()
    if fila is None or fila["alumno_id"] != alumno_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_SIN_SESION)
    return fila


def formatear_sse(evento: EventoSSE) -> str:
    return f"event: {evento.tipo}\ndata: {json.dumps(evento.datos, ensure_ascii=False)}\n\n"


async def _eventos_sse(
    tutor: Tutor, sesion_id: int, alumno_id: int, texto: str | None, imagen: Imagen | None
) -> AsyncIterator[str]:
    try:
        async with aclosing(tutor.turno(sesion_id, alumno_id, texto, imagen)) as eventos:
            async for evento in eventos:
                yield formatear_sse(evento)
    except Exception:
        log.exception("falló el turno de la sesión %s", sesion_id)
        yield formatear_sse(EventoSSE("error", {"mensaje": MENSAJE_FALLA, "reintentable": True}))


@router.post("/modulos/{modulo}/sesion")
def abrir_sesion(modulo: int, alumno: Alumno, con: Con, tutor: TutorDep) -> dict:
    if modulo not in prompts.MODULOS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_SIN_MODULO)
    if modulo > int(dominio.alumno(con, alumno.id)["modulo_actual"]):
        raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_MODULO_CERRADO)
    try:
        sesion_id, retomada = tutor.abrir_sesion(alumno.id, modulo)
    except TopeAlcanzado as tope:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, modulo_tutor.detalle_tope(tope.alcance, modulo)) from None
    return {"id": sesion_id, "retomada": retomada}


@router.get("/sesiones/{sesion_id}")
def ver_sesion(sesion_id: int, alumno: Alumno, con: Con) -> dict:
    sesion = _sesion_propia(con, sesion_id, alumno.id)
    filas = modulo_tutor.filas_de(con, sesion_id)
    return {
        "id": sesion["id"],
        "modulo": sesion["modulo"],
        "pendiente": modulo_tutor.pendiente(filas),
        "mensajes": mensajes_visibles([(rol, contenido) for _, rol, contenido in filas]),
    }


async def _leer_imagen(imagen: UploadFile | None) -> Imagen | None:
    if imagen is None:
        return None
    datos = await imagen.read(modulo_tutor.MAX_IMAGEN_BYTES + 1)
    if len(datos) > modulo_tutor.MAX_IMAGEN_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, MENSAJE_IMAGEN_GRANDE)
    if not datos:
        return None
    tipo = modulo_tutor.tipo_imagen(datos)
    if tipo is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, MENSAJE_IMAGEN_FORMATO)
    return Imagen(tipo, datos)


@router.post("/sesiones/{sesion_id}/turno")
async def turno(
    sesion_id: int,
    alumno: Alumno,
    con: Con,
    tutor: TutorDep,
    texto: Annotated[str | None, Form()] = None,
    imagen: Annotated[UploadFile | None, File()] = None,
) -> StreamingResponse:
    _sesion_propia(con, sesion_id, alumno.id)
    if texto is not None and len(texto) > MAX_TEXTO:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_TEXTO_LARGO)
    texto = (texto or "").strip() or None
    captura = await _leer_imagen(imagen)
    if texto is None and captura is None and not modulo_tutor.pendiente(modulo_tutor.filas_de(con, sesion_id)):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_VACIO)
    return StreamingResponse(
        _eventos_sse(tutor, sesion_id, alumno.id, texto, captura),
        media_type="text/event-stream",
        headers=CABECERAS_SSE,
    )
