"""Tests de la API (spec 40, contrato C8). Usan un modelo chico entrenado en el fixture."""

import pytest
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression

from api.main import app
from src.config import LONGITUD_MAX_TEXTO, SEED
from src.data.cargar import cargar_procesado
from src.models.train import construir_pipeline, dividir

NOTICIA = ("El Ministerio de Salud informó este lunes que la campaña de vacunación contra la "
           "influenza comenzará la próxima semana en todos los centros de salud del país.")


@pytest.fixture(scope="module")
def cliente():
    X_train, _, y_train, _ = dividir(cargar_procesado())
    modelo = construir_pipeline(LogisticRegression(max_iter=1000, random_state=SEED), modo="stem")
    with TestClient(app) as c:
        app.state.modelo = modelo.fit(X_train, y_train)
        app.state.nombre_modelo = "regresion_logistica"
        yield c


def codigo(r):
    return r.json()["error"]["codigo"]


def test_health(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200
    assert r.json()["modelo_cargado"] is True


def test_predict_cumple_c8(cliente):
    r = cliente.post("/predict", json={"texto": NOTICIA})
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"clase", "probabilidad", "probabilidades", "modelo", "preprocesamiento"}
    assert cuerpo["clase"] in ("falsa", "verdadera")
    assert cuerpo["preprocesamiento"]["original"] == NOTICIA
    assert cuerpo["preprocesamiento"]["modo"] == "stem"


@pytest.mark.parametrize("texto,esperado", [
    ("", "TEXTO_VACIO"),
    ("   ", "TEXTO_VACIO"),
    ("Noticia de solo cinco palabras", "TEXTO_DEMASIADO_CORTO"),
    ("palabra " * (LONGITUD_MAX_TEXTO // 8 + 1), "TEXTO_DEMASIADO_LARGO"),
])
def test_validaciones_de_texto(cliente, texto, esperado):
    r = cliente.post("/predict", json={"texto": texto})
    assert r.status_code == 422
    assert codigo(r) == esperado


@pytest.mark.parametrize("cuerpo", [{}, {"texto": 123}, {"otro": "x"}])
def test_formato_invalido(cliente, cuerpo):
    r = cliente.post("/predict", json=cuerpo)
    assert r.status_code == 422
    assert codigo(r) == "FORMATO_INVALIDO"


def test_json_mal_formado(cliente):
    r = cliente.post("/predict", content="{no es json", headers={"Content-Type": "application/json"})
    assert codigo(r) == "FORMATO_INVALIDO"


def test_sin_modelo_responde_503(cliente):
    guardado = app.state.modelo
    app.state.modelo = None
    try:
        assert cliente.get("/health").status_code == 503
        r = cliente.post("/predict", json={"texto": NOTICIA})
        assert r.status_code == 503 and codigo(r) == "MODELO_NO_DISPONIBLE"
    finally:
        app.state.modelo = guardado


def test_cors_permite_el_frontend(cliente):
    r = cliente.options("/predict", headers={"Origin": "http://localhost:5173",
                                             "Access-Control-Request-Method": "POST"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
