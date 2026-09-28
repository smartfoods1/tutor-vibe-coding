import asyncio
import base64
import json
import math
import struct
import subprocess
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from vibe_tutor import auth, costos, db, dominio, errores, voz
from vibe_tutor.config import get_settings

FIXTURES = Path(__file__).parent / "fixtures"
URL_STT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
URL_TTS = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash-tts:generateContent"
URL_TTS_RESPALDO = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
)
USO_STT = {
    "promptTokenCount": 100_000,
    "candidatesTokenCount": 10_000,
    "totalTokenCount": 110_000,
    "promptTokensDetails": [
        {"modality": "TEXT", "tokenCount": 40_000},
        {"modality": "AUDIO", "tokenCount": 60_000},
    ],
}
USO_TTS = {
    "promptTokenCount": 20_000,
    "candidatesTokenCount": 50_000,
    "totalTokenCount": 70_000,
    "promptTokensDetails": [{"modality": "TEXT", "tokenCount": 20_000}],
    "candidatesTokensDetails": [{"modality": "AUDIO", "tokenCount": 50_000}],
}


def _es_mp3(datos: bytes) -> bool:
    return datos[:3] == b"ID3" or datos[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")


def _sondear(datos: bytes, tmp_path: Path) -> dict:
    archivo = tmp_path / "sondeo.mp3"
    archivo.write_bytes(datos)
    salida = subprocess.run(
        [
            "ffprobe", "-v", "error", "-of", "json",
            "-show_entries", "stream=codec_name,sample_rate,channels:format=duration",
            str(archivo),
        ],
        capture_output=True,
        check=True,
    )
    info = json.loads(salida.stdout)
    pista = info["streams"][0]
    return {
        "codec": pista["codec_name"],
        "frecuencia": int(pista["sample_rate"]),
        "canales": pista["channels"],
        "duracion": float(info["format"]["duration"]),
    }


def _pcm(segundos: float = 0.5, frecuencia: int = 24000) -> bytes:
    muestras = int(segundos * frecuencia)
    return b"".join(
        struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * n / frecuencia)))
        for n in range(muestras)
    )


def _respuesta_texto(texto: str | None, uso: dict | None = None) -> dict:
    partes = [] if texto is None else [{"text": texto}]
    return {
        "candidates": [{"content": {"role": "model", "parts": partes}, "finishReason": "STOP"}],
        "usageMetadata": uso or USO_STT,
    }


def _respuesta_audio(pcm: bytes, mime: str = "audio/L16;codec=pcm;rate=24000") -> dict:
    return {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"inlineData": {"mimeType": mime, "data": base64.b64encode(pcm).decode()}}],
                },
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": USO_TTS,
    }


def _usos(con) -> list[dict]:
    return [dict(fila) for fila in con.execute("SELECT * FROM uso ORDER BY id")]


def _app(settings_tmp, con) -> FastAPI:
    app = FastAPI()
    errores.instalar(app)
    app.include_router(voz.router)
    app.dependency_overrides[get_settings] = lambda: settings_tmp
    app.dependency_overrides[voz.conexion] = lambda: con
    return app


@pytest.fixture
def alumno_id(con):
    return dominio.crear_alumno(con, "ana@example.com", fuente=None)


@pytest.fixture
def cliente(settings_tmp, con, alumno_id):
    app = _app(settings_tmp, con)
    app.dependency_overrides[auth.alumno_actual] = lambda: auth.Alumno(id=alumno_id, email="ana@example.com", es_admin=False)
    return TestClient(app)


@pytest.mark.parametrize("archivo", ["hola.webm", "hola.m4a"])
@pytest.mark.parametrize("mono_16k", [True, False])
async def test_a_mp3_webm_y_m4a(archivo, mono_16k, tmp_path):
    original = (FIXTURES / archivo).read_bytes()

    mp3 = await voz.a_mp3(original, mono_16k=mono_16k)

    assert _es_mp3(mp3)
    info = _sondear(mp3, tmp_path)
    assert info["codec"] == "mp3"
    assert info["duracion"] == pytest.approx(1.86, abs=0.2)
    if mono_16k:
        assert (info["frecuencia"], info["canales"]) == (16000, 1)


