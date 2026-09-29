import json

import pytest
import yaml

from vibe_tutor import dominio, herramientas
from vibe_tutor.herramientas import Contexto

MACHETE = [
    {
        "id": "codex-planes",
        "tema": "planes",
        "aplica_a": ["codex"],
        "sistema": ["mac", "windows"],
        "texto": "El plan Go cuesta US$8 por mes.",
        "fuente": "https://learn.chatgpt.com/docs/pricing",
        "verificado": "2026-09-28",
        "probado": False,
    },
    {
        "id": "claude-planes",
        "tema": "planes",
        "aplica_a": ["claude"],
        "sistema": ["mac", "windows"],
        "texto": "Claude Pro cuesta US$20 por mes.",
        "fuente": "https://claude.com/pricing",
        "verificado": "2026-09-27",
        "probado": True,
    },
    {
        "id": "codex-instalar-mac",
        "tema": "instalar",
        "aplica_a": ["codex"],
        "sistema": ["mac"],
        "texto": "Bajá la app de ChatGPT para Mac.",
        "fuente": "https://chatgpt.com/download",
        "verificado": "2026-09-28",
        "probado": False,
    },
    {
        "id": "codex-instalar-windows",
        "tema": "instalar",
        "aplica_a": ["codex"],
        "sistema": ["windows"],
        "texto": "Instalá la app de ChatGPT desde la Microsoft Store.",
        "fuente": "https://learn.chatgpt.com/docs/windows/windows-app",
        "verificado": "2026-09-28",
        "probado": False,
    },
]
IDEA = "# Recetas de la abuela\n\nUna página con las recetas de mi abuela, para mis primos."
RESUMEN = "Quiere una página con recetas familiares.\nMiedo principal: romper la compu."


@pytest.fixture
def raiz(tmp_path):
    raiz = tmp_path / "contenido"
    raiz.mkdir()
    (raiz / "machete.yaml").write_text(yaml.safe_dump(MACHETE, allow_unicode=True), encoding="utf-8")
    return raiz


@pytest.fixture
def alumno_id(con):
    return dominio.crear_alumno(con, "ana@example.com", fuente=None)


def sesion(con, alumno_id: int, modulo: int) -> int:
    with con:
        return con.execute(
            "INSERT INTO sesiones (alumno_id, modulo) VALUES (?, ?)", (alumno_id, modulo)
        ).lastrowid


def contexto(con, alumno_id, raiz, modulo: int) -> Contexto:
    return Contexto(alumno_id=alumno_id, sesion_id=sesion(con, alumno_id, modulo), modulo=modulo, contenido_dir=raiz)


def ejecutar(con, ctx, nombre, entrada):
    return herramientas.ejecutar(con, ctx, nombre, entrada)


def claves(esquema) -> set[str]:
    if isinstance(esquema, dict):
        return set(esquema) | set().union(*(claves(v) for v in esquema.values()))
    if isinstance(esquema, list):
        return set().union(*(claves(v) for v in esquema)) if esquema else set()
    return set()


@pytest.mark.parametrize(
    ("modulo", "nombres"),
    [
        (1, ["marcar_avance"]),
        (2, ["guardar_idea", "marcar_avance"]),
        (3, ["consultar_machete", "registrar_taller", "guardar_idea", "marcar_avance"]),
    ],
)
def test_herramientas_por_modulo(modulo, nombres):
    tools = herramientas.tools_de(modulo)

    assert [tool["name"] for tool in tools] == nombres
    assert tools == herramientas.tools_de(modulo)
    for tool in tools:
        assert tool["strict"] is True
        assert tool["eager_input_streaming"] is True
        esquema = tool["input_schema"]
        assert esquema["additionalProperties"] is False
        assert sorted(esquema["required"]) == sorted(esquema["properties"])
        # El modo estricto de la API no acepta límites de largo ni numéricos: se validan acá.
        assert not claves(esquema) & {"maxLength", "minLength", "minimum", "maximum"}
        # La API rechaza un enum en un campo con varios tipos (por ejemplo ["string", "null"]).
        for propiedad in esquema["properties"].values():
            assert not ("enum" in propiedad and isinstance(propiedad.get("type"), list)), propiedad
        assert tool["description"]


def test_tools_de_modulo_invalido():
    with pytest.raises(ValueError):
        herramientas.tools_de(4)


def test_guardar_idea_versiona_con_autor_tutor(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 2)

    primero = ejecutar(con, ctx, "guardar_idea", {"texto_md": IDEA, "que_sigue_md": "Un buscador."})
    segundo = ejecutar(con, ctx, "guardar_idea", {"texto_md": IDEA + "\n\nCon fotos.", "que_sigue_md": None})

    assert primero.es_error is False
    assert primero.eventos == (("idea", {"version": 1}),)
    assert segundo.eventos == (("idea", {"version": 2}),)
    assert "versión 2" in segundo.texto
    vigente = dominio.idea_vigente(con, alumno_id)
    assert vigente["autor"] == "tutor"
    assert vigente["texto_md"].endswith("Con fotos.")
    assert vigente["que_sigue_md"] is None


