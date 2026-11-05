"""Búsqueda de hiperparámetros con validación cruzada (spec 30, contrato C6).

Todo se decide con validación cruzada sobre el conjunto de entrenamiento: el de prueba
solo se usa al final para reportar.
"""

from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from src.config import PARAMS, SEED
from src.models.evaluacion import evaluar

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


def _nombre(valor) -> str:
    """Nombre legible de un valor de la grilla: (1, 2) -> "(1,2)", "lema" -> "lema"."""
    return f"({valor[0]},{valor[1]})" if isinstance(valor, tuple) else str(valor)


def comparar(pipeline, parametro: str, valores: list, X, y) -> dict:
    """F1 de validación cruzada del MISMO pipeline cambiando solo un parámetro.

    Es un experimento controlado: el modelo, sus hiperparámetros y todo lo demás quedan
    fijos, así la diferencia se debe solo a ese parámetro.
    Ejemplo: comparar(p, "prep__modo", ["stem", "lema"], X, y)
             -> {"stem": {"f1_macro": 0.78, "f1_std": 0.02}, "lema": {...}}
    """
    busqueda = GridSearchCV(pipeline, {parametro: valores}, cv=validacion_cruzada(),
                            scoring=EXPERIMENTOS["scoring"], refit=False).fit(X, y)
    r = busqueda.cv_results_
    return {
        _nombre(v): {"f1_macro": round(float(m), 4), "f1_std": round(float(s), 4)}
        for v, m, s in zip(r[f"param_{parametro}"], r["mean_test_score"], r["std_test_score"])
    }


def experimento_temporal(pipeline, df) -> dict:
    """E3: entrenar con la v1 (2018) y probar con la v2 (2020-21).

    No se usa para decidir nada: mide cuánto se degrada el modelo con noticias de otra
    época y otros temas (en 2018 no existía el COVID-19).
    """
    antes, despues = df[df["anio"] == 2018], df[df["anio"] > 2018]
    modelo = clone(pipeline).fit(antes["texto"].tolist(), antes["etiqueta"].tolist())
    m = evaluar(modelo, despues["texto"].tolist(), despues["etiqueta"].tolist())
    return {"2018 -> 2020-21": {"accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                                "n_train": len(antes), "n_test": len(despues)}}


def experimentos(pipeline, df, X, y) -> dict:
    """E1, E2 y E3 sobre el pipeline del modelo elegido (con sus mejores hiperparámetros)."""
    ngramas = [tuple(r) for r in EXPERIMENTOS["ngram_ranges"]]
    return {
        "stem_vs_lema": comparar(pipeline, "prep__modo", EXPERIMENTOS["modos"], X, y),
        "ngramas": comparar(pipeline, "tfidf__ngram_range", ngramas, X, y),
        "temporal": experimento_temporal(pipeline, df),
    }
