"""Endpoints del alumno (contracts/api.md): estado, guía escrita, idea, taller, kit, links, siguiente
paso (specs/002-siguiente-paso/contracts/api.md) y datos.

Las sesiones con el tutor viven en api.py y la baja de mails en mails.py. Con APROBACION_MANUAL,
quien espera aprobación solo llega a /yo, /mis-datos y /consentimientos (con `alumno_actual`); el
resto usa `alumno_aprobado`, que le responde 403 con el estado "pendiente".
"""

import json
import logging
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import yaml
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from vibe_tutor import api, auth, contenido, costos, dominio, kit, mails
from vibe_tutor.auth import Alumno, alumno_actual, alumno_aprobado, conexion
from vibe_tutor.config import Settings, get_settings

MODULOS_WEB = (1, 2, 3)
MODULOS_AUDIO = range(1, 8)
MODULO_LINK = 7
MODULO_GUIA_CON_DATOS = 3
MAX_URL = 500
MAX_TITULO_LINK = 120
MAX_LINKS = 5
# Temas del machete que la guía escrita del módulo 3 muestra en "Datos del día", en este orden.
TEMAS_DATOS_DEL_DIA = ("planes", "instalar", "ver", "publicar", "limites")
# Caracteres de control y de formato (invisibles, cambio de dirección del texto): nunca en un link.
CATEGORIAS_PROHIBIDAS = frozenset({"Cc", "Cf"})
LIMITE_GALERIA = 200
CONFIRMAR_BORRADO = "BORRAR"
TIPOS_CONSENTIMIENTO = ("mails_curso", "novedades", "siguiente_paso")
TEXTOS_CONSENTIMIENTO = ("mails_curso", "transferencia", "novedades", "siguiente_paso")

MENSAJE_FUERA_DE_LA_WEB = "Ese módulo no está en la web: los módulos 4 a 7 se hacen con el kit."
MENSAJE_NO_ABIERTO = "Ese módulo todavía no está abierto."
MENSAJE_GUIA = "La guía escrita de este módulo todavía no está lista. Probá de nuevo más tarde."
MENSAJE_SIN_IDEA = "Todavía no guardaste tu idea."
MENSAJE_TALLER = "Elegí tu herramienta o tu computadora."
MENSAJE_KIT_FALTA = "Para bajar tu kit todavía falta:"
MENSAJE_PASOS_FALTA = "Para ver cómo seguir en tu computadora todavía falta:"
MENSAJE_KIT_NO_DISPONIBLE = "El kit no está disponible en este momento. Probá de nuevo en un rato."
MENSAJE_LINK = "El link tiene que empezar con https:// y ser la dirección de tu página."
MENSAJE_LINK_LARGO = f"El link es muy largo: puede tener hasta {MAX_URL} caracteres."
MENSAJE_TITULO_LARGO = f"El título puede tener hasta {MAX_TITULO_LINK} caracteres."
MENSAJE_LINK_INVISIBLES = (
    "El link tiene caracteres invisibles o de control. Copialo de nuevo desde la barra del navegador."
)
MENSAJE_TITULO_INVISIBLES = "El título tiene caracteres invisibles o saltos de línea. Escribilo de nuevo en una línea."
MENSAJE_LINK_SIN_KIT = "Para registrar el link de tu página, primero bajá tu kit en el módulo 3."
MENSAJE_MAX_LINKS = f"Ya registraste {MAX_LINKS} links, el máximo. Si querés sumar otro, borrá uno de los que tenés."
MENSAJE_LINK_AJENO = "Ese link no existe."
MENSAJE_PLANTILLA = "La plantilla de la idea todavía no está lista. Probá de nuevo más tarde."
MENSAJE_SIN_DATOS_DEL_DIA = (
    "Los datos del día no están disponibles en este momento. Probá de nuevo en un rato, y no uses "
    "planes, precios ni pasos que no tengan fecha."
)
INTRO_DATOS_DEL_DIA = (
    "Estos datos cambian seguido. Cada uno dice de dónde sale y cuándo lo verificamos. Si algo no "
    "coincide con lo que ves en tu pantalla, hacé caso a la pantalla."
)
MENSAJE_SIN_CAMBIOS = "No hay ningún cambio para guardar."
MENSAJE_BORRAR = f"Para borrar tus datos, escribí {CONFIRMAR_BORRADO} en mayúsculas."
MENSAJE_PRIVACIDAD = "El aviso de privacidad todavía no está publicado. Probá de nuevo más tarde."
MENSAJE_CONSENTIMIENTOS = "Los textos de los permisos todavía no están publicados. Probá de nuevo más tarde."
MENSAJE_SIN_NOVEDADES = "Este curso no tiene una lista de novedades por mail, así que no hay nada que aceptar."
MENSAJE_SIN_SIGUIENTE_PASO = "Este curso no ofrece un siguiente paso por ahora, así que no hay nada que contestar."
MENSAJE_SIN_AVISO_SIGUIENTE_PASO = "Este curso no ofrece un siguiente paso por ahora, así que no hay aviso que pedir."
MENSAJE_AVISO_SIN_NEGOCIO = "El aviso del siguiente paso se pide solo si contestás que sí."
FALTA_IDEA = "Tu idea en una página: la armás en el módulo 2."
FALTA_HERRAMIENTA = "Elegir tu herramienta: Codex o Claude."
FALTA_SISTEMA = "Elegir tu computadora: Mac o Windows."
FALTA_COMPUTADORA = (
    "Una computadora con Mac o Windows: esta parte del curso se hace ahí. "
    "Tu avance queda guardado para cuando la tengas."
)

