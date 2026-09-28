from pathlib import Path

import pytest
from pydantic import ValidationError

from vibe_tutor.config import RUTA_ENV, Settings, get_settings

OBLIGATORIAS = {
    "mail_from": "Curso <hola@example.com>",
    "jwt_secret": "j" * 64,
    "admin_email": "admin@example.com",
    "dominio": "curso.example.com",
}
# Obligatorias salvo con MODO_DEMO=true: en el modo demo no se llama a Claude, Gemini ni Resend.
CLAVES_API = {
    "anthropic_api_key": "sk-ant-x",
    "gemini_api_key": "gm-x",
    "resend_api_key": "re-x",
}
COMPLETAS = {**OBLIGATORIAS, **CLAVES_API}
SECRETAS = ("anthropic_api_key", "gemini_api_key", "resend_api_key", "turnstile_secret", "jwt_secret")
ENV_EXAMPLE = Path(__file__).resolve().parents[2] / "deploy" / ".env.example"


@pytest.fixture
def entorno_limpio(monkeypatch):
    for campo in Settings.model_fields:
        monkeypatch.delenv(campo.upper(), raising=False)
    monkeypatch.delenv("VIBE_ENV_FILE", raising=False)
    get_settings.cache_clear()
    yield monkeypatch
    get_settings.cache_clear()


def test_lee_el_archivo_de_entorno_del_curso(tmp_path, entorno_limpio):
    archivo = tmp_path / ".env"
    lineas = [f"{clave.upper()}={valor}" for clave, valor in COMPLETAS.items()]
    lineas += ["TOPE_MENSUAL_USD=30", "DEV_CODIGO_FIJO=", "OTRA_CLAVE=se-ignora", "TURNSTILE_SITE_KEY=sitio-x"]
    archivo.write_text("\n".join(lineas), encoding="utf-8")
    entorno_limpio.setenv("VIBE_ENV_FILE", str(archivo))

    settings = get_settings()

    assert settings is get_settings()
    assert settings.mail_from == "Curso <hola@example.com>"
    assert settings.admin_email == "admin@example.com"
    assert settings.dominio == "curso.example.com"
    assert settings.tope_mensual_usd == 30.0
    assert settings.dev_codigo_fijo is None
    assert settings.turnstile_site_key == "sitio-x"


def test_valores_por_defecto(entorno_limpio):
    settings = Settings(_env_file=None, **COMPLETAS)

    assert RUTA_ENV == "/etc/vibe-tutor/.env"
    assert settings.modelo == "claude-sonnet-5"
    assert settings.tope_alumno_usd == 1.0
    assert settings.tope_mensual_usd == 50.0
    assert settings.data_dir == Path("/srv/vibe-tutor/data")
    assert settings.contenido_dir == Path("/srv/vibe-tutor/contenido")
    assert settings.turnstile_site_key == ""
    assert settings.turnstile_secret == ""
    assert settings.max_codigos_mail_hora == 5
    assert settings.max_codigos_ip_hora == 20
    assert settings.max_codigos_dia == 80
    assert settings.aviso_prueba is True
    assert settings.tareas_activas is True
    assert settings.autor_nombre == ""
    assert settings.newsletter_nombre == ""
    assert settings.modo_demo is False
    assert settings.aprobacion_manual is False


def test_exige_las_claves_obligatorias(entorno_limpio):
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)
    faltantes = {e["loc"][0] for e in error.value.errors() if e["type"] == "missing"}
    assert faltantes == set(OBLIGATORIAS)


@pytest.mark.parametrize("clave", sorted(CLAVES_API))
def test_sin_modo_demo_exige_las_claves_de_api(entorno_limpio, clave):
    for valor in (None, "", "   "):
        datos = {**COMPLETAS}
        if valor is None:
            del datos[clave]
        else:
            datos[clave] = valor
        with pytest.raises(ValidationError) as error:
            Settings(_env_file=None, **datos)
        assert clave.upper() in str(error.value)
        assert "MODO_DEMO" in str(error.value)


def test_sin_modo_demo_nombra_todas_las_claves_que_faltan(entorno_limpio):
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, **OBLIGATORIAS)
    for clave in CLAVES_API:
        assert clave.upper() in str(error.value)


