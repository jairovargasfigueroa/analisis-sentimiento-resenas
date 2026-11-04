# 02 · Contratos compartidos

Este archivo define **cómo se comunican las partes**. Gracias a él cada integrante puede avanzar en paralelo usando datos de ejemplo (mocks), sin esperar a los demás.

> **Regla:** cambiar un contrato requiere un PR que modifique este archivo y que apruebe el otro integrante.

---

## C1 · Configuración (`params.yaml` + `src/config.py`), ya creados

`params.yaml` tiene todos los valores ajustables. `src/config.py` lo lee y expone:

```python
from src.config import (
    PARAMS,                 # dict completo de params.yaml (nlp, tfidf, experiments, ...)
    SEED,                   # 42
    ETIQUETAS,              # ["falsa", "verdadera"]  (orden fijo: índice 0 y 1)
    RUTA_DATOS_RAW, RUTA_DATOS_PROCESADOS, TEST_SIZE,
    RUTA_MODELO,            # models/modelo_produccion.joblib
    RUTA_METRICAS,          # models/metricas.json
    LONGITUD_MAX_TEXTO,     # 20000
    MIN_PALABRAS_TEXTO,     # 20
    MAX_TEXTOS_LOTE,        # 100
)
```

Las rutas son `pathlib.Path` absolutas, así que funcionan sin importar desde qué carpeta se ejecute. Todos los comandos se corren desde la **raíz del repo** con `python -m ...`.

## C2 · Dataset procesado (`data/processed/noticias.csv`), de Brayan

CSV UTF-8 con estas columnas exactas:

| columna | tipo | descripción |
|---|---|---|
| `texto` | str | `Headline + ". " + Text`, sin preprocesar (no vacío; si no hay titular, solo `Text`) |
| `etiqueta` | str | `falsa` o `verdadera` |
| `tema` | str | columna `Topic` del corpus (Política, COVID-19, …) |
| `fuente` | str | columna `Source`. Se guarda para la EDA, pero **no entra al modelo**: hay sitios satíricos que solo publican falsas |
| `anio` | int | 2018 (versión 1) o 2020/2021 (versión 2); permite el experimento E3 |

## C3 · Funciones de NLP (`src/nlp/`)

Todas son **funciones puras**: no tienen efectos secundarios y la misma entrada da la misma salida. Todas son de Brayan.

```python
# normalizacion.py
def normalizar(texto: str) -> str: ...
#   "¡¡URGENTE!! La OMS confirmó 3 casos 😱 https://x.com" -> "exclamacion urgente exclamacion la oms confirmó num casos emoji"
#   (conserva las tildes: spaCy las necesita para lematizar; reglas exactas en spec 20)
def quitar_tildes(texto: str) -> str: ...   # conserva la ñ

# tokenizacion.py
def tokenizar(texto_normalizado: str) -> list[str]: ...

# stopwords.py
def obtener_stopwords() -> set[str]: ...    # lista final ya ajustada (conserva negaciones)
def quitar_stopwords(tokens: list[str]) -> tuple[list[str], list[str]]: ...
#   devuelve (tokens_conservados, stopwords_eliminadas)

# raices.py
def stemizar(tokens: list[str]) -> list[str]: ...
def lematizar(tokens: list[str]) -> list[str]: ...
```

**Orden de tildes y lematización:** spaCy necesita las tildes («afirmó» → «afirmar»; sin tilde, «afirmo» puede quedar como primera persona). Por eso: normalizar **sin** quitar tildes → tokenizar → quitar stop words → lematizar o stemizar → **quitar tildes** del resultado. Se cubre con un test.

## C4 · Transformer (`src/nlp/preprocesador.py`), de Brayan

```python
class TextPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, modo: str = "lema", quitar_stop: bool = True): ...
    #   modo ∈ {"lema", "stem", "ninguno"}
    def fit(self, X, y=None): return self
    def transform(self, X: list[str]) -> list[str]: ...
    #   cada texto -> normalizar -> tokenizar -> quitar_stopwords -> stemizar/lematizar -> quitar_tildes -> " ".join(...)
```

- Debe poder **serializarse con joblib**: el modelo de spaCy se carga de forma perezosa y no se guarda dentro del pickle (se excluye en `__getstate__`).
- `TfidfVectorizer` recibe ese texto ya procesado.

## C5 · Explicación paso a paso (`src/nlp/explicar.py`), de Brayan

```python
def explicar_preprocesamiento(texto: str, modo: str = "lema") -> dict: ...
```

Devuelve exactamente:

```json
{
  "original": "¡Increíble! La OMS no aprobó la vacuna 😱 https://x.com",
  "normalizado": "exclamacion increíble exclamacion la oms no aprobó la vacuna emoji",
  "tokens": ["exclamacion", "increíble", "exclamacion", "la", "oms", "no", "aprobó", "la", "vacuna", "emoji"],
  "stopwords_eliminadas": ["la", "la"],
  "tokens_sin_stopwords": ["exclamacion", "increíble", "exclamacion", "oms", "no", "aprobó", "vacuna", "emoji"],
  "modo": "lema",
  "raices_o_lemas": ["exclamacion", "increible", "exclamacion", "oms", "no", "aprobar", "vacuna", "emoji"],
  "texto_final": "exclamacion increible exclamacion oms no aprobar vacuna emoji"
}
```

