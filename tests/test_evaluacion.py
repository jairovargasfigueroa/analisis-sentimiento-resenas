"""Tests de la evaluación (spec 30, contrato C6). Usan modelos falsos para ser instantáneos."""

import numpy as np
import pytest

from src.config import ETIQUETAS
from src.models.evaluacion import analizar_errores, evaluar, evaluar_baseline


class ModeloFijo:
    """Devuelve probabilidades fijas: permite saber de antemano qué acierta y qué no."""

    classes_ = np.array(ETIQUETAS)

    def __init__(self, prob_verdadera):
        self.p = np.array(prob_verdadera)

    def predict_proba(self, X):
        return np.column_stack([1 - self.p, self.p])

    def predict(self, X):
        return self.classes_[(self.p > 0.5).astype(int)]


Y = ["falsa", "falsa", "verdadera", "verdadera"]


def test_evaluar_cumple_c6():
    m = evaluar(ModeloFijo([0.1, 0.8, 0.9, 0.3]), [""] * 4, Y)
    assert {"accuracy", "precision_macro", "recall_macro", "f1_macro",
            "matriz_confusion", "etiquetas", "por_clase"} <= set(m)
    assert m["accuracy"] == 0.5
    # filas = real, columnas = predicho: 1 falsa bien y 1 mal; 1 verdadera bien y 1 mal
    assert m["matriz_confusion"] == [[1, 1], [1, 1]]
    assert set(m["por_clase"]) == set(ETIQUETAS)
    assert m["por_clase"]["falsa"]["soporte"] == 2


def test_baseline_predice_siempre_la_mayoritaria():
    y_train = ["verdadera"] * 3 + ["falsa"]
    m = evaluar_baseline([""] * 4, y_train, [""] * 4, Y)
    assert m["matriz_confusion"] == [[0, 2], [0, 2]]
    assert m["accuracy"] == 0.5


def test_errores_ordenados_por_confianza():
    errores = analizar_errores(ModeloFijo([0.1, 0.8, 0.9, 0.3]), [""] * 4, Y)
    assert [e["indice"] for e in errores] == [1, 3]   # 0.8 equivocado antes que 0.7
    assert errores[0] == {"indice": 1, "real": "falsa", "predicho": "verdadera", "probabilidad": 0.8}
    assert errores[1]["probabilidad"] == pytest.approx(0.7)
