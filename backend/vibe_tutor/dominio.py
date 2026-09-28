"""Reglas del alumno que comparten el tutor, la API y las tareas (data-model.md)."""

import sqlite3

from vibe_tutor.db import AHORA_UTC

MAX_IDEA = 6000
MAX_QUE_SIGUE = 3000
MAX_RESUMEN = 1000
MAX_FUENTE = 64
MODULO_KIT = 4


class ErrorDominio(ValueError):
    """Un pedido que las reglas del curso no permiten; el mensaje se puede mostrar al alumno."""


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def crear_alumno(con: sqlite3.Connection, email: str, fuente: str | None) -> int:
    with con:
        cursor = con.execute(
            "INSERT INTO alumnos (email, fuente) VALUES (?, ?)",
            (normalizar_email(email), (fuente or None) and fuente[:MAX_FUENTE]),
        )
    return int(cursor.lastrowid)


def alumno(con: sqlite3.Connection, alumno_id: int) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM alumnos WHERE id = ?", (alumno_id,)).fetchone()


def alumno_por_email(con: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM alumnos WHERE email = ?", (normalizar_email(email),)).fetchone()


def tocar_actividad(con: sqlite3.Connection, alumno_id: int) -> None:
    with con:
        con.execute(f"UPDATE alumnos SET ultima_actividad = {AHORA_UTC} WHERE id = ?", (alumno_id,))


def registrar_evento(con: sqlite3.Connection, alumno_id: int | None, tipo: str, detalle: str | None = None) -> None:
    with con:
        con.execute("INSERT INTO eventos (alumno_id, tipo, detalle) VALUES (?, ?, ?)", (alumno_id, tipo, detalle))


def consentimiento(con: sqlite3.Connection, alumno_id: int, tipo: str) -> bool:
    fila = con.execute(
        "SELECT valor FROM consentimientos WHERE alumno_id = ? AND tipo = ? ORDER BY id DESC LIMIT 1",
        (alumno_id, tipo),
    ).fetchone()
    return bool(fila and fila["valor"])


def agregar_consentimiento(
    con: sqlite3.Connection, alumno_id: int, tipo: str, valor: bool, version_texto: str
) -> None:
    with con:
        con.execute(
            "INSERT INTO consentimientos (alumno_id, tipo, valor, version_texto) VALUES (?, ?, ?, ?)",
            (alumno_id, tipo, int(valor), version_texto),
        )


def idea_vigente(con: sqlite3.Connection, alumno_id: int) -> sqlite3.Row | None:
    return con.execute(
        "SELECT * FROM ideas WHERE alumno_id = ? ORDER BY version DESC LIMIT 1", (alumno_id,)
    ).fetchone()


def guardar_idea(
    con: sqlite3.Connection, alumno_id: int, texto_md: str, que_sigue_md: str | None, autor: str
) -> int:
    texto_md = (texto_md or "").strip()
    que_sigue_md = (que_sigue_md or "").strip() or None
    if not texto_md:
        raise ErrorDominio("La idea está vacía.")
    if len(texto_md) > MAX_IDEA:
        raise ErrorDominio(f"La idea supera los {MAX_IDEA} caracteres.")
    if que_sigue_md and len(que_sigue_md) > MAX_QUE_SIGUE:
        raise ErrorDominio(f"\"Qué sigue\" supera los {MAX_QUE_SIGUE} caracteres.")
    with con:
        fila = con.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 AS siguiente FROM ideas WHERE alumno_id = ?", (alumno_id,)
        ).fetchone()
        version = int(fila["siguiente"])
        con.execute(
            "INSERT INTO ideas (alumno_id, version, texto_md, que_sigue_md, autor) VALUES (?, ?, ?, ?, ?)",
            (alumno_id, version, texto_md, que_sigue_md, autor),
        )
    return version


def subir_modulo(con: sqlite3.Connection, alumno_id: int, modulo: int) -> int:
    with con:
        con.execute(
            "UPDATE alumnos SET modulo_actual = MAX(modulo_actual, ?) WHERE id = ?", (modulo, alumno_id)
        )
    return int(alumno(con, alumno_id)["modulo_actual"])


def completar_modulo(
    con: sqlite3.Connection, alumno_id: int, modulo: int, via: str, resumen: str | None = None
) -> int:
    """Marca el módulo 1, 2 o 3 y devuelve el módulo actual. Del 3 al 4 se sube recién con el kit."""
    actual = int(alumno(con, alumno_id)["modulo_actual"])
    if modulo not in (1, 2, 3) or modulo > actual:
        raise ErrorDominio("Ese módulo todavía no está abierto.")
    if modulo == 2 and idea_vigente(con, alumno_id) is None:
        raise ErrorDominio("Antes de terminar el módulo 2 hace falta guardar tu idea.")
    resumen = (resumen or "").strip()[:MAX_RESUMEN] or None
    with con:
        nuevo = con.execute(
            f"INSERT OR IGNORE INTO avance (alumno_id, modulo, completado, resumen, via) "
            f"VALUES (?, ?, {AHORA_UTC}, ?, ?)",
            (alumno_id, modulo, resumen, via),
        ).rowcount
        if nuevo:
            con.execute(
                "INSERT INTO eventos (alumno_id, tipo, detalle) VALUES (?, 'modulo_completo', ?)",
                (alumno_id, f"modulo={modulo}"),
            )
        con.execute(
            f"UPDATE sesiones SET fin = {AHORA_UTC} WHERE alumno_id = ? AND modulo = ? AND fin IS NULL",
            (alumno_id, modulo),
        )
    return subir_modulo(con, alumno_id, modulo + 1) if modulo < 3 else actual


def resumen_modulo(con: sqlite3.Connection, alumno_id: int, modulo: int) -> str | None:
    fila = con.execute(
        "SELECT resumen FROM avance WHERE alumno_id = ? AND modulo = ?", (alumno_id, modulo)
    ).fetchone()
    return fila["resumen"] if fila else None
