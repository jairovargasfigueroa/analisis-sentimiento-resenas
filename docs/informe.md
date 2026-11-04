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

El pipeline completo es un `TextPreprocessor` dentro de un `sklearn.Pipeline` (`prep → tfidf → clf`), serializado con joblib. **La API carga ese mismo Pipeline**, así que el preprocesamiento al predecir es exactamente el del entrenamiento. Los parámetros (stop words, modo, n-gramas) se leen de `params.yaml`.

```
normalizar (con tildes) → tokenizar → quitar stop words → lematizar | stemizar → quitar tildes
```

Ejemplo real de punta a punta, con modo `lema`:

| Paso | Resultado |
|---|---|
| Original | `¡¡ALERTA!! La OMS confirmó que *NUMBER* niños murieron tras la vacuna 😱 https://x.co/abc @salud #NoALaVacuna` |
| Normalizado | `exclamacion alerta exclamacion la oms confirmó que num niños murieron tras la vacuna emoji noalavacuna` |
| Stop words eliminadas | `la`, `que`, `la` |
| Lemas, sin tildes | `exclamacion alerta exclamacion oms confirmar num niño morir tras vacuna emoji noalavacun` |
| Con stemming | `exclam alert exclam oms confirm num niñ mur tras vacun emoji noalavacun` |

### 4.1 Normalización

| Paso | Decisión | Justificación |
|---|---|---|
| URLs y `@menciones` | Eliminar | No indican veracidad por sí mismas |
| `#hashtag` | Conservar la palabra | La v2 incluye posts de redes; la palabra puede aportar |
| Marcadores de la v1 | `*NUMBER*`, `*PHONE*` → `num`; `*URL*` → nada | Que la v1 y la v2 queden iguales (sección 2) |
| `¡` y `!` | Cada grupo → token `exclamacion` | El tono sensacionalista es típico de la noticia falsa |
| Emojis | Token `emoji` | Aparecen en posts de Facebook y WhatsApp |
| Minúsculas | Sí | "Gobierno" y "gobierno" son la misma palabra |
| Números | Token `num` | La cifra exacta no generaliza; cuántas cifras trae el texto sí puede ser señal |
| Puntuación | Eliminar (después de las exclamaciones) | El tokenizador trabaja sobre palabras |
| Letras repetidas | Máximo 2 (`graveeeee` → `gravee`) | Ruido típico de redes |
| Tildes | **No** se quitan aquí; se quitan al final, conservando la ñ | spaCy las necesita (4.4); "año" ≠ "ano" |

Alternativa descartada: borrar exclamaciones y emojis, porque se pierde la señal del tono.

### 4.2 Tokenización

Expresión regular `\b\w+\b` sobre el texto ya normalizado. Basta porque la puntuación, las URLs y los emojis ya se resolvieron. Casos difíciles del dominio:

- **Siglas con puntos** ("EE. UU.") quedan como `ee uu`.
- **Cifras con puntos** ("1.543") se resuelven antes: pasan a `num`.
- **Hashtags pegados** ("#NoALaVacuna") quedan como una sola palabra, `noalavacuna`, que luego ni el lematizador ni el stemmer saben partir.
- **Nombres propios compuestos** ("Andrés Manuel López Obrador") se separan en palabras; los bigramas de TF-IDF recuperan parte de esa unión.

### 4.3 Stop words

Base: NLTK en español (313 palabras). Se **conservan las negaciones** `no`, `ni`, `nunca`, `sin` y `tampoco`, porque «no hay vacuna» y «hay vacuna» afirman lo contrario. Sin ellas y con las tildes unificadas, la lista queda en 303. La comparación se hace sin tildes ("está" y "esta" se tratan igual). Las dos listas (`nlp.conservar` y `nlp.agregar`) están en `params.yaml`.

Ensayo (detalle en `docs/modificaciones_en_vivo.md`): quitar "no" de las conservadas baja el F1 de 0,786 a 0,776.

### 4.4 Stemming y lematización

- **Stemming:** `SnowballStemmer("spanish")`. Corta por reglas, es rápido y no necesita modelo, pero deja raíces que no son palabras.
- **Lematización:** spaCy `es_core_news_sm`, que devuelve la forma de diccionario.

| Palabra | Raíz (Snowball) | Lema (spaCy) |
|---|---|---|
| afirmó | afirm | afirmar |
| confirmaron | confirm | confirmar |
| vacunas | vacun | vacuna |
| murieron | mur | morir |
| niños | niñ | niño |
| presidente | president | presidente |
| declaraciones | declar | declaracion |
| informó | inform | informar |
| contagios | contagi | contagio |
| sociedad | socied | sociedad |

**Por qué las tildes se quitan al final:** spaCy lematiza «afirmó» como «afirmar», pero «afirmo» sin tilde como **«afirmoir»**. Por eso el orden es lematizar primero y quitar tildes después; un test lo fija.

**Pronombres pegados:** con «permitirlo» spaCy devuelve dos palabras («permitir él»). Se deja solo el verbo para que no se cuele un pronombre que además es stop word.

spaCy se carga una sola vez y vive en el módulo `raices.py`, no dentro del `TextPreprocessor`, así que no entra al pickle del modelo.

Con la configuración actual, el lema da F1 0,786 y el stemming 0,770. La comparación formal con validación cruzada es el experimento E1 (sección 5).

### 4.5 TF-IDF

`ngram_range (1, 2)`, `min_df 2`, `max_df 0,90`, `max_features 20000`, `sublinear_tf true`, todos desde `params.yaml → tfidf`. Con unigramas solos el F1 baja a 0,764: los pares de palabras (por ejemplo, una negación con su verbo) aportan información. La comparación formal es el experimento E2.

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