log = logging.getLogger("vibe_tutor.alumnos")
router = APIRouter(prefix="/api", tags=["alumnos"])


class IdeaNueva(BaseModel):
    texto_md: str = Field(max_length=dominio.MAX_IDEA * 2)
    que_sigue_md: str | None = Field(default=None, max_length=dominio.MAX_QUE_SIGUE * 2)


class Taller(BaseModel):
    herramienta: Literal["codex", "claude"] | None = None
    sistema: Literal["mac", "windows", "otro"] | None = None


class NuevoLink(BaseModel):
    url: str = Field(max_length=MAX_URL * 4)
    titulo: str | None = Field(default=None, max_length=MAX_TITULO_LINK * 4)
    mostrar_galeria: bool = False
    uso_contenido: bool = False


class CambioLink(BaseModel):
    mostrar_galeria: bool | None = None
    uso_contenido: bool | None = None


class CambioConsentimientos(BaseModel):
    novedades: bool | None = None
    mails_curso: bool | None = None
    siguiente_paso: bool | None = None


class RespuestaSiguientePaso(BaseModel):
    respuesta: Literal["si", "no"]
    aviso: bool = False


class Borrado(BaseModel):
    confirmar: str = Field(default="", max_length=32)


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _audio(raiz: Path, modulo: int) -> dict | None:
    carpeta = Path(raiz) / "audios"
    if not (carpeta / f"modulo-{modulo}.mp3").is_file():
        return None
    transcripcion = f"/audios/modulo-{modulo}.md" if (carpeta / f"modulo-{modulo}.md").is_file() else None
    return {"modulo": modulo, "url": f"/audios/modulo-{modulo}.mp3", "transcripcion": transcripcion}


def _leer_md(raiz: Path, ruta: str, mensaje: str) -> tuple[dict, str]:
    """Frontmatter y cuerpo de un archivo de contenido; 404 amable si falta o está roto."""
    try:
        return contenido.separar_frontmatter(contenido.leer(raiz, ruta))
    except (ValueError, yaml.YAMLError) as error:
        log.warning("no se pudo leer %s: %s", ruta, error)
        raise HTTPException(status.HTTP_404_NOT_FOUND, mensaje) from None


def _texto_del_curso(settings: Settings, valor: object) -> str:
    """Un texto de contenido/ listo para mostrar: con {{AUTOR}} y {{NEWSLETTER}} llenos."""
    return contenido.reemplazar_marcadores(str(valor), settings)


