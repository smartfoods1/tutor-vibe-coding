"""La app completa: /api/config, lo que el frontend necesita saber antes de que haya sesión."""

import pytest
from fastapi.testclient import TestClient

from vibe_tutor.config import get_settings
from vibe_tutor.main import crear_app


@pytest.fixture
def pedir_config(settings_tmp):
    def _pedir(**cambios) -> dict:
        settings = settings_tmp.model_copy(update={"tareas_activas": False, **cambios})
        app = crear_app()
        app.dependency_overrides[get_settings] = lambda: settings
        with TestClient(app, base_url="https://testserver") as cliente:
            respuesta = cliente.get("/api/config")
        assert respuesta.status_code == 200
        return respuesta.json()

    return _pedir


def test_config_por_defecto(pedir_config):
    assert pedir_config() == {
        "turnstile_site_key": "1x00000000000000000000AA",
        "aviso_prueba": True,
        "autor_nombre": None,
        "newsletter": None,
        "modo_demo": False,
        "aprobacion_manual": False,
        "siguiente_paso": None,
    }


def test_config_con_aprobacion_manual(pedir_config):
    assert pedir_config(aprobacion_manual=True)["aprobacion_manual"] is True


SIGUIENTE_PASO = {
    "siguiente_paso_nombre": "el curso de prueba",
    "siguiente_paso_pregunta": "¿Tenés un negocio que ya vende?",
    "siguiente_paso_texto": "En marzo abre un curso para construir el sistema que lo gestiona.",
}


def test_config_con_el_siguiente_paso_activo_trae_sus_tres_textos(pedir_config):
    datos = pedir_config(siguiente_paso=True, **SIGUIENTE_PASO)

    assert datos["siguiente_paso"] == {
        "nombre": "el curso de prueba",
        "pregunta": "¿Tenés un negocio que ya vende?",
        "texto": "En marzo abre un curso para construir el sistema que lo gestiona.",
    }


@pytest.mark.parametrize(
    "cambios",
    [
        {**SIGUIENTE_PASO},
        {"siguiente_paso": True, **SIGUIENTE_PASO, "siguiente_paso_texto": ""},
        {"siguiente_paso": True, **SIGUIENTE_PASO, "siguiente_paso_nombre": "   "},
        {"siguiente_paso": True},
    ],
    ids=["sin-la-bandera", "sin-texto", "nombre-en-blanco", "sin-textos"],
)
def test_config_con_el_siguiente_paso_inactivo_lo_da_como_null(pedir_config, cambios):
    assert pedir_config(**cambios)["siguiente_paso"] is None


def test_config_con_autor_newsletter_y_modo_demo(pedir_config):
    datos = pedir_config(autor_nombre="Ana", newsletter_nombre="El boletín de Ana", modo_demo=True)

    assert datos["autor_nombre"] == "Ana"
    assert datos["newsletter"] == "El boletín de Ana"
    assert datos["modo_demo"] is True


def test_config_con_textos_en_blanco_los_da_como_null(pedir_config):
    datos = pedir_config(autor_nombre="   ", newsletter_nombre=" ", turnstile_site_key="")

    assert datos["autor_nombre"] is None
    assert datos["newsletter"] is None
    assert datos["turnstile_site_key"] is None


def test_config_no_expone_claves(pedir_config):
    texto = str(pedir_config())

    for secreto in ("sk-ant-prueba", "gemini-prueba", "re_prueba", "clave-de-prueba"):
        assert secreto not in texto
