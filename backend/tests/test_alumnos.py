"""Endpoints del alumno (contracts/api.md): estado, guía escrita, idea, taller, kit, links y datos."""

import io
import json
import zipfile
from pathlib import Path

import pytest
import yaml

from vibe_tutor import alumnos, auth, costos, dominio, mails

MAIL = "ana@example.com"
IDEA = "# Registro de sueños\n\nUna página para anotar lo que soñé."
SKILLS = ("guardar-version", "volver-version", "publicar")
MACHETE = [
    {
        "id": "publicar-netlify-drop",
        "tema": "publicar",
        "aplica_a": ["codex", "claude"],
        "sistema": ["mac", "windows"],
        "texto": "Abrí la página de Netlify Drop y arrastrá la carpeta sitio.",
        "fuente": "https://docs.netlify.com/",
        "verificado": "2026-09-20",
        "probado": False,
    }
]


def _escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")


@pytest.fixture
def raiz(settings_tmp) -> Path:
    """Contenido de prueba: guías, textos legales, machete y una plantilla mínima del kit."""
    raiz = settings_tmp.contenido_dir
    for n in (1, 2, 3):
        _escribir(raiz / f"web/guia-modulo-{n}.md", f"---\ntitulo: Módulo {n} por escrito\nestado: borrador\n---\n\n# Guía {n}\n\nPaso a paso.\n")
    _escribir(
        raiz / "legal/privacidad.md",
        "---\nversion: 2026-10-01\ntitulo: Aviso de privacidad\nestado: borrador\n---\n\n# Privacidad\n\nQué guardamos.\n",
    )
    _escribir(
        raiz / "legal/consentimientos.md",
        "---\nversion: 2026-10-01\nmails_curso: Acepto recibir los mails del curso.\n"
        "transferencia: Acepto que mis datos se procesen en Estados Unidos.\n"
        "novedades: Quiero recibir las novedades de {{AUTOR}} por {{NEWSLETTER}}.\nestado: borrador\n---\n\n"
        "# Consentimientos\n\nDetalle de {{AUTOR}}.\n",
    )
    _escribir(raiz / "machete.yaml", yaml.safe_dump(MACHETE, allow_unicode=True))
    kit = raiz / "kit"
    for ruta in ("AGENTS.md", "CLAUDE.md", "bitacora.md", "cuaderno.md", "versiones/LEEME.txt"):
        _escribir(kit / ruta, f"{ruta} de {{{{TITULO}}}}\n")
    _escribir(kit / "LEEME-codex.txt", "Abrí la carpeta en {{HERRAMIENTA}}.\n")
    _escribir(kit / "LEEME-claude.txt", "Abrí la carpeta en {{HERRAMIENTA}}.\n")
    _escribir(kit / "sitio/index.html", "<title>{{TITULO}}</title>\n")
    _escribir(kit / "claude-settings.json", "{}\n")
    for nombre in SKILLS:
        _escribir(kit / f"skills/{nombre}/SKILL.md", f"---\nname: {nombre}\ndescription: Prueba.\n---\n\nPasos.\n")
    return raiz


@pytest.fixture
def mails_enviados(monkeypatch):
    enviados = []

    async def falso(settings, alumno_id, tipo, clave, datos=None):
        enviados.append((alumno_id, tipo, clave, datos))
        return "enviado"

    monkeypatch.setattr(mails, "enviar", falso)
    return enviados


@pytest.fixture
def cliente(hacer_cliente, raiz, mails_enviados):
    return hacer_cliente([alumnos.router], email=MAIL)


@pytest.fixture
def con_autor(settings_tmp):
    """La configuración de un curso con autor y con casilla de novedades."""
    return settings_tmp.model_copy(update={"autor_nombre": "Ana", "newsletter_nombre": "El boletín de Ana"})


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


def _fila(base, sql: str, *parametros):
    return base.execute(sql, parametros).fetchone()


def _con_idea(base, cliente, texto: str = IDEA) -> None:
    dominio.guardar_idea(base, cliente.alumno_id, texto, "- Compartirlo con el grupo.", "tutor")


def _en_modulo(base, cliente, modulo: int) -> None:
    with base:
        base.execute("UPDATE alumnos SET modulo_actual = ? WHERE id = ?", (modulo, cliente.alumno_id))


def _taller(base, cliente, herramienta: str | None, sistema: str | None) -> None:
    with base:
        base.execute(
            "UPDATE alumnos SET herramienta = ?, sistema = ? WHERE id = ?", (herramienta, sistema, cliente.alumno_id)
        )


# --- /yo ---


def test_yo_sin_sesion_da_401(hacer_cliente, raiz):
    respuesta = hacer_cliente([alumnos.router]).get("/api/yo")

    assert respuesta.status_code == 401
    assert "detalle" in respuesta.json()


def test_yo_de_un_alumno_nuevo(cliente):
    respuesta = cliente.get("/api/yo")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "email": MAIL,
        "es_admin": False,
        "modulo_actual": 1,
        "avance": [],
        "idea": None,
        "taller": {"herramienta": None, "sistema": None},
        "tope": {"bloqueado": False, "alcance": None},
        "consentimientos": {"mails_curso": True, "novedades": False},
        "audios": [],
    }


def test_yo_con_avance_idea_taller_y_audios(cliente, base, raiz):
    _con_idea(base, cliente)
    dominio.completar_modulo(base, cliente.alumno_id, 1, "tutor")
    _taller(base, cliente, "codex", "mac")
    _escribir(raiz / "audios/modulo-1.md", "Transcripción.")
    (raiz / "audios/modulo-1.mp3").write_bytes(b"ID3")
    (raiz / "audios/modulo-2.mp3").write_bytes(b"ID3")
    _escribir(raiz / "audios/modulo-3.md", "Transcripción sin audio.")

    datos = cliente.get("/api/yo").json()

    assert datos["modulo_actual"] == 2
    assert [(a["modulo"], a["via"]) for a in datos["avance"]] == [(1, "tutor")]
    assert datos["avance"][0]["completado"]
    assert datos["idea"]["version"] == 1
    assert datos["idea"]["actualizada"]
    assert datos["taller"] == {"herramienta": "codex", "sistema": "mac"}
    assert datos["audios"] == [
        {"modulo": 1, "url": "/audios/modulo-1.mp3", "transcripcion": "/audios/modulo-1.md"},
        {"modulo": 2, "url": "/audios/modulo-2.mp3", "transcripcion": None},
    ]


