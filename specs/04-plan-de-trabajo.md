# 04 · Plan de trabajo: qué hace cada uno y en qué orden

Este es el **mapa** del proyecto. Cada tarea es **una rama → uno o varios commits → un PR** que revisa otro integrante. Para saber *cómo* hacer cada tarea, ve a la spec que se indica.

## Seguimiento automático (GitHub Issues + CI)

- **Cada tarea es un issue** del repo, asignado a su dueño, con su fase (milestone), su área (etiqueta), su rama, su spec y sus dependencias. Se ven en la pestaña *Issues*, filtrando por milestone o por persona.
- La rama se llama **exactamente** como dice el issue.
- El PR lleva el título `[1.3] feat(nlp): ...` y en la descripción `Closes #<issue>`. **Al integrarse, el issue se cierra solo**: un issue cerrado es una tarea terminada.
- La **CI** (GitHub Actions) corre en cada PR. Verifica el formato del título, ejecuta `pytest` y compila el frontend. Solo se integra con todo en verde.
- El agente de IA de cada integrante revisa sus issues al iniciar cada sesión y propone la siguiente tarea (ver `AGENTS.md`).
- Cada uno lo ve con `gh issue list --assignee @me`, o en la web con *Issues → Assigned to me*.

**Equipo:** Jairo = P1 (datos y NLP) · Brayan = P2 (modelado) · Jovas = P3 (backend) · Adrián = P4 (frontend).

## Reglas para que nada choque

1. **Cada archivo tiene un único dueño** (tabla de `01-arquitectura.md`). Solo su dueño lo modifica.
2. Hay archivos **compartidos**: `README.md`, `requirements.txt`, `params.yaml`, `docs/informe.md` y `CONTRIBUCIONES.md`. Se tocan **solo en la sección propia** y con PR pequeños.
3. Antes de abrir un PR: `git switch main && git pull && git switch <tu-rama> && git merge main`, y después corre `pytest -q`.
4. **Nadie espera a nadie.** Si lo que necesitas aún no está en `main`, trabaja con el contrato de `02-contratos.md` y datos simulados (mocks).
5. El **orden de revisión** sugerido es que cada PR lo revise quien va a usar ese código:

| PR de | Lo revisa |
|---|---|
| P1 (Jairo) | P2 (Brayan) |
| P2 (Brayan) | P3 (Jovas) |
| P3 (Jovas) | P4 (Adrián) |
| P4 (Adrián) | P1 (Jairo) |

---

## Fase 0 · Preparación (todos, el primer día)

- [ ] Aceptar la invitación al repositorio.
- [ ] Configurar la identidad de Git con **su propia cuenta** (ver `03-flujo-git.md`).
- [ ] Clonar el repo, crear el entorno e instalar:
  ```bash
  py -3.12 -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  python -m nltk.downloader stopwords
  ```
- [ ] Leer `AGENTS.md`, las specs 00 a 04 y la spec de su área.
- [ ] **Uno de P2, P3 o P4 revisa y aprueba el PR #1**, y Jairo lo integra.

---

## Fase 1 · Base en paralelo (nadie depende de nadie)

| # | Quién | Rama | Tarea | Spec |
|---|---|---|---|---|
| 1.1 | **P1 Jairo** | `feat/datos-carga` | Elegir un **dataset real**, `data/README.md`, `src/data/cargar.py` y generar `data/processed/resenas.csv` | 10 |
| 1.2 | **P1 Jairo** | `feat/nlp-normalizacion` | `normalizar()` y `tokenizar()` + tests | 20-A |
| 1.3 | **P1 Jairo** | `feat/nlp-stopwords` | `obtener_stopwords()` y `quitar_stopwords()`, leyendo `params.yaml` + tests | 20-A |
| 1.4 | **P2 Brayan** | `feat/nlp-raices` | `stemizar()` y `lematizar()` + tests | 20-B |
| 1.5 | **P2 Brayan** | `exp/modelos-teoria` | Sección del informe: cómo funcionan por dentro Regresión Logística y Naive Bayes | 30-A |
| 1.6 | **P3 Jovas** | `feat/modelos-evaluacion` | `evaluacion.py`: métricas, baseline, matriz de confusión y errores. Se prueba con cualquier modelo de sklearn | 30-B |
| 1.7 | **P3 Jovas** | `feat/api-base` | FastAPI con `/health`, `/predict`, `/predict/lote` y `/metrics` usando un **modelo falso**, más esquemas, validaciones, formato de error y CORS | 40 |
| 1.8 | **P4 Adrián** | `feat/front-base` | Proyecto React + Vite, `src/api.js` y **mocks** de C8 | 50 |
| 1.9 | **P4 Adrián** | `feat/front-prediccion` | Vista "Analizar" y vista "Paso a paso" con datos mock | 50 |

