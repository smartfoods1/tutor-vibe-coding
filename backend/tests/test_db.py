import sqlite3
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from vibe_tutor import db
from vibe_tutor.main import crear_app

TABLAS = {
    "alumnos": [
        "id", "email", "creado", "ultima_actividad", "herramienta", "sistema", "modulo_actual", "fuente", "estado"
    ],
    "consentimientos": ["id", "alumno_id", "tipo", "valor", "version_texto", "creado"],
    "codigos": ["id", "email", "hash", "sal", "vence", "intentos", "usado", "ip", "pendiente_json", "creado", "fallos"],
    "avance": ["alumno_id", "modulo", "completado", "resumen", "via"],
    "ideas": ["id", "alumno_id", "version", "texto_md", "que_sigue_md", "autor", "creado"],
    "sesiones": ["id", "alumno_id", "modulo", "inicio", "fin", "costo_usd"],
    "mensajes": ["id", "sesion_id", "orden", "rol", "contenido_json", "creado"],
    "uso": [
        "id",
        "alumno_id",
        "sesion_id",
        "creado",
        "proveedor",
        "modelo",
        "input_tokens",
        "output_tokens",
        "cache_write",
        "cache_read",
        "costo_usd",
    ],
    "kits": ["id", "alumno_id", "creado", "version_curso", "fecha_machete", "herramienta", "sistema"],
    "links": ["id", "alumno_id", "url", "titulo", "mostrar_galeria", "uso_contenido", "creado", "aprobado"],
    "mails": ["id", "alumno_id", "tipo", "clave", "estado", "creado"],
    "eventos": ["id", "alumno_id", "tipo", "detalle", "creado"],
}


def _columnas(con: sqlite3.Connection, tabla: str) -> list[str]:
    return [fila["name"] for fila in con.execute(f"PRAGMA table_info({tabla})")]


def _alumno(con: sqlite3.Connection, email: str = "ana@example.com") -> int:
    return con.execute("INSERT INTO alumnos (email) VALUES (?)", (email,)).lastrowid


