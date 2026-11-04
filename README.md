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

## Instalación

Requisitos: Python 3.12 y Node 18 o superior.

Windows:

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

Todos los comandos se ejecutan desde la raíz del repo. Los parámetros ajustables están en [`params.yaml`](params.yaml).

> Entrenamiento, API y frontend: se completa a medida que se integran las partes (ver [60-entrega](specs/60-entrega.md)).

## Enunciado

[`docs/enunciado-proyecto-integrador.pdf`](docs/enunciado-proyecto-integrador.pdf)
