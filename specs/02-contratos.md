# 02 · Contratos compartidos

Este archivo define **cómo se comunican las partes**. Gracias a él cada integrante puede avanzar en paralelo usando datos de ejemplo (mocks), sin esperar a los demás.

> **Regla:** cambiar un contrato requiere un PR que modifique este archivo y que aprueben **todos** los afectados.

---

## C1 · Configuración (`src/config.py`), de P1

```python
SEED = 42
ETIQUETAS = ["negativo", "positivo"]        # orden fijo: índice 0 y 1
RUTA_DATOS_RAW = "data/raw/"
RUTA_DATOS_PROCESADOS = "data/processed/resenas.csv"
RUTA_MODELO = "models/modelo_produccion.joblib"
RUTA_METRICAS = "models/metricas.json"
LONGITUD_MAX_TEXTO = 5000                   # caracteres
MAX_TEXTOS_LOTE = 100
```

## C2 · Dataset procesado (`data/processed/resenas.csv`), de P1

CSV UTF-8 con estas columnas exactas:

| columna | tipo | descripción |
|---|---|---|
| `texto` | str | reseña original sin preprocesar (no vacía) |
| `etiqueta` | str | `positivo` o `negativo` |
| `estrellas` | int | puntuación original 1–5, si el dataset la trae (opcional) |

## C3 · Funciones de NLP (`src/nlp/`)

Todas son **funciones puras**: no tienen efectos secundarios y la misma entrada da la misma salida.

```python
# normalizacion.py  (P1)
def normalizar(texto: str) -> str: ...
#   "¡¡Me ENCANTÓ!! 😍 www.x.com" -> "me encanto" (reglas exactas en spec 20)

# tokenizacion.py   (P1)
def tokenizar(texto_normalizado: str) -> list[str]: ...

# stopwords.py      (P1)
def obtener_stopwords() -> set[str]: ...    # lista final ya ajustada (conserva negaciones)
def quitar_stopwords(tokens: list[str]) -> tuple[list[str], list[str]]: ...
#   devuelve (tokens_conservados, stopwords_eliminadas)

# raices.py         (P2)
def stemizar(tokens: list[str]) -> list[str]: ...
def lematizar(tokens: list[str]) -> list[str]: ...
```

## C4 · Transformer (`src/nlp/preprocesador.py`), de P1

```python
class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, modo: str = "lema", quitar_stop: bool = True): ...
    #   modo ∈ {"lema", "stem", "ninguno"}
    def fit(self, X, y=None): return self
    def transform(self, X: list[str]) -> list[str]: ...
    #   cada texto -> normalizar -> tokenizar -> quitar_stopwords -> stemizar/lematizar -> " ".join(...)
```

- Debe poder **serializarse con joblib**: el modelo de spaCy se carga de forma perezosa y no se guarda dentro del pickle (se excluye en `__getstate__`).
- `TfidfVectorizer` recibe ese texto ya procesado.

## C5 · Explicación paso a paso (`src/nlp/explicar.py`), de P4

```python
def explicar_preprocesamiento(texto: str, modo: str = "lema") -> dict: ...
```

Devuelve exactamente:

```json
{
  "original": "¡No me gustó NADA la comida! 😡 https://x.com",
  "normalizado": "no me gusto nada la comida",
  "tokens": ["no", "me", "gusto", "nada", "la", "comida"],
  "stopwords_eliminadas": ["me", "la"],
  "tokens_sin_stopwords": ["no", "gusto", "nada", "comida"],
  "modo": "lema",
  "raices_o_lemas": ["no", "gustar", "nada", "comida"],
  "texto_final": "no gustar nada comida"
}
```

El campo `texto_final` debe ser **idéntico** a `TextPreprocessor(modo).transform([texto])[0]`. Esto se cubre con un test.

## C6 · Artefactos de entrenamiento, de P2 (estructura de métricas: P3)

- `models/modelo_produccion.joblib`: `Pipeline` completo (`prep` → `tfidf` → `clf`) ya entrenado.
- `models/metricas.json`:

