import asyncio
import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx

from vibe_tutor import costos, dominio, mails, tareas
from vibe_tutor.tareas import Envio

RESEND = "https://api.resend.com/emails"
T0 = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


def _alumno(con, email: str, *, mails_curso: bool = True, modulo: int = 3, estado: str = "aprobado") -> int:
    alumno_id = dominio.crear_alumno(con, email, fuente=None, estado=estado)
    with con:
        con.execute("UPDATE alumnos SET modulo_actual = ? WHERE id = ?", (modulo, alumno_id))
    dominio.agregar_consentimiento(con, alumno_id, "mails_curso", True, "prueba")
    dominio.agregar_consentimiento(con, alumno_id, "transferencia", True, "prueba")
    if not mails_curso:
        dominio.agregar_consentimiento(con, alumno_id, "mails_curso", False, "prueba")
    return alumno_id


def _idea(con, alumno_id: int, creado: datetime) -> None:
    version = dominio.guardar_idea(con, alumno_id, "# Mi idea\n\nUn registro de sueños.", None, "tutor")
    with con:
        con.execute(
            "UPDATE ideas SET creado = ? WHERE alumno_id = ? AND version = ?", (_iso(creado), alumno_id, version)
        )


def _kit(con, alumno_id: int) -> None:
    with con:
        con.execute(
            "INSERT INTO kits (alumno_id, version_curso, fecha_machete, herramienta, sistema)"
            " VALUES (?, 'desarrollo', '2026-09-27', 'codex', 'mac')",
            (alumno_id,),
        )


def _mail(con, alumno_id, tipo, clave, estado, creado: datetime) -> None:
    with con:
        con.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado, creado) VALUES (?, ?, ?, ?, ?)",
            (alumno_id, tipo, clave, estado, _iso(creado)),
        )


def _gasto(con, costo: float, creado: datetime) -> None:
    costos.registrar(con, "anthropic", "claude-sonnet-5", {}, costo)
    with con:
        con.execute("UPDATE uso SET creado = ? WHERE id = (SELECT max(id) FROM uso)", (_iso(creado),))


# --- recordatorio ----------------------------------------------------------------------------------


def test_recordatorio_a_los_3_dias_de_la_ultima_version_de_la_idea(settings_tmp, base):
    listo = _alumno(base, "listo@example.com")
    _idea(base, listo, T0 - timedelta(days=3, minutes=1))

    reciente = _alumno(base, "reciente@example.com")
    _idea(base, reciente, T0 - timedelta(days=5))
    _idea(base, reciente, T0 - timedelta(days=2))

    con_kit = _alumno(base, "kit@example.com")
    _idea(base, con_kit, T0 - timedelta(days=5))
    _kit(base, con_kit)

    de_baja = _alumno(base, "baja@example.com", mails_curso=False)
    _idea(base, de_baja, T0 - timedelta(days=5))

    ya_recordado = _alumno(base, "ya@example.com")
    _idea(base, ya_recordado, T0 - timedelta(days=9))
    _mail(base, ya_recordado, "recordatorio", "recordatorio", "enviado", T0 - timedelta(days=5))

    _alumno(base, "sin-idea@example.com")

    en_el_modulo_2 = _alumno(base, "modulo-2@example.com", modulo=2)
    _idea(base, en_el_modulo_2, T0 - timedelta(days=5))

    en_el_modulo_4 = _alumno(base, "modulo-4@example.com", modulo=4)
    _idea(base, en_el_modulo_4, T0 - timedelta(days=5))

    assert tareas.correr_una_vez(settings_tmp, T0) == [
        Envio(listo, "recordatorio", "recordatorio"),
        Envio(en_el_modulo_4, "recordatorio", "recordatorio"),
    ]


def test_recordatorio_solo_a_quien_ya_fue_aprobado(settings_tmp, base):
    pendiente = _alumno(base, "pendiente@example.com", estado="pendiente")
    _idea(base, pendiente, T0 - timedelta(days=5))
    aprobado = _alumno(base, "aprobado@example.com")
    _idea(base, aprobado, T0 - timedelta(days=5))

    assert tareas.correr_una_vez(settings_tmp, T0) == [Envio(aprobado, "recordatorio", "recordatorio")]


def test_recordatorio_fallido_no_se_duplica_con_el_reintento(settings_tmp, base):
    alumno = _alumno(base, "ana@example.com")
    _idea(base, alumno, T0 - timedelta(days=4))
    _mail(base, alumno, "recordatorio", "recordatorio", "fallido", T0 - timedelta(minutes=20))

    assert tareas.correr_una_vez(settings_tmp, T0) == [Envio(alumno, "recordatorio", "recordatorio")]