El campo `texto_final` debe ser **idéntico** a `TextPreprocessor(modo).transform([texto])[0]`. Esto se cubre con un test.

## C6 · Artefactos de entrenamiento: base de Brayan (PR 1.3), completo de Jairo (PR 2.2)

El PR 1.3 genera `metricas.json` con `modelo_produccion`, `dataset`, `preprocesamiento` y `modelos` (línea base y Regresión Logística). El PR 2.2 agrega Naive Bayes, los campos de validación cruzada, `experimentos` y `errores_ejemplo`.

- `models/modelo_produccion.joblib`: `Pipeline` completo (`prep` → `tfidf` → `clf`) ya entrenado.
- `models/metricas.json`:

```json
{
  "modelo_produccion": "regresion_logistica",
  "justificacion": "Mayor F1 macro en validación cruzada y probabilidades mejor calibradas.",
  "fecha_entrenamiento": "2026-11-01T18:30:00",
  "dataset": {
    "nombre": "The Spanish Fake News Corpus", "n_total": 1543, "n_train": 1234, "n_test": 309,
    "distribucion_clases": {"falsa": 766, "verdadera": 777}
  },
  "preprocesamiento": {"modo": "lema", "ngram_range": [1, 2], "min_df": 2, "max_df": 0.9, "max_features": 20000},
  "modelos": {
    "baseline": {
      "accuracy": 0.52, "precision_macro": 0.26, "recall_macro": 0.5, "f1_macro": 0.34,
      "matriz_confusion": [[0, 153], [0, 156]], "etiquetas": ["falsa", "verdadera"]
    },
    "regresion_logistica": {
      "accuracy": 0.82, "precision_macro": 0.82, "recall_macro": 0.82, "f1_macro": 0.82,
      "matriz_confusion": [[125, 28], [27, 129]], "etiquetas": ["falsa", "verdadera"],
      "mejores_hiperparametros": {"clf__C": 10.0}, "f1_cv_media": 0.81, "f1_cv_std": 0.02
    },
    "naive_bayes": { "…mismos campos…": "" }
  },
  "experimentos": {
    "stem_vs_lema": {"stem": {"f1_macro": 0.80}, "lema": {"f1_macro": 0.81}},
    "ngramas": {"(1,1)": {"f1_macro": 0.80}, "(1,2)": {"f1_macro": 0.82}},
    "temporal": {"2018 -> 2020-21": {"f1_macro": 0.70}}
  },
  "errores_ejemplo": [
    {"texto": "…", "real": "falsa", "predicho": "verdadera", "probabilidad": 0.71, "explicacion": "sátira con estilo periodístico"}
  ]
}
```

Los números son de ejemplo. Los nombres de los campos son el contrato. `experimentos.temporal` es opcional (E3).

## C7 · Predicción en Python (`src/models/predecir.py`), de Brayan

```python
def cargar_modelo(ruta: str = RUTA_MODELO) -> Pipeline: ...
def predecir(modelo: Pipeline, textos: list[str]) -> list[dict]: ...
#   [{"clase": "falsa", "probabilidad": 0.93,
#     "probabilidades": {"falsa": 0.93, "verdadera": 0.07}}, ...]
```

---

## C8 · API REST: `/health`, `/predict` y `/predict/lote` de Brayan; `/metrics` de Jairo

Base: `http://localhost:8000`. JSON en UTF-8.

### `GET /health`
```json
200 {"status": "ok", "modelo_cargado": true, "modelo": "regresion_logistica", "version": "1.0.0"}
```
Si el modelo no cargó: `503 {"status": "error", "modelo_cargado": false, ...}`.

### `POST /predict`
Request:
```json
{"texto": "El Ministerio de Salud informó este lunes que la campaña de vacunación..."}
```
Response `200`:
```json
{
  "clase": "verdadera",
  "probabilidad": 0.94,
  "probabilidades": {"falsa": 0.06, "verdadera": 0.94},
  "modelo": "regresion_logistica",
  "preprocesamiento": { "…objeto C5 completo…": "" }
}
```

### `POST /predict/lote`
Request: `{"textos": ["…", "…"]}` (1 a `MAX_TEXTOS_LOTE` elementos).
Response `200`: `{"resultados": [ {"texto": "…", "clase": "…", "probabilidad": 0.0, "probabilidades": {}} ], "resumen": {"falsa": 12, "verdadera": 8}}`

El frontend lee el archivo subido (`.txt` con una noticia por línea, o `.csv` con una columna `texto`) y envía la lista.

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
| 422 | `TEXTO_DEMASIADO_CORTO` | menos de `MIN_PALABRAS_TEXTO` palabras |
| 422 | `TEXTO_DEMASIADO_LARGO` | más de `LONGITUD_MAX_TEXTO` caracteres |
| 422 | `FORMATO_INVALIDO` | falta el campo, tipo incorrecto o JSON mal formado |
| 422 | `LOTE_INVALIDO` | lista vacía o con más de `MAX_TEXTOS_LOTE` elementos |
| 503 | `MODELO_NO_DISPONIBLE` | no existe o no cargó `modelo_produccion.joblib` |