def test_yo_de_quien_administra(hacer_cliente, raiz):
    datos = hacer_cliente([alumnos.router], email="admin@example.com").get("/api/yo").json()

    assert datos["es_admin"] is True


def test_yo_con_el_tope_del_alumno_alcanzado(cliente, base):
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 1.5, alumno_id=cliente.alumno_id)

    assert cliente.get("/api/yo").json()["tope"] == {"bloqueado": True, "alcance": "alumno"}


def test_yo_registra_la_actividad(cliente, base):
    with base:
        base.execute("UPDATE alumnos SET ultima_actividad = '2026-01-01T00:00:00+00:00' WHERE id = ?", (cliente.alumno_id,))

    cliente.get("/api/yo")

    assert _fila(base, "SELECT ultima_actividad FROM alumnos WHERE id = ?", cliente.alumno_id)[0] > "2026-01-01T00:00:00+00:00"


# --- Guía escrita ---


def test_guia_del_modulo_actual(cliente):
    respuesta = cliente.get("/api/modulos/1/guia")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "modulo": 1,
        "titulo": "Módulo 1 por escrito",
        "guia_md": "# Guía 1\n\nPaso a paso.\n",
        "audio": None,
    }


def test_guia_reemplaza_autor_y_newsletter(hacer_cliente, raiz, con_autor):
    _escribir(
        raiz / "web/guia-modulo-1.md",
        "---\ntitulo: Lo que armó {{AUTOR}}\n---\n\n# Guía\n\nEste curso lo hizo {{AUTOR}}. Novedades: {{NEWSLETTER}}.\n",
    )

    con_config = hacer_cliente([alumnos.router], email=MAIL, settings=con_autor).get("/api/modulos/1/guia").json()
    sin_config = hacer_cliente([alumnos.router], email=MAIL).get("/api/modulos/1/guia").json()

    assert con_config["titulo"] == "Lo que armó Ana"
    assert con_config["guia_md"] == "# Guía\n\nEste curso lo hizo Ana. Novedades: El boletín de Ana.\n"
    assert sin_config["guia_md"] == "# Guía\n\nEste curso lo hizo el autor del curso. Novedades: .\n"


def test_guia_con_audio(cliente, raiz):
    (raiz / "audios").mkdir()
    (raiz / "audios/modulo-1.mp3").write_bytes(b"ID3")

    assert cliente.get("/api/modulos/1/guia").json()["audio"] == {
        "modulo": 1,
        "url": "/audios/modulo-1.mp3",
        "transcripcion": None,
    }


def test_guia_de_un_modulo_anterior(cliente, base):
    _en_modulo(base, cliente, 3)

    assert cliente.get("/api/modulos/2/guia").status_code == 200


def test_guia_de_un_modulo_que_no_esta_abierto_da_403(cliente):
    respuesta = cliente.get("/api/modulos/2/guia")

    assert respuesta.status_code == 403
    assert respuesta.json()["detalle"]


@pytest.mark.parametrize("modulo", [0, 4, 7])
def test_guia_fuera_de_la_web_da_404(cliente, base, modulo):
    _en_modulo(base, cliente, 7)

    respuesta = cliente.get(f"/api/modulos/{modulo}/guia")

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"]


def test_guia_sin_archivo_da_404_amable(cliente, raiz):
    (raiz / "web/guia-modulo-1.md").unlink()

    respuesta = cliente.get("/api/modulos/1/guia")

    assert respuesta.status_code == 404
    assert "todavía" in respuesta.json()["detalle"]


def test_guia_sin_titulo_usa_el_nombre_del_modulo(cliente, raiz):
    _escribir(raiz / "web/guia-modulo-1.md", "# Sin frontmatter\n")

    assert cliente.get("/api/modulos/1/guia").json()["titulo"] == "Módulo 1"


# --- Plantilla de la idea ---


def test_plantilla_de_la_idea(cliente, raiz):
    _escribir(
        raiz / "web/plantilla-idea.md",
        "---\nestado: borrador\n---\n\n# El nombre de tu idea\n\n## Qué es\n\nEn una o dos frases.\n",
    )

    respuesta = cliente.get("/api/idea/plantilla")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"texto_md": "# El nombre de tu idea\n\n## Qué es\n\nEn una o dos frases.\n"}


def test_plantilla_de_la_idea_reemplaza_el_autor(hacer_cliente, raiz, con_autor):
    _escribir(raiz / "web/plantilla-idea.md", "# El nombre de tu idea\n\nComo en los ejemplos de {{AUTOR}}.\n")

    respuesta = hacer_cliente([alumnos.router], email=MAIL, settings=con_autor).get("/api/idea/plantilla")

    assert respuesta.json() == {"texto_md": "# El nombre de tu idea\n\nComo en los ejemplos de Ana.\n"}


def test_plantilla_de_la_idea_sin_archivo_da_404_amable(cliente):
    respuesta = cliente.get("/api/idea/plantilla")

    assert respuesta.status_code == 404
    assert "todavía" in respuesta.json()["detalle"]


def test_plantilla_de_la_idea_pide_sesion(hacer_cliente, raiz):
    assert hacer_cliente([alumnos.router]).get("/api/idea/plantilla").status_code == 401


# --- Datos del día en la guía del módulo 3 ---

