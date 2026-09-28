import logging
import sqlite3
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

log = logging.getLogger("vibe_tutor.costos")

ZONA_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")
UMBRAL_AVISO = 0.8
MODELO_CLAUDE = "claude-sonnet-5"
MODELO_TTS = "gemini-3.8-flash-tts"
FORMATO_UTC = "%Y-%m-%dT%H:%M:%S+00:00"

# Precios en US$ por millón de tokens, verificados en las páginas oficiales el 28/9/2026
# (specs/001-curso-vibe-coding/research.md §5 y §10).
PRECIOS: dict[str, dict[str, float]] = {
    MODELO_CLAUDE: {
        "entrada": 2.00,
        "salida": 10.00,
        "cache_escritura": 2.50,
        "cache_escritura_1h": 4.00,
        "cache_lectura": 0.20,
    },
    "claude-opus-5": {
        "entrada": 5.00,
        "salida": 25.00,
        "cache_escritura": 6.25,
        "cache_escritura_1h": 10.00,
        "cache_lectura": 0.50,
    },
    "gemini-2.5-flash": {"entrada_texto": 0.30, "entrada_audio": 1.00, "salida": 2.50, "salida_audio": 2.50},
    MODELO_TTS: {"entrada_texto": 0.50, "entrada_audio": 0.50, "salida": 9.00, "salida_audio": 9.00},
    "gemini-3.8-flash-lite-tts": {"entrada_texto": 0.50, "entrada_audio": 0.50, "salida": 6.00, "salida_audio": 6.00},
    "gemini-2.5-flash-preview-tts": {"entrada_texto": 0.50, "entrada_audio": 0.50, "salida": 10.00, "salida_audio": 10.00},
}

# Aumentos anunciados: desde la fecha (hora de Argentina), la tarifa se reemplaza por esta.
AUMENTOS: dict[str, tuple[datetime, dict[str, float]]] = {
    MODELO_TTS: (
        datetime(2027, 1, 1, tzinfo=ZONA_ARGENTINA),
        {"entrada_texto": 1.00, "entrada_audio": 1.00, "salida": 18.00, "salida_audio": 18.00},
    ),
    "gemini-3.8-flash-lite-tts": (
        datetime(2027, 1, 1, tzinfo=ZONA_ARGENTINA),
        {"entrada_texto": 1.00, "entrada_audio": 1.00, "salida": 12.00, "salida_audio": 12.00},
    ),
}

_CAMPOS_GEMINI = ("entrada_texto", "entrada_audio", "salida", "salida_audio")


def _ahora_utc(ahora: datetime | None) -> datetime:
    ahora = ahora or datetime.now(timezone.utc)
    return ahora if ahora.tzinfo is not None else ahora.replace(tzinfo=timezone.utc)


def tarifa(modelo: str, momento: datetime | None = None) -> dict[str, float] | None:
    """Tarifa vigente del modelo en ese momento, o None si no hay precio cargado."""
    if modelo not in PRECIOS:
        return None
    aumento = AUMENTOS.get(modelo)
    if aumento and _ahora_utc(momento) >= aumento[0]:
        return aumento[1]
    return PRECIOS[modelo]


def _campo(origen: Any, nombre: str) -> Any:
    if origen is None:
        return None
    if isinstance(origen, Mapping):
        return origen.get(nombre)
    return getattr(origen, nombre, None)


def _entero(origen: Any, nombre: str) -> int:
    return int(_campo(origen, nombre) or 0)


def _partes_anthropic(usage: Any) -> list[Any]:
    return list(_campo(usage, "iterations") or [usage])


def _tarifa_claude(modelo: str | None, por_defecto: str) -> dict[str, float]:
    modelo = modelo or por_defecto
    if modelo.startswith("claude") and modelo in PRECIOS:
        return PRECIOS[modelo]
    log.warning("Sin precio para %s: se cobra la tarifa de Claude más alta", modelo)
    tarifas = [t for nombre, t in PRECIOS.items() if nombre.startswith("claude")]
    return {campo: max(t[campo] for t in tarifas) for campo in tarifas[0]}


def costo_anthropic(usage: Any, modelo: str = MODELO_CLAUDE) -> float:
    total = 0.0
    for parte in _partes_anthropic(usage):
        precio = _tarifa_claude(_campo(parte, "model") or _campo(usage, "model"), modelo)
        escritura = _entero(parte, "cache_creation_input_tokens")
        escritura_1h = min(_entero(_campo(parte, "cache_creation"), "ephemeral_1h_input_tokens"), escritura)
        total += (
            _entero(parte, "input_tokens") * precio["entrada"]
            + _entero(parte, "output_tokens") * precio["salida"]
            + (escritura - escritura_1h) * precio["cache_escritura"]
            + escritura_1h * precio["cache_escritura_1h"]
            + _entero(parte, "cache_read_input_tokens") * precio["cache_lectura"]
        )
    return total / 1_000_000


