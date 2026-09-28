import json
import logging
import re
from datetime import datetime, timedelta, timezone

import jwt
import pytest
import respx
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from vibe_tutor import auth, db, dominio, errores, mails
from vibe_tutor.config import get_settings

RESEND = "https://api.resend.com/emails"
SITEVERIFY = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
MAIL = "ana@example.com"
ADMIN = "admin@example.com"
HOST_PUBLICO = "https://curso.example.test"
CODIGO_DEV = "424242"
T0 = datetime(2026, 9, 26, 15, 0, tzinfo=timezone.utc)
CONSENTIDO = {"mails_curso": True, "transferencia": True, "novedades": False}


def _app(settings) -> FastAPI:
    app = FastAPI()
    errores.instalar(app)
    app.include_router(auth.router)

    @app.get("/api/yo-prueba")
    def yo(alumno: auth.Alumno = Depends(auth.alumno_actual)) -> dict:
        return {"id": alumno.id, "email": alumno.email, "es_admin": alumno.es_admin}

    @app.get("/api/solo-admin")
    def admin(alumno: auth.Alumno = Depends(auth.solo_admin)) -> dict:
        return {"ok": True}

    @app.get("/api/aprobado-prueba")
    def aprobado(alumno: auth.Alumno = Depends(auth.alumno_aprobado)) -> dict:
        return {"id": alumno.id, "estado": alumno.estado}

    app.dependency_overrides[get_settings] = lambda: settings
    return app


@pytest.fixture
def reloj(monkeypatch):
    estado = {"ahora": T0}
    monkeypatch.setattr(auth, "ahora", lambda: estado["ahora"])
    return estado


@pytest.fixture
def mails_enviados(monkeypatch):
    enviados = []

    async def falso(settings, alumno_id, tipo, clave, datos=None):
        enviados.append((alumno_id, tipo, clave) if datos is None else (alumno_id, tipo, clave, datos))
        return "enviado"

    monkeypatch.setattr(mails, "enviar", falso)
    return enviados


@pytest.fixture
def externos():
    with respx.mock(assert_all_called=False) as mock:
        mock.post(RESEND).respond(200, json={"id": "mail-1"})
        mock.post(SITEVERIFY).respond(
            200, json={"success": True, "hostname": "localhost", "action": "inscripcion"}
        )
        yield mock


@pytest.fixture
def resend(externos):
    return externos.routes[0]


@pytest.fixture
def turnstile(externos):
    return externos.routes[1]


@pytest.fixture
def cliente(settings_tmp, reloj, externos, mails_enviados):
    with TestClient(_app(settings_tmp), base_url="https://testserver") as c:
        yield c


@pytest.fixture
def settings_dev(settings_tmp):
    return settings_tmp.model_copy(update={"dev_codigo_fijo": CODIGO_DEV})


def _pedir(cliente, email=MAIL, **extra):
    cuerpo = {"email": email, "turnstile": "token-ok", "consentimientos": CONSENTIDO, **extra}
    return cliente.post("/api/auth/codigo", json=cuerpo)


def _codigo_enviado(ruta) -> str:
    cuerpo = json.loads(ruta.calls.last.request.content)
    return re.search(r"\b(\d{6})\b", cuerpo["text"]).group(1)


def _entrar(cliente, resend, email=MAIL, **extra):
    _pedir(cliente, email, **extra)
    return cliente.post("/api/auth/verificar", json={"email": email, "codigo": _codigo_enviado(resend)})


def _otro(codigo: str) -> str:
    return f"{(int(codigo) + 1) % 1_000_000:06d}"


def _con(settings):
    con = db.conectar(settings.data_dir / db.ARCHIVO)
    db.migrar(con)
    return con


def test_cualquier_mail_recibe_codigo(cliente, resend):
    respuesta = _pedir(cliente)

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}
    assert resend.call_count == 1
    assert json.loads(resend.calls.last.request.content)["to"] == [MAIL]
    assert "set-cookie" not in respuesta.headers


def test_mail_del_codigo(cliente, resend, settings_tmp):
    _pedir(cliente)

    pedido = resend.calls.last.request
    cuerpo = json.loads(pedido.content)
    assert pedido.headers["authorization"] == f"Bearer {settings_tmp.resend_api_key}"
    assert cuerpo["from"] == settings_tmp.mail_from
    assert "código" in cuerpo["subject"].lower()
    assert "10 minutos" in cuerpo["text"]


