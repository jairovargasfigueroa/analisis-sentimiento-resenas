"""API REST del detector de noticias falsas (spec 40, contrato C8).

Levantar: uvicorn api.main:app --reload --port 8000   (documentación en /docs)
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.esquemas import EntradaPrediccion, ErrorAPI, Estado, Prediccion, validar_texto
from src.config import RUTA_METRICAS, RUTA_MODELO
from src.models.predecir import cargar_modelo, predecir
from src.nlp.explicar import explicar_preprocesamiento

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def error(codigo: str, mensaje: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"codigo": codigo, "mensaje": mensaje}})


@app.exception_handler(ErrorAPI)
async def manejar_error_api(request: Request, exc: ErrorAPI):
    return error(exc.codigo, exc.mensaje, exc.status)


@app.exception_handler(RequestValidationError)
async def manejar_formato_invalido(request: Request, exc: RequestValidationError):
    # Reemplaza el error por defecto de FastAPI para usar el formato único de C8.
    return error("FORMATO_INVALIDO", "El cuerpo debe ser un JSON con el campo 'texto' (string).", 422)


def modelo_o_503(request: Request):
    if request.app.state.modelo is None:
        raise ErrorAPI("MODELO_NO_DISPONIBLE",
                       "No hay modelo entrenado. Ejecuta: python -m src.models.train", 503)
    return request.app.state.modelo


@app.get("/health", response_model=Estado, summary="Estado del servicio y del modelo",
         responses={503: {"description": "El modelo no cargó"}})
def health(request: Request):
    """Indica si la API está viva y si el modelo de producción cargó."""
    cargado = request.app.state.modelo is not None
    cuerpo = {"status": "ok" if cargado else "error", "modelo_cargado": cargado,
              "modelo": request.app.state.nombre_modelo, "version": VERSION}
    return JSONResponse(status_code=200 if cargado else 503, content=cuerpo)


@app.post("/predict", response_model=Prediccion, summary="Clasificar una noticia",
          responses={422: {"description": "Texto vacío, corto, largo o JSON inválido"},
                     503: {"description": "Modelo no disponible"}})
def predict(entrada: EntradaPrediccion, request: Request):
    """Devuelve falsa/verdadera, la probabilidad de cada clase y el preprocesamiento paso a paso."""
    texto = validar_texto(entrada.texto)
    modelo = modelo_o_503(request)
    resultado = predecir(modelo, [texto])[0]
    return {**resultado, "modelo": request.app.state.nombre_modelo,
            "preprocesamiento": explicar_preprocesamiento(texto, modelo.named_steps["prep"].modo)}