```json
{
  "modelo_produccion": "regresion_logistica",
  "justificacion": "Mayor F1 macro en validación cruzada y probabilidades mejor calibradas.",
  "fecha_entrenamiento": "2026-11-01T18:30:00",
  "dataset": {
    "nombre": "…", "n_total": 5000, "n_train": 4000, "n_test": 1000,
    "distribucion_clases": {"negativo": 2400, "positivo": 2600}
  },
  "preprocesamiento": {"modo": "lema", "ngram_range": [1, 2], "min_df": 2, "max_df": 0.9, "max_features": 20000},
  "modelos": {
    "baseline": {
      "accuracy": 0.52, "precision_macro": 0.26, "recall_macro": 0.5, "f1_macro": 0.34,
      "matriz_confusion": [[0, 480], [0, 520]], "etiquetas": ["negativo", "positivo"]
    },
    "regresion_logistica": {
      "accuracy": 0.89, "precision_macro": 0.89, "recall_macro": 0.89, "f1_macro": 0.89,
      "matriz_confusion": [[420, 60], [50, 470]], "etiquetas": ["negativo", "positivo"],
      "mejores_hiperparametros": {"clf__C": 1.0}, "f1_cv_media": 0.88, "f1_cv_std": 0.01
    },
    "naive_bayes": { "…mismos campos…": "" }
  },
  "experimentos": {
    "stem_vs_lema": {"stem": {"f1_macro": 0.87}, "lema": {"f1_macro": 0.88}},
    "ngramas": {"(1,1)": {"f1_macro": 0.86}, "(1,2)": {"f1_macro": 0.88}}
  },
  "errores_ejemplo": [
    {"texto": "…", "real": "negativo", "predicho": "positivo", "probabilidad": 0.71, "explicacion": "ironía"}
  ]
}
```

Los números son de ejemplo. Los nombres de los campos son el contrato.

## C7 · Predicción en Python (`src/models/predecir.py`), de P3

```python
def cargar_modelo(ruta: str = RUTA_MODELO) -> Pipeline: ...
def predecir(modelo: Pipeline, textos: list[str]) -> list[dict]: ...
#   [{"clase": "positivo", "probabilidad": 0.93,
#     "probabilidades": {"negativo": 0.07, "positivo": 0.93}}, ...]
```

---

## C8 · API REST, de P3 (consume P4)

Base: `http://localhost:8000`. JSON en UTF-8.

### `GET /health`
```json
200 {"status": "ok", "modelo_cargado": true, "modelo": "regresion_logistica", "version": "1.0.0"}
```
Si el modelo no cargó: `503 {"status": "error", "modelo_cargado": false, ...}`.

### `POST /predict`
Request:
```json
{"texto": "La comida estaba deliciosa y la atención excelente"}
```
Response `200`:
```json
{
  "clase": "positivo",
  "probabilidad": 0.94,
  "probabilidades": {"negativo": 0.06, "positivo": 0.94},
  "modelo": "regresion_logistica",
  "preprocesamiento": { "…objeto C5 completo…": "" }
}
```

### `POST /predict/lote`
Request: `{"textos": ["…", "…"]}` (1 a `MAX_TEXTOS_LOTE` elementos).
Response `200`: `{"resultados": [ {"texto": "…", "clase": "…", "probabilidad": 0.0, "probabilidades": {}} ], "resumen": {"positivo": 12, "negativo": 8}}`

El frontend lee el archivo subido (`.txt` con una reseña por línea, o `.csv` con una columna `texto`) y envía la lista.

### `GET /metrics`
Response `200`: el contenido de `models/metricas.json` (C6) tal cual.

### Errores (todos los endpoints)
Formato único:
```json
{"error": {"codigo": "TEXTO_VACIO", "mensaje": "El texto no puede estar vacío."}}
```

| HTTP | código | cuándo |
|---|---|---|
| 422 | `TEXTO_VACIO` | `texto` vacío o solo espacios |
| 422 | `TEXTO_DEMASIADO_LARGO` | más de `LONGITUD_MAX_TEXTO` caracteres |
| 422 | `FORMATO_INVALIDO` | falta el campo, tipo incorrecto o JSON mal formado |
| 422 | `LOTE_INVALIDO` | lista vacía o con más de `MAX_TEXTOS_LOTE` elementos |
| 503 | `MODELO_NO_DISPONIBLE` | no existe o no cargó `modelo_produccion.joblib` |
