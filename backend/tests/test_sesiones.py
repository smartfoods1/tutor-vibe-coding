import json

import pytest
from test_tutor import (
    PNG,
    RESUMEN,
    ClienteFalso,
    Respuesta,
    escribir_contenido,
    herramienta,
    texto,
)

from vibe_tutor import api, costos, dominio
from vibe_tutor import tutor as modulo_tutor
from vibe_tutor.tutor import EventoSSE, Tutor

EMAIL = "ana@example.com"


def leer_sse(cuerpo: str) -> list[tuple[str, dict]]:
    eventos = []
    for bloque in cuerpo.strip("\n").split("\n\n"):
        campos = dict(linea.split(": ", 1) for linea in bloque.split("\n"))
        eventos.append((campos["event"], json.loads(campos["data"])))
    return eventos


class TutorFalso:
    """Tutor que emite eventos fijos, para probar la capa HTTP sola."""

    def __init__(self, tutor_real: Tutor, eventos=None, falla: Exception | None = None):
        self.real = tutor_real
        self.eventos = list(eventos or [])
        self.falla = falla
        self.turnos: list[tuple] = []

    def abrir_sesion(self, alumno_id, modulo):
        return self.real.abrir_sesion(alumno_id, modulo)

    async def turno(self, sesion_id, alumno_id, texto=None, imagen=None):
        self.turnos.append((sesion_id, alumno_id, texto, imagen))
        for evento in self.eventos:
            yield evento
        if self.falla:
            raise self.falla


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


@pytest.fixture
def armar(hacer_cliente, settings_tmp, db_de):
    """Cliente HTTP con la sesión de EMAIL y un tutor con cliente falso de Claude."""
    escribir_contenido(settings_tmp.contenido_dir)

    def _armar(respuestas=(), email=EMAIL, tutor=None):
        cliente = hacer_cliente([api.router], email=email)
        falso = ClienteFalso(respuestas)
        cliente.claude = falso
        cliente.tutor = tutor or Tutor(settings_tmp, db_de, cliente=falso)
        cliente.app.dependency_overrides[api.obtener_tutor] = lambda: cliente.tutor
        return cliente

    return _armar


def avanzar(con, alumno_id: int, modulo: int) -> None:
    if modulo >= 2:
        dominio.completar_modulo(con, alumno_id, 1, "tutor", "Semilla.")
    if modulo >= 3:
        dominio.guardar_idea(con, alumno_id, "# Idea", None, "tutor")
        dominio.completar_modulo(con, alumno_id, 2, "tutor", "Idea lista.")


# --- Abrir sesión ---


def test_abrir_y_retomar_sesion(armar):
    cliente = armar()

    primera = cliente.post("/api/modulos/1/sesion")
    retomada = cliente.post("/api/modulos/1/sesion")

    assert primera.status_code == 200
    assert primera.json() == {"id": primera.json()["id"], "retomada": False}
    assert retomada.json() == {"id": primera.json()["id"], "retomada": True}
    assert cliente.claude.llamadas == []


def test_solo_el_modulo_actual_o_uno_anterior(armar, base):
    cliente = armar()

    adelantado = cliente.post("/api/modulos/2/sesion")
    avanzar(base, cliente.alumno_id, 3)
    actual = cliente.post("/api/modulos/3/sesion")
    anterior = cliente.post("/api/modulos/1/sesion")

    assert adelantado.status_code == 409
    assert "detalle" in adelantado.json()
    assert actual.status_code == 200
    assert anterior.status_code == 200
    assert actual.json()["id"] != anterior.json()["id"]


@pytest.mark.parametrize("modulo", [0, 4, 7])
def test_modulo_fuera_de_la_web(armar, modulo):
    respuesta = armar().post(f"/api/modulos/{modulo}/sesion")

    assert respuesta.status_code == 404
    assert "detalle" in respuesta.json()


def test_abrir_sesion_con_tope_del_alumno(armar, base):
    cliente = armar()
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=cliente.alumno_id)

    respuesta = cliente.post("/api/modulos/1/sesion")

    assert respuesta.status_code == 402
    assert respuesta.json() == {"detalle": "tope", "alcance": "alumno", "guia": "/api/modulos/1/guia"}
    assert base.execute("SELECT COUNT(*) FROM sesiones").fetchone()[0] == 0


def test_abrir_sesion_con_tope_del_mes_aunque_haya_una_abierta(armar, base):
    cliente = armar()
    assert cliente.post("/api/modulos/1/sesion").status_code == 200
    otro = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 50.0, alumno_id=otro)

    respuesta = cliente.post("/api/modulos/1/sesion")

    assert respuesta.status_code == 402
    assert respuesta.json() == {"detalle": "tope", "alcance": "mes", "guia": "/api/modulos/1/guia"}


# --- Ver una sesión ---


