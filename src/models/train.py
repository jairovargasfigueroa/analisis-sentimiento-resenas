"""Entrenamiento: python -m src.models.train [--rapido] (spec 30, contrato C6).

Va de data/raw a models/ sin pasos manuales: carga, split, entrena, evalúa y guarda.
Completo tarda unos 7 minutos; --rapido salta los experimentos E1, E2 y E3.
"""

import json
import sys
from datetime import datetime
from tempfile import TemporaryDirectory

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.config import PARAMS, RUTA_METRICAS, RUTA_MODELO, SEED, TEST_SIZE
from src.data.cargar import cargar_procesado
from src.models.evaluacion import (analizar_errores, evaluar, evaluar_baseline,
                                   palabras_influyentes)
from src.models.experimentos import buscar_hiperparametros, experimentos, resumen_cv
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


def construir_pipeline(clf, modo=None, ngram_range=None, memoria=None) -> Pipeline:
    """prep -> tfidf -> clf, con los valores de params.yaml salvo que se indiquen otros.

    memoria: carpeta donde el Pipeline guarda el resultado de prep y tfidf. En GridSearchCV
    solo cambia clf, así que cada partición se lematiza una vez y no una por combinación.
    """
    tfidf = dict(PARAMS["tfidf"])
    tfidf["ngram_range"] = tuple(ngram_range or tfidf["ngram_range"])
    return Pipeline([
        ("prep", TextPreprocessor(modo=modo or PARAMS["nlp"]["modo"])),
        ("tfidf", TfidfVectorizer(**tfidf)),
        ("clf", clf),
    ], memory=memoria)


def experimentos_anteriores() -> dict:
    """Los experimentos del último metricas.json, para no recalcularlos en el modo rápido."""
    if not RUTA_METRICAS.exists():
        return {}
    return json.loads(RUTA_METRICAS.read_text(encoding="utf-8")).get("experimentos", {})


def entrenar(con_experimentos=True):
    """Línea base, GridSearchCV de cada clasificador y experimentos.

    Devuelve (modelos, resultados, experimentos, datos).

    Los hiperparámetros se eligen con validación cruzada en train; test solo se reporta.
    con_experimentos=False salta E1, E2 y E3 (los más lentos) y conserva los anteriores: sirve
    para reentrenar rápido tras cambiar una stop word o un hiperparámetro.
    """
    df = cargar_procesado()
    X_train, X_test, y_train, y_test = dividir(df)

    resultados = {"baseline": evaluar_baseline(X_train, y_train, X_test, y_test)}
    busquedas = {}
    # Caché temporal compartida por los dos modelos y los experimentos: usan el mismo prep y tfidf.
    with TemporaryDirectory() as memoria:
        for nombre, clf in CLASIFICADORES.items():
            pipeline = construir_pipeline(clf, memoria=memoria)
            busquedas[nombre] = buscar_hiperparametros(pipeline, nombre, X_train, y_train)
        mejor = max(busquedas, key=lambda n: busquedas[n].best_score_)
        exps = (experimentos(busquedas[mejor].best_estimator_, df, X_train, y_train)
                if con_experimentos else experimentos_anteriores())

    modelos = {}
    for nombre, busqueda in busquedas.items():
        # Sin memoria antes de guardarlo: la carpeta temporal ya no existe.
        modelos[nombre] = busqueda.best_estimator_.set_params(memory=None)
        resultados[nombre] = {**evaluar(modelos[nombre], X_test, y_test), **resumen_cv(busqueda)}
    return modelos, resultados, exps, (df, X_train, X_test, y_test)


def elegir(resultados) -> str:
    """El modelo con mayor F1 macro de validación cruzada. El de test no participa:
    si se eligiera por test, el test dejaría de ser una medición independiente."""
    candidatos = [n for n in resultados if "f1_cv_media" in resultados[n]]
    return max(candidatos, key=lambda n: resultados[n]["f1_cv_media"])


def justificar(elegido, resultados) -> str:
    r = resultados[elegido]
    otros = [f"{n.replace('_', ' ')} ({resultados[n]['f1_cv_media']:.3f})"
             for n in resultados if n not in ("baseline", elegido)]
    return (f"Mayor F1 macro en validación cruzada: {r['f1_cv_media']:.3f} ± {r['f1_cv_std']:.3f} "
            f"frente a {', '.join(otros)}. En prueba obtiene {r['f1_macro']:.3f}, contra "
            f"{resultados['baseline']['f1_macro']:.3f} de la línea base.")


def errores_ejemplo(modelo, df, X_test, y_test, n=10) -> list[dict]:
    """Los errores más seguros del modelo, con tema, fuente y año para poder explicarlos."""
    filas = df.set_index("texto")  # los textos son únicos: cargar.py quita duplicados
    ejemplos = []
    for e in analizar_errores(modelo, X_test, y_test, n):
        texto = X_test[e.pop("indice")]
        fila = filas.loc[texto]
        ejemplos.append({"texto": texto[:400], **e, "tema": fila["tema"],
                         "fuente": fila["fuente"], "anio": int(fila["anio"])})
    return ejemplos


def guardar(modelos, resultados, exps, datos) -> str:
    """Guarda el modelo de producción y metricas.json (C6). Devuelve el nombre elegido."""
    df, X_train, X_test, y_test = datos
    elegido = elegir(resultados)
    modelo = modelos[elegido]
    RUTA_MODELO.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, RUTA_MODELO)

    prep = modelo.named_steps["prep"]
    tfidf = modelo.named_steps["tfidf"]
    metricas = {
        "modelo_produccion": elegido,
        "criterio": "mayor F1 macro en validación cruzada (5 particiones, solo train)",
        "justificacion": justificar(elegido, resultados),
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
        "experimentos": exps,
        "palabras_influyentes": palabras_influyentes(modelo),
        "errores_ejemplo": errores_ejemplo(modelo, df, X_test, y_test),
    }
    RUTA_METRICAS.write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    return elegido


if __name__ == "__main__":
    # python -m src.models.train --rapido   -> sin E1, E2 y E3 (para la defensa)
    rapido = "--rapido" in sys.argv
    if rapido:
        print("Modo rápido: sin E1, E2 ni E3; se conservan los experimentos anteriores.")
    modelos, resultados, exps, datos = entrenar(con_experimentos=not rapido)
    print(f"{'modelo':<22}{'f1_cv':>8}{'accuracy':>10}{'f1_test':>9}  hiperparámetros")
    for nombre, r in resultados.items():
        cv = f"{r['f1_cv_media']:.3f}" if "f1_cv_media" in r else "-"
        print(f"{nombre:<22}{cv:>8}{r['accuracy']:>10.3f}{r['f1_macro']:>9.3f}  "
              f"{r.get('mejores_hiperparametros', '')}")
    for nombre, comparacion in exps.items():
        print(f"{nombre}: " + ", ".join(f"{k} {v['f1_macro']:.3f}" for k, v in comparacion.items()))
    elegido = guardar(modelos, resultados, exps, datos)
    print(f"Modelo en producción: {elegido} -> {RUTA_MODELO}")
