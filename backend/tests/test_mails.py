import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
import respx

from vibe_tutor import contenido, costos, dominio, mails

RESEND = "https://api.resend.com/emails"
T0 = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
MAIL = "ana@example.com"
BASE = "https://localhost"
REPO_CONTENIDO = Path(__file__).resolve().parents[2] / "contenido"

PLANTILLAS = {
    "bienvenida": (
        "---\nasunto: Ya estás adentro del curso\nestado: borrador\n---\n"
        "Hola.\n\nEntrá cuando quieras: {{ENLACE_CURSO}}\nTe esperamos.\n"
    ),
    "recordatorio": (
        "---\nasunto: Tu idea está lista\n---\nEl paso que sigue es armar tu taller: {{ENLACE_MODULO_3}}.\n"
    ),
    "contame": (
        "---\nasunto: Contame qué hiciste\n# {{TITULO_LINK}} puede venir vacío\n---\n"
        "Registraste tu página:\n\n{{TITULO_LINK}}\n{{LINK_ALUMNO}}\n\nContame qué hiciste y cómo te fue.\n"
    ),
    "aviso_80": (
        "---\nasunto: El tutor ya gastó US$ {{GASTO_MES}}\n---\n"
        "Gasto del mes: US$ {{GASTO_MES}} de US$ {{TOPE_MES}}.\n\n"
        "Alumnos activos este mes: {{ALUMNOS_ACTIVOS}}.\n\nReporte: {{ENLACE_REPORTE}}\n"
    ),
    "pedidos": (
        "---\nasunto: Pedidos de acceso para aprobar ({{PENDIENTES}})\n---\n"
        "Pedidos esperando: {{PENDIENTES}}.\n\nAprobalos desde {{ENLACE_ADMIN}}\n"
    ),
}
PIE = (
    "---\nestado: borrador\n---\nPara no recibir más mails del curso: {{ENLACE_BAJA}}\n\n"
    "Art. 27 inc. 3 de la Ley 25.326.\n\n<!--\nNota interna: no sale en los mails. {{NO_SALE}}\n-->\n"
)


@pytest.fixture
def raiz(settings_tmp):
    raiz = settings_tmp.contenido_dir
    (raiz / "mails").mkdir(parents=True)
    (raiz / "legal").mkdir()
    for tipo, texto in PLANTILLAS.items():
        (raiz / "mails" / f"{tipo}.md").write_text(texto, encoding="utf-8")
    (raiz / "legal" / "pie-mails.md").write_text(PIE, encoding="utf-8")
    (raiz / "legal" / "consentimientos.md").write_text("---\nversion: 2026-10-01\n---\nTexto.\n", encoding="utf-8")
    return raiz


@pytest.fixture
def reloj(monkeypatch):
    estado = {"ahora": T0}
    monkeypatch.setattr(mails, "ahora", lambda: estado["ahora"])
    return estado


@pytest.fixture
def resend():
    with respx.mock(assert_all_called=False) as mock:
        yield mock.post(RESEND).mock(return_value=httpx.Response(200, json={"id": "mail-1"}))


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


def _alumno(con, email=MAIL, estado="aprobado") -> int:
    alumno_id = dominio.crear_alumno(con, email, fuente=None, estado=estado)
    for tipo in ("mails_curso", "transferencia"):
        dominio.agregar_consentimiento(con, alumno_id, tipo, True, "prueba")
    return alumno_id


@pytest.fixture
def alumno(base) -> int:
    return _alumno(base)


def _link(con, alumno_id, url="https://mi-idea.netlify.app", titulo="Mi registro de sueños") -> int:
    with con:
        cursor = con.execute("INSERT INTO links (alumno_id, url, titulo) VALUES (?, ?, ?)", (alumno_id, url, titulo))
    return int(cursor.lastrowid)


def _mails(con) -> list[dict]:
    return [dict(f) for f in con.execute("SELECT alumno_id, tipo, clave, estado, creado FROM mails ORDER BY id")]


def _pedido(ruta) -> tuple[httpx.Request, dict]:
    pedido = ruta.calls.last.request
    return pedido, json.loads(pedido.content)


# --- envío ---------------------------------------------------------------------------------------


