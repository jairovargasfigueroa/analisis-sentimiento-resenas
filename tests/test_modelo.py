"""Tests del entrenamiento base y la predicción (spec 30, contratos C6 y C7)."""

import joblib
import pytest
from sklearn.linear_model import LogisticRegression

from src.config import ETIQUETAS, SEED
from src.data.cargar import cargar_procesado
from src.models.predecir import cargar_modelo, predecir
from src.models.train import construir_pipeline, dividir


@pytest.fixture(scope="module")
def datos():
    return dividir(cargar_procesado())


@pytest.fixture(scope="module")
def modelo(datos, tmp_path_factory):
    # modo "stem" para que el test tarde segundos; el modelo real usa params.yaml.
    X_train, _, y_train, _ = datos
    pipe = construir_pipeline(LogisticRegression(max_iter=1000, random_state=SEED), modo="stem")
    ruta = tmp_path_factory.mktemp("modelos") / "modelo.joblib"
    joblib.dump(pipe.fit(X_train, y_train), ruta)
    return cargar_modelo(ruta)


def test_split_estratificado(datos):
    X_train, X_test, y_train, y_test = datos
    assert len(X_test) == pytest.approx(0.2 * (len(X_train) + len(X_test)), abs=1)
    proporcion = lambda y: y.count("falsa") / len(y)
    assert proporcion(y_train) == pytest.approx(proporcion(y_test), abs=0.01)


def test_predecir_cumple_c7(modelo):
    r = predecir(modelo, ["El Ministerio de Salud informó este lunes el inicio de la campaña."])[0]
    assert set(r) == {"clase", "probabilidad", "probabilidades"}
    assert list(r["probabilidades"]) == ETIQUETAS
    assert sum(r["probabilidades"].values()) == pytest.approx(1, abs=1e-3)
    assert r["probabilidad"] == max(r["probabilidades"].values())


def test_casos_obvios(modelo, datos):
    # Noticias de entrenamiento: el modelo cargado debe acertar la mayoría (ya las vio).
    X_train, _, y_train, _ = datos
    clases = [r["clase"] for r in predecir(modelo, X_train[:50])]
    assert sum(c == y for c, y in zip(clases, y_train[:50])) >= 45


def test_supera_a_la_linea_base(modelo, datos):
    _, X_test, _, y_test = datos
    clases = [r["clase"] for r in predecir(modelo, X_test)]
    assert sum(c == y for c, y in zip(clases, y_test)) / len(y_test) > 0.65
