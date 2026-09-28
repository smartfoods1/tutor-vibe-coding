from datetime import datetime, timedelta, timezone

import pytest
import yaml

from vibe_tutor import admin, costos, dominio

T0 = datetime(2026, 9, 28, 15, 0, tzinfo=timezone.utc)
ADMIN = "admin@example.com"
RUTAS = ("/api/admin/reporte", "/api/admin/novedades.csv", "/api/admin/links")


def _iso(momento: datetime) -> str:
    return momento.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


@pytest.fixture(autouse=True)
def reloj(monkeypatch):
    monkeypatch.setattr(admin, "ahora", lambda: T0)


@pytest.fixture
def base(db_de):
    con = db_de()
    yield con
    con.close()


@pytest.fixture
def cliente(hacer_cliente):
    return hacer_cliente([admin.router], email=ADMIN)


def _dato(id_: str, verificado: str) -> dict:
    return {
        "id": id_,
        "tema": "instalar",
        "aplica_a": ["codex"],
        "sistema": ["mac"],
        "texto": "Bajá la app de escritorio desde la página oficial.",
        "fuente": "https://example.com/oficial",
        "verificado": verificado,
        "probado": True,
    }


@pytest.fixture
def machete(settings_tmp):
    raiz = settings_tmp.contenido_dir
    raiz.mkdir(parents=True, exist_ok=True)
    datos = [
        _dato("dato-vencido", "2026-08-13"), _dato("dato-al-limite", "2026-08-14"), _dato("dato-nuevo", "2026-09-27")
    ]
    (raiz / "machete.yaml").write_text(yaml.safe_dump(datos, allow_unicode=True), encoding="utf-8")
    return raiz


def _evento(con, alumno_id, tipo: str, detalle: str | None, creado: datetime) -> None:
    with con:
        con.execute(
            "INSERT INTO eventos (alumno_id, tipo, detalle, creado) VALUES (?, ?, ?, ?)",
            (alumno_id, tipo, detalle, _iso(creado)),
        )


def _hace(dias: float) -> datetime:
    return T0 - timedelta(days=dias)


def _etapas(inscriptos=0, modulo_1=0, modulo_2=0, modulo_3=0, kits=0, links=0) -> dict:
    return {
        "inscriptos": inscriptos, "modulo_1": modulo_1, "modulo_2": modulo_2,
        "modulo_3": modulo_3, "kits": kits, "links": links,
    }


# --- acceso ------------------------------------------------------------------------------------------


@pytest.mark.parametrize("ruta", RUTAS)
def test_sin_sesion_da_401(hacer_cliente, ruta):
    assert hacer_cliente([admin.router]).get(ruta).status_code == 401


@pytest.mark.parametrize("ruta", RUTAS)
def test_un_alumno_comun_no_entra(hacer_cliente, ruta):
    respuesta = hacer_cliente([admin.router], email="ana@example.com").get(ruta)

    assert respuesta.status_code == 403
    assert set(respuesta.json()) == {"detalle"}


# --- reporte -----------------------------------------------------------------------------------------


def test_embudo_total_ultimos_30_dias_y_por_fuente(cliente, base, machete):
    ana = dominio.crear_alumno(base, "ana@example.com", fuente="hecho-en")
    _evento(base, ana, "inscripcion", "fuente=hecho-en", _hace(40))
    for modulo, dias in ((1, 39), (2, 38), (3, 37)):
        _evento(base, ana, "modulo_completo", f"modulo={modulo}", _hace(dias))
    _evento(base, ana, "kit", "herramienta=codex", _hace(36))
    _evento(base, ana, "kit", "herramienta=codex", _hace(5))
    _evento(base, ana, "link", None, _hace(2))

    beto = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    _evento(base, beto, "inscripcion", None, _hace(10))
    _evento(base, beto, "modulo_completo", "modulo=1", _hace(9))
    _evento(base, beto, "baja_mails", None, _hace(8))

    # Alguien que borró sus datos: sus eventos quedan sin alumno_id.
    _evento(base, None, "inscripcion", "fuente=hecho-en", _hace(3))
    _evento(base, None, "modulo_completo", "modulo=1", _hace(3))
    _evento(base, None, "borrado", None, _hace(1))

    respuesta = cliente.get("/api/admin/reporte")

    assert respuesta.status_code == 200
    embudo = respuesta.json()["embudo"]
    assert embudo["total"] == _etapas(inscriptos=3, modulo_1=3, modulo_2=1, modulo_3=1, kits=1, links=1)
    assert embudo["ultimos_30_dias"] == _etapas(inscriptos=2, modulo_1=2, kits=1, links=1)
    assert embudo["por_fuente"] == [
        {
            "fuente": "hecho-en",
            "total": _etapas(inscriptos=1, modulo_1=1, modulo_2=1, modulo_3=1, kits=1, links=1),
            "ultimos_30_dias": _etapas(kits=1, links=1),
        },
        {
            "fuente": None,
            "total": _etapas(inscriptos=1, modulo_1=1),
            "ultimos_30_dias": _etapas(inscriptos=1, modulo_1=1),
        },
    ]


