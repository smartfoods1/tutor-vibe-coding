import sqlite3
from pathlib import Path

ARCHIVO = "vibe.db"
AHORA_UTC = "(strftime('%Y-%m-%dT%H:%M:%S+00:00', 'now'))"

MIGRACIONES = (
    # 1: el esquema inicial. En las instalaciones anteriores a la migración 3, el consentimiento
    # opcional "novedades" tenía otro nombre; la 3 lo renombra y deja todas las bases iguales.
    f"""
    CREATE TABLE alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        ultima_actividad TEXT NOT NULL DEFAULT {AHORA_UTC},
        herramienta TEXT CHECK (herramienta IN ('codex', 'claude')),
        sistema TEXT CHECK (sistema IN ('mac', 'windows', 'otro')),
        modulo_actual INTEGER NOT NULL DEFAULT 1 CHECK (modulo_actual BETWEEN 1 AND 7),
        fuente TEXT
    );

    CREATE TABLE consentimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        tipo TEXT NOT NULL CHECK (tipo IN ('mails_curso', 'transferencia', 'novedades')),
        valor INTEGER NOT NULL CHECK (valor IN (0, 1)),
        version_texto TEXT NOT NULL,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    CREATE INDEX idx_consentimientos_alumno ON consentimientos (alumno_id, tipo, id);

    CREATE TABLE codigos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        hash TEXT NOT NULL,
        sal TEXT NOT NULL,
        vence TEXT NOT NULL,
        intentos INTEGER NOT NULL DEFAULT 0,
        usado INTEGER NOT NULL DEFAULT 0,
        ip TEXT NOT NULL DEFAULT '',
        pendiente_json TEXT,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    CREATE INDEX idx_codigos_email ON codigos (email, creado);
    CREATE INDEX idx_codigos_ip ON codigos (ip, creado);

    CREATE TABLE avance (
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        modulo INTEGER NOT NULL CHECK (modulo BETWEEN 1 AND 3),
        completado TEXT NOT NULL,
        resumen TEXT,
        via TEXT NOT NULL CHECK (via IN ('tutor', 'guia_escrita')),
        PRIMARY KEY (alumno_id, modulo)
    );

    CREATE TABLE ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        version INTEGER NOT NULL,
        texto_md TEXT NOT NULL,
        que_sigue_md TEXT,
        autor TEXT NOT NULL CHECK (autor IN ('tutor', 'alumno')),
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        UNIQUE (alumno_id, version)
    );

    CREATE TABLE sesiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        modulo INTEGER NOT NULL CHECK (modulo BETWEEN 1 AND 3),
        inicio TEXT NOT NULL DEFAULT {AHORA_UTC},
        fin TEXT,
        costo_usd REAL NOT NULL DEFAULT 0
    );
    CREATE INDEX idx_sesiones_alumno ON sesiones (alumno_id, modulo);

    CREATE TABLE mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sesion_id INTEGER NOT NULL REFERENCES sesiones (id) ON DELETE CASCADE,
        orden INTEGER NOT NULL,
        rol TEXT NOT NULL CHECK (rol IN ('user', 'assistant')),
        contenido_json TEXT NOT NULL,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        UNIQUE (sesion_id, orden)
    );

    CREATE TABLE uso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER REFERENCES alumnos (id) ON DELETE SET NULL,
        sesion_id INTEGER REFERENCES sesiones (id) ON DELETE SET NULL,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        proveedor TEXT NOT NULL,
        modelo TEXT NOT NULL,
        input_tokens INTEGER NOT NULL DEFAULT 0,
        output_tokens INTEGER NOT NULL DEFAULT 0,
        cache_write INTEGER NOT NULL DEFAULT 0,
        cache_read INTEGER NOT NULL DEFAULT 0,
        costo_usd REAL NOT NULL DEFAULT 0
    );
    CREATE INDEX idx_uso_creado ON uso (creado);
    CREATE INDEX idx_uso_alumno ON uso (alumno_id);
    CREATE INDEX idx_uso_sesion ON uso (sesion_id);

    CREATE TABLE kits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        version_curso TEXT NOT NULL,
        fecha_machete TEXT NOT NULL,
        herramienta TEXT NOT NULL CHECK (herramienta IN ('codex', 'claude')),
        sistema TEXT NOT NULL CHECK (sistema IN ('mac', 'windows'))
    );

    CREATE TABLE links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        url TEXT NOT NULL,
        titulo TEXT,
        mostrar_galeria INTEGER NOT NULL DEFAULT 0 CHECK (mostrar_galeria IN (0, 1)),
        uso_contenido INTEGER NOT NULL DEFAULT 0 CHECK (uso_contenido IN (0, 1)),
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );

    CREATE TABLE mails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER REFERENCES alumnos (id) ON DELETE CASCADE,
        tipo TEXT NOT NULL CHECK (tipo IN ('bienvenida', 'recordatorio', 'contame', 'aviso_80')),
        clave TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('enviado', 'fallido')),
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        UNIQUE (alumno_id, clave)
    );
    CREATE UNIQUE INDEX idx_mails_sin_alumno ON mails (clave) WHERE alumno_id IS NULL;

    CREATE TABLE eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER REFERENCES alumnos (id) ON DELETE SET NULL,
        tipo TEXT NOT NULL
            CHECK (tipo IN ('inscripcion', 'modulo_completo', 'kit', 'link', 'baja_mails', 'borrado')),
        detalle TEXT,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    CREATE INDEX idx_eventos_tipo ON eventos (tipo, creado);
    """,
    # 2: la galería muestra solo los links que aprobó quien administra, y los códigos llevan la
    # cuenta de sus intentos fallidos (el tope de fallos por mail suma los de todos sus códigos).
    """
    ALTER TABLE links ADD COLUMN aprobado INTEGER NOT NULL DEFAULT 0 CHECK (aprobado IN (0, 1));
    CREATE INDEX idx_links_galeria ON links (mostrar_galeria, aprobado);
    ALTER TABLE codigos ADD COLUMN fallos INTEGER NOT NULL DEFAULT 0;
    """,
    # 3: el consentimiento opcional pasa a llamarse "novedades" (la lista de novedades por mail de
    # quien opera el curso). SQLite no cambia un CHECK: se recrea la tabla con las mismas filas, ids
    # y fechas, y el tipo que no es de los obligatorios pasa a "novedades". Los códigos pendientes de
    # antes de esta migración guardan el nombre anterior: al verificarse, esa casilla queda en 0.
    f"""
    CREATE TABLE consentimientos_nueva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        tipo TEXT NOT NULL CHECK (tipo IN ('mails_curso', 'transferencia', 'novedades')),
        valor INTEGER NOT NULL CHECK (valor IN (0, 1)),
        version_texto TEXT NOT NULL,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    INSERT INTO consentimientos_nueva (id, alumno_id, tipo, valor, version_texto, creado)
        SELECT id, alumno_id,
               CASE WHEN tipo IN ('mails_curso', 'transferencia') THEN tipo ELSE 'novedades' END,
               valor, version_texto, creado
        FROM consentimientos ORDER BY id;
    DROP TABLE consentimientos;
    ALTER TABLE consentimientos_nueva RENAME TO consentimientos;
    CREATE INDEX idx_consentimientos_alumno ON consentimientos (alumno_id, tipo, id);
    """,
    # 4: aprobación manual de las inscripciones (APROBACION_MANUAL). Cada alumno tiene un estado
    # (los que ya existían quedan aprobados), los mails suman el aviso de pedidos a quien administra
    # y los eventos, la aprobación. Para cambiar los CHECK se recrean mails y eventos como en la 3:
    # mismas filas, ids, fechas e índices, y el contador de ids sigue donde estaba (así no se
    # reusan los ids de filas que se borraron con su alumno).
    f"""
    ALTER TABLE alumnos ADD COLUMN estado TEXT NOT NULL DEFAULT 'aprobado'
        CHECK (estado IN ('pendiente', 'aprobado'));

    CREATE TABLE mails_nueva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER REFERENCES alumnos (id) ON DELETE CASCADE,
        tipo TEXT NOT NULL CHECK (tipo IN ('bienvenida', 'recordatorio', 'contame', 'aviso_80', 'pedidos')),
        clave TEXT NOT NULL,
        estado TEXT NOT NULL CHECK (estado IN ('enviado', 'fallido')),
        creado TEXT NOT NULL DEFAULT {AHORA_UTC},
        UNIQUE (alumno_id, clave)
    );
    INSERT INTO mails_nueva (id, alumno_id, tipo, clave, estado, creado)
        SELECT id, alumno_id, tipo, clave, estado, creado FROM mails ORDER BY id;
    DELETE FROM sqlite_sequence WHERE name = 'mails_nueva';
    INSERT INTO sqlite_sequence (name, seq) SELECT 'mails_nueva', seq FROM sqlite_sequence WHERE name = 'mails';
    DROP TABLE mails;
    ALTER TABLE mails_nueva RENAME TO mails;
    CREATE UNIQUE INDEX idx_mails_sin_alumno ON mails (clave) WHERE alumno_id IS NULL;

    CREATE TABLE eventos_nueva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER REFERENCES alumnos (id) ON DELETE SET NULL,
        tipo TEXT NOT NULL
            CHECK (tipo IN ('inscripcion', 'modulo_completo', 'kit', 'link', 'baja_mails', 'borrado', 'aprobacion')),
        detalle TEXT,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    INSERT INTO eventos_nueva (id, alumno_id, tipo, detalle, creado)
        SELECT id, alumno_id, tipo, detalle, creado FROM eventos ORDER BY id;
    DELETE FROM sqlite_sequence WHERE name = 'eventos_nueva';
    INSERT INTO sqlite_sequence (name, seq) SELECT 'eventos_nueva', seq FROM sqlite_sequence WHERE name = 'eventos';
    DROP TABLE eventos;
    ALTER TABLE eventos_nueva RENAME TO eventos;
    CREATE INDEX idx_eventos_tipo ON eventos (tipo, creado);
    """,
    # 5: el siguiente paso al terminar el curso (spec 002, SIGUIENTE_PASO). Cada alumno anota si ya
    # contestó la pregunta (no qué contestó), los permisos suman el aviso "siguiente_paso" y las
    # respuestas se cuentan en una tabla sin alumno ni fecha, así no quedan con nadie. Para cambiar el
    # CHECK de los permisos se recrea la tabla como en la 4: mismas filas, ids, fechas e índice, y el
    # contador de ids sigue donde estaba.
    f"""
    ALTER TABLE alumnos ADD COLUMN siguiente_paso_respondido INTEGER NOT NULL DEFAULT 0
        CHECK (siguiente_paso_respondido IN (0, 1));

    CREATE TABLE consentimientos_nueva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_id INTEGER NOT NULL REFERENCES alumnos (id) ON DELETE CASCADE,
        tipo TEXT NOT NULL CHECK (tipo IN ('mails_curso', 'transferencia', 'novedades', 'siguiente_paso')),
        valor INTEGER NOT NULL CHECK (valor IN (0, 1)),
        version_texto TEXT NOT NULL,
        creado TEXT NOT NULL DEFAULT {AHORA_UTC}
    );
    INSERT INTO consentimientos_nueva (id, alumno_id, tipo, valor, version_texto, creado)
        SELECT id, alumno_id, tipo, valor, version_texto, creado FROM consentimientos ORDER BY id;
    DELETE FROM sqlite_sequence WHERE name = 'consentimientos_nueva';
    INSERT INTO sqlite_sequence (name, seq)
        SELECT 'consentimientos_nueva', seq FROM sqlite_sequence WHERE name = 'consentimientos';
    DROP TABLE consentimientos;
    ALTER TABLE consentimientos_nueva RENAME TO consentimientos;
    CREATE INDEX idx_consentimientos_alumno ON consentimientos (alumno_id, tipo, id);

    CREATE TABLE respuestas_siguiente_paso (
        respuesta TEXT NOT NULL PRIMARY KEY CHECK (respuesta IN ('si', 'no')),
        total INTEGER NOT NULL DEFAULT 0 CHECK (total >= 0)
    );
    """,
)


def conectar(path: Path) -> sqlite3.Connection:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=10, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=10000")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def migrar(con: sqlite3.Connection) -> None:
    version = con.execute("PRAGMA user_version").fetchone()[0]
    for numero, script in enumerate(MIGRACIONES[version:], start=version + 1):
        try:
            con.executescript(f"BEGIN;\n{script}\nPRAGMA user_version = {numero};\nCOMMIT;")
        except sqlite3.Error:
            con.rollback()
            raise