def _fila(con: sqlite3.Connection, alumno: Alumno) -> sqlite3.Row:
    return dominio.alumno(con, alumno.id)


def _modulo_abierto(con: sqlite3.Connection, alumno: Alumno, modulo: int) -> None:
    if modulo not in MODULOS_WEB:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_FUERA_DE_LA_WEB)
    if modulo > _fila(con, alumno)["modulo_actual"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, MENSAJE_NO_ABIERTO)


def _consentimientos(con: sqlite3.Connection, alumno_id: int) -> dict[str, bool]:
    return {tipo: dominio.consentimiento(con, alumno_id, tipo) for tipo in TIPOS_CONSENTIMIENTO}


def _falta_del_taller(fila: sqlite3.Row) -> list[str]:
    """Lo que falta elegir para usar el kit: herramienta y una computadora Mac o Windows."""
    falta = []
    if fila["herramienta"] is None:
        falta.append(FALTA_HERRAMIENTA)
    if fila["sistema"] == "otro":
        falta.append(FALTA_COMPUTADORA)
    elif fila["sistema"] is None:
        falta.append(FALTA_SISTEMA)
    return falta


def _falta_para_kit(con: sqlite3.Connection, fila: sqlite3.Row) -> list[str]:
    idea = [] if dominio.idea_vigente(con, fila["id"]) is not None else [FALTA_IDEA]
    return [*idea, *_falta_del_taller(fila)]


def _descarga(cuerpo: bytes | str, tipo: str, nombre: str) -> Response:
    """Archivo para bajar; lleva datos del alumno, así que el navegador no lo guarda en caché."""
    return Response(
        cuerpo,
        media_type=tipo,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"', "Cache-Control": "no-store"},
    )


def _filas(con: sqlite3.Connection, sql: str, *parametros) -> list[dict]:
    return [dict(fila) for fila in con.execute(sql, parametros)]


def _bloques(contenido_json: str) -> list[dict]:
    try:
        bloques = json.loads(contenido_json)
    except ValueError:
        return []
    return bloques if isinstance(bloques, list) else []


def _conversaciones(con: sqlite3.Connection, alumno_id: int) -> list[dict]:
    conversaciones = []
    for sesion in con.execute(
        "SELECT id, modulo, inicio, fin FROM sesiones WHERE alumno_id = ? ORDER BY id", (alumno_id,)
    ).fetchall():
        filas = con.execute(
            "SELECT rol, contenido_json FROM mensajes WHERE sesion_id = ? ORDER BY orden", (sesion["id"],)
        ).fetchall()
        mensajes = api.mensajes_visibles([(f["rol"], _bloques(f["contenido_json"])) for f in filas])
        conversaciones.append(
            {"modulo": sesion["modulo"], "inicio": sesion["inicio"], "fin": sesion["fin"], "mensajes": mensajes}
        )
    return conversaciones


def _tiene_invisibles(texto: str) -> bool:
    return any(unicodedata.category(caracter) in CATEGORIAS_PROHIBIDAS for caracter in texto)


def _url_valida(crudo: str) -> str:
    url = crudo.strip()
    if len(url) > MAX_URL:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_LINK_LARGO)
    if _tiene_invisibles(url):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_LINK_INVISIBLES)
    try:
        partes = urlsplit(url)
        host = partes.hostname or ""
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_LINK) from None
    if (
        not url.lower().startswith("https://")
        or "." not in host.strip(".")
        or "@" in partes.netloc
        or any(caracter.isspace() for caracter in url)
    ):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_LINK)
    return url


def _titulo_valido(crudo: str | None) -> str | None:
    if _tiene_invisibles(crudo or ""):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_TITULO_INVISIBLES)
    titulo = " ".join((crudo or "").split())
    if len(titulo) > MAX_TITULO_LINK:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_TITULO_LARGO)
    return titulo or None


# --- Estado ---


