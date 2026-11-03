# Analizador de Sentimiento de Reseñas

Aplicación web que clasifica reseñas en español como **positivas o negativas**, con su probabilidad, y muestra paso a paso el preprocesamiento de NLP aplicado.

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
3. Lee tu spec y crea tu rama: `git switch -c feat/<area>-<tarea>`.
4. Trabaja con commits pequeños y abre un PR que revise otro integrante.

## Instalación y ejecución

> Se completa a medida que se integran las partes (ver [60-entrega](specs/60-entrega.md)).

## Enunciado

[`docs/enunciado-proyecto-integrador.pdf`](docs/enunciado-proyecto-integrador.pdf)