async def test_a_mp3_m4a_con_moov_al_final(tmp_path):
    origen = tmp_path / "largo.m4a"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=10",
            "-ac", "1", "-c:a", "aac", "-b:a", "64k", str(origen),
        ],
        check=True,
    )
    datos = origen.read_bytes()
    assert datos.index(b"mdat") < datos.index(b"moov")

    mp3 = await voz.a_mp3(datos, mono_16k=True)

    assert _sondear(mp3, tmp_path)["duracion"] == pytest.approx(10, abs=0.3)


async def test_a_mp3_rechaza_basura():
    with pytest.raises(voz.AudioInvalido):
        await voz.a_mp3(b"esto no es audio", mono_16k=True)


async def test_a_mp3_rechaza_formato_no_permitido(tmp_path):
    origen = tmp_path / "audio.avi"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:a", "pcm_s16le", str(origen),
        ],
        check=True,
    )

    with pytest.raises(voz.AudioInvalido):
        await voz.a_mp3(origen.read_bytes(), mono_16k=True)


@pytest.mark.parametrize("archivo", ["hola.webm", "hola.m4a"])
async def test_transcribir_envia_mp3_y_thinking_0(archivo, respx_mock, settings_tmp, con):
    ruta = respx_mock.post(URL_STT).mock(
        return_value=httpx.Response(200, json=_respuesta_texto(" hola, esta es una prueba \n"))
    )

    texto = await voz.transcribir((FIXTURES / archivo).read_bytes(), settings=settings_tmp, con=con)

    assert texto == "hola, esta es una prueba"
    pedido = ruta.calls.last.request
    assert pedido.headers["x-goog-api-key"] == "gemini-prueba"
    assert "gemini-prueba" not in str(pedido.url)
    cuerpo = json.loads(pedido.content)
    partes = cuerpo["contents"][0]["parts"]
    audio = next(p["inline_data"] for p in partes if "inline_data" in p)
    assert audio["mime_type"] == "audio/mp3"
    assert _es_mp3(base64.b64decode(audio["data"]))
    instruccion = " ".join(p["text"] for p in partes if "text" in p)
    for termino in ("rioplatense", "voseo", "vibe coding", "Claude", "Codex", "ChatGPT", "Netlify", "carpeta", "link"):
        assert termino in instruccion
    config = cuerpo["generationConfig"]
    assert config["thinkingConfig"]["thinkingBudget"] == 0
    assert config["temperature"] == 0
    assert "2.0-flash" not in str(pedido.url)
    [uso] = _usos(con)
    assert (uso["proveedor"], uso["modelo"]) == ("gemini", "gemini-2.5-flash")
    assert uso["costo_usd"] == pytest.approx(0.012 + 0.06 + 0.025, abs=1e-6)
    assert uso["alumno_id"] is None


async def test_transcribir_y_sintetizar_registran_el_alumno(respx_mock, settings_tmp, con, alumno_id):
    respx_mock.post(URL_STT).mock(return_value=httpx.Response(200, json=_respuesta_texto("hola")))
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=_respuesta_audio(_pcm())))

    await voz.transcribir((FIXTURES / "hola.webm").read_bytes(), settings=settings_tmp, con=con, alumno_id=alumno_id)
    await voz.sintetizar("Hola.", settings=settings_tmp, con=con, alumno_id=alumno_id)

    assert [(u["modelo"], u["alumno_id"], u["sesion_id"]) for u in _usos(con)] == [
        ("gemini-2.5-flash", alumno_id, None),
        ("gemini-3.8-flash-tts", alumno_id, None),
    ]
    assert costos.gasto_alumno(con, alumno_id) > 0


@pytest.mark.parametrize(
    "respuesta",
    [
        _respuesta_texto(None),
        _respuesta_texto("   \n"),
        {"candidates": [], "usageMetadata": USO_STT},
        {"usageMetadata": USO_STT},
    ],
)
async def test_transcripcion_vacia(respuesta, respx_mock, settings_tmp, con):
    respx_mock.post(URL_STT).mock(return_value=httpx.Response(200, json=respuesta))

    texto = await voz.transcribir((FIXTURES / "hola.webm").read_bytes(), settings=settings_tmp, con=con)

    assert texto == ""