def _datos_completos(con: sqlite3.Connection, alumno_id: int) -> int:
    con.execute(
        "INSERT INTO consentimientos (alumno_id, tipo, valor, version_texto) VALUES (?, 'mails_curso', 1, 'v1')",
        (alumno_id,),
    )
    con.execute("INSERT INTO avance (alumno_id, modulo, completado, via) VALUES (?, 1, '2026-10-01', 'tutor')", (alumno_id,))
    con.execute("INSERT INTO ideas (alumno_id, version, texto_md, autor) VALUES (?, 1, '# Idea', 'tutor')", (alumno_id,))
    sesion_id = con.execute("INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (alumno_id,)).lastrowid
    con.execute(
        "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 0, 'user', '[]')", (sesion_id,)
    )
    con.execute(
        "INSERT INTO uso (alumno_id, sesion_id, proveedor, modelo, costo_usd) VALUES (?, ?, 'anthropic', 'claude-sonnet-5', 0.01)",
        (alumno_id, sesion_id),
    )
    con.execute(
        "INSERT INTO kits (alumno_id, version_curso, fecha_machete, herramienta, sistema) VALUES (?, 'v', '2026-09-28', 'codex', 'mac')",
        (alumno_id,),
    )
    con.execute("INSERT INTO links (alumno_id, url) VALUES (?, 'https://x.netlify.app')", (alumno_id,))
    con.execute("INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'bienvenida', 'bienvenida', 'enviado')", (alumno_id,))
    con.execute("INSERT INTO eventos (alumno_id, tipo) VALUES (?, 'inscripcion')", (alumno_id,))
    return sesion_id


def test_migrar_crea_tablas(tmp_path):
    con = db.conectar(tmp_path / "vibe.db")
    db.migrar(con)
    _alumno(con)
    con.commit()
    db.migrar(con)

    tablas = {fila["name"] for fila in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert set(TABLAS) <= tablas
    for tabla, columnas in TABLAS.items():
        assert _columnas(con, tabla) == columnas
    assert con.execute("SELECT count(*) FROM alumnos").fetchone()[0] == 1
    con.close()


def test_migracion_2_agrega_la_moderacion_de_la_galeria_y_los_fallos(tmp_path):
    con = db.conectar(tmp_path / "vibe.db")
    con.executescript(f"BEGIN;\n{db.MIGRACIONES[0]}\nPRAGMA user_version = 1;\nCOMMIT;")
    alumno_id = _alumno(con)
    con.execute("INSERT INTO links (alumno_id, url, mostrar_galeria) VALUES (?, 'https://x.netlify.app', 1)", (alumno_id,))
    con.execute("INSERT INTO codigos (email, hash, sal, vence) VALUES ('a@x.com', 'h', 's', 'v')")
    con.commit()

    db.migrar(con)

    assert con.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRACIONES) >= 2
    assert tuple(con.execute("SELECT mostrar_galeria, aprobado FROM links").fetchone()) == (1, 0)
    assert con.execute("SELECT fallos FROM codigos").fetchone()[0] == 0
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("UPDATE links SET aprobado = 2")
    con.close()


NOMBRE_ANTERIOR = "textos_del_autor"


def _base_en_la_version_2_con_el_nombre_anterior(ruta):
    """Una base como las de las instalaciones anteriores a la migración 3: el tercer consentimiento
    tenía otro nombre (acá, uno de ejemplo) en el CHECK de la tabla."""
    con = db.conectar(ruta)
    viejo = db.MIGRACIONES[0].replace("'novedades'", f"'{NOMBRE_ANTERIOR}'")
    assert viejo != db.MIGRACIONES[0]
    for numero, script in enumerate([viejo, db.MIGRACIONES[1]], start=1):
        con.executescript(f"BEGIN;\n{script}\nPRAGMA user_version = {numero};\nCOMMIT;")
    return con


def test_migracion_3_renombra_el_consentimiento_de_las_novedades(tmp_path):
    con = _base_en_la_version_2_con_el_nombre_anterior(tmp_path / "vibe.db")
    alumno_id = _alumno(con)
    otro_id = _alumno(con, "otro@example.com")
    filas = [
        (alumno_id, "mails_curso", 1, "v1", "2026-09-28T10:00:00+00:00"),
        (alumno_id, "transferencia", 1, "v1", "2026-09-28T10:00:00+00:00"),
        (alumno_id, NOMBRE_ANTERIOR, 1, "v1", "2026-09-28T10:00:00+00:00"),
        (otro_id, NOMBRE_ANTERIOR, 0, "v2", "2026-09-29T10:00:00+00:00"),
        (alumno_id, NOMBRE_ANTERIOR, 0, "v2", "2026-09-30T10:00:00+00:00"),
    ]
    con.executemany(
        "INSERT INTO consentimientos (alumno_id, tipo, valor, version_texto, creado) VALUES (?, ?, ?, ?, ?)", filas
    )
    con.commit()
    antes = [tuple(f) for f in con.execute("SELECT id, alumno_id, valor, version_texto, creado FROM consentimientos ORDER BY id")]

    db.migrar(con)

    assert con.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRACIONES) >= 3
    despues = con.execute("SELECT * FROM consentimientos ORDER BY id").fetchall()
    assert [(f["id"], f["alumno_id"], f["valor"], f["version_texto"], f["creado"]) for f in despues] == antes
    assert [f["tipo"] for f in despues] == ["mails_curso", "transferencia", "novedades", "novedades", "novedades"]
    assert _columnas(con, "consentimientos") == TABLAS["consentimientos"]
    indices = {f["name"] for f in con.execute("PRAGMA index_list(consentimientos)")}
    assert "idx_consentimientos_alumno" in indices
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(
            "INSERT INTO consentimientos (alumno_id, tipo, valor, version_texto) VALUES (?, ?, 1, 'v')",
            (alumno_id, NOMBRE_ANTERIOR),
        )
    nuevo = con.execute(
        "INSERT INTO consentimientos (alumno_id, tipo, valor, version_texto) VALUES (?, 'novedades', 1, 'v3')",
        (alumno_id,),
    ).lastrowid
    assert nuevo == 6
    con.execute("DELETE FROM alumnos WHERE id = ?", (otro_id,))
    assert con.execute("SELECT count(*) FROM consentimientos WHERE alumno_id = ?", (otro_id,)).fetchone()[0] == 0
    con.close()


