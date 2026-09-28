import asyncio
import base64
import binascii
import logging
import re
import sqlite3
import tempfile
import time
import weakref
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, StringConstraints

from vibe_tutor import auth, costos, db, dominio, tutor
from vibe_tutor.config import Settings, get_settings

log = logging.getLogger("vibe_tutor.voz")

MODELO_STT = "gemini-2.5-flash"
URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
ARCHIVO_DB = db.ARCHIVO
MAX_AUDIO_BYTES = 15 * 1024 * 1024
MAX_MP3_BYTES = 15 * 1024 * 1024
# Techo de duración del audio que va a transcribirse, aunque el archivo diga otra cosa.
MAX_SEGUNDOS_TRANSCRIPCION = 200
# Conversiones con ffmpeg y pedidos a Gemini que corren a la vez en todo el servidor.
MAX_AUDIOS_SIMULTANEOS = 2
MAX_TRANSCRIPCIONES_HORA = 30
VENTANA_TRANSCRIPCIONES_S = 3600
MAX_TEXTO_VOZ = 600
FRECUENCIA_PCM = 24000
TIMEOUT_GEMINI = httpx.Timeout(60.0, connect=10.0)
TIMEOUT_FFMPEG_S = 60
FORMATOS_ENTRADA = "matroska,webm,mov,mp4,m4a,3gp,ogg,wav,mp3,aac,flac"

PROMPT_TRANSCRIPCION = (
    "Transcribí de forma literal este audio. Habla una persona adulta que no programa y está haciendo "
    "un curso de vibe coding (construir una página propia conversando con una IA), en español "
    "rioplatense con voseo. Escribí exactamente lo que dice, sin resumir, corregir, traducir ni "
    "responderle. Usá la ortografía habitual de estos términos cuando aparezcan: vibe coding, Claude, "
    "Claude Code, Codex, ChatGPT, Netlify, Mac, Windows, app, carpeta, archivo, link, página, "
    "publicar, versión, captura. Devolvé solo el texto transcripto, sin comillas ni comentarios. "
    "Si no se entiende ninguna palabra, devolvé una respuesta vacía."
)


class AudioInvalido(ValueError):
    pass


class AudioMuyLargo(AudioInvalido):
    pass


class ErrorVoz(RuntimeError):
    pass


_SEMAFOROS: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Semaphore]" = weakref.WeakKeyDictionary()


def _semaforo() -> asyncio.Semaphore:
    """El semáforo del bucle en curso (uno solo en el servidor; los tests abren varios bucles)."""
    bucle = asyncio.get_running_loop()
    semaforo = _SEMAFOROS.get(bucle)
    if semaforo is None:
        semaforo = _SEMAFOROS[bucle] = asyncio.Semaphore(MAX_AUDIOS_SIMULTANEOS)
    return semaforo


def reloj() -> float:
    return time.monotonic()


class ContadorTranscripciones:
    """Pedidos de transcripción por alumno en la última hora (en memoria: el servicio corre en un
    solo proceso). Cuenta todos los pedidos que pasan, también los que después fallan."""

    def __init__(self) -> None:
        self._pedidos: dict[int, deque[float]] = {}

    def registrar(self, alumno_id: int, ahora: float) -> bool:
        """Anota el pedido y devuelve True, o False si el alumno ya llegó al máximo de la hora."""
        desde = ahora - VENTANA_TRANSCRIPCIONES_S
        for otro in [a for a, cola in self._pedidos.items() if not cola or cola[-1] <= desde]:
            del self._pedidos[otro]
        cola = self._pedidos.setdefault(alumno_id, deque())
        while cola and cola[0] <= desde:
            cola.popleft()
        if len(cola) >= MAX_TRANSCRIPCIONES_HORA:
            return False
        cola.append(ahora)
        return True