async def test_bienvenida_por_resend_con_baja_en_un_clic(settings_tmp, raiz, reloj, resend, base, alumno):
    estado = await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida")

    assert estado == "enviado"
    pedido, cuerpo = _pedido(resend)
    assert pedido.headers["authorization"] == "Bearer re_prueba"
    assert cuerpo["from"] == settings_tmp.mail_from
    assert cuerpo["to"] == [MAIL]
    assert cuerpo["subject"] == "Ya estás adentro del curso"
    token = mails.token_baja(settings_tmp, alumno)
    assert f"Entrá cuando quieras: {BASE}/\nTe esperamos." in cuerpo["text"]
    assert f"Para no recibir más mails del curso: {BASE}/baja?t={token}" in cuerpo["text"]
    assert "Art. 27 inc. 3" in cuerpo["text"]
    assert "{{" not in cuerpo["text"] and "estado: borrador" not in cuerpo["text"]
    assert "Nota interna" not in cuerpo["text"] and "Nota interna" not in cuerpo["html"]
    assert cuerpo["text"].endswith("Art. 27 inc. 3 de la Ley 25.326.\n")
    assert f'<a href="{BASE}/">{BASE}/</a>' in cuerpo["html"]
    assert f'<a href="{BASE}/baja?t={token}">' in cuerpo["html"]
    assert "<p>Hola.</p>" in cuerpo["html"]
    assert cuerpo["headers"] == {
        "List-Unsubscribe": f"<{BASE}/api/baja?t={token}>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    }
    assert _mails(base) == [
        {"alumno_id": alumno, "tipo": "bienvenida", "clave": "bienvenida", "estado": "enviado",
         "creado": "2026-09-28T15:00:00+00:00"}
    ]


async def test_recordatorio_lleva_al_modulo_3(settings_tmp, raiz, reloj, resend, base, alumno):
    assert await mails.enviar(settings_tmp, alumno, "recordatorio", "recordatorio") == "enviado"

    _, cuerpo = _pedido(resend)
    assert f"armar tu taller: {BASE}/modulo/3." in cuerpo["text"]
    assert f'<a href="{BASE}/modulo/3">{BASE}/modulo/3</a>.' in cuerpo["html"]
    assert "List-Unsubscribe" in cuerpo["headers"]


async def test_no_repite_una_clave_ya_enviada(settings_tmp, raiz, reloj, resend, base, alumno):
    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "enviado"
    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "omitido"

    assert resend.call_count == 1
    assert len(_mails(base)) == 1


async def test_respeta_la_baja(settings_tmp, raiz, reloj, resend, base, alumno):
    dominio.agregar_consentimiento(base, alumno, "mails_curso", False, "prueba")

    for tipo in ("bienvenida", "recordatorio"):
        assert await mails.enviar(settings_tmp, alumno, tipo, tipo) == "omitido"

    assert resend.call_count == 0
    assert _mails(base) == []


async def test_autor_y_newsletter_en_el_asunto_el_cuerpo_y_el_pie(settings_tmp, raiz, reloj, resend, base, alumno):
    (raiz / "mails" / "bienvenida.md").write_text(
        "---\nasunto: Te da la bienvenida {{AUTOR}}\n---\nHola, soy {{AUTOR}}. Novedades en {{NEWSLETTER}}.\n"
        "Entrá: {{ENLACE_CURSO}}\n",
        encoding="utf-8",
    )
    (raiz / "legal" / "pie-mails.md").write_text("Baja: {{ENLACE_BAJA}}\n\nResponsable: {{AUTOR}}.\n", encoding="utf-8")
    settings = settings_tmp.model_copy(update={"autor_nombre": "Ana", "newsletter_nombre": "El boletín de Ana"})

    assert await mails.enviar(settings, alumno, "bienvenida", "bienvenida") == "enviado"

    _, cuerpo = _pedido(resend)
    assert cuerpo["subject"] == "Te da la bienvenida Ana"
    assert "Hola, soy Ana. Novedades en El boletín de Ana." in cuerpo["text"]
    assert "Responsable: Ana." in cuerpo["text"]
    assert "{{" not in cuerpo["text"] + cuerpo["html"]


async def test_sin_autor_el_mail_dice_el_autor_del_curso(settings_tmp, raiz, reloj, resend, base, alumno):
    (raiz / "mails" / "bienvenida.md").write_text(
        "---\nasunto: Bienvenida\n---\nTe escribe {{AUTOR}}.{{NEWSLETTER}}\n", encoding="utf-8"
    )

    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "enviado"

    assert "Te escribe el autor del curso." in _pedido(resend)[1]["text"]


async def test_en_modo_demo_los_mails_se_loguean_y_no_se_mandan(settings_tmp, raiz, reloj, resend, base, alumno, caplog):
    demo = settings_tmp.model_copy(update={"modo_demo": True, "resend_api_key": ""})
    caplog.set_level(logging.DEBUG)

    estado = await mails.enviar(demo, alumno, "bienvenida", "bienvenida")

    assert estado == "enviado"
    assert resend.call_count == 0
    registros = " ".join(r.getMessage() for r in caplog.records)
    assert "Ya estás adentro del curso" in registros
    assert MAIL in registros
    assert "baja?t=" not in registros
    assert _mails(base)[0]["estado"] == "enviado"


async def test_alumno_inexistente_se_omite(settings_tmp, raiz, reloj, resend, base):
    assert await mails.enviar(settings_tmp, 999, "bienvenida", "bienvenida") == "omitido"
    assert resend.call_count == 0


async def test_aviso_80_va_a_quien_administra_sin_baja(settings_tmp, raiz, reloj, resend, base, alumno):
    dominio.agregar_consentimiento(base, alumno, "mails_curso", False, "prueba")
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 41.5, alumno_id=alumno)
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 9.0)
    otro = _alumno(base, "beto@example.com")
    with base:
        base.execute("UPDATE uso SET creado = '2026-08-20T12:00:00+00:00' WHERE costo_usd = 9.0")
        base.execute("UPDATE alumnos SET ultima_actividad = '2026-09-10T12:00:00+00:00' WHERE id = ?", (alumno,))
        base.execute("UPDATE alumnos SET ultima_actividad = '2026-08-31T12:00:00+00:00' WHERE id = ?", (otro,))
        base.execute("UPDATE uso SET creado = '2026-09-10T12:00:00+00:00' WHERE costo_usd = 41.5")

    estado = await mails.enviar(settings_tmp, None, "aviso_80", "aviso_80:2026-09")

    assert estado == "enviado"
    _, cuerpo = _pedido(resend)
    assert cuerpo["to"] == [settings_tmp.admin_email]
    assert cuerpo["subject"] == "El tutor ya gastó US$ 41,50"
    assert "Gasto del mes: US$ 41,50 de US$ 50,00." in cuerpo["text"]
    assert "Alumnos activos este mes: 1." in cuerpo["text"]
    assert f"Reporte: {BASE}/admin" in cuerpo["text"]
    assert "baja" not in cuerpo["text"]
    assert "headers" not in cuerpo
    assert _mails(base)[0] | {"creado": None} == {
        "alumno_id": None, "tipo": "aviso_80", "clave": "aviso_80:2026-09", "estado": "enviado", "creado": None
    }
    assert await mails.enviar(settings_tmp, None, "aviso_80", "aviso_80:2026-09") == "omitido"
    assert resend.call_count == 1