@router.get("/yo")
def yo(
    alumno: Alumno = Depends(alumno_actual),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    dominio.tocar_actividad(con, alumno.id)
    fila = _fila(con, alumno)
    idea = dominio.idea_vigente(con, alumno.id)
    tope = costos.estado_tope(
        con, alumno.id, tope_alumno=settings.tope_alumno_usd, tope_mensual=settings.tope_mensual_usd
    )
    return {
        "email": alumno.email,
        "es_admin": alumno.es_admin,
        "modulo_actual": fila["modulo_actual"],
        "avance": _filas(con, "SELECT modulo, completado, via FROM avance WHERE alumno_id = ? ORDER BY modulo", alumno.id),
        "idea": {"version": idea["version"], "actualizada": idea["creado"]} if idea else None,
        "taller": {"herramienta": fila["herramienta"], "sistema": fila["sistema"]},
        "tope": {"bloqueado": tope["bloqueado"], "alcance": tope["alcance"]},
        "consentimientos": _consentimientos(con, alumno.id),
        "audios": [audio for n in MODULOS_AUDIO if (audio := _audio(settings.contenido_dir, n))],
        "estado": alumno.estado,
    }


# --- Módulos 1 a 3 con la guía escrita ---


@router.get("/modulos/{n}/guia")
def guia(
    n: int,
    alumno: Alumno = Depends(alumno_aprobado),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    _modulo_abierto(con, alumno, n)
    dominio.tocar_actividad(con, alumno.id)
    frontmatter, cuerpo = _leer_md(settings.contenido_dir, f"web/guia-modulo-{n}.md", MENSAJE_GUIA)
    cuerpo = _texto_del_curso(settings, cuerpo)
    if n == MODULO_GUIA_CON_DATOS:
        cuerpo = f"{cuerpo.rstrip()}\n\n{_datos_del_dia(settings, _fila(con, alumno))}"
    return {
        "modulo": n,
        "titulo": _texto_del_curso(settings, frontmatter.get("titulo") or f"Módulo {n}"),
        "guia_md": cuerpo,
        "audio": _audio(settings.contenido_dir, n),
    }


def _datos_del_dia(settings: Settings, fila: sqlite3.Row) -> str:
    """La sección "## Datos del día" de la guía del módulo 3: los datos del machete que se vencen,
    filtrados por la herramienta y el sistema del alumno si ya los eligió, con fuente y fecha."""
    partes = ["## Datos del día\n"]
    try:
        datos = contenido.cargar_machete(settings.contenido_dir)
    except contenido.ErrorContenido as error:
        log.error("la guía del módulo 3 va sin datos del día: %s", error)
        partes.append(f"{MENSAJE_SIN_DATOS_DEL_DIA}\n")
        return "\n".join(partes)
    herramienta, sistema = fila["herramienta"], fila["sistema"]
    elegidos = [
        dato
        for dato in datos
        if dato.tema in TEMAS_DATOS_DEL_DIA
        and (herramienta is None or herramienta in dato.aplica_a)
        and (sistema not in kit.SISTEMAS or sistema in dato.sistema)
    ]
    if not elegidos:
        partes.append(f"{MENSAJE_SIN_DATOS_DEL_DIA}\n")
        return "\n".join(partes)
    partes.append(f"{INTRO_DATOS_DEL_DIA}\n")
    for tema in TEMAS_DATOS_DEL_DIA:
        del_tema = [dato for dato in elegidos if dato.tema == tema]
        if not del_tema:
            continue
        partes.append(f"### {kit.TITULOS_TEMAS.get(tema, tema)}\n")
        for dato in del_tema:
            partes.append(
                f"{dato.texto}\n\nVerificado el {contenido.fecha_corta(dato.verificado)} · Fuente: {dato.fuente}\n"
            )
    return "\n".join(partes)


@router.post("/modulos/{n}/completar")
def completar(
    n: int, alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)
) -> dict:
    _modulo_abierto(con, alumno, n)
    try:
        actual = dominio.completar_modulo(con, alumno.id, n, "guia_escrita")
    except dominio.ErrorDominio as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None
    dominio.tocar_actividad(con, alumno.id)
    return {"modulo_actual": actual}


# --- Idea ---


def _idea_o_404(con: sqlite3.Connection, alumno: Alumno) -> sqlite3.Row:
    idea = dominio.idea_vigente(con, alumno.id)
    if idea is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_SIN_IDEA)
    return idea