def _tarifa_gemini(modelo: str, momento: datetime | None) -> dict[str, float]:
    vigente = tarifa(modelo, momento)
    if vigente is not None:
        return vigente
    if modelo.endswith("-tts"):
        return tarifa(MODELO_TTS, momento)
    log.warning("Sin precio para %s: se cobra la tarifa Gemini más alta", modelo)
    tarifas = [tarifa(nombre, momento) for nombre in PRECIOS if nombre.startswith("gemini")]
    return {campo: max(t[campo] for t in tarifas) for campo in _CAMPOS_GEMINI}


def costo_gemini(
    modelo: str,
    entrada_texto: int,
    entrada_audio: int,
    salida: int,
    salida_audio: int,
    momento: datetime | None = None,
) -> float:
    precio = _tarifa_gemini(modelo, momento)
    return (
        entrada_texto * precio["entrada_texto"]
        + entrada_audio * precio["entrada_audio"]
        + salida * precio["salida"]
        + salida_audio * precio["salida_audio"]
    ) / 1_000_000


def _tokens_anthropic(usage: Any) -> dict[str, int]:
    partes = _partes_anthropic(usage)
    campos = {
        "input_tokens": "input_tokens",
        "output_tokens": "output_tokens",
        "cache_write": "cache_creation_input_tokens",
        "cache_read": "cache_read_input_tokens",
    }
    return {columna: sum(_entero(parte, campo) for parte in partes) for columna, campo in campos.items()}


def _normalizar_tokens(tokens: Any) -> dict[str, int]:
    if not isinstance(tokens, Mapping) or _campo(tokens, "iterations"):
        return _tokens_anthropic(tokens)
    return {
        "input_tokens": _entero(tokens, "input_tokens")
        or _entero(tokens, "entrada_texto") + _entero(tokens, "entrada_audio"),
        "output_tokens": _entero(tokens, "output_tokens")
        or _entero(tokens, "salida") + _entero(tokens, "salida_audio"),
        "cache_write": _entero(tokens, "cache_write") or _entero(tokens, "cache_creation_input_tokens"),
        "cache_read": _entero(tokens, "cache_read") or _entero(tokens, "cache_read_input_tokens"),
    }


def registrar(
    con: sqlite3.Connection,
    proveedor: str,
    modelo: str,
    tokens: Mapping[str, Any] | Any,
    costo: float,
    *,
    alumno_id: int | None = None,
    sesion_id: int | None = None,
) -> None:
    t = _normalizar_tokens(tokens)
    with con:
        con.execute(
            "INSERT INTO uso (alumno_id, sesion_id, proveedor, modelo, input_tokens, output_tokens,"
            " cache_write, cache_read, costo_usd) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                alumno_id,
                sesion_id,
                proveedor,
                modelo,
                t["input_tokens"],
                t["output_tokens"],
                t["cache_write"],
                t["cache_read"],
                costo,
            ),
        )
        if sesion_id is not None:
            con.execute("UPDATE sesiones SET costo_usd = costo_usd + ? WHERE id = ?", (costo, sesion_id))


def _limites_mes(ahora: datetime | None) -> tuple[str, str]:
    inicio = _ahora_utc(ahora).astimezone(ZONA_ARGENTINA).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if inicio.month == 12:
        fin = inicio.replace(year=inicio.year + 1, month=1)
    else:
        fin = inicio.replace(month=inicio.month + 1)
    return (
        inicio.astimezone(timezone.utc).strftime(FORMATO_UTC),
        fin.astimezone(timezone.utc).strftime(FORMATO_UTC),
    )


def mes_actual(con: sqlite3.Connection, ahora: datetime | None = None) -> float:
    inicio, fin = _limites_mes(ahora)
    total = con.execute(
        "SELECT SUM(costo_usd) FROM uso WHERE creado >= ? AND creado < ?", (inicio, fin)
    ).fetchone()[0]
    return float(total or 0.0)


def gasto_alumno(con: sqlite3.Connection, alumno_id: int) -> float:
    total = con.execute("SELECT SUM(costo_usd) FROM uso WHERE alumno_id = ?", (alumno_id,)).fetchone()[0]
    return float(total or 0.0)


def estado_tope(
    con: sqlite3.Connection,
    alumno_id: int | None,
    *,
    tope_alumno: float,
    tope_mensual: float,
    ahora: datetime | None = None,
) -> dict:
    gastado_mes = round(mes_actual(con, ahora), 6)
    gastado_alumno = round(gasto_alumno(con, alumno_id), 6) if alumno_id is not None else 0.0
    if gastado_mes >= tope_mensual:
        alcance = "mes"
    elif alumno_id is not None and gastado_alumno >= tope_alumno:
        alcance = "alumno"
    else:
        alcance = None
    return {
        "gastado_mes": gastado_mes,
        "tope_mensual": float(tope_mensual),
        "gastado_alumno": gastado_alumno,
        "tope_alumno": float(tope_alumno),
        "aviso": gastado_mes >= round(tope_mensual * UMBRAL_AVISO, 6),
        "bloqueado": alcance is not None,
        "alcance": alcance,
    }