def _base_en_la_version_3(ruta):
    """Una base como las de las instalaciones anteriores a la migración 4 (sin aprobación manual)."""
    con = db.conectar(ruta)
    for numero, script in enumerate(db.MIGRACIONES[:3], start=1):
        con.executescript(f"BEGIN;\n{script}\nPRAGMA user_version = {numero};\nCOMMIT;")
    return con


def _esquema(con):
    return sorted(
        (f["type"], f["name"], " ".join((f["sql"] or "").split()))
        for f in con.execute("SELECT type, name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'")
    )


@pytest.mark.parametrize("vieja", [_base_en_la_version_2_con_el_nombre_anterior, _base_en_la_version_3])
def test_una_base_nueva_termina_igual_que_una_migrada(tmp_path, vieja):
    nueva = db.conectar(tmp_path / "nueva.db")
    db.migrar(nueva)
    migrada = vieja(tmp_path / "migrada.db")
    _datos_completos(migrada, _alumno(migrada))
    migrada.commit()
    db.migrar(migrada)

    assert _esquema(nueva) == _esquema(migrada)
    nueva.close()
    migrada.close()


def _indices(con, tabla: str) -> dict[str, tuple]:
    """Índices de la tabla: nombre -> (único, parcial, columnas)."""
    return {
        f["name"]: (
            bool(f["unique"]),
            bool(f["partial"]),
            tuple(c["name"] for c in con.execute(f"PRAGMA index_info('{f['name']}')")),
        )
        for f in con.execute(f"PRAGMA index_list({tabla})")
    }


def test_migracion_4_suma_el_estado_y_los_tipos_nuevos_sin_perder_filas(tmp_path):
    con = _base_en_la_version_3(tmp_path / "vibe.db")
    ana = _alumno(con)
    beto = _alumno(con, "beto@example.com")
    borrado = _alumno(con, "borrado@example.com")
    _datos_completos(con, ana)
    con.executemany(
        "INSERT INTO mails (alumno_id, tipo, clave, estado, creado) VALUES (?, ?, ?, ?, ?)",
        [
            (beto, "bienvenida", "bienvenida", "fallido", "2026-09-27T10:00:00+00:00"),
            (None, "aviso_80", "aviso_80:2026-09", "enviado", "2026-09-27T11:00:00+00:00"),
            (beto, "contame", "contame", "enviado", "2026-09-27T12:00:00+00:00"),
            (borrado, "bienvenida", "bienvenida", "enviado", "2026-09-27T13:00:00+00:00"),
        ],
    )
    con.executemany(
        "INSERT INTO eventos (alumno_id, tipo, detalle, creado) VALUES (?, ?, ?, ?)",
        [
            (beto, "inscripcion", "fuente=hecho-en", "2026-09-27T10:00:00+00:00"),
            (None, "borrado", None, "2026-09-27T11:00:00+00:00"),
            (borrado, "inscripcion", None, "2026-09-27T12:00:00+00:00"),
        ],
    )
    # El último mail y el último evento se van con el alumno: sus ids no se tienen que reusar.
    con.execute("DELETE FROM alumnos WHERE id = ?", (borrado,))
    con.commit()
    mails_antes = [tuple(f) for f in con.execute("SELECT * FROM mails ORDER BY id")]
    eventos_antes = [tuple(f) for f in con.execute("SELECT * FROM eventos ORDER BY id")]
    ultimo_mail = con.execute("SELECT seq FROM sqlite_sequence WHERE name = 'mails'").fetchone()[0]
    ultimo_evento = con.execute("SELECT seq FROM sqlite_sequence WHERE name = 'eventos'").fetchone()[0]
    assert ultimo_mail > max(f[0] for f in mails_antes)

    db.migrar(con)

    assert con.execute("PRAGMA user_version").fetchone()[0] == len(db.MIGRACIONES) >= 4
    assert [tuple(f) for f in con.execute("SELECT * FROM mails ORDER BY id")] == mails_antes
    assert [tuple(f) for f in con.execute("SELECT * FROM eventos ORDER BY id")] == eventos_antes
    assert [f["estado"] for f in con.execute("SELECT estado FROM alumnos ORDER BY id")] == ["aprobado", "aprobado"]
    for tabla, columnas in TABLAS.items():
        assert _columnas(con, tabla) == columnas, tabla
    mails_indices = _indices(con, "mails")
    assert mails_indices["idx_mails_sin_alumno"] == (True, True, ("clave",))
    assert (True, False, ("alumno_id", "clave")) in mails_indices.values()
    assert _indices(con, "eventos")["idx_eventos_tipo"] == (False, False, ("tipo", "creado"))
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"

    nuevo_mail = "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, ?, ?, ?)"
    pedidos = con.execute(nuevo_mail, (None, "pedidos", "pedidos:2026-09-29T10", "enviado")).lastrowid
    assert pedidos == ultimo_mail + 1
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(nuevo_mail, (None, "pedidos", "pedidos:2026-09-29T10", "fallido"))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(nuevo_mail, (beto, "bienvenida", "bienvenida", "enviado"))
    aprobacion = con.execute("INSERT INTO eventos (alumno_id, tipo) VALUES (?, 'aprobacion')", (beto,)).lastrowid
    assert aprobacion == ultimo_evento + 1
    con.execute("UPDATE alumnos SET estado = 'pendiente' WHERE id = ?", (beto,))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("UPDATE alumnos SET estado = 'rechazado' WHERE id = ?", (beto,))

    con.execute("DELETE FROM alumnos WHERE id = ?", (beto,))
    assert con.execute("SELECT count(*) FROM mails WHERE alumno_id = ?", (beto,)).fetchone()[0] == 0
    assert con.execute("SELECT count(*) FROM mails WHERE alumno_id IS NULL").fetchone()[0] == 2
    assert con.execute("SELECT count(*) FROM eventos WHERE alumno_id = ?", (beto,)).fetchone()[0] == 0
    assert con.execute("SELECT count(*) FROM eventos WHERE alumno_id IS NULL").fetchone()[0] == 4
    con.close()