MACHETE_GUIA = [
    {"id": "codex-planes", "tema": "planes", "aplica_a": ["codex"], "sistema": ["mac", "windows"],
     "texto": "El plan Plus de ChatGPT cuesta US$20.", "fuente": "https://chatgpt.com/pricing",
     "verificado": "2026-09-20", "probado": False},
    {"id": "claude-planes", "tema": "planes", "aplica_a": ["claude"], "sistema": ["mac", "windows"],
     "texto": "El plan Pro de Claude cuesta US$20.", "fuente": "https://claude.com/pricing",
     "verificado": "2026-09-21", "probado": False},
    {"id": "codex-instalar-mac", "tema": "instalar", "aplica_a": ["codex"], "sistema": ["mac"],
     "texto": "Bajá la app de ChatGPT para Mac.", "fuente": "https://chatgpt.com/download",
     "verificado": "2026-09-22", "probado": False},
    {"id": "codex-instalar-windows", "tema": "instalar", "aplica_a": ["codex"], "sistema": ["windows"],
     "texto": "Instalá la app desde la Microsoft Store.", "fuente": "https://apps.microsoft.com/",
     "verificado": "2026-09-23", "probado": False},
    {"id": "ver-codex", "tema": "ver", "aplica_a": ["codex"], "sistema": ["mac", "windows"],
     "texto": "Doble clic en sitio/index.html.", "fuente": "https://learn.chatgpt.com/docs/browser",
     "verificado": "2026-09-24", "probado": False},
    {"id": "publicar-netlify-drop", "tema": "publicar", "aplica_a": ["codex", "claude"], "sistema": ["mac", "windows"],
     "texto": "Arrastrá la carpeta sitio a Netlify Drop.", "fuente": "https://app.netlify.com/drop",
     "verificado": "2026-09-25", "probado": False},
    {"id": "limites-netlify", "tema": "limites", "aplica_a": ["codex", "claude"], "sistema": ["mac", "windows"],
     "texto": "Cada publicación usa 15 créditos.", "fuente": "https://docs.netlify.com/",
     "verificado": "2026-09-26", "probado": False},
    {"id": "volver-checkpoints-claude", "tema": "volver-atras", "aplica_a": ["claude"], "sistema": ["mac", "windows"],
     "texto": "Con /rewind se vuelve atrás.", "fuente": "https://code.claude.com/docs/en/checkpointing",
     "verificado": "2026-09-27", "probado": False},
    {"id": "ayuda-emergencias", "tema": "ayuda", "aplica_a": ["codex", "claude"], "sistema": ["mac", "windows"],
     "texto": "Si hay riesgo inmediato: 911.", "fuente": "https://www.argentina.gob.ar/tema/emergencias",
     "verificado": "2026-09-27", "probado": False},
]


@pytest.fixture
def guia_3(cliente, base, raiz):
    _escribir(raiz / "machete.yaml", yaml.safe_dump(MACHETE_GUIA, allow_unicode=True))
    _en_modulo(base, cliente, 3)
    return cliente


def _datos_del_dia(respuesta) -> str:
    assert respuesta.status_code == 200
    guia = respuesta.json()["guia_md"]
    assert guia.startswith("# Guía 3\n\nPaso a paso.\n")
    assert guia.count("## Datos del día") == 1
    return guia.split("## Datos del día", 1)[1]


def test_guia_3_sin_taller_trae_todos_los_datos_del_dia(guia_3):
    datos = _datos_del_dia(guia_3.get("/api/modulos/3/guia"))

    for dato in MACHETE_GUIA:
        if dato["tema"] in ("volver-atras", "ayuda"):
            assert dato["texto"] not in datos, dato["id"]
            continue
        assert dato["texto"] in datos, dato["id"]
        assert dato["fuente"] in datos, dato["id"]
        verificado = dato["verificado"]
        dia, mes = int(verificado[8:]), int(verificado[5:7])
        assert f"{dia}/{mes}/2026" in datos, dato["id"]
    assert datos.index("El plan Plus") < datos.index("Bajá la app") < datos.index("Doble clic") < datos.index("Arrastrá")


def test_guia_3_con_taller_filtra_por_herramienta_y_sistema(guia_3, base):
    _taller(base, guia_3, "codex", "windows")

    datos = _datos_del_dia(guia_3.get("/api/modulos/3/guia"))

    assert "El plan Plus de ChatGPT" in datos
    assert "Instalá la app desde la Microsoft Store." in datos
    assert "Arrastrá la carpeta sitio a Netlify Drop." in datos
    assert "Claude" not in datos
    assert "para Mac" not in datos


def test_guia_3_con_otro_sistema_no_filtra_por_sistema(guia_3, base):
    _taller(base, guia_3, "codex", "otro")

    datos = _datos_del_dia(guia_3.get("/api/modulos/3/guia"))

    assert "para Mac" in datos and "Microsoft Store" in datos
    assert "Claude" not in datos


def test_guia_3_con_el_machete_roto_igual_responde(guia_3, raiz):
    (raiz / "machete.yaml").write_text("- id: roto\n", encoding="utf-8")

    datos = _datos_del_dia(guia_3.get("/api/modulos/3/guia"))

    assert "no" in datos and "disponibles" in datos


def test_las_guias_1_y_2_no_llevan_datos_del_dia(guia_3):
    for n in (1, 2):
        assert "Datos del día" not in guia_3.get(f"/api/modulos/{n}/guia").json()["guia_md"]


# --- Completar con la guía escrita ---


def test_completar_el_modulo_1_con_la_guia(cliente, base):
    respuesta = cliente.post("/api/modulos/1/completar")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"modulo_actual": 2}
    assert _fila(base, "SELECT via FROM avance WHERE alumno_id = ? AND modulo = 1", cliente.alumno_id)[0] == "guia_escrita"
    assert _fila(base, "SELECT detalle FROM eventos WHERE tipo = 'modulo_completo' AND alumno_id = ?", cliente.alumno_id)[0] == "modulo=1"