def test_mail_invalido_da_422(cliente, resend):
    respuesta = _pedir(cliente, email="no-es-un-mail")

    assert respuesta.status_code == 422
    assert "detalle" in respuesta.json()
    assert resend.call_count == 0


def test_turnstile_invalido_da_400(cliente, resend, turnstile):
    turnstile.respond(200, json={"success": False, "error-codes": ["invalid-input-response"]})

    respuesta = _pedir(cliente)

    assert respuesta.status_code == 400
    assert "detalle" in respuesta.json()
    assert resend.call_count == 0


@pytest.mark.parametrize(
    "respuesta_cf",
    [
        {"success": True, "hostname": "otro.example.com", "action": "inscripcion"},
        {"success": True, "hostname": "localhost", "action": "otra"},
    ],
)
def test_turnstile_chequea_hostname_y_accion(cliente, resend, turnstile, respuesta_cf):
    turnstile.respond(200, json=respuesta_cf)

    assert _pedir(cliente).status_code == 400
    assert resend.call_count == 0


def test_turnstile_manda_secreto_token_e_ip(cliente, turnstile, settings_tmp):
    _pedir(cliente)

    enviado = turnstile.calls.last.request.content.decode()
    assert settings_tmp.turnstile_secret in enviado
    assert "token-ok" in enviado
    assert "remoteip=testclient" in enviado


def test_sin_turnstile_configurado_no_lo_verifica(settings_tmp, reloj, externos, mails_enviados, turnstile, resend):
    sin_turnstile = settings_tmp.model_copy(update={"turnstile_site_key": "", "turnstile_secret": ""})
    with TestClient(_app(sin_turnstile), base_url="https://testserver") as c:
        respuesta = c.post("/api/auth/codigo", json={"email": MAIL, "consentimientos": CONSENTIDO})

    assert respuesta.status_code == 200
    assert turnstile.call_count == 0
    assert resend.call_count == 1


@pytest.mark.parametrize(
    ("consentimientos", "motivo"),
    [
        ({"mails_curso": False, "transferencia": True}, "mails"),
        ({"mails_curso": True, "transferencia": False}, "Estados Unidos"),
        ({}, "mails"),
    ],
)
def test_mail_nuevo_sin_consentimientos_obligatorios_da_422(cliente, resend, consentimientos, motivo):
    respuesta = _pedir(cliente, consentimientos=consentimientos)

    assert respuesta.status_code == 422
    assert motivo in respuesta.json()["detalle"]
    assert resend.call_count == 0


def test_alumno_existente_no_necesita_consentimientos_de_nuevo(cliente, resend, settings_tmp):
    con = _con(settings_tmp)
    dominio.crear_alumno(con, MAIL, fuente=None)
    con.close()

    respuesta = cliente.post("/api/auth/codigo", json={"email": MAIL, "turnstile": "token-ok"})

    assert respuesta.status_code == 200
    assert resend.call_count == 1


def test_codigo_guardado_con_hash_ip_y_pendientes(cliente, resend, settings_tmp):
    _pedir(cliente, fuente="hecho-en")
    codigo = _codigo_enviado(resend)

    con = _con(settings_tmp)
    (fila,) = con.execute("SELECT * FROM codigos").fetchall()
    con.close()
    assert codigo not in fila["hash"] and codigo not in fila["sal"]
    assert fila["email"] == MAIL
    assert fila["ip"] == "testclient"
    assert datetime.fromisoformat(fila["vence"]) == T0 + timedelta(minutes=10)
    assert json.loads(fila["pendiente_json"]) == {"consentimientos": CONSENTIDO, "fuente": "hecho-en"}


