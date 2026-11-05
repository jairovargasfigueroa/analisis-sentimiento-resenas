# Informe técnico · Detector de Noticias Falsas en Español

Proyecto Integrador · Primer Parcial · *Tópicos y Programación Avanzada*.
Integrantes: Brayan Albaro Garcia Taboada (@Alba-Tab) y Jairo Moises Vargas Figueroa (@jairovargasfigueroa).

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

El análisis completo está en `notebooks/01_eda.ipynb` (secciones 1 a 10), ejecutado y con sus salidas. Resumen de lo que se encontró y de qué se decidió con cada hallazgo:

| Pregunta | Hallazgo | Decisión |
|---|---|---|
| ¿Cuánto se pierde al limpiar? | 1 duplicado de 1.543 noticias; ningún texto vacío | — |
| ¿Faltantes? | 72 titulares vacíos, **todos de la v2**; 7 fuentes y 3 enlaces | Si falta el titular se usa solo el cuerpo (`cargar.py`) |
| ¿Clases balanceadas? | 765 falsas (49,6 %) y 777 verdaderas; también en cada versión | Sin `class_weight` ni sobremuestreo; split estratificado |
| ¿Longitudes? | Las falsas son más cortas: mediana de 283 palabras frente a 436. La más corta tiene 28 palabras; solo 2 superan los 20.000 caracteres | `min_palabras: 20` y `max_chars: 20000` en la API |
| ¿Qué palabras distinguen? | Con stop words, las 15 más frecuentes son iguales en las dos clases. Sin ellas, separa el **estilo**: «puntualizó», «reveló», «verdad», «nadie», «pueblo» en falsas; fechas, cifras escritas, «destacó», «indicó», «instituto» en verdaderas | Quitar stop words; el modelo aprende estilo |
| ¿Temas? | En cada tema hay entre 40 % y 60 % de falsas: el corpus está emparejado por tema. La v2 está dominada por COVID-19 (237 noticias), que no existe en la v1 | El tema no es un atajo; se mide la época con E3 |
| ¿Exclamaciones? | 15,3 % de las falsas tienen al menos una, frente al 8,8 % de las verdaderas | Se conservan como el token `exclamacion` |
| ¿Fuentes? | De 347 fuentes, solo 14 publican de las dos clases. El 96 % de las falsas (735 de 765) viene de fuentes que nunca publican una verdadera, sobre todo sitios satíricos (*El Dizque*, 143; *El Ruinaversal*, 94) | `fuente` **no entra** al modelo: con ella acertaría sin leer el texto |
| ¿La fuente se cuela en el texto? | Las firmas de agencia aparecen casi solo en verdaderas: «bbc» 26/0, «reuters» 8/0, «afp» 7/0, «notimex» 3/0 | `nlp.agregar: [bbc, afp, efe, reuters, notimex]` |

**Stop words del dominio.** Se midió el efecto de agregar las firmas de agencia con validación cruzada de 5 particiones sobre train: F1 macro 0,7631 sin ellas y 0,7623 con ellas. La diferencia es mucho menor que el desvío entre particiones (0,013), así que es ruido. A igual rendimiento se prefiere el modelo que no depende de quién firma la noticia. Las palabras comunes a ambas clases («así», «solo») no se agregaron porque bajan el F1 (receta B1).

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

### 5.1 Por qué estos dos modelos

TF-IDF produce vectores **dispersos** de hasta 20.000 dimensiones con solo 1.233 noticias de entrenamiento. Con tantas columnas y tan pocas filas, los modelos lineales y probabilísticos funcionan bien, entrenan en segundos y se pueden explicar. Árboles, Random Forest o XGBoost tienden a sobreajustar en este escenario y no aprovechan la dispersión.