def test_alumno_nuevo_queda_aprobado_por_defecto(con):
    alumno_id = _alumno(con)

    assert con.execute("SELECT estado FROM alumnos WHERE id = ?", (alumno_id,)).fetchone()[0] == "aprobado"


def test_conectar_wal_filas_y_claves_foraneas(tmp_path):
    ruta = tmp_path / "datos" / "vibe.db"
    con = db.conectar(ruta)

    assert ruta.exists()
    assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert isinstance(con.execute("SELECT 1 AS uno").fetchone(), sqlite3.Row)
    con.close()


def test_valores_por_defecto(con):
    alumno_id = _alumno(con)
    alumno = con.execute("SELECT * FROM alumnos WHERE id = ?", (alumno_id,)).fetchone()
    sesion_id = con.execute("INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (alumno_id,)).lastrowid
    sesion = con.execute("SELECT * FROM sesiones WHERE id = ?", (sesion_id,)).fetchone()
    link = con.execute(
        "SELECT * FROM links WHERE id = ?",
        (con.execute("INSERT INTO links (alumno_id, url) VALUES (?, 'https://a.b')", (alumno_id,)).lastrowid,),
    ).fetchone()

    assert alumno["modulo_actual"] == 1
    assert alumno["herramienta"] is None and alumno["fuente"] is None
    assert datetime.fromisoformat(alumno["creado"]).utcoffset() == timedelta(0)
    assert alumno["ultima_actividad"] == alumno["creado"]
    assert sesion["costo_usd"] == 0 and sesion["fin"] is None
    assert link["mostrar_galeria"] == 0 and link["uso_contenido"] == 0


def test_email_de_alumno_es_unico(con):
    _alumno(con)
    with pytest.raises(sqlite3.IntegrityError):
        _alumno(con)


def test_mensajes_rol_y_orden(con):
    sesion_id = con.execute("INSERT INTO sesiones (alumno_id, modulo) VALUES (?, 1)", (_alumno(con),)).lastrowid
    con.execute("INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 0, 'user', '[]')", (sesion_id,))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(
            "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 1, 'tutor', '[]')", (sesion_id,)
        )
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(
            "INSERT INTO mensajes (sesion_id, orden, rol, contenido_json) VALUES (?, 0, 'assistant', '[]')",
            (sesion_id,),
        )


@pytest.mark.parametrize(
    ("tabla", "columnas", "valores"),
    [
        ("alumnos", "email, herramienta", "'b@x.com', 'cursor'"),
        ("alumnos", "email, sistema", "'b@x.com', 'linux'"),
        ("alumnos", "email, modulo_actual", "'b@x.com', 8"),
        ("sesiones", "alumno_id, modulo", "1, 4"),
        ("avance", "alumno_id, modulo, completado, via", "1, 1, 'x', 'magia'"),
        ("ideas", "alumno_id, version, texto_md, autor", "1, 1, 'x', 'otro'"),
        ("consentimientos", "alumno_id, tipo, valor, version_texto", "1, 'otro', 1, 'v1'"),
        ("consentimientos", "alumno_id, tipo, valor, version_texto", "1, 'textos', 1, 'v1'"),
        ("kits", "alumno_id, version_curso, fecha_machete, herramienta, sistema", "1, 'v', 'f', 'codex', 'otro'"),
        ("mails", "alumno_id, tipo, clave, estado", "1, 'spam', 'k', 'enviado'"),
        ("eventos", "tipo", "'otro'"),
        ("alumnos", "email, estado", "'b@x.com', 'rechazado'"),
    ],
)
def test_valores_permitidos(con, tabla, columnas, valores):
    _alumno(con, "a@x.com")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(f"INSERT INTO {tabla} ({columnas}) VALUES ({valores})")


def test_idea_version_y_clave_de_mail_unicas(con):
    alumno_id = _alumno(con)
    con.execute("INSERT INTO ideas (alumno_id, version, texto_md, autor) VALUES (?, 1, 'a', 'tutor')", (alumno_id,))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO ideas (alumno_id, version, texto_md, autor) VALUES (?, 1, 'b', 'alumno')", (alumno_id,))
    con.execute("INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'recordatorio', 'recordatorio', 'enviado')", (alumno_id,))
    with pytest.raises(sqlite3.IntegrityError):
        con.execute(
            "INSERT INTO mails (alumno_id, tipo, clave, estado) VALUES (?, 'recordatorio', 'recordatorio', 'fallido')",
            (alumno_id,),
        )


def test_datos_de_otro_alumno_inexistente_se_rechazan(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO ideas (alumno_id, version, texto_md, autor) VALUES (999, 1, 'a', 'tutor')")


def test_borrar_alumno_borra_sus_datos_y_deja_uso_y_eventos_anonimos(con):
    alumno_id = _alumno(con)
    otro_id = _alumno(con, "otro@example.com")
    _datos_completos(con, alumno_id)
    _datos_completos(con, otro_id)

    con.execute("DELETE FROM alumnos WHERE id = ?", (alumno_id,))

    for tabla in ("consentimientos", "avance", "ideas", "sesiones", "kits", "links", "mails"):
        assert con.execute(f"SELECT count(*) FROM {tabla} WHERE alumno_id = ?", (alumno_id,)).fetchone()[0] == 0
        assert con.execute(f"SELECT count(*) FROM {tabla} WHERE alumno_id = ?", (otro_id,)).fetchone()[0] == 1
    assert con.execute("SELECT count(*) FROM mensajes").fetchone()[0] == 1
    for tabla in ("uso", "eventos"):
        filas = con.execute(f"SELECT alumno_id FROM {tabla} ORDER BY id").fetchall()
        assert [f["alumno_id"] for f in filas] == [None, otro_id]
    assert [f["sesion_id"] for f in con.execute("SELECT sesion_id FROM uso ORDER BY id")][0] is None


def test_salud():
    assert TestClient(crear_app()).get("/api/salud").json() == {"ok": True}


def test_fixtures(settings_tmp):
    assert settings_tmp.data_dir.is_dir()


def test_login_y_voz_abren_la_base_del_curso(settings_tmp):
    from vibe_tutor import auth, voz

    conexiones = auth.conexion(settings_tmp)
    next(conexiones).close()
    with voz._abrir(settings_tmp):
        pass

    assert db.ARCHIVO == "vibe.db"
    assert [p.name for p in settings_tmp.data_dir.glob("*.db")] == ["vibe.db"]
