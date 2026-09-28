from pathlib import Path

import pytest

from vibe_tutor import db
from vibe_tutor.config import Settings


@pytest.fixture
def settings_tmp(tmp_path, monkeypatch) -> Settings:
    for campo in Settings.model_fields:
        monkeypatch.delenv(campo.upper(), raising=False)
    datos = tmp_path / "data"
    datos.mkdir()
    return Settings(
        _env_file=None,
        anthropic_api_key="sk-ant-prueba",
        gemini_api_key="gemini-prueba",
        resend_api_key="re_prueba",
        mail_from="Vibe Tutor <tutor@example.com>",
        turnstile_site_key="1x00000000000000000000AA",
        turnstile_secret="1x0000000000000000000000000000000AA",
        jwt_secret="clave-de-prueba-" * 4,
        admin_email="admin@example.com",
        dominio="localhost",
        data_dir=datos,
        contenido_dir=tmp_path / "contenido",
    )


@pytest.fixture
def con():
    conexion = db.conectar(Path(":memory:"))
    db.migrar(conexion)
    yield conexion
    conexion.close()


@pytest.fixture
def db_de(settings_tmp):
    """Abre la base del settings de prueba (con migraciones)."""

    def abrir():
        conexion = db.conectar(settings_tmp.data_dir / db.ARCHIVO)
        db.migrar(conexion)
        return conexion

    return abrir


@pytest.fixture
def hacer_cliente(settings_tmp, db_de):
    """Arma un TestClient con los routers pedidos y, si se pasa un mail, con la sesión de ese alumno.

    Uso: cliente = hacer_cliente([alumnos.router], email="ana@example.com")
    Cada test arma su propia app con sus routers, así no depende de módulos ajenos.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from vibe_tutor import auth, dominio, errores
    from vibe_tutor.config import get_settings

    abiertos = []

    def _hacer(routers, email: str | None = None, settings=None):
        app = FastAPI()
        errores.instalar(app)
        auth.instalar_csrf(app)
        for router in routers:
            app.include_router(router)
        app.dependency_overrides[get_settings] = lambda: settings or settings_tmp
        cliente = TestClient(app, base_url="https://testserver")
        cliente.__enter__()
        abiertos.append(cliente)
        if email:
            con = db_de()
            fila = dominio.alumno_por_email(con, email)
            alumno_id = fila["id"] if fila else dominio.crear_alumno(con, email, fuente=None)
            for tipo in ("mails_curso", "transferencia"):
                dominio.agregar_consentimiento(con, alumno_id, tipo, True, "prueba")
            con.close()
            cliente.cookies.set(auth.COOKIE, auth.emitir_token(settings or settings_tmp, alumno_id))
            cliente.alumno_id = alumno_id
        return cliente

    yield _hacer
    for cliente in abiertos:
        cliente.__exit__(None, None, None)