- **Regresión Logística.** Calcula una suma ponderada de los pesos TF-IDF de la noticia, *z = w·x + b*, y la pasa por la sigmoide, *p = 1 / (1 + e^(-z))*, que da la probabilidad de «verdadera». Los pesos *w* se aprenden minimizando la pérdida logarítmica (log-loss) con regularización L2. `C` es la **inversa** de la regularización: un `C` chico obliga a pesos pequeños (modelo simple) y uno grande deja que algunos términos pesen mucho. Cada coeficiente dice cuánto empuja un término hacia una clase, por eso el modelo es interpretable (sección 6.3).
- **Naive Bayes multinomial.** Aplica el teorema de Bayes: *P(clase | noticia) ∝ P(clase) · Π P(término | clase)*. Es «naive» porque supone que los términos son **independientes** entre sí dada la clase. `alpha` es el **suavizado de Laplace**: suma `alpha` a cada conteo para que un término no visto en una clase no anule toda la probabilidad.

### 5.2 Búsqueda de hiperparámetros

`GridSearchCV` con `StratifiedKFold` de 5 particiones barajadas con `SEED = 42`, `scoring="f1_macro"` y solo con el conjunto de entrenamiento. El pipeline completo (`prep → tfidf → clf`) se clona en cada partición, así TF-IDF aprende el vocabulario sin ver la partición de validación. Las grillas salen de `params.yaml → experiments.models`.

Para que la búsqueda no lematice cada partición una vez por combinación, el `Pipeline` usa `memory`: guarda en una carpeta temporal la salida de `prep` y `tfidf`, que no cambian cuando solo cambia el clasificador. Con 200 noticias la búsqueda de los dos modelos bajó de 74 s a 22 s con los mismos resultados. Además, `pasos()` memoriza el preprocesamiento de cada noticia (la clave incluye la lista de stop words vigente), porque en la validación cruzada cada noticia aparece en 5 particiones. Con las dos cachés, el entrenamiento completo con los experimentos tarda unos 80 s (antes ~7 minutos), y `python -m src.models.train --rapido`, sin E1, E2 ni E3, unos 45 s: suficiente para una modificación en vivo.

**El modelo de producción se elige por el F1 de validación cruzada, no por el de prueba.** Si se eligiera mirando el test, el test dejaría de ser una medición independiente. Por eso el F1 de prueba bajó de 0,786 (modelo base del PR 1.3, elegido sin CV) a 0,773: no empeoró el modelo, mejoró la honestidad de la medición.

### 5.3 Tabla comparativa

| Modelo | Mejor hiperparámetro | F1 macro CV (train) | Accuracy test | F1 macro test |
|---|---|---|---|---|
| Línea base (siempre la mayoritaria) | — | — | 50,5 % | 0,336 |
| **Regresión Logística** ★ | `C = 10` | **0,766 ± 0,006** | **77,3 %** | **0,773** |
| Naive Bayes | `alpha = 0,1` | 0,695 ± 0,024 | 73,5 % | 0,732 |

- Los dos superan con holgura a la línea base: el texto tiene señal.
- **Regresión Logística gana** en CV (y también en test, aunque eso no participa en la decisión). Naive Bayes queda 7 puntos atrás en CV: su supuesto de independencia se rompe con unigramas + bigramas («no» y «no creer» están muy correlacionados), mientras que la Regresión Logística reparte el peso entre términos correlacionados.
- El mejor `C` es alto (poca regularización): con 20.000 términos, el modelo necesita pesos grandes en pocos términos muy informativos. El mejor `alpha` es bajo por la misma razón: los términos raros pero muy asociados a una clase son los que informan.

### 5.4 Experimentos

Mismo modelo y mismos hiperparámetros; cambia **un solo** parámetro. F1 macro de validación cruzada en train.

