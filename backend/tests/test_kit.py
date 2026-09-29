"""Armado del kit (contracts/kit.md): estructura, personalización y reglas del zip."""

import io
import json
import re
import stat
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import pytest
import yaml

from vibe_tutor import contenido, kit

BACKEND = Path(__file__).resolve().parents[1]
REPO_CONTENIDO = BACKEND.parent / "contenido"
HOY = date(2026, 10, 1)
DOMINIO = "vibe.ejemplo.test"
IDEA = "# Registro de sueños\n\n## Qué es\n\nUna página para anotar lo que soñé cada mañana.\n"
QUE_SIGUE = "- Compartir los sueños con mi grupo de meditación."
SKILLS = ("guardar-version", "volver-version", "publicar")
LECCIONES = (
    "curso/leccion-4-primera-victoria.md",
    "curso/leccion-5-construir.md",
    "curso/leccion-6-cuando-se-rompe.md",
    "curso/leccion-7-terminar-y-mostrar.md",
)
OBLIGATORIOS = (
    "LEEME.txt",
    "AGENTS.md",
    "CLAUDE.md",
    "mi-idea.md",
    "bitacora.md",
    "cuaderno.md",
    *LECCIONES,
    "curso/machete.md",
    "curso/VERSION",
    "sitio/index.html",
    "versiones/LEEME.txt",
    ".claude/settings.json",
    *(f".claude/skills/{nombre}/SKILL.md" for nombre in SKILLS),
    *(f".agents/skills/{nombre}/SKILL.md" for nombre in SKILLS),
)
MARCADORES = (
    "{{TITULO}}", "{{URL_CURSO}}", "{{URL_AUDIOS}}", "{{HERRAMIENTA}}", "{{SISTEMA}}", "{{FECHA}}", "{{AYUDA}}",
    "{{AUTOR}}", "{{NEWSLETTER}}",
)
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9._/-]+$")
EXTENSIONES_TEXTO = (".md", ".txt", ".html")

MACHETE = [
    {
        "id": "codex-instalar-mac",
        "tema": "instalar",
        "aplica_a": ["codex"],
        "sistema": ["mac"],
        "texto": "Bajá la app de ChatGPT para Mac.",
        "fuente": "https://chatgpt.com/download",
        "verificado": "2026-09-20",
        "probado": False,
    },
    {
        "id": "claude-instalar",
        "tema": "instalar",
        "aplica_a": ["claude"],
        "sistema": ["mac", "windows"],
        "texto": "Bajá la app de escritorio de Claude.",
        "fuente": "https://code.claude.com/docs/en/desktop",
        "verificado": "2026-09-10",
        "probado": False,
    },
    {
        "id": "codex-instalar-windows",
        "tema": "instalar",
        "aplica_a": ["codex"],
        "sistema": ["windows"],
        "texto": "Instalá la app de ChatGPT desde la Microsoft Store.",
        "fuente": "https://learn.chatgpt.com/docs/windows/windows-app",
        "verificado": "2026-09-05",
        "probado": False,
    },
    {
        "id": "ayuda-emergencias",
        "tema": "ayuda",
        "aplica_a": ["codex", "claude"],
        "sistema": ["mac", "windows"],
        "texto": "Si hay riesgo inmediato: 911 en todo el país.",
        "fuente": "https://www.argentina.gob.ar/tema/emergencias",
        "verificado": "2026-09-25",
        "probado": False,
    },
]


def _escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


