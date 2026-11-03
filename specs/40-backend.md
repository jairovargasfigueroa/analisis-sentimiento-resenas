# 40 · Backend (API REST)

- **Responsable:** Integrante 3
- **Ramas sugeridas:** `feat/api-base`, `feat/api-predict`, `feat/api-validaciones`, `test/api`
- **Archivos:** `api/main.py`, `api/esquemas.py`, `tests/test_api.py`
- **Enunciado:** sección 5.5. Contrato: **C8** de `02-contratos.md`.

## Framework: FastAPI

Justificación para el informe:

- Valida entradas automáticamente con Pydantic.
- Genera la documentación interactiva sola (`/docs` con Swagger y `/redoc`), lo que cubre el requisito de "documentación de los endpoints".
- Es rápido y tiene un cliente de pruebas integrado.

## Reglas clave

- El modelo se carga **una sola vez al iniciar** (evento `lifespan`), con `cargar_modelo()` de C7.
- **No se reimplementa el preprocesamiento:** la predicción usa el `Pipeline` cargado, y el detalle paso a paso usa `explicar_preprocesamiento()` (C5).
- Si el modelo no existe, la API **arranca igual**: `/health` responde 503 y `/predict` devuelve `MODELO_NO_DISPONIBLE`.
- CORS habilitado para `http://localhost:5173`.

## Mientras no exista el modelo real

Para no bloquearse, se puede entrenar un modelo de prueba pequeño con datos inventados o con lo que ya esté en `main`, sin subir ese artefacto. También se puede probar con un `Pipeline` falso en los tests (fixture de pytest).

## Endpoints (C8)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio y del modelo |
| POST | `/predict` | Una reseña → clase, probabilidad y preprocesamiento |
| POST | `/predict/lote` | Varias reseñas → resultados y resumen |
| GET | `/metrics` | Contenido de `models/metricas.json` |

## Validaciones (con el formato de error de C8)

- [ ] Texto vacío o solo espacios → `TEXTO_VACIO`.
- [ ] Más de `LONGITUD_MAX_TEXTO` caracteres → `TEXTO_DEMASIADO_LARGO`.
- [ ] JSON mal formado, campo faltante o tipo incorrecto → `FORMATO_INVALIDO`. Se sobrescribe el manejador de `RequestValidationError` para usar el formato propio.
- [ ] Lote vacío o mayor a `MAX_TEXTOS_LOTE` → `LOTE_INVALIDO`.

Los mensajes de error deben ser **claros y en español**.

> Posible modificación en vivo: "rechazar textos de menos de 3 palabras". Deja las validaciones en una función o en un validador de Pydantic fácil de extender.

## Documentación

- Cada endpoint con `summary`, `description` y un **ejemplo** en el esquema Pydantic (`json_schema_extra`).
- Sección "API" en el README con un ejemplo `curl` por endpoint.

## Tests (`tests/test_api.py`, con `TestClient`)

- [ ] `/health` → 200 y `modelo_cargado: true`.
- [ ] `/predict` con una reseña positiva → 200, con todas las claves de C8.
- [ ] `/predict` con texto vacío → 422 `TEXTO_VACIO`.
- [ ] `/predict` con texto demasiado largo → 422 `TEXTO_DEMASIADO_LARGO`.
- [ ] `/predict` sin el campo `texto` → 422 `FORMATO_INVALIDO`.
- [ ] `/predict/lote` con 3 textos → 3 resultados y resumen correcto.
- [ ] `/metrics` → 200, con las claves `modelo_produccion` y `modelos`.

Se ejecutan con `pytest -q`.

## Criterios de aceptación
- [ ] `uvicorn api.main:app --reload` levanta y `/docs` muestra los 4 endpoints con ejemplos.
- [ ] Todos los tests pasan.
- [ ] El backend no contiene lógica de normalización, stop words ni TF-IDF propia.