def test_verificar_crea_el_alumno_con_consentimientos_fuente_y_evento(cliente, resend, settings_tmp, mails_enviados):
    respuesta = _entrar(cliente, resend, fuente="hecho-en")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True, "nuevo": True, "estado": "aprobado"}
    con = _con(settings_tmp)
    alumno = dominio.alumno_por_email(con, MAIL)
    assert alumno["fuente"] == "hecho-en"
    assert dominio.consentimiento(con, alumno["id"], "mails_curso") is True
    assert dominio.consentimiento(con, alumno["id"], "transferencia") is True
    assert dominio.consentimiento(con, alumno["id"], "novedades") is False
    versiones = {f["version_texto"] for f in con.execute("SELECT version_texto FROM consentimientos")}
    assert versiones and "" not in versiones
    eventos = [tuple(f) for f in con.execute("SELECT alumno_id, tipo, detalle FROM eventos")]
    assert eventos == [(alumno["id"], "inscripcion", "fuente=hecho-en")]
    assert alumno["estado"] == "aprobado"
    pendientes = con.execute("SELECT pendiente_json FROM codigos").fetchone()[0]
    con.close()
    assert pendientes is None
    assert mails_enviados == [(alumno["id"], "bienvenida", "bienvenida")]


@pytest.mark.parametrize(("newsletter", "guardado"), [("El boletín de Ana", True), ("", False), ("   ", False)])
def test_las_novedades_se_guardan_solo_si_el_curso_tiene_newsletter(
    settings_tmp, reloj, externos, resend, mails_enviados, newsletter, guardado
):
    settings = settings_tmp.model_copy(update={"newsletter_nombre": newsletter})
    with TestClient(_app(settings), base_url="https://testserver") as c:
        respuesta = _entrar(c, resend, consentimientos={**CONSENTIDO, "novedades": True})

    assert respuesta.status_code == 200
    con = _con(settings_tmp)
    alumno = dominio.alumno_por_email(con, MAIL)
    assert dominio.consentimiento(con, alumno["id"], "novedades") is guardado
    tipos = sorted(f["tipo"] for f in con.execute("SELECT tipo FROM consentimientos"))
    con.close()
    assert tipos == ["mails_curso", "novedades", "transferencia"]


def test_en_modo_demo_el_codigo_no_se_manda_y_el_log_no_lo_muestra(
    settings_tmp, reloj, externos, resend, mails_enviados, monkeypatch, caplog
):
    demo = settings_tmp.model_copy(update={"modo_demo": True, "resend_api_key": ""})
    monkeypatch.setattr(auth.secrets, "randbelow", lambda tope: 918273)
    caplog.set_level(logging.DEBUG)
    with TestClient(_app(demo), base_url="https://testserver") as c:
        respuesta = _pedir(c)

    assert respuesta.status_code == 200
    assert resend.call_count == 0
    registros = " ".join(r.getMessage() for r in caplog.records)
    assert "918273" not in registros
    assert auth.ASUNTO in registros
    assert MAIL in registros


def test_segunda_entrada_no_duplica_alumno_ni_bienvenida(cliente, resend, settings_tmp, mails_enviados):
    _entrar(cliente, resend)
    cliente.post("/api/auth/salir")

    respuesta = _entrar(cliente, resend)

    assert respuesta.json() == {"ok": True, "nuevo": False, "estado": "aprobado"}
    con = _con(settings_tmp)
    assert con.execute("SELECT count(*) FROM alumnos").fetchone()[0] == 1
    assert con.execute("SELECT count(*) FROM eventos WHERE tipo = 'inscripcion'").fetchone()[0] == 1
    con.close()
    assert len(mails_enviados) == 1


def test_cookie_de_sesion(cliente, resend, settings_tmp):
    respuesta = _entrar(cliente, resend)

    cookie = respuesta.headers["set-cookie"]
    assert auth.COOKIE == "__Host-vibe_sesion"
    assert cookie.startswith("__Host-vibe_sesion=")
    for atributo in ("HttpOnly", "Secure", "SameSite=strict", "Path=/", "Max-Age=2592000"):
        assert atributo in cookie
    assert "domain" not in cookie.lower()
    datos = jwt.decode(
        respuesta.cookies[auth.COOKIE],
        settings_tmp.jwt_secret,
        algorithms=["HS256"],
        options={"verify_iat": False, "verify_exp": False},
    )
    con = _con(settings_tmp)
    alumno_id = dominio.alumno_por_email(con, MAIL)["id"]
    con.close()
    assert datos["sub"] == str(alumno_id)
    assert datos["exp"] - datos["iat"] == 30 * 24 * 3600
    assert cliente.get("/api/yo-prueba").json() == {"id": alumno_id, "email": MAIL, "es_admin": False}


def test_admin_por_mail(cliente, resend):
    _entrar(cliente, resend, email="Admin@Example.com")

    assert cliente.get("/api/yo-prueba").json()["es_admin"] is True
    assert cliente.get("/api/solo-admin").status_code == 200