# --- aviso del 80% ---------------------------------------------------------------------------------


def test_aviso_del_80_por_ciento_una_vez_por_mes(settings_tmp, base):
    _gasto(base, 39.0, T0 - timedelta(days=2))
    assert tareas.correr_una_vez(settings_tmp, T0) == []

    _gasto(base, 1.5, T0 - timedelta(hours=1))
    assert tareas.correr_una_vez(settings_tmp, T0) == [Envio(None, "aviso_80", "aviso_80:2026-09")]

    _mail(base, None, "aviso_80", "aviso_80:2026-09", "enviado", T0)
    assert tareas.correr_una_vez(settings_tmp, T0 + timedelta(hours=1)) == []

    fin_de_septiembre_en_argentina = datetime(2026, 10, 1, 2, 0, tzinfo=timezone.utc)
    assert tareas.correr_una_vez(settings_tmp, fin_de_septiembre_en_argentina) == []

    octubre = datetime(2026, 10, 2, 15, 0, tzinfo=timezone.utc)
    assert tareas.correr_una_vez(settings_tmp, octubre) == []
    _gasto(base, 45.0, octubre - timedelta(hours=1))
    assert tareas.correr_una_vez(settings_tmp, octubre) == [Envio(None, "aviso_80", "aviso_80:2026-10")]


# --- reintentos --------------------------------------------------------------------------------------


def test_reintenta_un_mail_fallido_hasta_3_veces_en_24_horas(settings_tmp, base):
    alumno = _alumno(base, "ana@example.com")
    _mail(base, alumno, "bienvenida", "bienvenida", "fallido", T0)
    _mail(base, alumno, "contame", "contame:7", "enviado", T0)

    vueltas = [T0 + timedelta(minutes=1) + i * tareas.INTERVALO for i in range(4 * 30)]
    reintentos = [
        momento for momento in vueltas
        if Envio(alumno, "bienvenida", "bienvenida") in tareas.correr_una_vez(settings_tmp, momento)
    ]

    assert len(reintentos) == 3
    assert all(momento - T0 < timedelta(hours=24) for momento in reintentos)


def test_vueltas_con_demora_nunca_pasan_de_3_reintentos(settings_tmp, base):
    _mail(base, None, "aviso_80", "aviso_80:2026-09", "fallido", T0)
    paso = tareas.INTERVALO + timedelta(seconds=7)

    vueltas = [T0 + timedelta(seconds=30) + i * paso for i in range(4 * 30)]
    reintentos = [m for m in vueltas if tareas.correr_una_vez(settings_tmp, m)]

    assert 1 <= len(reintentos) <= 3


# --- retención ---------------------------------------------------------------------------------------


def test_retencion_de_conversaciones_y_codigos(settings_tmp, base):
    activo = _alumno(base, "activo@example.com")
    inactivo = _alumno(base, "inactivo@example.com")
    with base:
        base.execute("UPDATE alumnos SET ultima_actividad = ? WHERE id = ?", (_iso(T0 - timedelta(days=100)), activo))
        base.execute("UPDATE alumnos SET ultima_actividad = ? WHERE id = ?", (_iso(T0 - timedelta(days=366)), inactivo))
    sesiones = {}
    for nombre, alumno_id, fin in (
        ("vieja", activo, T0 - timedelta(days=31)),
        ("reciente", activo, T0 - timedelta(days=29)),
        ("abierta", activo, None),
        ("abandonada", inactivo, None),
    ):
        with base:
            cursor = base.execute(
                "INSERT INTO sesiones (alumno_id, modulo, fin) VALUES (?, 1, ?)",
                (alumno_id, _iso(fin) if fin else None),
            )
            sesiones[nombre] = cursor.lastrowid
            base.execute(
                "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 0, 'user', ?)",
                (cursor.lastrowid, json.dumps([{"type": "text", "text": "hola"}])),
            )
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 0.02, alumno_id=activo, sesion_id=sesiones["vieja"])
    with base:
        base.execute(
            "INSERT INTO avance (alumno_id, modulo, completado, resumen, via) VALUES (?, 1, ?, 'resumen', 'tutor')",
            (activo, _iso(T0 - timedelta(days=31))),
        )
        for horas in (25, 23):
            base.execute(
                "INSERT INTO codigos (email, hash, sal, vence, pendiente_json, creado)"
                " VALUES (?, 'h', 's', ?, '{}', ?)",
                (f"hace-{horas}@example.com", _iso(T0), _iso(T0 - timedelta(hours=horas))),
            )

    tareas.correr_una_vez(settings_tmp, T0)

    quedan = {fila[0] for fila in base.execute("SELECT id FROM sesiones")}
    assert quedan == {sesiones["reciente"], sesiones["abierta"]}
    con_mensajes = {fila[0] for fila in base.execute("SELECT sesion_id FROM mensajes")}
    assert con_mensajes == quedan
    uso = base.execute("SELECT alumno_id, sesion_id, costo_usd FROM uso").fetchone()
    assert (uso["alumno_id"], uso["sesion_id"], uso["costo_usd"]) == (activo, None, 0.02)
    assert base.execute("SELECT resumen FROM avance WHERE alumno_id = ?", (activo,)).fetchone()[0] == "resumen"
    assert [f[0] for f in base.execute("SELECT email FROM codigos")] == ["hace-23@example.com"]
    assert dominio.alumno(base, inactivo) is not None


