# 01 · Arquitectura

## Principio central (exigido por el docente)

> El preprocesamiento usado al entrenar debe ser **exactamente el mismo** que se usa al predecir desde la API.

Por eso el preprocesamiento, TF-IDF y el modelo se empaquetan en **un solo `sklearn.pipeline.Pipeline`**, se serializan con `joblib`, y el backend solo lo **carga**.

```
ENTRENAMIENTO  ·  python -m src.models.train
data/raw/*.csv ─► carga y limpieza ─► split estratificado (SEED=42)
                                         │
                       Pipeline([ ("prep",  TextPreprocessor),   ◄ src/nlp
                                  ("tfidf", TfidfVectorizer),
                                  ("clf",   LogisticRegression | MultinomialNB) ])
                                         │  GridSearchCV (solo con train)
                                         ▼
                 models/modelo_produccion.joblib  +  models/metricas.json

USO  ·  cada consulta
frontend (React) ──HTTP/JSON──► api (FastAPI) ──joblib.load──► predict_proba ──► respuesta
```

## Stack y justificación

| Capa | Tecnología | Por qué |
|---|---|---|
| Lenguaje | Python 3.11 | Es el estándar del ecosistema de ML; todas las librerías lo soportan. |
| NLP | `re`/`unicodedata`, NLTK (stop words y `SnowballStemmer("spanish")`), spaCy `es_core_news_sm` (lemas) | Cubren normalización, stemming y lematización en español. |
| ML | scikit-learn | Trae TF-IDF, ambos modelos, `Pipeline`, `GridSearchCV` y las métricas. |
| Serialización | joblib | Es la forma recomendada por scikit-learn para guardar pipelines. |
| Backend | FastAPI + Uvicorn | Valida entradas con Pydantic y genera documentación automática en `/docs`. |
| Tests | pytest + `fastapi.testclient` | Son simples y estándar. |
| Frontend | React + Vite | Es ligero y rápido de levantar; se trabaja por componentes. |
| Notebooks | Jupyter | Para la EDA y los experimentos que se muestran en la defensa. |

## Estructura de carpetas y responsables

```
analisis-sentimiento-resenas/
├── data/
│   ├── raw/                 # dataset original (o script de descarga si pesa)  → P1
│   └── processed/           # dataset limpio y etiquetado                        → P1
├── notebooks/
│   ├── 01_eda.ipynb                                                              → P1
│   └── 02_experimentos.ipynb                                                     → P2
├── src/
│   ├── config.py            # SEED, rutas, nombres de etiquetas                  → P1
│   ├── data/
│   │   └── cargar.py        # carga, limpieza y etiquetado del dataset           → P1
│   ├── nlp/
│   │   ├── normalizacion.py # normalizar()                                       → P1
│   │   ├── tokenizacion.py  # tokenizar()                                        → P1
│   │   ├── stopwords.py     # obtener_stopwords(), quitar_stopwords()            → P1
│   │   ├── raices.py        # stemizar(), lematizar()                            → P2
│   │   ├── preprocesador.py # TextPreprocessor (transformer de sklearn)          → P1
│   │   └── explicar.py      # explicar_preprocesamiento()                        → P4
│   └── models/
│       ├── train.py         # comando único de entrenamiento                     → P2
│       ├── experimentos.py  # stem vs lema, uni vs uni+bi                        → P2
│       ├── evaluacion.py    # métricas, baseline, matriz de confusión, errores   → P3
│       └── predecir.py      # cargar_modelo(), predecir()                        → P3
├── models/                  # artefactos generados: .joblib y metricas.json
├── api/
│   ├── main.py              # app FastAPI                                        → P3
│   └── esquemas.py          # modelos Pydantic de request/response               → P3
├── frontend/                # app React + Vite                                   → P4
├── tests/                   # test_nlp.py (P1/P2), test_api.py (P3), test_modelo.py (P3)
├── docs/
│   ├── informe.md           # informe técnico                                    → todos
│   └── enunciado-proyecto-integrador.pdf
├── specs/                   # estas especificaciones
├── requirements.txt         # dependencias con versión fija                      → P2 (los demás agregan vía PR)
├── README.md                                                                     → todos
└── CONTRIBUCIONES.md                                                             → todos
```

## Reproducibilidad

- `SEED = 42` en `src/config.py`, usado en el split, en `GridSearchCV`/`StratifiedKFold` y en cualquier muestreo.
- `requirements.txt` con versiones **fijas** (`paquete==x.y.z`), generadas con `pip freeze` filtrado.
- `python -m src.models.train` va de `data/raw` a `models/` **sin pasos manuales**.
- Los artefactos de `models/` se suben al repo en la entrega final (son pequeños) para que `git clone` + levantar funcione aunque no se reentrene.

## Puertos y ejecución local

| Servicio | Comando | URL |
|---|---|---|
| API | `uvicorn api.main:app --reload --port 8000` | http://localhost:8000 (docs en `/docs`) |
| Frontend | `cd frontend && npm run dev` | http://localhost:5173 |

El frontend lee la URL de la API desde `VITE_API_URL` (por defecto `http://localhost:8000`). La API habilita CORS para `http://localhost:5173`.
