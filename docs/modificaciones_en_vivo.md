# Modificaciones en vivo (recetas ensayadas)

Cada receta dice qué se cambia, el comando para reentrenar, los números antes y después y cómo leerlos.

- **B1 a B5** (Brayan) se ensayaron el 2026-11-04 con el modelo base del PR 1.3: Regresión Logística sin búsqueda de hiperparámetros, F1 0,786.
- **J1 a J3** (Jairo) se ensayaron el 2026-11-05 con el entrenamiento final del PR 2.2.

**Punto de partida actual:** Regresión Logística `C = 10`, elegida por validación cruzada, modo `lema`, `ngram_range [1, 2]` → **F1 CV 0,766 · F1 test 0,773**. Línea base: F1 0,336. Con el modelo nuevo cambian los números absolutos de B1 a B4, pero la dirección del efecto y la forma de leerlo se mantienen.

```bash
python -m src.models.train --rapido   # ~45 s: búsqueda de los dos modelos, sin E1, E2 ni E3
python -m src.models.train            # ~80 s: completo, con E1, E2 y E3
```

Después de reentrenar, reiniciar uvicorn para que la API cargue el modelo nuevo.

---

## Brayan · datos, NLP y API

### B1. Agregar stop words del dominio

**Qué se cambia** (`params.yaml`):

```yaml
nlp:
  agregar: [asi, ahora, solo, mismo]
```

Se eligieron porque aparecen en la misma proporción de noticias falsas y verdaderas (por ejemplo, «así» en el 38 % de las falsas y el 37 % de las verdaderas), así que en principio no ayudan a distinguir.

| | accuracy | F1 macro |
|---|---|---|
| Antes | 0,786 | 0,786 |
| Después | 0,777 | 0,776 |

**Cómo leerlo:** baja 1 punto. Que una palabra aparezca igual en las dos clases no significa que no aporte: combinada con otras en los bigramas sí puede ayudar. Por eso `agregar` queda vacío y la decisión final se toma con la EDA (Jairo, experimento E4).

### B2. Quitar «no» de las negaciones conservadas

**Qué se cambia** (`params.yaml`):

```yaml
nlp:
  conservar: [ni, nunca, sin, tampoco]    # sin "no": NLTK lo elimina como stop word
```

| | accuracy | F1 macro |
|---|---|---|
| Antes | 0,786 | 0,786 |
| Después | 0,777 | 0,776 |

**Cómo leerlo:** baja 1 punto. Confirma la decisión de conservar las negaciones: «no hay vacuna» y «hay vacuna» dicen lo contrario y, sin el «no», el modelo las ve iguales.

### B3. Cambiar lematización por stemming

**Qué se cambia** (`params.yaml`):

```yaml
nlp:
  modo: stem       # antes: lema
```

| | accuracy | F1 macro | tiempo de entrenamiento |
|---|---|---|---|
| Lema (spaCy) | 0,786 | 0,786 | ~25 s |
| Stem (Snowball) | 0,770 | 0,770 | ~10 s |

**Cómo leerlo:** el stemming es más rápido pero pierde 1,6 puntos. Une palabras distintas («mur» sirve para *murieron* y *muro*) y deja raíces que no son palabras. El lema conserva la forma de diccionario (*murieron* → *morir*). La comparación formal con validación cruzada es el experimento E1 de Jairo.

### B4. Cambiar el rango de n-gramas

**Qué se cambia** (`params.yaml`):

```yaml
tfidf:
  ngram_range: [1, 1]     # antes: [1, 2]
```

| | accuracy | F1 macro |
|---|---|---|
| Unigramas + bigramas | 0,786 | 0,786 |
| Solo unigramas | 0,764 | 0,764 |

**Cómo leerlo:** sin bigramas baja 2,2 puntos. Los pares de palabras (una negación con su verbo, nombres compuestos) aportan información que las palabras sueltas no tienen.

### B5. Agregar o endurecer una validación de la API

**Qué se cambia** (`params.yaml`), sin tocar código:

```yaml
api:
  min_palabras: 30        # antes: 20
```

Reiniciar uvicorn (no hace falta reentrenar) y probar con una noticia de 25 palabras:

```bash
curl -X POST localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"texto": "El Ministerio de Salud informó este lunes que la campaña de vacunación contra la influenza comenzará la próxima semana en todos los centros de salud."}'
```

| `min_palabras` | Respuesta |
|---|---|
| 20 | `200` · `verdadera` |
| 30 | `422` · `TEXTO_DEMASIADO_CORTO` · «La noticia debe tener al menos 30 palabras.» |

**Para una validación nueva** (por ejemplo, rechazar textos que sean solo una URL), se agrega un `if` en `validar_texto()` de `api/esquemas.py` con su propio código de error, y un caso en `tests/test_api.py`.

---

## Jairo · modelos y métricas

Ensayadas el 2026-11-05 sobre el entrenamiento final (PR 2.2), con el mismo split. Para cambios en las grillas o en `evaluacion.py` alcanza con `--rapido` (~45 s); el entrenamiento completo tarda ~80 s.