def _creado(con, alumno_id: int, creado: datetime) -> None:
    with con:
        con.execute("UPDATE alumnos SET creado = ? WHERE id = ?", (_iso(creado), alumno_id))


def test_retencion_borra_los_pedidos_de_acceso_pendientes_de_mas_de_90_dias(settings_tmp, base):
    vencido = _alumno(base, "vencido@example.com", estado="pendiente")
    _creado(base, vencido, T0 - timedelta(days=90, minutes=1))
    dominio.registrar_evento(base, vencido, "inscripcion")
    reciente = _alumno(base, "reciente@example.com", estado="pendiente")
    _creado(base, reciente, T0 - timedelta(days=89, hours=23))
    aprobado_viejo = _alumno(base, "viejo@example.com")
    _creado(base, aprobado_viejo, T0 - timedelta(days=400))
    with base:
        base.execute("UPDATE alumnos SET ultima_actividad = ? WHERE id = ?", (_iso(T0), vencido))

    borrados = tareas.retencion(base, T0)

    assert borrados["pendientes"] == 1
    assert dominio.alumno(base, vencido) is None
    assert dominio.alumno(base, reciente) is not None
    assert dominio.alumno(base, aprobado_viejo) is not None
    assert base.execute("SELECT count(*) FROM consentimientos WHERE alumno_id = ?", (vencido,)).fetchone()[0] == 0
    eventos = [tuple(f) for f in base.execute("SELECT alumno_id, tipo FROM eventos ORDER BY id")]
    assert eventos == [(None, "inscripcion"), (None, "borrado")]


def test_la_tarea_periodica_aplica_la_retencion_de_pendientes(settings_tmp, base):
    vencido = _alumno(base, "vencido@example.com", estado="pendiente")
    _creado(base, vencido, T0 - timedelta(days=91))

    tareas.correr_una_vez(settings_tmp, T0)

    assert dominio.alumno(base, vencido) is None


def _sesion(con, alumno_id: int, modulo: int, inicio: datetime, mensajes: list[datetime]) -> int:
    with con:
        sesion_id = con.execute(
            "INSERT INTO sesiones (alumno_id, modulo, inicio) VALUES (?, ?, ?)", (alumno_id, modulo, _iso(inicio))
        ).lastrowid
        for orden, creado in enumerate(mensajes):
            con.execute(
                "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json, creado) VALUES (?, ?, 'user', '[]', ?)",
                (sesion_id, orden, _iso(creado)),
            )
    return sesion_id


def _completado(con, alumno_id: int, modulo: int, cuando: datetime) -> None:
    with con:
        con.execute(
            "INSERT INTO avance (alumno_id, modulo, completado, via) VALUES (?, ?, ?, 'tutor')",
            (alumno_id, modulo, _iso(cuando)),
        )


def test_retencion_de_sesiones_reabiertas_de_modulos_ya_completos(settings_tmp, base):
    ana = _alumno(base, "ana@example.com")
    _completado(base, ana, 1, T0 - timedelta(days=40))
    _completado(base, ana, 2, T0 - timedelta(days=10))
    vieja = _sesion(base, ana, 1, T0 - timedelta(days=45), [T0 - timedelta(days=45), T0 - timedelta(days=31)])
    sin_mensajes = _sesion(base, ana, 1, T0 - timedelta(days=35), [])
    con_mensaje_reciente = _sesion(base, ana, 1, T0 - timedelta(days=45), [T0 - timedelta(days=29)])
    recien_iniciada = _sesion(base, ana, 1, T0 - timedelta(days=2), [])
    modulo_completo_hace_poco = _sesion(base, ana, 2, T0 - timedelta(days=45), [T0 - timedelta(days=40)])
    modulo_sin_completar = _sesion(base, ana, 3, T0 - timedelta(days=45), [T0 - timedelta(days=40)])

    borrados = tareas.retencion(base, T0)

    quedan = {fila[0] for fila in base.execute("SELECT id FROM sesiones")}
    assert quedan == {con_mensaje_reciente, recien_iniciada, modulo_completo_hace_poco, modulo_sin_completar}
    assert vieja not in quedan and sin_mensajes not in quedan
    assert borrados["sesiones_reabiertas"] == 2
    assert {fila[0] for fila in base.execute("SELECT DISTINCT sesion_id FROM mensajes")} <= quedan