def crear_plantilla(raiz: Path) -> Path:
    """Arma en raiz un contenido/ de prueba con machete y plantilla del kit; devuelve raiz."""
    _escribir(raiz / "machete.yaml", yaml.safe_dump(MACHETE, allow_unicode=True))
    plantilla = raiz / "kit"
    _escribir(
        plantilla / "AGENTS.md",
        "# Tutor de {{TITULO}}\n\nAntes de responder, leé `bitacora.md` y `mi-idea.md`.\n"
        "Curso: {{URL_CURSO}}. Audios: {{URL_AUDIOS}}.\nHerramienta: {{HERRAMIENTA}} en {{SISTEMA}}.\n\n"
        "## Si la persona está mal\n\nOfrecé estos recursos:\n\n{{AYUDA}}\n",
    )
    _escribir(plantilla / "CLAUDE.md", "@AGENTS.md\n@bitacora.md\n")
    _escribir(plantilla / "curso/autor.md", "Este curso lo armó {{AUTOR}}. Novedades: {{NEWSLETTER}}.\n")
    _escribir(plantilla / "LEEME-codex.txt", "Abrí esta carpeta en la app de ChatGPT, modo {{HERRAMIENTA}}, en tu {{SISTEMA}}.\n")
    _escribir(plantilla / "LEEME-claude.txt", "Abrí esta carpeta en la pestaña Code de {{HERRAMIENTA}}, en tu {{SISTEMA}}.\n")
    _escribir(plantilla / "bitacora.md", "# Bitácora\n\n- Kit armado el {{FECHA}}.\n- Lección actual: 4\n")
    _escribir(plantilla / "cuaderno.md", "# Cuaderno\n\n| Qué pedí | Qué esperaba | Qué pasó |\n|---|---|---|\n")
    _escribir(
        plantilla / "sitio/index.html",
        "<!doctype html>\n<html lang=\"es\"><head><title>{{TITULO}}</title></head>\n"
        "<body><h1>{{TITULO}}</h1></body></html>\n",
    )
    _escribir(plantilla / "versiones/LEEME.txt", "Acá se guardan las versiones de sitio/.\n")
    for numero, leccion in enumerate(LECCIONES, start=4):
        _escribir(plantilla / leccion, f"# Lección {numero}\n\nAudio: {{{{URL_AUDIOS}}}}/modulo-{numero}.mp3\n")
    for nombre in SKILLS:
        _escribir(
            plantilla / "skills" / nombre / "SKILL.md",
            f"---\nname: {nombre}\ndescription: Hace {nombre} dentro de esta carpeta.\n---\n\n"
            f"# {nombre}\n\nEn {{{{HERRAMIENTA}}}}, trabajá solo dentro de esta carpeta.\n",
        )
    _escribir(
        plantilla / "claude-settings.json",
        json.dumps({"permissions": {"defaultMode": "acceptEdits", "ask": ["Bash"]}}, indent=2),
    )
    _escribir(plantilla / ".DS_Store", "basura del Finder")
    return raiz


@pytest.fixture
def raiz(tmp_path) -> Path:
    return crear_plantilla(tmp_path / "contenido")


def _armar(raiz: Path, idea: str = IDEA, que_sigue: str | None = QUE_SIGUE, herramienta="codex", sistema="mac"):
    return kit.armar(raiz, idea, que_sigue, herramienta, sistema, DOMINIO, hoy=HOY)


def _abrir(datos: bytes) -> zipfile.ZipFile:
    return zipfile.ZipFile(io.BytesIO(datos))


def _archivos(datos: bytes) -> dict[str, bytes]:
    """Contenido del zip por ruta relativa a la carpeta raíz."""
    with _abrir(datos) as archivo:
        nombres = [n for n in archivo.namelist() if not n.endswith("/")]
        raices = {n.split("/", 1)[0] for n in nombres}
        assert len(raices) == 1, f"el zip tiene que tener una sola carpeta raíz: {raices}"
        return {n.split("/", 1)[1]: archivo.read(n) for n in nombres}


def _texto(archivos: dict[str, bytes], ruta: str) -> str:
    return archivos[ruta].decode("utf-8")


def _chequear_contrato(datos: bytes, nombre_zip: str) -> dict[str, bytes]:
    """Reglas de contracts/kit.md que valen para cualquier plantilla."""
    raiz_zip = nombre_zip.removesuffix(".zip")
    assert re.fullmatch(r"mi-proyecto-[a-z0-9]+(?:-[a-z0-9]+)*", raiz_zip)
    with _abrir(datos) as archivo:
        assert archivo.testzip() is None
        for info in archivo.infolist():
            assert info.filename.startswith(f"{raiz_zip}/"), info.filename
            assert NOMBRE_VALIDO.fullmatch(info.filename), f"nombre con acentos o espacios: {info.filename}"
            modo = info.external_attr >> 16
            assert not stat.S_ISLNK(modo), f"enlace simbólico: {info.filename}"
            if not info.is_dir():
                assert stat.S_ISREG(modo), f"no es un archivo común: {info.filename}"
    archivos = _archivos(datos)
    faltantes = [ruta for ruta in OBLIGATORIOS if ruta not in archivos]
    assert not faltantes, f"faltan en el kit: {faltantes}"
    for nombre in SKILLS:
        claude = archivos[f".claude/skills/{nombre}/SKILL.md"]
        assert claude == archivos[f".agents/skills/{nombre}/SKILL.md"], nombre
        frontmatter, cuerpo = contenido.separar_frontmatter(claude.decode("utf-8"))
        assert set(frontmatter) == {"name", "description"}, nombre
        assert frontmatter["name"] == nombre
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", frontmatter["name"])
        assert str(frontmatter["description"]).strip()
        assert cuerpo.strip()
    agents = archivos["AGENTS.md"]
    assert len(agents) < 8 * 1024
    assert len(agents.decode("utf-8").splitlines()) < 200
    assert len(_texto(archivos, "bitacora.md").splitlines()) < 40
    json.loads(archivos[".claude/settings.json"])
    for ruta, bytes_ in archivos.items():
        if ruta.endswith(EXTENSIONES_TEXTO) and ruta != "mi-idea.md":
            texto = bytes_.decode("utf-8")
            for marcador in MARCADORES:
                assert marcador not in texto, f"{ruta} quedó con {marcador}"
    return archivos