def test_no_admin_da_403(cliente, resend):
    _entrar(cliente, resend)

    respuesta = cliente.get("/api/solo-admin")

    assert respuesta.status_code == 403
    assert "detalle" in respuesta.json()


def test_codigo_de_un_solo_uso(cliente, resend):
    _pedir(cliente)
    codigo = _codigo_enviado(resend)

    primera = cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo})
    segunda = cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo})

    assert primera.status_code == 200
    assert segunda.status_code == 401
    assert "detalle" in segunda.json()


def test_vencido(cliente, resend, reloj):
    _pedir(cliente)
    codigo = _codigo_enviado(resend)

    reloj["ahora"] = T0 + timedelta(minutes=11)
    respuesta = cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo})

    assert respuesta.status_code == 401
    assert "set-cookie" not in respuesta.headers


def test_vigente_a_los_nueve_minutos(cliente, resend, reloj):
    _pedir(cliente)
    codigo = _codigo_enviado(resend)

    reloj["ahora"] = T0 + timedelta(minutes=9)

    assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo}).status_code == 200


def test_cinco_intentos(cliente, resend):
    _pedir(cliente)
    codigo = _codigo_enviado(resend)

    for _ in range(5):
        assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": _otro(codigo)}).status_code == 401

    respuesta = cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo})
    assert respuesta.status_code == 401
    assert "set-cookie" not in respuesta.headers


def test_codigo_nuevo_invalida_el_anterior(cliente, resend):
    _pedir(cliente)
    viejo = _codigo_enviado(resend)
    _pedir(cliente)
    nuevo = _codigo_enviado(resend)

    if viejo != nuevo:
        assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": viejo}).status_code == 401
    assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": nuevo}).status_code == 200


def test_verificar_con_codigo_de_otro_mail(cliente, resend):
    _pedir(cliente)
    codigo = _codigo_enviado(resend)

    respuesta = cliente.post("/api/auth/verificar", json={"email": "otra@example.com", "codigo": codigo})

    assert respuesta.status_code == 401


def test_limite_por_mail(cliente, resend, reloj):
    for minuto in range(6):
        reloj["ahora"] = T0 + timedelta(minutes=minuto)
        assert _pedir(cliente).json() == {"ok": True}

    assert resend.call_count == 5

    reloj["ahora"] = T0 + timedelta(minutes=61)
    _pedir(cliente)
    assert resend.call_count == 6


def test_limite_por_ip(settings_tmp, reloj, externos, mails_enviados, resend):
    ajustado = settings_tmp.model_copy(update={"max_codigos_ip_hora": 3})
    with TestClient(_app(ajustado), base_url="https://testserver") as c:
        for numero in range(5):
            assert _pedir(c, email=f"persona{numero}@example.com").status_code == 200

    assert resend.call_count == 3


def test_limite_diario_global(settings_tmp, reloj, externos, mails_enviados, resend):
    ajustado = settings_tmp.model_copy(update={"max_codigos_dia": 2})
    with TestClient(_app(ajustado), base_url="https://testserver") as c:
        for numero in range(3):
            reloj["ahora"] = T0 + timedelta(minutes=numero)
            _pedir(c, email=f"persona{numero}@example.com")
        assert resend.call_count == 2

        reloj["ahora"] = T0 + timedelta(hours=24, minutes=1)
        _pedir(c, email="otra@example.com")

    assert resend.call_count == 3


def test_resend_caido_responde_igual(settings_tmp, reloj, mails_enviados, caplog):
    caplog.set_level(logging.DEBUG)
    with respx.mock(assert_all_called=False) as mock:
        ruta = mock.post(RESEND).respond(500, json={"message": "error"})
        mock.post(SITEVERIFY).respond(200, json={"success": True, "hostname": "localhost", "action": "inscripcion"})
        with TestClient(_app(settings_tmp), base_url="https://testserver") as c:
            respuesta = _pedir(c)

    assert ruta.call_count == 1
    assert respuesta.json() == {"ok": True}
    assert any(r.levelno == logging.ERROR and r.name == auth.__name__ for r in caplog.records)
    assert _codigo_enviado(ruta) not in caplog.text
    assert settings_tmp.resend_api_key not in caplog.text


