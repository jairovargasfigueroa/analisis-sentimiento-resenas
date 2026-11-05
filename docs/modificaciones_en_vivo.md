# Modificaciones en vivo (recetas ensayadas)

Cada receta dice qué se cambia, el comando para reentrenar, los números antes y después y cómo leerlos. Todas se ensayaron el 2026-11-04 sobre el mismo split (SEED = 42, 309 noticias de prueba).

Punto de partida: Regresión Logística, modo `lema`, `ngram_range [1, 2]` → **accuracy 0,786 · F1 macro 0,786**. Línea base: F1 0,336.

```bash
python -m src.models.train      # reentrena e imprime la tabla; ~25 s con lema, ~10 s con stem
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

_(PR 3.3: cambiar `C` o `alpha`, cambiar el rango de n-gramas en el GridSearch, agregar una métrica nueva.)_