@router.get("/idea")
def ver_idea(alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)) -> dict:
    dominio.tocar_actividad(con, alumno.id)
    idea = _idea_o_404(con, alumno)
    return {campo: idea[campo] for campo in ("version", "texto_md", "que_sigue_md", "autor", "creado")}


@router.put("/idea")
def editar_idea(
    datos: IdeaNueva, alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)
) -> dict:
    try:
        version = dominio.guardar_idea(con, alumno.id, datos.texto_md, datos.que_sigue_md, "alumno")
    except dominio.ErrorDominio as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from None
    dominio.tocar_actividad(con, alumno.id)
    return {"version": version}


@router.get("/idea/plantilla")
def plantilla_idea(
    alumno: Alumno = Depends(alumno_aprobado), settings: Settings = Depends(get_settings)
) -> dict:
    """La plantilla de "mi idea en una página" (contenido/web/plantilla-idea.md, sin frontmatter)."""
    _, cuerpo = _leer_md(settings.contenido_dir, "web/plantilla-idea.md", MENSAJE_PLANTILLA)
    return {"texto_md": _texto_del_curso(settings, cuerpo)}


@router.get("/idea.md")
def descargar_idea(alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)) -> Response:
    idea = _idea_o_404(con, alumno)
    dominio.tocar_actividad(con, alumno.id)
    return _descarga(kit.mi_idea(idea["texto_md"], idea["que_sigue_md"]), "text/markdown", "mi-idea.md")


# --- Taller y kit ---


@router.put("/taller")
def elegir_taller(
    datos: Taller, alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)
) -> dict:
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_TALLER)
    with con:
        for columna in ("herramienta", "sistema"):
            if columna in cambios:
                con.execute(f"UPDATE alumnos SET {columna} = ? WHERE id = ?", (cambios[columna], alumno.id))
    dominio.tocar_actividad(con, alumno.id)
    fila = _fila(con, alumno)
    falta = _falta_para_kit(con, fila)
    return {"herramienta": fila["herramienta"], "sistema": fila["sistema"], "kit_habilitado": not falta, "falta": falta}


@router.get("/kit")
def bajar_kit(
    alumno: Alumno = Depends(alumno_aprobado),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> Response:
    fila = _fila(con, alumno)
    falta = _falta_para_kit(con, fila)
    if falta:
        raise HTTPException(
            status.HTTP_409_CONFLICT, {"detalle": f"{MENSAJE_KIT_FALTA} {' '.join(falta)}", "falta": falta}
        )
    idea = dominio.idea_vigente(con, alumno.id)
    herramienta, sistema = fila["herramienta"], fila["sistema"]
    try:
        zip_, nombre, metadatos = kit.armar(
            settings.contenido_dir,
            idea["texto_md"],
            idea["que_sigue_md"],
            herramienta,
            sistema,
            settings.dominio,
            autor=settings.autor_nombre,
            newsletter=settings.newsletter_nombre,
        )
    except (ValueError, OSError) as error:
        log.error("no se pudo armar el kit: %s", error)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, MENSAJE_KIT_NO_DISPONIBLE) from None
    with con:
        con.execute(
            "INSERT INTO kits (alumno_id, version_curso, fecha_machete, herramienta, sistema) VALUES (?, ?, ?, ?, ?)",
            (alumno.id, metadatos["version_curso"], metadatos["fecha_machete"], herramienta, sistema),
        )
    dominio.registrar_evento(con, alumno.id, "kit", f"herramienta={herramienta},sistema={sistema}")
    dominio.subir_modulo(con, alumno.id, dominio.MODULO_KIT)
    dominio.tocar_actividad(con, alumno.id)
    return _descarga(zip_, "application/zip", nombre)