async def test_firmas_del_plan_registran_en_base_nueva(respx_mock, settings_tmp, monkeypatch):
    monkeypatch.setattr(voz, "get_settings", lambda: settings_tmp)
    respx_mock.post(URL_STT).mock(return_value=httpx.Response(200, json=_respuesta_texto("hola")))
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=_respuesta_audio(_pcm())))

    texto = await voz.transcribir((FIXTURES / "hola.webm").read_bytes())
    mp3 = await voz.sintetizar("Hola.")

    assert texto == "hola"
    assert _es_mp3(mp3)
    base = db.conectar(settings_tmp.data_dir / db.ARCHIVO)
    try:
        assert [u["modelo"] for u in _usos(base)] == ["gemini-2.5-flash", "gemini-3.8-flash-tts"]
    finally:
        base.close()


async def test_transcribir_error_de_gemini(respx_mock, settings_tmp, con):
    respx_mock.post(URL_STT).mock(return_value=httpx.Response(503, json={"error": {"code": 503}}))

    with pytest.raises(voz.ErrorVoz):
        await voz.transcribir((FIXTURES / "hola.webm").read_bytes(), settings=settings_tmp, con=con)
    assert _usos(con) == []


async def test_sintetizar_primer_modelo(respx_mock, settings_tmp, con, tmp_path):
    principal = respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=_respuesta_audio(_pcm())))
    respaldo = respx_mock.post(URL_TTS_RESPALDO)

    mp3 = await voz.sintetizar("Saturno está en Piscis.", settings=settings_tmp, con=con)

    assert _es_mp3(mp3)
    assert _sondear(mp3, tmp_path)["duracion"] == pytest.approx(0.5, abs=0.15)
    assert principal.call_count == 1
    assert respaldo.call_count == 0
    cuerpo = json.loads(principal.calls.last.request.content)
    # El texto va solo, sin instrucción de estilo: el TTS la leería en voz alta.
    assert cuerpo["contents"][0]["parts"][0]["text"] == "Saturno está en Piscis."
    assert "systemInstruction" not in cuerpo
    config = cuerpo["generationConfig"]
    assert config["responseModalities"] == ["AUDIO"]
    assert config["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]["voiceName"] == "Charon"
    [uso] = _usos(con)
    assert (uso["proveedor"], uso["modelo"]) == ("gemini", "gemini-3.8-flash-tts")
    vigente = costos.tarifa("gemini-3.8-flash-tts")
    esperado = (20_000 * vigente["entrada_texto"] + 50_000 * vigente["salida_audio"]) / 1_000_000
    assert uso["costo_usd"] == pytest.approx(esperado, abs=1e-6)


async def test_sintetizar_respaldo(respx_mock, settings_tmp, con, tmp_path):
    principal = respx_mock.post(URL_TTS).mock(return_value=httpx.Response(500, json={"error": {"code": 500}}))
    respaldo = respx_mock.post(URL_TTS_RESPALDO).mock(
        return_value=httpx.Response(200, json=_respuesta_audio(_pcm(1.0, 16000), "audio/L16;codec=pcm;rate=16000"))
    )

    mp3 = await voz.sintetizar("Hola, Ana.", settings=settings_tmp, con=con)

    assert _es_mp3(mp3)
    assert _sondear(mp3, tmp_path)["duracion"] == pytest.approx(1.0, abs=0.15)
    assert principal.call_count == 1
    assert respaldo.call_count == 1
    [uso] = _usos(con)
    assert uso["modelo"] == "gemini-2.5-flash-preview-tts"


async def test_sintetizar_respaldo_si_no_hay_audio(respx_mock, settings_tmp, con):
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=_respuesta_texto(None, USO_TTS)))
    respaldo = respx_mock.post(URL_TTS_RESPALDO).mock(
        return_value=httpx.Response(200, json=_respuesta_audio(_pcm()))
    )

    mp3 = await voz.sintetizar("Hola.", settings=settings_tmp, con=con)

    assert _es_mp3(mp3)
    assert respaldo.call_count == 1


