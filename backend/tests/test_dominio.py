import pytest

from vibe_tutor import dominio
from vibe_tutor.dominio import ErrorDominio


def _alumno(con, email="ana@example.com") -> int:
    return dominio.crear_alumno(con, email, fuente=None)


def test_crear_alumno_normaliza_el_mail_y_arranca_en_el_modulo_1(con):
    alumno_id = dominio.crear_alumno(con, "  Ana@Example.COM ", fuente="hecho-en")

    fila = dominio.alumno(con, alumno_id)
    assert fila["email"] == "ana@example.com"
    assert fila["modulo_actual"] == 1
    assert fila["fuente"] == "hecho-en"


def test_alumno_por_email(con):
    alumno_id = _alumno(con)

    assert dominio.alumno_por_email(con, "ANA@example.com")["id"] == alumno_id
    assert dominio.alumno_por_email(con, "otro@example.com") is None


def test_vale_el_ultimo_consentimiento_de_cada_tipo(con):
    alumno_id = _alumno(con)
    assert dominio.consentimiento(con, alumno_id, "novedades") is False

    dominio.agregar_consentimiento(con, alumno_id, "novedades", True, "2026-09-28")
    assert dominio.consentimiento(con, alumno_id, "novedades") is True

    dominio.agregar_consentimiento(con, alumno_id, "novedades", False, "2026-09-28")
    assert dominio.consentimiento(con, alumno_id, "novedades") is False
    filas = con.execute("SELECT count(*) FROM consentimientos WHERE alumno_id = ?", (alumno_id,)).fetchone()[0]
    assert filas == 2


def test_registrar_evento(con):
    alumno_id = _alumno(con)

    dominio.registrar_evento(con, alumno_id, "kit", "herramienta=codex")

    fila = con.execute("SELECT alumno_id, tipo, detalle FROM eventos").fetchone()
    assert tuple(fila) == (alumno_id, "kit", "herramienta=codex")


def test_guardar_idea_versiona(con):
    alumno_id = _alumno(con)
    assert dominio.idea_vigente(con, alumno_id) is None

    assert dominio.guardar_idea(con, alumno_id, "# Mi idea", None, "tutor") == 1
    assert dominio.guardar_idea(con, alumno_id, "# Mi idea v2", "- fotos", "alumno") == 2

    vigente = dominio.idea_vigente(con, alumno_id)
    assert vigente["version"] == 2
    assert vigente["texto_md"] == "# Mi idea v2"
    assert vigente["que_sigue_md"] == "- fotos"
    assert vigente["autor"] == "alumno"


@pytest.mark.parametrize(
    ("texto", "que_sigue"),
    [("", None), ("   ", None), ("x" * 6001, None), ("ok", "y" * 3001)],
)
def test_guardar_idea_valida_largos(con, texto, que_sigue):
    alumno_id = _alumno(con)

    with pytest.raises(ErrorDominio):
        dominio.guardar_idea(con, alumno_id, texto, que_sigue, "tutor")


def test_completar_modulo_1_sube_al_2_y_registra_una_sola_vez(con):
    alumno_id = _alumno(con)
    con.execute("INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (alumno_id,))

    assert dominio.completar_modulo(con, alumno_id, 1, "tutor", "Quiere un registro de sueños.") == 2
    assert dominio.completar_modulo(con, alumno_id, 1, "guia_escrita") == 2

    avance = con.execute("SELECT modulo, via, resumen FROM avance WHERE alumno_id = ?", (alumno_id,)).fetchall()
    assert [tuple(f) for f in avance] == [(1, "tutor", "Quiere un registro de sueños.")]
    eventos = con.execute("SELECT tipo, detalle FROM eventos WHERE tipo = 'modulo_completo'").fetchall()
    assert [tuple(f) for f in eventos] == [("modulo_completo", "modulo=1")]
    sesion = con.execute("SELECT fin FROM sesiones WHERE alumno_id = ?", (alumno_id,)).fetchone()
    assert sesion["fin"] is not None


def test_completar_modulo_2_exige_idea(con):
    alumno_id = _alumno(con)
    dominio.completar_modulo(con, alumno_id, 1, "tutor")

    with pytest.raises(ErrorDominio, match="idea"):
        dominio.completar_modulo(con, alumno_id, 2, "guia_escrita")

    dominio.guardar_idea(con, alumno_id, "# Mi idea", None, "tutor")
    assert dominio.completar_modulo(con, alumno_id, 2, "guia_escrita") == 3


def test_completar_modulo_3_no_sube_hasta_el_kit(con):
    alumno_id = _alumno(con)
    dominio.subir_modulo(con, alumno_id, 3)

    assert dominio.completar_modulo(con, alumno_id, 3, "tutor") == 3
    assert dominio.subir_modulo(con, alumno_id, 4) == 4


def test_no_se_puede_completar_un_modulo_posterior_al_actual(con):
    alumno_id = _alumno(con)

    with pytest.raises(ErrorDominio):
        dominio.completar_modulo(con, alumno_id, 3, "tutor")


def test_subir_modulo_nunca_baja(con):
    alumno_id = _alumno(con)
    dominio.subir_modulo(con, alumno_id, 7)

    assert dominio.subir_modulo(con, alumno_id, 4) == 7


def test_resumen_del_modulo_se_recorta(con):
    alumno_id = _alumno(con)

    dominio.completar_modulo(con, alumno_id, 1, "tutor", "r" * 1500)

    assert len(dominio.resumen_modulo(con, alumno_id, 1)) == 1000
    assert dominio.resumen_modulo(con, alumno_id, 2) is None


def test_tocar_actividad(con):
    alumno_id = _alumno(con)
    con.execute("UPDATE alumnos SET ultima_actividad = '2020-01-01T00:00:00+00:00' WHERE id = ?", (alumno_id,))

    dominio.tocar_actividad(con, alumno_id)

    assert dominio.alumno(con, alumno_id)["ultima_actividad"] > "2026-01-01"
