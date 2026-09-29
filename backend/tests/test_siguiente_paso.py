"""Siguiente paso al terminar el curso (spec 002, contracts/api.md): la pregunta que llega con el
primer link, la respuesta que se cuenta sin guardar quién contestó y el aviso como permiso propio."""

import pytest

from vibe_tutor import alumnos, auth, dominio, mails

MAIL = "ana@example.com"
LINK = {"url": "https://mi-idea.netlify.app", "titulo": "Mi registro de sueños"}
VERSION = "2026-10-01"
TEXTOS = {
    "siguiente_paso_nombre": "el curso de prueba",
    "siguiente_paso_pregunta": "¿Tenés un negocio que ya vende?",
    "siguiente_paso_texto": "En marzo abre un curso para construir el sistema que lo gestiona.",
}
INACTIVAS = {
    "apagada": {"siguiente_paso": False},
    "falta-el-nombre": {"siguiente_paso_nombre": ""},
    "falta-la-pregunta": {"siguiente_paso_pregunta": "  "},
    "falta-el-texto": {"siguiente_paso_texto": ""},
}


@pytest.fixture(autouse=True)
def legales(settings_tmp):
    """El texto de los permisos, con la versión que se guarda con cada aviso."""
    carpeta = settings_tmp.contenido_dir / "legal"
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "consentimientos.md").write_text(f"---\nversion: {VERSION}\n---\n\n# Permisos\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def mails_enviados(monkeypatch):
    enviados = []

    async def falso(settings, alumno_id, tipo, clave, datos=None):
        enviados.append((alumno_id, tipo, clave))
        return "enviado"

    monkeypatch.setattr(mails, "enviar", falso)
    return enviados


@pytest.fixture
def activa(settings_tmp):
    """La configuración con la función activa: la bandera prendida y los tres textos."""
    return settings_tmp.model_copy(update={"siguiente_paso": True, **TEXTOS})


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


@pytest.fixture
def entrar(hacer_cliente, base):
    """Un alumno que ya bajó su kit (módulo 4), listo para registrar el link de su página."""

    def _entrar(settings, email: str = MAIL):
        cliente = hacer_cliente([alumnos.router], email=email, settings=settings)
        with base:
            base.execute("UPDATE alumnos SET modulo_actual = 4 WHERE id = ?", (cliente.alumno_id,))
        return cliente

    return _entrar


def _con_link(cliente):
    assert cliente.post("/api/links", json=LINK).status_code == 201
    return cliente


def _respondido(base, alumno_id: int) -> int:
    return base.execute("SELECT siguiente_paso_respondido FROM alumnos WHERE id = ?", (alumno_id,)).fetchone()[0]


def _totales(base) -> dict[str, int]:
    return {f["respuesta"]: f["total"] for f in base.execute("SELECT respuesta, total FROM respuestas_siguiente_paso")}


def _avisos(base, alumno_id: int) -> list[tuple]:
    return [
        tuple(f)
        for f in base.execute(
            "SELECT valor, version_texto FROM consentimientos WHERE alumno_id = ? AND tipo = 'siguiente_paso' ORDER BY id",
            (alumno_id,),
        )
    ]


def _nada_cambio(base, alumno_id: int) -> None:
    assert _respondido(base, alumno_id) == 0
    assert _totales(base) == {}
    assert _avisos(base, alumno_id) == []


# --- La pregunta llega con el primer link (POST /links) ---


def test_el_primer_link_trae_la_pregunta(entrar, activa):
    respuesta = entrar(activa).post("/api/links", json=LINK)

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": respuesta.json()["id"], "mail": True, "pregunta_siguiente_paso": True}


def test_el_segundo_link_no_trae_la_pregunta(entrar, activa):
    cliente = _con_link(entrar(activa))

    segundo = cliente.post("/api/links", json={"url": "https://otra.netlify.app"})

    assert segundo.status_code == 201
    assert segundo.json()["pregunta_siguiente_paso"] is False


def test_borrar_el_primer_link_y_registrar_otro_no_repite_la_pregunta(entrar, activa):
    cliente = entrar(activa)
    link_id = cliente.post("/api/links", json=LINK).json()["id"]
    assert cliente.delete(f"/api/links/{link_id}").status_code == 200

    otro = cliente.post("/api/links", json={"url": "https://otra.netlify.app"})

    assert otro.status_code == 201
    assert otro.json()["pregunta_siguiente_paso"] is False


@pytest.mark.parametrize("cambios", INACTIVAS.values(), ids=INACTIVAS.keys())
def test_con_la_funcion_inactiva_el_primer_link_no_trae_la_pregunta(entrar, activa, cambios):
    respuesta = entrar(activa.model_copy(update=cambios)).post("/api/links", json=LINK)

    assert respuesta.status_code == 201
    assert respuesta.json()["pregunta_siguiente_paso"] is False


def test_quien_ya_contesto_no_recibe_la_pregunta(entrar, activa, base):
    cliente = entrar(activa)
    with base:
        base.execute("UPDATE alumnos SET siguiente_paso_respondido = 1 WHERE id = ?", (cliente.alumno_id,))

    assert cliente.post("/api/links", json=LINK).json()["pregunta_siguiente_paso"] is False


# --- La respuesta (POST /siguiente-paso) ---


def test_contestar_que_si_y_pedir_el_aviso(entrar, activa, base, mails_enviados):
    cliente = _con_link(entrar(activa))
    mails_antes = list(mails_enviados)

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"consentimientos": {"mails_curso": True, "novedades": False, "siguiente_paso": True}}
    assert _respondido(base, cliente.alumno_id) == 1
    assert _totales(base) == {"si": 1}
    assert _avisos(base, cliente.alumno_id) == [(1, VERSION)]
    assert cliente.get("/api/yo").json()["consentimientos"]["siguiente_paso"] is True
    assert mails_enviados == mails_antes


