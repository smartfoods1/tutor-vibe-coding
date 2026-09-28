"""Armado del kit (contracts/kit.md): un zip en memoria, personalizado para cada alumno.

La plantilla vive en contenido/kit/. El armado copia la plantilla, reemplaza los marcadores en los
archivos de texto y genera lo que es de cada alumno: mi-idea.md, curso/machete.md (filtrado por
herramienta y sistema), curso/VERSION y LEEME.txt. Las skills se copian a .claude/skills y a
.agents/skills, sin enlaces simbólicos. El marcador {{AYUDA}} de AGENTS.md se llena con los datos
del tema "ayuda" del machete y su fecha de verificación: las líneas de ayuda no se escriben a mano.
{{AUTOR}} y {{NEWSLETTER}} se llenan con los datos de quien opera el curso (contenido.valores_del_curso).

También se usa sin la web:
    python -m vibe_tutor.kit --idea idea.md --herramienta codex --sistema mac --salida kit.zip
Sin --dominio (ni la variable DOMINIO) los links del kit apuntan al curso corriendo en la computadora
(localhost:5173); --autor y --newsletter (o AUTOR_NOMBRE y NEWSLETTER_NOMBRE) son opcionales.
"""

import argparse
import html
import io
import os
import re
import stat
import sys
import unicodedata
import zipfile
from datetime import date, datetime
from pathlib import Path

from vibe_tutor import contenido
from vibe_tutor.costos import ZONA_ARGENTINA

CARPETA_PLANTILLA = "kit"
ARCHIVO_VERSION = "VERSION"
HERRAMIENTAS = {"codex": "Codex", "claude": "Claude"}
SISTEMAS = {"mac": "Mac", "windows": "Windows"}
OBLIGATORIOS = ("AGENTS.md", "CLAUDE.md", "bitacora.md")
GENERADOS = frozenset({"LEEME.txt", "mi-idea.md", "curso/machete.md", "curso/VERSION"})
IGNORADOS = frozenset({".DS_Store", "Thumbs.db", "desktop.ini", ".gitkeep"})
EXTENSIONES_TEXTO = (".md", ".txt", ".html")
TITULO_POR_DEFECTO = "Mi idea"
SLUG_POR_DEFECTO = "mi-idea"
VERSION_POR_DEFECTO = "desarrollo"
MAX_TITULO = 80
MAX_SLUG = 40
MAX_VERSION = 64
SIN_QUE_SIGUE = "Todavía no hay nada anotado."
LEEME_VERSIONES = (
    "Acá se guardan las copias de la carpeta sitio/ que hace \"guardar versión\", "
    "una carpeta por fecha y hora.\n"
)
TITULOS_TEMAS = {
    "planes": "Planes y costos",
    "instalar": "Instalar",
    "ver": "Ver la página en la computadora",
    "publicar": "Publicar",
    "limites": "Límites",
    "volver-atras": "Volver atrás",
    "ayuda": "Ayuda ante un malestar serio",
}
TEMA_AYUDA = "ayuda"
MARCADOR_AYUDA = "{{AYUDA}}"
CONTENIDO_REPO = Path(__file__).resolve().parents[2] / "contenido"
DOMINIO_POR_DEFECTO = "localhost:5173"

