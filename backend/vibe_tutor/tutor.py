"""Ciclo del tutor de la web: una conversación por alumno y módulo, con herramientas y SSE.

Sin respaldo ante rechazos ni compactación: cada módulo es una conversación corta (research §2).
El tope de costo se chequea antes de cada llamada al modelo. Las capturas viajan solo en las
llamadas del turno en que se mandan; en la base queda un marcador de texto (FR-011). Con
MODO_DEMO el cliente de Claude se reemplaza por el guion fijo de demo.py, sin costo.
"""

import asyncio
import base64
import json
import logging
import sqlite3
import weakref
from collections.abc import AsyncIterator, Callable
from contextlib import aclosing, closing
from dataclasses import dataclass, field
from typing import Any

import anthropic

from vibe_tutor import costos, demo, dominio, herramientas, prompts
from vibe_tutor.config import Settings

log = logging.getLogger("vibe_tutor.tutor")

MAX_TOKENS = 16000
MAX_VUELTAS = 6
MAX_IMAGEN_BYTES = 5 * 1024 * 1024
MARCA_CAPTURA = "[captura de pantalla enviada]"
CODIGOS_REINTENTABLES = {408, 409}
# Regla de esfuerzo (research §2): "low" para conversar y "medium" en el tramo de cierre del
# módulo, que es cuando el tutor guarda la idea o marca el avance. El tramo de cierre arranca con
# este número de mensajes del alumno en la sesión (contando el del turno), según el presupuesto
# de respuestas de cada módulo en contenido/curriculo.md. El esfuerzo no cambia dentro de un turno.
UMBRAL_CIERRE = {1: 5, 2: 10, 3: 10}

TEXTO_RECHAZO = "Prefiero no responder ese mensaje. Si querés, contámelo de otra forma y seguimos."
TEXTO_VACIO = "(La respuesta quedó vacía.)"
RESULTADO_INTERRUMPIDO = (
    "Sin resultado: el turno se interrumpió antes de terminar esta herramienta. "
    "Si guardaba algo, revisá el estado antes de repetirla."
)
RESULTADO_LIMITE = (
    f"No se ejecutó: se alcanzó el límite de {MAX_VUELTAS} rondas de herramientas en este turno. "
    "Respondé con lo que ya tenés."
)
RESULTADO_TRUNCADO = (
    "No se ejecutó: la respuesta se cortó por largo antes de completar la entrada de la herramienta. "
    "Si la necesitás, pedila de nuevo con una entrada más corta."
)
RESULTADOS_NO_EJECUTADOS = {"tool_use": RESULTADO_LIMITE, "max_tokens": RESULTADO_TRUNCADO}


class TopeAlcanzado(Exception):
    def __init__(self, alcance: str):
        super().__init__(f"tope alcanzado ({alcance})")
        self.alcance = alcance


@dataclass(frozen=True)
class EventoSSE:
    tipo: str
    datos: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Imagen:
    media_type: str
    datos: bytes

    def bloque(self) -> dict:
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": self.media_type, "data": base64.b64encode(self.datos).decode()},
        }


def tipo_imagen(datos: bytes) -> str | None:
    """El tipo real de la captura según sus primeros bytes: PNG, JPEG o WebP; si no, None."""
    if datos.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if datos.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if len(datos) >= 12 and datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    return None


def esfuerzo(modulo: int, mensajes_del_alumno: int) -> str:
    return "medium" if mensajes_del_alumno >= UMBRAL_CIERRE[modulo] else "low"


def _datos_tope(alcance: str, modulo: int) -> dict:
    return {"alcance": alcance, "guia": f"/api/modulos/{modulo}/guia"}


def detalle_tope(alcance: str, modulo: int) -> dict:
    """Cuerpo del 402 del contrato: el tutor está bloqueado y el alumno pasa a la guía escrita."""
    return {"detalle": "tope", **_datos_tope(alcance, modulo)}


def _texto(texto: str) -> dict:
    return {"type": "text", "text": texto}


def _resultado(tool_use_id: str, texto: str, es_error: bool = False) -> dict:
    bloque = {"type": "tool_result", "tool_use_id": tool_use_id, "content": texto}
    if es_error:
        bloque["is_error"] = True
    return bloque


def _error(mensaje: str, reintentable: bool) -> EventoSSE:
    return EventoSSE("error", {"mensaje": mensaje, "reintentable": reintentable})


def _a_dict(bloque: Any) -> dict:
    return dict(bloque) if isinstance(bloque, dict) else bloque.to_dict(mode="json")


def _pedidos(contenido: list[dict]) -> list[dict]:
    return [b for b in contenido if b.get("type") == "tool_use"]


def _guardable(contenido: list[dict]) -> list[dict]:
    if any(bloque.get("type") in ("text", "tool_use") for bloque in contenido):
        return contenido
    return [*contenido, _texto(TEXTO_VACIO)]