def test_con_modo_demo_no_hacen_falta_las_claves_de_api(entorno_limpio):
    settings = Settings(_env_file=None, **OBLIGATORIAS, modo_demo=True)

    assert settings.modo_demo is True
    assert settings.anthropic_api_key == settings.gemini_api_key == settings.resend_api_key == ""


def test_con_modo_demo_igual_exige_lo_demas(entorno_limpio):
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, modo_demo=True)
    faltantes = {e["loc"][0] for e in error.value.errors() if e["type"] == "missing"}
    assert faltantes == set(OBLIGATORIAS)


def test_modo_demo_autor_y_newsletter_desde_el_archivo(tmp_path, entorno_limpio):
    archivo = tmp_path / ".env"
    lineas = [f"{clave.upper()}={valor}" for clave, valor in OBLIGATORIAS.items()]
    lineas += [
        "MODO_DEMO=true", "AUTOR_NOMBRE=  Ana Pérez ", "NEWSLETTER_NOMBRE=El boletín de Ana", "APROBACION_MANUAL=true"
    ]
    archivo.write_text("\n".join(lineas), encoding="utf-8")
    entorno_limpio.setenv("VIBE_ENV_FILE", str(archivo))

    settings = get_settings()

    assert settings.modo_demo is True
    assert settings.autor_nombre == "Ana Pérez"
    assert settings.newsletter_nombre == "El boletín de Ana"
    assert settings.aprobacion_manual is True
    assert settings.anthropic_api_key == ""


def test_rechaza_jwt_corto(entorno_limpio):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{**COMPLETAS, "jwt_secret": "corta"})


def test_no_expone_secretos(entorno_limpio):
    secretos = {campo: f"{campo}-valor-secreto-" * 3 for campo in SECRETAS}
    settings = Settings(_env_file=None, **{**COMPLETAS, **secretos, "dev_codigo_fijo": "918273"})

    texto = repr(settings) + str(settings)
    for valor in [*secretos.values(), "918273"]:
        assert valor not in texto

    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, **{**COMPLETAS, "jwt_secret": "jwt-casi-secreto"})
    assert "jwt-casi-secreto" not in str(error.value)


def test_env_example_lista_exactamente_las_variables(entorno_limpio):
    claves = {
        linea.split("=", 1)[0].strip()
        for linea in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
        if "=" in linea and not linea.lstrip().startswith("#")
    }
    valores = [
        linea.split("=", 1)[1].strip()
        for linea in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
        if "=" in linea and not linea.lstrip().startswith("#")
    ]

    # Los ajustes pueden faltar en el ejemplo (tienen un valor por defecto razonable); el resto tiene
    # que estar, y no puede aparecer nada que Settings no conozca. AUTOR_NOMBRE, NEWSLETTER_NOMBRE y
    # MODO_DEMO los suma al ejemplo quien mantiene deploy/: acá se aceptan estén o no.
    ajustes = {
        "MODELO", "TTS_MODELO", "TTS_MODELO_RESPALDO", "TTS_VOZ", "MAX_CODIGOS_MAIL_HORA", "MAX_CODIGOS_IP_HORA",
        "MAX_CODIGOS_DIA", "AVISO_PRUEBA", "TAREAS_ACTIVAS", "AUTOR_NOMBRE", "NEWSLETTER_NOMBRE", "MODO_DEMO",
    }
    campos = {campo.upper() for campo in Settings.model_fields}
    assert campos - ajustes <= claves
    assert claves <= campos, f"variables que Settings no conoce: {claves - campos}"
    assert all(valor == "" for valor in valores)


def test_variables_vacias_toman_el_valor_por_defecto(tmp_path, entorno_limpio):
    archivo = tmp_path / ".env"
    lineas = [f"{clave.upper()}={valor}" for clave, valor in OBLIGATORIAS.items()]
    lineas += ["TOPE_ALUMNO_USD=", "TOPE_MENSUAL_USD=", "AVISO_PRUEBA=", "MAX_CODIGOS_DIA=", "APROBACION_MANUAL="]
    archivo.write_text("\n".join(lineas), encoding="utf-8")

    settings = Settings(_env_file=archivo, **{k: v for k, v in CLAVES_API.items()})

    assert settings.tope_alumno_usd == 1.0
    assert settings.tope_mensual_usd == 50.0
    assert settings.aviso_prueba is True
    assert settings.max_codigos_dia == 80
    assert settings.aprobacion_manual is False