def test_completar_el_modulo_2_sin_idea_da_409(cliente, base):
    _en_modulo(base, cliente, 2)

    respuesta = cliente.post("/api/modulos/2/completar")

    assert respuesta.status_code == 409
    assert "idea" in respuesta.json()["detalle"]


def test_completar_el_modulo_2_con_idea(cliente, base):
    _en_modulo(base, cliente, 2)
    _con_idea(base, cliente)

    assert cliente.post("/api/modulos/2/completar").json() == {"modulo_actual": 3}


def test_completar_un_modulo_que_no_esta_abierto_da_403(cliente):
    assert cliente.post("/api/modulos/3/completar").status_code == 403


@pytest.mark.parametrize("modulo", [0, 4])
def test_completar_un_modulo_fuera_de_la_web_da_404(cliente, base, modulo):
    _en_modulo(base, cliente, 7)

    assert cliente.post(f"/api/modulos/{modulo}/completar").status_code == 404


def test_completar_el_modulo_3_no_pasa_al_4_sin_el_kit(cliente, base):
    _en_modulo(base, cliente, 3)

    assert cliente.post("/api/modulos/3/completar").json() == {"modulo_actual": 3}


# --- Idea ---


def test_idea_sin_guardar_da_404(cliente):
    assert cliente.get("/api/idea").status_code == 404
    assert cliente.get("/api/idea.md").status_code == 404


def test_editar_la_idea_crea_versiones(cliente, base):
    _con_idea(base, cliente)

    respuesta = cliente.put("/api/idea", json={"texto_md": "# Registro de sueños\n\nAhora con fechas.", "que_sigue_md": ""})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"version": 2}
    idea = cliente.get("/api/idea").json()
    assert idea["version"] == 2
    assert idea["texto_md"] == "# Registro de sueños\n\nAhora con fechas."
    assert idea["que_sigue_md"] is None
    assert idea["autor"] == "alumno"
    assert idea["creado"]
    assert _fila(base, "SELECT count(*) FROM ideas WHERE alumno_id = ?", cliente.alumno_id)[0] == 2


@pytest.mark.parametrize(
    ("cuerpo", "mensaje"),
    [
        ({"texto_md": "   "}, "vacía"),
        ({"texto_md": "x" * 6001}, "6000"),
        ({"texto_md": "Idea", "que_sigue_md": "y" * 3001}, "3000"),
    ],
)
def test_idea_invalida_da_422_con_el_motivo(cliente, cuerpo, mensaje):
    respuesta = cliente.put("/api/idea", json=cuerpo)

    assert respuesta.status_code == 422
    assert mensaje in respuesta.json()["detalle"]


def test_descargar_mi_idea(cliente, base):
    _con_idea(base, cliente)

    respuesta = cliente.get("/api/idea.md")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "text/markdown; charset=utf-8"
    assert respuesta.headers["content-disposition"] == 'attachment; filename="mi-idea.md"'
    assert respuesta.text == f"{IDEA}\n\n## Qué sigue\n\n- Compartirlo con el grupo.\n"


# --- Taller ---


def test_elegir_el_taller(cliente, base):
    respuesta = cliente.put("/api/taller", json={"herramienta": "codex", "sistema": "mac"})

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["herramienta"] == "codex"
    assert datos["sistema"] == "mac"
    assert datos["kit_habilitado"] is False
    assert any("idea" in falta for falta in datos["falta"])
    fila = _fila(base, "SELECT herramienta, sistema FROM alumnos WHERE id = ?", cliente.alumno_id)
    assert tuple(fila) == ("codex", "mac")


def test_taller_completo_con_idea_habilita_el_kit(cliente, base):
    _con_idea(base, cliente)

    datos = cliente.put("/api/taller", json={"herramienta": "claude", "sistema": "windows"}).json()

    assert datos["kit_habilitado"] is True
    assert datos["falta"] == []


def test_taller_con_otro_sistema_no_habilita_el_kit(cliente, base):
    _con_idea(base, cliente)

    datos = cliente.put("/api/taller", json={"herramienta": "codex", "sistema": "otro"}).json()

    assert datos["kit_habilitado"] is False
    assert any("Mac o Windows" in falta for falta in datos["falta"])
    assert _fila(base, "SELECT sistema FROM alumnos WHERE id = ?", cliente.alumno_id)[0] == "otro"


def test_taller_se_puede_elegir_de_a_una_cosa(cliente, base):
    cliente.put("/api/taller", json={"herramienta": "codex"})
    cliente.put("/api/taller", json={"sistema": "windows"})

    assert tuple(_fila(base, "SELECT herramienta, sistema FROM alumnos WHERE id = ?", cliente.alumno_id)) == ("codex", "windows")


@pytest.mark.parametrize("cuerpo", [{}, {"herramienta": "cursor"}, {"sistema": "linux"}])
def test_taller_invalido_da_422(cliente, cuerpo):
    assert cliente.put("/api/taller", json=cuerpo).status_code == 422


# --- Kit ---


def test_kit_sin_idea_ni_taller_da_409_con_lo_que_falta(cliente):
    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 409
    datos = respuesta.json()
    assert datos["detalle"]
    assert len(datos["falta"]) == 3


def test_kit_sin_taller_da_409(cliente, base):
    _con_idea(base, cliente)
    _taller(base, cliente, "codex", None)

    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 409
    assert len(respuesta.json()["falta"]) == 1


def test_kit_con_otro_sistema_da_409(cliente, base):
    _con_idea(base, cliente)
    _taller(base, cliente, "codex", "otro")

    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 409
    assert "Mac o Windows" in respuesta.json()["falta"][0]