| Experimento | Opciones | F1 CV | Decisión |
|---|---|---|---|
| **E1** · reducción de palabras | stem: 0,7658 ± 0,015 · **lema: 0,7663 ± 0,006** | empate | Se mantiene **lema**: igual de preciso, la mitad de variación entre particiones, y sus términos son palabras reales (legibles en el paso a paso y en las palabras influyentes). Costo: es más lento que Snowball |
| **E2** · n-gramas | (1,1): 0,760 ± 0,020 · **(1,2): 0,766 ± 0,006** | +0,6 puntos | Se mantienen los **bigramas**. Capturan negaciones y expresiones: «no creer», «no saber», «fuente cercano» pesan hacia falsa; «num mil», «año pasado» hacia verdadera |
| **E3** · otra época | entrenar con 2018 (970) y probar con 2020-21 (572) | F1 **0,643** | No decide nada: mide un riesgo. Cae 12 puntos porque la v2 habla de COVID-19, que no existía en 2018 |

E1 y E2 confirman la configuración de `params.yaml` (`nlp.modo: lema`, `tfidf.ngram_range: [1, 2]`). E3 muestra que el modelo aprende el estilo **y los temas de una época**: para usarlo con noticias nuevas habría que reentrenarlo periódicamente.

## 6. Evaluación y análisis de errores

Todo sobre el conjunto de prueba (309 noticias), que no se usó para decidir nada. Detalle en el notebook (secciones 12, 15 y 16) y en la pestaña **Métricas** de la app.

### 6.1 Matriz de confusión (Regresión Logística)

| | predicho falsa | predicho verdadera |
|---|---|---|
| **real falsa** (153) | 116 (75,8 %) | 37 (24,2 %) |
| **real verdadera** (156) | 33 (21,2 %) | 123 (78,8 %) |

| Clase | Precision | Recall | F1 |
|---|---|---|---|
| falsa | 0,779 | 0,758 | 0,768 |
| verdadera | 0,769 | 0,789 | 0,779 |

Los errores están **repartidos** entre las dos direcciones (37 y 33): el modelo no está sesgado hacia una clase, coherente con un corpus balanceado. El error más costoso en la práctica es la primera fila: **37 falsas pasan como verdaderas** (recall de «falsa» de 75,8 %). Entre los 10 errores más seguros, 7 son de ese tipo.

### 6.2 Línea base

Predecir siempre «verdadera» (la mayoritaria en train) acierta el 50,5 % pero tiene F1 macro 0,336, porque nunca detecta una falsa. La Regresión Logística la supera por 44 puntos de F1: el modelo aporta valor real, como pide el enunciado (5.3).

### 6.3 Palabras más influyentes

Coeficientes de la Regresión Logística (lemas):

- Hacia **verdadera**: cifras («dos», «cinco», el token `num`), días y referencias temporales («lunes», «martes», «pasado», «año») y palabras de crónica («centro», «evento», «proceso»). Es el lenguaje de agencia.
- Hacia **falsa**: tono y apelación («revelar», el token `exclamacion`, «pueblo», «gente», «nadie», «pues», «no»), y también **palabras de tema** («virus», «amlo», «feminista») que en este corpus abundan en bulos. Esto último es un sesgo del corpus, no una regla general, y explica parte de los errores.

### 6.4 Cinco errores explicados

Los cinco errores salen de los 10 en que el modelo estaba más seguro (`metricas.json → errores_ejemplo`), elegidos por mostrar causas distintas:

1. **Falsa con estilo de agencia y cita de autoridad** («Exvicepresidente de Pfizer: no hay necesidad de vacunas», 93 % verdadera). Titular con cita textual, un cargo con nombre, sin exclamaciones: los rasgos que el modelo asocia con «verdadera». Lo falso es el contenido, y el modelo no verifica hechos.
2. **Falsa que se apoya en un medio real** («Forbes afirma que Angélica Rivera está en la lista de millonarios», 90 % verdadera). Atribuye la información a *Forbes*, nombra a una columnista y da detalles concretos. Citar fuentes y dar cifras es típico de las verdaderas: el bulo toma prestada la credibilidad.
3. **Verdadera con un tema que suena a bulo** («Líder religioso que culpó a los homosexuales del coronavirus dio positivo», *Milenio*, 84 % falsa). COVID-19, una figura polémica, una situación irónica y «controversia en redes sociales»: todo lo que abunda entre las falsas.
4. **Verdadera arrastrada por una palabra de tema** («Feministas protestan frente a Palacio Nacional», *El Universal*, 82 % falsa). «feminista» es uno de los términos con más peso hacia falsa porque en el entrenamiento aparece sobre todo en bulos políticos. Es un sesgo de tema aprendido de un corpus pequeño.
5. **Sátira escrita como entrevista** («Messi: todavía estoy a tiempo de jugar con la selección española», *Hay noticia*, 80 % verdadera). Imita una entrevista deportiva y cita un medio real. Lo absurdo es evidente para quien sabe de fútbol, no para una bolsa de palabras que no sabe quién es Messi.