**Regla para interpretar:** se decide con el **F1 de validación cruzada** (columna «F1 CV»), no con el de prueba. Con 309 noticias de prueba, una diferencia de un punto puede ser ruido.

### J1. Cambiar `C` de la Regresión Logística (más regularización)

**Qué se cambia** (`params.yaml`):

```yaml
experiments:
  models:
    regresion_logistica:
      C: [0.1]            # antes: [0.1, 1.0, 10.0, 30.0]
```

```bash
python -m src.models.train --rapido
```

| `C` | F1 CV | F1 test | Falsas que pasan como verdaderas |
|---|---|---|---|
| 10 (antes, elegido por la búsqueda) | 0,766 ± 0,006 | 0,773 | 37 de 153 |
| 0,1 | 0,738 ± 0,020 | 0,746 | 48 de 153 |

**Cómo leerlo:** `C` es la inversa de la regularización. Con `C = 0,1` los pesos se achican tanto que el modelo pierde términos informativos: **subajusta**. Baja casi 3 puntos y deja pasar 11 falsas más. Sigue en producción porque supera a Naive Bayes (0,695 en CV).

**Pregunta probable: ¿por qué no `C = 1`, si en prueba da más?** Con `C = 1` el F1 de prueba es 0,786, mayor que el 0,773 de `C = 10`, pero en validación cruzada da 0,762 frente a 0,766. Se elige por CV porque el test no puede participar en la decisión: si se eligiera por test, se estaría ajustando el modelo a esas 309 noticias, y la diferencia (1 punto) está dentro del ruido.

### J2. Cambiar `alpha` de Naive Bayes (más suavizado)

**Qué se cambia** (`params.yaml`):

```yaml
experiments:
  models:
    naive_bayes:
      alpha: [1.0]        # antes: [0.05, 0.1, 0.5, 1.0]
```

| `alpha` | F1 CV | F1 test | Matriz de confusión `[[falsa→falsa, falsa→verdadera], [verdadera→falsa, verdadera→verdadera]]` |
|---|---|---|---|
| 0,1 (antes) | 0,695 | 0,732 | `[[97, 56], [26, 130]]` |
| 1,0 | 0,676 | 0,670 | `[[69, 84], [12, 144]]` |

**Cómo leerlo:** `alpha` es el suavizado de Laplace: suma `alpha` a cada conteo. Con `alpha = 1` los términos raros, que justamente son los más asociados a una clase, pierden peso y las probabilidades se aplanan. El modelo se inclina hacia «verdadera»: deja pasar **84** falsas. El modelo de producción no cambia (sigue la Regresión Logística); el efecto se ve en la fila de Naive Bayes de la pestaña **Métricas**.

### J3. Agregar una métrica: exactitud balanceada y AUC ROC

**Qué se cambia** (`src/models/evaluacion.py`, función `evaluar`):

```python
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

    proba = modelo.predict_proba(X)[:, list(modelo.classes_).index(ETIQUETAS[1])]
    return {
        ...,
        "balanced_accuracy": round(balanced_accuracy_score(y, pred), 4),
        "roc_auc": round(roc_auc_score([v == ETIQUETAS[1] for v in y], proba), 4),
    }
```

Para verla en la interfaz, en `frontend/src/components/ComparacionModelos.jsx` se agrega una columna `<th>AUC</th>` y `<td>{pct(m.roc_auc)}</td>`. Reentrenar con `--rapido` y reiniciar uvicorn.

| Métrica (Regresión Logística, prueba) | Valor |
|---|---|
| Accuracy | 0,773 |
| Exactitud balanceada | 0,773 |
| **AUC ROC** | **0,835** |
| AUC ROC de la línea base | 0,5 (no ordena nada) |

**Cómo leerlo:**

- La **exactitud balanceada** es el promedio del recall de cada clase. Aquí coincide con la accuracy porque el corpus está balanceado; con clases desbalanceadas, la accuracy engañaría y esta no.
- El **AUC ROC** mide si el modelo **ordena** bien: la probabilidad de que una verdadera al azar reciba más puntaje que una falsa al azar. 0,835 es mejor que lo que sugiere la accuracy: el modelo separa bastante bien las clases, y parte de los errores se deben al umbral de 0,5. Moverlo (por ejemplo, exigir 0,6 para decir «verdadera») cambiaría cuántas falsas pasan.

### Otras variantes rápidas

- **N-gramas en la búsqueda:** el rango de producción se cambia en `tfidf.ngram_range` (receta B4). La comparación formal con validación cruzada es el experimento E2 (`experiments.ngram_ranges`), y requiere el entrenamiento completo.
- **Forzar Naive Bayes en producción:** dejar `regresion_logistica.C: [0.001]`. La regularización es tan fuerte que la Regresión Logística predice siempre la misma clase (F1 CV 0,335, igual que la línea base), queda por debajo de Naive Bayes (0,695) y el script pone a Naive Bayes en producción **sin tocar código**. Muestra que la elección depende de la búsqueda, no de una preferencia.
