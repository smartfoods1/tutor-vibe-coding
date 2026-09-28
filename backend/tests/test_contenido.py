from datetime import date
from pathlib import Path

import pytest

from vibe_tutor import contenido
from vibe_tutor.contenido import ErrorContenido

REPO_CONTENIDO = Path(__file__).resolve().parents[2] / "contenido"
HOY = date(2026, 10, 1)

DATO = {
    "id": "codex-instalar-mac",
    "tema": "instalar",
    "aplica_a": ["codex"],
    "sistema": ["mac"],
    "texto": "Bajá la app de escritorio de ChatGPT.",
    "fuente": "https://learn.chatgpt.com/docs",
    "verificado": "2026-09-28",
    "probado": False,
}


def _machete(tmp_path: Path, datos: list[dict]) -> Path:
    import yaml

    raiz = tmp_path / "contenido"
    raiz.mkdir(exist_ok=True)
    (raiz / "machete.yaml").write_text(yaml.safe_dump(datos, allow_unicode=True), encoding="utf-8")
    return raiz


def _dato(**cambios) -> dict:
    return {**DATO, **cambios}


def test_carga_un_machete_valido(tmp_path):
    raiz = _machete(tmp_path, [DATO, _dato(id="claude-publicar", tema="publicar", aplica_a=["claude"], sistema=["mac", "windows"])])

    datos = contenido.cargar_machete(raiz, hoy=HOY)

    assert [d.id for d in datos] == ["codex-instalar-mac", "claude-publicar"]
    assert datos[0].verificado == date(2026, 9, 28)
    assert datos[1].sistema == ("mac", "windows")


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"fuente": "http://inseguro.com"}, "https://"),
        ({"verificado": "28/9/2026"}, "fecha"),
        ({"verificado": "2026-10-02"}, "futura"),
        ({"tema": "chismes"}, "tema"),
        ({"aplica_a": ["cursor"]}, "aplica_a"),
        ({"aplica_a": []}, "aplica_a"),
        ({"sistema": ["linux"]}, "sistema"),
        ({"texto": ""}, "texto"),
        ({"texto": "x" * 1501}, "texto"),
        ({"probado": "sí"}, "probado"),
        ({"id": "Con Espacios"}, "id"),
    ],
)
def test_rechaza_datos_invalidos(tmp_path, cambios, mensaje):
    raiz = _machete(tmp_path, [_dato(**cambios)])

    with pytest.raises(ErrorContenido, match=mensaje):
        contenido.cargar_machete(raiz, hoy=HOY)


def test_rechaza_campos_faltantes(tmp_path):
    incompleto = dict(DATO)
    del incompleto["fuente"]

    with pytest.raises(ErrorContenido, match="fuente"):
        contenido.cargar_machete(_machete(tmp_path, [incompleto]), hoy=HOY)


def test_rechaza_ids_repetidos(tmp_path):
    with pytest.raises(ErrorContenido, match="repetido"):
        contenido.cargar_machete(_machete(tmp_path, [DATO, DATO]), hoy=HOY)


@pytest.mark.parametrize(
    "texto",
    [
        "Codex se puede usar GRATIS con la app de escritorio.",
        "El plan es gratuito.",
        "Una opción gratuita para publicar.",
        "Se puede hacer sin pagar nada.",
        "Publicar no tiene costo.",
        "Publicar es sin costo.",
        "Se crea con Google y no pide tarjeta.",
        "No hace falta tarjeta.",
        "Se abre sin tarjeta de crédito.",
        "Con el plan Free alcanza.",
        "El plan free de Netlify da 300 créditos.",
        "Usá el free plan.",
        'En el plan "Free" se puede publicar.',
    ],
)
def test_prometer_que_no_se_paga_exige_prueba_real(tmp_path, texto):
    with pytest.raises(ErrorContenido, match="gratis"):
        contenido.cargar_machete(_machete(tmp_path, [_dato(texto=texto, probado=False)]), hoy=HOY)
    assert contenido.cargar_machete(_machete(tmp_path, [_dato(texto=texto, probado=True)]), hoy=HOY)[0].probado


