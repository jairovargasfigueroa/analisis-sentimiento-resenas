"""Entrenamiento: python -m src.models.train (spec 30, contrato C6).

Va de data/raw a models/ sin pasos manuales: carga, split, entrena, evalúa y guarda.
"""

import json
from datetime import datetime

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.config import PARAMS, RUTA_METRICAS, RUTA_MODELO, SEED, TEST_SIZE
from src.data.cargar import cargar_procesado
from src.models.evaluacion import evaluar, evaluar_baseline
from src.models.experimentos import buscar_hiperparametros, resumen_cv
from src.nlp.preprocesador import TextPreprocessor

# Nombre (el de params.yaml -> experiments.models) -> clasificador.
# Para comparar otro modelo basta agregarlo aquí y su grilla en params.yaml.
CLASIFICADORES = {
    "regresion_logistica": LogisticRegression(max_iter=1000, random_state=SEED),
    # Multinomial: modela la frecuencia de cada término por clase; acepta los pesos TF-IDF.
    "naive_bayes": MultinomialNB(),
}


def dividir(df):
    """Split estratificado 80/20 con SEED. El test no se usa para ajustar nada."""
    return train_test_split(
        df["texto"].tolist(), df["etiqueta"].tolist(),
        test_size=TEST_SIZE, stratify=df["etiqueta"], random_state=SEED,
    )


def construir_pipeline(clf, modo=None, ngram_range=None) -> Pipeline:
    """prep -> tfidf -> clf, con los valores de params.yaml salvo que se indiquen otros."""
    tfidf = dict(PARAMS["tfidf"])
    tfidf["ngram_range"] = tuple(ngram_range or tfidf["ngram_range"])
    return Pipeline([
        ("prep", TextPreprocessor(modo=modo or PARAMS["nlp"]["modo"])),
        ("tfidf", TfidfVectorizer(**tfidf)),
        ("clf", clf),
    ])


def entrenar():
    """Línea base y GridSearchCV de cada clasificador; devuelve (modelos, resultados, datos).

    Los hiperparámetros se eligen con validación cruzada en train; test solo se reporta.
    """
    df = cargar_procesado()
    X_train, X_test, y_train, y_test = dividir(df)

    resultados = {"baseline": evaluar_baseline(X_train, y_train, X_test, y_test)}
    modelos = {}
    for nombre, clf in CLASIFICADORES.items():
        busqueda = buscar_hiperparametros(construir_pipeline(clf), nombre, X_train, y_train)
        modelos[nombre] = busqueda.best_estimator_
        resultados[nombre] = {**evaluar(modelos[nombre], X_test, y_test), **resumen_cv(busqueda)}
    return modelos, resultados, (df, X_train, X_test)


def guardar(modelos, resultados, datos) -> str:
    """Guarda el modelo de producción y metricas.json (C6). Devuelve el nombre elegido."""
    df, X_train, X_test = datos
    # shortcut: elige por F1 en test porque aún no hay validación cruzada; el PR 2.2 la usa.
    elegido = max(modelos, key=lambda n: resultados[n]["f1_macro"])
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelos[elegido], RUTA_MODELO)

    prep = modelos[elegido].named_steps["prep"]
    tfidf = modelos[elegido].named_steps["tfidf"]
    metricas = {
        "modelo_produccion": elegido,
        "justificacion": "Único modelo entrenado por ahora; supera ampliamente a la línea base.",
        "fecha_entrenamiento": datetime.now().isoformat(timespec="seconds"),
        "dataset": {
            "nombre": "The Spanish Fake News Corpus",
            "n_total": len(df), "n_train": len(X_train), "n_test": len(X_test),
            "distribucion_clases": df["etiqueta"].value_counts().to_dict(),
        },
        "preprocesamiento": {
            "modo": prep.modo, "ngram_range": list(tfidf.ngram_range), "min_df": tfidf.min_df,
            "max_df": tfidf.max_df, "max_features": tfidf.max_features,
        },
        "modelos": resultados,
    }
    RUTA_METRICAS.write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    return elegido


if __name__ == "__main__":
    modelos, resultados, datos = entrenar()
    print(f"{'modelo':<22}{'f1_cv':>8}{'accuracy':>10}{'f1_test':>9}  hiperparámetros")
    for nombre, r in resultados.items():
        cv = f"{r['f1_cv_media']:.3f}" if "f1_cv_media" in r else "-"
        print(f"{nombre:<22}{cv:>8}{r['accuracy']:>10.3f}{r['f1_macro']:>9.3f}  "
              f"{r.get('mejores_hiperparametros', '')}")
    elegido = guardar(modelos, resultados, datos)
    print(f"Modelo en producción: {elegido} -> {RUTA_MODELO}")
