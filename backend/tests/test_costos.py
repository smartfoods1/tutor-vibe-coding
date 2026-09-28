from datetime import datetime, timezone

import pytest
from anthropic.types.beta import BetaUsage

from vibe_tutor import costos, db
from vibe_tutor.costos import (
    PRECIOS,
    costo_anthropic,
    costo_gemini,
    estado_tope,
    gasto_alumno,
    mes_actual,
    registrar,
    tarifa,
)

ANTES_DEL_AUMENTO = datetime(2027, 1, 1, 2, 59, tzinfo=timezone.utc)
DESPUES_DEL_AUMENTO = datetime(2027, 1, 1, 3, 0, tzinfo=timezone.utc)


def _alumno(con, email: str = "ana@example.com") -> int:
    return con.execute("INSERT INTO alumnos (email) VALUES (?)", (email,)).lastrowid


def _sesion(con, alumno_id: int | None = None) -> int:
    alumno_id = alumno_id or _alumno(con)
    return con.execute("INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (alumno_id,)).lastrowid


def _uso(con, creado: str, costo: float, alumno_id: int | None = None) -> None:
    con.execute(
        "INSERT INTO uso (alumno_id, creado, proveedor, modelo, costo_usd) VALUES (?, ?, 'anthropic', 'claude-sonnet-5', ?)",
        (alumno_id, creado, costo),
    )
    con.commit()


def test_precios_verificados_el_28_9_2026():
    assert costos.MODELO_CLAUDE == "claude-sonnet-5"
    assert PRECIOS["claude-sonnet-5"] == {
        "entrada": 2.00,
        "salida": 10.00,
        "cache_escritura": 2.50,
        "cache_escritura_1h": 4.00,
        "cache_lectura": 0.20,
    }
    assert PRECIOS["claude-opus-5"]["entrada"] == 5.00
    assert PRECIOS["gemini-2.5-flash"] == {
        "entrada_texto": 0.30,
        "entrada_audio": 1.00,
        "salida": 2.50,
        "salida_audio": 2.50,
    }
    assert PRECIOS["gemini-3.8-flash-tts"]["salida_audio"] == 9.00
    assert PRECIOS["gemini-3.8-flash-lite-tts"]["salida_audio"] == 6.00


def test_la_voz_sube_el_1_de_enero_de_2027_en_hora_argentina():
    assert tarifa("gemini-3.8-flash-tts", ANTES_DEL_AUMENTO)["salida_audio"] == 9.00
    assert tarifa("gemini-3.8-flash-tts", DESPUES_DEL_AUMENTO)["salida_audio"] == 18.00
    assert tarifa("gemini-3.8-flash-tts", DESPUES_DEL_AUMENTO)["entrada_texto"] == 1.00
    assert tarifa("gemini-3.8-flash-lite-tts", DESPUES_DEL_AUMENTO)["salida_audio"] == 12.00
    assert tarifa("gemini-2.5-flash", DESPUES_DEL_AUMENTO)["entrada_audio"] == 1.00


def test_costo_anthropic_con_sonnet_5_por_defecto():
    usage = {
        "input_tokens": 1_000_000,
        "output_tokens": 100_000,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 500_000,
    }
    assert costo_anthropic(usage) == pytest.approx(2.00 + 1.00 + 0.10)


def test_costo_anthropic_objeto_del_sdk():
    usage = BetaUsage(
        input_tokens=1_000_000,
        output_tokens=100_000,
        cache_creation_input_tokens=None,
        cache_read_input_tokens=500_000,
    )
    assert costo_anthropic(usage) == pytest.approx(3.10)


def test_costo_anthropic_escritura_de_cache_de_5_minutos_y_de_1_hora():
    assert costo_anthropic(
        {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 1_000_000}
    ) == pytest.approx(2.50)
    assert costo_anthropic(
        {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_input_tokens": 1_000_000,
            "cache_creation": {"ephemeral_5m_input_tokens": 600_000, "ephemeral_1h_input_tokens": 400_000},
        }
    ) == pytest.approx(0.6 * 2.50 + 0.4 * 4.00)


def test_costo_anthropic_suma_iteraciones_y_usa_el_precio_de_cada_modelo():
    usage = BetaUsage.model_validate(
        {
            "input_tokens": 1_000_000,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
            "iterations": [
                {
                    "type": "message",
                    "model": "claude-sonnet-5",
                    "input_tokens": 1_000_000,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
                {
                    "type": "fallback_message",
                    "model": "claude-opus-5",
                    "input_tokens": 1_000_000,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            ],
        }
    )
    assert costo_anthropic(usage) == pytest.approx(2.00 + 5.00)


def test_modelo_de_claude_sin_precio_cobra_la_tarifa_de_claude_mas_alta():
    usage = {"model": "claude-futuro-9", "input_tokens": 1_000_000, "output_tokens": 100_000}
    assert costo_anthropic(usage) == pytest.approx(5.00 + 2.50)


def test_costo_gemini_con_fecha():
    assert costo_gemini("gemini-2.5-flash", 1_000_000, 1_000_000, 1_000_000, 0) == pytest.approx(3.80)
    assert costo_gemini("gemini-3.8-flash-tts", 1_000_000, 0, 0, 1_000_000, momento=ANTES_DEL_AUMENTO) == pytest.approx(
        9.50
    )
    assert costo_gemini(
        "gemini-3.8-flash-tts", 1_000_000, 0, 0, 1_000_000, momento=DESPUES_DEL_AUMENTO
    ) == pytest.approx(19.00)
    assert costo_gemini("gemini-2.5-flash-preview-tts", 2_000, 0, 0, 30_000) == pytest.approx(0.001 + 0.3)
    assert costo_gemini("gemini-2.5-flash", 0, 0, 0, 0) == 0


def test_modelo_de_gemini_sin_precio_no_lanza_y_cobra_la_tarifa_mas_alta():
    assert costo_gemini(
        "gemini-3-pro-preview", 1_000_000, 1_000_000, 1_000_000, 1_000_000, momento=ANTES_DEL_AUMENTO
    ) == pytest.approx(0.50 + 1.00 + 10.00 + 10.00)
    assert costo_gemini("gemini-9-flash-tts", 1_000_000, 0, 0, 1_000_000, momento=ANTES_DEL_AUMENTO) == pytest.approx(
        9.50
    )


def test_registrar_con_alumno_y_sesion(con):
    alumno_id = _alumno(con)
    sesion_id = _sesion(con, alumno_id)
    con.commit()

    registrar(
        con,
        "anthropic",
        "claude-sonnet-5",
        {"input_tokens": 10, "output_tokens": 20, "cache_creation_input_tokens": 30, "cache_read_input_tokens": 40},
        0.25,
        alumno_id=alumno_id,
        sesion_id=sesion_id,
    )
    registrar(
        con,
        "gemini",
        "gemini-2.5-flash",
        {"entrada_texto": 5, "entrada_audio": 7, "salida": 3, "salida_audio": 0},
        0.5,
        alumno_id=alumno_id,
    )
    registrar(con, "gemini", "gemini-3.8-flash-tts", {"input_tokens": 1, "output_tokens": 2}, 1.0)

    filas = con.execute(
        "SELECT alumno_id, sesion_id, proveedor, modelo, input_tokens, output_tokens, cache_write, cache_read, costo_usd"
        " FROM uso ORDER BY id"
    ).fetchall()
    assert [tuple(fila) for fila in filas] == [
        (alumno_id, sesion_id, "anthropic", "claude-sonnet-5", 10, 20, 30, 40, 0.25),
        (alumno_id, None, "gemini", "gemini-2.5-flash", 12, 3, 0, 0, 0.5),
        (None, None, "gemini", "gemini-3.8-flash-tts", 1, 2, 0, 0, 1.0),
    ]
    assert con.execute("SELECT costo_usd FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()[0] == pytest.approx(0.25)
    assert gasto_alumno(con, alumno_id) == pytest.approx(0.75)
    assert mes_actual(con) == pytest.approx(1.75)


def test_registrar_acepta_usage_del_sdk(con):
    usage = BetaUsage(input_tokens=100, output_tokens=50, cache_creation_input_tokens=None, cache_read_input_tokens=7)

    registrar(con, "anthropic", "claude-sonnet-5", usage, costo_anthropic(usage))

    fila = con.execute("SELECT input_tokens, output_tokens, cache_write, cache_read FROM uso").fetchone()
    assert tuple(fila) == (100, 50, 0, 7)


def test_registrar_confirma_la_transaccion(tmp_path):
    ruta = tmp_path / db.ARCHIVO
    con = db.conectar(ruta)
    db.migrar(con)
    sesion_id = _sesion(con)
    con.commit()

    registrar(con, "anthropic", "claude-sonnet-5", {"input_tokens": 1, "output_tokens": 1}, 2.5, sesion_id=sesion_id)

    otra = db.conectar(ruta)
    assert otra.execute("SELECT count(*) FROM uso").fetchone()[0] == 1
    assert otra.execute("SELECT costo_usd FROM sesiones").fetchone()[0] == pytest.approx(2.5)
    otra.close()
    con.close()


def test_gasto_del_alumno_es_de_toda_su_vida_y_solo_suyo(con):
    ana = _alumno(con)
    beto = _alumno(con, "beto@example.com")
    _uso(con, "2026-09-10T12:00:00+00:00", 0.30, ana)
    _uso(con, "2026-11-10T12:00:00+00:00", 0.20, ana)
    _uso(con, "2026-11-10T12:00:00+00:00", 0.90, beto)

    assert gasto_alumno(con, ana) == pytest.approx(0.50)
    assert gasto_alumno(con, beto) == pytest.approx(0.90)
    assert gasto_alumno(con, 999) == 0.0


def test_mes_argentino(con):
    _uso(con, "2026-09-01T02:59:59+00:00", 100.0)
    _uso(con, "2026-09-01T03:00:00+00:00", 1.0)
    _uso(con, "2026-09-15T12:00:00+00:00", 2.0)
    _uso(con, "2026-10-01T01:00:00+00:00", 4.0)
    _uso(con, "2026-10-01T03:00:00+00:00", 8.0)

    fin_de_septiembre = datetime(2026, 10, 1, 2, 30, tzinfo=timezone.utc)
    octubre = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
    agosto = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)

    assert mes_actual(con, ahora=fin_de_septiembre) == pytest.approx(7.0)
    assert mes_actual(con, ahora=octubre) == pytest.approx(8.0)
    assert mes_actual(con, ahora=agosto) == pytest.approx(100.0)


def test_mes_actual_sin_registros(con):
    assert mes_actual(con) == 0.0


def test_mes_de_diciembre_pasa_de_anio(con):
    _uso(con, "2026-12-31T23:00:00+00:00", 3.0)
    _uso(con, "2027-01-01T02:59:00+00:00", 5.0)
    _uso(con, "2027-01-01T03:00:00+00:00", 11.0)

    assert mes_actual(con, ahora=datetime(2026, 12, 10, tzinfo=timezone.utc)) == pytest.approx(8.0)
    assert mes_actual(con, ahora=datetime(2027, 1, 10, tzinfo=timezone.utc)) == pytest.approx(11.0)


AHORA = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


def test_tope_sin_gasto(con):
    ana = _alumno(con)
    assert estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA) == {
        "gastado_mes": 0.0,
        "tope_mensual": 50.0,
        "gastado_alumno": 0.0,
        "tope_alumno": 1.0,
        "aviso": False,
        "bloqueado": False,
        "alcance": None,
    }


def test_tope_del_alumno_bloquea_solo_a_ese_alumno(con):
    ana = _alumno(con)
    beto = _alumno(con, "beto@example.com")
    _uso(con, "2026-09-10T12:00:00+00:00", 0.99, ana)
    assert estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)["bloqueado"] is False

    _uso(con, "2026-09-11T12:00:00+00:00", 0.01, ana)
    estado_ana = estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)
    estado_beto = estado_tope(con, beto, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)

    assert estado_ana["bloqueado"] is True and estado_ana["alcance"] == "alumno"
    assert estado_ana["gastado_alumno"] == pytest.approx(1.0)
    assert estado_beto["bloqueado"] is False and estado_beto["alcance"] is None


