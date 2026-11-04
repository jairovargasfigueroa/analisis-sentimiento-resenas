# 20 · Pipeline de NLP

- **Responsable:** Brayan (PR 1.2, rama `feat/nlp-pipeline`). Jairo ajusta las stop words del dominio según la EDA (PR 2.1) y hace el experimento E4 (opcional).
- **Archivos:** `src/nlp/normalizacion.py`, `tokenizacion.py`, `stopwords.py`, `raices.py`, `preprocesador.py`, `explicar.py`
- **Enunciado:** sección 5.2. Cada paso se **implementa**, se muestra con un **ejemplo antes/después** y se **justifica**.
- Interfaces: C3, C4 y C5 de `02-contratos.md`. Tests: `tests/test_nlp.py`.

## Orden del pipeline

```
normalizar (con tildes) → tokenizar → quitar stop words → lematizar | stemizar → quitar tildes → " ".join
```

spaCy necesita las tildes para lematizar bien: «afirmó» → «afirmar», pero «afirmo» sin tilde puede quedar como primera persona. Por eso las tildes se quitan **al final**, sobre el lema o la raíz.

## Normalización: `normalizar(texto) -> str`

Aplicar en este orden y **justificar cada decisión en el informe**:

| Paso | Decisión | Justificación |
|---|---|---|
| URLs (`http…`, `www…`) | eliminar | no indican veracidad por sí mismas |
| Menciones y hashtags | quitar `@usuario`; de `#hashtag` conservar la palabra | la v2 incluye posts de Facebook y WhatsApp |
| `!` y `¡` | cada grupo seguido → token `exclamacion` | el tono sensacionalista es típico de la noticia falsa (se comprueba en la EDA) |
| Emojis | token `emoji` | aparecen en los posts de redes |
| Minúsculas | sí | "Gobierno" y "gobierno" son la misma palabra |
| Números | token `num` | las cifras exactas no generalizan, pero cuántas cifras trae el texto sí puede ser señal |
| Puntuación | eliminar (después de las exclamaciones) | el tokenizador trabaja sobre palabras |
| Letras repetidas | máximo 2 (`graveeeee` → `gravee`) | ruido típico de redes |
| Espacios múltiples | reducir a uno | limpieza |
| Tildes | **no** se quitan aquí; `quitar_tildes()` se aplica al final, conservando la ñ | ver "Orden del pipeline"; "año" ≠ "ano" |

## Tokenización: `tokenizar(texto) -> list[str]`

- Expresión regular `\b\w+\b` sobre el texto normalizado. Justificar por qué basta.
- Casos difíciles del dominio para el informe: siglas (OMS, EE. UU.), cifras con puntos (1.543), hashtags pegados (#QuédateEnCasa), nombres propios compuestos.

## Stop words: `obtener_stopwords()`, `quitar_stopwords(tokens)`

- Base: `nltk.corpus.stopwords.words("spanish")`.
- **Conservar** las de `params.yaml → nlp.conservar`: las negaciones (`no`, `ni`, `nunca`, `sin`, `tampoco`). «no hay vacuna» y «hay vacuna» afirman cosas opuestas.
- **Agregar** las de `params.yaml → nlp.agregar`: palabras que la EDA muestre iguales en ambas clases.
- Las listas se leen de `params.yaml` (vía `src/config.PARAMS`), **no se escriben fijas en el código**. Así la modificación en vivo "agregar o quitar una stop word" es cambiar una línea y reentrenar.

## Raíces y lemas: `stemizar(tokens)`, `lematizar(tokens)`

- **Stemming:** `nltk.stem.SnowballStemmer("spanish")`.
- **Lematización:** spaCy `es_core_news_sm`, `token.lemma_` en minúsculas.
- Cargar spaCy **una sola vez** (variable de módulo con carga perezosa).
- Tabla para el informe con **10 palabras del corpus**, su raíz y su lema (por ejemplo, `afirmó → afirm / afirmar`).
- La comparación de métricas stem vs lema es el experimento E1 (spec 30).

## Transformer: `TextPreprocessor` (C4)

- Encadena los pasos en el orden de arriba. `modo ∈ {"lema", "stem", "ninguno"}`.
- Se serializa con joblib: spaCy se carga de forma perezosa y se excluye en `__getstate__`.

## Explicación paso a paso: `explicar_preprocesamiento(texto, modo)` (C5)

- Reutiliza las mismas funciones (**no** reimplementa nada) y devuelve cada paso intermedio.
- La API la usa para el campo `preprocesamiento`, y el frontend la muestra.

## TF-IDF (lo configura `train.py`)

Los parámetros salen de `params.yaml → tfidf` y se documentan en `metricas.json` (C6) y en el informe:

- `ngram_range`: `(1,1)` contra `(1,2)` (experimento E2).
- `min_df: 2`, `max_df: 0.90`, `max_features: 20000`, `sublinear_tf: true`.

## Criterios de aceptación

- [ ] Las funciones y clases cumplen C3, C4 y C5 y tienen docstring con un ejemplo antes/después.
- [ ] Tests: URL eliminada, ñ conservada, «no» conservado, «afirmó» se lematiza a «afirmar», `TextPreprocessor` se serializa con joblib y da el mismo resultado.
- [ ] Test: `explicar_preprocesamiento(t, m)["texto_final"] == TextPreprocessor(modo=m).transform([t])[0]` para al menos 5 textos.
