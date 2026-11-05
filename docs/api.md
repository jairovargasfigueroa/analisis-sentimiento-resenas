# API REST

Base: `http://localhost:8000`. JSON en UTF-8. La documentación interactiva (Swagger) está en <http://localhost:8000/docs>.

```bash
uvicorn api.main:app --reload --port 8000
```

El modelo se carga una sola vez al iniciar, desde `models/modelo_produccion.joblib`. Si no existe, la API arranca igual: `/health` responde 503 y `/predict` devuelve `MODELO_NO_DISPONIBLE`. Se genera con `python -m src.models.train`.

## `GET /health`

Estado del servicio y del modelo.

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "modelo_cargado": true, "modelo": "regresion_logistica", "version": "1.0.0"}
```

## `POST /predict`

Clasifica una noticia y devuelve el preprocesamiento paso a paso.

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texto": "El Ministerio de Salud informó este lunes que la campaña de vacunación contra la influenza comenzará la próxima semana en todos los centros de salud del país."}'
```

```json
{
  "clase": "verdadera",
  "probabilidad": 0.5125,
  "probabilidades": {"falsa": 0.4875, "verdadera": 0.5125},
  "modelo": "regresion_logistica",
  "preprocesamiento": {
    "original": "El Ministerio de Salud informó …",
    "normalizado": "el ministerio de salud informó …",
    "tokens": ["el", "ministerio", "de", "salud", "informó", "…"],
    "stopwords_eliminadas": ["el", "de", "…"],
    "tokens_sin_stopwords": ["ministerio", "salud", "informó", "…"],
    "modo": "lema",
    "raices_o_lemas": ["ministerio", "salud", "informar", "…"],
    "texto_final": "ministerio salud informar …"
  }
}
```

## `POST /predict/lote`

Clasifica de 1 a `api.max_textos_lote` (100) noticias en una sola llamada. No devuelve el paso a paso: para eso está `/predict`. La pestaña **Lote** del frontend lo usa con un `.csv` (columna `texto`) o un `.txt` (una noticia por línea); hay un ejemplo en `frontend/public/ejemplo_lote.csv`.

```bash
curl -X POST http://localhost:8000/predict/lote \
  -H "Content-Type: application/json" \
  -d '{"textos": ["Primera noticia completa, con al menos veinte palabras…", "Segunda noticia completa…"]}'
```

```json
{
  "resultados": [
    {"texto": "Primera noticia…", "clase": "falsa", "probabilidad": 0.72,
     "probabilidades": {"falsa": 0.72, "verdadera": 0.28}},
    {"texto": "Segunda noticia…", "clase": "verdadera", "probabilidad": 0.61,
     "probabilidades": {"falsa": 0.39, "verdadera": 0.61}}
  ],
  "resumen": {"falsa": 1, "verdadera": 1}
}
```

Si el lote está vacío, tiene más de 100 noticias o **alguna** noticia no es válida, se rechaza entero con `LOTE_INVALIDO`, y el mensaje dice cuál falla: `"Noticia 2: La noticia debe tener al menos 20 palabras."`.

## `GET /metrics`

Devuelve `models/metricas.json` tal cual (contrato C6): el modelo en producción con su criterio y justificación, las métricas de la línea base y de cada modelo (F1 de validación cruzada, métricas de prueba, matriz de confusión, métricas por clase, hiperparámetros), los experimentos E1, E2 y E3, las palabras más influyentes y los errores con mayor confianza. La pestaña **Métricas** lo muestra.

```bash
curl http://localhost:8000/metrics
```

```json
{
  "modelo_produccion": "regresion_logistica",
  "criterio": "mayor F1 macro en validación cruzada (5 particiones, solo train)",
  "justificacion": "Mayor F1 macro en validación cruzada: 0.766 ± 0.006 frente a naive bayes (0.695). …",
  "modelos": {"baseline": {"…": ""}, "regresion_logistica": {"…": ""}, "naive_bayes": {"…": ""}},
  "experimentos": {"stem_vs_lema": {"…": ""}, "ngramas": {"…": ""}, "temporal": {"…": ""}},
  "palabras_influyentes": {"falsa": ["…"], "verdadera": ["…"]},
  "errores_ejemplo": ["…"]
}
```

Se carga al iniciar, junto con el modelo: así describe siempre el modelo que está sirviendo `/predict`. Si se reentrena, hay que reiniciar uvicorn. Sin métricas responde 503 `MODELO_NO_DISPONIBLE`.

## Errores

Todos tienen el mismo formato:

```json
{"error": {"codigo": "TEXTO_DEMASIADO_CORTO", "mensaje": "La noticia debe tener al menos 20 palabras."}}
```

| HTTP | código | cuándo | ejemplo |
|---|---|---|---|
| 422 | `TEXTO_VACIO` | `texto` vacío o solo espacios | `-d '{"texto": "  "}'` |
| 422 | `TEXTO_DEMASIADO_CORTO` | menos de `api.min_palabras` (20) palabras | `-d '{"texto": "Hay vacuna"}'` |
| 422 | `TEXTO_DEMASIADO_LARGO` | más de `api.max_chars` (20.000) caracteres | — |
| 422 | `FORMATO_INVALIDO` | falta `texto` (o `textos` en el lote), tipo incorrecto o JSON mal formado | `-d '{"text": "…"}'` |
| 422 | `LOTE_INVALIDO` | lote vacío, con más de 100 noticias o con alguna noticia inválida | `-d '{"textos": []}'` |
| 503 | `MODELO_NO_DISPONIBLE` | no existe o no cargó el modelo | — |

Los límites se leen de `params.yaml → api`: cambiarlos no requiere tocar código.

> La probabilidad del ejemplo es baja (0,51) porque es una noticia de dos líneas: el modelo se entrenó con noticias de unas 350 palabras de mediana. Con textos completos es más seguro.
