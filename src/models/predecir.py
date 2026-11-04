"""Predicción con el modelo serializado (contrato C7). La usa la API."""

import joblib
from sklearn.pipeline import Pipeline

from src.config import ETIQUETAS, RUTA_MODELO


def cargar_modelo(ruta=RUTA_MODELO) -> Pipeline:
    """Carga el Pipeline completo (prep -> tfidf -> clf) guardado por train.py."""
    return joblib.load(ruta)


def predecir(modelo: Pipeline, textos: list[str]) -> list[dict]:
    """Clase, su probabilidad y la probabilidad de cada etiqueta, en el orden de ETIQUETAS.

    Ejemplo: [{"clase": "falsa", "probabilidad": 0.93,
               "probabilidades": {"falsa": 0.93, "verdadera": 0.07}}]
    """
    # predict_proba ordena las columnas según modelo.classes_, no según ETIQUETAS.
    columnas = list(modelo.classes_)
    resultados = []
    for fila in modelo.predict_proba(textos):
        probs = {e: round(float(fila[columnas.index(e)]), 4) for e in ETIQUETAS}
        clase = max(probs, key=probs.get)
        resultados.append({"clase": clase, "probabilidad": probs[clase], "probabilidades": probs})
    return resultados
