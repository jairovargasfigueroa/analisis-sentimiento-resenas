# 01 · Arquitectura

## Principio central (exigido por el docente)

> El preprocesamiento usado al entrenar debe ser **exactamente el mismo** que se usa al predecir desde la API.

Por eso el preprocesamiento, TF-IDF y el modelo se empaquetan en **un solo `sklearn.pipeline.Pipeline`**, se serializan con `joblib`, y el backend solo lo **carga**.

```
ENTRENAMIENTO  ·  python -m src.models.train
data/raw/*.xlsx ─► carga y unificación ─► split estratificado (SEED=42)
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
| Lenguaje | Python 3.12 | Es el estándar del ecosistema de ML; todas las librerías lo soportan. |
| Configuración | `params.yaml` + PyYAML | Una sola fuente de parámetros: cambiar un valor y reentrenar, sin tocar código (idea tomada del ejemplo del docente). |
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
│   ├── raw/                 # corpus original (.xlsx) y su README                → Brayan
│   └── processed/           # noticias.csv (C2)                                  → Brayan
├── notebooks/
│   └── 01_eda.ipynb         # EDA, experimentos y análisis de errores            → Jairo
├── src/
│   ├── config.py            # lee params.yaml: SEED, rutas, etiquetas            → Brayan
│   ├── data/
│   │   └── cargar.py        # carga y unificación del corpus                     → Brayan
│   ├── nlp/
│   │   ├── normalizacion.py # normalizar(), quitar_tildes()                      → Brayan
│   │   ├── tokenizacion.py  # tokenizar()                                        → Brayan
│   │   ├── stopwords.py     # obtener_stopwords(), quitar_stopwords()            → Brayan
│   │   ├── raices.py        # stemizar(), lematizar()                            → Brayan
│   │   ├── preprocesador.py # TextPreprocessor (transformer de sklearn)          → Brayan
│   │   └── explicar.py      # explicar_preprocesamiento()                        → Brayan
│   └── models/
│       ├── train.py         # comando único de entrenamiento                     → Brayan (base), Jairo (comparación)
│       ├── experimentos.py  # E1 stem vs lema, E2 n-gramas, E3 temporal          → Jairo
│       ├── evaluacion.py    # métricas, baseline, matriz de confusión, errores   → Jairo
│       └── predecir.py      # cargar_modelo(), predecir()                        → Brayan
├── models/                  # artefactos generados: .joblib y metricas.json
├── api/
│   ├── main.py              # app FastAPI (/health, /predict, /predict/lote)     → Brayan; /metrics → Jairo
│   └── esquemas.py          # modelos Pydantic de request/response               → Brayan
├── frontend/                # React + Vite: Analizar y Lote → Brayan; Métricas → Jairo
├── tests/                   # test_datos, test_nlp, test_modelo, test_api        → el dueño de cada parte
├── docs/
│   ├── informe.md           # informe técnico                                    → los dos (cada uno su sección)
│   ├── api.md               # endpoints con ejemplos curl                        → Brayan
│   ├── modificaciones_en_vivo.md  # recetas probadas para la defensa             → los dos
│   └── enunciado-proyecto-integrador.pdf
├── specs/                   # estas especificaciones
├── params.yaml              # todos los parámetros ajustables                    → por sección (ver el archivo)
├── requirements.txt         # dependencias con versión fija                      → compartido, cambios por PR
├── README.md                                                                     → Brayan
└── CONTRIBUCIONES.md                                                             → los dos (cada uno su sección)
```

## Reproducibilidad

- `SEED` (definido en `params.yaml`, expuesto por `src/config.py`) se usa en el split, en `GridSearchCV`/`StratifiedKFold` y en cualquier muestreo.
- `requirements.txt` con versiones **fijas** (`paquete==x.y.z`), ya probadas con Python 3.12. Para agregar una librería: instalarla, fijar la versión y abrir un PR.
- `python -m src.models.train` va de `data/raw` a `models/` **sin pasos manuales**.
- Los artefactos de `models/` se suben al repo en la entrega final (son pequeños) para que `git clone` + levantar funcione aunque no se reentrene.

## Puertos y ejecución local

| Servicio | Comando | URL |
|---|---|---|
| API | `uvicorn api.main:app --reload --port 8000` | http://localhost:8000 (docs en `/docs`) |
| Frontend | `cd frontend && npm run dev` | http://localhost:5173 |

El frontend lee la URL de la API desde `VITE_API_URL` (por defecto `http://localhost:8000`). La API habilita CORS para `http://localhost:5173`.