def test_tope_del_mes_avisa_al_80_y_bloquea_a_todos_al_100(con):
    ana = _alumno(con)
    _uso(con, "2026-09-10T12:00:00+00:00", 39.99)
    assert estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)["aviso"] is False

    _uso(con, "2026-09-11T12:00:00+00:00", 0.01)
    estado = estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)
    assert estado["aviso"] is True and estado["bloqueado"] is False
    assert estado["gastado_mes"] == pytest.approx(40.0)

    _uso(con, "2026-09-12T12:00:00+00:00", 10.0)
    estado = estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)
    assert estado["bloqueado"] is True and estado["alcance"] == "mes"


def test_cuando_se_pasan_los_dos_topes_manda_el_del_mes(con):
    ana = _alumno(con)
    _uso(con, "2026-09-10T12:00:00+00:00", 50.0, ana)

    estado = estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)

    assert estado["alcance"] == "mes"


def test_tope_sin_alumno_mira_solo_el_mes(con):
    _uso(con, "2026-09-10T12:00:00+00:00", 45.0)

    estado = estado_tope(con, None, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)

    assert estado["gastado_alumno"] == 0.0 and estado["aviso"] is True and estado["bloqueado"] is False


def test_tope_suma_de_muchos_turnos_no_queda_por_debajo(con):
    ana = _alumno(con)
    for dia in range(1, 11):
        _uso(con, f"2026-09-{dia:02d}T12:00:00+00:00", 0.1, ana)

    estado = estado_tope(con, ana, tope_alumno=1.0, tope_mensual=50.0, ahora=AHORA)

    assert estado["bloqueado"] is True
    assert estado["gastado_alumno"] == pytest.approx(1.0)


def test_umbral_de_aviso():
    assert costos.UMBRAL_AVISO == 0.8