def test_filtra_por_herramienta_y_sistema(tmp_path):
    raiz = _machete(
        tmp_path,
        [
            DATO,
            _dato(id="codex-instalar-windows", sistema=["windows"]),
            _dato(id="claude-instalar", aplica_a=["claude"], sistema=["mac", "windows"]),
            _dato(id="ayuda", tema="ayuda", aplica_a=["codex", "claude"], sistema=["mac", "windows"]),
        ],
    )
    datos = contenido.cargar_machete(raiz, hoy=HOY)

    filtrados = contenido.filtrar(datos, herramienta="codex", sistema="windows")

    assert [d.id for d in filtrados] == ["codex-instalar-windows", "ayuda"]


def test_fecha_mas_vieja_y_vencidos(tmp_path):
    raiz = _machete(
        tmp_path,
        [
            _dato(id="nuevo", verificado="2026-09-28"),
            _dato(id="viejo", verificado="2026-08-10"),
            _dato(id="limite", verificado="2026-08-17"),
        ],
    )
    datos = contenido.cargar_machete(raiz, hoy=HOY)

    assert contenido.fecha_mas_vieja(datos) == date(2026, 8, 10)
    assert [d.id for d in contenido.vencidos(datos, hoy=HOY)] == ["viejo"]


def test_lee_de_disco_en_cada_pedido(tmp_path):
    raiz = tmp_path / "contenido"
    (raiz / "web").mkdir(parents=True)
    guia = raiz / "web" / "modulo-1.md"
    guia.write_text("versión 1", encoding="utf-8")

    assert contenido.leer(raiz, "web/modulo-1.md") == "versión 1"
    guia.write_text("versión 2", encoding="utf-8")
    assert contenido.leer(raiz, "web/modulo-1.md") == "versión 2"


@pytest.mark.parametrize("ruta", ["../secreto.txt", "/etc/passwd", "web/../../secreto.txt"])
def test_no_lee_fuera_de_contenido(tmp_path, ruta):
    raiz = tmp_path / "contenido"
    raiz.mkdir()
    (tmp_path / "secreto.txt").write_text("no", encoding="utf-8")

    with pytest.raises(ErrorContenido, match="fuera"):
        contenido.leer(raiz, ruta)


def test_archivo_inexistente(tmp_path):
    raiz = tmp_path / "contenido"
    raiz.mkdir()

    with pytest.raises(ErrorContenido, match="no existe"):
        contenido.leer(raiz, "web/modulo-9.md")


def test_machete_del_repo_es_valido():
    datos = contenido.cargar_machete(REPO_CONTENIDO)

    temas = {d.tema for d in datos}
    assert {"planes", "instalar", "publicar", "ver", "ayuda"} <= temas
    for herramienta in ("codex", "claude"):
        for sistema in ("mac", "windows"):
            filtrados = contenido.filtrar(datos, herramienta=herramienta, sistema=sistema)
            assert {"instalar", "publicar"} <= {d.tema for d in filtrados}, (herramienta, sistema)


def test_el_machete_del_repo_no_promete_lo_que_no_probo():
    datos = {d.id: d for d in contenido.cargar_machete(REPO_CONTENIDO)}

    netlify = datos["limites-netlify"]
    assert netlify.probado is False
    assert "free" not in netlify.texto.lower()
    assert "20 publicaciones" not in netlify.texto
    assert "300 créditos" in netlify.texto and "15" in netlify.texto


def test_el_machete_del_repo_trae_la_descarga_oficial_de_claude():
    dato = {d.id: d for d in contenido.cargar_machete(REPO_CONTENIDO)}["claude-instalar"]

    assert "https://claude.com/download" in dato.texto
    assert dato.verificado.isoformat() == "2026-09-28"


def test_version_legal_sale_del_frontmatter(tmp_path):
    legal = tmp_path / "legal"
    legal.mkdir()
    (legal / "consentimientos.md").write_text("---\nversion: 2026-10-01\n---\n\n# Consentimientos\n", encoding="utf-8")

    assert contenido.version_legal(tmp_path) == "2026-10-01"


def test_version_legal_sin_archivo_es_borrador(tmp_path):
    assert contenido.version_legal(tmp_path) == "borrador"


# --- Marcadores de quien opera el curso ({{AUTOR}} y {{NEWSLETTER}}) ---


def _config(autor: str = "", newsletter: str = ""):
    from types import SimpleNamespace

    return SimpleNamespace(autor_nombre=autor, newsletter_nombre=newsletter)


def test_reemplaza_autor_y_newsletter_con_la_configuracion():
    texto = "Lo escribió {{AUTOR}}. Las novedades salen por {{NEWSLETTER}}."

    assert (
        contenido.reemplazar_marcadores(texto, _config("Ana Pérez", "El boletín de Ana"))
        == "Lo escribió Ana Pérez. Las novedades salen por El boletín de Ana."
    )


