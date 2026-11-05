"""API REST del detector de noticias falsas (spec 40, contrato C8).

Levantar: uvicorn api.main:app --reload --port 8000   (documentación en /docs)
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.esquemas import (EntradaLote, EntradaPrediccion, ErrorAPI, Estado, Prediccion,
                          PrediccionLote, validar_lote, validar_texto)
from src.config import ETIQUETAS, RUTA_METRICAS, RUTA_MODELO
from src.models.predecir import cargar_modelo, predecir
from src.nlp.explicar import explicar_preprocesamiento

VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo y sus métricas una sola vez al iniciar. Si no existen, la API arranca igual (503).

    Las métricas se leen junto con el modelo para que /metrics describa siempre el modelo que
    está sirviendo /predict: si se reentrena, hay que reiniciar uvicorn y cambian los dos a la vez.
    """
    app.state.modelo = cargar_modelo() if RUTA_MODELO.exists() else None
    app.state.metricas = (
        json.loads(RUTA_METRICAS.read_text(encoding="utf-8")) if RUTA_METRICAS.exists() else None
    )
    app.state.nombre_modelo = app.state.metricas["modelo_produccion"] if app.state.metricas else None
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
    campo = ("'textos' (lista de strings)" if request.url.path.endswith("/lote")
             else "'texto' (string)")
    return error("FORMATO_INVALIDO", f"El cuerpo debe ser un JSON con el campo {campo}.", 422)


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


@app.post("/predict/lote", response_model=PrediccionLote, summary="Clasificar varias noticias",
          responses={422: {"description": "Lote vacío, demasiado grande o con una noticia inválida"},
                     503: {"description": "Modelo no disponible"}})
def predict_lote(entrada: EntradaLote, request: Request):
    """Clasifica de 1 a MAX_TEXTOS_LOTE noticias en una sola llamada y resume cuántas hay por clase.

    No devuelve el paso a paso (sería muy pesado): para eso está /predict con una noticia.
    """
    textos = validar_lote(entrada.textos)
    modelo = modelo_o_503(request)
    resultados = [{"texto": t, **r} for t, r in zip(textos, predecir(modelo, textos))]
    resumen = {e: sum(r["clase"] == e for r in resultados) for e in ETIQUETAS}
    return {"resultados": resultados, "resumen": resumen}


@app.get("/metrics", summary="Métricas y comparación de los modelos",
         responses={503: {"description": "No hay modelo entrenado"}})
def metrics(request: Request):
    """Devuelve models/metricas.json (contrato C6): modelo en producción y por qué, métricas de
    la línea base y de cada modelo, experimentos E1-E3, palabras influyentes y errores."""
    if request.app.state.metricas is None:
        raise ErrorAPI("MODELO_NO_DISPONIBLE",
                       "No hay métricas: falta entrenar. Ejecuta: python -m src.models.train", 503)
    return request.app.state.metricas
