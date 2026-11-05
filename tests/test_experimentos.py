"""Tests de la búsqueda y los experimentos (spec 30): reproducibilidad y formato de C6.

Usan 150 noticias y stemming para tardar segundos; el entrenamiento real usa todo el train.
"""

from tempfile import TemporaryDirectory

import pytest
from sklearn.linear_model import LogisticRegression

from src.config import SEED
from src.data.cargar import cargar_procesado
from src.models.experimentos import buscar_hiperparametros, comparar, grilla, resumen_cv
from src.models.train import construir_pipeline, dividir, elegir


@pytest.fixture(scope="module")
def muestra():
    X_train, _, y_train, _ = dividir(cargar_procesado())
    return X_train[:150], y_train[:150]


def buscar(X, y):
    with TemporaryDirectory() as memoria:
        pipeline = construir_pipeline(LogisticRegression(max_iter=1000, random_state=SEED),
                                      modo="stem", memoria=memoria)
        return resumen_cv(buscar_hiperparametros(pipeline, "regresion_logistica", X, y))


def test_dos_entrenamientos_dan_las_mismas_metricas(muestra):
    # SEED fija el barajado de las particiones y el modelo: mismo resultado siempre.
    assert buscar(*muestra) == buscar(*muestra)


def test_grilla_lee_params_yaml():
    assert set(grilla("regresion_logistica")) == {"clf__C"}
    assert set(grilla("naive_bayes")) == {"clf__alpha"}


def test_comparar_cambia_un_solo_parametro(muestra):
    pipeline = construir_pipeline(LogisticRegression(max_iter=1000, random_state=SEED), modo="stem")
    r = comparar(pipeline, "tfidf__ngram_range", [(1, 1), (1, 2)], *muestra)
    assert set(r) == {"(1,1)", "(1,2)"}
    assert all(0 <= v["f1_macro"] <= 1 for v in r.values())


def test_elige_por_validacion_cruzada_no_por_test():
    resultados = {
        "baseline": {"f1_macro": 0.33},
        "a": {"f1_macro": 0.90, "f1_cv_media": 0.70},   # mejor en test, peor en CV
        "b": {"f1_macro": 0.80, "f1_cv_media": 0.75},
    }
    assert elegir(resultados) == "b"
