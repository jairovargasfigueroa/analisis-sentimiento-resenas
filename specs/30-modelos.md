# 30 · Modelos de machine learning y pipeline reproducible

- **Enunciado:** secciones 5.3 y 5.4.
- Interfaces: C4 (entrada), C6 y C7 (salida).

| Parte | Responsable | Rama sugerida | Archivos |
|---|---|---|---|
| A · Entrenamiento, ajuste y experimentos | Integrante 2 | `feat/modelos-train`, `exp/stem-vs-lema`, `exp/ngramas` | `src/models/train.py`, `src/models/experimentos.py`, `notebooks/02_experimentos.ipynb`, `requirements.txt` |
| B · Evaluación, baseline y predicción | Integrante 3 | `feat/modelos-evaluacion` | `src/models/evaluacion.py`, `src/models/predecir.py`, `tests/test_modelo.py` |

---

## Parte A · Integrante 2

### Comando único

```bash
python -m src.models.train
```

Hace todo, sin pasos manuales:

1. Carga `data/processed/resenas.csv` (o lo genera llamando a `src/data/cargar.py`).
2. Split estratificado 80/20 con `SEED`.
3. Ejecuta los **experimentos E1 y E2**, solo con train y validación cruzada.
4. Ajusta los **dos modelos** con `GridSearchCV(cv=StratifiedKFold(5, shuffle=True, random_state=SEED), scoring="f1_macro")`.
5. Evalúa en test con `evaluacion.py` (Parte B), incluido el baseline.
6. Elige el modelo de producción (el de **mayor F1 macro en CV**; el test solo se reporta).
7. Guarda `models/modelo_produccion.joblib` y `models/metricas.json` (C6).
8. Imprime en consola una tabla resumen.

### Modelos y grillas

| Modelo | Pipeline | Grilla mínima |
|---|---|---|
| Regresión Logística | `prep → tfidf → LogisticRegression(max_iter=1000, random_state=SEED)` | `clf__C: [0.1, 1, 10]`, `clf__class_weight: [None, "balanced"]` |
| Naive Bayes | `prep → tfidf → MultinomialNB()` | `clf__alpha: [0.1, 0.5, 1.0]` |

### Experimentos (se reportan en `metricas.json` → `experimentos` y en el notebook)

- **E1 · Stemming vs lematización:** el mismo modelo y la misma configuración, cambiando solo `prep__modo`. Se compara F1 macro en CV y se **elige uno**.
- **E2 · Unigramas vs unigramas + bigramas:** `tfidf__ngram_range` en `(1,1)` vs `(1,2)`. Mostrar un bigrama que ayude (por ejemplo, `no_gustar`).

### Justificación (para el informe y la defensa)

- Por qué estos dos modelos sirven para texto con TF-IDF: datos dispersos y de alta dimensión, ambos son modelos lineales o probabilísticos rápidos.
- **Cómo funciona cada uno internamente.** Todos los integrantes deben poder explicarlo:
  - **Regresión Logística:** combinación lineal de los pesos TF-IDF → sigmoide → probabilidad; se entrena minimizando log-loss; `C` es la inversa de la regularización.
  - **Naive Bayes:** teorema de Bayes con independencia entre palabras; `alpha` es el suavizado de Laplace.

### Reproducibilidad
- [ ] `requirements.txt` con versiones fijas (`==`).
- [ ] Dos ejecuciones seguidas de `train.py` dan **las mismas métricas**.

---

## Parte B · Integrante 3

### `src/models/evaluacion.py`

```python
def evaluar(modelo, X_test, y_test) -> dict: ...
#   accuracy, precision_macro, recall_macro, f1_macro, matriz_confusion, etiquetas (C6)
def evaluar_baseline(X_train, y_train, X_test, y_test) -> dict: ...
#   DummyClassifier(strategy="most_frequent")
def analizar_errores(modelo, X_test, y_test, n=10) -> list[dict]: ...
#   los n errores con mayor probabilidad equivocada (los más "seguros" pero incorrectos)
```

- El **baseline** demuestra que el modelo aporta valor, como pide el enunciado.
- **Análisis de errores:** en el informe se explica **por qué** falla en cada uno de al menos 5 ejemplos (ironía, negación lejana, reseña mixta, jerga, error de etiqueta).
- **Palabras más influyentes** (solo Regresión Logística): las 15 con coeficiente más positivo y las 15 con coeficiente más negativo. Se agrega a `metricas.json` como `palabras_influyentes` si el tiempo alcanza.

### `src/models/predecir.py` (C7)

La usa la API. Carga el `.joblib` y devuelve clase, probabilidad y probabilidades con las etiquetas de `config.ETIQUETAS`.

### Criterios de aceptación (B)
- [ ] `tests/test_modelo.py`: el modelo carga, predice una reseña obviamente positiva como `positivo` y otra obviamente negativa como `negativo`, y las probabilidades suman 1.
- [ ] La matriz de confusión se interpreta en el informe (qué tipo de error es más frecuente).

---

## Criterios de aceptación globales
- [ ] `python -m src.models.train` desde un clon limpio genera ambos artefactos.
- [ ] `metricas.json` cumple C6 e incluye baseline, ambos modelos, E1, E2 y ejemplos de error.
- [ ] El modelo de producción supera claramente al baseline.