def test_reporte_vacio(cliente, machete):
    datos = cliente.get("/api/admin/reporte").json()

    assert datos["embudo"] == {"total": _etapas(), "ultimos_30_dias": _etapas(), "por_fuente": []}
    assert datos["gasto"]["mes_usd"] == 0
    assert datos["gasto"]["promedio_por_alumno_usd"] == 0
    assert datos["generado"] == "2026-09-28T15:00:00+00:00"


def test_gasto_del_mes_contra_el_tope_y_promedio_por_alumno(cliente, base, machete, settings_tmp):
    ana = dominio.crear_alumno(base, "ana@example.com", fuente=None)
    beto = dominio.crear_alumno(base, "beto@example.com", fuente=None)
    for alumno_id, costo, creado in (
        (ana, 0.30, _hace(1)),
        (beto, 0.10, _hace(2)),
        (None, 0.20, _hace(3)),
        (ana, 0.50, datetime(2026, 8, 20, tzinfo=timezone.utc)),
    ):
        costos.registrar(base, "anthropic", "claude-sonnet-5", {}, costo, alumno_id=alumno_id)
        with base:
            base.execute("UPDATE uso SET creado = ? WHERE id = (SELECT max(id) FROM uso)", (_iso(creado),))

    gasto = cliente.get("/api/admin/reporte").json()["gasto"]

    assert gasto["mes_usd"] == pytest.approx(0.60)
    assert gasto["tope_mensual_usd"] == 50.0
    assert gasto["porcentaje_tope"] == pytest.approx(1.2)
    assert gasto["aviso_80"] is False
    assert gasto["bloqueado"] is False
    assert gasto["tope_alumno_usd"] == settings_tmp.tope_alumno_usd
    assert gasto["promedio_por_alumno_usd"] == pytest.approx(0.45)
    assert gasto["alumnos_con_gasto"] == 2


def test_gasto_al_80_por_ciento(cliente, base, machete):
    costos.registrar(base, "anthropic", "claude-sonnet-5", {}, 41.0)
    with base:
        base.execute("UPDATE uso SET creado = ?", (_iso(_hace(1)),))

    gasto = cliente.get("/api/admin/reporte").json()["gasto"]

    assert gasto["aviso_80"] is True
    assert gasto["porcentaje_tope"] == pytest.approx(82.0)


def test_datos_del_machete_con_mas_de_45_dias(cliente, machete):
    datos = cliente.get("/api/admin/reporte").json()["machete"]

    assert datos["error"] is None
    assert datos["total"] == 3
    assert datos["vencidos"] == [
        {
            "id": "dato-vencido",
            "tema": "instalar",
            "verificado": "2026-08-13",
            "dias": 46,
            "fuente": "https://example.com/oficial",
        }
    ]


def test_reporte_sin_machete_igual_responde(cliente):
    respuesta = cliente.get("/api/admin/reporte")

    assert respuesta.status_code == 200
    assert respuesta.json()["machete"]["vencidos"] == []
    assert "machete.yaml" in respuesta.json()["machete"]["error"]


# --- CSV de las novedades ------------------------------------------------------------------------------