_TITULO = re.compile(r"^#[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
_QUE_SIGUE = re.compile(r"^#{1,6}[ \t]+qu[eé] sigue\b", re.IGNORECASE | re.MULTILINE)


class ErrorKit(ValueError):
    """Un pedido de kit con datos que el curso no admite (herramienta o sistema)."""


def hoy_argentina() -> date:
    return datetime.now(ZONA_ARGENTINA).date()


def titulo_de(idea_md: str) -> str:
    """El primer título "# " de la idea, sin formato; "Mi idea" si no hay."""
    for linea in (idea_md or "").splitlines():
        encontrado = _TITULO.match(linea)
        if encontrado:
            titulo = " ".join(re.sub(r"[*_`]+", "", encontrado.group(1)).split())
            return titulo[:MAX_TITULO].strip() or TITULO_POR_DEFECTO
    return TITULO_POR_DEFECTO


def slug(titulo: str) -> str:
    """Nombre para archivos: minúsculas, sin acentos ni espacios, con guiones."""
    ascii_ = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode("ascii")
    resultado = re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
    if len(resultado) > MAX_SLUG:
        corto = resultado[:MAX_SLUG]
        if resultado[MAX_SLUG] != "-" and "-" in corto:
            corto = corto.rsplit("-", 1)[0]
        resultado = corto.strip("-")
    return resultado or SLUG_POR_DEFECTO


def mi_idea(texto_md: str, que_sigue_md: str | None) -> str:
    """mi-idea.md: la idea vigente y, al final, la sección "Qué sigue"."""
    texto = (texto_md or "").strip()
    que_sigue = (que_sigue_md or "").strip()
    primera, _, resto = que_sigue.partition("\n")
    if _QUE_SIGUE.match(primera):
        que_sigue = resto.strip()
    if que_sigue:
        return f"{texto}\n\n## Qué sigue\n\n{que_sigue}\n"
    if _QUE_SIGUE.search(texto):
        return f"{texto}\n"
    return f"{texto}\n\n## Qué sigue\n\n{SIN_QUE_SIGUE}\n"


def _dominio(dominio: str) -> str:
    return re.sub(r"^https?://", "", dominio.strip()).rstrip("/")


def url_del_curso(dominio: str) -> str:
    """La dirección del curso: https, salvo el curso corriendo en la computadora (localhost), que va por http."""
    host = _dominio(dominio)
    local = re.match(r"^(?:localhost|127\.0\.0\.1)(?::\d+)?$", host)
    return f"{'http' if local else 'https'}://{host}"


def _destinos(ruta: str, herramienta: str) -> list[str]:
    """Adónde va cada archivo de la plantilla dentro del kit."""
    if ruta.startswith("LEEME-") and ruta.endswith(".txt") and "/" not in ruta:
        return ["LEEME.txt"] if ruta == f"LEEME-{herramienta}.txt" else []
    if ruta == "claude-settings.json":
        return [".claude/settings.json"]
    if ruta.startswith("skills/"):
        resto = ruta.removeprefix("skills/")
        return [f".claude/skills/{resto}", f".agents/skills/{resto}"]
    if ruta in GENERADOS:
        return []
    return [ruta]


def _leer_plantilla(plantilla: Path, herramienta: str) -> dict[str, bytes]:
    if not plantilla.is_dir():
        raise contenido.ErrorContenido(f"no existe la plantilla del kit ({plantilla})")
    faltantes = [r for r in (*OBLIGATORIOS, f"LEEME-{herramienta}.txt") if not (plantilla / r).is_file()]
    if faltantes:
        raise contenido.ErrorContenido(f"a la plantilla del kit le faltan: {', '.join(faltantes)}")
    archivos: dict[str, bytes] = {}
    for carpeta, subcarpetas, nombres in os.walk(plantilla):
        subcarpetas.sort()
        for nombre in sorted(nombres):
            origen = Path(carpeta) / nombre
            if nombre in IGNORADOS or nombre.startswith("._") or origen.is_symlink():
                continue
            ruta = origen.relative_to(plantilla).as_posix()
            destinos = _destinos(ruta, herramienta)
            if destinos:
                datos = origen.read_bytes()
                for destino in destinos:
                    archivos[destino] = datos
    return archivos


def _reemplazar(texto: str, marcadores: dict[str, str], es_html: bool) -> str:
    for nombre, valor in marcadores.items():
        texto = texto.replace("{{" + nombre + "}}", html.escape(valor) if es_html else valor)
    return texto


def _version_curso(raiz: Path) -> str:
    try:
        texto = contenido.leer(raiz, ARCHIVO_VERSION)
    except contenido.ErrorContenido:
        return VERSION_POR_DEFECTO
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    return lineas[0][:MAX_VERSION] if lineas else VERSION_POR_DEFECTO


def _ayuda(datos: list[contenido.Dato]) -> str:
    """El bloque {{AYUDA}} de AGENTS.md: los recursos de ayuda del machete, tal cual, con su fecha."""
    ayuda = [dato for dato in datos if dato.tema == TEMA_AYUDA]
    if not ayuda:
        raise contenido.ErrorContenido("el machete no tiene datos de ayuda para AGENTS.md")
    lineas = [f"- {' '.join(dato.texto.split())}" for dato in ayuda]
    fecha = contenido.fecha_corta(contenido.fecha_mas_vieja(ayuda))
    return "\n".join(lineas) + f"\n\nDatos verificados el {fecha}; las fuentes están en `curso/machete.md`."


def _machete_md(datos: list[contenido.Dato], herramienta: str, sistema: str, hoy: date, fecha: str) -> str:
    partes = [
        "# Machete\n",
        "Datos que cambian seguido (planes, instalación, cómo ver y publicar tu página, límites y "
        "ayuda), con la fuente oficial de cada uno y la fecha en que se verificó. Si algo de acá no "
        "coincide con lo que ves en tu pantalla, hacé caso a la pantalla y contáselo al tutor.\n",
        f"Armado para {HERRAMIENTAS[herramienta]} en {SISTEMAS[sistema]} el {hoy.isoformat()}. "
        f"El dato más viejo se verificó el {fecha}.\n",
    ]
    temas = [*TITULOS_TEMAS, *sorted({d.tema for d in datos} - set(TITULOS_TEMAS))]
    for tema in temas:
        del_tema = [d for d in datos if d.tema == tema]
        if not del_tema:
            continue
        partes.append(f"## {TITULOS_TEMAS.get(tema, tema)}\n")
        for dato in del_tema:
            pie = f"Fuente: {dato.fuente} · Verificado: {dato.verificado.isoformat()}"
            if tema != TEMA_AYUDA:
                pie += f" · Probado en la realidad: {'sí' if dato.probado else 'todavía no'}"
            partes.append(f"{dato.texto}\n\n{pie}\n")
    return "\n".join(partes)


def _version_txt(version: str, fecha_machete: str, hoy: date, herramienta: str, sistema: str) -> str:
    return (
        f"curso: {version}\n"
        f"kit armado: {hoy.isoformat()} ({HERRAMIENTAS[herramienta]} en {SISTEMAS[sistema]})\n"
        f"machete verificado: {fecha_machete} (dato más viejo)\n"
    )


def _zip(carpeta: str, archivos: dict[str, bytes], hoy: date) -> bytes:
    """Zip determinista: mismas entradas, mismos bytes. Solo archivos comunes."""
    buffer = io.BytesIO()
    momento = (hoy.year, hoy.month, hoy.day, 0, 0, 0)
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archivo:
        for ruta in sorted(archivos):
            info = zipfile.ZipInfo(f"{carpeta}/{ruta}", date_time=momento)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archivo.writestr(info, archivos[ruta])
    return buffer.getvalue()


def armar(
    contenido_dir: Path,
    idea_md: str,
    que_sigue_md: str | None,
    herramienta: str,
    sistema: str,
    dominio: str,
    hoy: date | None = None,
    *,
    autor: str | None = None,
    newsletter: str | None = None,
) -> tuple[bytes, str, dict[str, str]]:
    """Arma el kit y devuelve (bytes del zip, nombre del zip, {version_curso, fecha_machete}).

    `autor` y `newsletter` llenan {{AUTOR}} y {{NEWSLETTER}} (sin autor: "el autor del curso").
    """
    if herramienta not in HERRAMIENTAS:
        raise ErrorKit(f"herramienta desconocida: {herramienta}")
    if sistema not in SISTEMAS:
        raise ErrorKit(f"el kit es para Mac o Windows, no para {sistema}")
    raiz = Path(contenido_dir)
    hoy = hoy or hoy_argentina()
    plantilla = _leer_plantilla(raiz / CARPETA_PLANTILLA, herramienta)
    datos = contenido.filtrar(contenido.cargar_machete(raiz, hoy=hoy), herramienta=herramienta, sistema=sistema)
    if not datos:
        raise contenido.ErrorContenido(f"el machete no tiene datos para {herramienta} en {sistema}")
    fecha_machete = contenido.fecha_mas_vieja(datos).isoformat()
    version_curso = _version_curso(raiz)
    titulo = titulo_de(idea_md)
    url_curso = url_del_curso(dominio)
    marcadores = {
        "TITULO": titulo,
        "URL_CURSO": url_curso,
        "URL_AUDIOS": f"{url_curso}/audios",
        "HERRAMIENTA": HERRAMIENTAS[herramienta],
        "SISTEMA": SISTEMAS[sistema],
        "FECHA": hoy.isoformat(),
        **contenido.valores_del_curso(autor, newsletter),
    }
    if MARCADOR_AYUDA.encode() in plantilla["AGENTS.md"]:
        marcadores["AYUDA"] = _ayuda(datos)
    archivos: dict[str, bytes] = {}
    for ruta, crudo in plantilla.items():
        if ruta.endswith(EXTENSIONES_TEXTO):
            crudo = _reemplazar(crudo.decode("utf-8"), marcadores, ruta.endswith(".html")).encode("utf-8")
        archivos[ruta] = crudo
    archivos.setdefault("versiones/LEEME.txt", LEEME_VERSIONES.encode("utf-8"))
    archivos["mi-idea.md"] = mi_idea(idea_md, que_sigue_md).encode("utf-8")
    archivos["curso/machete.md"] = _machete_md(datos, herramienta, sistema, hoy, fecha_machete).encode("utf-8")
    archivos["curso/VERSION"] = _version_txt(version_curso, fecha_machete, hoy, herramienta, sistema).encode("utf-8")
    carpeta = f"mi-proyecto-{slug(titulo)}"
    metadatos = {"version_curso": version_curso, "fecha_machete": fecha_machete}
    return _zip(carpeta, archivos, hoy), f"{carpeta}.zip", metadatos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m vibe_tutor.kit", description="Arma el kit del curso para una idea, sin pasar por la web."
    )
    parser.add_argument("--idea", required=True, type=Path, help="archivo .md con la idea en una página")
    parser.add_argument("--herramienta", required=True, choices=sorted(HERRAMIENTAS))
    parser.add_argument("--sistema", required=True, choices=sorted(SISTEMAS))
    parser.add_argument("--salida", type=Path, default=Path("."), help="archivo .zip o carpeta donde dejarlo")
    parser.add_argument("--que-sigue", type=Path, help="archivo .md con lo que queda para después (opcional)")
    parser.add_argument("--contenido", type=Path, default=Path(os.environ.get("CONTENIDO_DIR") or CONTENIDO_REPO))
    parser.add_argument(
        "--dominio",
        default=os.environ.get("DOMINIO") or DOMINIO_POR_DEFECTO,
        help=f"dirección del curso para los links del kit (por defecto, DOMINIO o {DOMINIO_POR_DEFECTO})",
    )
    parser.add_argument(
        "--autor", default=os.environ.get("AUTOR_NOMBRE", ""), help="quien opera el curso (por defecto, AUTOR_NOMBRE)"
    )
    parser.add_argument(
        "--newsletter",
        default=os.environ.get("NEWSLETTER_NOMBRE", ""),
        help="nombre de la lista de novedades (por defecto, NEWSLETTER_NOMBRE)",
    )
    args = parser.parse_args(argv)
    try:
        idea = args.idea.read_text(encoding="utf-8")
        que_sigue = args.que_sigue.read_text(encoding="utf-8") if args.que_sigue else None
        datos, nombre, metadatos = armar(
            args.contenido,
            idea,
            que_sigue,
            args.herramienta,
            args.sistema,
            args.dominio,
            autor=args.autor,
            newsletter=args.newsletter,
        )
        destino = args.salida / nombre if args.salida.is_dir() else args.salida
        destino.write_bytes(datos)
    except (OSError, UnicodeDecodeError, contenido.ErrorContenido, ErrorKit) as error:
        parser.exit(1, f"No se pudo armar el kit: {error}\n")
    print(f"Kit armado: {destino}")
    print(f"Versión del curso: {metadatos['version_curso']} · machete verificado: {metadatos['fecha_machete']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
