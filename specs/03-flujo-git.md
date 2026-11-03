# 03 · Flujo de trabajo con Git y GitHub

El docente evalúa la contribución individual **a partir del historial de commits**: lo que no esté en tus commits no cuenta como trabajo tuyo. Estas reglas salen de la sección 6.2 del enunciado.

## Configuración inicial (una sola vez, cada integrante)

```bash
git config --global user.name "Tu Nombre Apellido"
git config --global user.email "el-correo-de-tu-cuenta-github@ejemplo.com"
git clone https://github.com/jairovargasfigueroa/analisis-sentimiento-resenas.git
cd analisis-sentimiento-resenas
```

Comprueba que tus commits salgan con tu cuenta: el correo debe ser uno verificado en tu GitHub.

## Ramas

- `main` está **protegida**: nadie hace push directo, todo entra por pull request.
- Se crea **una rama por funcionalidad**, a partir de `main` actualizado:

```bash
git switch main
git pull
git switch -c feat/nlp-normalizacion
```

Formato del nombre: `tipo/area-descripcion-corta`. Ejemplos: `feat/nlp-stopwords`, `feat/modelos-gridsearch`, `feat/api-predict`, `feat/front-panel-metricas`, `docs/informe-nlp`, `fix/api-cors`.

Las ramas deben ser **cortas**: es mejor abrir varios PR pequeños que uno enorme.

## Commits

Se usa **Conventional Commits**: `tipo(ámbito): qué se hizo`, y en el cuerpo, **por qué**.

```
feat(nlp): conservar "no", "ni", "nunca" y "sin" al quitar stop words

En análisis de sentimiento la negación invierte el significado:
"no me gustó" sin el "no" se vuelve positivo.
```

| tipo | uso |
|---|---|
| `feat` | funcionalidad nueva |
| `fix` | corrección de un error |
| `test` | tests |
| `docs` | documentación, specs o informe |
| `refactor` | reorganizar código sin cambiar comportamiento |
| `exp` | experimentos y comparaciones (notebooks, resultados) |
| `chore` | configuración, dependencias, `.gitignore` |

Reglas:

- Commits **frecuentes y repartidos en el tiempo**. El docente marca como alerta un único commit gigante el último día.
- Un commit = una idea. No mezcles NLP y frontend en el mismo commit.
- Cambios de formato, comentarios o archivos generados **no cuentan** como aporte sustancial.
- Trabajo en pareja: el que hace el commit agrega al final `Co-authored-by: Nombre <correo-github>` del compañero.

## Pull requests

1. Sube tu rama: `git push -u origin feat/nlp-normalizacion`.
2. Abre el PR hacia `main` (`gh pr create` o desde la web). Completa la plantilla.
3. Pide revisión a **otro integrante**, idealmente el que va a consumir tu código.
4. El revisor lee el código, lo prueba y **aprueba** o pide cambios con comentarios concretos.
5. Quien abrió el PR lo integra con **"Create a merge commit"**. No uses "Squash and merge", porque mantener los commits individuales preserva la autoría.
6. Borra la rama después del merge.

Si `main` avanzó mientras trabajabas:

```bash
git switch main
git pull
git switch feat/mi-rama
git merge main      # NO rebase sobre ramas compartidas
```

## Prohibido (sección 6.2 del enunciado)

- `git push --force` o cualquier reescritura de la historia de `main`.
- Commits con la cuenta o el nombre de otra persona.
- Cuentas compartidas.

## Orden sugerido de integración

```
P1: config + cargar datos ─┐
P1: normalizar/tokenizar/stopwords ─┬─► P1: TextPreprocessor ─► P2: train.py ─► P3: API con modelo real ─► P4: frontend con API real
P2: stemizar/lematizar ─────────────┘
P3: API con modelo de prueba (mock) ──────────────────────────────────────────┘
P4: frontend con JSON mock (C8) ──────────────────────────────────────────────────────────────────────────┘
```

Nadie tiene que esperar: con los contratos de `02-contratos.md`, cada uno empieza con datos simulados y conecta lo real cuando está en `main`.

## Entrega

- La versión evaluada es el **último commit de `main` antes de las 23:59 del día anterior a la presentación**.
- Sobre ese commit se crea la etiqueta: `git tag entrega-final` y luego `git push origin entrega-final`.
- En la defensa, la **modificación en vivo** se sube con un commit propio de quien la hace.