**Patrón.** El modelo acierta cuando el estilo delata a la noticia y falla cuando el estilo engaña: falsas bien redactadas y verdaderas sobre temas que suelen ser bulos. Hay casos, como las cifras oficiales de homicidios en Cali etiquetadas como falsas, que solo se resolverían contrastando el dato con otra fuente, algo fuera del alcance de un clasificador de texto.

## 7. Arquitectura, API y frontend

```
ENTRENAMIENTO · python -m src.models.train
data/raw/*.xlsx → cargar.py → noticias.csv → split 80/20 (SEED=42)
                                   │
          Pipeline([prep: TextPreprocessor, tfidf: TfidfVectorizer, clf: LogisticRegression])
                                   ▼
               models/modelo_produccion.joblib + models/metricas.json

USO · cada consulta
frontend (React, :5173) ──JSON──► API (FastAPI, :8000) ──joblib.load al iniciar──► predict_proba
                         ◄── clase, probabilidades y preprocesamiento paso a paso ──┘
```

### API (`api/`)

| Endpoint | Qué devuelve |
|---|---|
| `GET /health` | Estado, si el modelo cargó y su nombre (503 si no hay modelo) |
| `POST /predict` | `falsa`/`verdadera`, la probabilidad de cada clase y el preprocesamiento paso a paso |
| `GET /metrics` | `metricas.json` completo (Jairo, PR 2.3) |

- **FastAPI** porque valida las entradas con Pydantic y genera la documentación sola en `/docs`.
- El modelo se carga **una vez** al iniciar (`lifespan`). Si no existe, la API arranca igual y responde 503 en vez de caerse.
- **No reimplementa el preprocesamiento**: predice con el Pipeline cargado y el paso a paso sale de `explicar_preprocesamiento()`, que usa la misma función que `TextPreprocessor`.
- **Validaciones** con un formato de error único `{"error": {"codigo", "mensaje"}}`: `TEXTO_VACIO`, `TEXTO_DEMASIADO_CORTO` (menos de 20 palabras: con menos no hay base para decidir), `TEXTO_DEMASIADO_LARGO` (más de 20.000 caracteres), `FORMATO_INVALIDO` y `MODELO_NO_DISPONIBLE`. Los límites salen de `params.yaml`.
- CORS habilitado solo para el frontend.
- Endpoints y ejemplos `curl` en `docs/api.md`. Cada código de error tiene su test.

### Frontend (`frontend/`)

React + Vite, con versiones fijas. Se tomó del ejemplo del docente (Opiniómetro) la **estructura** de pestañas y el indicador de estado, no su código.

- **Cabecera**: punto verde o rojo según `GET /health`, consultado cada 10 s.
- **Analizar**: caja de texto con contador, 4 noticias de ejemplo del conjunto de prueba (una falsa y una verdadera de cada época), resultado con su probabilidad y el **paso a paso**: original → normalizado → tokens con las stop words tachadas → sin stop words → lemas → entrada a TF-IDF.
- **Métricas**: Jairo, PR 2.3.
- El frontend no tiene lógica de NLP: solo muestra lo que devuelve la API. Todas las llamadas HTTP están en `src/api.js`.

## 8. Conclusiones y limitaciones

Desde la parte de datos y NLP (Brayan):