def test_bajar_el_kit(cliente, base):
    _con_idea(base, cliente)
    _taller(base, cliente, "codex", "mac")
    _en_modulo(base, cliente, 3)

    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/zip"
    assert respuesta.headers["content-disposition"] == 'attachment; filename="mi-proyecto-registro-de-suenos.zip"'
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo:
        mi_idea = archivo.read("mi-proyecto-registro-de-suenos/mi-idea.md").decode("utf-8")
        leeme = archivo.read("mi-proyecto-registro-de-suenos/LEEME.txt").decode("utf-8")
    assert mi_idea.startswith(IDEA)
    assert leeme == "Abrí la carpeta en Codex.\n"
    fila = _fila(base, "SELECT version_curso, fecha_machete, herramienta, sistema FROM kits WHERE alumno_id = ?", cliente.alumno_id)
    assert tuple(fila) == ("desarrollo", "2026-09-20", "codex", "mac")
    evento = _fila(base, "SELECT detalle FROM eventos WHERE tipo = 'kit' AND alumno_id = ?", cliente.alumno_id)
    assert evento[0] == "herramienta=codex,sistema=mac"
    assert _fila(base, "SELECT modulo_actual FROM alumnos WHERE id = ?", cliente.alumno_id)[0] == 4


def test_bajar_el_kit_de_nuevo_no_baja_el_modulo(cliente, base):
    _con_idea(base, cliente)
    _taller(base, cliente, "claude", "windows")
    _en_modulo(base, cliente, 7)

    assert cliente.get("/api/kit").status_code == 200
    assert cliente.get("/api/kit").status_code == 200

    assert _fila(base, "SELECT modulo_actual FROM alumnos WHERE id = ?", cliente.alumno_id)[0] == 7
    assert _fila(base, "SELECT count(*) FROM kits WHERE alumno_id = ?", cliente.alumno_id)[0] == 2


def test_el_kit_lleva_el_autor_y_el_newsletter_de_la_configuracion(hacer_cliente, base, raiz, con_autor, mails_enviados):
    _escribir(raiz / "kit/AGENTS.md", "Curso de {{AUTOR}} ({{NEWSLETTER}}) para {{TITULO}}.\n")
    cliente = hacer_cliente([alumnos.router], email=MAIL, settings=con_autor)
    _con_idea(base, cliente)
    _taller(base, cliente, "codex", "mac")

    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 200
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as archivo:
        agents = archivo.read("mi-proyecto-registro-de-suenos/AGENTS.md").decode("utf-8")
    assert agents == "Curso de Ana (El boletín de Ana) para Registro de sueños.\n"


def test_kit_con_la_plantilla_rota_da_503(cliente, base, raiz):
    _con_idea(base, cliente)
    _taller(base, cliente, "codex", "mac")
    (raiz / "kit/AGENTS.md").unlink()

    respuesta = cliente.get("/api/kit")

    assert respuesta.status_code == 503
    assert respuesta.json()["detalle"]
    assert _fila(base, "SELECT count(*) FROM kits")[0] == 0


# --- Links y galería ---

LINK = {"url": "https://mi-idea.netlify.app", "titulo": "Mi registro de sueños"}


@pytest.fixture
def con_kit(cliente, base):
    """El alumno ya bajó el kit: está en el módulo 4."""
    _en_modulo(base, cliente, 4)
    return cliente


def _aprobar(base, link_id: int) -> None:
    with base:
        base.execute("UPDATE links SET aprobado = 1 WHERE id = ?", (link_id,))


def test_registrar_un_link(con_kit, base, mails_enviados):
    cliente = con_kit
    respuesta = cliente.post("/api/links", json=LINK)

    assert respuesta.status_code == 201
    link_id = respuesta.json()["id"]
    assert respuesta.json() == {"id": link_id, "mail": True}
    fila = _fila(base, "SELECT url, titulo, mostrar_galeria, uso_contenido, aprobado FROM links WHERE id = ?", link_id)
    assert tuple(fila) == ("https://mi-idea.netlify.app", "Mi registro de sueños", 0, 0, 0)
    assert _fila(base, "SELECT count(*) FROM eventos WHERE tipo = 'link' AND alumno_id = ?", cliente.alumno_id)[0] == 1
    assert _fila(base, "SELECT modulo_actual FROM alumnos WHERE id = ?", cliente.alumno_id)[0] == 7
    assert mails_enviados == [
        (cliente.alumno_id, "contame", "contame", {"link": LINK["url"], "titulo": LINK["titulo"]})
    ]


def test_registrar_un_link_con_las_dos_opciones(con_kit, base):
    link_id = con_kit.post("/api/links", json={**LINK, "mostrar_galeria": True, "uso_contenido": True}).json()["id"]

    assert tuple(_fila(base, "SELECT mostrar_galeria, uso_contenido FROM links WHERE id = ?", link_id)) == (1, 1)


def test_link_sin_titulo(con_kit, base, mails_enviados):
    link_id = con_kit.post("/api/links", json={"url": "https://ejemplo.com/mi-pagina"}).json()["id"]

    assert _fila(base, "SELECT titulo FROM links WHERE id = ?", link_id)[0] is None
    assert mails_enviados[0][3] == {"link": "https://ejemplo.com/mi-pagina", "titulo": None}


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"url": "http://mi-idea.netlify.app"},
        {"url": "javascript:alert(1)"},
        {"url": "https://"},
        {"url": "https://con espacios.com"},
        {"url": "https://ejemplo.com/" + "a" * 500},
        {"url": "https://ejemplo.com", "titulo": "t" * 121},
        {"url": "https://ejemplo.com/\u202egnp.exe"},
        {"url": "https://ejemplo.com/\u200b"},
        {"url": "https://ejemplo.com/\x7f"},
        {"url": "https://ejemplo.com", "titulo": "Mi p\u00e1gina\u202e al rev\u00e9s"},
        {"url": "https://ejemplo.com", "titulo": "Con\u200bespacio invisible"},
        {"url": "https://ejemplo.com", "titulo": "Con\x00nulo"},
        {"url": "https://ejemplo.com", "titulo": "Con\nsalto"},
        {"url": "https://ejemplo.com", "titulo": "Con\ufeffmarca"},
    ],
)
def test_link_invalido_da_422(con_kit, base, mails_enviados, cuerpo):
    respuesta = con_kit.post("/api/links", json=cuerpo)

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"]
    assert _fila(base, "SELECT count(*) FROM links")[0] == 0
    assert mails_enviados == []