def test_guardar_idea_en_el_modulo_2_le_cuenta_al_tutor_lo_que_ve_la_persona(con, alumno_id, raiz):
    """El resultado de la herramienta le llega al modelo: tiene que describir la pantalla de verdad."""
    ctx = contexto(con, alumno_id, raiz, 2)

    resultado = ejecutar(con, ctx, "guardar_idea", {"texto_md": IDEA, "que_sigue_md": None})

    for nombre in ("Leer mi idea acá", "Está bien así", "Quiero cambiar algo"):
        assert nombre in resultado.texto
    # No la manda a otra pantalla a leer lo que ya tiene en la charla.
    assert "ya la puede ver" not in resultado.texto


def test_guardar_idea_en_el_modulo_3_no_habla_de_botones_que_ahi_no_estan(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "guardar_idea", {"texto_md": IDEA, "que_sigue_md": None})

    assert "Mi idea" in resultado.texto
    assert "Está bien así" not in resultado.texto


@pytest.mark.parametrize(
    "entrada",
    [
        {"texto_md": "x" * 6001, "que_sigue_md": None},
        {"texto_md": IDEA, "que_sigue_md": "y" * 3001},
        {"texto_md": "   ", "que_sigue_md": None},
    ],
)
def test_guardar_idea_limites(con, alumno_id, raiz, entrada):
    ctx = contexto(con, alumno_id, raiz, 2)

    resultado = ejecutar(con, ctx, "guardar_idea", entrada)

    assert resultado.es_error is True
    assert resultado.eventos == ()
    assert dominio.idea_vigente(con, alumno_id) is None


def test_marcar_avance_modulo_1(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 1)

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 1, "resumen": RESUMEN})

    assert resultado.es_error is False
    assert resultado.eventos == (("avance", {"modulo_completado": 1, "modulo_actual": 2}),)
    fila = con.execute("SELECT * FROM avance WHERE alumno_id = ?", (alumno_id,)).fetchone()
    assert (fila["modulo"], fila["via"], fila["resumen"]) == (1, "tutor", RESUMEN)
    assert con.execute("SELECT fin FROM sesiones WHERE id = ?", (ctx.sesion_id,)).fetchone()["fin"] is not None
    evento = con.execute("SELECT tipo, detalle FROM eventos WHERE alumno_id = ?", (alumno_id,)).fetchone()
    assert (evento["tipo"], evento["detalle"]) == ("modulo_completo", "modulo=1")


def test_marcar_avance_modulo_3_no_sube_hasta_el_kit(con, alumno_id, raiz):
    dominio.completar_modulo(con, alumno_id, 1, "tutor", "Semilla.")
    dominio.guardar_idea(con, alumno_id, IDEA, None, "tutor")
    dominio.completar_modulo(con, alumno_id, 2, "tutor", "Idea lista.")
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 3, "resumen": "Instaló la app.\nEligió Codex en Mac."})

    assert resultado.eventos == (("avance", {"modulo_completado": 3, "modulo_actual": 3}),)
    assert "kit" in resultado.texto


def test_marcar_avance_otro_modulo(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 1)

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 2, "resumen": RESUMEN})

    assert resultado.es_error is True
    assert "módulo 1" in resultado.texto
    assert con.execute("SELECT COUNT(*) FROM avance").fetchone()[0] == 0


def test_marcar_avance_modulo_2_sin_idea(con, alumno_id, raiz):
    dominio.completar_modulo(con, alumno_id, 1, "tutor", "Semilla.")
    ctx = contexto(con, alumno_id, raiz, 2)

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 2, "resumen": RESUMEN})

    assert resultado.es_error is True
    assert "idea" in resultado.texto
    assert resultado.eventos == ()


@pytest.mark.parametrize(
    "resumen",
    [
        "x" * 1001,
        "\n".join(f"línea {n}" for n in range(6)),
        "  \n ",
        "Se llama ana@example.com y quiere recetas.\nMiedo: costo.",
        "Su teléfono es 11 1234-5678.\nQuiere recetas.",
    ],
)
def test_marcar_avance_valida_el_resumen(con, alumno_id, raiz, resumen):
    ctx = contexto(con, alumno_id, raiz, 1)

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 1, "resumen": resumen})

    assert resultado.es_error is True
    assert con.execute("SELECT COUNT(*) FROM avance").fetchone()[0] == 0


def test_consultar_machete_filtra_por_taller(con, alumno_id, raiz):
    with con:
        con.execute("UPDATE alumnos SET herramienta = 'codex', sistema = 'windows' WHERE id = ?", (alumno_id,))
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "consultar_machete", {"tema": "todos"})

    assert resultado.es_error is False
    assert "codex-planes" in resultado.texto
    assert "codex-instalar-windows" in resultado.texto
    assert "codex-instalar-mac" not in resultado.texto
    assert "claude-planes" not in resultado.texto
    assert "verificado el 2026-09-28" in resultado.texto
    assert "https://learn.chatgpt.com/docs/pricing" in resultado.texto
    assert "probado: false" in resultado.texto