def guardar_filas(con, sesion_id: int, filas: list[tuple[str, list[dict]]]) -> None:
    with con:
        for orden, (rol, contenido) in enumerate(filas):
            con.execute(
                "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, ?, ?, ?)",
                (sesion_id, orden, rol, json.dumps(contenido, ensure_ascii=False)),
            )


def test_detalle_de_sesion_solo_mensajes_visibles(armar, base):
    cliente = armar()
    with base:
        sesion_id = base.execute(
            "INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (cliente.alumno_id,)
        ).lastrowid
    guardar_filas(
        base,
        sesion_id,
        [
            ("user", [texto("Datos de este alumno para esta sesión...\n\nEmpezá el módulo.")]),
            ("assistant", [{"type": "thinking", "thinking": "", "signature": "f"}, texto("Hola, soy el tutor.")]),
            ("user", [texto("Quiero una página de recetas.")]),
            ("assistant", [texto("Anoto."), herramienta("t1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})]),
            ("user", [{"type": "tool_result", "tool_use_id": "t1", "content": "Módulo 1 marcado."}]),
            ("assistant", [texto("Terminaste el módulo 1.")]),
            ("user", [texto(modulo_tutor.MARCA_CAPTURA), texto("Me trabé.")]),
            ("user", [texto("¿Seguís ahí?")]),
        ],
    )

    respuesta = cliente.get(f"/api/sesiones/{sesion_id}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": sesion_id,
        "modulo": 1,
        "pendiente": True,
        "mensajes": [
            {"rol": "tutor", "texto": "Hola, soy el tutor."},
            {"rol": "alumno", "texto": "Quiero una página de recetas."},
            {"rol": "tutor", "texto": "Anoto.\n\nTerminaste el módulo 1."},
            {"rol": "alumno", "texto": f"{modulo_tutor.MARCA_CAPTURA}\n\nMe trabé.\n\n¿Seguís ahí?"},
        ],
    }


def test_detalle_de_sesion_nueva(armar):
    cliente = armar()
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]

    detalle = cliente.get(f"/api/sesiones/{sesion_id}").json()

    assert detalle == {"id": sesion_id, "modulo": 1, "pendiente": True, "mensajes": []}


def test_detalle_de_sesion_ajena_o_inexistente(armar, hacer_cliente):
    duena = armar()
    sesion_id = duena.post("/api/modulos/1/sesion").json()["id"]
    otro = armar(email="beto@example.com")

    assert otro.get(f"/api/sesiones/{sesion_id}").status_code == 404
    assert duena.get("/api/sesiones/9999").status_code == 404


# --- Turnos ---


def test_turno_inicial_por_sse(armar):
    cliente = armar([Respuesta([texto("Hola, soy el tutor.")])])
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]

    respuesta = cliente.post(f"/api/sesiones/{sesion_id}/turno")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/event-stream")
    assert respuesta.headers["cache-control"] == "no-cache"
    assert respuesta.headers["x-accel-buffering"] == "no"
    assert respuesta.text.endswith("\n\n")
    eventos = leer_sse(respuesta.text)
    assert eventos[0] == ("pensando", {})
    assert eventos[-1] == ("fin", {"stop_reason": "end_turn"})
    assert "".join(d["delta"] for t, d in eventos if t == "texto") == "Hola, soy el tutor."
    detalle = cliente.get(f"/api/sesiones/{sesion_id}").json()
    assert detalle["pendiente"] is False
    assert detalle["mensajes"] == [{"rol": "tutor", "texto": "Hola, soy el tutor."}]


def test_turno_con_texto_y_avance(armar):
    cliente = armar(
        [
            Respuesta([texto("Hola.")]),
            Respuesta([herramienta("toolu_1", "marcar_avance", {"modulo": 1, "resumen": RESUMEN})], stop_reason="tool_use"),
            Respuesta([texto("Terminaste el módulo 1.")]),
        ]
    )
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]
    cliente.post(f"/api/sesiones/{sesion_id}/turno")

    respuesta = cliente.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "Quiero una página de recetas"})

    eventos = leer_sse(respuesta.text)
    assert ("avance", {"modulo_completado": 1, "modulo_actual": 2}) in eventos
    assert ("herramienta", {"nombre": "marcar_avance", "estado": "fin", "error": False}) in eventos
    assert eventos[-1][0] == "fin"
    assert cliente.claude.llamadas[1]["messages"][-1]["content"][-1] == texto("Quiero una página de recetas")