async def test_aviso_80_cuenta_como_activos_solo_a_los_aprobados(settings_tmp, raiz, reloj, resend, base, alumno):
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 41.0, alumno_id=alumno)
    _alumno(base, "pendiente@example.com", estado="pendiente")

    assert await mails.enviar(settings_tmp, None, "aviso_80", "aviso_80:2026-09") == "enviado"

    assert "Alumnos activos este mes: 1." in _pedido(resend)[1]["text"]


# --- pedidos de acceso (APROBACION_MANUAL) ------------------------------------------------------------


def test_clave_de_pedidos_por_hora_de_argentina():
    assert mails.clave_pedidos(datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)) == "pedidos:2026-09-28T12"
    assert mails.clave_pedidos(datetime(2026, 9, 28, 15, 59, tzinfo=timezone.utc)) == "pedidos:2026-09-28T12"
    assert mails.clave_pedidos(datetime(2026, 9, 29, 2, 30, tzinfo=timezone.utc)) == "pedidos:2026-09-28T23"


async def test_pedidos_va_a_quien_administra_sin_baja(settings_tmp, raiz, reloj, resend, base, alumno):
    estado = await mails.enviar(settings_tmp, None, "pedidos", "pedidos:2026-09-28T12", {"pendientes": 3})

    assert estado == "enviado"
    _, cuerpo = _pedido(resend)
    assert cuerpo["to"] == [settings_tmp.admin_email]
    assert cuerpo["subject"] == "Pedidos de acceso para aprobar (3)"
    assert "Pedidos esperando: 3." in cuerpo["text"]
    assert f"Aprobalos desde {BASE}/admin" in cuerpo["text"]
    assert "baja" not in cuerpo["text"] and "Art. 27" not in cuerpo["text"]
    assert "headers" not in cuerpo
    assert _mails(base) == [
        {"alumno_id": None, "tipo": "pedidos", "clave": "pedidos:2026-09-28T12", "estado": "enviado",
         "creado": "2026-09-28T15:00:00+00:00"}
    ]
    assert await mails.enviar(settings_tmp, None, "pedidos", "pedidos:2026-09-28T12", {"pendientes": 4}) == "omitido"
    assert await mails.enviar(settings_tmp, None, "pedidos", "pedidos:2026-09-28T13", {"pendientes": 4}) == "enviado"
    assert resend.call_count == 2