@router.get("/kit/pasos")
def pasos_del_kit(
    alumno: Alumno = Depends(alumno_aprobado),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    """Los pasos para abrir el kit y seguir en la computadora (el LEEME del kit, en markdown).

    Solo lee: no arma el kit ni registra nada. No hace falta tener la idea, pero sí la herramienta
    y una computadora Mac o Windows.
    """
    fila = _fila(con, alumno)
    falta = _falta_del_taller(fila)
    if falta:
        raise HTTPException(
            status.HTTP_409_CONFLICT, {"detalle": f"{MENSAJE_PASOS_FALTA} {' '.join(falta)}", "falta": falta}
        )
    try:
        return kit.pasos(
            settings.contenido_dir,
            fila["herramienta"],
            fila["sistema"],
            settings.dominio,
            autor=settings.autor_nombre,
            newsletter=settings.newsletter_nombre,
        )
    except (ValueError, OSError) as error:
        log.error("no se pudieron armar los pasos del kit: %s", error)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, MENSAJE_KIT_NO_DISPONIBLE) from None


# --- Mostrar lo que hizo ---


_COLUMNAS_LINK = "id, url, titulo, mostrar_galeria, uso_contenido, aprobado, creado"
_BOOLEANOS_LINK = ("mostrar_galeria", "uso_contenido", "aprobado")


def link_json(fila: sqlite3.Row) -> dict:
    """Una fila de links como JSON, con las opciones como true o false."""
    datos = dict(fila)
    for columna in _BOOLEANOS_LINK:
        if columna in datos:
            datos[columna] = bool(datos[columna])
    return datos


def _link_propio(con: sqlite3.Connection, alumno: Alumno, link_id: int) -> sqlite3.Row:
    fila = con.execute(
        f"SELECT {_COLUMNAS_LINK} FROM links WHERE id = ? AND alumno_id = ?", (link_id, alumno.id)
    ).fetchone()
    if fila is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, MENSAJE_LINK_AJENO)
    return fila


@router.post("/links", status_code=status.HTTP_201_CREATED)
def registrar_link(
    datos: NuevoLink,
    tareas: BackgroundTasks,
    alumno: Alumno = Depends(alumno_aprobado),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    """Registra el link de la página. El mail contame sale una sola vez en la vida del alumno.

    `pregunta_siguiente_paso` dice si la web tiene que hacer la pregunta del siguiente paso: solo
    con la función activa, con el primer link del alumno y si todavía no la contestó.
    """
    if _fila(con, alumno)["modulo_actual"] < dominio.MODULO_KIT:
        raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_LINK_SIN_KIT)
    url = _url_valida(datos.url)
    titulo = _titulo_valido(datos.titulo)
    with con:
        con.execute("BEGIN IMMEDIATE")
        cantidad = con.execute("SELECT count(*) FROM links WHERE alumno_id = ?", (alumno.id,)).fetchone()[0]
        if cantidad >= MAX_LINKS:
            raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_MAX_LINKS)
        link_id = con.execute(
            "INSERT INTO links (alumno_id, url, titulo, mostrar_galeria, uso_contenido) VALUES (?, ?, ?, ?, ?)",
            (alumno.id, url, titulo, int(datos.mostrar_galeria), int(datos.uso_contenido)),
        ).lastrowid
    dominio.registrar_evento(con, alumno.id, "link")
    pregunta = settings.hay_siguiente_paso and dominio.toca_preguntar_siguiente_paso(con, alumno.id)
    dominio.subir_modulo(con, alumno.id, MODULO_LINK)
    dominio.tocar_actividad(con, alumno.id)
    mail = mails.contame_pendiente(con, alumno.id)
    if mail:
        tareas.add_task(mails.enviar, settings, alumno.id, "contame", mails.CLAVE_CONTAME, {"link": url, "titulo": titulo})
    return {"id": link_id, "mail": mail, "pregunta_siguiente_paso": pregunta}


@router.get("/links")
def mis_links(alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)) -> list[dict]:
    filas = con.execute(f"SELECT {_COLUMNAS_LINK} FROM links WHERE alumno_id = ? ORDER BY id", (alumno.id,))
    return [link_json(fila) for fila in filas]


