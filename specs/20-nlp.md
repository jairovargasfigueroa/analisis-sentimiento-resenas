# 20 · Pipeline de NLP

- **Enunciado:** sección 5.2. Cada paso se **implementa**, se muestra con un **ejemplo antes/después** y se **justifica**.
- Interfaces: C3, C4 y C5 de `02-contratos.md`.

Está dividida en tres partes para que tres integrantes tengan commits de NLP.

| Parte | Responsable | Rama sugerida | Archivos |
|---|---|---|---|
| A · Normalización, tokenización, stop words y transformer | Integrante 1 | `feat/nlp-normalizacion`, `feat/nlp-stopwords`, `feat/nlp-preprocesador` | `normalizacion.py`, `tokenizacion.py`, `stopwords.py`, `preprocesador.py` |
| B · Stemming y lematización | Integrante 2 | `feat/nlp-raices` | `raices.py` |
| C · Explicación paso a paso | Integrante 4 | `feat/nlp-explicar` | `explicar.py` |

Tests de esta spec: `tests/test_nlp.py`. Cada parte agrega los suyos.

---

## Parte A · Integrante 1

### Normalización: `normalizar(texto) -> str`

Aplicar en este orden y **justificar cada decisión en el informe**:

| Paso | Decisión | Justificación |
|---|---|---|
| URLs (`http…`, `www…`) | eliminar | no aportan sentimiento |
| Menciones y hashtags | quitar `@usuario`; de `#hashtag` conservar la palabra | la palabra del hashtag puede tener sentimiento |
| Emojis | **convertir a palabra** o eliminar; decidir y justificar (por ejemplo, 😍→`emoji_positivo`, 😡→`emoji_negativo`) | los emojis son una señal fuerte de sentimiento |
| Minúsculas | sí | "Bueno" y "bueno" son la misma palabra |
| Tildes | quitar (`unicodedata`), **conservando la ñ** | la gente escribe con y sin tilde; "año" ≠ "ano" |
| Números | eliminar | no indican sentimiento en este dominio; documentar si se decide otra cosa |
| Puntuación | eliminar | el tokenizador trabaja sobre palabras |
| Letras repetidas | reducir a máximo 2 (`buenisimooooo`→`buenisimoo`) | ruido típico de reseñas |
| Espacios múltiples | reducir a uno | limpieza |

### Tokenización: `tokenizar(texto) -> list[str]`

- Por espacios o con una expresión regular `\b\w+\b`. Justificar por qué basta, ya que el texto viene normalizado.
- Mostrar en el informe **casos difíciles del dominio**: palabras pegadas, "x" en lugar de "por", abreviaturas ("q", "xq"), palabras alargadas.

### Stop words: `obtener_stopwords()`, `quitar_stopwords(tokens)`

- Base: `nltk.corpus.stopwords.words("spanish")`, **normalizada igual que el texto** (sin tildes).
- **Quitar de la lista** (es decir, conservarlas): `no`, `ni`, `nunca`, `jamas`, `sin`, `nada`, `muy`, `poco`, `pero`. Justificar: niegan o intensifican el sentimiento.
- **Agregar**, si la EDA lo justifica, palabras del dominio que no aportan (por ejemplo, `restaurante`, `hotel`, `comida`, si aparecen igual en ambas clases).
- Dejar las listas `CONSERVAR` y `AGREGAR` como constantes al inicio del archivo. Esto facilita la **modificación en vivo** ("agregar o quitar una stop word").

### Transformer: `TextPreprocessor` (C4)

- Encadena `normalizar → tokenizar → quitar_stopwords → (stemizar | lematizar | nada) → " ".join`.
- Se puede serializar con joblib (spaCy se carga de forma perezosa).

### Criterios de aceptación (A)
- [ ] Las cuatro funciones o clases cumplen C3/C4 y tienen docstring con un ejemplo antes/después.
- [ ] Tests: URL eliminada, tilde quitada con la ñ conservada, "no" conservado, `TextPreprocessor` se serializa con `joblib.dump`/`load` y da el mismo resultado.

---

## Parte B · Integrante 2

### `stemizar(tokens)` y `lematizar(tokens)`

- **Stemming:** `nltk.stem.SnowballStemmer("spanish")`.
- **Lematización:** spaCy `es_core_news_sm`. Usar `token.lemma_` y normalizar el lema igual que el texto (minúsculas y sin tildes).
- Cargar el modelo de spaCy **una sola vez** (variable de módulo con carga perezosa).
- Mostrar en el informe una tabla de **10 palabras del dataset** con su raíz y su lema (por ejemplo, `gustaron → gust / gustar`).

### Criterios de aceptación (B)
- [ ] Funciones según C3, con tests (`["comiendo"]` → raíz `com…`, lema `comer`).
- [ ] La comparación de **métricas** entre stem y lema la hace P2 en la spec 30 (experimento E1).

---

## Parte C · Integrante 4

### `explicar_preprocesamiento(texto, modo)` (C5)

- Reutiliza las funciones de A y B (**no** reimplementa nada) y devuelve **cada paso intermedio**.
- La API la usa para devolver el campo `preprocesamiento`, y el frontend la muestra.

### Criterios de aceptación (C)
- [ ] Devuelve exactamente las claves de C5.
- [ ] Test: `explicar_preprocesamiento(t, m)["texto_final"] == TextPreprocessor(modo=m).transform([t])[0]` para al menos 5 textos de ejemplo.

---

## TF-IDF (lo configura P2 en `train.py`)

Parámetros documentados en `metricas.json` (C6) y en el informe:

- `ngram_range`: se compara `(1,1)` contra `(1,2)` (experimento E2, spec 30).
- `min_df=2` (descarta palabras que aparecen en un solo documento).
- `max_df=0.9` (descarta palabras presentes en casi todo).
- `max_features`: 20.000 o lo que justifique el tamaño del vocabulario.
- `sublinear_tf=True`.