async def _ffmpeg(entrada: list[str], salida: list[str], datos: bytes | None = None) -> bytes:
    proceso = await asyncio.create_subprocess_exec(
        "ffmpeg", "-hide_banner", "-loglevel", "error", *entrada, "-vn", *salida, "-f", "mp3", "pipe:1",
        stdin=asyncio.subprocess.PIPE if datos is not None else asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        mp3, error = await asyncio.wait_for(proceso.communicate(datos), TIMEOUT_FFMPEG_S)
    except TimeoutError:
        proceso.kill()
        await proceso.wait()
        raise AudioInvalido("ffmpeg tardó demasiado en convertir el audio") from None
    if proceso.returncode != 0 or not mp3:
        detalle = error.decode(errors="replace").strip()[-300:]
        raise AudioInvalido(f"ffmpeg no pudo convertir el audio: {detalle or 'salida vacía'}")
    return mp3


async def a_mp3(datos: bytes, mono_16k: bool) -> bytes:
    """Convierte a MP3. Con mono_16k (el audio para transcribir) corta a MAX_SEGUNDOS_TRANSCRIPCION."""
    if not datos:
        raise AudioInvalido("El audio está vacío")
    formato = (
        ["-t", str(MAX_SEGUNDOS_TRANSCRIPCION), "-ac", "1", "-ar", "16000", "-b:a", "32k"]
        if mono_16k
        else ["-b:a", "64k"]
    )
    with tempfile.TemporaryDirectory(prefix="vibe-voz-") as carpeta:
        origen = Path(carpeta, "entrada")
        origen.write_bytes(datos)
        return await _ffmpeg(
            ["-nostdin", "-protocol_whitelist", "file", "-format_whitelist", FORMATOS_ENTRADA, "-i", str(origen)],
            formato,
        )


async def _pcm_a_mp3(pcm: bytes, frecuencia: int) -> bytes:
    return await _ffmpeg(
        ["-f", "s16le", "-ar", str(frecuencia), "-ac", "1", "-i", "pipe:0"], ["-b:a", "64k"], pcm
    )


@contextmanager
def _abrir(settings: Settings) -> Iterator[sqlite3.Connection]:
    con = db.conectar(settings.data_dir / ARCHIVO_DB)
    try:
        db.migrar(con)
        yield con
    finally:
        con.close()


async def _generar(settings: Settings, modelo: str, cuerpo: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_GEMINI) as cliente:
            respuesta = await cliente.post(
                URL_GEMINI.format(modelo=modelo),
                json=cuerpo,
                headers={"x-goog-api-key": settings.gemini_api_key},
            )
    except httpx.HTTPError as error:
        raise ErrorVoz(f"Gemini {modelo} no respondió: {type(error).__name__}") from None
    if respuesta.status_code != 200:
        raise ErrorVoz(f"Gemini {modelo} respondió {respuesta.status_code}")
    try:
        datos = respuesta.json()
    except ValueError:
        datos = None
    if not isinstance(datos, dict):
        raise ErrorVoz(f"Gemini {modelo} devolvió una respuesta ilegible")
    return datos


def _partes(respuesta: dict) -> list[dict]:
    candidatos = respuesta.get("candidates") or []
    if not candidatos:
        return []
    return (candidatos[0].get("content") or {}).get("parts") or []


def _texto(respuesta: dict) -> str:
    return "".join(p.get("text", "") for p in _partes(respuesta) if not p.get("thought")).strip()


def _audio(respuesta: dict) -> tuple[bytes, str] | None:
    for parte in _partes(respuesta):
        dato = parte.get("inlineData") or parte.get("inline_data") or {}
        if dato.get("data"):
            try:
                audio = base64.b64decode(dato["data"])
            except binascii.Error:
                return None
            return audio, dato.get("mimeType") or dato.get("mime_type") or ""
    return None


async def _audio_a_mp3(datos: bytes, mime: str) -> bytes:
    if mime and not re.match(r"audio/(l16|pcm)\b", mime, re.IGNORECASE):
        return await a_mp3(datos, mono_16k=False)
    frecuencia = re.search(r"rate=(\d+)", mime)
    return await _pcm_a_mp3(datos, int(frecuencia.group(1)) if frecuencia else FRECUENCIA_PCM)


def _tokens(uso: dict) -> dict[str, int]:
    def por_modalidad(clave: str, modalidad: str) -> int:
        return sum(int(d.get("tokenCount") or 0) for d in uso.get(clave) or [] if d.get("modality") == modalidad)

    entrada_audio = por_modalidad("promptTokensDetails", "AUDIO")
    salida_audio = por_modalidad("candidatesTokensDetails", "AUDIO")
    return {
        "entrada_texto": max(int(uso.get("promptTokenCount") or 0) - entrada_audio, 0),
        "entrada_audio": entrada_audio,
        "salida": max(int(uso.get("candidatesTokenCount") or 0) - salida_audio, 0)
        + int(uso.get("thoughtsTokenCount") or 0),
        "salida_audio": salida_audio,
    }


def _registrar(
    respuesta: dict, modelo: str, settings: Settings, con: sqlite3.Connection | None, alumno_id: int | None
) -> None:
    uso = respuesta.get("usageMetadata")
    if not uso:
        return
    tokens = _tokens(uso)
    costo = costos.costo_gemini(modelo, **tokens)
    if con is not None:
        costos.registrar(con, "gemini", modelo, tokens, costo, alumno_id=alumno_id)
        return
    with _abrir(settings) as propia:
        costos.registrar(propia, "gemini", modelo, tokens, costo, alumno_id=alumno_id)


async def transcribir(
    audio: bytes,
    *,
    settings: Settings | None = None,
    con: sqlite3.Connection | None = None,
    alumno_id: int | None = None,
) -> str:
    settings = settings or get_settings()
    async with _semaforo():
        mp3 = await a_mp3(audio, mono_16k=True)
        if len(mp3) > MAX_MP3_BYTES:
            raise AudioMuyLargo("el audio convertido supera los 15 MB")
        respuesta = await _generar(settings, MODELO_STT, _pedido_transcripcion(mp3))
    _registrar(respuesta, MODELO_STT, settings, con, alumno_id)
    return _texto(respuesta)


def _pedido_transcripcion(mp3: bytes) -> dict:
    return {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT_TRANSCRIPCION},
                    {"inline_data": {"mime_type": "audio/mp3", "data": base64.b64encode(mp3).decode()}},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 2048,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }


# Los modelos TTS de Gemini no aceptan instrucciones de sistema, y una instrucción de estilo
# pegada al texto la leen en voz alta (y cuesta un 70% más de audio). Se manda solo el texto.
async def sintetizar(
    texto: str,
    *,
    settings: Settings | None = None,
    con: sqlite3.Connection | None = None,
    alumno_id: int | None = None,
) -> bytes:
    settings = settings or get_settings()
    cuerpo = {
        "contents": [{"role": "user", "parts": [{"text": texto}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": settings.tts_voz}}},
        },
    }
    fallas = []
    async with _semaforo():
        for modelo in dict.fromkeys((settings.tts_modelo, settings.tts_modelo_respaldo)):
            try:
                respuesta = await _generar(settings, modelo, cuerpo)
            except ErrorVoz as error:
                fallas.append(str(error))
                log.warning("TTS: %s", error)
                continue
            _registrar(respuesta, modelo, settings, con, alumno_id)
            audio = _audio(respuesta)
            if audio is None:
                fallas.append(f"Gemini {modelo} no devolvió audio")
                log.warning("TTS: %s no devolvió audio", modelo)
                continue
            return await _audio_a_mp3(*audio)
    raise ErrorVoz("; ".join(fallas))


def conexion(settings: Annotated[Settings, Depends(get_settings)]) -> Iterator[sqlite3.Connection]:
    with _abrir(settings) as con:
        yield con


class PedidoHablar(BaseModel):
    texto: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TEXTO_VOZ)]


MENSAJE_MODO_DEMO = "La voz no está disponible en el modo demo."


def _sin_modo_demo(settings: Annotated[Settings, Depends(get_settings)]) -> None:
    """En el modo demo no hay claves de Gemini: la voz responde 503 sin llamar a nadie."""
    if settings.modo_demo:
        raise HTTPException(503, MENSAJE_MODO_DEMO)


# La voz es parte del tutor: quien espera que aprueben su inscripción no la usa (403 "pendiente").
router = APIRouter(
    prefix="/api/voz", tags=["voz"], dependencies=[Depends(auth.alumno_aprobado), Depends(_sin_modo_demo)]
)

Alumno = Annotated[auth.Alumno, Depends(auth.alumno_aprobado)]


def _chequear_tope(con: sqlite3.Connection, settings: Settings, alumno_id: int) -> None:
    """La voz cuenta en el tope del tutor: con el tope alcanzado responde 402, como el tutor."""
    estado = costos.estado_tope(
        con, alumno_id, tope_alumno=settings.tope_alumno_usd, tope_mensual=settings.tope_mensual_usd
    )
    if estado["bloqueado"]:
        fila = dominio.alumno(con, alumno_id)
        modulo = min(max(int(fila["modulo_actual"]) if fila else 1, 1), 3)
        raise HTTPException(402, tutor.detalle_tope(estado["alcance"], modulo))


def _chequear_limite(request: Request, alumno_id: int) -> None:
    contador = getattr(request.app.state, "transcripciones", None)
    if contador is None:
        contador = request.app.state.transcripciones = ContadorTranscripciones()
    if not contador.registrar(alumno_id, reloj()):
        raise HTTPException(
            429, "Ya mandaste muchos audios en la última hora. Escribí tu mensaje o probá con la voz en un rato."
        )


@router.post("/transcribir")
async def transcribir_audio(
    audio: Annotated[UploadFile, File()],
    alumno: Alumno,
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    con: Annotated[sqlite3.Connection, Depends(conexion)],
) -> dict[str, str]:
    _chequear_tope(con, settings, alumno.id)
    _chequear_limite(request, alumno.id)
    datos = await audio.read(MAX_AUDIO_BYTES + 1)
    if len(datos) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "El audio supera los 15 MB.")
    if not datos:
        raise HTTPException(422, "El audio está vacío.")
    try:
        texto = await transcribir(datos, settings=settings, con=con, alumno_id=alumno.id)
    except AudioMuyLargo:
        raise HTTPException(413, "El audio es demasiado largo. Grabá uno más corto.") from None
    except AudioInvalido:
        raise HTTPException(422, "No pude leer el audio.") from None
    except ErrorVoz as error:
        log.warning("STT: %s", error)
        raise HTTPException(502, "No se pudo transcribir el audio. Probá de nuevo.") from None
    return {"texto": texto}


@router.post("/hablar")
async def hablar(
    pedido: PedidoHablar,
    alumno: Alumno,
    settings: Annotated[Settings, Depends(get_settings)],
    con: Annotated[sqlite3.Connection, Depends(conexion)],
) -> Response:
    _chequear_tope(con, settings, alumno.id)
    try:
        mp3 = await sintetizar(pedido.texto, settings=settings, con=con, alumno_id=alumno.id)
    except (ErrorVoz, AudioInvalido) as error:
        log.warning("TTS sin audio: %s", error)
        raise HTTPException(502, "No se pudo generar la voz.") from None
    return Response(mp3, media_type="audio/mpeg")
