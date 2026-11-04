# 10 · Datos y análisis exploratorio

- **Responsables:** Brayan (carga, PR 1.1) y Jairo (EDA, PR 2.1)
- **Ramas:** `feat/datos-carga`, `exp/eda`
- **Archivos:** `src/data/cargar.py`, `data/`, `notebooks/01_eda.ipynb`, secciones `data`, `labels` y `nlp.agregar` de `params.yaml`
- **Enunciado:** sección 4 (reglas del dataset) y sección 5.1

## Objetivo

Dejar el corpus de noticias limpio con el formato C2 y hacer la EDA que pide el docente.

## Dataset elegido

**The Spanish Fake News Corpus** (versiones 1 y 2; la segunda fue la base de FakeDeS en IberLEF 2021). Datos **reales**, en **español**, etiquetados a mano, licencia **CC BY 4.0**. Se descarga del GitHub de los autores, sin registro.

| Archivo | Período | Noticias | Verdaderas / falsas | Temas principales |
|---|---|---|---|---|
| `train.xlsx` + `development.xlsx` (v1) | ene–jul 2018 | 971 | 491 / 480 | Política, Entretenimiento, Sociedad, Deporte, Ciencia |
| `test.xlsx` (v2) | nov 2020–mar 2021 | 572 | 286 / 286 | COVID-19, Sociedad, Política |

Columnas originales: `Id`, `Category`, `Topic`, `Source`, `Headline`, `Text`, `Link`. Mediana de unas 315 palabras en v1 y 400 en v2 (máximo 2.574 en v1 y 4.017 en v2; la más larga, con titular, tiene 25.872 caracteres). Incluye fuentes de varios países de habla hispana, también Bolivia.

Documentar en `data/raw/README.md`: **nombre, URL, licencia, fecha de obtención, número de registros y columnas originales**.

## Carga y unificación (`src/data/cargar.py`)

```python
def cargar_crudo() -> pd.DataFrame: ...          # lee los tres .xlsx de data/raw
def limpiar_y_etiquetar(df) -> pd.DataFrame: ...  # devuelve columnas C2
def cargar_procesado() -> pd.DataFrame: ...       # lee data/processed/noticias.csv
```

Cuidados (si no se hacen, las métricas salen absurdas):

- La v2 trae los encabezados en mayúsculas (`CATEGORY`, `TOPICS`, …): se unifican los nombres de columna.
- La etiqueta falsa viene como `Fake` en v1 y como `False` en v2. Se mapea a `falsa` / `verdadera` (`True` → `verdadera`).
- `texto = Headline + ". " + Text`. Algunas noticias de la v2 no tienen titular: en ese caso, solo `Text`. En la v1, el `Text` ya empieza con el titular (943 de 971): tampoco se repite.
- `anio`: 2018 para v1; para v2 el año de la noticia (2020 o 2021) si se puede, si no 2021.
- La columna `Source` se guarda como `fuente`, pero **no entra al modelo**: hay sitios satíricos (El Dizque, El Ruinaversal) que solo aparecen como falsos. Usarla sería hacer trampa.
- Eliminar filas con texto vacío y **duplicados exactos**. Reportar cuántas se eliminaron.

## Split

Se juntan las 1.543 noticias y `train.py` hace `train_test_split(test_size=TEST_SIZE, stratify=y, random_state=SEED)`. El conjunto de prueba **no se usa para ajustar nada**.

Experimento extra (E3, opcional): entrenar con 2018 y probar con 2020–21, para medir la generalización en el tiempo. No se usa para elegir nada.

## EDA (`notebooks/01_eda.ipynb`, Jairo)

Debe mostrar, con gráficos y una conclusión escrita en cada caso:

- [ ] Número de registros antes y después de limpiar.
- [ ] **Faltantes** por columna (titulares vacíos de la v2).
- [ ] **Distribución de clases** (barras): confirma que no hace falta `class_weight`.
- [ ] **Longitud de los textos** (palabras y caracteres): histograma por clase y percentiles. Justifica `max_chars` y `min_palabras`.
- [ ] **Palabras más frecuentes** por clase, con y sin stop words. Las que aparecen igual en ambas clases van a `nlp.agregar`.
- [ ] **Temas por clase** y por versión del corpus.
- [ ] **Exclamaciones** por clase: comprueba si el token `exclamacion` tiene sentido.
- [ ] **Hallazgo de las fuentes satíricas**: fuentes que solo publican falsas.

## Criterios de aceptación

- [ ] `data/raw/README.md` con origen, licencia, fecha y tamaño.
- [ ] `data/processed/noticias.csv` cumple C2 y tiene 1.543 filas (menos los duplicados reportados).
- [ ] `python -c "from src.data.cargar import cargar_procesado; print(cargar_procesado().shape)"` funciona.
- [ ] El notebook de EDA se ejecuta de principio a fin sin errores y tiene conclusiones escritas.
