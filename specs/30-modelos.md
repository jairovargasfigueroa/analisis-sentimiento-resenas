# 30 · Modelos de machine learning y pipeline reproducible

- **Enunciado:** secciones 5.3 y 5.4.
- Interfaces: C4 (entrada), C6 y C7 (salida).

| Parte | Responsable | Rama | Archivos |
|---|---|---|---|
| Base · `train.py` mínimo (Regresión Logística + línea base) y predicción | Brayan (PR 1.3) | `feat/modelo-base` | `src/models/train.py`, `src/models/predecir.py`, `tests/test_modelo.py` |
| Comparación · Naive Bayes, GridSearchCV, experimentos, evaluación y errores | Jairo (PR 2.2) | `exp/experimentos` | `src/models/evaluacion.py`, `src/models/experimentos.py`, notebook de EDA y experimentos, secciones `tfidf` y `experiments` de `params.yaml` |

**Clave:** `train.py` lee los modelos y sus grillas de `params.yaml → experiments.models` en un diccionario. Así Jairo agrega Naive Bayes y los experimentos sin reescribir `train.py`.

---

## Entrenamiento (base: Brayan · comparación: Jairo)

### Comando único

```bash
python -m src.models.train
```

Hace todo, sin pasos manuales:

1. Carga `data/processed/noticias.csv` (o lo genera llamando a `src/data/cargar.py`).
2. Split estratificado 80/20 con `SEED`.
3. Ejecuta los **experimentos E1 y E2**, solo con train y validación cruzada.
4. Ajusta los **dos modelos** con `GridSearchCV(cv=StratifiedKFold(5, shuffle=True, random_state=SEED), scoring="f1_macro")`.
5. Evalúa en test, incluida la línea base (en el PR 1.3 con `classification_report`; desde el 2.2 con `evaluacion.py`).
6. Elige el modelo de producción (el de **mayor F1 macro en CV**; el test solo se reporta).
7. Guarda `models/modelo_produccion.joblib` y `models/metricas.json` (C6).
8. Imprime en consola una tabla resumen.

### Modelos y grillas

Las grillas se leen de `params.yaml → experiments.models`. **No se escriben fijas en el código**, para que "cambiar un hiperparámetro y reentrenar" sea editar una línea. Valores iniciales:

| Modelo | Pipeline | Grilla mínima |
|---|---|---|
| Regresión Logística | `prep → tfidf → LogisticRegression(max_iter=1000, random_state=SEED)` | `clf__C: [0.1, 1, 10, 30]` |
| Naive Bayes | `prep → tfidf → MultinomialNB()` | `clf__alpha: [0.05, 0.1, 0.5, 1.0]` |

No hace falta `class_weight`: las clases están balanceadas (777 / 766, dato de la EDA).

**Por qué estos dos:** TF-IDF genera vectores dispersos de miles de dimensiones con pocos ejemplos (unas 1.230 noticias de entrenamiento). Los modelos lineales y probabilísticos funcionan bien ahí y son fáciles de explicar. Random Forest o XGBoost sobreajustarían con tan pocos datos.

**Prueba rápida orientativa** (preprocesamiento mínimo, LR con C=10 y NB con alpha=0,1; no son los números finales):

| Modelo | N-gramas | F1 macro, split 80/20 | F1 macro, 2018 → 2020–21 |
|---|---|---|---|
| Regresión Logística | (1,2) | 0,825 | 0,702 |
| Regresión Logística | (1,1) | 0,803 | 0,702 |
| Naive Bayes | (1,2) | 0,746 | 0,580 |
| Naive Bayes | (1,1) | 0,715 | 0,570 |
| Línea base | — | 0,335 | 0,333 |

### Experimentos (se reportan en `metricas.json` → `experimentos` y en el notebook)

- **E1 · Stemming vs lematización:** el mismo modelo y la misma configuración, cambiando solo `prep__modo`. Se compara F1 macro en CV y se **elige uno**.
- **E2 · Unigramas vs unigramas + bigramas:** `tfidf__ngram_range` en `(1,1)` vs `(1,2)`. Mostrar un bigrama que ayude (por ejemplo, `no confirmar`).
- **E3 · Generalización en el tiempo (opcional):** entrenar con 2018 y probar con 2020–21. Se espera una caída (el modelo aprende temas y estilos de 2018): se muestra como hallazgo, no se esconde. Va en `metricas.json → experimentos.temporal`.
- **E4 · Stop words completa vs ajustada (opcional, Jairo):** la lista de NLTK tal cual contra la ajustada con la EDA.

### Justificación (para el informe y la defensa)

- **Cómo funciona cada uno internamente.** Los dos integrantes deben poder explicarlo:
  - **Regresión Logística:** combinación lineal de los pesos TF-IDF → sigmoide → probabilidad; se entrena minimizando log-loss; `C` es la inversa de la regularización.
  - **Naive Bayes:** teorema de Bayes con independencia entre palabras; `alpha` es el suavizado de Laplace.

### Reproducibilidad
- [ ] Si se agrega una librería, se fija su versión en `requirements.txt` (`==`).
- [ ] Dos ejecuciones seguidas de `train.py` dan **las mismas métricas**.
- [ ] La decisión de qué modelo va a producción se toma con el **F1 macro de validación cruzada**, no con el de prueba: el de prueba solo se reporta.

---

## Evaluación y predicción

### `src/models/evaluacion.py` (Jairo)

```python
def evaluar(modelo, X_test, y_test) -> dict: ...
#   accuracy, precision_macro, recall_macro, f1_macro, matriz_confusion, etiquetas (C6)
def evaluar_baseline(X_train, y_train, X_test, y_test) -> dict: ...
#   DummyClassifier(strategy="most_frequent")
def analizar_errores(modelo, X_test, y_test, n=10) -> list[dict]: ...
#   los n errores con mayor probabilidad equivocada (los más "seguros" pero incorrectos)
```

- El **baseline** demuestra que el modelo aporta valor, como pide el enunciado.
- **Análisis de errores:** en el informe se explica **por qué** falla en cada uno de al menos 5 ejemplos: sátira que imita el estilo periodístico, noticias verdaderas con tono alarmista, falsas escritas con estilo formal, posts cortos de redes y temas nuevos (COVID) que no estaban en el entrenamiento.
- **Palabras más influyentes** (solo Regresión Logística): las 15 con coeficiente más positivo y las 15 con coeficiente más negativo. Se agrega a `metricas.json` como `palabras_influyentes` si el tiempo alcanza.

### `src/models/predecir.py` (C7, Brayan)

La usa la API. Carga el `.joblib` y devuelve clase, probabilidad y probabilidades con las etiquetas de `config.ETIQUETAS`.

### Criterios de aceptación
- [ ] `tests/test_modelo.py`: el modelo carga, predice una noticia claramente falsa (satírica, sensacionalista) como `falsa` y una de agencia claramente verdadera como `verdadera`, y las probabilidades suman 1.
- [ ] La matriz de confusión se interpreta en el informe (qué tipo de error es más frecuente).

---

## Criterios de aceptación globales
- [ ] `python -m src.models.train` desde un clon limpio genera ambos artefactos.
- [ ] `metricas.json` cumple C6 e incluye baseline, ambos modelos, E1, E2 y ejemplos de error (E3 si se hizo).
- [ ] El modelo de producción supera claramente al baseline.
