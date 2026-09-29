"""Modo demo: el tutor recorre los módulos 1 a 3 con un guion fijo, sin llamar a Claude y sin costo."""

import json

import pytest
from test_sesiones import leer_sse
from test_tutor import escribir_contenido, recoger

from vibe_tutor import api, costos, demo, dominio
from vibe_tutor.tutor import Tutor

IDEA_QUE = "Una página para juntar las recetas de mi abuela Rosa"
IDEA_QUIEN = "Para mis primos, que siempre me las piden"
IDEA_CHICA = "Una sola página con cinco recetas y sus fotos"


@pytest.fixture(autouse=True)
def sin_pausas(monkeypatch):
    monkeypatch.setattr(demo, "PAUSA", 0)


@pytest.fixture
def settings_demo(settings_tmp):
    escribir_contenido(settings_tmp.contenido_dir)
    return settings_tmp.model_copy(
        update={"modo_demo": True, "anthropic_api_key": "", "gemini_api_key": "", "resend_api_key": ""}
    )


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


@pytest.fixture
def alumno_id(base):
    return dominio.crear_alumno(base, "ana@example.com", fuente=None)


@pytest.fixture
def tutor(settings_demo, db_de):
    return Tutor(settings_demo, db_de)


def _texto(eventos) -> str:
    return "".join(e.datos["delta"] for e in eventos if e.tipo == "texto")


def _tipos(eventos) -> list[str]:
    return [e.tipo for e in eventos]


def _datos(eventos, tipo: str) -> list[dict]:
    return [e.datos for e in eventos if e.tipo == tipo]


async def _charlar(tutor, alumno_id, modulo, mensajes):
    """Abre la sesión, deja que el tutor salude y manda los mensajes; devuelve los eventos de cada turno."""
    sesion_id, retomada = tutor.abrir_sesion(alumno_id, modulo)
    assert retomada is False
    turnos = [await recoger(tutor.turno(sesion_id, alumno_id))]
    for mensaje in mensajes:
        turnos.append(await recoger(tutor.turno(sesion_id, alumno_id, mensaje)))
    return sesion_id, turnos


def test_con_modo_demo_el_tutor_usa_el_cliente_demo(tutor):
    assert isinstance(tutor.cliente, demo.ClienteDemo)


async def test_modulo_1_saluda_pregunta_y_termina_con_marcar_avance(tutor, base, alumno_id):
    _, turnos = await _charlar(
        tutor, alumno_id, 1, ["Usé ChatGPT un par de veces", "Me da miedo romper algo", "Un recetario de mi familia"]
    )

    saludo = _texto(turnos[0])
    assert "modo demo" in saludo.lower()
    assert saludo.rstrip().endswith("?")
    for turno in turnos[1:3]:
        assert _tipos(turno)[-1] == "fin"
        assert _texto(turno).rstrip().endswith("?")
        assert _datos(turno, "avance") == []
    cierre = turnos[3]
    assert {"nombre": "marcar_avance", "estado": "fin", "error": False} in _datos(cierre, "herramienta")
    assert _datos(cierre, "avance") == [{"modulo_completado": 1, "modulo_actual": 2}]
    assert _tipos(cierre)[-1] == "fin"
    assert "módulo 2" in _texto(cierre)
    fila = base.execute("SELECT via, resumen FROM avance WHERE alumno_id = ? AND modulo = 1", (alumno_id,)).fetchone()
    assert fila["via"] == "tutor"
    assert "Un recetario" not in fila["resumen"]
    assert dominio.alumno(base, alumno_id)["modulo_actual"] == 2


