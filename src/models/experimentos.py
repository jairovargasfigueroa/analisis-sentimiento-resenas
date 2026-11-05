"""Búsqueda de hiperparámetros con validación cruzada (spec 30, contrato C6).

Todo se decide con validación cruzada sobre el conjunto de entrenamiento: el de prueba
solo se usa al final para reportar.
"""

from sklearn.model_selection import GridSearchCV, StratifiedKFold

from src.config import PARAMS, SEED

EXPERIMENTOS = PARAMS["experiments"]


def validacion_cruzada() -> StratifiedKFold:
    """5 particiones estratificadas (cada una con ~50 % de falsas) y barajadas con SEED."""
    return StratifiedKFold(n_splits=EXPERIMENTOS["cv_folds"], shuffle=True, random_state=SEED)


def grilla(nombre: str) -> dict:
    """params.yaml -> experiments.models.<nombre> con el prefijo del paso "clf" del Pipeline.

    Ejemplo: {"C": [0.1, 1.0]} -> {"clf__C": [0.1, 1.0]}
    """
    return {f"clf__{k}": v for k, v in EXPERIMENTOS["models"][nombre].items()}


def buscar_hiperparametros(pipeline, nombre: str, X, y) -> GridSearchCV:
    """Prueba cada combinación de la grilla con validación cruzada y reentrena la mejor con todo X.

    GridSearchCV clona el pipeline en cada partición, así que el preprocesamiento y TF-IDF se
    ajustan solo con los datos de entrenamiento de esa partición (sin fuga de información).
    """
    busqueda = GridSearchCV(pipeline, grilla(nombre), cv=validacion_cruzada(),
                            scoring=EXPERIMENTOS["scoring"])
    return busqueda.fit(X, y)


def resumen_cv(busqueda: GridSearchCV) -> dict:
    """Mejores hiperparámetros y el F1 de validación cruzada (media y desvío entre particiones)."""
    i = busqueda.best_index_
    return {
        "mejores_hiperparametros": busqueda.best_params_,
        "f1_cv_media": round(float(busqueda.cv_results_["mean_test_score"][i]), 4),
        "f1_cv_std": round(float(busqueda.cv_results_["std_test_score"][i]), 4),
    }
