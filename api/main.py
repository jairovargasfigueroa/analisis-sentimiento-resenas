"""API REST del detector de noticias falsas (spec 40, contrato C8).

Levantar: uvicorn api.main:app --reload --port 8000   (documentación en /docs)
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.esquemas import ErrorAPI

VERSION = "1.0.0"


app = FastAPI(title="Detector de Noticias Falsas", version=VERSION)


def error(codigo: str, mensaje: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"codigo": codigo, "mensaje": mensaje}})


@app.exception_handler(ErrorAPI)
async def manejar_error_api(request: Request, exc: ErrorAPI):
    return error(exc.codigo, exc.mensaje, exc.status)


@app.exception_handler(RequestValidationError)
async def manejar_formato_invalido(request: Request, exc: RequestValidationError):
    # Reemplaza el error por defecto de FastAPI para usar el formato único de C8.
    return error("FORMATO_INVALIDO", "El cuerpo debe ser un JSON con el campo 'texto' (string).", 422)