async def test_sintetizar_respaldo_si_audio_ilegible(respx_mock, settings_tmp, con):
    ilegible = _respuesta_audio(b"")
    ilegible["candidates"][0]["content"]["parts"][0]["inlineData"]["data"] = "abc"
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=ilegible))
    respaldo = respx_mock.post(URL_TTS_RESPALDO).mock(
        return_value=httpx.Response(200, json=_respuesta_audio(_pcm()))
    )

    mp3 = await voz.sintetizar("Hola.", settings=settings_tmp, con=con)

    assert _es_mp3(mp3)
    assert respaldo.call_count == 1


async def test_sintetizar_ambos_fallan(respx_mock, settings_tmp, con):
    respx_mock.post(URL_TTS).mock(side_effect=httpx.ConnectError("sin red"))
    respx_mock.post(URL_TTS_RESPALDO).mock(return_value=httpx.Response(500))

    with pytest.raises(voz.ErrorVoz):
        await voz.sintetizar("Hola.", settings=settings_tmp, con=con)


@pytest.mark.parametrize(
    ("archivo", "tipo"),
    [("hola.webm", "audio/webm;codecs=opus"), ("hola.m4a", "audio/mp4")],
)
def test_endpoint_transcribir(archivo, tipo, cliente, respx_mock, con):
    ruta = respx_mock.post(URL_STT).mock(
        return_value=httpx.Response(200, json=_respuesta_texto("hola, esta es una prueba"))
    )

    respuesta = cliente.post(
        "/api/voz/transcribir",
        files={"audio": (archivo, (FIXTURES / archivo).read_bytes(), tipo)},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"texto": "hola, esta es una prueba"}
    audio = json.loads(ruta.calls.last.request.content)["contents"][0]["parts"][1]["inline_data"]
    assert _es_mp3(base64.b64decode(audio["data"]))
    [uso] = _usos(con)
    assert uso["alumno_id"] is not None


def test_endpoint_transcribir_limites(cliente, respx_mock):
    ruta = respx_mock.post(URL_STT)

    grande = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("a.webm", b"\0" * (15 * 1024 * 1024 + 1), "audio/webm")},
    )
    vacio = cliente.post("/api/voz/transcribir", files={"audio": ("a.webm", b"", "audio/webm")})
    basura = cliente.post("/api/voz/transcribir", files={"audio": ("a.webm", b"no es audio", "audio/webm")})

    assert grande.status_code == 413
    assert vacio.status_code == 422
    assert basura.status_code == 422
    assert ruta.call_count == 0


def test_endpoint_transcribir_gemini_caido(cliente, respx_mock):
    respx_mock.post(URL_STT).mock(return_value=httpx.Response(500))

    respuesta = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("hola.webm", (FIXTURES / "hola.webm").read_bytes(), "audio/webm")},
    )

    assert respuesta.status_code == 502


def test_endpoint_hablar(cliente, respx_mock, con, alumno_id):
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(200, json=_respuesta_audio(_pcm())))

    respuesta = cliente.post("/api/voz/hablar", json={"texto": "Hola, ¿cómo va?"})

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "audio/mpeg"
    assert _es_mp3(respuesta.content)
    assert [u["alumno_id"] for u in _usos(con)] == [alumno_id]


@pytest.mark.parametrize(("quien", "alcance"), [("alumno", "alumno"), ("otro", "mes")])
def test_voz_con_tope_responde_402(cliente, respx_mock, con, alumno_id, quien, alcance):
    stt = respx_mock.post(URL_STT)
    tts = respx_mock.post(URL_TTS)
    if quien == "alumno":
        costos.registrar(con, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=alumno_id)
    else:
        otro = dominio.crear_alumno(con, "beto@example.com", fuente=None)
        costos.registrar(con, "anthropic", "claude-sonnet-5", {}, 50.0, alumno_id=otro)
    dominio.completar_modulo(con, alumno_id, 1, "guia_escrita")

    transcribir = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("hola.webm", (FIXTURES / "hola.webm").read_bytes(), "audio/webm")},
    )
    hablar = cliente.post("/api/voz/hablar", json={"texto": "Hola."})

    esperado = {"detalle": "tope", "alcance": alcance, "guia": "/api/modulos/2/guia"}
    assert (transcribir.status_code, transcribir.json()) == (402, esperado)
    assert (hablar.status_code, hablar.json()) == (402, esperado)
    assert stt.call_count == 0
    assert tts.call_count == 0


