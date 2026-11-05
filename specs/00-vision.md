# 00 · Visión del proyecto

## Problema

Circulan muchas noticias falsas en español por medios digitales, Facebook y WhatsApp, y verificar cada una a mano lleva tiempo.
Hace falta una primera señal rápida: ¿esta noticia parece **falsa o verdadera**, y con qué seguridad?

## Solución

Una aplicación web, **Detector de Noticias Falsas**, en la que el usuario:

1. Pega una noticia, o sube un archivo con varias.
2. Ve si parece **falsa o verdadera**, con su **probabilidad**.
3. Ve **paso a paso** cómo se preprocesó el texto: normalizado, tokens, stop words eliminadas y lemas o raíces.
4. Consulta un **panel de métricas** que compara los dos modelos entrenados.

## Tarea de ML

- **Tipo:** clasificación binaria de texto (`falsa` / `verdadera`).
- **Modelos (dos, como permite el enunciado):**
  - **Regresión Logística**: lineal, da probabilidades y sus coeficientes son interpretables (qué palabras empujan a cada clase). Candidata a producción.
  - **Naive Bayes Multinomial**: el clásico para texto con TF-IDF o conteos; muy rápido y sirve de buen punto de comparación.
- Se comparan, se elige uno para producción y se justifica. También se reporta una **línea base** (predecir siempre la clase mayoritaria).

## Dataset

**The Spanish Fake News Corpus** (versiones 1 y 2; la segunda fue la base de FakeDeS en IberLEF 2021): 1.543 noticias reales, etiquetadas a mano y casi balanceadas (777 verdaderas, 766 falsas), con licencia CC BY 4.0. El detalle está en `specs/10-datos-eda.md`.

## Alcance

**Incluye:** las cinco capas obligatorias (datos, pipeline de NLP, modelos, backend y frontend), un pipeline reproducible, tests, la documentación y la defensa.

**No incluye:** verificar hechos contra fuentes externas (el modelo solo mira el texto), modelos de deep learning, historial con base de datos ni autenticación de usuarios. Docker es opcional y queda para el final si sobra tiempo.

**Limitación conocida:** un clasificador de texto aprende el **estilo** (sátira, sensacionalismo), no la veracidad. Se dice en el informe y se muestra en el análisis de errores.

## Equipo

| Integrante | Usuario GitHub | Parte | Specs |
|---|---|---|---|
| Brayan Albaro Garcia Taboada | @Alba-Tab | Parte 1 · Predicción: datos, pipeline de NLP, modelo base, API de predicción, pestaña Analizar | 10 (carga), 20, 30 (base), 40, 50 (Analizar) |
| Jairo Vargas Figueroa | @jairovargasfigueroa | Parte 2 · Análisis y métricas: EDA, Naive Bayes, GridSearchCV, experimentos, errores, `/metrics` y pestaña Métricas | 10 (EDA), 30 (comparación), 40 (`/metrics`), 50 (Métricas) |

Los dos participan en `60-entrega.md`. **Cada integrante tiene commits de NLP y de ML**, porque el docente preguntará a ambos sobre ello.