def test_arma_el_kit_con_los_archivos_obligatorios(raiz):
    datos, nombre, _ = _armar(raiz)

    assert nombre == "mi-proyecto-registro-de-suenos.zip"
    archivos = _chequear_contrato(datos, nombre)
    with _abrir(datos) as archivo:
        assert all(n.startswith("mi-proyecto-registro-de-suenos/") for n in archivo.namelist())
    for sobrante in ("LEEME-codex.txt", "LEEME-claude.txt", "claude-settings.json", ".DS_Store", "skills/publicar/SKILL.md"):
        assert sobrante not in archivos


def test_mi_idea_es_la_del_alumno_con_que_sigue(raiz):
    archivos = _archivos(_armar(raiz)[0])

    mi_idea = _texto(archivos, "mi-idea.md")
    assert mi_idea.startswith("# Registro de sueños")
    assert "Una página para anotar lo que soñé cada mañana." in mi_idea
    assert "## Qué sigue" in mi_idea
    assert mi_idea.index("## Qué sigue") < mi_idea.index(QUE_SIGUE)


def test_mi_idea_sin_que_sigue_deja_la_seccion_para_completar(raiz):
    archivos = _archivos(_armar(raiz, que_sigue=None)[0])

    assert _texto(archivos, "mi-idea.md").count("## Qué sigue") == 1


def test_mi_idea_no_repite_que_sigue_si_la_idea_ya_lo_trae(raiz):
    idea = IDEA + "\n## Qué sigue\n\n- Una app para el celular.\n"

    archivos = _archivos(_armar(raiz, idea=idea, que_sigue=None)[0])

    assert _texto(archivos, "mi-idea.md").count("## Qué sigue") == 1


def test_mi_idea_md_para_descargar():
    texto = kit.mi_idea("# Mi idea\n\nAlgo chico.", "## Qué sigue\n\n- Algo grande.")

    assert texto == "# Mi idea\n\nAlgo chico.\n\n## Qué sigue\n\n- Algo grande.\n"


def test_skills_identicas_en_claude_y_agents_sin_enlaces(raiz):
    datos, _, _ = _armar(raiz)
    archivos = _archivos(datos)

    for nombre in SKILLS:
        assert archivos[f".claude/skills/{nombre}/SKILL.md"] == archivos[f".agents/skills/{nombre}/SKILL.md"]
    with _abrir(datos) as archivo:
        assert not any(stat.S_ISLNK(info.external_attr >> 16) for info in archivo.infolist())


def test_skills_con_frontmatter_solo_name_y_description(raiz):
    archivos = _archivos(_armar(raiz)[0])

    for nombre in SKILLS:
        frontmatter, _ = contenido.separar_frontmatter(_texto(archivos, f".claude/skills/{nombre}/SKILL.md"))
        assert frontmatter == {"name": nombre, "description": f"Hace {nombre} dentro de esta carpeta."}


def test_los_permisos_de_claude_van_a_claude_settings(raiz):
    archivos = _archivos(_armar(raiz)[0])

    assert json.loads(archivos[".claude/settings.json"]) == {
        "permissions": {"defaultMode": "acceptEdits", "ask": ["Bash"]}
    }


@pytest.mark.parametrize(
    ("herramienta", "sistema", "esperado"),
    [
        ("codex", "mac", "Abrí esta carpeta en la app de ChatGPT, modo Codex, en tu Mac.\n"),
        ("claude", "windows", "Abrí esta carpeta en la pestaña Code de Claude, en tu Windows.\n"),
    ],
)
def test_leeme_de_la_herramienta_elegida(raiz, herramienta, sistema, esperado):
    archivos = _archivos(_armar(raiz, herramienta=herramienta, sistema=sistema)[0])

    assert _texto(archivos, "LEEME.txt") == esperado