def _completar_resultados(asistente: list[dict], usuario: list[dict]) -> list[dict]:
    resultados = [b for b in usuario if b.get("type") == "tool_result"]
    respondidos = {b.get("tool_use_id") for b in resultados}
    faltantes = [
        _resultado(b["id"], RESULTADO_INTERRUMPIDO, es_error=True)
        for b in asistente
        if b.get("type") == "tool_use" and b.get("id") not in respondidos
    ]
    return resultados + faltantes + [b for b in usuario if b.get("type") != "tool_result"]


def construir_mensajes(filas: list[tuple[str, list[dict]]]) -> list[dict]:
    """Une filas seguidas del mismo rol y repara tool_use sin su tool_result."""
    mensajes: list[dict] = []
    for rol, contenido in filas:
        bloques = list(contenido)
        if mensajes and mensajes[-1]["role"] == rol:
            mensajes[-1]["content"].extend(bloques)
        else:
            mensajes.append({"role": rol, "content": bloques})
    reparados: list[dict] = []
    for mensaje in mensajes:
        if mensaje["role"] == "user" and reparados:
            mensaje = {"role": "user", "content": _completar_resultados(reparados[-1]["content"], mensaje["content"])}
        reparados.append(mensaje)
    if reparados and reparados[-1]["role"] == "assistant":
        faltantes = _completar_resultados(reparados[-1]["content"], [])
        if faltantes:
            reparados.append({"role": "user", "content": faltantes})
    return reparados


def filas_de(con: sqlite3.Connection, sesion_id: int) -> list[tuple[int, str, list[dict]]]:
    consulta = con.execute(
        "SELECT orden, rol, contenido_json FROM mensajes WHERE sesion_id = ? ORDER BY orden", (sesion_id,)
    )
    return [(fila["orden"], fila["rol"], json.loads(fila["contenido_json"])) for fila in consulta]


def es_del_alumno(indice: int, rol: str, contenido: list[dict]) -> bool:
    """Una fila escrita por el alumno: ni el mensaje de estado (la primera) ni resultados de herramientas."""
    return indice > 0 and rol == "user" and any(b.get("type") == "text" for b in contenido)


def pendiente(filas: list[tuple[int, str, list[dict]]]) -> bool:
    """Si la sesión espera una respuesta del tutor."""
    mensajes = construir_mensajes([(rol, contenido) for _, rol, contenido in filas])
    return bool(mensajes) and mensajes[-1]["role"] == "user"


def _insertar(con: sqlite3.Connection, sesion_id: int, rol: str, contenido: list[dict]) -> int:
    with con:
        fila = con.execute(
            "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES "
            "(?, (SELECT COALESCE(MAX(orden), -1) + 1 FROM mensajes WHERE sesion_id = ?), ?, ?) RETURNING orden",
            (sesion_id, sesion_id, rol, json.dumps(contenido, ensure_ascii=False)),
        ).fetchone()
    return int(fila["orden"])


def _error_api(error: Exception) -> EventoSSE:
    if isinstance(error, anthropic.APIStatusError):
        codigo = error.status_code
        if codigo == 429:
            return _error("El tutor está saturado en este momento. Esperá unos segundos y tocá Reintentar.", True)
        if codigo >= 500 or codigo in CODIGOS_REINTENTABLES:
            return _error("El tutor tuvo un problema técnico. Tu mensaje quedó guardado: tocá Reintentar.", True)
        return _error("El tutor no pudo procesar este mensaje. Quedó registrado para revisarlo.", False)
    if isinstance(error, anthropic.APIConnectionError):
        return _error("Se cortó la conexión con el tutor. Tu mensaje quedó guardado: tocá Reintentar.", True)
    return _error("La respuesta llegó incompleta. Tu mensaje quedó guardado: tocá Reintentar.", True)


def _no_ejecutadas(iniciadas: dict[str, str], ejecutadas: set[str]) -> list[EventoSSE]:
    return [
        EventoSSE("herramienta", {"nombre": nombre, "estado": "fin", "error": True})
        for id_, nombre in iniciadas.items()
        if id_ not in ejecutadas
    ]