def test_turno_con_captura(armar, base):
    cliente = armar([Respuesta([texto("Veo la pantalla.")])])
    avanzar(base, cliente.alumno_id, 3)
    sesion_id = cliente.post("/api/modulos/3/sesion").json()["id"]

    respuesta = cliente.post(
        f"/api/sesiones/{sesion_id}/turno",
        data={"texto": "Me trabé"},
        files={"imagen": ("captura.png", PNG, "image/png")},
    )

    assert leer_sse(respuesta.text)[-1][0] == "fin"
    [llamada] = cliente.claude.llamadas
    assert [b["type"] for b in llamada["messages"][0]["content"]] == ["text", "image", "text"]
    detalle = cliente.get(f"/api/sesiones/{sesion_id}").json()
    assert detalle["mensajes"][0] == {"rol": "alumno", "texto": f"{modulo_tutor.MARCA_CAPTURA}\n\nMe trabé"}


def test_turno_captura_con_tipo_mentido(armar):
    cliente = armar()
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]

    respuesta = cliente.post(
        f"/api/sesiones/{sesion_id}/turno",
        files={"imagen": ("captura.png", b"GIF89a" + b"\x00" * 40, "image/png")},
    )

    assert respuesta.status_code == 415
    assert "PNG" in respuesta.json()["detalle"]
    assert cliente.claude.llamadas == []


def test_turno_captura_demasiado_grande(armar):
    cliente = armar()
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]
    grande = PNG + b"\x00" * (5 * 1024 * 1024)

    respuesta = cliente.post(f"/api/sesiones/{sesion_id}/turno", files={"imagen": ("c.png", grande, "image/png")})

    assert respuesta.status_code == 413
    assert "5 MB" in respuesta.json()["detalle"]
    assert cliente.claude.llamadas == []


def test_turno_texto_demasiado_largo(armar):
    cliente = armar()
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]

    respuesta = cliente.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "a" * 4001})

    assert respuesta.status_code == 422
    assert "4.000" in respuesta.json()["detalle"]
    assert cliente.claude.llamadas == []


def test_turno_sin_nada_y_sin_pendiente(armar):
    cliente = armar([Respuesta([texto("Hola.")])])
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]
    cliente.post(f"/api/sesiones/{sesion_id}/turno")

    vacio = cliente.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "   "})
    sin_cuerpo = cliente.post(f"/api/sesiones/{sesion_id}/turno")

    assert vacio.status_code == 422
    assert sin_cuerpo.status_code == 422
    assert len(cliente.claude.llamadas) == 1


def test_turno_en_sesion_ajena(armar):
    duena = armar()
    sesion_id = duena.post("/api/modulos/1/sesion").json()["id"]
    otro = armar(email="beto@example.com")

    assert otro.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "hola"}).status_code == 404
    assert otro.post("/api/sesiones/9999/turno", data={"texto": "hola"}).status_code == 404
    assert otro.claude.llamadas == []


def test_turno_con_tope_llega_como_evento(armar, base):
    cliente = armar()
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 1.0, alumno_id=cliente.alumno_id)

    respuesta = cliente.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "hola"})

    assert respuesta.status_code == 200
    assert leer_sse(respuesta.text) == [("tope", {"alcance": "alumno", "guia": "/api/modulos/1/guia"})]
    assert cliente.claude.llamadas == []


def test_excepcion_del_tutor_cierra_con_error(armar, settings_tmp, db_de):
    real = Tutor(settings_tmp, db_de, cliente=ClienteFalso([]))
    falso = TutorFalso(real, eventos=[EventoSSE("texto", {"delta": "Ho"})], falla=RuntimeError("se rompió"))
    cliente = armar(tutor=falso)
    sesion_id = cliente.post("/api/modulos/1/sesion").json()["id"]

    eventos = leer_sse(cliente.post(f"/api/sesiones/{sesion_id}/turno", data={"texto": "hola"}).text)

    assert eventos[0] == ("texto", {"delta": "Ho"})
    tipo, datos = eventos[-1]
    assert tipo == "error"
    assert datos["reintentable"] is True
    assert "se rompió" not in datos["mensaje"]
    assert falso.turnos == [(sesion_id, cliente.alumno_id, "hola", None)]


RUTAS = [
    ("POST", "/api/modulos/1/sesion"),
    ("GET", "/api/sesiones/1"),
    ("POST", "/api/sesiones/1/turno"),
]


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS)
def test_rutas_protegidas(hacer_cliente, metodo, ruta):
    cliente = hacer_cliente([api.router])

    respuesta = cliente.request(metodo, ruta)

    assert respuesta.status_code == 401
    assert "detalle" in respuesta.json()


def test_obtener_tutor_arma_uno_solo_por_app(hacer_cliente, settings_tmp):
    cliente = hacer_cliente([api.router], email=EMAIL)
    app = cliente.app

    class Pedido:
        def __init__(self):
            self.app = app

    primero = api.obtener_tutor(Pedido(), settings_tmp)
    segundo = api.obtener_tutor(Pedido(), settings_tmp)

    assert isinstance(primero, Tutor)
    assert primero is segundo
    assert primero.settings is settings_tmp