**Prioridad:** la 1.1 de Jairo es la primera que conviene integrar, porque el dataset real alimenta todo lo demás.

## Fase 2 · Piezas que dependen de la fase 1

| # | Quién | Rama | Tarea | Necesita en `main` | Spec |
|---|---|---|---|---|---|
| 2.1 | **P1 Jairo** | `feat/nlp-preprocesador` | `TextPreprocessor` (C4), que se pueda serializar + test | 1.2, 1.3, 1.4 | 20-A |
| 2.2 | **P1 Jairo** | `exp/eda` | Notebook `01_eda.ipynb` con las conclusiones. Ajustar `nlp.agregar` según la EDA | 1.1, 1.3 | 10 |
| 2.3 | **P4 Adrián** | `feat/nlp-explicar` | `explicar_preprocesamiento()` (C5) + test de coherencia | 2.1 | 20-C |
| 2.4 | **P3 Jovas** | `feat/modelos-predecir` | `predecir.py` (C7) + `tests/test_modelo.py` | 2.1 | 30-B |
| 2.5 | **P4 Adrián** | `feat/front-lote`, `feat/front-metricas` | Vistas "Lote" y "Métricas" con mocks | — | 50 |

## Fase 3 · Modelo real e integración

| # | Quién | Rama | Tarea | Necesita | Spec |
|---|---|---|---|---|---|
| 3.1 | **P2 Brayan** | `feat/modelos-train` | `train.py`: experimentos E1 y E2, GridSearchCV, comparación, guarda `.joblib` y `metricas.json` | 1.1, 1.6, 2.1 | 30-A |
| 3.2 | **P2 Brayan** | `exp/experimentos` | Notebook `02_experimentos.ipynb` con E1, E2, tabla comparativa y gráficos | 3.1 | 30-A |
| 3.3 | **P3 Jovas** | `feat/api-modelo-real` | La API carga el modelo real, usa `predecir()` y `explicar_preprocesamiento()`; tests completos | 2.3, 2.4, 3.1 | 40 |
| 3.4 | **P3 Jovas** | `feat/modelos-errores` | Análisis de errores interpretado (al menos 5 casos) y palabras influyentes | 3.1 | 30-B |
| 3.5 | **P4 Adrián** | `feat/front-api-real` | Conectar a la API real, apagar los mocks e indicador de `/health` | 3.3 | 50 |

**Prueba de integración (todos juntos):** clonar el repo en una carpeta nueva y levantarlo siguiendo solo el README.

## Fase 4 · Documentación, extras y ensayo

| # | Quién | Tarea | Spec |
|---|---|---|---|
| 4.1 | Todos | Su sección de `docs/informe.md` (tabla de autores en la spec 60) | 60 |
| 4.2 | Todos | Su receta en `docs/modificaciones_en_vivo.md`, **probada** y con los números obtenidos | 60 |
| 4.3 | Todos | Su sección de `CONTRIBUCIONES.md` | 60 |
| 4.4 | P1 Jairo | README final: instalación desde cero | 60 |
| 4.5 | P3 Jovas | `docs/api.md` con ejemplos `curl` | 40 |
| 4.6 | P3 + P4 (opcional) | Docker Compose (API + frontend). Suma como valor agregado | 60 |
| 4.7 | Todos | Diapositivas: cada uno arma las de su parte | 60 |
| 4.8 | P1 Jairo | Último PR integrado → tag `entrega-final` | 03 |
| 4.9 | Todos | **Ensayo:** exposición de 10 minutos, 3 minutos por persona y una modificación en vivo cada uno | 60 |

---

## Resumen por persona (en orden)

**Jairo (P1):** 1.1 dataset → 1.2 normalización y tokenización → 1.3 stop words → 2.1 TextPreprocessor → 2.2 EDA → 4.4 README → 4.8 tag.

**Brayan (P2):** 1.4 stemming y lematización → 1.5 teoría de los modelos → 3.1 train.py → 3.2 notebook de experimentos.

**Jovas (P3):** 1.6 evaluación → 1.7 API base → 2.4 predecir → 3.3 API con modelo real → 3.4 análisis de errores → 4.5 docs de la API.

**Adrián (P4):** 1.8 base React → 1.9 Analizar y Paso a paso → 2.5 Lote y Métricas → 2.3 explicar_preprocesamiento → 3.5 conexión real.

Todos terminan con 4.1, 4.2, 4.3, 4.7 y 4.9.

Cada uno tiene trabajo de NLP/ML, como exige el enunciado:

| Integrante | Su parte de NLP/ML |
|---|---|
| Jairo | Normalización, stop words y TextPreprocessor |
| Brayan | Stemming y lematización, experimentos y modelos |
| Jovas | Evaluación, baseline y errores |
| Adrián | explicar_preprocesamiento |