async def test_pedidos_sin_datos_cuenta_los_pendientes_de_la_base(settings_tmp, raiz, reloj, resend, base, alumno):
    for numero in range(2):
        _alumno(base, f"pendiente{numero}@example.com", estado="pendiente")

    assert await mails.enviar(settings_tmp, alumno, "pedidos", "pedidos:2026-09-28T12") == "enviado"

    _, cuerpo = _pedido(resend)
    assert cuerpo["to"] == [settings_tmp.admin_email]
    assert "Pedidos esperando: 2." in cuerpo["text"]
    assert _mails(base)[0]["alumno_id"] is None


async def test_los_mails_del_curso_no_van_a_quien_espera_aprobacion(settings_tmp, raiz, reloj, resend, base):
    pendiente = _alumno(base, estado="pendiente")
    _link(base, pendiente)

    for tipo in ("bienvenida", "recordatorio", "contame"):
        assert await mails.enviar(settings_tmp, pendiente, tipo, tipo) == "omitido"

    assert resend.call_count == 0
    assert _mails(base) == []


async def test_falla_de_resend_queda_fallido_sin_loguear_la_clave(settings_tmp, raiz, reloj, base, alumno, caplog):
    caplog.set_level(logging.DEBUG)
    with respx.mock() as mock:
        mock.post(RESEND).mock(return_value=httpx.Response(500, json={"name": "internal_server_error"}))
        assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"
    with respx.mock() as mock:
        mock.post(RESEND).mock(side_effect=httpx.ConnectError("sin red"))
        assert await mails.enviar(settings_tmp, alumno, "recordatorio", "recordatorio") == "fallido"

    assert [(m["clave"], m["estado"]) for m in _mails(base)] == [("bienvenida", "fallido"), ("recordatorio", "fallido")]
    assert "re_prueba" not in caplog.text
    assert MAIL not in caplog.text


async def test_reintento_actualiza_la_fila_fallida(settings_tmp, raiz, reloj, base, alumno):
    with respx.mock() as mock:
        mock.post(RESEND).mock(return_value=httpx.Response(503))
        assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"
    reloj["ahora"] = T0 + timedelta(hours=2)
    with respx.mock() as mock:
        ruta = mock.post(RESEND).mock(return_value=httpx.Response(200, json={"id": "mail-2"}))
        assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "enviado"
        assert ruta.call_count == 1

    assert _mails(base) == [
        {"alumno_id": alumno, "tipo": "bienvenida", "clave": "bienvenida", "estado": "enviado",
         "creado": "2026-09-28T15:00:00+00:00"}
    ]


async def test_sin_plantilla_queda_fallido(settings_tmp, raiz, reloj, resend, base, alumno, caplog):
    (raiz / "mails" / "bienvenida.md").unlink()

    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"

    assert resend.call_count == 0
    assert _mails(base)[0]["estado"] == "fallido"
    assert "bienvenida" in caplog.text


