"""Contenido del curso: archivos versionados en contenido/, leídos de disco en cada pedido.

El machete (contenido/machete.yaml) guarda los datos que se vencen, con fuente oficial, fecha de
verificación y si se probaron en la realidad (Constitución IV).

Los textos pueden llevar {{AUTOR}} y {{NEWSLETTER}}, que dependen de quien opera el curso (AUTOR_NOMBRE
y NEWSLETTER_NOMBRE en la configuración); `reemplazar_marcadores` los llena al servir o armar cada texto.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import yaml

from vibe_tutor.costos import ZONA_ARGENTINA

ARCHIVO_MACHETE = "machete.yaml"
AUTOR_POR_DEFECTO = "el autor del curso"
MARCADORES_DEL_CURSO = frozenset({"AUTOR", "NEWSLETTER"})
TEMAS = frozenset({"instalar", "planes", "publicar", "ver", "volver-atras", "limites", "ayuda"})
HERRAMIENTAS = frozenset({"codex", "claude"})
SISTEMAS = frozenset({"mac", "windows"})
MAX_TEXTO = 1500
DIAS_VIGENCIA = 45
CAMPOS = ("id", "tema", "aplica_a", "sistema", "texto", "fuente", "verificado", "probado")
_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_GRATIS = re.compile(
    r"\b(?:gratis|gratuit[oa]s?|sin pagar|sin costo|no tiene costo|sin tarjeta|no pide tarjeta|no hace falta tarjeta"
    r"|plan\s+[\"'“«]?free|free[\"'”»]?\s+plan)\b",
    re.IGNORECASE,
)


class ErrorContenido(ValueError):
    pass


@dataclass(frozen=True)
class Dato:
    id: str
    tema: str
    aplica_a: tuple[str, ...]
    sistema: tuple[str, ...]
    texto: str
    fuente: str
    verificado: date
    probado: bool


def _hoy() -> date:
    return datetime.now(ZONA_ARGENTINA).date()


def _lista(crudo: dict, campo: str, permitidos: frozenset[str], id_: str) -> tuple[str, ...]:
    valor = crudo[campo]
    if not isinstance(valor, list) or not valor or not set(valor) <= permitidos:
        raise ErrorContenido(f"{id_}: {campo} tiene que ser una lista con valores de {sorted(permitidos)}")
    return tuple(valor)


def _dato(crudo: object, hoy: date) -> Dato:
    if not isinstance(crudo, dict):
        raise ErrorContenido("cada dato del machete tiene que ser un diccionario")
    faltantes = [campo for campo in CAMPOS if campo not in crudo]
    id_ = str(crudo.get("id", "?"))
    if faltantes:
        raise ErrorContenido(f"{id_}: faltan campos: {', '.join(faltantes)}")
    if not isinstance(crudo["id"], str) or not _ID.match(crudo["id"]):
        raise ErrorContenido(f"{id_}: el id tiene que ser un slug en minúsculas con guiones")
    if crudo["tema"] not in TEMAS:
        raise ErrorContenido(f"{id_}: tema desconocido; los válidos son {sorted(TEMAS)}")
    texto = crudo["texto"]
    if not isinstance(texto, str) or not texto.strip() or len(texto) > MAX_TEXTO:
        raise ErrorContenido(f"{id_}: el texto tiene que tener entre 1 y {MAX_TEXTO} caracteres")
    fuente = crudo["fuente"]
    if not isinstance(fuente, str) or not fuente.startswith("https://"):
        raise ErrorContenido(f"{id_}: la fuente tiene que ser una URL que empiece con https://")
    try:
        verificado = date.fromisoformat(str(crudo["verificado"]))
    except ValueError:
        raise ErrorContenido(f"{id_}: la fecha de verificación tiene que ser AAAA-MM-DD") from None
    if verificado > hoy:
        raise ErrorContenido(f"{id_}: la fecha de verificación es futura")
    if not isinstance(crudo["probado"], bool):
        raise ErrorContenido(f"{id_}: probado tiene que ser true o false")
    if _GRATIS.search(texto) and not crudo["probado"]:
        raise ErrorContenido(f"{id_}: dice gratis pero no está probado en la realidad (Constitución IV)")
    return Dato(
        id=crudo["id"],
        tema=crudo["tema"],
        aplica_a=_lista(crudo, "aplica_a", HERRAMIENTAS, id_),
        sistema=_lista(crudo, "sistema", SISTEMAS, id_),
        texto=texto.strip(),
        fuente=fuente,
        verificado=verificado,
        probado=crudo["probado"],
    )


def cargar_machete(raiz: Path, hoy: date | None = None) -> list[Dato]:
    texto = leer(raiz, ARCHIVO_MACHETE)
    try:
        crudos = yaml.safe_load(texto) or []
    except yaml.YAMLError as error:
        raise ErrorContenido(f"machete.yaml no es YAML válido: {error}") from None
    if not isinstance(crudos, list):
        raise ErrorContenido("machete.yaml tiene que ser una lista de datos")
    hoy = hoy or _hoy()
    datos = [_dato(crudo, hoy) for crudo in crudos]
    vistos: set[str] = set()
    for dato in datos:
        if dato.id in vistos:
            raise ErrorContenido(f"{dato.id}: id repetido")
        vistos.add(dato.id)
    return datos


def filtrar(datos: list[Dato], *, herramienta: str, sistema: str) -> list[Dato]:
    return [d for d in datos if herramienta in d.aplica_a and sistema in d.sistema]


def fecha_mas_vieja(datos: list[Dato]) -> date:
    return min(d.verificado for d in datos)


def fecha_corta(fecha: date) -> str:
    """Una fecha como la escribimos para las personas: 28/9/2026."""
    return f"{fecha.day}/{fecha.month}/{fecha.year}"


def vencidos(datos: list[Dato], hoy: date | None = None, dias: int = DIAS_VIGENCIA) -> list[Dato]:
    hoy = hoy or _hoy()
    return [d for d in datos if (hoy - d.verificado).days > dias]


def leer(raiz: Path, ruta: str) -> str:
    """Lee un archivo de texto de contenido/, siempre desde disco y sin salir de la carpeta."""
    base = Path(raiz).resolve()
    destino = (base / ruta).resolve()
    if not destino.is_relative_to(base):
        raise ErrorContenido(f"{ruta}: queda fuera de la carpeta de contenido")
    if not destino.is_file():
        raise ErrorContenido(f"{ruta}: no existe")
    return destino.read_text(encoding="utf-8")


_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


def separar_frontmatter(texto: str) -> tuple[dict, str]:
    """Devuelve el frontmatter YAML (o {} si no hay) y el cuerpo sin él."""
    encontrado = _FRONTMATTER.match(texto)
    if not encontrado:
        return {}, texto
    datos = yaml.safe_load(encontrado.group(1)) or {}
    if not isinstance(datos, dict):
        raise ErrorContenido("el frontmatter no es un mapa")
    return datos, texto[encontrado.end():].lstrip("\n")


def version_legal(raiz: Path) -> str:
    """Versión de los textos de consentimiento que se muestran al inscribirse."""
    try:
        datos, _ = separar_frontmatter(leer(raiz, "legal/consentimientos.md"))
    except ErrorContenido:
        return "borrador"
    return str(datos.get("version") or "borrador")


def valores_del_curso(autor_nombre: str | None, newsletter_nombre: str | None) -> dict[str, str]:
    """Los valores de {{AUTOR}} y {{NEWSLETTER}}: sin autor, "el autor del curso"; sin newsletter, vacío."""
    return {
        "AUTOR": " ".join((autor_nombre or "").split()) or AUTOR_POR_DEFECTO,
        "NEWSLETTER": " ".join((newsletter_nombre or "").split()),
    }


def reemplazar(texto: str, valores: Mapping[str, str]) -> str:
    """Reemplaza cada {{NOMBRE}} de `valores` por su valor; los demás marcadores quedan como están."""
    for nombre, valor in valores.items():
        texto = texto.replace("{{" + nombre + "}}", valor)
    return texto


def reemplazar_marcadores(texto: str, settings: object | None) -> str:
    """Llena {{AUTOR}} y {{NEWSLETTER}} con la configuración (autor_nombre y newsletter_nombre).

    Sin configuración (None) usa los valores por defecto. La usan el prompt del tutor, las guías,
    los textos legales y los mails; el kit suma `valores_del_curso` a sus propios marcadores.
    """
    newsletter = getattr(settings, "newsletter_nombre", None)
    valores = valores_del_curso(getattr(settings, "autor_nombre", None), newsletter)
    return reemplazar(_bloques_de_newsletter(texto, bool((newsletter or "").strip())), valores)


# {{#NEWSLETTER}}...{{/NEWSLETTER}}: se deja (sin las marcas) solo si el curso tiene newsletter.
# Un bloque en líneas propias se lleva también su salto de línea.
_BLOQUE_NEWSLETTER = re.compile(r"\{\{#NEWSLETTER\}\}(\n?)(.*?)\{\{/NEWSLETTER\}\}(\n?)", re.DOTALL)


def _bloques_de_newsletter(texto: str, hay_newsletter: bool) -> str:
    if hay_newsletter:
        return _BLOQUE_NEWSLETTER.sub(lambda m: m.group(2) + (m.group(3) if not m.group(1) else ""), texto)
    return _BLOQUE_NEWSLETTER.sub(lambda m: m.group(3) if not m.group(1) else "", texto)
