# Informe técnico · Detector de Noticias Falsas en Español

Proyecto Integrador · Primer Parcial · *Tópicos y Programación Avanzada*.
Integrantes: Brayan Albaro Garcia Taboada (@Alba-Tab) y Jairo Vargas Figueroa (@jairovargasfigueroa).

| Sección | Autor |
|---|---|
| 1. Problema y objetivo | Brayan |
| 2. Dataset: origen, licencia y carga | Brayan |
| 3. EDA | Jairo |
| 4. Decisiones de NLP | Brayan |
| 5. Modelos y experimentos | Jairo |
| 6. Evaluación y análisis de errores | Jairo |
| 7. Arquitectura, API y frontend | Brayan |
| 8. Conclusiones y limitaciones | Los dos |
| 9. Declaración de uso de asistentes de IA | Los dos |
| 10. Referencias | Los dos |

## 1. Problema y objetivo

Circulan muchas noticias falsas en español por medios digitales, Facebook y WhatsApp, y verificar cada una a mano lleva tiempo. El objetivo es una **primera señal rápida**: dada una noticia, decir si parece **falsa o verdadera**, con qué probabilidad, y mostrar paso a paso cómo se procesó el texto.

Es una clasificación binaria de texto con TF-IDF y modelos clásicos (Regresión Logística y Naive Bayes), servida por una API (FastAPI) y una interfaz web (React).

El modelo **no verifica hechos**: solo mira el texto. Aprende rasgos de estilo y de tema que en el corpus se asocian con cada clase. Esa limitación se discute en la sección 8.

## 2. Dataset: origen, licencia y carga

**The Spanish Fake News Corpus**, versiones 1.0 y 2.0 ([GitHub de los autores](https://github.com/jpposadas/FakeNewsCorpusSpanish)). Licencia **CC BY 4.0**. Obtenido el 2026-11-04. Etiquetado a mano por los autores contrastando con sitios de verificación.

| Archivo | Versión | Período | Noticias | Verdaderas / falsas |
|---|---|---|---|---|
| `train.xlsx` + `development.xlsx` | 1.0 | ene–jul 2018 | 971 | 491 / 480 |
| `test.xlsx` | 2.0 (FakeDeS, IberLEF 2021) | nov 2020–mar 2021 | 572 | 286 / 286 |

Se juntan las dos versiones y `train.py` hace su propio split estratificado 80/20 con `SEED = 42` (1.233 de entrenamiento, 309 de prueba).

### Carga y unificación (`src/data/cargar.py`)

Las dos versiones no tienen el mismo formato. Unificarlas mal habría dado métricas absurdas o pistas falsas para el modelo:

| Diferencia | v1 (2018) | v2 (2020-21) | Qué se hizo |
|---|---|---|---|
| Encabezados | `Category`, `Topic` | `CATEGORY`, `TOPICS` | Todo a minúsculas y `topics` → `topic` |
| Etiqueta | texto `"True"` / `"Fake"` | booleano `True` / `False` | Se mapea a `verdadera` / `falsa`; una etiqueta desconocida lanza error |
| Titular | el `Text` ya empieza con el titular (943 de 971) | no lo repite; 72 sin titular | `texto = titular + ". " + cuerpo`, salvo que falte el titular o el cuerpo ya lo traiga |
| Cifras y enlaces | anonimizados: `*NUMBER*`, `*PHONE*`, `*URL*` | dígitos y URLs reales | `normalizar()` los iguala (sección 4) |
| Fecha | — | no trae fecha por noticia | `anio`: 2018 para v1, 2021 para toda la v2 |

El titular repetido y los marcadores se encontraron al revisar ejemplos. Las dos le daban al modelo una pista de **la versión** del corpus, no de la veracidad. Corregirlas bajó el F1 de 0,796 a 0,786: ese punto no venía del contenido.

Además se quitó 1 duplicado exacto. Quedan **1.542 noticias: 765 falsas y 777 verdaderas**, casi balanceadas, así que no hace falta `class_weight`.

La columna `Source` se guarda como `fuente`, pero **no entra al modelo**: hay sitios satíricos que solo aparecen como falsos y usarla sería hacer trampa.

La noticia más larga tiene 25.872 caracteres (4.017 palabras) y el 99,5 % mide menos de 13.600. Eso justifica el límite de 20.000 caracteres de la API (solo 2 noticias lo superan).

## 3. EDA

_(Jairo, PR 3.3.)_

## 4. Decisiones de NLP

_(Brayan, pendiente.)_

## 5. Modelos y experimentos

_(Jairo, PR 3.3.)_

## 6. Evaluación y análisis de errores

_(Jairo, PR 3.3.)_

## 7. Arquitectura, API y frontend

_(Brayan, pendiente.)_

## 8. Conclusiones y limitaciones

_(Brayan, pendiente.)_

## 9. Declaración de uso de asistentes de IA

_(Brayan, pendiente.)_

## 10. Referencias

_(Brayan, pendiente.)_