def test_sin_autor_dice_el_autor_del_curso_y_sin_newsletter_queda_vacio():
    texto = "Lo escribió {{AUTOR}}.{{NEWSLETTER}}"

    assert contenido.reemplazar_marcadores(texto, _config()) == "Lo escribió el autor del curso."
    assert contenido.reemplazar_marcadores(texto, None) == "Lo escribió el autor del curso."
    assert contenido.reemplazar_marcadores(texto, _config("   ", "  ")) == "Lo escribió el autor del curso."


def test_no_toca_los_demas_marcadores():
    texto = "{{AUTOR}} · {{AYUDA}} · {{URL_CURSO}} · {{ENLACE_BAJA}} · {{autor}}"

    assert contenido.reemplazar_marcadores(texto, _config("Ana")) == "Ana · {{AYUDA}} · {{URL_CURSO}} · {{ENLACE_BAJA}} · {{autor}}"


def test_valores_del_curso():
    assert contenido.valores_del_curso("Ana", "El boletín") == {"AUTOR": "Ana", "NEWSLETTER": "El boletín"}
    assert contenido.valores_del_curso(None, None) == {"AUTOR": contenido.AUTOR_POR_DEFECTO, "NEWSLETTER": ""}
    assert contenido.AUTOR_POR_DEFECTO == "el autor del curso"
    assert set(contenido.valores_del_curso("", "")) == contenido.MARCADORES_DEL_CURSO == {"AUTOR", "NEWSLETTER"}


TEXTOS_CON_MARCADORES_DEL_CURSO = ("prompts", "web", "legal")


def _textos_del_repo() -> list[Path]:
    rutas = [r for carpeta in TEXTOS_CON_MARCADORES_DEL_CURSO for r in sorted((REPO_CONTENIDO / carpeta).glob("*.md"))]
    return [r for r in rutas if r.name != "pie-mails.md"]  # el pie va con los mails y sus marcadores


def test_los_textos_del_repo_usan_solo_marcadores_que_el_backend_llena():
    import re

    rutas = _textos_del_repo()
    assert rutas
    for ruta in rutas:
        texto = ruta.read_text(encoding="utf-8")
        usados = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", texto))
        sobrantes = usados - contenido.MARCADORES_DEL_CURSO
        assert not sobrantes, f"{ruta.name}: marcadores sin valor: {sobrantes}"
        assert "{{" not in contenido.reemplazar_marcadores(texto, None), ruta.name


class _Conf:
    def __init__(self, autor_nombre="", newsletter_nombre=""):
        self.autor_nombre = autor_nombre
        self.newsletter_nombre = newsletter_nombre


def test_bloque_de_newsletter_se_saca_si_no_hay_newsletter():
    texto = "Antes.\n{{#NEWSLETTER}}\n- **{{NEWSLETTER}}**: novedades de {{AUTOR}}.\n{{/NEWSLETTER}}\nDespués."

    sin = contenido.reemplazar_marcadores(texto, _Conf(autor_nombre="Ana"))
    con = contenido.reemplazar_marcadores(texto, _Conf(autor_nombre="Ana", newsletter_nombre="Substack"))

    assert sin == "Antes.\nDespués."
    assert con == "Antes.\n- **Substack**: novedades de Ana.\nDespués."


def test_bloque_de_newsletter_en_la_misma_linea():
    texto = "Podés cambiarlo.{{#NEWSLETTER}} Si ya te llegan, date de baja en {{NEWSLETTER}}.{{/NEWSLETTER}} Fin."

    assert contenido.reemplazar_marcadores(texto, _Conf()) == "Podés cambiarlo. Fin."
    assert contenido.reemplazar_marcadores(texto, _Conf(newsletter_nombre="X")) == (
        "Podés cambiarlo. Si ya te llegan, date de baja en X. Fin."
    )


def test_textos_legales_sin_newsletter_no_dejan_huecos():
    raiz = Path(__file__).resolve().parents[2] / "contenido"
    for nombre in ("legal/privacidad.md", "legal/consentimientos.md"):
        texto = contenido.reemplazar_marcadores(contenido.leer(raiz, nombre), _Conf(autor_nombre="Ana"))
        _, cuerpo = contenido.separar_frontmatter(texto)
        assert "****" not in cuerpo and " por ." not in cuerpo and "{{" not in cuerpo, nombre