async def test_sin_pie_legal_no_manda_mails_con_baja(settings_tmp, raiz, reloj, resend, base, alumno):
    (raiz / "legal" / "pie-mails.md").unlink()

    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"
    assert resend.call_count == 0


@pytest.mark.parametrize(
    "plantilla",
    ["---\nestado: borrador\n---\nSin asunto.\n", "---\nasunto: Hola\n---\nHola {{NOMBRE_DESCONOCIDO}}.\n"],
)
async def test_plantilla_incompleta_queda_fallido(settings_tmp, raiz, reloj, resend, base, alumno, plantilla):
    (raiz / "mails" / "bienvenida.md").write_text(plantilla, encoding="utf-8")

    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"
    assert resend.call_count == 0


async def test_nunca_levanta_excepciones(settings_tmp, raiz, reloj, resend, base, alumno, monkeypatch):
    assert await mails.enviar(settings_tmp, alumno, "otro", "otro") == "fallido"

    def rota(*args, **kwargs):
        raise RuntimeError("base rota")

    monkeypatch.setattr(mails.db, "conectar", rota)
    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "fallido"
    assert resend.call_count == 0


async def test_html_escapa_el_texto_y_hace_clicables_los_links(settings_tmp, raiz, reloj, resend, base, alumno):
    (raiz / "mails" / "bienvenida.md").write_text(
        "---\nasunto: Hola <b>\n---\nUsá <b>esto</b> & aquello.\nMirá https://ejemplo.com/a?b=1&c=2.\n\nChau.\n",
        encoding="utf-8",
    )

    assert await mails.enviar(settings_tmp, alumno, "bienvenida", "bienvenida") == "enviado"

    _, cuerpo = _pedido(resend)
    assert "<b>esto</b>" not in cuerpo["html"]
    assert "Usá &lt;b&gt;esto&lt;/b&gt; &amp; aquello.<br>" in cuerpo["html"]
    assert '<a href="https://ejemplo.com/a?b=1&amp;c=2">https://ejemplo.com/a?b=1&amp;c=2</a>.</p>' in cuerpo["html"]
    assert "<p>Chau.</p>" in cuerpo["html"]
    assert cuerpo["subject"] == "Hola <b>"


# --- contame ---------------------------------------------------------------------------------------


async def test_contame_con_los_datos_del_link(settings_tmp, raiz, reloj, resend, base, alumno):
    _link(base, alumno)

    estado = await mails.enviar(
        settings_tmp, alumno, "contame", mails.CLAVE_CONTAME,
        {"link": "https://mi-idea.netlify.app", "titulo": "Mi registro de sueños"},
    )

    assert mails.CLAVE_CONTAME == "contame"
    assert estado == "enviado"
    _, cuerpo = _pedido(resend)
    assert "Registraste tu página:\n\nMi registro de sueños\nhttps://mi-idea.netlify.app\n\nContame" in cuerpo["text"]
    assert "Para no recibir más mails del curso" in cuerpo["text"]
    assert "List-Unsubscribe" in cuerpo["headers"]
    assert [(m["tipo"], m["clave"], m["estado"]) for m in _mails(base)] == [("contame", "contame", "enviado")]


async def test_contame_toma_el_ultimo_link_de_la_base_si_no_vienen_datos(settings_tmp, raiz, reloj, resend, base, alumno):
    _link(base, alumno, url="https://vieja.netlify.app", titulo="Vieja")
    _link(base, alumno, url="https://ana.claude.site", titulo=None)

    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "enviado"

    _, cuerpo = _pedido(resend)
    assert "Registraste tu página:\n\nhttps://ana.claude.site\n\nContame" in cuerpo["text"]
    assert '<p>Registraste tu página:</p>\n<p><a href="https://ana.claude.site">' in cuerpo["html"]
    assert "vieja" not in cuerpo["text"]


async def test_contame_sin_links_propios_no_sale(settings_tmp, raiz, reloj, resend, base, alumno):
    _link(base, _alumno(base, "beto@example.com"))

    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "omitido"
    assert resend.call_count == 0
    assert _mails(base) == []