def test_contestar_que_si_sin_pedir_el_aviso(entrar, activa, base):
    cliente = _con_link(entrar(activa))

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "si"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"consentimientos": {"mails_curso": True, "novedades": False, "siguiente_paso": False}}
    assert _respondido(base, cliente.alumno_id) == 1
    assert _totales(base) == {"si": 1}
    assert _avisos(base, cliente.alumno_id) == []


def test_contestar_que_no(entrar, activa, base):
    cliente = _con_link(entrar(activa))

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "no", "aviso": False})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"consentimientos": {"mails_curso": True, "novedades": False, "siguiente_paso": False}}
    assert _respondido(base, cliente.alumno_id) == 1
    assert _totales(base) == {"no": 1}
    assert _avisos(base, cliente.alumno_id) == []


def test_las_respuestas_se_suman_sin_alumno(entrar, activa, base):
    for email, respuesta in (("a@example.com", "si"), ("b@example.com", "no"), ("c@example.com", "si")):
        cliente = _con_link(entrar(activa, email))
        assert cliente.post("/api/siguiente-paso", json={"respuesta": respuesta}).status_code == 200

    assert _totales(base) == {"si": 2, "no": 1}


def test_la_respuesta_no_queda_con_el_alumno_ni_cambia_nada_mas(entrar, activa, base):
    cliente = _con_link(entrar(activa))
    fila_antes = dict(dominio.alumno(base, cliente.alumno_id))
    tablas = ("eventos", "consentimientos", "links", "mails", "avance", "kits")
    antes = {tabla: [tuple(f) for f in base.execute(f"SELECT * FROM {tabla} ORDER BY rowid")] for tabla in tablas}

    assert cliente.post("/api/siguiente-paso", json={"respuesta": "no"}).status_code == 200

    fila = dict(dominio.alumno(base, cliente.alumno_id))
    assert (fila_antes.pop("siguiente_paso_respondido"), fila.pop("siguiente_paso_respondido")) == (0, 1)
    del fila_antes["ultima_actividad"], fila["ultima_actividad"]
    assert fila == fila_antes
    for tabla in tablas:
        assert [tuple(f) for f in base.execute(f"SELECT * FROM {tabla} ORDER BY rowid")] == antes[tabla], tabla


