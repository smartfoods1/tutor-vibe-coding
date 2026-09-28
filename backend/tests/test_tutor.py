import asyncio
import base64
import copy
import json
from types import SimpleNamespace

import anthropic
import httpx2
import pytest
import yaml

from vibe_tutor import costos, dominio, herramientas, prompts
from vibe_tutor import tutor as modulo_tutor
from vibe_tutor.tutor import EventoSSE, Imagen, TopeAlcanzado, Tutor

USO = {"input_tokens": 1000, "output_tokens": 100, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
COSTO_USO = (1000 * 2.00 + 100 * 10.00) / 1_000_000
USO_CARO = {**USO, "input_tokens": 600_000}
IDEA = "# Recetas de la abuela\n\nUna página con las recetas de mi abuela."
RESUMEN = "Quiere una página de recetas familiares.\nMiedo: romper la compu."
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
WEBP = b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 64
MACHETE = [
    {
        "id": "ayuda-emergencias",
        "tema": "ayuda",
        "aplica_a": ["codex", "claude"],
        "sistema": ["mac", "windows"],
        "texto": "Si hay riesgo inmediato: 911 o 107 (SAME).",
        "fuente": "https://www.argentina.gob.ar/tema/emergencias",
        "verificado": "2026-09-28",
        "probado": False,
    },
    {
        "id": "codex-planes",
        "tema": "planes",
        "aplica_a": ["codex"],
        "sistema": ["mac", "windows"],
        "texto": "El plan Go cuesta US$8 por mes.",
        "fuente": "https://learn.chatgpt.com/docs/pricing",
        "verificado": "2026-09-28",
        "probado": False,
    },
]


def texto(t: str) -> dict:
    return {"type": "text", "text": t}


def herramienta(id_: str, nombre: str, entrada: dict) -> dict:
    return {"type": "tool_use", "id": id_, "name": nombre, "input": entrada}


def pensamiento(firma: str = "firma") -> dict:
    return {"type": "thinking", "thinking": "", "signature": firma}


class Respuesta:
    def __init__(self, bloques, stop_reason="end_turn", uso=None, corte_tras=None, modelo="claude-sonnet-5"):
        self.bloques = bloques
        self.stop_reason = stop_reason
        self.uso = uso or USO
        self.corte_tras = corte_tras
        self.modelo = modelo

    def mensaje(self, bloques=None, stop_reason=None, uso=None) -> anthropic.types.Message:
        return anthropic.types.Message.model_validate(
            {
                "id": "msg_prueba",
                "type": "message",
                "role": "assistant",
                "model": self.modelo,
                "content": copy.deepcopy(self.bloques if bloques is None else bloques),
                "stop_reason": stop_reason if bloques is not None else self.stop_reason,
                "stop_sequence": None,
                "usage": uso or self.uso,
            }
        )

    def eventos(self):
        final = self.mensaje()
        for indice, bloque in enumerate(final.content):
            yield SimpleNamespace(type="content_block_start", index=indice, content_block=bloque)
            if bloque.type == "text":
                mitad = len(bloque.text) // 2
                for trozo in (bloque.text[:mitad], bloque.text[mitad:]):
                    if trozo:
                        yield SimpleNamespace(type="text", text=trozo, snapshot="")
            yield SimpleNamespace(type="content_block_stop", index=indice, content_block=bloque)
        yield SimpleNamespace(type="message_stop", message=final)


def error_conexion() -> anthropic.APIConnectionError:
    return anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))