def test_reemplaza_los_marcadores(raiz):
    archivos = _archivos(_armar(raiz)[0])

    agents = _texto(archivos, "AGENTS.md")
    assert agents.startswith("# Tutor de Registro de sueños\n")
    assert "Curso: https://vibe.ejemplo.test. Audios: https://vibe.ejemplo.test/audios." in agents
    assert "Herramienta: Codex en Mac." in agents
    assert "Kit armado el 2026-10-01." in _texto(archivos, "bitacora.md")
    assert "https://vibe.ejemplo.test/audios/modulo-5.mp3" in _texto(archivos, "curso/leccion-5-construir.md")
    assert "En Codex, trabajá solo" in _texto(archivos, ".agents/skills/publicar/SKILL.md")
    assert "<title>Registro de sueños</title>" in _texto(archivos, "sitio/index.html")
    for ruta, bytes_ in archivos.items():
        if ruta.endswith(EXTENSIONES_TEXTO):
            assert "{{" not in bytes_.decode("utf-8"), ruta


def test_reemplaza_autor_y_newsletter(raiz):
    datos, _, _ = kit.armar(
        raiz, IDEA, None, "codex", "mac", DOMINIO, hoy=HOY, autor="Ana & Beto", newsletter="El boletín de Ana"
    )
    archivos = _archivos(datos)

    assert _texto(archivos, "curso/autor.md") == "Este curso lo armó Ana & Beto. Novedades: El boletín de Ana.\n"


def test_sin_autor_dice_el_autor_del_curso(raiz):
    archivos = _archivos(_armar(raiz)[0])

    assert _texto(archivos, "curso/autor.md") == "Este curso lo armó el autor del curso. Novedades: .\n"


def test_el_autor_se_escapa_en_el_html(raiz):
    _escribir(raiz / "kit/sitio/index.html", "<p>Curso de {{AUTOR}}</p>\n")

    datos, _, _ = kit.armar(raiz, IDEA, None, "codex", "mac", DOMINIO, hoy=HOY, autor="<b>Ana</b>")

    assert _texto(_archivos(datos), "sitio/index.html") == "<p>Curso de &lt;b&gt;Ana&lt;/b&gt;</p>\n"


def test_el_dominio_por_defecto_es_el_de_desarrollo_local():
    assert kit.DOMINIO_POR_DEFECTO == "localhost:5173"


@pytest.mark.parametrize(
    ("dominio", "url"),
    [
        ("localhost:5173", "http://localhost:5173"),
        ("http://127.0.0.1:8000/", "http://127.0.0.1:8000"),
        ("localhost", "http://localhost"),
        ("curso.example.test", "https://curso.example.test"),
        ("http://curso.example.test", "https://curso.example.test"),
        ("localhost.example.test", "https://localhost.example.test"),
    ],
)
def test_url_del_curso(dominio, url):
    assert kit.url_del_curso(dominio) == url


def test_linea_de_comandos_sin_dominio_usa_el_local(raiz, tmp_path, monkeypatch):
    monkeypatch.delenv("DOMINIO", raising=False)
    monkeypatch.delenv("AUTOR_NOMBRE", raising=False)
    monkeypatch.delenv("NEWSLETTER_NOMBRE", raising=False)
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")
    salida = tmp_path / "kit.zip"

    kit.main(["--idea", str(idea), "--herramienta", "codex", "--sistema", "mac", "--salida", str(salida),
              "--contenido", str(raiz)])

    archivos = _archivos(salida.read_bytes())
    assert "Curso: http://localhost:5173. Audios: http://localhost:5173/audios." in _texto(archivos, "AGENTS.md")
    assert "lo armó el autor del curso" in _texto(archivos, "curso/autor.md")