def test_ruta_protegida(cliente):
    respuesta = cliente.get("/api/yo-prueba")

    assert respuesta.status_code == 401
    assert "detalle" in respuesta.json()


def test_cookie_invalida(cliente, settings_tmp):
    con = _con(settings_tmp)
    alumno_id = dominio.crear_alumno(con, MAIL, fuente=None)
    con.close()

    def token(clave, sub=str(alumno_id), dias=1, algoritmo="HS256"):
        datos = {"sub": sub, "iat": T0 - timedelta(days=1), "exp": T0 + timedelta(days=dias)}
        return jwt.encode(datos, clave, algorithm=algoritmo)

    secreto = settings_tmp.jwt_secret
    cliente.cookies.set(auth.COOKIE, token(secreto))
    assert cliente.get("/api/yo-prueba").status_code == 200

    invalidos = (
        token("x" * 64),
        token(secreto, dias=-1),
        token(secreto, sub="999"),
        token(secreto, sub=MAIL),
        token(None, algoritmo="none"),
        jwt.encode({"sub": str(alumno_id)}, secreto, algorithm="HS256"),
        "basura",
    )
    for invalido in invalidos:
        cliente.cookies.set(auth.COOKIE, invalido)
        assert cliente.get("/api/yo-prueba").status_code == 401


def test_alumno_borrado_pierde_la_sesion(cliente, resend, settings_tmp):
    _entrar(cliente, resend)
    con = _con(settings_tmp)
    con.execute("DELETE FROM alumnos")
    con.commit()
    con.close()

    assert cliente.get("/api/yo-prueba").status_code == 401


def test_sesion_dura_treinta_dias(cliente, resend, reloj):
    _entrar(cliente, resend)

    reloj["ahora"] = T0 + timedelta(days=29, hours=23)
    assert cliente.get("/api/yo-prueba").status_code == 200

    reloj["ahora"] = T0 + timedelta(days=30, seconds=1)
    assert cliente.get("/api/yo-prueba").status_code == 401


def test_salir(cliente, resend):
    _entrar(cliente, resend)

    respuesta = cliente.post("/api/auth/salir")

    assert respuesta.json() == {"ok": True}
    cookie = respuesta.headers["set-cookie"]
    assert cookie.startswith(f"{auth.COOKIE}=") and "Max-Age=0" in cookie
    assert cliente.get("/api/yo-prueba").status_code == 401


def test_dev_codigo_solo_localhost(settings_dev, reloj, externos, mails_enviados):
    with TestClient(_app(settings_dev), base_url=HOST_PUBLICO, client=("127.0.0.1", 50000)) as c:
        respuesta = c.post("/api/auth/verificar", json={"email": MAIL, "codigo": CODIGO_DEV})

    assert respuesta.status_code == 401


def test_dev_codigo_desde_ip_externa(settings_dev, reloj, externos, mails_enviados):
    with TestClient(_app(settings_dev), base_url="https://localhost", client=("203.0.113.9", 50000)) as c:
        respuesta = c.post("/api/auth/verificar", json={"email": MAIL, "codigo": CODIGO_DEV})

    assert respuesta.status_code == 401


@pytest.mark.parametrize("base_url", ["https://localhost", "https://127.0.0.1:8340"])
def test_dev_codigo_en_localhost_crea_al_alumno(settings_dev, reloj, externos, mails_enviados, resend, base_url):
    with TestClient(_app(settings_dev), base_url=base_url, client=("127.0.0.1", 50000)) as c:
        respuesta = c.post("/api/auth/verificar", json={"email": MAIL, "codigo": CODIGO_DEV})
        assert respuesta.status_code == 200
        assert c.get("/api/yo-prueba").json()["email"] == MAIL

    assert resend.call_count == 0


def test_sin_dev_codigo_configurado(settings_tmp, reloj, externos, mails_enviados):
    with TestClient(_app(settings_tmp), base_url="https://localhost", client=("127.0.0.1", 50000)) as c:
        respuesta = c.post("/api/auth/verificar", json={"email": MAIL, "codigo": CODIGO_DEV})

    assert respuesta.status_code == 401


# --- aprobación manual (APROBACION_MANUAL) ----------------------------------------------------------


@pytest.fixture
def manual(settings_tmp, reloj, externos, mails_enviados):
    """Cliente de una instalación donde quien administra aprueba cada inscripción."""
    settings = settings_tmp.model_copy(update={"aprobacion_manual": True})
    with TestClient(_app(settings), base_url="https://testserver") as c:
        yield c


