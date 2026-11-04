# 60 · Entrega, documentación y defensa

- **Responsables:** los dos. Cada uno escribe la sección del informe de **su** parte, en su propio PR (3.2 Brayan, 3.3 Jairo).
- **Enunciado:** secciones 5.7, 6, 7, 8 y 10.

## Checklist de entrega (sección 7 del enunciado)

- [ ] Código fuente completo: pipeline de NLP, entrenamiento, backend y frontend.
- [ ] Modelos serializados en `models/` **y** el script que los regenera con un solo comando.
- [ ] Notebook de EDA y experimentos (`01_eda.ipynb`), ejecutado y con las salidas visibles.
- [ ] Informe técnico breve en `docs/informe.md`.
- [ ] `docs/api.md` con los endpoints y ejemplos (Brayan).
- [ ] `docs/modificaciones_en_vivo.md`: una receta **probada** por integrante, con los números antes y después.
- [ ] `README.md` con instalación y ejecución **desde cero**.
- [ ] `CONTRIBUCIONES.md` coherente con el historial de commits.
- [ ] Diapositivas en `docs/presentacion.pdf`, o el enlace en el README.
- [ ] Tag `entrega-final` sobre el último commit de `main` antes del plazo.

## README.md (se va completando con PRs)

1. Descripción del proyecto en dos o tres líneas.
2. Requisitos: Python 3.12 y Node 18 o superior.
3. Instalación (el modelo de spaCy ya viene en `requirements.txt`):
   ```bash
   py -3.12 -m venv .venv          # macOS: python3.12 -m venv .venv
   .venv\Scripts\activate          # macOS: source .venv/bin/activate
   pip install -r requirements.txt
   python -m nltk.downloader stopwords
   ```
4. Entrenar: `python -m src.models.train`.
5. Levantar la API: `uvicorn api.main:app --reload`.
6. Levantar el frontend: `cd frontend && npm install && npm run dev`.
7. Tests: `pytest -q`.
8. Endpoints, con ejemplos `curl`.

**Prueba de fuego:** el otro integrante clona el repo en una carpeta nueva y lo levanta siguiendo **solo** el README.

## Informe técnico (`docs/informe.md`)

| Sección | Autor |
|---|---|
| 1. Problema y objetivo | Brayan |
| 2. Dataset: origen, licencia, fecha y carga | Brayan |
| 3. EDA: clases, longitudes, fuentes satíricas | Jairo |
| 4. Decisiones de NLP, con ejemplos antes/después de cada paso | Brayan |
| 5. Modelos: justificación, funcionamiento interno, hiperparámetros, **tabla comparativa**, E1, E2 (E3) | Jairo |
| 6. Evaluación: baseline, matriz de confusión, **análisis de errores** | Jairo |
| 7. Arquitectura: diagrama, API y frontend | Brayan |
| 8. Conclusiones y limitaciones (estilo vs veracidad, caída temporal) | Los dos |
| 9. **Declaración de uso de asistentes de IA** (obligatoria, sección 10 del enunciado; una sola vez) | Los dos |
| 10. Referencias (dataset, librerías, ejemplo del docente) | Los dos |

## CONTRIBUCIONES.md

Cada integrante completa **su propia sección**, en su propio commit, con:

- Rol y specs a cargo.
- Lista de aportes con enlace a los PR.
- Su parte de NLP/ML.

Debe **coincidir con el historial**. Se puede revisar con `git shortlog -sne` y `git log --author="Nombre" --oneline`.

## Presentación (sección 8 del enunciado)

1. **Exposición grupal (~10 min):** problema → dataset → arquitectura → **demo en vivo** (una noticia, el paso a paso y las métricas; un lote si se hizo). Diapositivas: Brayan (problema, datos, NLP, demo), Jairo (modelos, métricas, errores, conclusiones).
2. **Explicación individual (~3 min por persona):** cada uno muestra **sus commits** y explica qué hizo, por qué y qué alternativas consideró.
3. **Preguntas:** cualquiera puede ser preguntado sobre cualquier parte, sobre todo NLP y el funcionamiento interno de los modelos.
4. **Modificación en vivo.** Ensayar antes:

| Área | Ensayo | Dónde se toca |
|---|---|---|
| NLP | Agregar o quitar una stop word y reentrenar | `params.yaml` → `nlp.conservar` / `nlp.agregar` |
| NLP | Cambiar n-gramas o stem↔lema y reentrenar | `params.yaml` → `experiments.ngram_ranges` / `experiments.modos` |
| Modelado | Cambiar `C` o `alpha`, reentrenar y comparar | `params.yaml` → `experiments.models` |
| Modelado | Calcular otra métrica (por ejemplo, error por clase o AUC) | `src/models/evaluacion.py` |
| Backend | Cambiar el mínimo de palabras o agregar una validación | `params.yaml` → `api.min_palabras`, `api/esquemas.py` |
| Frontend | Mostrar un dato nuevo de la API (por ejemplo, las 5 palabras que más pesaron) | `frontend/src/components/` |

Cada receta probada se documenta en `docs/modificaciones_en_vivo.md`: qué se cambia, el comando para reentrenar, las métricas antes y después, y cómo interpretarlas.

El día de la presentación se clona **desde el tag**: `git clone --branch entrega-final <url>`.