async def test_modulo_2_guarda_la_idea_con_lo_que_escribio_la_persona(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")

    _, turnos = await _charlar(tutor, alumno_id, 2, [IDEA_QUE, IDEA_QUIEN, IDEA_CHICA, "Ya la miré, me gusta"])

    assert "modo demo" in _texto(turnos[0]).lower()
    assert _datos(turnos[3], "idea") == [{"version": 1}]
    assert _datos(turnos[3], "avance") == []
    idea = dominio.idea_vigente(base, alumno_id)
    assert idea["autor"] == "tutor"
    assert idea["texto_md"].startswith("# ")
    for respuesta in (IDEA_QUE, IDEA_QUIEN, IDEA_CHICA):
        assert respuesta in idea["texto_md"]
    assert _datos(turnos[4], "avance") == [{"modulo_completado": 2, "modulo_actual": 3}]
    assert dominio.alumno(base, alumno_id)["modulo_actual"] == 3


async def test_modulo_2_nombra_los_botones_de_la_web_al_guardar_la_idea(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")

    _, turnos = await _charlar(tutor, alumno_id, 2, [IDEA_QUE, IDEA_QUIEN, IDEA_CHICA])

    texto = _texto(turnos[3])
    for nombre in ("Leer mi idea acá", "Está bien así", "Quiero cambiar algo"):
        assert nombre in texto


async def test_modulo_2_quiero_cambiar_algo_no_cierra_el_modulo(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")

    sesion_id, turnos = await _charlar(
        tutor, alumno_id, 2, [IDEA_QUE, IDEA_QUIEN, IDEA_CHICA, "Quiero cambiar algo"]
    )

    # El guion fijo no puede reescribir la idea: lo dice, manda a "Mi idea" y espera a que la persona termine.
    assert _datos(turnos[4], "avance") == []
    assert "Mi idea" in _texto(turnos[4])
    # La web ya sacó los botones al tocar uno y el guion fijo no guarda otra versión: no manda a tocarlos.
    assert "tocá" not in _texto(turnos[4])
    assert dominio.alumno(base, alumno_id)["modulo_actual"] == 2
    # Con "Está bien así" recién ahí se cierra.
    cierre = await recoger(tutor.turno(sesion_id, alumno_id, "Está bien así"))
    assert _datos(cierre, "avance") == [{"modulo_completado": 2, "modulo_actual": 3}]


async def test_modulo_3_registra_el_taller_cuando_la_persona_elige(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")
    dominio.guardar_idea(base, alumno_id, "# Recetas", None, "tutor")
    dominio.completar_modulo(base, alumno_id, 2, "tutor", "Idea lista.")

    _, turnos = await _charlar(tutor, alumno_id, 3, ["Tengo una Mac", "Prefiero Claude", "Listo, ya la instalé"])

    assert "Mac" in _texto(turnos[0])
    assert _datos(turnos[1], "taller") == []
    assert "Codex" in _texto(turnos[1]) and "Claude" in _texto(turnos[1])
    assert _datos(turnos[2], "taller") == [{"herramienta": "claude", "sistema": "mac"}]
    fila = dominio.alumno(base, alumno_id)
    assert (fila["herramienta"], fila["sistema"]) == ("claude", "mac")
    assert _datos(turnos[3], "avance") == [{"modulo_completado": 3, "modulo_actual": 3}]
    assert "kit" in _texto(turnos[3])


async def test_modulo_3_con_todo_en_un_mensaje_y_sin_computadora(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")
    dominio.guardar_idea(base, alumno_id, "# Recetas", None, "tutor")
    dominio.completar_modulo(base, alumno_id, 2, "tutor", "Idea lista.")

    _, turnos = await _charlar(tutor, alumno_id, 3, ["Solo tengo el celular y uso ChatGPT"])

    assert _datos(turnos[1], "taller") == [{"herramienta": "codex", "sistema": "otro"}]
    assert "Mac o Windows" in _texto(turnos[1])


async def test_modulo_3_pregunta_de_nuevo_si_no_entiende(tutor, base, alumno_id):
    dominio.completar_modulo(base, alumno_id, 1, "tutor", "Semilla.")
    dominio.guardar_idea(base, alumno_id, "# Recetas", None, "tutor")
    dominio.completar_modulo(base, alumno_id, 2, "tutor", "Idea lista.")

    _, turnos = await _charlar(tutor, alumno_id, 3, ["No sé", "Windows, la de mi trabajo", "No sé cuál"])

    assert "Mac o una" in _texto(turnos[1]) or "Mac o Windows" in _texto(turnos[1])
    assert _datos(turnos[2], "taller") == []
    assert _datos(turnos[3], "taller") == []
    assert dominio.alumno(base, alumno_id)["herramienta"] is None


async def test_despues_de_cerrar_el_modulo_no_vuelve_a_marcarlo(tutor, base, alumno_id):
    sesion_id, _ = await _charlar(tutor, alumno_id, 1, ["Sí", "Nada", "Un blog"])

    otro = await recoger(tutor.turno(sesion_id, alumno_id, "¿Y ahora?"))

    assert _datos(otro, "herramienta") == []
    assert "ya quedó completo" in _texto(otro)
    assert base.execute("SELECT count(*) FROM avance WHERE alumno_id = ?", (alumno_id,)).fetchone()[0] == 1


async def test_el_modo_demo_no_gasta(tutor, base, alumno_id):
    await _charlar(tutor, alumno_id, 1, ["Sí", "Nada", "Un blog"])

    usos = base.execute("SELECT proveedor, modelo, costo_usd, input_tokens, output_tokens FROM uso").fetchall()
    assert usos
    assert {(u["modelo"], u["costo_usd"], u["input_tokens"], u["output_tokens"]) for u in usos} == {(demo.MODELO, 0, 0, 0)}
    assert base.execute("SELECT sum(costo_usd) FROM sesiones").fetchone()[0] == 0
    estado = costos.estado_tope(base, alumno_id, tope_alumno=1.0, tope_mensual=50.0)
    assert estado["gastado_alumno"] == 0 and estado["bloqueado"] is False


async def test_una_captura_sola_cuenta_como_mensaje(tutor, base, alumno_id):
    from vibe_tutor.tutor import Imagen

    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    sesion_id, _ = await _charlar(tutor, alumno_id, 1, [])

    turno = await recoger(tutor.turno(sesion_id, alumno_id, None, Imagen("image/png", png)))

    assert _tipos(turno)[-1] == "fin"
    assert _texto(turno).rstrip().endswith("?")


# --- el guion, sin base ---


def _estado(modulo: int) -> dict:
    return {"role": "user", "content": [{"type": "text", "text": f"Datos...\n- Módulo de esta sesión: {modulo}.\n\nEmpezá el módulo."}]}


def test_guion_saluda_aunque_la_persona_escriba_primero():
    mensajes = [{"role": "user", "content": [*_estado(1)["content"], {"type": "text", "text": "Hola"}]}]

    bloques = demo.guion(mensajes)

    assert [b["type"] for b in bloques] == ["text"]
    assert "modo demo" in bloques[0]["text"].lower()


def test_guion_reintenta_si_la_herramienta_fallo():
    mensajes = [
        _estado(1),
        {"role": "assistant", "content": [{"type": "text", "text": "Hola?"}]},
        *[
            m
            for respuesta in ("a", "b")
            for m in (
                {"role": "user", "content": [{"type": "text", "text": respuesta}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Otra?"}]},
            )
        ],
        {"role": "user", "content": [{"type": "text", "text": "c"}]},
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "t1", "name": "marcar_avance", "input": {"modulo": 1, "resumen": "x"}}],
        },
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "falló", "is_error": True}]},
    ]

    despues_del_error = demo.guion(mensajes)
    mensajes += [
        {"role": "assistant", "content": despues_del_error},
        {"role": "user", "content": [{"type": "text", "text": "dale"}]},
    ]
    reintento = demo.guion(mensajes)

    assert [b["type"] for b in despues_del_error] == ["text"]
    assert [b["name"] for b in reintento if b["type"] == "tool_use"] == ["marcar_avance"]


def test_despues_de_una_herramienta_el_texto_arranca_en_un_parrafo_nuevo():
    mensajes = [
        _estado(1),
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "marcar_avance", "input": {}}]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]},
    ]

    [bloque] = demo.guion(mensajes)

    assert bloque["text"].startswith("\n\nListo, el módulo 1 quedó completo.")