def test_linea_de_comandos_con_autor_y_newsletter(raiz, tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOR_NOMBRE", "Beto")
    monkeypatch.setenv("NEWSLETTER_NOMBRE", "Las novedades de Beto")
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")

    kit.main(["--idea", str(idea), "--herramienta", "codex", "--sistema", "mac", "--salida", str(tmp_path / "a.zip"),
              "--contenido", str(raiz), "--dominio", DOMINIO])
    kit.main(["--idea", str(idea), "--herramienta", "codex", "--sistema", "mac", "--salida", str(tmp_path / "b.zip"),
              "--contenido", str(raiz), "--dominio", DOMINIO, "--autor", "Ana", "--newsletter", "El boletín"])

    del_entorno = _texto(_archivos((tmp_path / "a.zip").read_bytes()), "curso/autor.md")
    de_la_linea = _texto(_archivos((tmp_path / "b.zip").read_bytes()), "curso/autor.md")
    assert del_entorno == "Este curso lo armó Beto. Novedades: Las novedades de Beto.\n"
    assert de_la_linea == "Este curso lo armó Ana. Novedades: El boletín.\n"


def test_el_dominio_puede_venir_con_https_y_barra(raiz):
    datos, _, _ = kit.armar(raiz, IDEA, None, "codex", "mac", "https://vibe.ejemplo.test/", hoy=HOY)

    assert "Curso: https://vibe.ejemplo.test. Audios: https://vibe.ejemplo.test/audios." in _texto(
        _archivos(datos), "AGENTS.md"
    )


def test_no_reemplaza_marcadores_dentro_de_la_idea(raiz):
    idea = "# Mi web\n\nQuiero que diga {{FECHA}} tal cual."

    archivos = _archivos(_armar(raiz, idea=idea)[0])

    assert "{{FECHA}}" in _texto(archivos, "mi-idea.md")


def test_el_titulo_se_escapa_en_el_html(raiz):
    idea = "# <b>Hola</b> & chau\n\nUna idea."

    archivos = _archivos(_armar(raiz, idea=idea)[0])

    html = _texto(archivos, "sitio/index.html")
    assert "<title>&lt;b&gt;Hola&lt;/b&gt; &amp; chau</title>" in html
    assert "<b>Hola</b>" not in html
    assert "# Tutor de <b>Hola</b> & chau" in _texto(archivos, "AGENTS.md")


def test_machete_filtrado_por_herramienta_y_sistema_con_fuente_y_fecha(raiz):
    archivos = _archivos(_armar(raiz, herramienta="codex", sistema="mac")[0])

    machete = _texto(archivos, "curso/machete.md")
    assert "Bajá la app de ChatGPT para Mac." in machete
    assert "Si hay riesgo inmediato: 911 en todo el país." in machete
    assert "https://chatgpt.com/download" in machete
    assert "2026-09-20" in machete
    assert "Bajá la app de escritorio de Claude." not in machete
    assert "Microsoft Store" not in machete


def test_machete_le_habla_a_la_persona_y_la_ayuda_va_sin_la_marca_de_probado(raiz):
    machete = _texto(_archivos(_armar(raiz, herramienta="codex", sistema="mac")[0]), "curso/machete.md")

    introduccion = machete.split("\n## ", 1)[0]
    assert "a la persona" not in introduccion
    assert "tu pantalla" in introduccion
    secciones = {bloque.split("\n", 1)[0]: bloque for bloque in machete.split("\n## ")[1:]}
    assert "Probado en la realidad: todavía no" in secciones[kit.TITULOS_TEMAS["instalar"]]
    ayuda = secciones[kit.TITULOS_TEMAS["ayuda"]]
    assert "Si hay riesgo inmediato: 911 en todo el país." in ayuda
    assert "Verificado: 2026-09-25" in ayuda
    assert "Probado" not in ayuda


def test_agents_trae_la_ayuda_del_machete_con_su_fecha(raiz):
    agents = _texto(_archivos(_armar(raiz)[0]), "AGENTS.md")

    assert "- Si hay riesgo inmediato: 911 en todo el país." in agents
    assert "25/9/2026" in agents
    assert "{{AYUDA}}" not in agents


def test_agents_con_la_marca_de_ayuda_y_sin_datos_de_ayuda_no_arma(raiz):
    sin_ayuda = [dato for dato in MACHETE if dato["tema"] != "ayuda"]
    (raiz / "machete.yaml").write_text(yaml.safe_dump(sin_ayuda, allow_unicode=True), encoding="utf-8")

    with pytest.raises(contenido.ErrorContenido, match="ayuda"):
        _armar(raiz)


def test_version_con_la_fecha_mas_vieja_del_machete_filtrado(raiz):
    datos, _, metadatos = _armar(raiz, herramienta="codex", sistema="mac")

    assert metadatos == {"version_curso": "desarrollo", "fecha_machete": "2026-09-20"}
    version = _texto(_archivos(datos), "curso/VERSION")
    assert "desarrollo" in version
    assert "2026-09-20" in version
    assert "2026-09-05" not in version


def test_version_del_curso_sale_de_contenido_version(raiz):
    (raiz / "VERSION").write_text("2026-10-01+abc1234\n", encoding="utf-8")

    datos, _, metadatos = _armar(raiz, herramienta="claude", sistema="windows")

    assert metadatos == {"version_curso": "2026-10-01+abc1234", "fecha_machete": "2026-09-10"}
    assert "2026-10-01+abc1234" in _texto(_archivos(datos), "curso/VERSION")


def test_nombres_sin_acentos_ni_espacios(raiz):
    datos, nombre, _ = _armar(raiz, idea="# ¡Mi Página de Ñandúes!\n\nAlgo.")

    assert nombre == "mi-proyecto-mi-pagina-de-nandues.zip"
    with _abrir(datos) as archivo:
        assert all(NOMBRE_VALIDO.fullmatch(n) for n in archivo.namelist())


@pytest.mark.parametrize(
    ("idea", "titulo", "slug"),
    [
        ("# Registro de sueños\n\nAlgo.", "Registro de sueños", "registro-de-suenos"),
        ("Intro sin título\n\n## Qué es\n\n# Recetas de la abuela\n", "Recetas de la abuela", "recetas-de-la-abuela"),
        ("## Solo subtítulos\n\nNada.", "Mi idea", "mi-idea"),
        ("#   **Mapa  de  bares**  \n", "Mapa de bares", "mapa-de-bares"),
        ("# !!!\n", "!!!", "mi-idea"),
    ],
)
def test_titulo_y_slug_de_la_idea(idea, titulo, slug):
    assert kit.titulo_de(idea) == titulo
    assert kit.slug(kit.titulo_de(idea)) == slug


def test_slug_largo_se_corta_sin_guion_al_final():
    resultado = kit.slug("Una idea con un nombre larguísimo que no entra en ningún lado de verdad")

    assert len(resultado) <= 40
    assert not resultado.endswith("-")
    assert resultado.startswith("una-idea-con-un-nombre")


def test_el_zip_es_el_mismo_para_los_mismos_datos(raiz):
    assert _armar(raiz)[0] == _armar(raiz)[0]


@pytest.mark.parametrize(("herramienta", "sistema"), [("cursor", "mac"), ("codex", "otro"), ("claude", "linux")])
def test_herramienta_o_sistema_invalidos(raiz, herramienta, sistema):
    with pytest.raises(kit.ErrorKit):
        _armar(raiz, herramienta=herramienta, sistema=sistema)


def test_sin_plantilla_no_arma(tmp_path):
    raiz = tmp_path / "contenido"
    _escribir(raiz / "machete.yaml", yaml.safe_dump(MACHETE, allow_unicode=True))

    with pytest.raises(contenido.ErrorContenido):
        _armar(raiz)


def test_sin_datos_del_machete_para_ese_camino_no_arma(raiz):
    (raiz / "machete.yaml").write_text(yaml.safe_dump(MACHETE[:1], allow_unicode=True), encoding="utf-8")

    with pytest.raises(contenido.ErrorContenido):
        _armar(raiz, herramienta="claude", sistema="windows")


def test_linea_de_comandos(raiz, tmp_path, capsys):
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")
    salida = tmp_path / "kit.zip"

    codigo = kit.main(
        ["--idea", str(idea), "--herramienta", "claude", "--sistema", "windows", "--salida", str(salida),
         "--contenido", str(raiz), "--dominio", DOMINIO]
    )

    assert codigo == 0
    archivos = _chequear_contrato(salida.read_bytes(), "mi-proyecto-registro-de-suenos.zip")
    assert "Una página para anotar lo que soñé" in _texto(archivos, "mi-idea.md")
    assert "Claude" in _texto(archivos, "LEEME.txt")
    assert str(salida) in capsys.readouterr().out


def test_linea_de_comandos_con_una_carpeta_de_salida(raiz, tmp_path):
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")
    carpeta = tmp_path / "kits"
    carpeta.mkdir()

    kit.main(["--idea", str(idea), "--herramienta", "codex", "--sistema", "mac", "--salida", str(carpeta),
              "--contenido", str(raiz)])

    assert (carpeta / "mi-proyecto-registro-de-suenos.zip").is_file()


def test_se_corre_como_modulo(raiz, tmp_path):
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")
    salida = tmp_path / "kit.zip"

    resultado = subprocess.run(
        [sys.executable, "-m", "vibe_tutor.kit", "--idea", str(idea), "--herramienta", "codex",
         "--sistema", "mac", "--salida", str(salida), "--contenido", str(raiz), "--dominio", DOMINIO],
        cwd=BACKEND, capture_output=True, text=True, timeout=60,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert zipfile.is_zipfile(salida)


def test_linea_de_comandos_con_datos_invalidos_avisa(raiz, tmp_path, capsys):
    idea = tmp_path / "idea.md"
    idea.write_text(IDEA, encoding="utf-8")

    with pytest.raises(SystemExit) as salida:
        kit.main(["--idea", str(idea), "--herramienta", "codex", "--sistema", "mac", "--salida",
                  str(tmp_path / "kit.zip"), "--contenido", str(tmp_path / "no-existe")])

    assert salida.value.code != 0
    assert "no existe" in capsys.readouterr().err


@pytest.mark.skipif(
    not (REPO_CONTENIDO / "kit" / "AGENTS.md").exists(), reason="la plantilla real del kit todavía no está escrita"
)
@pytest.mark.parametrize(("herramienta", "sistema"), [("codex", "mac"), ("codex", "windows"), ("claude", "mac"), ("claude", "windows")])
def test_kit_con_la_plantilla_real_del_repo(herramienta, sistema):
    datos, nombre, metadatos = kit.armar(REPO_CONTENIDO, IDEA, QUE_SIGUE, herramienta, sistema, DOMINIO)

    archivos = _chequear_contrato(datos, nombre)
    assert "{{" not in "".join(
        b.decode("utf-8") for r, b in archivos.items() if r.endswith(EXTENSIONES_TEXTO) and r != "mi-idea.md"
    )
    claude_md = _texto(archivos, "CLAUDE.md")
    assert "@AGENTS.md" in claude_md and "@bitacora.md" in claude_md
    agents = _texto(archivos, "AGENTS.md")
    assert "`bitacora.md`" in agents
    assert "@bitacora.md" not in agents
    assert _texto(archivos, "mi-idea.md").startswith("# Registro de sueños")
    assert metadatos["fecha_machete"] in _texto(archivos, "curso/VERSION")


@pytest.mark.parametrize(("herramienta", "sistema"), [("codex", "mac"), ("claude", "windows")])
def test_agents_real_trae_la_ayuda_del_machete_real(herramienta, sistema):
    plantilla = (REPO_CONTENIDO / "kit" / "AGENTS.md").read_text(encoding="utf-8")
    assert plantilla.count("{{AYUDA}}") == 1
    assert "0800" not in plantilla and "911" not in plantilla.replace("{{AYUDA}}", "")

    datos, _, _ = kit.armar(REPO_CONTENIDO, IDEA, QUE_SIGUE, herramienta, sistema, DOMINIO)

    agents = _texto(_archivos(datos), "AGENTS.md")
    ayuda = [d for d in contenido.cargar_machete(REPO_CONTENIDO) if d.tema == "ayuda"]
    assert ayuda
    for dato in ayuda:
        assert " ".join(dato.texto.split()) in " ".join(agents.split()), dato.id
    mas_vieja = min(d.verificado for d in ayuda)
    assert f"{mas_vieja.day}/{mas_vieja.month}/{mas_vieja.year}" in agents
    assert "no lo anotes en ningún archivo" in agents.lower()
    assert len(agents.encode("utf-8")) < 8 * 1024
    assert len(agents.splitlines()) < 200


# --- Los pasos para abrir el kit, en la web (pantalla "Cómo seguir en tu computadora") ---

LEEME_DE_PRUEBA = """TU CARPETA DEL CURSO: {{TITULO}}

Kit armado el {{FECHA}}, para {{HERRAMIENTA}} en una computadora con {{SISTEMA}}.


ANTES DE EMPEZAR

1. Guardá esta carpeta en un lugar fijo.
   - En Mac: abrí el Finder.
2. No borres nada de lo que hay adentro.


CÓMO ABRIRLA EN CLAUDE

Abrí la app.


LA PRIMERA VEZ

1. Para comprobar que la app anda escribí: hola, probando
   La app tiene que contestar que anda.
2. Para arrancar, escribí: empecemos

Cuando la app vuelva a contestar, escribí: sigamos
"""


def test_leeme_a_markdown_pone_los_titulos_en_minuscula_con_los_nombres_propios():
    texto = kit.leeme_a_markdown(LEEME_DE_PRUEBA)

    assert "## Antes de empezar" in texto
    assert "## Cómo abrirla en Claude" in texto
    assert "## La primera vez" in texto
    assert "ANTES DE EMPEZAR" not in texto


def test_leeme_a_markdown_saca_la_primera_linea_con_el_titulo_de_la_idea():
    texto = kit.leeme_a_markdown(LEEME_DE_PRUEBA)

    assert "TU CARPETA DEL CURSO" not in texto
    assert texto.lstrip().startswith("Kit armado el {{FECHA}}")


def test_leeme_a_markdown_marca_lo_que_hay_que_escribir():
    texto = kit.leeme_a_markdown(LEEME_DE_PRUEBA)

    assert "escribí: `hola, probando`" in texto
    assert "escribí: `empecemos`" in texto
    assert "escribí: `sigamos`" in texto


def test_leeme_a_markdown_no_toca_las_listas_ni_el_resto():
    texto = kit.leeme_a_markdown(LEEME_DE_PRUEBA)

    assert "1. Guardá esta carpeta en un lugar fijo.\n   - En Mac: abrí el Finder.\n2. No borres nada" in texto
    assert "La app tiene que contestar que anda." in texto


def test_leeme_a_markdown_no_toma_una_frase_en_mayusculas_dentro_de_un_parrafo_por_titulo():
    texto = kit.leeme_a_markdown("Intro.\n\nEsto NO es un título\nNI ESTO tampoco, porque sigue texto\n")

    assert "##" not in texto


def test_pasos_no_dice_cuando_se_armo_el_kit(raiz):
    (raiz / "kit/LEEME-codex.txt").write_text(
        "TU CARPETA: {{TITULO}}\n\nKit armado el {{FECHA}}, para {{HERRAMIENTA}} en una computadora con {{SISTEMA}}.\n",
        encoding="utf-8",
    )

    texto = kit.pasos(raiz, "codex", "mac", DOMINIO, hoy=HOY)["texto_md"]

    assert texto.strip() == "Los pasos para Codex en una computadora con Mac."


def test_pasos_de_la_herramienta_y_la_computadora_elegidas(raiz):
    pasos = kit.pasos(raiz, "claude", "windows", DOMINIO, hoy=HOY)

    assert pasos["herramienta"] == "claude"
    assert pasos["sistema"] == "windows"
    assert set(pasos) == {"herramienta", "sistema", "texto_md"}
    assert "{{" not in pasos["texto_md"]


@pytest.mark.parametrize(("herramienta", "sistema"), [("codex", "mac"), ("codex", "windows"), ("claude", "mac"), ("claude", "windows")])
def test_pasos_con_la_plantilla_real_del_repo(herramienta, sistema):
    pasos = kit.pasos(REPO_CONTENIDO, herramienta, sistema, DOMINIO, hoy=HOY)
    texto = pasos["texto_md"]

    nombre = kit.HERRAMIENTAS[herramienta]
    assert "{{" not in texto
    assert f"## Cómo abrirla en {nombre}" in texto
    for titulo in ("## Antes de empezar", "## La primera vez", "## Cómo seguir otro día", "## Permisos", "## Nunca"):
        assert titulo in texto, titulo
    assert "`empecemos`" in texto and "`sigamos`" in texto
    assert kit.SISTEMAS[sistema] in texto
    # "Kit armado el <fecha>" es del zip: en la web, esa fecha sería la de hoy y no la de la descarga.
    assert "Kit armado" not in texto
    assert texto.lstrip().startswith(f"Los pasos para {nombre}")
    # Es el mismo texto que el LEEME.txt del kit: lo que se dice de la otra herramienta no aparece.
    otra = kit.HERRAMIENTAS["codex" if herramienta == "claude" else "claude"]
    assert f"Cómo abrirla en {otra}" not in texto


def test_pasos_sale_del_mismo_archivo_que_el_leeme_del_kit(raiz):
    """Un solo texto: si se cambia el LEEME de la plantilla, cambian el kit y la pantalla."""
    (raiz / "kit/LEEME-codex.txt").write_text(
        "TU CARPETA: {{TITULO}}\n\nUNA FRASE ÚNICA DE PRUEBA para {{HERRAMIENTA}}.\n", encoding="utf-8"
    )

    en_el_kit = _texto(_archivos(_armar(raiz)[0]), "LEEME.txt")
    en_la_web = kit.pasos(raiz, "codex", "mac", DOMINIO, hoy=HOY)["texto_md"]

    assert "UNA FRASE ÚNICA DE PRUEBA para Codex." in en_el_kit
    assert "UNA FRASE ÚNICA DE PRUEBA para Codex." in en_la_web


@pytest.mark.parametrize(("herramienta", "sistema"), [("cursor", "mac"), ("codex", "linux"), ("codex", "otro")])
def test_pasos_con_herramienta_o_sistema_invalidos(raiz, herramienta, sistema):
    with pytest.raises(kit.ErrorKit):
        kit.pasos(raiz, herramienta, sistema, DOMINIO, hoy=HOY)


def test_pasos_sin_el_leeme_de_la_herramienta_avisa(raiz):
    (raiz / "kit/LEEME-codex.txt").unlink()

    with pytest.raises(contenido.ErrorContenido):
        kit.pasos(raiz, "codex", "mac", DOMINIO, hoy=HOY)


def test_pasos_llena_el_autor_del_curso(raiz):
    (raiz / "kit/LEEME-codex.txt").write_text("TU CARPETA: {{TITULO}}\n\nHola {{AUTOR}}.\n", encoding="utf-8")

    pasos = kit.pasos(raiz, "codex", "mac", DOMINIO, hoy=HOY, autor="Ana")

    assert "Hola Ana." in pasos["texto_md"]