- **El modelo aprende estilo, no veracidad.** Las señales que más ayudan (exclamaciones, tono, temas) son de forma. Una noticia falsa bien escrita o una verdadera alarmista lo engañan.
- **Las diferencias de formato entre versiones del corpus contaminan el modelo** si no se igualan. Dos de ellas valían un punto de F1.
- **Pocos datos** (1.542 noticias): por eso modelos lineales y validación cruzada, no modelos más complejos.

Desde la parte de modelos y métricas (Jairo):

- **El modelo funciona y es honesto.** La Regresión Logística llega a F1 0,766 en validación cruzada y 0,773 en prueba, 44 puntos por encima de la línea base. Se eligió sin mirar el test, así que ese 0,773 es una estimación limpia de cómo rinde con noticias nuevas del mismo tipo.
- **Los atajos estaban en los datos, no en el modelo.** La fuente decide casi sola la etiqueta y las firmas de agencia la filtraban dentro del texto. Un modelo que las usara tendría números mejores y sería inútil con una noticia de una fuente desconocida.
- **Se degrada con el tiempo** (E3: de 0,766 a 0,643 entrenando con 2018 y probando con 2020-21). En producción habría que reentrenarlo periódicamente con noticias nuevas.
- **Falla cuando el estilo engaña:** falsas bien redactadas que citan medios o autoridades, y verdaderas sobre temas que en el corpus abundan en bulos. Es una primera señal para priorizar qué verificar, no un verificador.
- **Trabajo futuro:** más datos y más recientes, ajustar el umbral de decisión (el AUC de 0,835 indica que el modelo ordena mejor de lo que sugiere su accuracy) y contrastar las afirmaciones con fuentes externas.

## 9. Declaración de uso de asistentes de IA

**Brayan:** usé Claude (Anthropic), a través de Claude Code, como asistente durante todo el desarrollo de la Parte 1 (datos, pipeline de NLP, modelo base, API, frontend y README) y de esta documentación. Me ayudó a redactar código, tests, specs, mensajes de commit y estos textos, y a revisar el corpus. Por ejemplo, señaló el titular repetido y los marcadores `*NUMBER*` de la v1. Revisé cada cambio, corrí los tests y ensayé las modificaciones en vivo con los números que figuran en `docs/modificaciones_en_vivo.md`. Las decisiones de diseño y su justificación están en este informe y en los mensajes de commit, y puedo explicarlas.

**Jairo:** usé Claude (Anthropic), a través de Claude Code, como asistente en la organización del repositorio (specs, reglas para agentes, issues y CI), en la revisión de los PRs de Brayan y en toda la Parte 2: el notebook de EDA y experimentos, `evaluacion.py`, `experimentos.py`, los cambios de `train.py`, el endpoint `/metrics`, la pestaña Métricas, esta documentación y los mensajes de commit. Revisé cada cambio, corrí los tests y el entrenamiento, comprobé en el navegador la pestaña Métricas contra la API real, y los números de este informe y de las recetas J1 a J3 salen de ejecuciones reales. Las decisiones y su justificación están en el informe y en los commits, y puedo explicarlas y modificarlas.

## 10. Referencias

- Posadas-Durán, J. P., Gómez-Adorno, H., Sidorov, G., & Escobar, J. J. M. (2019). Detection of fake news in a new corpus for the Spanish language. *Journal of Intelligent & Fuzzy Systems*, 36(5), 4869-4876.
- Gómez-Adorno, H., Posadas-Durán, J. P., Enguix, G. B., & Capetillo, C. P. (2021). Overview of FakeDeS at IberLEF 2021: Fake News Detection in Spanish Shared Task. *Procesamiento del Lenguaje Natural*, 67, 223-231.
- Librerías: scikit-learn, NLTK, spaCy (`es_core_news_sm`), FastAPI, React, Vite.
- Ejemplo del docente: [Opiniómetro](https://github.com/kenjikv/opiniometro) (estructura de pestañas e idea de `params.yaml`).
