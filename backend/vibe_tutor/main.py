import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI

from vibe_tutor import admin, alumnos, api, auth, errores, mails, tareas, voz
from vibe_tutor.config import Settings, get_settings

log = logging.getLogger("vibe_tutor")


@contextlib.asynccontextmanager
async def _ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    tarea = None
    try:
        settings = get_settings()
    except Exception:
        log.exception("no se pudo leer la configuración; la tarea periódica no arranca")
        settings = None
    if settings is not None and settings.tareas_activas:
        tarea = asyncio.create_task(tareas.bucle(settings))
    try:
        yield
    finally:
        if tarea is not None:
            tarea.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await tarea


def _configurar_registro() -> None:
    """Que los avisos del curso (log.info) salgan por la terminal o por journald.

    uvicorn configura solo sus propios registros; sin esto, Python muestra de WARNING para arriba.
    Si ya hay algo configurado (por ejemplo, pytest o un --log-config propio), no se toca.
    """
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s: %(message)s")
    # httpx anota cada pedido a las APIs (Claude, Gemini, Resend) en INFO: es ruido.
    logging.getLogger("httpx").setLevel(logging.WARNING)


def crear_app() -> FastAPI:
    _configurar_registro()
    app = FastAPI(
        title="Vibe Tutor", docs_url=None, redoc_url=None, openapi_url=None, lifespan=_ciclo_de_vida
    )
    errores.instalar(app)
    auth.instalar_csrf(app)

    @app.get("/api/salud")
    def salud() -> dict:
        return {"ok": True}

    @app.get("/api/config")
    def config(settings: Settings = Depends(get_settings)) -> dict:
        """Lo que el frontend necesita saber antes de que haya sesión."""
        return {
            "turnstile_site_key": settings.turnstile_site_key or None,
            "aviso_prueba": settings.aviso_prueba,
            "autor_nombre": settings.autor_nombre.strip() or None,
            "newsletter": settings.newsletter_nombre.strip() or None,
            "modo_demo": settings.modo_demo,
            "aprobacion_manual": settings.aprobacion_manual,
        }

    for modulo in (auth, voz, api, alumnos, admin, mails):
        app.include_router(modulo.router)
    return app