def test_novedades_csv_solo_los_que_aceptaron_las_novedades(cliente, base):
    def alumno(email: str, *valores: bool) -> None:
        alumno_id = dominio.crear_alumno(base, email, fuente=None)
        for valor in valores:
            dominio.agregar_consentimiento(base, alumno_id, "novedades", valor, "2026-10-01")

    alumno("si@example.com", True)
    alumno("se-arrepintio@example.com", True, False)
    alumno("cambio-de-idea@example.com", False, True)
    alumno("nunca@example.com")
    alumno("no@example.com", False)
    alumno("=hyperlink(1)@example.com", True)

    respuesta = cliente.get("/api/admin/novedades.csv")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/csv")
    assert "attachment" in respuesta.headers["content-disposition"]
    assert 'filename="novedades.csv"' in respuesta.headers["content-disposition"]
    assert respuesta.headers["cache-control"] == "no-store"
    assert respuesta.text.splitlines() == ["email", "si@example.com", "cambio-de-idea@example.com"]


def test_novedades_csv_sin_nadie(cliente):
    assert cliente.get("/api/admin/novedades.csv").text.splitlines() == ["email"]


# --- moderación de la galería ----------------------------------------------------------------------


def _link(con, alumno_id: int, url: str, *, galeria: bool, aprobado: bool = False, titulo: str | None = None) -> int:
    with con:
        return con.execute(
            "INSERT INTO links (alumno_id, url, titulo, mostrar_galeria, aprobado) VALUES (?, ?, ?, ?, ?)",
            (alumno_id, url, titulo, int(galeria), int(aprobado)),
        ).lastrowid


def test_links_para_moderar_pendientes_primero(cliente, base):
    alumno = dominio.crear_alumno(base, "ana@example.com", fuente=None)
    aprobado = _link(base, alumno, "https://aprobado.netlify.app", galeria=True, aprobado=True, titulo="Ya está")
    _link(base, alumno, "https://privado.netlify.app", galeria=False)
    pendiente_viejo = _link(base, alumno, "https://viejo.netlify.app", galeria=True)
    pendiente_nuevo = _link(base, alumno, "https://nuevo.netlify.app", galeria=True, titulo="Nuevo")

    respuesta = cliente.get("/api/admin/links")

    assert respuesta.status_code == 200
    links = respuesta.json()
    assert [link["id"] for link in links] == [pendiente_nuevo, pendiente_viejo, aprobado]
    assert {k: v for k, v in links[0].items() if k != "creado"} == {
        "id": pendiente_nuevo, "url": "https://nuevo.netlify.app", "titulo": "Nuevo",
        "mostrar_galeria": True, "aprobado": False,
    }
    assert links[2]["aprobado"] is True
    assert links[0]["creado"]
    assert "ana@example.com" not in respuesta.text


def test_aprobar_y_desaprobar_un_link(cliente, base):
    alumno = dominio.crear_alumno(base, "ana@example.com", fuente=None)
    link_id = _link(base, alumno, "https://mi-idea.netlify.app", galeria=True)

    aprobar = cliente.put(f"/api/admin/links/{link_id}", json={"aprobado": True})

    assert aprobar.status_code == 200
    assert aprobar.json()["aprobado"] is True
    assert base.execute("SELECT aprobado FROM links WHERE id = ?", (link_id,)).fetchone()[0] == 1
    assert cliente.put(f"/api/admin/links/{link_id}", json={"aprobado": False}).json()["aprobado"] is False
    assert base.execute("SELECT aprobado FROM links WHERE id = ?", (link_id,)).fetchone()[0] == 0


def test_aprobar_un_link_que_no_existe_da_404(cliente):
    respuesta = cliente.put("/api/admin/links/999", json={"aprobado": True})

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"]


def test_aprobar_pide_un_booleano(cliente, base):
    alumno = dominio.crear_alumno(base, "ana@example.com", fuente=None)
    link_id = _link(base, alumno, "https://mi-idea.netlify.app", galeria=True)

    assert cliente.put(f"/api/admin/links/{link_id}", json={}).status_code == 422
    assert cliente.put(f"/api/admin/links/{link_id}", json={"aprobado": "tal vez"}).status_code == 422


def test_un_alumno_comun_no_aprueba_links(hacer_cliente, base):
    alumno = hacer_cliente([admin.router], email="ana@example.com")
    link_id = _link(base, alumno.alumno_id, "https://mi-idea.netlify.app", galeria=True)

    respuesta = alumno.put(f"/api/admin/links/{link_id}", json={"aprobado": True})

    assert respuesta.status_code == 403
    assert base.execute("SELECT aprobado FROM links WHERE id = ?", (link_id,)).fetchone()[0] == 0
