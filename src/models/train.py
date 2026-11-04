"""Entrenamiento: python -m src.models.train (spec 30, contrato C6).

Va de data/raw a models/ sin pasos manuales: carga, split, entrena, evalúa y guarda.
"""

from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import ETIQUETAS, PARAMS, SEED, TEST_SIZE
from src.data.cargar import cargar_procesado
from src.nlp.preprocesador import TextPreprocessor

# Nombre (el de params.yaml -> experiments.models) -> clasificador.
# Para comparar otro modelo basta agregarlo aquí y su grilla en params.yaml.
CLASIFICADORES = {
    "regresion_logistica": LogisticRegression(max_iter=1000, random_state=SEED),
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


def evaluar(modelo, X, y) -> dict:
    """Métricas de C6 sobre (X, y). Macro: las dos clases pesan igual."""
    pred = modelo.predict(X)
    p, r, f1, _ = precision_recall_fscore_support(y, pred, average="macro", zero_division=0)
    return {
        "accuracy": round(accuracy_score(y, pred), 4),
        "precision_macro": round(p, 4), "recall_macro": round(r, 4), "f1_macro": round(f1, 4),
        "matriz_confusion": confusion_matrix(y, pred, labels=ETIQUETAS).tolist(),
        "etiquetas": ETIQUETAS,
    }


def entrenar():
    """Entrena la línea base y cada clasificador; devuelve (modelos, resultados, datos)."""
    df = cargar_procesado()
    X_train, X_test, y_train, y_test = dividir(df)

    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    resultados = {"baseline": evaluar(baseline, X_test, y_test)}
    modelos = {}
    for nombre, clf in CLASIFICADORES.items():
        modelos[nombre] = construir_pipeline(clf).fit(X_train, y_train)
        resultados[nombre] = evaluar(modelos[nombre], X_test, y_test)
    return modelos, resultados, (df, X_train, X_test)


if __name__ == "__main__":
    modelos, resultados, datos = entrenar()
    print(f"{'modelo':<22}{'accuracy':>10}{'f1_macro':>10}")
    for nombre, r in resultados.items():
        print(f"{nombre:<22}{r['accuracy']:>10.3f}{r['f1_macro']:>10.3f}")
