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
| 422 | `FORMATO_INVALIDO` | falta `texto`, no es string o el JSON está mal formado | `-d '{"text": "…"}'` |
| 503 | `MODELO_NO_DISPONIBLE` | no existe o no cargó el modelo | — |

Los límites se leen de `params.yaml → api`: cambiarlos no requiere tocar código.

> La probabilidad del ejemplo es baja (0,51) porque es una noticia de dos líneas: el modelo se entrenó con noticias de unas 350 palabras de mediana. Con textos completos es más seguro.