@pytest.mark.parametrize("modulo", [1, 3])
def test_link_sin_haber_bajado_el_kit_da_409(cliente, base, mails_enviados, modulo):
    _en_modulo(base, cliente, modulo)

    respuesta = cliente.post("/api/links", json=LINK)

    assert respuesta.status_code == 409
    assert "kit" in respuesta.json()["detalle"]
    assert _fila(base, "SELECT count(*) FROM links")[0] == 0
    assert _fila(base, "SELECT modulo_actual FROM alumnos WHERE id = ?", cliente.alumno_id)[0] == modulo
    assert mails_enviados == []


def test_como_mucho_cinco_links(con_kit, base, mails_enviados):
    for numero in range(5):
        assert con_kit.post("/api/links", json={"url": f"https://pagina-{numero}.netlify.app"}).status_code == 201

    respuesta = con_kit.post("/api/links", json={"url": "https://pagina-6.netlify.app"})

    assert respuesta.status_code == 409
    assert "5" in respuesta.json()["detalle"]
    assert _fila(base, "SELECT count(*) FROM links WHERE alumno_id = ?", con_kit.alumno_id)[0] == 5


def test_borrar_un_link_libera_lugar(con_kit, base):
    ids = [con_kit.post("/api/links", json={"url": f"https://pagina-{n}.netlify.app"}).json()["id"] for n in range(5)]

    assert con_kit.delete(f"/api/links/{ids[0]}").status_code == 200
    assert con_kit.post("/api/links", json={"url": "https://otra.netlify.app"}).status_code == 201


def test_el_mail_contame_sale_una_sola_vez(con_kit, base, mails_enviados):
    primero = con_kit.post("/api/links", json=LINK)
    with base:
        base.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'contame', 'contame', 'enviado')",
            (con_kit.alumno_id,),
        )

    segundo = con_kit.post("/api/links", json={"url": "https://otra.netlify.app"})

    assert primero.json()["mail"] is True
    assert segundo.status_code == 201
    assert segundo.json()["mail"] is False
    assert [envio[2] for envio in mails_enviados] == ["contame"]


def test_sin_mails_del_curso_el_link_no_manda_mail(con_kit, base, mails_enviados):
    dominio.agregar_consentimiento(base, con_kit.alumno_id, "mails_curso", False, "prueba")

    respuesta = con_kit.post("/api/links", json=LINK)

    assert respuesta.status_code == 201
    assert respuesta.json()["mail"] is False
    assert mails_enviados == []


def test_mis_links(con_kit, base, hacer_cliente):
    otro = hacer_cliente([alumnos.router], email="beto@example.com")
    _en_modulo(base, otro, 4)
    otro.post("/api/links", json={"url": "https://ajeno.netlify.app"})
    primero = con_kit.post("/api/links", json={**LINK, "mostrar_galeria": True}).json()["id"]
    segundo = con_kit.post("/api/links", json={"url": "https://otra.netlify.app", "uso_contenido": True}).json()["id"]
    _aprobar(base, primero)

    respuesta = con_kit.get("/api/links")

    assert respuesta.status_code == 200
    links = respuesta.json()
    assert [link["id"] for link in links] == [primero, segundo]
    assert {k: v for k, v in links[0].items() if k != "creado"} == {
        "id": primero, "url": LINK["url"], "titulo": LINK["titulo"],
        "mostrar_galeria": True, "uso_contenido": False, "aprobado": True,
    }
    assert links[1]["uso_contenido"] is True and links[1]["aprobado"] is False
    assert links[0]["creado"]
    assert "ajeno" not in respuesta.text


def test_cambiar_las_opciones_de_un_link(con_kit, base):
    link_id = con_kit.post("/api/links", json=LINK).json()["id"]

    respuesta = con_kit.patch(f"/api/links/{link_id}", json={"mostrar_galeria": True})

    assert respuesta.status_code == 200
    assert respuesta.json()["mostrar_galeria"] is True
    assert respuesta.json()["uso_contenido"] is False
    assert respuesta.json()["id"] == link_id
    otra = con_kit.patch(f"/api/links/{link_id}", json={"uso_contenido": True, "mostrar_galeria": False}).json()
    assert (otra["mostrar_galeria"], otra["uso_contenido"]) == (False, True)
    assert tuple(_fila(base, "SELECT mostrar_galeria, uso_contenido FROM links WHERE id = ?", link_id)) == (0, 1)


def test_cambiar_un_link_sin_cambios_da_422(con_kit):
    link_id = con_kit.post("/api/links", json=LINK).json()["id"]

    respuesta = con_kit.patch(f"/api/links/{link_id}", json={})

    assert respuesta.status_code == 422
    assert respuesta.json()["detalle"]


def test_no_se_puede_cambiar_ni_borrar_el_link_de_otro(con_kit, base, hacer_cliente):
    link_id = con_kit.post("/api/links", json=LINK).json()["id"]
    otro = hacer_cliente([alumnos.router], email="beto@example.com")

    cambiar = otro.patch(f"/api/links/{link_id}", json={"mostrar_galeria": True})
    borrar = otro.delete(f"/api/links/{link_id}")
    inexistente = otro.delete("/api/links/999")

    assert (cambiar.status_code, borrar.status_code, inexistente.status_code) == (404, 404, 404)
    assert cambiar.json()["detalle"]
    assert tuple(_fila(base, "SELECT mostrar_galeria FROM links WHERE id = ?", link_id)) == (0,)


def test_borrar_un_link(con_kit, base):
    link_id = con_kit.post("/api/links", json=LINK).json()["id"]

    respuesta = con_kit.delete(f"/api/links/{link_id}")

    assert respuesta.status_code == 200
    assert _fila(base, "SELECT count(*) FROM links WHERE id = ?", link_id)[0] == 0
    assert con_kit.get("/api/links").json() == []


