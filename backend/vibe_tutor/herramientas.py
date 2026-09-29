"""Herramientas del tutor de la web (módulos 1 a 3).

Los esquemas que van a la API no llevan límites de largo (el modo estricto no los acepta): los
límites se validan acá, antes de tocar la base. Lo que el modelo manda es dato, nunca instrucción.
"""

import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

from vibe_tutor import contenido, dominio

log = logging.getLogger("vibe_tutor.herramientas")

MAX_LINEAS_RESUMEN = 5
TEMAS = sorted(contenido.TEMAS)
TODOS = "todos"
HERRAMIENTAS_TALLER = ["codex", "claude"]
SISTEMAS_TALLER = ["mac", "windows", "otro"]
TIPOS = {
    "string": "texto",
    "integer": "entero",
    "number": "número",
    "boolean": "true o false",
    "array": "lista",
    "object": "objeto",
    "null": "null",
}
# Mails y números largos (teléfonos, documentos): el resumen del módulo no lleva datos personales.
_MAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_NUMERO_LARGO = re.compile(r"(?<!\d)\d(?:[\s.\-]?\d){6,}(?!\d)")
_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def _tool(nombre: str, descripcion: str, propiedades: dict) -> dict:
    return {
        "name": nombre,
        "description": descripcion,
        "strict": True,
        "eager_input_streaming": True,
        "input_schema": {
            "type": "object",
            "properties": propiedades,
            "required": list(propiedades),
            "additionalProperties": False,
        },
    }


def _campo(tipo, descripcion: str, **extra) -> dict:
    return {"type": tipo, "description": descripcion, **extra}


_DEFINICIONES: dict[str, dict] = {
    "guardar_idea": _tool(
        "guardar_idea",
        "Guarda una versión nueva de \"mi idea en una página\" del alumno. Cada llamada crea una versión "
        "(no borra las anteriores). El alumno la ve, la puede editar y descargar. Usala cuando la entrevista "
        f"del módulo 2 llegó a una página completa, o para corregirla. Hasta {dominio.MAX_IDEA} caracteres.",
        {
            "texto_md": _campo(
                "string",
                "La página completa en markdown: qué es; para quién; qué siente cuando la imagina funcionando "
                "y por qué le importa; la versión más chica que ya valdría la pena; el molde; lo que la máquina "
                "no puede adivinar; sé que funciona si. Empieza con un título '# ...'. Sin datos de salud.",
            ),
            "que_sigue_md": _campo(
                ["string", "null"],
                f"Lo que quedó afuera de la primera versión (logins, pagos, datos compartidos), en markdown, "
                f"hasta {dominio.MAX_QUE_SIGUE} caracteres; null si no hay nada.",
            ),
        },
    ),
    "marcar_avance": _tool(
        "marcar_avance",
        "Marca como completo el módulo de esta conversación, cuando el alumno ya hizo lo que pide el "
        "módulo. Deja un resumen para el tutor del módulo siguiente. En el módulo 2 exige una idea guardada.",
        {
            "modulo": _campo("integer", "El número del módulo de esta conversación.", enum=[1, 2, 3]),
            "resumen": _campo(
                "string",
                f"De 2 a {MAX_LINEAS_RESUMEN} líneas, hasta {dominio.MAX_RESUMEN} caracteres, para el módulo "
                "siguiente: qué quedó decidido y categorías genéricas (por ejemplo, 'miedo: costo'). Sin nombres, "
                "mails, teléfonos, edad, frases textuales ni datos de salud.",
            ),
        },
    ),
    "consultar_machete": _tool(
        "consultar_machete",
        "Devuelve los datos que se vencen (planes, precios, pasos para instalar, publicar, ver la página, "
        "volver atrás, límites), con su fuente, fecha de verificación y si se probó en la realidad. Filtra "
        "por la herramienta y el sistema del alumno si ya los eligió. Usala siempre antes de dar uno de "
        "esos datos: nunca los des de memoria.",
        {"tema": _campo("string", "Tema a consultar, o 'todos'.", enum=[*TEMAS, TODOS])},
    ),
    "registrar_taller": _tool(
        "registrar_taller",
        "Guarda la herramienta y el sistema que eligió el alumno para los módulos 4 a 7. Con sistema 'otro' "
        "(celular, tablet o Linux) el kit no se habilita, pero su avance queda guardado.",
        {
            "herramienta": _campo("string", "codex (app de ChatGPT en modo Codex) o claude (app de Claude).", enum=HERRAMIENTAS_TALLER),
            "sistema": _campo("string", "mac, windows u otro.", enum=SISTEMAS_TALLER),
        },
    ),
}

POR_MODULO: dict[int, tuple[str, ...]] = {
    1: ("marcar_avance",),
    2: ("guardar_idea", "marcar_avance"),
    3: ("consultar_machete", "registrar_taller", "guardar_idea", "marcar_avance"),
}
_VALIDADORES = {nombre: Draft202012Validator(tool["input_schema"]) for nombre, tool in _DEFINICIONES.items()}