def error_estado(codigo: int) -> anthropic.APIStatusError:
    respuesta = httpx2.Response(codigo, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
    clases = {400: anthropic.BadRequestError, 429: anthropic.RateLimitError, 500: anthropic.InternalServerError}
    clase = clases.get(codigo, anthropic.APIStatusError)
    return clase(f"error {codigo}", response=respuesta, body=None)


class StreamFalso:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.emitidos = 0

    async def __aenter__(self):
        if isinstance(self.respuesta, BaseException):
            raise self.respuesta
        return self

    async def __aexit__(self, *excepcion):
        return False

    def __aiter__(self):
        return self._eventos()

    async def _eventos(self):
        for evento in self.respuesta.eventos():
            if self.respuesta.corte_tras is not None and self.emitidos >= self.respuesta.corte_tras:
                raise error_conexion()
            self.emitidos += 1
            yield evento
            await asyncio.sleep(0)

    async def get_final_message(self):
        return self.respuesta.mensaje()

    @property
    def current_message_snapshot(self):
        uso = {**self.respuesta.uso, "output_tokens": 0}
        return self.respuesta.mensaje(bloques=[], stop_reason=None, uso=uso)


class ClienteFalso:
    """Imita AsyncAnthropic().messages.stream; guarda una copia de cada llamada."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas: list[dict] = []
        self.messages = SimpleNamespace(stream=self._stream)

    def _stream(self, **kwargs):
        self.llamadas.append(copy.deepcopy(kwargs))
        if not self.respuestas:
            raise AssertionError("llamada de más a la API")
        return StreamFalso(self.respuestas.pop(0))


def escribir_contenido(raiz) -> None:
    (raiz / "prompts").mkdir(parents=True, exist_ok=True)
    (raiz / "web").mkdir(parents=True, exist_ok=True)
    (raiz / "prompts" / "base.md").write_text("# Tutor\n\nSos el tutor del curso.\n", encoding="utf-8")
    for n in (1, 2, 3):
        (raiz / "web" / f"modulo-{n}.md").write_text(f"# Módulo {n}\n\nGuía del módulo {n}.\n", encoding="utf-8")
    (raiz / "machete.yaml").write_text(yaml.safe_dump(MACHETE, allow_unicode=True), encoding="utf-8")


@pytest.fixture
def contenido(settings_tmp):
    escribir_contenido(settings_tmp.contenido_dir)
    return settings_tmp.contenido_dir


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


@pytest.fixture
def alumno_id(base):
    return dominio.crear_alumno(base, "ana@example.com", fuente=None)


def avanzar_hasta(con, alumno_id: int, modulo: int) -> None:
    if modulo >= 2:
        dominio.completar_modulo(con, alumno_id, 1, "tutor", "Semilla: recetas.")
    if modulo >= 3:
        dominio.guardar_idea(con, alumno_id, IDEA, None, "tutor")
        dominio.completar_modulo(con, alumno_id, 2, "tutor", "Idea lista.")


@pytest.fixture
def armar(settings_tmp, db_de, contenido):
    def _armar(respuestas):
        cliente = ClienteFalso(respuestas)
        return Tutor(settings_tmp, db_de, cliente=cliente), cliente

    return _armar


async def recoger(generador) -> list[EventoSSE]:
    return [evento async for evento in generador]


def tipos(eventos: list[EventoSSE]) -> list[str]:
    return [evento.tipo for evento in eventos]


def guardados(con, sesion_id: int) -> list[tuple[str, list]]:
    filas = con.execute(
        "SELECT rol, contenido_json FROM mensajes WHERE sesion_id = ? ORDER BY orden", (sesion_id,)
    ).fetchall()
    return [(fila["rol"], json.loads(fila["contenido_json"])) for fila in filas]


def validar_secuencia(mensajes: list[dict]) -> None:
    assert mensajes, "sin mensajes"
    assert mensajes[0]["role"] == "user"
    assert mensajes[-1]["role"] == "user"
    for anterior, actual in zip(mensajes, mensajes[1:]):
        assert anterior["role"] != actual["role"], "dos mensajes seguidos con el mismo rol"
    for indice, mensaje in enumerate(mensajes):
        assert mensaje["content"], "mensaje sin contenido"
        if mensaje["role"] != "assistant":
            continue
        pedidos = [b["id"] for b in mensaje["content"] if b["type"] == "tool_use"]
        if not pedidos:
            continue
        siguiente = mensajes[indice + 1]["content"]
        primeros = [b["tool_use_id"] for b in siguiente[: len(pedidos)] if b["type"] == "tool_result"]
        assert sorted(primeros) == sorted(pedidos), "tool_use sin su tool_result al comienzo del mensaje siguiente"


def imagenes_de(mensajes: list[dict]) -> list[dict]:
    return [b for m in mensajes for b in m["content"] if b["type"] == "image"]


# --- Sesiones ---


def test_abrir_sesion_guarda_el_mensaje_de_estado(armar, base, alumno_id):
    tutor, cliente = armar([])

    sesion_id, retomada = tutor.abrir_sesion(alumno_id, 1)

    assert retomada is False
    assert cliente.llamadas == []
    fila = base.execute("SELECT * FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()
    assert (fila["alumno_id"], fila["modulo"], fila["fin"]) == (alumno_id, 1, None)
    [(rol, contenido)] = guardados(base, sesion_id)
    assert rol == "user"
    inicio = contenido[0]["text"]
    assert "Módulo de esta sesión: 1" in inicio
    assert inicio.rstrip().endswith(prompts.EMPEZAR)


def test_abrir_sesion_retoma_la_abierta(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 2)
    otro = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    tutor, _ = armar([])

    primera, _ = tutor.abrir_sesion(alumno_id, 2)
    retomada = tutor.abrir_sesion(alumno_id, 2)
    del_modulo_1, nueva_1 = tutor.abrir_sesion(alumno_id, 1)
    de_otro, nueva_otro = tutor.abrir_sesion(otro, 1)

    assert retomada == (primera, True)
    assert nueva_1 is False and del_modulo_1 != primera
    assert nueva_otro is False and de_otro not in (primera, del_modulo_1)
    with base:
        base.execute("UPDATE sesiones SET fin = inicio WHERE id = ?", (primera,))
    segunda, retomada_2 = tutor.abrir_sesion(alumno_id, 2)
    assert retomada_2 is False and segunda != primera


def test_abrir_sesion_con_tope_del_alumno(armar, base, alumno_id):
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=alumno_id)
    tutor, _ = armar([])

    with pytest.raises(TopeAlcanzado) as error:
        tutor.abrir_sesion(alumno_id, 1)

    assert error.value.alcance == "alumno"
    assert base.execute("SELECT COUNT(*) FROM sesiones").fetchone()[0] == 0


def test_abrir_sesion_con_tope_del_mes(armar, base, alumno_id):
    otro = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 50.0, alumno_id=otro)
    tutor, _ = armar([])

    with pytest.raises(TopeAlcanzado) as error:
        tutor.abrir_sesion(alumno_id, 1)

    assert error.value.alcance == "mes"


def test_abrir_sesion_modulo_invalido(armar, alumno_id):
    tutor, _ = armar([])

    with pytest.raises(ValueError):
        tutor.abrir_sesion(alumno_id, 4)


# --- Turnos ---


async def test_turno_inicial_sin_texto(armar, base, alumno_id):
    tutor, cliente = armar([Respuesta([pensamiento(), texto("Hola. Soy el tutor del curso.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert tipos(eventos)[0] == "pensando"
    assert set(tipos(eventos)) == {"pensando", "texto", "fin"}
    assert "".join(e.datos["delta"] for e in eventos if e.tipo == "texto") == "Hola. Soy el tutor del curso."
    assert eventos[-1] == EventoSSE("fin", {"stop_reason": "end_turn"})
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user", "assistant"]
    [llamada] = cliente.llamadas
    validar_secuencia(llamada["messages"])
    assert "Módulo de esta sesión: 1" in llamada["messages"][0]["content"][0]["text"]


async def test_parametros_de_la_llamada(armar, settings_tmp, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Hola.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    await recoger(tutor.turno(sesion_id, alumno_id, None))

    [llamada] = cliente.llamadas
    assert llamada["model"] == "claude-sonnet-5"
    assert llamada["max_tokens"] == modulo_tutor.MAX_TOKENS
    assert llamada["thinking"] == {"type": "adaptive"}
    assert llamada["output_config"] == {"effort": "low"}
    assert llamada["cache_control"] == {"type": "ephemeral"}
    assert llamada["system"] == prompts.construir_system(settings_tmp.contenido_dir, 1)
    assert llamada["system"][-1]["cache_control"] == {"type": "ephemeral"}
    assert llamada["tools"] == herramientas.tools_de(1)
    # Sin respaldo ante rechazos ni compactación: cada módulo es una conversación corta.
    for clave in ("betas", "fallbacks", "context_management"):
        assert clave not in llamada


def test_regla_de_esfuerzo():
    for modulo, umbral in modulo_tutor.UMBRAL_CIERRE.items():
        assert modulo_tutor.esfuerzo(modulo, umbral - 1) == "low"
        assert modulo_tutor.esfuerzo(modulo, umbral) == "medium"
        assert modulo_tutor.esfuerzo(modulo, umbral + 5) == "medium"
    assert modulo_tutor.esfuerzo(1, 0) == "low"


async def test_esfuerzo_medium_al_cierre_y_parejo_dentro_del_turno(armar, alumno_id):
    umbral = modulo_tutor.UMBRAL_CIERRE[1]
    respuestas = [Respuesta([texto("Hola.")])]
    respuestas += [Respuesta([texto(f"Respuesta {n}.")]) for n in range(1, umbral)]
    respuestas += [
        Respuesta([herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})], stop_reason="tool_use"),
        Respuesta([texto("Listo, terminaste el módulo 1.")]),
    ]
    tutor, cliente = armar(respuestas)
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    await recoger(tutor.turno(sesion_id, alumno_id, None))
    for n in range(1, umbral + 1):
        await recoger(tutor.turno(sesion_id, alumno_id, f"Mensaje {n}"))

    esfuerzos = [llamada["output_config"]["effort"] for llamada in cliente.llamadas]
    assert esfuerzos == ["low"] * umbral + ["medium", "medium"]


async def test_registrar_taller_emite_taller(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 3)
    tutor, _ = armar(
        [
            Respuesta(
                [herramienta("toolu_1", "registrar_taller", {"herramienta": "claude", "sistema": "windows"})],
                stop_reason="tool_use",
            ),
            Respuesta([texto("Anotado: Claude en Windows.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 3)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "Claude, en una Windows"))

    assert EventoSSE("taller", {"herramienta": "claude", "sistema": "windows"}) in eventos
    assert eventos[-1] == EventoSSE("fin", {"stop_reason": "end_turn"})


async def test_guardar_idea_emite_idea(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 2)
    tutor, cliente = armar(
        [
            Respuesta(
                [pensamiento(), texto("Te armo la página."), herramienta("toolu_1", "guardar_idea", {"texto_md": IDEA, "que_sigue_md": "Un buscador."})],
                stop_reason="tool_use",
            ),
            Respuesta([texto("Ya está guardada. Miralá en Mi idea.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 2)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "Dale, guardala"))

    assert [e.datos for e in eventos if e.tipo == "herramienta"] == [
        {"nombre": "guardar_idea", "estado": "inicio", "error": False},
        {"nombre": "guardar_idea", "estado": "fin", "error": False},
    ]
    assert EventoSSE("idea", {"version": 1}) in eventos
    assert tipos(eventos).index("idea") < len(eventos) - 1
    assert eventos[-1] == EventoSSE("fin", {"stop_reason": "end_turn"})
    vigente = dominio.idea_vigente(base, alumno_id)
    assert (vigente["version"], vigente["autor"], vigente["que_sigue_md"]) == (1, "tutor", "Un buscador.")
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user", "user", "assistant", "user", "assistant"]
    segunda = cliente.llamadas[1]["messages"]
    validar_secuencia(segunda)
    [resultado] = segunda[-1]["content"]
    assert resultado["tool_use_id"] == "toolu_1"
    assert "is_error" not in resultado
    assert segunda[-2]["content"][0] == pensamiento()


async def test_marcar_avance_emite_avance(armar, base, alumno_id):
    tutor, _ = armar(
        [
            Respuesta([herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})], stop_reason="tool_use"),
            Respuesta([texto("Terminaste el módulo 1.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "Quiero una página de recetas"))

    assert EventoSSE("avance", {"modulo_completado": 1, "modulo_actual": 2}) in eventos
    assert tipos(eventos)[-1] == "fin"
    assert dominio.alumno(base, alumno_id)["modulo_actual"] == 2
    assert dominio.resumen_modulo(base, alumno_id, 1) == RESUMEN


async def test_error_de_herramienta(armar, alumno_id):
    tutor, cliente = armar(
        [
            Respuesta([herramienta("toolu_1", "marcar_avance", {"modulo": 3, "resumen": RESUMEN})], stop_reason="tool_use"),
            Respuesta([texto("Perdón, sigamos.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    finales = [e.datos for e in eventos if e.tipo == "herramienta" and e.datos["estado"] == "fin"]
    assert finales == [{"nombre": "marcar_avance", "estado": "fin", "error": True}]
    assert "avance" not in tipos(eventos)
    [resultado] = cliente.llamadas[1]["messages"][-1]["content"]
    assert resultado["is_error"] is True
    assert tipos(eventos)[-1] == "fin"


async def test_limite_de_vueltas(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 3)
    maximo = modulo_tutor.MAX_VUELTAS
    respuestas = [
        Respuesta([herramienta(f"toolu_{n}", "consultar_machete", {"tema": "todos"})], stop_reason="tool_use")
        for n in range(maximo + 1)
    ]
    tutor, cliente = armar(respuestas)
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 3)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "¿Qué necesito?"))

    assert tipos(eventos)[-1] == "error"
    assert "fin" not in tipos(eventos)
    assert len(cliente.llamadas) == maximo + 1
    ejecutadas = [e for e in eventos if e.tipo == "herramienta" and e.datos["estado"] == "fin" and not e.datos["error"]]
    assert len(ejecutadas) == maximo
    cliente.respuestas.append(Respuesta([texto("Perdón.")]))
    await recoger(tutor.turno(sesion_id, alumno_id, "¿Y?"))
    validar_secuencia(cliente.llamadas[-1]["messages"])
    ultimo = cliente.llamadas[-1]["messages"][-1]["content"]
    assert ultimo[0]["tool_use_id"] == f"toolu_{maximo}"
    assert ultimo[0]["is_error"] is True
    assert ultimo[-1] == texto("¿Y?")


async def test_stream_cortado(armar, base, alumno_id):
    tutor, cliente = armar(
        [
            Respuesta([texto("Hola.")]),
            Respuesta([pensamiento(), texto("El vibe coding es construir conversando.")], corte_tras=4),
            Respuesta([texto("Te decía.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    await recoger(tutor.turno(sesion_id, alumno_id, None))

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "¿Qué es el vibe coding?"))

    assert tipos(eventos)[-1] == "error"
    assert eventos[-1].datos["reintentable"] is True
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user", "assistant", "user"]
    parcial = base.execute("SELECT input_tokens, output_tokens, alumno_id FROM uso ORDER BY id DESC").fetchone()
    assert (parcial["input_tokens"], parcial["output_tokens"], parcial["alumno_id"]) == (1000, 0, alumno_id)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    assert tipos(eventos)[-1] == "fin"
    enviados = cliente.llamadas[-1]["messages"]
    validar_secuencia(enviados)
    assert enviados[-1]["content"] == [texto("¿Qué es el vibe coding?"), texto("hola")]


async def test_reintentar_sin_texto_tras_corte(armar, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Hola.")], corte_tras=1), Respuesta([texto("Hola.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    await recoger(tutor.turno(sesion_id, alumno_id, None))

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert tipos(eventos)[-1] == "fin"
    assert cliente.llamadas[0]["messages"] == cliente.llamadas[1]["messages"]


@pytest.mark.parametrize(("error", "reintentable"), [(error_estado(400), False), (error_estado(429), True), (error_estado(500), True), (error_conexion(), True)])
async def test_errores_antes_del_stream(armar, base, alumno_id, error, reintentable):
    tutor, _ = armar([error])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert tipos(eventos) == ["pensando", "error"]
    assert eventos[-1].datos["reintentable"] is reintentable
    assert eventos[-1].datos["mensaje"]
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user"]


async def test_refusal_con_mensaje_amable(armar, base, alumno_id):
    tutor, cliente = armar(
        [
            Respuesta(
                [texto("Empie"), herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})],
                stop_reason="refusal",
            ),
            Respuesta([texto("Sigamos.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "Algo raro"))

    assert tipos(eventos)[-1] == "error"
    assert eventos[-1].datos == {"mensaje": modulo_tutor.TEXTO_RECHAZO, "reintentable": False}
    assert "Claude" not in modulo_tutor.TEXTO_RECHAZO
    assert len(cliente.llamadas) == 1
    assert base.execute("SELECT COUNT(*) FROM avance").fetchone()[0] == 0
    rol, contenido = guardados(base, sesion_id)[-1]
    assert (rol, contenido) == ("assistant", [texto(modulo_tutor.TEXTO_RECHAZO)])

    await recoger(tutor.turno(sesion_id, alumno_id, "Otra cosa"))

    validar_secuencia(cliente.llamadas[-1]["messages"])


async def test_max_tokens_con_herramienta_no_ejecuta(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 2)
    tutor, cliente = armar(
        [
            Respuesta([texto("Guardo."), herramienta("toolu_1", "guardar_idea", {"texto_md": "# Rec"})], stop_reason="max_tokens"),
            Respuesta([texto("La guardo más corta.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 2)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert dominio.idea_vigente(base, alumno_id) is None
    assert tipos(eventos)[-1] == "error"
    assert eventos[-1].datos["reintentable"] is True
    assert {"nombre": "guardar_idea", "estado": "fin", "error": True} in [e.datos for e in eventos if e.tipo == "herramienta"]

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert tipos(eventos)[-1] == "fin"
    enviados = cliente.llamadas[-1]["messages"]
    validar_secuencia(enviados)
    assert enviados[-1]["content"][0]["is_error"] is True


async def test_max_tokens_solo_texto_termina(armar, alumno_id):
    tutor, _ = armar([Respuesta([texto("Una respuesta larguísima")], stop_reason="max_tokens")])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert eventos[-1] == EventoSSE("fin", {"stop_reason": "max_tokens"})


async def test_herramienta_colgada_se_repara(armar, base, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Retomo.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    with base:
        base.execute(
            "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 1, 'assistant', ?)",
            (sesion_id, json.dumps([herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})])),
        )

    await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    enviados = cliente.llamadas[0]["messages"]
    validar_secuencia(enviados)
    assert enviados[-1]["content"][0]["tool_use_id"] == "toolu_1"
    assert enviados[-1]["content"][0]["is_error"] is True
    assert enviados[-1]["content"][-1] == texto("hola")


async def test_sin_mensaje_pendiente(armar, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Hola.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    await recoger(tutor.turno(sesion_id, alumno_id, None))

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "   "))

    assert tipos(eventos) == ["error"]
    assert eventos[0].datos["reintentable"] is False
    assert len(cliente.llamadas) == 1


async def test_sesion_inexistente_o_ajena(armar, base, alumno_id):
    otro = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    tutor, cliente = armar([])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    inexistente = await recoger(tutor.turno(999, alumno_id, "hola"))
    ajena = await recoger(tutor.turno(sesion_id, otro, "hola"))

    assert tipos(inexistente) == ["error"]
    assert tipos(ajena) == ["error"]
    assert cliente.llamadas == []
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user"]


async def test_turno_en_curso(armar, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Hola.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    primero = tutor.turno(sesion_id, alumno_id, None)
    assert (await anext(primero)).tipo == "pensando"

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "otra cosa"))

    assert tipos(eventos) == ["error"]
    assert tipos(await recoger(primero))[-1] == "fin"
    assert len(cliente.llamadas) == 1


async def test_costo_registrado_con_alumno_y_sesion(armar, base, alumno_id):
    tutor, _ = armar(
        [
            Respuesta([herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})], stop_reason="tool_use"),
            Respuesta([texto("Listo.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    await recoger(tutor.turno(sesion_id, alumno_id, None))

    filas = base.execute("SELECT * FROM uso ORDER BY id").fetchall()
    assert [(f["proveedor"], f["modelo"], f["alumno_id"], f["sesion_id"]) for f in filas] == [
        ("anthropic", "claude-sonnet-5", alumno_id, sesion_id)
    ] * 2
    assert costos.gasto_alumno(base, alumno_id) == pytest.approx(2 * COSTO_USO)
    costo_sesion = base.execute("SELECT costo_usd FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()[0]
    assert costo_sesion == pytest.approx(2 * COSTO_USO)


async def test_tope_antes_del_turno(armar, base, alumno_id):
    tutor, cliente = armar([])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=alumno_id)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    assert eventos == [EventoSSE("tope", {"alcance": "alumno", "guia": "/api/modulos/1/guia"})]
    assert cliente.llamadas == []
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user"]


async def test_tope_del_mes_antes_del_turno(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 2)
    otro = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    tutor, cliente = armar([])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 2)
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 50.0, alumno_id=otro)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert eventos == [EventoSSE("tope", {"alcance": "mes", "guia": "/api/modulos/2/guia"})]
    assert cliente.llamadas == []


async def test_tope_entre_vueltas(armar, base, alumno_id):
    tutor, cliente = armar(
        [
            Respuesta(
                [herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})],
                stop_reason="tool_use",
                uso=USO_CARO,
            ),
            Respuesta([texto("No debería llegar.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    assert eventos[-1] == EventoSSE("tope", {"alcance": "alumno", "guia": "/api/modulos/1/guia"})
    assert len(cliente.llamadas) == 1
    assert EventoSSE("avance", {"modulo_completado": 1, "modulo_actual": 2}) in eventos
    assert guardados(base, sesion_id)[-1][1][0]["type"] == "tool_result"


async def test_turno_toca_la_actividad(armar, base, alumno_id):
    with base:
        base.execute("UPDATE alumnos SET ultima_actividad = '2026-01-01T00:00:00+00:00' WHERE id = ?", (alumno_id,))
    tutor, _ = armar([Respuesta([texto("Hola.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    await recoger(tutor.turno(sesion_id, alumno_id, "hola"))

    assert dominio.alumno(base, alumno_id)["ultima_actividad"] > "2026-01-01T00:00:00+00:00"


# --- Capturas ---


@pytest.mark.parametrize(("datos", "tipo"), [(PNG, "image/png"), (JPEG, "image/jpeg"), (WEBP, "image/webp")])
def test_tipo_de_imagen(datos, tipo):
    assert modulo_tutor.tipo_imagen(datos) == tipo


@pytest.mark.parametrize("datos", [b"GIF89a" + b"\x00" * 20, b"no es una imagen", b"", b"RIFF\x00\x00\x00\x00WAVE"])
def test_tipo_de_imagen_no_permitida(datos):
    assert modulo_tutor.tipo_imagen(datos) is None


async def test_la_captura_viaja_solo_en_el_turno(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 3)
    tutor, cliente = armar(
        [
            Respuesta([texto("Hola.")]),
            Respuesta([herramienta("toolu_1", "consultar_machete", {"tema": "instalar"})], stop_reason="tool_use"),
            Respuesta([texto("Veo la pantalla de instalación. Tocá Siguiente.")]),
            Respuesta([texto("De nada.")]),
        ]
    )
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 3)
    await recoger(tutor.turno(sesion_id, alumno_id, None))

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "Me trabé acá", Imagen("image/png", PNG)))

    assert tipos(eventos)[-1] == "fin"
    esperado = {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(PNG).decode()}}
    for llamada in cliente.llamadas[1:3]:
        mensajes = llamada["messages"]
        validar_secuencia(mensajes)
        assert imagenes_de(mensajes) == [esperado]
        assert mensajes[2]["content"] == [esperado, texto("Me trabé acá")]
    guardado = json.dumps(guardados(base, sesion_id))
    assert base64.b64encode(PNG).decode() not in guardado
    assert '"image"' not in guardado
    assert guardados(base, sesion_id)[2] == ("user", [texto(modulo_tutor.MARCA_CAPTURA), texto("Me trabé acá")])

    await recoger(tutor.turno(sesion_id, alumno_id, "Gracias"))

    ultimo = cliente.llamadas[-1]["messages"]
    assert imagenes_de(ultimo) == []
    assert ultimo[2]["content"] == [texto(modulo_tutor.MARCA_CAPTURA), texto("Me trabé acá")]


async def test_captura_sin_texto(armar, base, alumno_id):
    avanzar_hasta(base, alumno_id, 3)
    tutor, cliente = armar([Respuesta([texto("Veo la pantalla.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 3)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None, Imagen("image/webp", WEBP)))

    assert tipos(eventos)[-1] == "fin"
    [llamada] = cliente.llamadas
    assert [b["type"] for b in llamada["messages"][0]["content"]] == ["text", "image"]
    assert guardados(base, sesion_id)[1] == ("user", [texto(modulo_tutor.MARCA_CAPTURA)])


# --- Con el SDK real y un transporte falso ---


def sse(*eventos: dict) -> bytes:
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in eventos).encode()


def inicio_sse() -> dict:
    return {
        "type": "message_start",
        "message": {
            "id": "msg_real",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-5",
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {**USO, "output_tokens": 1},
        },
    }


def bloque_sse(indice: int, bloque: dict, *deltas: dict) -> list[dict]:
    return [
        {"type": "content_block_start", "index": indice, "content_block": bloque},
        *({"type": "content_block_delta", "index": indice, "delta": delta} for delta in deltas),
        {"type": "content_block_stop", "index": indice},
    ]


def cierre_sse(stop_reason: str) -> list[dict]:
    return [
        {"type": "message_delta", "delta": {"stop_reason": stop_reason, "stop_sequence": None}, "usage": {"output_tokens": 100}},
        {"type": "message_stop"},
    ]


RESPUESTA_HERRAMIENTA_SSE = sse(
    inicio_sse(),
    *bloque_sse(0, {"type": "thinking", "thinking": "", "signature": ""}, {"type": "signature_delta", "signature": "firma-real"}),
    *bloque_sse(1, {"type": "text", "text": ""}, {"type": "text_delta", "text": "Me fijo "}, {"type": "text_delta", "text": "en el machete."}),
    *bloque_sse(
        2,
        {"type": "tool_use", "id": "toolu_real", "name": "consultar_machete", "input": {}},
        {"type": "input_json_delta", "partial_json": '{"tema": '},
        {"type": "input_json_delta", "partial_json": '"planes"}'},
    ),
    *cierre_sse("tool_use"),
)
RESPUESTA_TEXTO_SSE = sse(
    inicio_sse(),
    *bloque_sse(0, {"type": "text", "text": ""}, {"type": "text_delta", "text": "El plan Go cuesta US$8."}),
    *cierre_sse("end_turn"),
)
RESPUESTA_TRUNCADA_SSE = sse(
    inicio_sse(),
    {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
    {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "El vibe co"}},
)


class TransporteSSE:
    def __init__(self, cuerpos: list):
        self.cuerpos = list(cuerpos)
        self.pedidos: list[httpx2.Request] = []

    def __call__(self, pedido: httpx2.Request) -> httpx2.Response:
        self.pedidos.append(pedido)
        return httpx2.Response(200, headers={"content-type": "text/event-stream"}, content=self.cuerpos.pop(0))

    def cuerpo(self, indice: int) -> dict:
        return json.loads(self.pedidos[indice].content)


def cliente_real(transporte: TransporteSSE) -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(
        api_key="sk-ant-prueba",
        max_retries=0,
        http_client=anthropic.DefaultAsyncHttpxClient(transport=httpx2.MockTransport(transporte)),
    )


async def test_sdk_real_ciclo_con_herramienta(settings_tmp, db_de, contenido, base, alumno_id):
    avanzar_hasta(base, alumno_id, 3)
    transporte = TransporteSSE([RESPUESTA_HERRAMIENTA_SSE, RESPUESTA_TEXTO_SSE])
    tutor = Tutor(settings_tmp, db_de, cliente=cliente_real(transporte))
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 3)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "¿Cuánto sale?"))

    assert tipos(eventos)[-1] == "fin"
    assert "".join(e.datos["delta"] for e in eventos if e.tipo == "texto") == "Me fijo en el machete.El plan Go cuesta US$8."
    assert [e.datos["estado"] for e in eventos if e.tipo == "herramienta"] == ["inicio", "fin"]
    assert "anthropic-beta" not in transporte.pedidos[0].headers
    assert transporte.pedidos[0].url.path == "/v1/messages"
    assert "beta" not in transporte.pedidos[0].url.params
    primero = transporte.cuerpo(0)
    assert primero["model"] == "claude-sonnet-5"
    assert primero["stream"] is True
    assert primero["thinking"] == {"type": "adaptive"}
    assert primero["output_config"] == {"effort": "low"}
    assert primero["cache_control"] == {"type": "ephemeral"}
    assert primero["system"][-1]["cache_control"] == {"type": "ephemeral"}
    assert all(tool["eager_input_streaming"] is True for tool in primero["tools"])
    for clave in ("fallbacks", "context_management"):
        assert clave not in primero
    segundo = transporte.cuerpo(1)
    validar_secuencia(segundo["messages"])
    assert segundo["messages"][-2] == {
        "role": "assistant",
        "content": [
            {"type": "thinking", "thinking": "", "signature": "firma-real"},
            {"type": "text", "text": "Me fijo en el machete."},
            herramienta("toolu_real", "consultar_machete", {"tema": "planes"}),
        ],
    }
    [resultado] = segundo["messages"][-1]["content"]
    assert resultado["tool_use_id"] == "toolu_real"
    assert "codex-planes" in resultado["content"]


async def test_sdk_real_stream_sin_cierre_no_guarda(settings_tmp, db_de, contenido, base, alumno_id):
    transporte = TransporteSSE([RESPUESTA_TRUNCADA_SSE, RESPUESTA_TEXTO_SSE])
    tutor = Tutor(settings_tmp, db_de, cliente=cliente_real(transporte))
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, "¿Qué es el vibe coding?"))

    assert tipos(eventos)[-1] == "error"
    assert eventos[-1].datos["reintentable"] is True
    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user", "user"]
    assert tuple(base.execute("SELECT input_tokens, alumno_id FROM uso").fetchone()) == (1000, alumno_id)

    eventos = await recoger(tutor.turno(sesion_id, alumno_id, None))

    assert tipos(eventos)[-1] == "fin"
    assert transporte.cuerpo(0)["messages"] == transporte.cuerpo(1)["messages"]


async def test_cliente_se_desconecta(armar, base, alumno_id):
    tutor, cliente = armar([Respuesta([texto("Una respuesta que nadie termina de leer.")]), Respuesta([texto("Hola de nuevo.")])])
    sesion_id, _ = tutor.abrir_sesion(alumno_id, 1)
    turno = tutor.turno(sesion_id, alumno_id, None)
    assert (await anext(turno)).tipo == "pensando"
    assert (await anext(turno)).tipo == "texto"

    await turno.aclose()

    assert [rol for rol, _ in guardados(base, sesion_id)] == ["user"]
    assert base.execute("SELECT COUNT(*) FROM uso").fetchone()[0] == 1
    assert tipos(await recoger(tutor.turno(sesion_id, alumno_id, None)))[-1] == "fin"
    assert cliente.llamadas[0]["messages"] == cliente.llamadas[1]["messages"]
