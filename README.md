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
git clone https://github.com/jairovargasfigueroa/detector-noticias-falsas.git
cd detector-noticias-falsas
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

Genera `data/processed/noticias.csv`, busca los hiperparámetros de los dos modelos con validación cruzada, elige el mejor, corre los experimentos E1, E2 y E3 y guarda `models/modelo_produccion.joblib` y `models/metricas.json`. Tarda unos 80 s (`--rapido`, sin experimentos, unos 45 s) e imprime una tabla como esta:

| modelo | F1 CV | accuracy | F1 test | hiperparámetros |
|---|---|---|---|---|
| línea base (clase mayoritaria) | — | 0,505 | 0,336 | — |
| Regresión Logística ★ | 0,766 | 0,773 | 0,773 | C = 10 |
| Naive Bayes | 0,695 | 0,735 | 0,732 | alpha = 0,1 |

El repo ya trae el modelo entrenado en `models/`, así que este paso solo hace falta si se cambia algo.

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

Abre <http://localhost:5173>. La cabecera muestra un punto verde si la API y el modelo están listos. Tiene tres pestañas:

- **Analizar**: una noticia, su clase y el preprocesamiento paso a paso. Prueba con los botones de ejemplo: son noticias del conjunto de prueba, que el modelo no vio al entrenar.
- **Lote**: sube un `.csv` (columna `texto`) o un `.txt` (una noticia por línea). Hay un ejemplo descargable en la misma pestaña.
- **Métricas**: comparación de modelos, matriz de confusión, experimentos, palabras influyentes y errores.

### 6. Tests

```bash
pytest -q
```

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `python3.12: command not found` (macOS) | `brew install python@3.12`, o con [uv](https://docs.astral.sh/uv/): `uv venv --python 3.12 .venv` |
| `Resource stopwords not found` | `python -m nltk.downloader stopwords` con el entorno activado |
| `DLL load failed … nombre del archivo o la extensión es demasiado largo` (Windows, al importar spaCy) | La ruta de la carpeta es demasiado larga para Windows (límite de 260 caracteres). Clona el repo en una ruta corta, por ejemplo `C:\proyectos\`, y vuelve a crear `.venv` |
| La cabecera dice que no hay modelo (503) | Falta entrenar: `python -m src.models.train` y reiniciar uvicorn |
| El frontend no conecta con la API | Revisa que uvicorn esté en el puerto 8000, o define `VITE_API_URL` (ver `frontend/.env.example`) |

## Estructura

```
data/raw/         corpus original (.xlsx) y su README
src/data/         carga y unificación del corpus
src/nlp/          normalización, tokens, stop words, lemas y TextPreprocessor
src/models/       train.py, experimentos.py, evaluacion.py y predecir.py
models/           modelo entrenado (.joblib) y metricas.json
notebooks/        EDA, experimentos y análisis de errores (01_eda.ipynb)
api/              FastAPI: /health, /predict, /predict/lote y /metrics
frontend/         React + Vite: pestañas Analizar, Lote y Métricas
tests/            pytest
docs/             informe, API, modificaciones en vivo y diapositivas
params.yaml       todos los parámetros ajustables (stop words, TF-IDF, grillas, límites de la API)
```

Cambiar un valor de `params.yaml` y reentrenar (`python -m src.models.train --rapido`) alcanza para casi todas las modificaciones en vivo. Las recetas ensayadas están en [`docs/modificaciones_en_vivo.md`](docs/modificaciones_en_vivo.md).

## Datos

*The Spanish Fake News Corpus* (Posadas-Durán et al., 2019; Gómez-Adorno et al., 2021), licencia CC BY 4.0. Detalle y cita en [`data/raw/README.md`](data/raw/README.md).

## Presentación

[`docs/presentacion.pdf`](docs/presentacion.pdf): 11 diapositivas más la portada. El guion de cada una está en [`docs/diapositivas/`](docs/diapositivas/) y el PDF se regenera desde `presentacion.html` (instrucciones en el propio archivo).

## Enunciado

[`docs/enunciado-proyecto-integrador.pdf`](docs/enunciado-proyecto-integrador.pdf)
