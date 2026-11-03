# 60 · Entrega, documentación y defensa

- **Responsables:** todos. Cada uno escribe la sección del informe de **su** área, con su propio commit.
- **Enunciado:** secciones 5.7, 6, 7, 8 y 10.

## Checklist de entrega (sección 7 del enunciado)

- [ ] Código fuente completo: pipeline de NLP, entrenamiento, backend y frontend.
- [ ] Modelos serializados en `models/` **y** el script que los regenera con un solo comando.
- [ ] Notebooks de EDA (`01_eda.ipynb`) y de experimentos (`02_experimentos.ipynb`), ejecutados y con las salidas visibles.
- [ ] Informe técnico breve en `docs/informe.md`.
- [ ] `README.md` con instalación y ejecución **desde cero**.
- [ ] `CONTRIBUCIONES.md` coherente con el historial de commits.
- [ ] Diapositivas en `docs/presentacion.pdf`, o el enlace en el README.
- [ ] Tag `entrega-final` sobre el último commit de `main` antes del plazo.

## README.md (se va completando con PRs)

1. Descripción del proyecto en dos o tres líneas.
2. Requisitos: Python 3.11 y Node 18 o superior.
3. Instalación:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
   pip install -r requirements.txt
   python -m spacy download es_core_news_sm
   python -m nltk.downloader stopwords
   ```
4. Entrenar: `python -m src.models.train`.
5. Levantar la API: `uvicorn api.main:app --reload`.
6. Levantar el frontend: `cd frontend && npm install && npm run dev`.
7. Tests: `pytest -q`.
8. Endpoints, con ejemplos `curl`.

**Prueba de fuego:** otro integrante clona el repo en una carpeta nueva y lo levanta siguiendo **solo** el README.

## Informe técnico (`docs/informe.md`)

| Sección | Autor |
|---|---|
| 1. Problema y objetivo | Integrante 1 |
| 2. Dataset: origen, licencia, fecha, EDA y desbalance | Integrante 1 |
| 3. Decisiones de NLP, con ejemplos antes/después de cada paso | Integrantes 1, 2 y 4 |
| 4. Modelos: justificación, funcionamiento interno, hiperparámetros, **tabla comparativa**, E1, E2 | Integrante 2 |
| 5. Evaluación: baseline, matriz de confusión, **análisis de errores** | Integrante 3 |
| 6. Arquitectura: diagrama, API y frontend | Integrantes 3 y 4 |
| 7. Conclusiones y limitaciones | Todos |
| 8. **Declaración de uso de asistentes de IA** (obligatoria, sección 10 del enunciado) | Todos |
| 9. Referencias (dataset, librerías, código reutilizado) | Todos |

## CONTRIBUCIONES.md

Cada integrante completa **su propia sección**, en su propio commit, con:

- Rol y specs a cargo.
- Lista de aportes con enlace a los PR.
- Su parte de NLP/ML.

Debe **coincidir con el historial**. Se puede revisar con `git shortlog -sne` y `git log --author="Nombre" --oneline`.

## Presentación (sección 8 del enunciado)

1. **Exposición grupal (~10 min):** problema → dataset → arquitectura → **demo en vivo** (una reseña, un lote, el paso a paso y las métricas).
2. **Explicación individual (~3 min por persona):** cada uno muestra **sus commits** y explica qué hizo, por qué y qué alternativas consideró.
3. **Preguntas:** cualquiera puede ser preguntado sobre cualquier parte, sobre todo NLP y el funcionamiento interno de los modelos.
4. **Modificación en vivo.** Ensayar antes:

| Área | Ensayo | Dónde se toca |
|---|---|---|
| NLP | Agregar o quitar una stop word y reentrenar | `src/nlp/stopwords.py` (`CONSERVAR`/`AGREGAR`) |
| NLP | Cambiar n-gramas o stem↔lema y reentrenar | `src/models/train.py` |
| Modelado | Cambiar `C` o `alpha`, reentrenar y comparar | `src/models/train.py` |
| Modelado | Calcular otra métrica (por ejemplo, error por clase o AUC) | `src/models/evaluacion.py` |
| Backend | Rechazar textos de menos de 3 palabras | `api/esquemas.py` |
| Frontend | Mostrar un dato nuevo o cambiar un gráfico | `frontend/src/components/` |

El día de la presentación se clona **desde el tag**: `git clone --branch entrega-final <url>`.
