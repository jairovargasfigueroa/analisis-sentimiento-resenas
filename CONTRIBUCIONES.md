# Contribuciones

Cada integrante completa **su propia sección** en su propio commit. Esta información debe coincidir con el historial de Git (`git shortlog -sne`).

## Brayan Albaro Garcia Taboada (@Alba-Tab)

**Parte 1 · Predicción** · Specs 10 (carga), 20, 30 (base), 40, 50 (Analizar)

- [#45](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/45) [1.0] chore(config): adaptar el proyecto a noticias falsas
- [#46](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/46) [1.1] feat(datos): corpus de noticias falsas unificado
- [#47](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/47) [1.2] feat(nlp): pipeline de preprocesamiento completo
- [#48](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/48) [1.3] feat(modelos): entrenamiento base con regresión logística
- [#49](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/49) [1.4] feat(api): endpoints de estado y predicción
- [#50](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/50) [1.5] feat(front): pestaña Analizar con paso a paso
- [#51](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/51) [1.6] docs(readme): instalación desde cero en Windows y macOS
- Documentación: secciones 1, 2, 4 y 7 del informe, modificaciones en vivo B1–B5 y diapositivas de problema, datos, NLP y demo.

**Parte de NLP/ML:** normalización con señales de estilo (exclamaciones, emojis, cifras), stop words con las negaciones conservadas, stemming y lematización (y por qué las tildes se quitan al final), `TextPreprocessor` serializable y `explicar_preprocesamiento()`; split estratificado, línea base y Regresión Logística; y la detección de dos diferencias de formato entre versiones del corpus (titular repetido y marcadores `*NUMBER*`) que inflaban el F1.

## Jairo Vargas Figueroa (@jairovargasfigueroa)

**Parte 2 · Análisis y métricas** · Specs 10 (EDA), 30 (comparación), 40 (`/metrics`), 50 (Métricas)

- Organización del repositorio y especificaciones iniciales del proyecto (`specs/`, `AGENTS.md`, CI): PRs [#1](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/1), [#2](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/2) y [#3](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/3).
- Revisión e integración de los PRs de la Parte 1 de Brayan (#45 a #52).
- [#53](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/53) [2.1] exp(eda): análisis exploratorio del corpus
- [#54](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/54) [2.2] exp(modelos): comparación de modelos y experimentos
- [#55](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/55) [2.3] feat(metricas): endpoint y pestaña de métricas
- [#57](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/57) [3.1] feat(lote): predicción por lote en API y frontend (`/predict/lote`, pestaña Lote, docs de `/predict/lote` y `/metrics`, README actualizado)
- [#56](https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas/pull/56) [3.3] docs(entrega): secciones 3, 5 y 6 del informe, conclusiones, recetas J1–J3, diapositivas de modelos, métricas, errores y conclusiones, y el modo `--rapido` de entrenamiento con la caché de `pasos()` (de 274 s a 46 s).

**Parte de NLP/ML:** EDA completa (clases, longitudes, palabras y temas por clase, exclamaciones, fuentes satíricas) y la detección de las firmas de agencia («bbc», «afp», «reuters») que filtraban la fuente dentro del texto, agregadas como stop words del dominio tras medirlas con validación cruzada; `evaluacion.py` (métricas por clase, matriz de confusión, línea base, errores más seguros, palabras influyentes); Naive Bayes y `GridSearchCV` con `StratifiedKFold` de 5 y `Pipeline(memory)`; elección del modelo por F1 de validación cruzada en lugar de test; experimentos E1 (stem vs lema), E2 (n-gramas) y E3 (2018 → 2020-21); y el análisis de cinco errores.