def test_la_idea_del_guion_respeta_los_limites():
    largo = "palabra " * 2000
    mensajes = [_estado(2), {"role": "assistant", "content": [{"type": "text", "text": "¿Qué es?"}]}]
    for respuesta in (largo, largo, largo):
        mensajes += [
            {"role": "user", "content": [{"type": "text", "text": respuesta}]},
            {"role": "assistant", "content": [{"type": "text", "text": "¿Y?"}]},
        ]
    mensajes.pop()

    [pedido] = [b for b in demo.guion(mensajes) if b["type"] == "tool_use"]

    assert pedido["name"] == "guardar_idea"
    assert len(pedido["input"]["texto_md"]) <= dominio.MAX_IDEA
    assert len(pedido["input"]["que_sigue_md"]) <= dominio.MAX_QUE_SIGUE


# --- por HTTP, como lo usa la página ---


def test_recorrido_por_la_api_en_modo_demo(hacer_cliente, settings_demo, base):
    cliente = hacer_cliente([api.router], email="ana@example.com", settings=settings_demo)

    sesion = cliente.post("/api/modulos/1/sesion").json()
    eventos = []
    for texto in (None, "Nunca usé ninguna", "El miedo a no entender", "Una agenda para mi club"):
        ruta = f"/api/sesiones/{sesion['id']}/turno"
        respuesta = cliente.post(ruta, data={"texto": texto}) if texto else cliente.post(ruta)
        assert respuesta.status_code == 200
        eventos.append(leer_sse(respuesta.text))

    assert eventos[0][0] == ("pensando", {})
    assert eventos[0][-1][0] == "fin"
    assert ("avance", {"modulo_completado": 1, "modulo_actual": 2}) in eventos[-1]
    conversacion = cliente.get(f"/api/sesiones/{sesion['id']}").json()
    assert conversacion["pendiente"] is False
    assert [m["rol"] for m in conversacion["mensajes"]] == ["tutor", "alumno", "tutor", "alumno", "tutor", "alumno", "tutor"]
    assert "modo demo" in conversacion["mensajes"][0]["texto"].lower()
    guardados = [json.loads(f[0]) for f in base.execute("SELECT contenido_json FROM mensajes WHERE rol = 'assistant'")]
    assert any(b.get("type") == "tool_use" for bloques in guardados for b in bloques)