@router.patch("/links/{link_id}")
def cambiar_link(
    link_id: int,
    datos: CambioLink,
    alumno: Alumno = Depends(alumno_aprobado),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    _link_propio(con, alumno, link_id)
    cambios = {campo: valor for campo, valor in datos.model_dump(exclude_unset=True).items() if valor is not None}
    if not cambios:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_SIN_CAMBIOS)
    with con:
        for campo, valor in cambios.items():
            con.execute(f"UPDATE links SET {campo} = ? WHERE id = ? AND alumno_id = ?", (int(valor), link_id, alumno.id))
    dominio.tocar_actividad(con, alumno.id)
    return link_json(_link_propio(con, alumno, link_id))


@router.delete("/links/{link_id}")
def borrar_link(
    link_id: int, alumno: Alumno = Depends(alumno_aprobado), con: sqlite3.Connection = Depends(conexion)
) -> dict:
    _link_propio(con, alumno, link_id)
    with con:
        con.execute("DELETE FROM links WHERE id = ? AND alumno_id = ?", (link_id, alumno.id))
    dominio.tocar_actividad(con, alumno.id)
    return {"ok": True}


@router.get("/galeria")
def galeria(con: sqlite3.Connection = Depends(conexion)) -> list[dict]:
    """Solo los links que el alumno quiso mostrar y que aprobó quien administra el curso."""
    return _filas(
        con,
        "SELECT titulo, url FROM links WHERE mostrar_galeria = 1 AND aprobado = 1 ORDER BY id DESC LIMIT ?",
        LIMITE_GALERIA,
    )


# --- Siguiente paso (spec 002) ---


@router.post("/siguiente-paso")
def responder_siguiente_paso(
    datos: RespuestaSiguientePaso,
    alumno: Alumno = Depends(alumno_aprobado),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    """La respuesta a la pregunta que llega con el primer link. Se cuenta sin guardar quién contestó
    (FR-012): del alumno queda solo que ya contestó y, si contestó que sí y lo pidió, el aviso."""
    if datos.aviso and datos.respuesta != "si":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_AVISO_SIN_NEGOCIO)
    if not settings.hay_siguiente_paso:
        raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_SIN_SIGUIENTE_PASO)
    version = contenido.version_legal(settings.contenido_dir)
    try:
        dominio.contestar_siguiente_paso(con, alumno.id, datos.respuesta, datos.aviso, version)
    except dominio.ErrorDominio as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None
    dominio.tocar_actividad(con, alumno.id)
    return {"consentimientos": _consentimientos(con, alumno.id)}


# --- Datos del alumno ---


@router.put("/consentimientos")
def cambiar_consentimientos(
    datos: CambioConsentimientos,
    alumno: Alumno = Depends(alumno_actual),
    settings: Settings = Depends(get_settings),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    cambios = {tipo: valor for tipo, valor in datos.model_dump(exclude_unset=True).items() if valor is not None}
    if not cambios:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MENSAJE_SIN_CAMBIOS)
    if cambios.get("novedades") and not settings.hay_newsletter:
        raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_SIN_NOVEDADES)
    # El aviso del siguiente paso se pide solo con la función activa, pero se saca siempre: así
    # quien lo pidió lo puede sacar aunque la función se haya apagado después.
    if cambios.get("siguiente_paso") and not settings.hay_siguiente_paso:
        raise HTTPException(status.HTTP_409_CONFLICT, MENSAJE_SIN_AVISO_SIGUIENTE_PASO)
    version = contenido.version_legal(settings.contenido_dir)
    for tipo, valor in cambios.items():
        antes = dominio.consentimiento(con, alumno.id, tipo)
        dominio.agregar_consentimiento(con, alumno.id, tipo, valor, version)
        if tipo == "mails_curso" and antes and not valor:
            dominio.registrar_evento(con, alumno.id, "baja_mails")
    dominio.tocar_actividad(con, alumno.id)
    return _consentimientos(con, alumno.id)


