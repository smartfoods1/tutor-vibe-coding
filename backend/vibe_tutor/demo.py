"""Modo demo (MODO_DEMO=true): un cliente falso de Anthropic que recorre los módulos 1 a 3 con un
guion fijo, para probar el curso completo en la computadora sin claves de API y sin costo.

Imita lo que usa tutor.py de `AsyncAnthropic().messages.stream(...)`: un contexto asincrónico que
emite eventos de texto y de inicio de bloques (también los de tool_use), con `get_final_message()`
y `current_message_snapshot`, y el uso en cero. No guarda estado: cada respuesta sale de mirar la
conversación que manda el tutor (el módulo, lo que escribió la persona y cómo salieron las
herramientas), así una sesión retomada o un reintento siguen donde quedaron.

El guion, por módulo:
1. saluda, hace tres preguntas y cierra con marcar_avance;
2. saluda, hace tres preguntas, guarda con guardar_idea una idea armada con esas respuestas y,
   cuando la persona la miró, cierra con marcar_avance;
3. pregunta la computadora y la herramienta, llama a registrar_taller cuando la persona elige y,
   con la app instalada, cierra con marcar_avance.
"""

import asyncio
import copy
import re
import unicodedata
import uuid
from types import SimpleNamespace

import anthropic

from vibe_tutor import dominio

MODELO = "demo"
# Segundos entre trozos de texto, para que la respuesta se vea escribirse como con el tutor real.
PAUSA = 0.03
PALABRAS_POR_TROZO = 3
MAX_RESPUESTA_EN_IDEA = 1200
USO_CERO = {
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
}
_MODULO = re.compile(r"Módulo de esta sesión: ([1-3])\b")
_CAPTURA = re.compile(r"^\[captura de pantalla[^\]]*\]$")

AVISO = "Estás en el modo demo: te respondo con un guion fijo, sin inteligencia artificial y sin costo."
SALUDOS = {
    1: f"Hola, soy el tutor del curso. {AVISO} En este primer módulo vemos qué es el vibe coding: vos "
    "pensás y decidís qué querés, la máquina escribe el código y vos mirás si quedó como lo imaginaste.",
    2: f"Hola de nuevo. {AVISO} En este módulo vamos a dejar tu idea en una página, con tus palabras.",
    3: f"Hola. {AVISO} En este módulo elegimos con qué herramienta vas a construir tu página y la instalamos.",
}
PREGUNTAS = {
    1: (
        "Para arrancar: ¿alguna vez usaste una herramienta de inteligencia artificial, como ChatGPT o Claude?",
        "Gracias por contarlo. Cuando pensás en armar algo propio en la computadora, ¿qué es lo que más te frena?",
        (
            "Gracias. Sea lo que sea, el curso está pensado para ir de a un paso y sin romper nada. Última "
            "pregunta: ¿qué te gustaría que exista, aunque sea algo chiquito, y por qué te importa?"
        ),
    ),
    2: (
        "Primera pregunta: ¿qué es tu idea, contada en una o dos frases?",
        "Me gusta. ¿Para quién es? Pensá en una persona concreta que la usaría.",
        (
            "Perfecto. Ahora achiquemos: ¿cuál sería la versión más chica que ya te serviría, algo que "
            "entre en una sola página?"
        ),
    ),
}
PREGUNTA_SISTEMA = "Para empezar: ¿qué computadora vas a usar, una Mac o una con Windows?"
REPREGUNTA_SISTEMA = (
    "No me quedó claro: ¿es una Mac o una computadora con Windows? Si solo tenés un celular o una "
    "tablet, contámelo también."
)
PREGUNTA_HERRAMIENTA = (
    "Bien. Ahora la herramienta: podés usar Codex, que viene con la app de ChatGPT, o Claude, con su app "
    "de escritorio. ¿Cuál preferís? Si ya pagás alguna de las dos, conviene esa."
)
REPREGUNTA_HERRAMIENTA = "No me quedó claro cuál preferís: ¿Codex (la app de ChatGPT) o Claude?"
CIERRES = {
    1: "Con eso cerramos el módulo 1: ya sabés qué es el vibe coding y cuál es tu parte. Lo marco como completo.",
    2: "Genial. Cerramos el módulo 2 con tu idea guardada. Lo marco como completo.",
    3: "Excelente. Cerramos el módulo 3. Lo marco como completo.",
}
DESPUES_DEL_CIERRE = {
    1: "Listo, el módulo 1 quedó completo. Cuando quieras, seguí con el módulo 2: ahí convertimos tu idea "
    "en una página.",
    2: "Listo, el módulo 2 quedó completo. En el módulo 3 elegimos tu herramienta y la instalamos.",
    3: "Listo, el módulo 3 quedó completo. El paso que sigue es bajar tu kit desde la web y abrirlo con la "
    "herramienta que elegiste.",
}
YA_COMPLETO = "Este módulo ya quedó completo. Podés seguir con el siguiente desde el inicio del curso."
ANTES_DE_GUARDAR = (
    "Con lo que me contaste armé tu idea en una página. La guardo para que la puedas ver, editar y descargar."
)
IDEA_GUARDADA = (
    "Listo, la guardé. Mirala en \"Mi idea\": está armada con tus respuestas tal cual y la podés editar "
    "como quieras. Cuando la hayas mirado, escribime y cerramos el módulo."
)
TALLER_REGISTRADO = (
    "Anotado. Ahora instalá la app siguiendo la guía escrita del módulo 3: ahí están los pasos y los datos "
    "del día, con la fecha en que se verificaron. Cuando la tengas instalada, avisame."
)
TALLER_SIN_COMPUTADORA = (
    "Anotado. Para el kit hace falta una computadora con Mac o Windows; tu avance queda guardado para "
    "cuando tengas una. Escribime y cerramos el módulo."
)
FALLO = "No pude completar ese paso ({detalle}). Escribime cualquier cosa y lo intento de nuevo."
RESUMENES = {
    1: "Recorrido en el modo demo, con el guion fijo.\nLas respuestas no se analizaron.",
    2: "Recorrido en el modo demo, con el guion fijo.\nLa idea quedó guardada con las respuestas de la persona.",
    3: "Recorrido en el modo demo, con el guion fijo.\nEl taller quedó registrado; falta bajar el kit.",
}
MOLDE = "Una sola página, con un título, una explicación corta y un link o un botón para lo principal."
FUNCIONA_SI = "La persona para la que es la abre en el celular y entiende en pocos segundos para qué sirve."
QUE_SIGUE = "- Lo que quede afuera de la primera versión (por ejemplo, cuentas de usuario o pagos)."
NOMBRES_HERRAMIENTAS = {"codex": "Codex", "claude": "Claude"}
NOMBRES_SISTEMAS = {"mac": "Mac", "windows": "Windows", "otro": "otro equipo"}
_SISTEMAS = (
    ("mac", re.compile(r"\bmac(?:book|os)?\b|\bimac\b|\bapple\b")),
    ("windows", re.compile(r"\bwindows\b|\bwin\b|\bpc\b")),
    ("otro", re.compile(r"\b(?:celular|telefono|tablet|ipad|iphone|android|linux|chromebook)\b")),
)
_HERRAMIENTAS = (
    ("claude", re.compile(r"\bclaude\b")),
    ("codex", re.compile(r"\bcodex\b|\bchat ?gpt\b|\bopenai\b")),
)