def test_consultar_machete_por_tema_sin_taller(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "consultar_machete", {"tema": "planes"})

    assert "codex-planes" in resultado.texto
    assert "claude-planes" in resultado.texto
    assert "probado: true" in resultado.texto
    assert "codex-instalar" not in resultado.texto


def test_consultar_machete_sistema_otro_filtra_solo_herramienta(con, alumno_id, raiz):
    with con:
        con.execute("UPDATE alumnos SET herramienta = 'codex', sistema = 'otro' WHERE id = ?", (alumno_id,))
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "consultar_machete", {"tema": "instalar"})

    assert "codex-instalar-mac" in resultado.texto
    assert "codex-instalar-windows" in resultado.texto


def test_consultar_machete_sin_resultados(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "consultar_machete", {"tema": "publicar"})

    assert resultado.es_error is False
    assert "No hay datos" in resultado.texto


def test_consultar_machete_no_disponible(con, alumno_id, tmp_path):
    ctx = contexto(con, alumno_id, tmp_path / "no-existe", 3)

    resultado = ejecutar(con, ctx, "consultar_machete", {"tema": "todos"})

    assert resultado.es_error is True
    assert "memoria" in resultado.texto


def test_registrar_taller(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "registrar_taller", {"herramienta": "claude", "sistema": "mac"})

    assert resultado.es_error is False
    fila = dominio.alumno(con, alumno_id)
    assert (fila["herramienta"], fila["sistema"]) == ("claude", "mac")
    assert resultado.eventos == (("taller", {"herramienta": "claude", "sistema": "mac"}),)


def test_registrar_taller_otro(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "registrar_taller", {"herramienta": "codex", "sistema": "otro"})

    assert resultado.es_error is False
    assert "Mac o Windows" in resultado.texto
    assert dominio.alumno(con, alumno_id)["sistema"] == "otro"
    assert resultado.eventos == (("taller", {"herramienta": "codex", "sistema": "otro"}),)


@pytest.mark.parametrize(
    ("modulo", "nombre", "entrada"),
    [
        (1, "guardar_idea", {"texto_md": IDEA, "que_sigue_md": None}),
        (2, "consultar_machete", {"tema": "todos"}),
        (2, "registrar_taller", {"herramienta": "codex", "sistema": "mac"}),
        (3, "borrar_todo", {}),
    ],
)
def test_herramienta_fuera_del_modulo(con, alumno_id, raiz, modulo, nombre, entrada):
    ctx = contexto(con, alumno_id, raiz, modulo)

    resultado = ejecutar(con, ctx, nombre, entrada)

    assert resultado.es_error is True
    assert nombre in resultado.texto
    assert dominio.idea_vigente(con, alumno_id) is None
    assert dominio.alumno(con, alumno_id)["herramienta"] is None


@pytest.mark.parametrize(
    ("nombre", "entrada", "fragmento"),
    [
        ("registrar_taller", {"herramienta": "cursor", "sistema": "mac"}, "herramienta"),
        ("registrar_taller", {"herramienta": "codex"}, "sistema"),
        ("registrar_taller", {"herramienta": "codex", "sistema": "mac", "extra": 1}, "extra"),
        ("marcar_avance", {"modulo": "1", "resumen": RESUMEN}, "modulo"),
        ("consultar_machete", {"tema": "chismes"}, "tema"),
        ("guardar_idea", {"texto_md": 42, "que_sigue_md": None}, "texto_md"),
        ("guardar_idea", "no es un objeto", "objeto"),
    ],
)
def test_entradas_invalidas(con, alumno_id, raiz, nombre, entrada, fragmento):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, nombre, entrada)

    assert resultado.es_error is True
    assert fragmento in resultado.texto
    assert dominio.alumno(con, alumno_id)["herramienta"] is None


def test_enum_sin_distinguir_mayusculas(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    resultado = ejecutar(con, ctx, "registrar_taller", {"herramienta": "Codex", "sistema": "Windows"})

    assert resultado.es_error is False
    assert dominio.alumno(con, alumno_id)["herramienta"] == "codex"


def test_los_resultados_son_texto_serializable(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 3)

    for nombre, entrada in [
        ("consultar_machete", {"tema": "todos"}),
        ("registrar_taller", {"herramienta": "codex", "sistema": "mac"}),
        ("guardar_idea", {"texto_md": IDEA, "que_sigue_md": None}),
    ]:
        resultado = ejecutar(con, ctx, nombre, entrada)
        assert isinstance(resultado.texto, str) and resultado.texto
        json.dumps(resultado.eventos)


def test_marcar_avance_acepta_fechas_y_numeros_cortos(con, alumno_id, raiz):
    ctx = contexto(con, alumno_id, raiz, 1)
    resumen = "Empezó el 2026-09-28 y quiere 3 recetas por semana.\nMiedo: costo."

    resultado = ejecutar(con, ctx, "marcar_avance", {"modulo": 1, "resumen": resumen})

    assert resultado.es_error is False
    assert dominio.resumen_modulo(con, alumno_id, 1) == resumen