def test_voz_con_tope_desde_el_modulo_4_manda_a_la_guia_3(cliente, respx_mock, con, alumno_id):
    costos.registrar(con, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=alumno_id)
    with con:
        con.execute("UPDATE alumnos SET modulo_actual = 5 WHERE id = ?", (alumno_id,))

    respuesta = cliente.post("/api/voz/hablar", json={"texto": "Hola."})

    assert respuesta.json()["guia"] == "/api/modulos/3/guia"


def test_hablar_texto_largo(cliente, respx_mock):
    ruta = respx_mock.post(URL_TTS)

    largo = cliente.post("/api/voz/hablar", json={"texto": "a" * 601})
    vacio = cliente.post("/api/voz/hablar", json={"texto": ""})

    assert largo.status_code == 422
    assert vacio.status_code == 422
    assert ruta.call_count == 0


def test_endpoint_hablar_falla(cliente, respx_mock):
    respx_mock.post(URL_TTS).mock(return_value=httpx.Response(500))
    respx_mock.post(URL_TTS_RESPALDO).mock(return_value=httpx.Response(500))

    respuesta = cliente.post("/api/voz/hablar", json={"texto": "Hola."})

    assert respuesta.status_code == 502


def test_voz_requiere_login(settings_tmp, con, respx_mock):
    stt = respx_mock.post(URL_STT)
    tts = respx_mock.post(URL_TTS)
    cliente = TestClient(_app(settings_tmp, con))

    transcribir = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("hola.webm", (FIXTURES / "hola.webm").read_bytes(), "audio/webm")},
    )
    hablar = cliente.post("/api/voz/hablar", json={"texto": "Hola."})

    assert transcribir.status_code == 401
    assert hablar.status_code == 401
    assert stt.call_count == 0
    assert tts.call_count == 0


def test_en_modo_demo_la_voz_responde_503_sin_llamar_a_gemini(settings_tmp, con, alumno_id, respx_mock):
    demo = settings_tmp.model_copy(update={"modo_demo": True, "gemini_api_key": ""})
    app = _app(demo, con)
    app.dependency_overrides[auth.alumno_actual] = lambda: auth.Alumno(id=alumno_id, email="ana@example.com", es_admin=False)
    stt = respx_mock.post(URL_STT)
    tts = respx_mock.post(URL_TTS)
    cliente = TestClient(app)

    transcribir = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("hola.webm", (FIXTURES / "hola.webm").read_bytes(), "audio/webm")},
    )
    hablar = cliente.post("/api/voz/hablar", json={"texto": "Hola."})

    for respuesta in (transcribir, hablar):
        assert respuesta.status_code == 503
        assert respuesta.json() == {"detalle": "La voz no está disponible en el modo demo."}
    assert stt.call_count == 0
    assert tts.call_count == 0
    assert _usos(con) == []


# --- techos de la transcripción --------------------------------------------------------------------


async def test_transcribir_corta_el_audio_a_200_segundos(respx_mock, settings_tmp, con, tmp_path):
    origen = tmp_path / "largo.m4a"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=215",
            "-ac", "1", "-ar", "8000", "-c:a", "aac", "-b:a", "16k", str(origen),
        ],
        check=True,
    )
    ruta = respx_mock.post(URL_STT).mock(return_value=httpx.Response(200, json=_respuesta_texto("hola")))

    await voz.transcribir(origen.read_bytes(), settings=settings_tmp, con=con)

    audio = json.loads(ruta.calls.last.request.content)["contents"][0]["parts"][1]["inline_data"]
    duracion = _sondear(base64.b64decode(audio["data"]), tmp_path)["duracion"]
    assert duracion == pytest.approx(200, abs=0.5)