def test_con_aprobacion_manual_el_alumno_nuevo_queda_pendiente_y_avisa(manual, resend, settings_tmp, mails_enviados):
    respuesta = _entrar(manual, resend, fuente="hecho-en")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True, "nuevo": True, "estado": "pendiente"}
    assert respuesta.cookies.get(auth.COOKIE)
    con = _con(settings_tmp)
    alumno = dominio.alumno_por_email(con, MAIL)
    eventos = [tuple(f) for f in con.execute("SELECT alumno_id, tipo FROM eventos")]
    con.close()
    assert alumno["estado"] == "pendiente"
    assert alumno["fuente"] == "hecho-en"
    assert eventos == [(alumno["id"], "inscripcion")]
    # Sin bienvenida: sale el aviso a quien administra, con clave por hora de Argentina (T0 son las 12).
    assert mails_enviados == [(None, "pedidos", "pedidos:2026-09-26T12", {"pendientes": 1})]


def test_con_aprobacion_manual_el_aviso_cuenta_los_pendientes(manual, resend, reloj, mails_enviados):
    _entrar(manual, resend)
    reloj["ahora"] = T0 + timedelta(minutes=30)
    _entrar(manual, resend, email="beto@example.com")
    reloj["ahora"] = T0 + timedelta(hours=1)
    _entrar(manual, resend, email="caro@example.com")

    assert mails_enviados == [
        (None, "pedidos", "pedidos:2026-09-26T12", {"pendientes": 1}),
        (None, "pedidos", "pedidos:2026-09-26T12", {"pendientes": 2}),
        (None, "pedidos", "pedidos:2026-09-26T13", {"pendientes": 3}),
    ]


def test_con_aprobacion_manual_quien_administra_entra_aprobado(manual, resend, settings_tmp, mails_enviados):
    respuesta = _entrar(manual, resend, email="Admin@Example.com")

    assert respuesta.json() == {"ok": True, "nuevo": True, "estado": "aprobado"}
    con = _con(settings_tmp)
    alumno = dominio.alumno_por_email(con, ADMIN)
    con.close()
    assert alumno["estado"] == "aprobado"
    assert mails_enviados == [(alumno["id"], "bienvenida", "bienvenida")]


def test_un_pendiente_que_vuelve_a_entrar_sigue_pendiente_sin_otro_aviso(manual, resend, mails_enviados):
    _entrar(manual, resend)
    manual.post("/api/auth/salir")

    respuesta = _entrar(manual, resend)

    assert respuesta.json() == {"ok": True, "nuevo": False, "estado": "pendiente"}
    assert len(mails_enviados) == 1


def test_un_aprobado_entra_aprobado_aunque_se_active_la_aprobacion_manual(cliente, manual, resend, mails_enviados):
    assert _entrar(cliente, resend).json()["estado"] == "aprobado"

    respuesta = _entrar(manual, resend)

    assert respuesta.json() == {"ok": True, "nuevo": False, "estado": "aprobado"}
    assert [m[1] for m in mails_enviados] == ["bienvenida"]


def test_quien_espera_aprobacion_tiene_sesion_pero_no_acceso(manual, resend):
    _entrar(manual, resend)

    assert manual.get("/api/yo-prueba").status_code == 200
    respuesta = manual.get("/api/aprobado-prueba")

    assert respuesta.status_code == 403
    assert respuesta.json() == {"detalle": auth.MENSAJE_PENDIENTE, "estado": "pendiente"}
    assert auth.MENSAJE_PENDIENTE == (
        "Tu pedido de acceso está pendiente. Te avisamos por mail cuando esté aprobado."
    )


def test_alumno_aprobado_deja_pasar_a_los_aprobados(cliente, resend):
    _entrar(cliente, resend)

    assert cliente.get("/api/aprobado-prueba").json()["estado"] == "aprobado"
    cliente.cookies.clear()
    assert cliente.get("/api/aprobado-prueba").status_code == 401


def test_quien_administra_siempre_cuenta_como_aprobado(cliente, settings_tmp):
    con = _con(settings_tmp)
    admin_id = dominio.crear_alumno(con, ADMIN, fuente=None, estado="pendiente")
    con.close()
    cliente.cookies.set(auth.COOKIE, auth.emitir_token(settings_tmp, admin_id))

    assert cliente.get("/api/aprobado-prueba").json() == {"id": admin_id, "estado": "aprobado"}