def test_los_links_piden_sesion(hacer_cliente, raiz):
    anonimo = hacer_cliente([alumnos.router])

    assert anonimo.get("/api/links").status_code == 401
    assert anonimo.patch("/api/links/1", json={"mostrar_galeria": True}).status_code == 401
    assert anonimo.delete("/api/links/1").status_code == 401


def test_galeria_publica_solo_con_los_links_aprobados(hacer_cliente, con_kit, base):
    aprobado = con_kit.post("/api/links", json={**LINK, "mostrar_galeria": True}).json()["id"]
    con_kit.post("/api/links", json={"url": "https://privado.netlify.app", "titulo": "No mostrar"})
    otro_aprobado = con_kit.post("/api/links", json={"url": "https://otra.netlify.app", "mostrar_galeria": True}).json()["id"]
    con_kit.post("/api/links", json={"url": "https://pendiente.netlify.app", "mostrar_galeria": True})
    oculto = con_kit.post("/api/links", json={"url": "https://oculto.netlify.app"}).json()["id"]
    for link_id in (aprobado, otro_aprobado, oculto):
        _aprobar(base, link_id)

    respuesta = hacer_cliente([alumnos.router]).get("/api/galeria")

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"titulo": None, "url": "https://otra.netlify.app"},
        {"titulo": "Mi registro de sueños", "url": "https://mi-idea.netlify.app"},
    ]


# --- Consentimientos ---


def test_cambiar_las_novedades(hacer_cliente, raiz, base, con_autor):
    cliente = hacer_cliente([alumnos.router], email=MAIL, settings=con_autor)

    respuesta = cliente.put("/api/consentimientos", json={"novedades": True})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"mails_curso": True, "novedades": True}
    fila = _fila(
        base, "SELECT valor, version_texto FROM consentimientos WHERE alumno_id = ? AND tipo = 'novedades' ORDER BY id DESC",
        cliente.alumno_id,
    )
    assert tuple(fila) == (1, "2026-10-01")
    assert cliente.get("/api/yo").json()["consentimientos"] == {"mails_curso": True, "novedades": True}
    assert cliente.put("/api/consentimientos", json={"novedades": False}).json()["novedades"] is False


def test_sin_newsletter_no_se_pueden_aceptar_las_novedades(cliente, base):
    respuesta = cliente.put("/api/consentimientos", json={"novedades": True})

    assert respuesta.status_code == 409
    assert respuesta.json()["detalle"]
    assert _fila(base, "SELECT count(*) FROM consentimientos WHERE tipo = 'novedades'")[0] == 0
    juntos = cliente.put("/api/consentimientos", json={"novedades": True, "mails_curso": False})
    assert juntos.status_code == 409
    assert dominio.consentimiento(base, cliente.alumno_id, "mails_curso") is True


def test_sin_newsletter_igual_se_pueden_rechazar_las_novedades(cliente, base):
    respuesta = cliente.put("/api/consentimientos", json={"novedades": False})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"mails_curso": True, "novedades": False}


def test_darse_de_baja_y_de_alta_en_los_mails(cliente, base):
    assert cliente.put("/api/consentimientos", json={"mails_curso": False}).json()["mails_curso"] is False
    assert _fila(base, "SELECT count(*) FROM eventos WHERE tipo = 'baja_mails' AND alumno_id = ?", cliente.alumno_id)[0] == 1

    assert cliente.put("/api/consentimientos", json={"mails_curso": True}).json()["mails_curso"] is True
    assert dominio.consentimiento(base, cliente.alumno_id, "mails_curso") is True


@pytest.mark.parametrize("cuerpo", [{}, {"transferencia": False}, {"novedades": "quizás"}, {"otro_permiso": True}])
def test_consentimientos_invalidos_da_422(cliente, cuerpo):
    assert cliente.put("/api/consentimientos", json=cuerpo).status_code == 422


# --- Mis datos ---


def _conversacion(base, alumno_id: int) -> None:
    with base:
        sesion_id = base.execute(
            "INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1) RETURNING id", (alumno_id,)
        ).fetchone()[0]
        mensajes = [
            ("user", [{"type": "text", "text": "[Estado del alumno] idea vigente: ninguna."}]),
            ("assistant", [{"type": "text", "text": "Hola, soy el tutor del curso."}]),
            ("user", [{"type": "text", "text": "Hola, quiero hacer una página."}]),
            (
                "assistant",
                [
                    {"type": "thinking", "thinking": "interno", "signature": "x"},
                    {"type": "text", "text": "¡Buenísimo! Contame más."},
                    {"type": "tool_use", "id": "t1", "name": "guardar_idea", "input": {"texto_md": "x"}},
                ],
            ),
            ("user", [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]),
            ("user", [{"type": "text", "text": "[captura de pantalla enviada]"}]),
        ]
        for orden, (rol, contenido) in enumerate(mensajes):
            base.execute(
                "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, ?, ?, ?)",
                (sesion_id, orden, rol, json.dumps(contenido)),
            )
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 0.01, alumno_id=alumno_id, sesion_id=sesion_id)