# --- lectura de la conversación ------------------------------------------------------------------


def _bloques(mensaje: dict) -> list[dict]:
    contenido = mensaje.get("content")
    if isinstance(contenido, str):
        return [{"type": "text", "text": contenido}]
    return [b if isinstance(b, dict) else b.to_dict() for b in contenido or []]


def _modulo(mensajes: list[dict]) -> int:
    for mensaje in mensajes[:1]:
        for bloque in _bloques(mensaje):
            encontrado = _MODULO.search(bloque.get("text") or "")
            if encontrado:
                return int(encontrado.group(1))
    return 1


def _leer(mensajes: list[dict]) -> SimpleNamespace:
    """Lo que el guion necesita saber: qué escribió la persona, qué herramientas salieron bien y
    si el último mensaje trae resultados de herramientas (y cuáles)."""
    respuestas: list[str] = []
    nombres: dict[str, str] = {}
    exitos: set[str] = set()
    ultimos: list[tuple[str, bool, str]] = []
    estado_visto = False
    for indice, mensaje in enumerate(mensajes):
        if mensaje.get("role") == "assistant":
            for bloque in _bloques(mensaje):
                if bloque.get("type") == "tool_use":
                    nombres[bloque.get("id")] = bloque.get("name")
            continue
        textos, resultados, escribio = [], [], False
        for bloque in _bloques(mensaje):
            tipo = bloque.get("type")
            if tipo == "text":
                if not estado_visto:
                    estado_visto = True  # el primer texto es el estado del alumno, no lo escribió él
                    continue
                escribio = True
                texto = (bloque.get("text") or "").strip()
                if texto and not _CAPTURA.match(texto):
                    textos.append(texto)
            elif tipo == "image":
                escribio = True
            elif tipo == "tool_result":
                nombre = nombres.get(bloque.get("tool_use_id"), "")
                es_error = bool(bloque.get("is_error"))
                if not es_error:
                    exitos.add(nombre)
                resultados.append((nombre, es_error, str(bloque.get("content") or "")))
        if escribio:
            respuestas.append(" ".join(textos))
        if indice == len(mensajes) - 1 and resultados and not escribio:
            ultimos = resultados
    return SimpleNamespace(
        modulo=_modulo(mensajes),
        respuestas=respuestas,
        exitos=exitos,
        ultimos=ultimos,
        saludo=not any(m.get("role") == "assistant" for m in mensajes),
    )