class Tutor:
    def __init__(self, settings: Settings, con_factory: Callable[[], sqlite3.Connection], cliente=None):
        self.settings = settings
        self._con_factory = con_factory
        if cliente is None and settings.modo_demo:
            cliente = demo.ClienteDemo()
        self.cliente = cliente or anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._candados: weakref.WeakValueDictionary[int, asyncio.Lock] = weakref.WeakValueDictionary()

    def _alcance_tope(self, con: sqlite3.Connection, alumno_id: int) -> str | None:
        estado = costos.estado_tope(
            con, alumno_id, tope_alumno=self.settings.tope_alumno_usd, tope_mensual=self.settings.tope_mensual_usd
        )
        return estado["alcance"] if estado["bloqueado"] else None

    def abrir_sesion(self, alumno_id: int, modulo: int) -> tuple[int, bool]:
        """Retoma la sesión abierta del módulo o crea una nueva con el mensaje de estado.

        Devuelve (id, retomada). Levanta TopeAlcanzado si el tutor está bloqueado para el alumno.
        """
        if modulo not in prompts.MODULOS:
            raise ValueError(f"el tutor de la web cubre los módulos 1 a 3 (llegó {modulo})")
        with closing(self._con_factory()) as con:
            alcance = self._alcance_tope(con, alumno_id)
            if alcance is not None:
                raise TopeAlcanzado(alcance)
            with con:
                con.execute("BEGIN IMMEDIATE")
                abierta = con.execute(
                    "SELECT id FROM sesiones WHERE alumno_id = ? AND modulo = ? AND fin IS NULL "
                    "ORDER BY id DESC LIMIT 1",
                    (alumno_id, modulo),
                ).fetchone()
                if abierta is not None:
                    return int(abierta["id"]), True
                inicio = prompts.mensaje_inicio(con, alumno_id, modulo)
                sesion_id = con.execute(
                    "INSERT INTO sesiones (alumno_id, modulo) VALUES (?, ?)", (alumno_id, modulo)
                ).lastrowid
                con.execute(
                    "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 0, 'user', ?)",
                    (sesion_id, json.dumps([_texto(inicio)], ensure_ascii=False)),
                )
            return int(sesion_id), False

    async def turno(
        self, sesion_id: int, alumno_id: int, texto: str | None = None, imagen: Imagen | None = None
    ) -> AsyncIterator[EventoSSE]:
        candado = self._candados.setdefault(sesion_id, asyncio.Lock())
        if candado.locked():
            yield _error("Ya hay una respuesta en curso en esta conversación.", False)
            return
        async with candado:
            with closing(self._con_factory()) as con:
                async with aclosing(self._turno(con, sesion_id, alumno_id, texto, imagen)) as eventos:
                    async for evento in eventos:
                        yield evento

    async def _turno(
        self, con: sqlite3.Connection, sesion_id: int, alumno_id: int, texto: str | None, imagen: Imagen | None
    ) -> AsyncIterator[EventoSSE]:
        sesion = con.execute("SELECT alumno_id, modulo FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()
        if sesion is None or sesion["alumno_id"] != alumno_id:
            yield _error("Esa conversación no existe.", False)
            return
        modulo = int(sesion["modulo"])
        texto = (texto or "").strip() or None
        nuevos = ([_texto(MARCA_CAPTURA)] if imagen else []) + ([_texto(texto)] if texto else [])
        if not nuevos and not pendiente(filas_de(con, sesion_id)):
            yield _error("No hay ningún mensaje nuevo para responder.", False)
            return
        alcance = self._alcance_tope(con, alumno_id)
        if alcance is not None:
            yield EventoSSE("tope", _datos_tope(alcance, modulo))
            return
        orden_nuevo = _insertar(con, sesion_id, "user", nuevos) if nuevos else None
        dominio.tocar_actividad(con, alumno_id)

        contexto = herramientas.Contexto(
            alumno_id=alumno_id, sesion_id=sesion_id, modulo=modulo, contenido_dir=self.settings.contenido_dir
        )
        filas = filas_de(con, sesion_id)
        nivel = esfuerzo(modulo, sum(es_del_alumno(i, rol, c) for i, (_, rol, c) in enumerate(filas)))
        system = prompts.construir_system(self.settings.contenido_dir, modulo, self.settings)
        tools = herramientas.tools_de(modulo)
        vueltas = 0
        while True:
            if vueltas:
                alcance = self._alcance_tope(con, alumno_id)
                if alcance is not None:
                    yield EventoSSE("tope", _datos_tope(alcance, modulo))
                    return
            yield EventoSSE("pensando", {})
            params = {
                "model": self.settings.modelo,
                "max_tokens": MAX_TOKENS,
                "system": system,
                "tools": tools,
                "messages": self._mensajes(con, sesion_id, orden_nuevo, imagen),
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": nivel},
                "cache_control": prompts.CACHE_CONTROL,
            }
            iniciadas: dict[str, str] = {}
            stream = None
            final = None
            falla: Exception | None = None
            try:
                async with self.cliente.messages.stream(**params) as stream:
                    async for evento in stream:
                        if evento.type == "text" and evento.text:
                            yield EventoSSE("texto", {"delta": evento.text})
                        elif evento.type == "content_block_start" and evento.content_block.type == "tool_use":
                            iniciadas[evento.content_block.id] = evento.content_block.name
                            yield EventoSSE(
                                "herramienta", {"nombre": evento.content_block.name, "estado": "inicio", "error": False}
                            )
                    mensaje = await stream.get_final_message()
                    if mensaje.stop_reason is None:
                        raise ValueError("el stream terminó sin stop_reason")
                    final = mensaje
            except Exception as error:
                falla = error
            finally:
                if final is None:
                    self._registrar_parcial(con, alumno_id, sesion_id, stream)
            if falla is not None:
                log.warning(
                    "falló la llamada a Claude (sesión %s): %r",
                    sesion_id,
                    falla,
                    exc_info=not isinstance(falla, anthropic.APIError),
                )
                for evento in _no_ejecutadas(iniciadas, set()):
                    yield evento
                yield _error_api(falla)
                return

            contenido = [_a_dict(bloque) for bloque in final.content]
            costos.registrar(
                con,
                "anthropic",
                final.model or self.settings.modelo,
                final.usage,
                self._costo(final.usage),
                alumno_id=alumno_id,
                sesion_id=sesion_id,
            )

            if final.stop_reason == "refusal":
                _insertar(con, sesion_id, "assistant", [_texto(TEXTO_RECHAZO)])
                for evento in _no_ejecutadas(iniciadas, set()):
                    yield evento
                yield _error(TEXTO_RECHAZO, False)
                return

            _insertar(con, sesion_id, "assistant", _guardable(contenido))
            pedidos = _pedidos(contenido)
            if not pedidos:
                for evento in _no_ejecutadas(iniciadas, set()):
                    yield evento
                yield EventoSSE("fin", {"stop_reason": final.stop_reason})
                return

            if final.stop_reason != "tool_use" or vueltas >= MAX_VUELTAS:
                motivo = RESULTADOS_NO_EJECUTADOS.get(final.stop_reason, RESULTADO_INTERRUMPIDO)
                _insertar(con, sesion_id, "user", [_resultado(p["id"], motivo, es_error=True) for p in pedidos])
                for evento in _no_ejecutadas(iniciadas, set()):
                    yield evento
                if final.stop_reason == "tool_use":
                    yield _error("El tutor se trabó encadenando pasos y lo corté. Escribile cómo seguir.", False)
                else:
                    yield _error("La respuesta se cortó antes de terminar. Tocá Reintentar para que siga.", True)
                return

            vueltas += 1
            resultados = []
            posteriores: list[EventoSSE] = []
            for pedido in pedidos:
                resultado = self._ejecutar(con, contexto, pedido)
                resultados.append(_resultado(pedido["id"], resultado.texto, resultado.es_error))
                yield EventoSSE("herramienta", {"nombre": pedido["name"], "estado": "fin", "error": resultado.es_error})
                posteriores += [EventoSSE(tipo, datos) for tipo, datos in resultado.eventos]
            for evento in _no_ejecutadas(iniciadas, {p["id"] for p in pedidos}):
                yield evento
            _insertar(con, sesion_id, "user", resultados)
            for evento in posteriores:
                yield evento

    def _costo(self, usage) -> float:
        """Lo que costó una llamada; en el modo demo no se llama a Claude y cuesta 0."""
        return 0.0 if self.settings.modo_demo else costos.costo_anthropic(usage, self.settings.modelo)

    def _mensajes(
        self, con: sqlite3.Connection, sesion_id: int, orden_nuevo: int | None, imagen: Imagen | None
    ) -> list[dict]:
        """Los mensajes para la API; la captura del turno reemplaza a su marcador solo en memoria."""
        filas = []
        for orden, rol, contenido in filas_de(con, sesion_id):
            if imagen is not None and orden == orden_nuevo:
                contenido = [imagen.bloque() if b == _texto(MARCA_CAPTURA) else b for b in contenido]
            filas.append((rol, contenido))
        return construir_mensajes(filas)

    def _ejecutar(self, con: sqlite3.Connection, contexto: herramientas.Contexto, pedido: dict):
        try:
            return herramientas.ejecutar(con, contexto, pedido["name"], pedido.get("input"))
        except Exception:
            log.exception("falló la herramienta %s", pedido.get("name"))
            return herramientas.ResultadoHerramienta(f"Error inesperado al ejecutar {pedido.get('name')}.", es_error=True)

    def _registrar_parcial(self, con: sqlite3.Connection, alumno_id: int, sesion_id: int, stream) -> None:
        if stream is None:
            return
        try:
            parcial = stream.current_message_snapshot
            costo = self._costo(parcial.usage)
            costos.registrar(
                con,
                "anthropic",
                parcial.model or self.settings.modelo,
                parcial.usage,
                costo,
                alumno_id=alumno_id,
                sesion_id=sesion_id,
            )
        except Exception:
            log.debug("sin uso parcial para registrar (sesión %s)", sesion_id, exc_info=True)