@router.get("/mis-datos")
def mis_datos(alumno: Alumno = Depends(alumno_actual), con: sqlite3.Connection = Depends(conexion)) -> Response:
    dominio.tocar_actividad(con, alumno.id)
    fila = _fila(con, alumno)
    datos = {
        "exportado": _ahora(),
        "alumno": {
            **{
                campo: fila[campo]
                for campo in (
                    "email", "creado", "ultima_actividad", "herramienta", "sistema", "modulo_actual", "fuente", "estado"
                )
            },
            # Si ya contestó la pregunta del siguiente paso; qué contestó no se guarda (spec 002, FR-012).
            "siguiente_paso_respondido": bool(fila["siguiente_paso_respondido"]),
        },
        "consentimientos": [
            {**c, "valor": bool(c["valor"])}
            for c in _filas(
                con,
                "SELECT tipo, valor, version_texto, creado FROM consentimientos WHERE alumno_id = ? ORDER BY id",
                alumno.id,
            )
        ],
        "avance": _filas(
            con, "SELECT modulo, completado, resumen, via FROM avance WHERE alumno_id = ? ORDER BY modulo", alumno.id
        ),
        "ideas": _filas(
            con,
            "SELECT version, texto_md, que_sigue_md, autor, creado FROM ideas WHERE alumno_id = ? ORDER BY version",
            alumno.id,
        ),
        "conversaciones": _conversaciones(con, alumno.id),
        "kits": _filas(
            con,
            "SELECT creado, version_curso, fecha_machete, herramienta, sistema FROM kits WHERE alumno_id = ? ORDER BY id",
            alumno.id,
        ),
        "links": [
            link_json(fila)
            for fila in con.execute(
                "SELECT url, titulo, mostrar_galeria, uso_contenido, aprobado, creado FROM links"
                " WHERE alumno_id = ? ORDER BY id",
                (alumno.id,),
            )
        ],
        "mails": _filas(con, "SELECT tipo, estado, creado FROM mails WHERE alumno_id = ? ORDER BY id", alumno.id),
    }
    return _descarga(json.dumps(datos, ensure_ascii=False, indent=2), "application/json", "mis-datos.json")


@router.delete("/mis-datos")
def borrar_mis_datos(
    datos: Borrado,
    response: Response,
    alumno: Alumno = Depends(alumno_actual),
    con: sqlite3.Connection = Depends(conexion),
) -> dict:
    if datos.confirmar != CONFIRMAR_BORRADO:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, MENSAJE_BORRAR)
    with con:
        con.execute("DELETE FROM codigos WHERE email = ?", (alumno.email,))
        con.execute("DELETE FROM alumnos WHERE id = ?", (alumno.id,))
        con.execute("INSERT INTO eventos (alumno_id, tipo) VALUES (NULL, 'borrado')")
    auth.borrar_cookie(response)
    log.info("se borraron los datos de un alumno a su pedido")
    return {"ok": True}


# --- Textos legales (públicos) ---


@router.get("/legal/privacidad")
def privacidad(settings: Settings = Depends(get_settings)) -> dict:
    frontmatter, cuerpo = _leer_md(settings.contenido_dir, "legal/privacidad.md", MENSAJE_PRIVACIDAD)
    return {
        "version": str(frontmatter.get("version") or "borrador"),
        "titulo": _texto_del_curso(settings, frontmatter.get("titulo") or "Aviso de privacidad"),
        "texto_md": _texto_del_curso(settings, cuerpo),
    }


@router.get("/legal/consentimientos")
def textos_consentimientos(settings: Settings = Depends(get_settings)) -> dict:
    frontmatter, cuerpo = _leer_md(settings.contenido_dir, "legal/consentimientos.md", MENSAJE_CONSENTIMIENTOS)
    return {
        "version": str(frontmatter.get("version") or "borrador"),
        "textos": {
            tipo: _texto_del_curso(settings, frontmatter.get(tipo) or "").strip() for tipo in TEXTOS_CONSENTIMIENTO
        },
        "texto_md": _texto_del_curso(settings, cuerpo),
    }
