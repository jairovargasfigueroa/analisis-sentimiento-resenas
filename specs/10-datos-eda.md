# 10 · Datos y análisis exploratorio

- **Responsable:** Integrante 1 (Jairo)
- **Ramas sugeridas:** `feat/datos-carga`, `exp/eda`
- **Archivos:** `src/config.py`, `src/data/cargar.py`, `data/`, `notebooks/01_eda.ipynb`
- **Enunciado:** sección 4 (reglas del dataset) y sección 5.1

## Objetivo

Conseguir un dataset de reseñas en español, documentarlo, dejarlo limpio con el formato C2 y hacer la EDA que pide el docente.

## Elección del dataset

Criterios:

- En **español**.
- **Al menos 1.000 reseñas** etiquetadas, o con estrellas. Lo ideal es tener entre 3.000 y 20.000 para que entrene rápido.
- Licencia que permita uso académico.
- Que se pueda descargar sin pasos manuales complicados.

Candidatos (**verificar disponibilidad y licencia** antes de elegir):

- Reseñas de restaurantes u hoteles en español (Kaggle o Hugging Face Datasets, buscar "spanish reviews", "reseñas tripadvisor español").
- Reseñas de películas en español con puntuación (por ejemplo, el corpus *muchocine*).
- Reseñas de productos en español con estrellas.

Documentar en `data/README.md`: **nombre, URL, licencia, fecha de descarga, número de registros y columnas originales**.

Si el archivo pesa más de 50 MB, no se sube: en su lugar se crea `src/data/descargar.py`, que lo descarga.

## Etiquetado

Si el dataset trae estrellas de 1 a 5:

- 1–2 → `negativo`
- 4–5 → `positivo`
- 3 → **se descarta** (es ambiguo). Hay que justificarlo en el informe.

## Limpieza (`src/data/cargar.py`)

```python
def cargar_crudo() -> pd.DataFrame: ...          # lee data/raw
def limpiar_y_etiquetar(df) -> pd.DataFrame: ...  # devuelve columnas C2
def cargar_procesado() -> pd.DataFrame: ...       # lee data/processed/resenas.csv
```

- Eliminar filas con texto nulo o vacío, y **duplicados exactos**. Reportar cuántas se eliminaron.
- Guardar el resultado en `data/processed/resenas.csv` (C2).

## EDA (`notebooks/01_eda.ipynb`)

Debe mostrar, con gráficos y una conclusión escrita en cada caso:

- [ ] Número de registros antes y después de limpiar.
- [ ] **Valores faltantes** por columna.
- [ ] **Distribución de clases** (barras) y, si hay estrellas, distribución de estrellas.
- [ ] **Longitud de los textos** (en palabras y en caracteres): histograma por clase y percentiles. Esto justifica `LONGITUD_MAX_TEXTO`.
- [ ] **Palabras más frecuentes** por clase, con y sin stop words (barras o nube de palabras).
- [ ] Conclusión sobre el **desbalance**: si la clase minoritaria es menor al 40 %, proponer un tratamiento (`class_weight="balanced"` o submuestreo) y avisar a P2.
- [ ] Ejemplos de textos difíciles: ironía, negaciones, emojis, URLs, faltas de ortografía. Estos sirven de insumo para la spec 20.

## Split

El split lo **hace `train.py` (P2)**, no la EDA, para que sea reproducible. Se usa `train_test_split(test_size=0.2, stratify=y, random_state=SEED)`.

El conjunto de prueba **no se usa para ajustar nada**.

## Criterios de aceptación

- [ ] `src/config.py` creado según C1.
- [ ] `data/README.md` con origen, licencia, fecha y tamaño.
- [ ] `data/processed/resenas.csv` cumple C2 y tiene al menos 1.000 filas.
- [ ] `python -c "from src.data.cargar import cargar_procesado; print(cargar_procesado().shape)"` funciona.
- [ ] El notebook de EDA se ejecuta de principio a fin sin errores y tiene conclusiones escritas.