async def test_contame_sale_una_sola_vez_en_la_vida(settings_tmp, raiz, reloj, resend, base, alumno):
    primero = _link(base, alumno)

    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "enviado"
    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "omitido"
    reloj["ahora"] = T0 + timedelta(days=40)
    _link(base, alumno, url="https://otra.netlify.app")
    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "omitido"
    assert await mails.enviar(settings_tmp, alumno, "contame", f"contame:{primero}") == "omitido"

    assert resend.call_count == 1
    assert [m["clave"] for m in _mails(base)] == ["contame"]


async def test_contame_con_la_clave_vieja_cuenta_como_ya_mandado(settings_tmp, raiz, reloj, resend, base, alumno):
    link_id = _link(base, alumno)
    with base:
        base.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'contame', ?, 'enviado')",
            (alumno, f"contame:{link_id}"),
        )

    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "omitido"
    assert resend.call_count == 0


async def test_contame_fallido_se_reintenta_con_el_link_de_la_base(settings_tmp, raiz, reloj, base, alumno):
    _link(base, alumno, url="https://mi-idea.netlify.app", titulo="Mi registro")
    with respx.mock() as mock:
        mock.post(RESEND).mock(return_value=httpx.Response(500))
        estado = await mails.enviar(
            settings_tmp, alumno, "contame", "contame", {"link": "https://mi-idea.netlify.app", "titulo": "Mi registro"}
        )
        assert estado == "fallido"
    reloj["ahora"] = T0 + timedelta(minutes=15)
    with respx.mock() as mock:
        ruta = mock.post(RESEND).mock(return_value=httpx.Response(200, json={"id": "mail-2"}))
        assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "enviado"

    assert "Mi registro\nhttps://mi-idea.netlify.app" in json.loads(ruta.calls.last.request.content)["text"]
    assert [(m["clave"], m["estado"]) for m in _mails(base)] == [("contame", "enviado")]


def test_contame_pendiente_dice_si_el_mail_va_a_salir(base, alumno):
    assert mails.contame_pendiente(base, alumno) is True

    with base:
        base.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'contame', 'contame', 'fallido')", (alumno,)
        )
    assert mails.contame_pendiente(base, alumno) is True

    with base:
        base.execute("UPDATE mails SET estado = 'enviado'")
    assert mails.contame_pendiente(base, alumno) is False

    otro = _alumno(base, "beto@example.com")
    dominio.agregar_consentimiento(base, otro, "mails_curso", False, "prueba")
    assert mails.contame_pendiente(base, otro) is False


async def test_contame_respeta_la_baja(settings_tmp, raiz, reloj, resend, base, alumno):
    _link(base, alumno)
    dominio.agregar_consentimiento(base, alumno, "mails_curso", False, "prueba")

    assert await mails.enviar(settings_tmp, alumno, "contame", "contame") == "omitido"
    assert resend.call_count == 0


# --- token de baja ---------------------------------------------------------------------------------


def test_token_de_baja_va_y_vuelve(settings_tmp):
    token = mails.token_baja(settings_tmp, 42)

    assert mails.leer_token_baja(settings_tmp, token) == 42
    assert re.fullmatch(r"[A-Za-z0-9._-]+", token)
    assert settings_tmp.jwt_secret not in token


@pytest.mark.parametrize("token", ["", "42", "42.", "abc.def", "42.xyz", "-1.abc", None])
def test_token_de_baja_invalido(settings_tmp, token):
    assert mails.leer_token_baja(settings_tmp, token) is None


def test_token_de_baja_no_sirve_para_otro_alumno_ni_con_otro_secreto(settings_tmp):
    token = mails.token_baja(settings_tmp, 42)
    _, firma = token.split(".")

    assert mails.leer_token_baja(settings_tmp, f"43.{firma}") is None
    otro = settings_tmp.model_copy(update={"jwt_secret": "otra-clave-de-prueba-" * 3})
    assert mails.leer_token_baja(otro, token) is None
    cambiado = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert mails.leer_token_baja(settings_tmp, cambiado) is None


# --- /api/baja -----------------------------------------------------------------------------------


