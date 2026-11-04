# 04 · Plan de trabajo: qué hace cada uno y en qué orden

Cada tarea es **una rama → varios commits (uno por idea) → un PR** que revisa el otro integrante. Para saber *cómo* hacer cada tarea, ve a la spec que se indica.

Se reparte **por funcionalidad, no por capa**: cada uno entrega una parte completa (datos o NLP, modelo, API y frontend). Así los dos tienen commits de NLP y ML, como exige el enunciado (6.1), y la Parte 1 sola ya es presentable.

**Equipo:** Brayan (@Alba-Tab) = Parte 1 · Predicción · Jairo (@jairovargasfigueroa) = Parte 2 · Análisis y métricas.

## Seguimiento (GitHub Issues + CI)

- **Cada tarea es un issue**, asignado a su dueño, con su milestone (`Parte 1 · Predicción`, `Parte 2 · Análisis y métricas`, `Noche y cierre`), su área, su rama y sus commits previstos.
- La rama se llama **exactamente** como dice el issue.
- El PR lleva el título `[1.3] feat(modelos): ...` y en la descripción `Closes #<issue>`. Al integrarse en `main`, el issue se cierra solo.
- La **CI** corre en cada PR, también en los encadenados: formato del título, `pytest` y build del frontend.

## Reglas para que nada choque

1. Cada archivo tiene un dueño (tabla de `01-arquitectura.md`). Jairo agrega archivos y pestañas nuevos; no edita los de Brayan, salvo una línea en `params.yaml` y el registro de rutas en `api/main.py` y `App.jsx`.
2. Contratos compartidos (`02-contratos.md`): `noticias.csv` (C2), `TextPreprocessor` (C4), `metricas.json` (C6) y la API (C8). Con ellos cada uno avanza con datos simulados.
3. Antes de abrir un PR: `pytest -q` en verde.
4. Cada PR lo revisa e integra **el otro integrante**.

---

## Parte 1 · Brayan: Predicción (PRs encadenados)

Cada rama sale de la anterior y su PR apunta a esa rama, así cada uno muestra solo su cambio. Al terminar el 1.6, `uvicorn` y `npm run dev` levantan un sistema que clasifica una noticia y muestra el paso a paso.

| # | Rama | Sale de | Tarea | Spec |
|---|---|---|---|---|
| 1.0 | `chore/config-noticias` | `main` | `params.yaml`, CI en PRs encadenados, `openpyxl`, specs para noticias | 00, 02 |
| 1.1 | `feat/datos-carga` | 1.0 | Corpus en `data/raw` con su README, unificación v1/v2, `noticias.csv` + tests | 10 |
| 1.2 | `feat/nlp-pipeline` | 1.1 | Normalizar, tokenizar, stop words, raíces y lemas, `TextPreprocessor`, `explicar_preprocesamiento()` + tests | 20 |
| 1.3 | `feat/modelo-base` | 1.2 | Split 80/20, `train.py` con Regresión Logística y línea base, artefactos, `predecir()` + tests | 30 |
| 1.4 | `feat/api-prediccion` | 1.3 | Esquemas, error único, `/health`, `/predict`, validaciones, CORS + tests | 40 |
| 1.5 | `feat/front-analizar` | 1.4 | React + Vite, cabecera con estado de la API, pestaña Analizar y paso a paso | 50 |
| 1.6 | `docs/readme-instalacion` | 1.5 | README: instalación desde cero (Windows y macOS), entrenar y levantar todo | 60 |

## Parte 2 · Jairo: Análisis y métricas (salen de `main` con la Parte 1 integrada)

Los 2.1 y 2.2 se pueden trabajar a la vez; el 2.3 arranca con un `metricas.json` de ejemplo (C6) y luego usa el real.

| # | Rama | Tarea | Spec |
|---|---|---|---|
| 2.1 | `exp/eda` | EDA: clases, longitudes, faltantes, palabras y temas por clase, fuentes satíricas; stop words del dominio | 10 |
| 2.2 | `exp/experimentos` | Evaluación, Naive Bayes, GridSearchCV, E1 y E2 (E3 y E4 opcionales), `metricas.json` completo, 5 errores explicados | 30 |
| 2.3 | `feat/metricas` | `GET /metrics` + tests, pestaña Métricas (tarjeta, tabla comparativa, matriz de confusión, experimentos, errores) | 40, 50 |

## Noche y cierre

| # | Quién | Rama | Tarea |
|---|---|---|---|
| 3.1 | Brayan (opcional) | `feat/prediccion-lote` | `POST /predict/lote` + tests, pestaña Lote |
| 3.2 | Brayan | `docs/entrega-brayan` | Informe (datos, NLP, arquitectura y API), modificaciones en vivo, CONTRIBUCIONES, diapositivas |
| 3.3 | Jairo | `docs/entrega-jairo` | Informe (EDA, modelos, experimentos, errores), modificaciones en vivo, CONTRIBUCIONES, diapositivas |

Los dos tocan `api/main.py` y `App.jsx`: el que integra segundo hace `git merge main` en su rama y resuelve (son pocas líneas).

## Qué es obligatorio y qué se puede cortar

| Prioridad | Qué |
|---|---|
| Obligatorio | EDA; todos los pasos de NLP; E1 y E2; dos modelos con GridSearchCV y línea base; 5 errores explicados; API con `/health`, `/predict` y `/metrics`, validaciones, tests y documentación; frontend con resultado, paso a paso y panel de métricas; README, informe, CONTRIBUCIONES, diapositivas y tag |
| Se corta primero | PR 3.1 lote; E3 y E4; pestaña Datos; Docker |
| Se simplifica | EDA y experimentos en un solo notebook; la pestaña Métricas con tarjeta, tabla comparativa y matriz de confusión |

**Regla de las 22:30:** si a esa hora `main` no tiene los dos modelos comparados y el panel de métricas, se corta todo lo opcional y se pasa directo a la documentación y al tag `entrega-final` (antes de las 23:30).
