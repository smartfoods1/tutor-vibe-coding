"""Errores de la API en el formato del contrato: {"detalle": "<mensaje para mostrar>"}."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

MENSAJE_VALIDACION = "Revisá los datos: algo no tiene el formato esperado."


def instalar(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def _http(request: Request, error: HTTPException) -> JSONResponse:
        cuerpo = error.detail if isinstance(error.detail, dict) else {"detalle": error.detail}
        return JSONResponse(cuerpo, status_code=error.status_code, headers=getattr(error, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validacion(request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse({"detalle": MENSAJE_VALIDACION}, status_code=422)