def test_un_paso_que_falla_no_frena_a_los_demas(settings_tmp, base, monkeypatch):
    alumno = _alumno(base, "ana@example.com")
    _idea(base, alumno, T0 - timedelta(days=4))
    with base:
        base.execute(
            "INSERT INTO codigos (email, hash, sal, vence, creado) VALUES ('x@example.com', 'h', 's', ?, ?)",
            (_iso(T0), _iso(T0 - timedelta(days=2))),
        )

    def roto(*args, **kwargs):
        raise RuntimeError("se rompió el cálculo del tope")

    monkeypatch.setattr(tareas.costos, "estado_tope", roto)

    assert tareas.correr_una_vez(settings_tmp, T0) == [Envio(alumno, "recordatorio", "recordatorio")]
    assert base.execute("SELECT count(*) FROM codigos").fetchone()[0] == 0


# --- bucle -----------------------------------------------------------------------------------------------


class _Parar(Exception):
    pass


async def test_bucle_manda_los_envios_cada_15_minutos_y_sigue_ante_errores(settings_tmp, monkeypatch):
    envios = [Envio(1, "recordatorio", "recordatorio"), Envio(None, "aviso_80", "aviso_80:2026-09")]
    vueltas = iter([RuntimeError("falla una vuelta"), envios])

    def correr(settings, ahora=None):
        resultado = next(vueltas)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado

    enviados, esperas = [], []

    async def enviar(settings, alumno_id, tipo, clave, datos=None):
        enviados.append((alumno_id, tipo, clave))
        return "enviado"

    async def dormir(segundos):
        esperas.append(segundos)
        if esperas.count(tareas.INTERVALO.total_seconds()) == 2:
            raise _Parar

    monkeypatch.setattr(tareas, "correr_una_vez", correr)
    monkeypatch.setattr(mails, "enviar", enviar)
    monkeypatch.setattr(tareas, "dormir", dormir)

    with pytest.raises(_Parar):
        await tareas.bucle(settings_tmp)

    assert enviados == [(1, "recordatorio", "recordatorio"), (None, "aviso_80", "aviso_80:2026-09")]
    assert esperas == [900.0, tareas.PAUSA_ENTRE_MAILS, 900.0]


async def test_bucle_se_puede_cancelar(settings_tmp, monkeypatch):
    monkeypatch.setattr(tareas, "correr_una_vez", lambda settings, ahora=None: [])
    tarea = asyncio.create_task(tareas.bucle(settings_tmp))
    await asyncio.sleep(0.05)

    tarea.cancel()
    with pytest.raises(asyncio.CancelledError):
        await tarea


async def test_de_punta_a_punta_el_recordatorio_sale_una_sola_vez(settings_tmp, base, monkeypatch):
    raiz = settings_tmp.contenido_dir
    (raiz / "mails").mkdir(parents=True)
    (raiz / "legal").mkdir()
    (raiz / "mails" / "recordatorio.md").write_text(
        "---\nasunto: Tu idea está lista\n---\nSeguí acá: {{ENLACE_MODULO_3}}\n", encoding="utf-8"
    )
    (raiz / "legal" / "pie-mails.md").write_text("Baja: {{ENLACE_BAJA}}\n", encoding="utf-8")
    monkeypatch.setattr(mails, "ahora", lambda: T0)
    alumno = _alumno(base, "ana@example.com")
    _idea(base, alumno, T0 - timedelta(days=4))

    with respx.mock() as mock:
        ruta = mock.post(RESEND).mock(return_value=httpx.Response(200, json={"id": "mail-1"}))
        estados = await tareas.mandar(settings_tmp, tareas.correr_una_vez(settings_tmp, T0))
        assert estados == ["enviado"]
        assert tareas.correr_una_vez(settings_tmp, T0 + timedelta(minutes=15)) == []
        assert ruta.call_count == 1
        assert json.loads(ruta.calls.last.request.content)["to"] == ["ana@example.com"]
