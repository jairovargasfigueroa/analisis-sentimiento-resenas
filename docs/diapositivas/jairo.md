# Diapositivas · Parte de Jairo (EDA, modelos, métricas, errores y conclusiones)

Guion y contenido de cada diapositiva. Van después de la demo de Brayan y se unen con las suyas en `docs/presentacion.pdf`. Tiempo total de esta parte: ~5 minutos.

---

## 7 · Lo que mostró la EDA

**La fuente casi decide la etiqueta.**

- De 347 fuentes, solo 14 publican de las dos clases.
- El 96 % de las falsas viene de sitios que **nunca** publican una verdadera (El Dizque, El Ruinaversal: sátira).
- Por eso la fuente **no entra al modelo**: acertaría sin leer el texto.
- Y se colaba dentro del texto: «bbc» aparece en 26 verdaderas y 0 falsas → las firmas de agencia van como stop words.

> Decir: «medimos que quitarlas no cambia el F1 en validación cruzada, así que preferimos el modelo que no depende de quién firma».

---

## 8 · Dos modelos, elegidos con validación cruzada

| | F1 validación cruzada | F1 prueba |
|---|---|---|
| Línea base | — | 0,336 |
| **Regresión Logística** (C=10) ★ | **0,766 ± 0,006** | **0,773** |
| Naive Bayes (alpha=0,1) | 0,695 ± 0,024 | 0,732 |

- `GridSearchCV`, 5 particiones estratificadas, **solo con train**.
- Se elige por F1 de **validación cruzada**; la prueba se mira una sola vez, al final.
- Naive Bayes pierde porque supone palabras independientes, y con bigramas («no», «no creer») eso no se cumple.

> Si preguntan por qué el test bajó de 0,786 a 0,773: antes se elegía mirando el test. Ahora el test es una medición limpia.

---

## 9 · Qué aporta cada decisión

| Experimento (mismo modelo, cambia una cosa) | Resultado |
|---|---|
| E1 · stem vs **lema** | 0,766 vs 0,766 → lema: igual de preciso y la mitad de variación |
| E2 · unigramas vs **+ bigramas** | 0,760 → 0,766: «no creer», «fuente cercano», «año pasado» |
| E3 · entrenar 2018, probar 2020-21 | **0,643**: el COVID no existía en 2018 |

> E3 es un hallazgo, no un fracaso: el modelo aprende una época y habría que reentrenarlo.

---

## 10 · Pestaña Métricas (demo)

1. Tarjeta del modelo en producción con su justificación.
2. Tabla comparativa y barras de F1.
3. **Matriz de confusión**: 37 falsas pasan como verdaderas y 33 al revés, sin sesgo hacia una clase.
4. Efecto de cada decisión (E1, E2, E3).
5. Palabras más influyentes: cifras y días → verdadera; «revelar», exclamaciones → falsa.
6. Errores con mayor confianza.

---

## 11 · Cuándo se equivoca

| Error | Por qué |
|---|---|
| «Exvicepresidente de Pfizer: no hay necesidad de vacunas» → verdadera 93 % | Falsa con estilo de agencia y cita de autoridad |
| «Forbes afirma que Angélica Rivera…» → verdadera 90 % | El bulo se apoya en un medio real |
| «Feministas protestan frente a Palacio Nacional» → falsa 82 % | Palabra de tema que en el corpus abunda en bulos |
| «Messi: todavía estoy a tiempo de jugar con España» → verdadera 80 % | Sátira escrita como entrevista |

**Falla cuando el estilo engaña.**

---

## 12 · Conclusiones

- Supera a la línea base por **44 puntos** de F1 con dos modelos simples y explicables.
- **Aprende cómo está escrita una noticia, no si es verdad.** Es una primera señal, no un verificador.
- Los datos mandan: la fuente y las firmas filtradas habrían dado un modelo «perfecto» e inútil.
- Se degrada con el tiempo (E3): habría que reentrenarlo con noticias nuevas.
- Reproducible: `python -m src.models.train` da siempre los mismos números (SEED = 42, test incluido).

> Cerrar: «todo lo que vieron sale de `params.yaml`: cambiar una línea y reentrenar con `--rapido` tarda menos de un minuto». Pasa a la modificación en vivo.
