# Diapositivas · Parte de Brayan (problema, datos, NLP y demo)

Guion y contenido de cada diapositiva. Se unen con las de Jairo (6 a 11: EDA, modelos, métricas, errores y conclusiones) en `docs/presentacion.pdf`. Tiempo total de esta parte: ~5 minutos.

---

## 1 · Problema

**¿Esta noticia parece falsa?**

- Circulan noticias falsas en español por medios digitales, Facebook y WhatsApp.
- Verificar cada una a mano es lento.
- Objetivo: una **primera señal rápida**, falsa o verdadera con su probabilidad, y mostrar **cómo** se procesó el texto.

> Decir: «el modelo no verifica hechos, juzga el texto». Se retoma en las conclusiones.

---

## 2 · Datos y formato del corpus

**The Spanish Fake News Corpus** · CC BY 4.0 · etiquetado a mano

| | Período | Noticias | Verdaderas / falsas |
|---|---|---|---|
| v1 | 2018 | 971 | 491 / 480 |
| v2 (FakeDeS 2021) | 2020–21 | 572 | 286 / 286 |

- 1.542 noticias después de quitar 1 duplicado: **balanceado**, sin `class_weight`.
- Split estratificado 80/20 con SEED = 42 → 1.233 / 309.
- La **fuente no entra al modelo**: hay sitios satíricos que solo publican falsas.

**Las dos versiones no tienen el mismo formato.**

- v1 repite el titular dentro del cuerpo (943 de 971).
- v1 anonimiza cifras y enlaces: `*NUMBER*`, `*URL*`; v2 trae los reales.
- Sin igualarlo, el modelo aprende **de qué año es** la noticia, no si es falsa.
- Corregirlo bajó el F1 de 0,796 a **0,786**: ese punto era falso.

---

## 3 · Pipeline de NLP

```
normalizar → tokenizar → stop words → lematizar → quitar tildes → TF-IDF → modelo
```

`¡¡ALERTA!! La OMS confirmó que 3 niños murieron 😱 https://…`
→ `exclamacion alerta exclamacion oms confirmar num niño morir emoji`

- Exclamaciones y emojis se vuelven **tokens**: el tono sensacionalista es señal.
- Se **conservan las negaciones**: «no hay vacuna» ≠ «hay vacuna» (sin «no», el F1 baja 1 punto).
- Todo va en **un solo Pipeline** serializado: la API usa exactamente el mismo preprocesamiento.

---

## 4 · La decisión que más cuesta explicar: las tildes

| Palabra | Lema |
|---|---|
| afirmó | **afirmar** ✓ |
| afirmo (sin tilde) | **afirmoir** ✗ |

- spaCy necesita las tildes → se lematiza **antes** de quitarlas.
- Snowball une «murieron» y «muro» en `mur`. Con validación cruzada, lema y stem empatan (E1, diapositiva 8); queda lema por estabilidad y legibilidad.

---

## 5 · Demo en vivo

1. Mostrar la cabecera: **punto verde** (`/health`).
2. Botón **«Falsa 2021»** → *Parece falsa* (~90 % con el modelo final).
3. Bajar al **paso a paso**: stop words tachadas, lemas, entrada a TF-IDF.
4. Borrar texto hasta dejar menos de 20 palabras → el botón se desactiva; por `curl`, la API responde `TEXTO_DEMASIADO_CORTO`.
5. Pasar a Jairo: pestaña **Métricas**.

Plan B si algo falla: tener `uvicorn` y `npm run dev` levantados antes de empezar, y el `curl` de `docs/api.md` a mano.
