"""API REST del detector de noticias falsas (spec 40, contrato C8).

Levantar: uvicorn api.main:app --reload --port 8000   (documentación en /docs)
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.esquemas import ErrorAPI, Estado
from src.config import RUTA_METRICAS, RUTA_MODELO
from src.models.predecir import cargar_modelo

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo una sola vez al iniciar. Si no existe, la API arranca igual (503)."""
    app.state.modelo = cargar_modelo() if RUTA_MODELO.exists() else None
    app.state.nombre_modelo = (
        json.loads(RUTA_METRICAS.read_text(encoding="utf-8"))["modelo_produccion"]
        if RUTA_METRICAS.exists() else None
    )
    yield


app = FastAPI(title="Detector de Noticias Falsas", version=VERSION, lifespan=lifespan)


def error(codigo: str, mensaje: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"codigo": codigo, "mensaje": mensaje}})


@app.exception_handler(ErrorAPI)
async def manejar_error_api(request: Request, exc: ErrorAPI):
    return error(exc.codigo, exc.mensaje, exc.status)


@app.exception_handler(RequestValidationError)
async def manejar_formato_invalido(request: Request, exc: RequestValidationError):
    # Reemplaza el error por defecto de FastAPI para usar el formato único de C8.
    return error("FORMATO_INVALIDO", "El cuerpo debe ser un JSON con el campo 'texto' (string).", 422)


@app.get("/health", response_model=Estado, summary="Estado del servicio y del modelo",
         responses={503: {"description": "El modelo no cargó"}})
def health(request: Request):
    """Indica si la API está viva y si el modelo de producción cargó."""
    cargado = request.app.state.modelo is not None
    cuerpo = {"status": "ok" if cargado else "error", "modelo_cargado": cargado,
              "modelo": request.app.state.nombre_modelo, "version": VERSION}
    return JSONResponse(status_code=200 if cargado else 503, content=cuerpo)