def test_descargar_mis_datos(cliente, base, hacer_cliente):
    otro = hacer_cliente([alumnos.router], email="beto@example.com")
    dominio.guardar_idea(base, otro.alumno_id, "La idea de otro", None, "tutor")
    _con_idea(base, cliente)
    dominio.completar_modulo(base, cliente.alumno_id, 1, "tutor", resumen="Quiere un registro de sueños.")
    _conversacion(base, cliente.alumno_id)
    _taller(base, cliente, "codex", "mac")
    cliente.get("/api/kit")
    cliente.post("/api/links", json=LINK)
    with base:
        base.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'bienvenida', 'bienvenida', 'enviado')",
            (cliente.alumno_id,),
        )

    respuesta = cliente.get("/api/mis-datos")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("application/json")
    assert respuesta.headers["content-disposition"] == 'attachment; filename="mis-datos.json"'
    assert respuesta.headers["cache-control"] == "no-store"
    datos = respuesta.json()
    assert set(datos) >= {"alumno", "consentimientos", "avance", "ideas", "conversaciones", "kits", "links", "mails"}
    assert datos["alumno"]["email"] == MAIL
    assert datos["alumno"]["herramienta"] == "codex"
    assert {(c["tipo"], c["valor"]) for c in datos["consentimientos"]} >= {("mails_curso", True), ("transferencia", True)}
    assert datos["avance"][0]["resumen"] == "Quiere un registro de sueños."
    assert [i["texto_md"] for i in datos["ideas"]] == [IDEA]
    assert datos["conversaciones"][0]["modulo"] == 1
    assert "Estado del alumno" not in respuesta.text
    assert datos["conversaciones"][0]["mensajes"] == [
        {"rol": "tutor", "texto": "Hola, soy el tutor del curso."},
        {"rol": "alumno", "texto": "Hola, quiero hacer una página."},
        {"rol": "tutor", "texto": "¡Buenísimo! Contame más."},
        {"rol": "alumno", "texto": "[captura de pantalla enviada]"},
    ]
    assert datos["kits"][0]["herramienta"] == "codex"
    assert datos["links"][0]["url"] == LINK["url"]
    assert datos["mails"][0]["tipo"] == "bienvenida"
    assert "La idea de otro" not in respuesta.text
    assert "beto@example.com" not in respuesta.text


def test_borrar_mis_datos_pide_confirmacion(cliente, base):
    for cuerpo in ({}, {"confirmar": "borrar"}, {"confirmar": "SI"}):
        respuesta = cliente.request("DELETE", "/api/mis-datos", json=cuerpo)
        assert respuesta.status_code in (400, 422)
        assert respuesta.json()["detalle"]

    assert dominio.alumno(base, cliente.alumno_id) is not None


def test_borrar_mis_datos(cliente, base, hacer_cliente):
    alumno_id = cliente.alumno_id
    otro = hacer_cliente([alumnos.router], email="beto@example.com")
    _con_idea(base, cliente)
    dominio.completar_modulo(base, alumno_id, 1, "tutor")
    _conversacion(base, alumno_id)
    _taller(base, cliente, "codex", "mac")
    cliente.get("/api/kit")
    cliente.post("/api/links", json=LINK)
    with base:
        base.execute(
            "INSERT INTO codigos (email, hash, sal, vence, ip) VALUES (?, 'h', 's', '2026-01-01T00:00:00+00:00', '1.1.1.1')",
            (MAIL,),
        )

    respuesta = cliente.request("DELETE", "/api/mis-datos", json={"confirmar": "BORRAR"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}
    assert f'{auth.COOKIE}=""' in respuesta.headers["set-cookie"]
    assert dominio.alumno(base, alumno_id) is None
    for tabla in ("consentimientos", "avance", "ideas", "sesiones", "kits", "links", "mails"):
        assert _fila(base, f"SELECT count(*) FROM {tabla} WHERE alumno_id = ?", alumno_id)[0] == 0, tabla
    assert _fila(base, "SELECT count(*) FROM mensajes")[0] == 0
    assert _fila(base, "SELECT count(*) FROM codigos WHERE email = ?", MAIL)[0] == 0
    assert tuple(_fila(base, "SELECT count(*), sum(alumno_id IS NULL) FROM uso")) == (1, 1)
    assert _fila(base, "SELECT count(*) FROM eventos WHERE alumno_id = ?", alumno_id)[0] == 0
    assert _fila(base, "SELECT count(*) FROM eventos WHERE tipo = 'kit' AND alumno_id IS NULL")[0] == 1
    assert _fila(base, "SELECT count(*) FROM eventos WHERE tipo = 'borrado' AND alumno_id IS NULL")[0] == 1
    assert dominio.alumno(base, otro.alumno_id) is not None
    assert cliente.get("/api/yo").status_code == 401


# --- Textos legales ---


def test_aviso_de_privacidad(hacer_cliente, raiz):
    respuesta = hacer_cliente([alumnos.router]).get("/api/legal/privacidad")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "version": "2026-10-01",
        "titulo": "Aviso de privacidad",
        "texto_md": "# Privacidad\n\nQué guardamos.\n",
    }


def test_textos_de_consentimiento(hacer_cliente, raiz, con_autor):
    respuesta = hacer_cliente([alumnos.router], settings=con_autor).get("/api/legal/consentimientos")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "version": "2026-10-01",
        "textos": {
            "mails_curso": "Acepto recibir los mails del curso.",
            "transferencia": "Acepto que mis datos se procesen en Estados Unidos.",
            "novedades": "Quiero recibir las novedades de Ana por El boletín de Ana.",
        },
        "texto_md": "# Consentimientos\n\nDetalle de Ana.\n",
    }


def test_privacidad_reemplaza_el_autor(hacer_cliente, raiz):
    _escribir(
        raiz / "legal/privacidad.md",
        "---\nversion: 2026-10-01\ntitulo: Privacidad del curso de {{AUTOR}}\n---\n\nResponsable: {{AUTOR}}.\n",
    )

    datos = hacer_cliente([alumnos.router]).get("/api/legal/privacidad").json()

    assert datos["titulo"] == "Privacidad del curso de el autor del curso"
    assert datos["texto_md"] == "Responsable: el autor del curso.\n"


@pytest.mark.parametrize(("ruta", "archivo"), [("privacidad", "privacidad.md"), ("consentimientos", "consentimientos.md")])
def test_texto_legal_que_falta_da_404(hacer_cliente, raiz, ruta, archivo):
    (raiz / "legal" / archivo).unlink()

    respuesta = hacer_cliente([alumnos.router]).get(f"/api/legal/{ruta}")

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"]