@pytest.fixture
def cliente(hacer_cliente):
    return hacer_cliente([mails.router])


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_baja_con_token(cliente, settings_tmp, raiz, base, alumno, metodo):
    token = mails.token_baja(settings_tmp, alumno)
    if metodo == "post":
        respuesta = cliente.post(f"/api/baja?t={token}", data={"List-Unsubscribe": "One-Click"})
    else:
        respuesta = cliente.get("/api/baja", params={"t": token})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}
    assert dominio.consentimiento(base, alumno, "mails_curso") is False
    ultima = base.execute(
        "SELECT valor, version_texto FROM consentimientos"
        " WHERE alumno_id = ? AND tipo = 'mails_curso' ORDER BY id DESC",
        (alumno,),
    ).fetchone()
    assert (ultima["valor"], ultima["version_texto"]) == (0, "2026-10-01")
    eventos = base.execute("SELECT alumno_id, tipo FROM eventos WHERE tipo = 'baja_mails'").fetchall()
    assert [tuple(e) for e in eventos] == [(alumno, "baja_mails")]


def test_baja_repetida_no_duplica_el_historial(cliente, settings_tmp, raiz, base, alumno):
    token = mails.token_baja(settings_tmp, alumno)

    assert cliente.post(f"/api/baja?t={token}").status_code == 200
    assert cliente.get(f"/api/baja?t={token}").status_code == 200

    assert base.execute("SELECT count(*) FROM eventos WHERE tipo = 'baja_mails'").fetchone()[0] == 1
    ceros = base.execute("SELECT count(*) FROM consentimientos WHERE tipo = 'mails_curso' AND valor = 0").fetchone()[0]
    assert ceros == 1


def test_baja_de_un_alumno_que_ya_borro_sus_datos(cliente, settings_tmp, raiz, base):
    assert cliente.post(f"/api/baja?t={mails.token_baja(settings_tmp, 999)}").json() == {"ok": True}


@pytest.mark.parametrize("consulta", ["", "?t=", "?t=basura", "?t=1.AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"])
@pytest.mark.parametrize("metodo", ["get", "post"])
def test_baja_con_token_invalido_da_400(cliente, raiz, base, alumno, consulta, metodo):
    respuesta = getattr(cliente, metodo)(f"/api/baja{consulta}")

    assert respuesta.status_code == 400
    assert set(respuesta.json()) == {"detalle"}
    assert dominio.consentimiento(base, alumno, "mails_curso") is True


async def test_despues_de_la_baja_no_salen_mails_del_curso(cliente, settings_tmp, raiz, reloj, resend, base, alumno):
    cliente.post(f"/api/baja?t={mails.token_baja(settings_tmp, alumno)}")

    assert await mails.enviar(settings_tmp, alumno, "recordatorio", "recordatorio") == "omitido"
    assert resend.call_count == 0


# --- plantillas reales del repo ----------------------------------------------------------------------


@pytest.mark.parametrize("tipo", sorted(PLANTILLAS))
def test_plantillas_del_repo_usan_marcadores_conocidos(tipo):
    ruta = REPO_CONTENIDO / "mails" / f"{tipo}.md"
    if not ruta.is_file():
        pytest.skip(f"todavía no existe contenido/mails/{tipo}.md")
    datos, cuerpo = contenido.separar_frontmatter(ruta.read_text(encoding="utf-8"))

    assert str(datos.get("asunto") or "").strip(), "falta el asunto en el frontmatter"
    usados = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", f"{datos['asunto']}\n{cuerpo}"))
    assert usados <= mails.MARCADORES[tipo], f"marcadores sin valor: {usados - mails.MARCADORES[tipo]}"


def test_pie_legal_del_repo_lleva_la_baja():
    ruta = REPO_CONTENIDO / "legal" / "pie-mails.md"
    if not ruta.is_file():
        pytest.skip("todavía no existe contenido/legal/pie-mails.md")
    _, cuerpo = contenido.separar_frontmatter(ruta.read_text(encoding="utf-8"))

    assert "{{ENLACE_BAJA}}" in cuerpo
    assert set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", cuerpo)) <= mails.MARCADORES["bienvenida"]


@pytest.mark.parametrize("tipo", sorted(PLANTILLAS))
def test_autor_y_newsletter_son_marcadores_conocidos_de_todos_los_mails(tipo):
    assert contenido.MARCADORES_DEL_CURSO <= mails.MARCADORES[tipo]