def _sin_acentos(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii").lower()


def _elegido(respuestas: list[str], patrones) -> str | None:
    """Lo último que nombró la persona entre las opciones (si dice "Windows no, Mac", vale Mac)."""
    elegido = None
    for respuesta in respuestas:
        texto = _sin_acentos(respuesta)
        menciones = [(m.start(), valor) for valor, patron in patrones for m in patron.finditer(texto)]
        if menciones:
            elegido = max(menciones)[1]
    return elegido


# --- armado de la respuesta ----------------------------------------------------------------------


def _texto(texto: str) -> dict:
    return {"type": "text", "text": texto}


def _herramienta(nombre: str, entrada: dict) -> dict:
    return {"type": "tool_use", "id": f"toolu_demo_{uuid.uuid4().hex[:16]}", "name": nombre, "input": entrada}


def _una_linea(texto: str, maximo: int = MAX_RESPUESTA_EN_IDEA) -> str:
    linea = " ".join(texto.split()).lstrip("#").strip()
    if len(linea) > maximo:
        linea = linea[:maximo].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return linea


def _titulo(que_es: str) -> str:
    frase = re.split(r"[.!?\n]", que_es.strip(), maxsplit=1)[0].strip(" ,;:")
    palabras = frase.split()
    titulo = " ".join(palabras[:8]) if palabras else ""
    titulo = titulo[:70].strip()
    return (titulo[:1].upper() + titulo[1:]) if titulo else "Mi idea"


def idea_de_ejemplo(respuestas: list[str]) -> tuple[str, str]:
    """La idea en una página armada con las tres primeras respuestas del módulo 2, tal cual."""
    primeras = (respuestas + ["", "", ""])[:3]
    que_es, para_quien, version_chica = [_una_linea(r) or "(sin respuesta)" for r in primeras]
    texto = "\n\n".join(
        [
            f"# {_titulo(que_es)}",
            f"## Qué es\n\n{que_es}",
            f"## Para quién\n\n{para_quien}",
            f"## La versión más chica que ya valdría la pena\n\n{version_chica}",
            f"## El molde\n\n{MOLDE}",
            f"## Sé que funciona si\n\n{FUNCIONA_SI}",
        ]
    )
    return texto[: dominio.MAX_IDEA], QUE_SIGUE[: dominio.MAX_QUE_SIGUE]


def _cerrar(estado: SimpleNamespace) -> list[dict]:
    return [
        _texto(CIERRES[estado.modulo]),
        _herramienta("marcar_avance", {"modulo": estado.modulo, "resumen": RESUMENES[estado.modulo]}),
    ]


def _guion_1(estado: SimpleNamespace) -> list[dict]:
    n = len(estado.respuestas)
    if n < len(PREGUNTAS[1]):
        return [_texto(PREGUNTAS[1][n])]
    return _cerrar(estado)


def _guion_2(estado: SimpleNamespace) -> list[dict]:
    if "guardar_idea" in estado.exitos:
        return _cerrar(estado)
    n = len(estado.respuestas)
    if n < len(PREGUNTAS[2]):
        return [_texto(PREGUNTAS[2][n])]
    texto_md, que_sigue_md = idea_de_ejemplo(estado.respuestas)
    pedido = _herramienta("guardar_idea", {"texto_md": texto_md, "que_sigue_md": que_sigue_md})
    return [_texto(ANTES_DE_GUARDAR), pedido]


def _guion_3(estado: SimpleNamespace) -> list[dict]:
    if "registrar_taller" in estado.exitos:
        return _cerrar(estado)
    sistema = _elegido(estado.respuestas, _SISTEMAS)
    herramienta = _elegido(estado.respuestas, _HERRAMIENTAS)
    if sistema is None:
        return [_texto(REPREGUNTA_SISTEMA if estado.respuestas else PREGUNTA_SISTEMA)]
    if herramienta is None:
        # Si después de decir la computadora ya contestó algo sin elegir herramienta, se repregunta.
        dijo_sistema = next(i for i, r in enumerate(estado.respuestas) if _elegido([r], _SISTEMAS))
        ya_pregunto = len(estado.respuestas) - 1 > dijo_sistema
        return [_texto(REPREGUNTA_HERRAMIENTA if ya_pregunto else PREGUNTA_HERRAMIENTA)]
    anuncio = f"Buenísimo: anoto {NOMBRES_HERRAMIENTAS[herramienta]} en {NOMBRES_SISTEMAS[sistema]}."
    return [_texto(anuncio), _herramienta("registrar_taller", {"herramienta": herramienta, "sistema": sistema})]


def _despues_de_herramientas(estado: SimpleNamespace) -> list[dict]:
    fallas = [(nombre, detalle) for nombre, es_error, detalle in estado.ultimos if es_error]
    if fallas:
        detalle = " ".join(fallas[0][1].split())[:200].rstrip(".")
        return [_texto(FALLO.format(detalle=detalle or fallas[0][0]))]
    nombres = {nombre for nombre, _, _ in estado.ultimos}
    if "marcar_avance" in nombres:
        return [_texto(DESPUES_DEL_CIERRE[estado.modulo])]
    if "guardar_idea" in nombres:
        return [_texto(IDEA_GUARDADA)]
    if "registrar_taller" in nombres:
        sistema = _elegido(estado.respuestas, _SISTEMAS)
        return [_texto(TALLER_SIN_COMPUTADORA if sistema == "otro" else TALLER_REGISTRADO)]
    return [_texto("Listo. ¿Seguimos?")]


def guion(mensajes: list[dict]) -> list[dict]:
    """Los bloques de la próxima respuesta del tutor (texto y, si toca, un pedido de herramienta)."""
    estado = _leer(mensajes)
    if estado.ultimos:
        # En la página, este texto sigue en la misma burbuja que el de antes de la herramienta.
        return [_texto(f"\n\n{bloque['text']}") for bloque in _despues_de_herramientas(estado)]
    if "marcar_avance" in estado.exitos:
        return [_texto(YA_COMPLETO)]
    bloques = {1: _guion_1, 2: _guion_2, 3: _guion_3}[estado.modulo](estado)
    if estado.saludo:  # la primera respuesta de la sesión arranca con el saludo del módulo
        bloques[0] = _texto(f"{SALUDOS[estado.modulo]} {bloques[0]['text']}")
    return bloques


# --- el cliente falso ----------------------------------------------------------------------------


def _mensaje(bloques: list[dict]) -> anthropic.types.Message:
    return anthropic.types.Message.model_validate(
        {
            "id": f"msg_demo_{uuid.uuid4().hex[:16]}",
            "type": "message",
            "role": "assistant",
            "model": MODELO,
            "content": copy.deepcopy(bloques),
            "stop_reason": "tool_use" if any(b["type"] == "tool_use" for b in bloques) else "end_turn",
            "stop_sequence": None,
            "usage": dict(USO_CERO),
        }
    )


def _trozos(texto: str) -> list[str]:
    palabras = re.findall(r"\S+\s*", texto)
    return ["".join(palabras[i : i + PALABRAS_POR_TROZO]) for i in range(0, len(palabras), PALABRAS_POR_TROZO)]


class StreamDemo:
    """Lo que devuelve `messages.stream(...)`: se usa con `async with` y se recorre con `async for`."""

    def __init__(self, mensaje: anthropic.types.Message):
        self._mensaje = mensaje

    async def __aenter__(self) -> "StreamDemo":
        return self

    async def __aexit__(self, *excepcion) -> bool:
        return False

    def __aiter__(self):
        return self._eventos()

    async def _eventos(self):
        for indice, bloque in enumerate(self._mensaje.content):
            yield SimpleNamespace(type="content_block_start", index=indice, content_block=bloque)
            if bloque.type == "text":
                for trozo in _trozos(bloque.text):
                    await asyncio.sleep(PAUSA)
                    yield SimpleNamespace(type="text", text=trozo, snapshot="")
            yield SimpleNamespace(type="content_block_stop", index=indice, content_block=bloque)
        yield SimpleNamespace(type="message_stop", message=self._mensaje)

    async def get_final_message(self) -> anthropic.types.Message:
        return self._mensaje

    @property
    def current_message_snapshot(self) -> anthropic.types.Message:
        return self._mensaje.model_copy(update={"content": [], "stop_reason": None})


class ClienteDemo:
    """Reemplaza a `anthropic.AsyncAnthropic` en el modo demo: `cliente.messages.stream(**params)`."""

    def __init__(self) -> None:
        self.messages = SimpleNamespace(stream=self._stream)

    def _stream(self, *, messages: list[dict], **_otros) -> StreamDemo:
        return StreamDemo(_mensaje(guion(messages)))