# --- fallos acumulados por mail ------------------------------------------------------------------


def _fallar(cliente, resend, veces: int) -> str:
    """Pide un código nuevo y lo erra `veces` veces; devuelve el código bueno."""
    _pedir(cliente)
    codigo = _codigo_enviado(resend)
    for _ in range(veces):
        assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": _otro(codigo)}).status_code == 401
    return codigo


def test_diez_fallos_en_el_dia_todavia_dejan_entrar(cliente, resend, reloj):
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=20)
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=40)
    codigo = _fallar(cliente, resend, 0)

    assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo}).status_code == 200


def test_mas_de_diez_fallos_en_24_horas_bloquean_el_mail(cliente, resend, reloj, settings_tmp):
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=20)
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=40)
    codigo = _fallar(cliente, resend, 1)

    respuesta = cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo})

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detalle": auth.MENSAJE_CODIGO}
    assert "set-cookie" not in respuesta.headers
    con = _con(settings_tmp)
    assert con.execute("SELECT count(*) FROM alumnos").fetchone()[0] == 0
    con.close()


def test_el_bloqueo_no_toca_a_otros_mails(cliente, resend, reloj):
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=20)
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=40)
    _fallar(cliente, resend, 1)

    assert _entrar(cliente, resend, email="otra@example.com").status_code == 200


def test_el_bloqueo_se_levanta_cuando_pasa_la_ventana(cliente, resend, reloj):
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=20)
    _fallar(cliente, resend, 5)
    reloj["ahora"] = T0 + timedelta(minutes=40)
    _fallar(cliente, resend, 1)

    reloj["ahora"] = T0 + timedelta(hours=24, minutes=41)
    codigo = _fallar(cliente, resend, 0)

    assert cliente.post("/api/auth/verificar", json={"email": MAIL, "codigo": codigo}).status_code == 200


# --- anti CSRF -------------------------------------------------------------------------------------


def _app_csrf(settings) -> FastAPI:
    app = _app(settings)
    auth.instalar_csrf(app)

    @app.api_route("/api/cambiar", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def cambiar() -> dict:
        return {"ok": True}

    return app


@pytest.mark.parametrize("metodo", ["POST", "PUT", "PATCH", "DELETE"])
@pytest.mark.parametrize("sitio", ["cross-site", "same-site", "otra-cosa"])
def test_csrf_rechaza_pedidos_que_cambian_datos_desde_otro_sitio(settings_tmp, metodo, sitio):
    with TestClient(_app_csrf(settings_tmp), base_url="https://testserver") as c:
        respuesta = c.request(metodo, "/api/cambiar", headers={"Sec-Fetch-Site": sitio})

    assert respuesta.status_code == 403
    assert respuesta.json()["detalle"]


@pytest.mark.parametrize("metodo", ["POST", "PUT", "PATCH", "DELETE"])
@pytest.mark.parametrize("cabeceras", [{"Sec-Fetch-Site": "same-origin"}, {"Sec-Fetch-Site": "none"}, {}])
def test_csrf_deja_pasar_la_propia_pagina_y_los_pedidos_sin_la_cabecera(settings_tmp, metodo, cabeceras):
    with TestClient(_app_csrf(settings_tmp), base_url="https://testserver") as c:
        respuesta = c.request(metodo, "/api/cambiar", headers=cabeceras)

    assert respuesta.status_code == 200


def test_csrf_no_toca_las_lecturas(settings_tmp):
    with TestClient(_app_csrf(settings_tmp), base_url="https://testserver") as c:
        respuesta = c.get("/api/cambiar", headers={"Sec-Fetch-Site": "cross-site"})

    assert respuesta.status_code == 200


def test_la_app_real_trae_el_anti_csrf():
    from vibe_tutor.main import crear_app

    with TestClient(crear_app(), base_url="https://testserver") as c:
        otro_sitio = c.post("/api/auth/salir", headers={"Sec-Fetch-Site": "cross-site"})
        propio = c.post("/api/auth/salir", headers={"Sec-Fetch-Site": "same-origin"})

    assert otro_sitio.status_code == 403
    assert otro_sitio.json()["detalle"]
    assert propio.status_code == 200