@dataclass(frozen=True)
class Contexto:
    alumno_id: int
    sesion_id: int
    modulo: int
    contenido_dir: Path


@dataclass(frozen=True)
class ResultadoHerramienta:
    texto: str
    es_error: bool = False
    eventos: tuple[tuple[str, dict], ...] = ()


class ErrorHerramienta(ValueError):
    """Entrada que no se puede usar; el mensaje vuelve al modelo como tool_result con error."""


def tools_de(modulo: int) -> list[dict]:
    if modulo not in POR_MODULO:
        raise ValueError(f"módulo sin tutor en la web: {modulo}")
    return [_DEFINICIONES[nombre] for nombre in POR_MODULO[modulo]]


def _canonico(valor, opciones: list):
    if not isinstance(valor, str) or valor in opciones:
        return valor
    iguales = [o for o in opciones if isinstance(o, str) and o.casefold() == valor.casefold()]
    return iguales[0] if len(iguales) == 1 else valor


def _normalizar_enums(esquema: dict, entrada: dict) -> dict:
    normalizada = dict(entrada)
    for campo, sub in esquema["properties"].items():
        if campo in normalizada and "enum" in sub:
            normalizada[campo] = _canonico(normalizada[campo], sub["enum"])
    return normalizada


def _valor(valor) -> str:
    return "null" if valor is None else str(valor)


def _errores_de_validacion(validador: Draft202012Validator, entrada: dict) -> list[str]:
    propiedades = validador.schema["properties"]
    mensajes: list[str] = []
    for error in validador.iter_errors(entrada):
        campo = ".".join(str(parte) for parte in error.absolute_path)
        if error.validator == "required":
            nuevos = [f"falta el campo '{c}'" for c in error.validator_value if c not in error.instance]
        elif error.validator == "additionalProperties":
            nuevos = [f"campo desconocido '{c}'" for c in error.instance if c not in propiedades]
        elif error.validator == "type":
            tipos = error.validator_value if isinstance(error.validator_value, list) else [error.validator_value]
            nuevos = [f"'{campo}' tiene que ser {' o '.join(TIPOS.get(t, t) for t in tipos)}"]
        elif error.validator == "enum":
            opciones = ", ".join(_valor(v) for v in error.validator_value)
            nuevos = [f"'{campo}' tiene que ser uno de: {opciones} (llegó {_valor(error.instance)})"]
        else:
            nuevos = [f"'{campo or 'entrada'}' no es válido"]
        mensajes += [mensaje for mensaje in nuevos if mensaje not in mensajes]
    return mensajes


def ejecutar(con: sqlite3.Connection, contexto: Contexto, nombre: str, entrada) -> ResultadoHerramienta:
    disponibles = POR_MODULO.get(contexto.modulo, ())
    if nombre not in disponibles:
        return ResultadoHerramienta(
            f"La herramienta {nombre!r} no está disponible en el módulo {contexto.modulo}. "
            f"Las disponibles son: {', '.join(disponibles)}.",
            es_error=True,
        )
    if not isinstance(entrada, dict):
        return ResultadoHerramienta(f"Entrada inválida para {nombre}: tiene que ser un objeto JSON con sus campos.", es_error=True)
    validador = _VALIDADORES[nombre]
    entrada = _normalizar_enums(validador.schema, entrada)
    mensajes = _errores_de_validacion(validador, entrada)
    if mensajes:
        return ResultadoHerramienta(f"Entrada inválida para {nombre}: {'; '.join(mensajes)}.", es_error=True)
    try:
        return _DESPACHO[nombre](con, contexto, **entrada)
    except (ErrorHerramienta, dominio.ErrorDominio) as error:
        return ResultadoHerramienta(str(error), es_error=True)
    except Exception as error:
        log.exception("falló la herramienta %s", nombre)
        return ResultadoHerramienta(f"Error inesperado en {nombre} ({type(error).__name__}).", es_error=True)


def _guardar_idea(con, contexto: Contexto, texto_md: str, que_sigue_md: str | None) -> ResultadoHerramienta:
    version = dominio.guardar_idea(con, contexto.alumno_id, texto_md, que_sigue_md, "tutor")
    if contexto.modulo == 2:
        # Lo que llega acá lo lee el modelo: tiene que describir lo que la persona ve (Chat.tsx, IdeaGuardada.tsx).
        texto = (
            f"Idea guardada como versión {version}. La web se la muestra al alumno debajo de la charla: puede "
            'leerla ahí mismo en "Leer mi idea acá" y tiene dos botones, "Está bien así" y "Quiero cambiar algo". '
            'También la puede editar y descargar en "Mi idea". No lo mandes a otra pantalla a leerla: pedile '
            "que la lea ahí y te diga si lo representa."
        )
    else:
        texto = f'Idea guardada como versión {version}. El alumno ya la puede ver, editar y descargar en "Mi idea".'
    return ResultadoHerramienta(texto, eventos=(("idea", {"version": version}),))


