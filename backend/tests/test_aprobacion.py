"""Aprobación manual de las inscripciones (APROBACION_MANUAL), con la app completa.

Quien espera aprobación tiene sesión, pero solo llega a su estado, sus datos, sus permisos y la
salida; el resto de las rutas del alumno le responden 403 con el estado "pendiente". Los tests
recorren todas las rutas de la app, así una ruta nueva que se olvide de `auth.alumno_aprobado`
hace fallar el test.
"""

import re

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from vibe_tutor import auth, dominio, mails
from vibe_tutor.config import get_settings
from vibe_tutor.main import crear_app

MAIL = "ana@example.com"
ADMIN = "admin@example.com"
PENDIENTE = {"detalle": auth.MENSAJE_PENDIENTE, "estado": "pendiente"}
# Lo que quien espera aprobación sí puede usar, además de las rutas públicas.
PERMITIDAS = {
    ("GET", "/api/yo"),
    ("GET", "/api/mis-datos"),
    ("DELETE", "/api/mis-datos"),
    ("PUT", "/api/consentimientos"),
    ("POST", "/api/auth/salir"),
}
PUBLICAS = {
    ("GET", "/api/salud"),
    ("GET", "/api/config"),
    ("POST", "/api/auth/codigo"),
    ("POST", "/api/auth/verificar"),
    ("GET", "/api/legal/privacidad"),
    ("GET", "/api/legal/consentimientos"),
    ("GET", "/api/galeria"),
    ("GET", "/api/baja"),
    ("POST", "/api/baja"),
}


def _rutas(app) -> set[tuple[str, str]]:
    """(método, ruta) de todas las rutas de la app, también las de los routers incluidos."""

    def recorrer(rutas):
        for ruta in rutas:
            if isinstance(ruta, APIRoute):
                yield from ((metodo, ruta.path) for metodo in ruta.methods)
            elif hasattr(ruta, "original_router"):  # así guarda FastAPI 0.141 los routers incluidos
                yield from recorrer(ruta.original_router.routes)

    return set(recorrer(app.routes))


def _llenar(ruta: str) -> str:
    return re.sub(r"\{[^}]+\}", "1", ruta)


@pytest.fixture
def app(settings_tmp):
    settings = settings_tmp.model_copy(update={"tareas_activas": False, "aprobacion_manual": True})
    app = crear_app()
    app.dependency_overrides[get_settings] = lambda: settings
    return app


@pytest.fixture
def entrar(app, settings_tmp, db_de):
    """Abre un cliente de la app completa con la sesión de un alumno en el estado pedido."""
    clientes = []

    def _entrar(email: str, estado: str) -> TestClient:
        con = db_de()
        alumno_id = dominio.crear_alumno(con, email, fuente=None, estado=estado)
        for tipo in ("mails_curso", "transferencia"):
            dominio.agregar_consentimiento(con, alumno_id, tipo, True, "prueba")
        con.close()
        cliente = TestClient(app, base_url="https://testserver")
        cliente.__enter__()
        clientes.append(cliente)
        cliente.cookies.set(auth.COOKIE, auth.emitir_token(settings_tmp, alumno_id))
        cliente.alumno_id = alumno_id
        return cliente

    yield _entrar
    for cliente in clientes:
        cliente.__exit__(None, None, None)


@pytest.fixture
def pendiente(entrar):
    return entrar(MAIL, "pendiente")


@pytest.fixture
def mails_enviados(monkeypatch):
    enviados = []

    async def falso(settings, alumno_id, tipo, clave, datos=None):
        enviados.append((alumno_id, tipo, clave))
        return "enviado"

    monkeypatch.setattr(mails, "enviar", falso)
    return enviados


def test_quien_espera_aprobacion_no_llega_a_ninguna_otra_ruta_del_alumno(app, pendiente):
    rutas = _rutas(app)
    assert PERMITIDAS | PUBLICAS <= rutas
    protegidas = sorted(r for r in rutas - PERMITIDAS - PUBLICAS if not r[1].startswith("/api/admin/"))
    # Sesiones y turnos del tutor, guías, módulos, idea, taller, kit, links y voz.
    assert len(protegidas) >= 17

    for metodo, ruta in protegidas:
        respuesta = pendiente.request(metodo, _llenar(ruta))
        assert (respuesta.status_code, respuesta.json()) == (403, PENDIENTE), (metodo, ruta)


def test_quien_espera_aprobacion_llega_a_lo_permitido_y_a_lo_publico(pendiente):
    for metodo, ruta in sorted(PERMITIDAS | PUBLICAS):
        respuesta = pendiente.request(metodo, ruta)
        assert respuesta.status_code != 403 or respuesta.json() != PENDIENTE, (metodo, ruta)


def test_quien_espera_aprobacion_no_entra_al_admin(app, pendiente):
    for metodo, ruta in sorted(r for r in _rutas(app) if r[1].startswith("/api/admin/")):
        assert pendiente.request(metodo, _llenar(ruta)).status_code == 403, (metodo, ruta)


def test_quien_espera_aprobacion_ve_su_estado_sus_datos_y_sus_permisos(pendiente):
    yo = pendiente.get("/api/yo")

    assert yo.status_code == 200
    assert yo.json()["estado"] == "pendiente"
    assert yo.json()["email"] == MAIL
    datos = pendiente.get("/api/mis-datos")
    assert datos.status_code == 200
    assert datos.json()["alumno"]["estado"] == "pendiente"
    cambio = pendiente.put("/api/consentimientos", json={"mails_curso": False})
    assert cambio.status_code == 200
    assert cambio.json()["mails_curso"] is False
    assert pendiente.get("/api/config").json()["aprobacion_manual"] is True
    assert pendiente.post("/api/auth/salir").status_code == 200


def test_quien_espera_aprobacion_puede_borrar_sus_datos(pendiente, db_de):
    respuesta = pendiente.request("DELETE", "/api/mis-datos", json={"confirmar": "BORRAR"})

    assert respuesta.status_code == 200
    con = db_de()
    assert dominio.alumno(con, pendiente.alumno_id) is None
    con.close()


def test_quien_administra_nunca_queda_pendiente(entrar):
    admin = entrar(ADMIN, "pendiente")

    assert admin.get("/api/yo").json()["estado"] == "aprobado"
    assert admin.get("/api/idea").status_code == 404
    assert admin.get("/api/admin/pedidos").status_code == 200


def test_al_aprobar_el_pedido_se_abre_el_curso(entrar, pendiente, mails_enviados):
    admin = entrar(ADMIN, "aprobado")
    assert pendiente.get("/api/idea").status_code == 403
    assert [p["email"] for p in admin.get("/api/admin/pedidos").json()] == [MAIL]

    assert admin.post(f"/api/admin/pedidos/{pendiente.alumno_id}/aprobar").json() == {"ok": True}

    assert pendiente.get("/api/yo").json()["estado"] == "aprobado"
    assert pendiente.get("/api/idea").status_code == 404
    assert pendiente.get("/api/modulos/1/guia").status_code != 403
    assert mails_enviados == [(pendiente.alumno_id, "bienvenida", "bienvenida")]


def test_al_rechazar_el_pedido_se_pierde_la_sesion(entrar, pendiente):
    admin = entrar(ADMIN, "aprobado")

    assert admin.delete(f"/api/admin/pedidos/{pendiente.alumno_id}").status_code == 200

    assert pendiente.get("/api/yo").status_code == 401
    assert admin.get("/api/admin/pedidos").json() == []
