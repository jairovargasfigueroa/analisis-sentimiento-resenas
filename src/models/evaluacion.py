"""Evaluación de modelos: métricas, línea base y errores (spec 30, contrato C6)."""

from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from src.config import ETIQUETAS


def evaluar(modelo, X, y) -> dict:
    """Métricas de C6 sobre (X, y), más el detalle por clase.

    Macro: las dos clases pesan igual. matriz_confusion[i][j] = noticias de la clase
    ETIQUETAS[i] que el modelo predijo como ETIQUETAS[j] (filas = real, columnas = predicho).
    """
    pred = modelo.predict(X)
    p, r, f1, _ = precision_recall_fscore_support(y, pred, average="macro", zero_division=0)
    pc, rc, f1c, soporte = precision_recall_fscore_support(
        y, pred, labels=ETIQUETAS, zero_division=0)
    return {
        "accuracy": round(accuracy_score(y, pred), 4),
        "precision_macro": round(p, 4), "recall_macro": round(r, 4), "f1_macro": round(f1, 4),
        "matriz_confusion": confusion_matrix(y, pred, labels=ETIQUETAS).tolist(),
        "etiquetas": ETIQUETAS,
        "por_clase": {
            e: {"precision": round(pc[i], 4), "recall": round(rc[i], 4),
                "f1": round(f1c[i], 4), "soporte": int(soporte[i])}
            for i, e in enumerate(ETIQUETAS)
        },
    }


def evaluar_baseline(X_train, y_train, X_test, y_test) -> dict:
    """Línea base: predecir siempre la clase más frecuente del entrenamiento.

    Si un modelo no la supera con holgura, no aporta nada (enunciado, 5.3).
    """
    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    return evaluar(baseline, X_test, y_test)


def analizar_errores(modelo, X, y, n=10) -> list[dict]:
    """Los n errores en que el modelo estaba más seguro (mayor probabilidad de la clase equivocada).

    Son los más útiles para entender qué aprendió: un error con 0,51 es una duda, uno con
    0,95 muestra un patrón que engaña al modelo.
    """
    columnas = list(modelo.classes_)
    errores = []
    for i, (fila, real) in enumerate(zip(modelo.predict_proba(X), y)):
        predicho = columnas[fila.argmax()]
        if predicho != real:
            errores.append({"indice": i, "real": real, "predicho": predicho,
                            "probabilidad": round(float(fila.max()), 4)})
    return sorted(errores, key=lambda e: e["probabilidad"], reverse=True)[:n]