def test_mp3_de_mas_de_15_mb_da_413_sin_llamar_a_gemini(cliente, respx_mock, monkeypatch):
    ruta = respx_mock.post(URL_STT)

    async def enorme(datos, mono_16k):
        return b"\xff\xfb" + b"\0" * (15 * 1024 * 1024)

    monkeypatch.setattr(voz, "a_mp3", enorme)

    respuesta = cliente.post(
        "/api/voz/transcribir",
        files={"audio": ("hola.webm", (FIXTURES / "hola.webm").read_bytes(), "audio/webm")},
    )

    assert respuesta.status_code == 413
    assert respuesta.json()["detalle"]
    assert ruta.call_count == 0


class _Medidor:
    """Cuenta cuántas conversiones y pedidos a Gemini corren al mismo tiempo."""

    def __init__(self):
        self.ahora = 0
        self.maximo = 0

    async def paso(self):
        self.ahora += 1
        self.maximo = max(self.maximo, self.ahora)
        await asyncio.sleep(0.01)
        self.ahora -= 1


async def test_como_mucho_dos_audios_a_la_vez(settings_tmp, con, monkeypatch):
    medidor = _Medidor()

    async def convertir(datos, mono_16k):
        await medidor.paso()
        return b"\xff\xfb" + b"\0" * 100

    async def generar(settings, modelo, cuerpo):
        await medidor.paso()
        if "responseModalities" in cuerpo["generationConfig"]:
            return _respuesta_audio(b"ID3", mime="audio/mpeg")
        return _respuesta_texto("hola")

    monkeypatch.setattr(voz, "a_mp3", convertir)
    monkeypatch.setattr(voz, "_generar", generar)

    await asyncio.gather(
        *(voz.transcribir(b"audio", settings=settings_tmp, con=con) for _ in range(4)),
        *(voz.sintetizar("Hola.", settings=settings_tmp, con=con) for _ in range(4)),
    )

    assert medidor.maximo == 2


# --- límite de transcripciones por hora ------------------------------------------------------------


def _pedir_transcripcion(cliente):
    return cliente.post("/api/voz/transcribir", files={"audio": ("a.webm", b"audio", "audio/webm")})


def test_mas_de_30_transcripciones_en_una_hora_da_429(cliente, monkeypatch):
    reloj = {"ahora": 1000.0}
    monkeypatch.setattr(voz, "reloj", lambda: reloj["ahora"])
    llamadas = []

    async def falsa(audio, **kwargs):
        llamadas.append(kwargs["alumno_id"])
        if len(llamadas) % 2:
            raise voz.ErrorVoz("Gemini no respondió")
        return "hola"

    monkeypatch.setattr(voz, "transcribir", falsa)

    for numero in range(30):
        reloj["ahora"] = 1000.0 + numero * 60
        assert _pedir_transcripcion(cliente).status_code in (200, 502)

    reloj["ahora"] = 1000.0 + 30 * 60
    respuesta = _pedir_transcripcion(cliente)

    assert respuesta.status_code == 429
    assert respuesta.json()["detalle"]
    assert len(llamadas) == 30

    reloj["ahora"] = 1000.0 + 3600 + 1
    assert _pedir_transcripcion(cliente).status_code in (200, 502)
    assert len(llamadas) == 31


def test_el_limite_de_transcripciones_es_por_alumno(settings_tmp, con, monkeypatch):
    async def falsa(audio, **kwargs):
        return "hola"

    monkeypatch.setattr(voz, "transcribir", falsa)
    app = _app(settings_tmp, con)
    ana = dominio.crear_alumno(con, "ana@example.com", fuente=None)
    beto = dominio.crear_alumno(con, "beto@example.com", fuente=None)
    cliente = TestClient(app)

    app.dependency_overrides[auth.alumno_actual] = lambda: auth.Alumno(id=ana, email="ana@example.com", es_admin=False)
    for _ in range(30):
        assert _pedir_transcripcion(cliente).status_code == 200
    assert _pedir_transcripcion(cliente).status_code == 429

    app.dependency_overrides[auth.alumno_actual] = lambda: auth.Alumno(id=beto, email="beto@example.com", es_admin=False)
    assert _pedir_transcripcion(cliente).status_code == 200
