# 50 · Frontend

- **Responsable:** Integrante 4
- **Ramas sugeridas:** `feat/front-base`, `feat/front-prediccion`, `feat/front-pasos`, `feat/front-lote`, `feat/front-metricas`
- **Archivos:** todo dentro de `frontend/`
- **Enunciado:** sección 5.6. Consume el contrato **C8**.

## Stack

- **React + Vite** (`npm create vite@latest frontend -- --template react`).
- Gráficos con **Recharts** o Chart.js (elegir uno y justificarlo).
- CSS simple o un framework ligero. Nada pesado.
- La URL de la API sale de `import.meta.env.VITE_API_URL`, con valor por defecto `http://localhost:8000`. Dejar `frontend/.env.example`.
- Todas las llamadas HTTP van en **un solo archivo**, `src/api.js`, con funciones `health()`, `predecir(texto)`, `predecirLote(textos)` y `metricas()`.

## Empezar sin backend

Crear `src/mocks/` con las respuestas de ejemplo de C8 (predict, lote, metrics) y una bandera `VITE_USAR_MOCK=true` para desarrollar la interfaz mientras la API no esté en `main`.

## Vistas y componentes

### 1. Analizar una reseña
- [ ] Área de texto con un contador de caracteres (límite de 5.000) y un botón "Analizar".
- [ ] Botones con **reseñas de ejemplo** (una positiva, una negativa, una con negación, una irónica). Sirven para la demo.
- [ ] Resultado: la **clase** con color (verde o rojo) y la **probabilidad** como barra o medidor (por ejemplo, "Positivo · 94 %").
- [ ] Estado de carga mientras espera y **mensaje de error claro** usando `error.mensaje` de la API.

### 2. Preprocesamiento paso a paso (exigido por el docente)
Con el campo `preprocesamiento` (C5), mostrar en orden:
- [ ] Texto original → **normalizado**.
- [ ] **Tokens** (como etiquetas o "chips").
- [ ] **Stop words eliminadas**, resaltadas o tachadas.
- [ ] **Lemas o raíces**, indicando qué modo se usó.
- [ ] Texto final que entra a TF-IDF.

### 3. Análisis por lote
- [ ] Subir un `.txt` (una reseña por línea) o un `.csv` (columna `texto`), leído en el navegador.
- [ ] Tabla de resultados (texto, clase, probabilidad) y un gráfico de resumen (positivas vs negativas).
- [ ] Validar en el cliente: archivo vacío o más de 100 reseñas.

### 4. Panel de métricas
Con `GET /metrics` (C6):
- [ ] Tarjeta del **modelo en producción** con su justificación.
- [ ] **Tabla comparativa** baseline vs Regresión Logística vs Naive Bayes (accuracy, precision, recall, F1).
- [ ] **Gráfico de barras** comparando el F1 de los tres.
- [ ] **Matriz de confusión** del modelo en producción (tabla de 2×2 coloreada).
- [ ] Resultados de los experimentos E1 (stem vs lema) y E2 (n-gramas).

### 5. Indicador de estado
- [ ] Un punto verde o rojo en la cabecera según `GET /health`.

> Posible modificación en vivo: "mostrar un dato nuevo de la API" o "cambiar una visualización". Mantén los componentes pequeños, uno por archivo, en `src/components/`.

## Criterios de aceptación
- [ ] `npm install && npm run dev` levanta en http://localhost:5173.
- [ ] Las cinco vistas funcionan contra la API real.
- [ ] Ninguna lógica de NLP o ML en el frontend: solo muestra lo que devuelve la API.
- [ ] `frontend/README.md` breve, con los comandos.