def test_en_modo_demo_anda_igual(entrar, activa, base):
    cliente = _con_link(entrar(activa.model_copy(update={"modo_demo": True})))

    assert cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True}).status_code == 200
    assert _avisos(base, cliente.alumno_id) == [(1, VERSION)]


@pytest.mark.parametrize("cambios", INACTIVAS.values(), ids=INACTIVAS.keys())
def test_con_la_funcion_inactiva_da_409(entrar, activa, base, cambios):
    cliente = _con_link(entrar(activa.model_copy(update=cambios)))

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True})

    assert respuesta.status_code == 409
    assert set(respuesta.json()) == {"detalle"}
    assert respuesta.json()["detalle"] == alumnos.MENSAJE_SIN_SIGUIENTE_PASO
    _nada_cambio(base, cliente.alumno_id)


def test_sin_ningun_link_da_409(entrar, activa, base):
    cliente = entrar(activa)

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True})

    assert respuesta.status_code == 409
    assert "link" in respuesta.json()["detalle"]
    _nada_cambio(base, cliente.alumno_id)


def test_contestar_de_nuevo_da_409_y_cuenta_una_sola_vez(entrar, activa, base):
    cliente = _con_link(entrar(activa))
    assert cliente.post("/api/siguiente-paso", json={"respuesta": "si"}).status_code == 200

    otra = cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True})
    distinta = cliente.post("/api/siguiente-paso", json={"respuesta": "no"})

    assert (otra.status_code, distinta.status_code) == (409, 409)
    assert "contestaste" in otra.json()["detalle"]
    assert _totales(base) == {"si": 1}
    assert _avisos(base, cliente.alumno_id) == []


@pytest.mark.parametrize(
    "cuerpo",
    [
        {},
        {"aviso": True},
        {"respuesta": None},
        {"respuesta": "tal vez"},
        {"respuesta": "sí"},
        {"respuesta": "SI"},
        {"respuesta": True},
        {"respuesta": "si", "aviso": "quizás"},
    ],
)
def test_respuesta_invalida_da_422(entrar, activa, base, cuerpo):
    cliente = _con_link(entrar(activa))

    respuesta = cliente.post("/api/siguiente-paso", json=cuerpo)

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"]
    _nada_cambio(base, cliente.alumno_id)


def test_pedir_el_aviso_contestando_que_no_da_422(entrar, activa, base):
    cliente = _con_link(entrar(activa))

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "no", "aviso": True})

    assert respuesta.status_code == 422
    assert respuesta.json() == {"detalle": alumnos.MENSAJE_AVISO_SIN_NEGOCIO}
    _nada_cambio(base, cliente.alumno_id)
    assert cliente.post("/api/siguiente-paso", json={"respuesta": "no"}).status_code == 200


def test_sin_sesion_da_401(hacer_cliente, activa):
    respuesta = hacer_cliente([alumnos.router], settings=activa).post("/api/siguiente-paso", json={"respuesta": "si"})

    assert respuesta.status_code == 401


def test_una_sesion_pendiente_recibe_el_403_de_la_aprobacion(entrar, activa, base):
    cliente = _con_link(entrar(activa))
    with base:
        base.execute("UPDATE alumnos SET estado = 'pendiente' WHERE id = ?", (cliente.alumno_id,))

    respuesta = cliente.post("/api/siguiente-paso", json={"respuesta": "si", "aviso": True})

    assert (respuesta.status_code, respuesta.json()) == (403, {"detalle": auth.MENSAJE_PENDIENTE, "estado": "pendiente"})
    _nada_cambio(base, cliente.alumno_id)
