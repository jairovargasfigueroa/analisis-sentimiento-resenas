# 00 · Visión del proyecto

## Problema

Restaurantes, hoteles y tiendas reciben muchas reseñas en español y no pueden leerlas todas.
Necesitan saber rápidamente si una reseña es **positiva o negativa**, y con qué seguridad.

## Solución

Una aplicación web, **Analizador de Sentimiento de Reseñas**, en la que el usuario:

1. Escribe una reseña, o sube un archivo con varias.
2. Ve si es **positiva o negativa**, con su **probabilidad**.
3. Ve **paso a paso** cómo se preprocesó el texto: normalizado, tokens, stop words eliminadas y lemas o raíces.
4. Consulta un **panel de métricas** que compara los dos modelos entrenados.

## Tarea de ML

- **Tipo:** clasificación binaria de texto (`positivo` / `negativo`).
- **Modelos (dos, como permite el enunciado):**
  - **Regresión Logística**: lineal, da probabilidades calibradas y sus coeficientes son interpretables (qué palabras empujan a cada clase).
  - **Naive Bayes Multinomial**: el clásico para texto con TF-IDF o conteos; muy rápido y sirve de buen punto de comparación.
- Se comparan, se elige uno para producción y se justifica. También se reporta una **línea base** (predecir siempre la clase mayoritaria).

## Dataset

Lo define `specs/10-datos-eda.md`. Requisitos:

- Reseñas **en español**, con al menos **1.000 registros etiquetados** o con puntuación de estrellas convertible a etiqueta.
- Se documentan su origen, licencia y fecha de obtención.

## Alcance

**Incluye:** las cinco capas obligatorias (datos, pipeline de NLP, modelos, backend y frontend), un pipeline reproducible, tests, la documentación y la defensa.

**No incluye:** clase neutral (se descartan las reseñas de 3 estrellas, ver spec 10), modelos de deep learning ni autenticación de usuarios. Docker es opcional y queda para el final si sobra tiempo.

## Equipo

| # | Integrante | Usuario GitHub | Área principal | Specs |
|---|---|---|---|---|
| 1 | Jairo Vargas Figueroa | @jairovargasfigueroa | Datos, EDA y NLP base | 10, 20 (parte A) |
| 2 | Brayan Albaro Garcia Taboada | @Alba-Tab | Modelado y experimentos | 20 (parte B), 30 (parte A) |
| 3 | Jovas Josue | @JOVAS45 | Backend, evaluación y tests | 30 (parte B), 40 |
| 4 | Adrian Rosales | @black7in | Frontend y explicación del pipeline | 20 (parte C), 50 |

Todos participan en `60-entrega.md`. **Cada integrante tiene asignada al menos una parte de NLP o ML**, porque el docente preguntará a todos sobre ello.
