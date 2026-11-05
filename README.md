# Detector de Noticias Falsas en Español

Aplicación web que clasifica noticias en español como **falsas o verdaderas**, con su probabilidad, y muestra paso a paso el preprocesamiento de NLP aplicado. Se entrena con *The Spanish Fake News Corpus* (1.543 noticias reales, CC BY 4.0).

Proyecto Integrador · Primer Parcial · *Tópicos y Programación Avanzada*.

```
Datos → Pipeline NLP → TF-IDF → Regresión Logística / Naive Bayes → API (FastAPI) → Frontend (React)
```

## Cómo está organizado este proyecto

El desarrollo está **guiado por especificaciones**: todo lo que hay que construir, quién lo hace y cuándo está terminado está en [`specs/`](specs/).

| Spec | Contenido |
|---|---|
| [00-vision](specs/00-vision.md) | Problema, solución, alcance y equipo |
| [01-arquitectura](specs/01-arquitectura.md) | Capas, stack, carpetas y responsables |
| [02-contratos](specs/02-contratos.md) | Interfaces compartidas (funciones, artefactos, API) |
| [03-flujo-git](specs/03-flujo-git.md) | Ramas, commits y pull requests |
| [04-plan-de-trabajo](specs/04-plan-de-trabajo.md) | **Qué hace cada integrante y en qué orden** (Brayan: Predicción · Jairo: Análisis y métricas) |
| [10-datos-eda](specs/10-datos-eda.md) | Dataset y análisis exploratorio |
| [20-nlp](specs/20-nlp.md) | Pipeline de preprocesamiento |
| [30-modelos](specs/30-modelos.md) | Entrenamiento, comparación y evaluación |
| [40-backend](specs/40-backend.md) | API REST |
| [50-frontend](specs/50-frontend.md) | Interfaz web |
| [60-entrega](specs/60-entrega.md) | Documentación, entrega y defensa |

Si usas un asistente de IA, este lee primero [`AGENTS.md`](AGENTS.md) (o `CLAUDE.md`).

### Para empezar (cada integrante)

1. Acepta la invitación al repositorio.
2. Configura tu identidad de Git y clona el repo (ver [03-flujo-git](specs/03-flujo-git.md)).
3. Busca tu nombre en [04-plan-de-trabajo](specs/04-plan-de-trabajo.md): ahí están tus tareas en orden.
4. Para cada tarea, crea la rama que dice su issue, haz commits pequeños y abre un PR que revise el otro integrante.

## Instalación desde cero

Requisitos: **Python 3.12**, **Node 18 o superior** y Git. Todos los comandos se ejecutan desde la raíz del repo.

### 1. Clonar

```bash
git clone https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas.git
cd analisis-sentimiento-resenas
```

### 2. Entorno de Python

Windows (PowerShell):

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m nltk.downloader stopwords
```

macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader stopwords
```

`requirements.txt` ya incluye el modelo de spaCy en español (`es_core_news_sm`).

### 3. Entrenar

```bash
python -m src.models.train
```

Genera `data/processed/noticias.csv`, entrena y guarda `models/modelo_produccion.joblib` y `models/metricas.json`. Tarda menos de un minuto e imprime una tabla como esta:

| modelo | accuracy | F1 macro |
|---|---|---|
| línea base (clase mayoritaria) | 0,505 | 0,336 |
| Regresión Logística | 0,786 | 0,786 |

### 4. Levantar la API

```bash
uvicorn api.main:app --reload --port 8000
```

Queda en <http://localhost:8000>, con la documentación interactiva en <http://localhost:8000/docs>. Los endpoints y sus errores, con ejemplos `curl`, están en [`docs/api.md`](docs/api.md).

### 5. Levantar el frontend (en otra terminal)

```bash
cd frontend
npm install
npm run dev
```

Abre <http://localhost:5173>. La cabecera muestra un punto verde si la API y el modelo están listos. Prueba con los botones de ejemplo: son noticias del conjunto de prueba, que el modelo no vio al entrenar.

### 6. Tests

```bash
pytest -q
```

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `python3.12: command not found` (macOS) | `brew install python@3.12`, o con [uv](https://docs.astral.sh/uv/): `uv venv --python 3.12 .venv` |
| `Resource stopwords not found` | `python -m nltk.downloader stopwords` con el entorno activado |
| La cabecera dice que no hay modelo (503) | Falta entrenar: `python -m src.models.train` y reiniciar uvicorn |
| El frontend no conecta con la API | Revisa que uvicorn esté en el puerto 8000, o define `VITE_API_URL` (ver `frontend/.env.example`) |

## Estructura

```
data/raw/         corpus original (.xlsx) y su README
src/data/         carga y unificación del corpus
src/nlp/          normalización, tokens, stop words, lemas y TextPreprocessor
src/models/       train.py y predecir.py
api/              FastAPI: /health y /predict
frontend/         React + Vite: pestaña Analizar con el paso a paso
tests/            pytest
params.yaml       todos los parámetros ajustables (stop words, TF-IDF, grillas, límites de la API)
```

Cambiar un valor de `params.yaml` y reentrenar alcanza para casi todas las modificaciones en vivo.

## Datos

*The Spanish Fake News Corpus* (Posadas-Durán et al., 2019; Gómez-Adorno et al., 2021), licencia CC BY 4.0. Detalle y cita en [`data/raw/README.md`](data/raw/README.md).

## Enunciado

[`docs/enunciado-proyecto-integrador.pdf`](docs/enunciado-proyecto-integrador.pdf)