def _tiene_dato_personal(texto: str) -> bool:
    if _MAIL.search(texto):
        return True
    return any(not _FECHA.fullmatch(numero.group()) for numero in _NUMERO_LARGO.finditer(texto))


def _validar_resumen(resumen: str) -> str:
    resumen = resumen.strip()
    lineas = [linea for linea in resumen.splitlines() if linea.strip()]
    if not lineas:
        raise ErrorHerramienta("El resumen está vacío: escribí de 2 a 5 líneas.")
    if len(resumen) > dominio.MAX_RESUMEN:
        raise ErrorHerramienta(f"El resumen supera los {dominio.MAX_RESUMEN} caracteres: acortalo.")
    if len(lineas) > MAX_LINEAS_RESUMEN:
        raise ErrorHerramienta(f"El resumen tiene {len(lineas)} líneas: dejalo en {MAX_LINEAS_RESUMEN} como máximo.")
    if _tiene_dato_personal(resumen):
        raise ErrorHerramienta(
            "El resumen parece tener un mail o un número de teléfono o documento: sacalo. "
            "El resumen no lleva datos personales ni de salud."
        )
    return resumen


def _marcar_avance(con, contexto: Contexto, modulo: int, resumen: str) -> ResultadoHerramienta:
    if modulo != contexto.modulo:
        raise ErrorHerramienta(
            f"Esta conversación es del módulo {contexto.modulo}: solo podés marcar ese módulo (llegó {modulo})."
        )
    resumen = _validar_resumen(resumen)
    actual = dominio.completar_modulo(con, contexto.alumno_id, modulo, "tutor", resumen)
    texto = f"Módulo {modulo} marcado como completo. Módulo actual del alumno: {actual}."
    if modulo == 3:
        texto += " El módulo 4 se abre cuando descargue el kit desde la web."
    return ResultadoHerramienta(texto, eventos=(("avance", {"modulo_completado": modulo, "modulo_actual": actual}),))


def _formatear_dato(dato: contenido.Dato) -> str:
    probado = "true (se probó en la realidad)" if dato.probado else "false (no se probó en la realidad)"
    return (
        f"[{dato.id}] (tema {dato.tema}; herramienta: {', '.join(dato.aplica_a)}; sistema: {', '.join(dato.sistema)}; "
        f"verificado el {dato.verificado.isoformat()}; probado: {probado}; fuente: {dato.fuente})\n"
        f"{dato.texto}"
    )


def _consultar_machete(con, contexto: Contexto, tema: str | None) -> ResultadoHerramienta:
    try:
        datos = contenido.cargar_machete(contexto.contenido_dir)
    except contenido.ErrorContenido as error:
        log.error("no se pudo leer el machete: %s", error)
        raise ErrorHerramienta(
            "El machete no está disponible ahora. No des planes, precios ni pasos de memoria: "
            "decile al alumno que siga con la guía escrita o que vuelva en un rato."
        ) from None
    fila = dominio.alumno(con, contexto.alumno_id)
    herramienta, sistema = fila["herramienta"], fila["sistema"]
    elegidos = [
        dato
        for dato in datos
        if (tema in (None, TODOS) or dato.tema == tema)
        and (herramienta is None or herramienta in dato.aplica_a)
        and (sistema not in ("mac", "windows") or sistema in dato.sistema)
    ]
    filtro = f"tema {tema or TODOS}, herramienta {herramienta or 'sin elegir'}, sistema {sistema or 'sin elegir'}"
    if not elegidos:
        return ResultadoHerramienta(f"No hay datos del machete para {filtro}.")
    encabezado = (
        f"Datos del machete ({filtro}). Decí el dato con su fecha de verificación. "
        "Decí \"gratis\" solo si el dato dice probado: true; si dice false, contalo como lo que informa la empresa."
    )
    return ResultadoHerramienta("\n\n".join([encabezado, *(_formatear_dato(d) for d in elegidos)]))


def _registrar_taller(con, contexto: Contexto, herramienta: str, sistema: str) -> ResultadoHerramienta:
    with con:
        con.execute(
            "UPDATE alumnos SET herramienta = ?, sistema = ? WHERE id = ?", (herramienta, sistema, contexto.alumno_id)
        )
    texto = f"Taller registrado: herramienta {herramienta}, sistema {sistema}."
    if sistema == "otro":
        texto += (
            " El kit necesita una computadora con Mac o Windows, así que todavía no se habilita. "
            "Su avance queda guardado para cuando tenga una."
        )
    return ResultadoHerramienta(texto, eventos=(("taller", {"herramienta": herramienta, "sistema": sistema}),))


_DESPACHO = {
    "guardar_idea": _guardar_idea,
    "marcar_avance": _marcar_avance,
    "consultar_machete": _consultar_machete,
    "registrar_taller": _registrar_taller,
}
