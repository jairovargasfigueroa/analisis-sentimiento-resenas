# Reglas para agentes de IA (y para humanos)

Este repositorio es el **Proyecto Integrador – Primer Parcial** de *Tópicos y Programación Avanzada*.
El enunciado original del docente está en `docs/enunciado-proyecto-integrador.pdf`. Ante cualquier duda, **el enunciado manda**.

El proyecto se desarrolla **guiado por especificaciones**: todo lo que hay que construir está en `specs/`.

## Al iniciar cada sesión (obligatorio, antes de cualquier otra cosa)

Haz esto tú mismo, sin esperar a que el integrante lo pida:

1. **Identifica al integrante** con `git config user.name`, `git config user.email` y, si está disponible, `gh api user --jq .login`. Búscalo en esta tabla:

   | Integrante | Usuario GitHub | Parte |
   |---|---|---|
   | Brayan Albaro Garcia Taboada | Alba-Tab | Parte 1 · Predicción (PRs 1.0–1.6, 3.1, 3.2) |
   | Jairo Vargas Figueroa | jairovargasfigueroa | Parte 2 · Análisis y métricas (PRs 2.1–2.3, 3.3) |

   Si no coincide con nadie, o si Git no tiene su identidad configurada, **pregúntale quién es** y ayúdale a configurar `user.name` y `user.email` con su propia cuenta antes de seguir.
2. **Trae lo último:** `git fetch origin` y `git switch main && git pull` (si hay cambios sin commitear en otra rama, primero haz commit o pregunta).
3. **Revisa sus tareas en GitHub Issues.** Cada tarea del plan es un issue asignado a su dueño, con milestone (fase), rama, spec y dependencias. Un issue **cerrado** es una tarea terminada: se cierra solo cuando su PR se integra.
   ```bash
   gh issue list --assignee @me --state open      # sus tareas pendientes
   gh issue view <N>                              # detalle: rama, spec, "Depende de"
   gh issue list --state closed                   # lo que ya terminó todo el equipo
   gh pr list                                     # PR abiertos (en revisión)
   ```
   Si `gh` no está instalado o no tiene sesión, ayúdale a instalarlo y a ejecutar `gh auth login`. Mientras tanto, usa `git log origin/main --merges --oneline` y compara las ramas integradas con las del plan.
4. **Elige la siguiente tarea de ESE integrante**, siguiendo el orden de su parte en `specs/04-plan-de-trabajo.md`:
   - Si tiene una rama de una tarea a medias (`git branch`, o un PR abierto suyo), continúa esa.
   - Si no, toma su primer issue abierto en ese orden.
   - Mira la sección "Depende de" del issue: si alguno sigue **abierto**, no esperes; trabaja con el contrato de `02-contratos.md` y datos simulados, o adelanta su siguiente tarea que no dependa de nada.
   - Si le toca revisar un PR de un compañero (`gh pr list --search "review-requested:@me"`), díselo primero: revisar desbloquea al equipo.
5. **Díselo al integrante** en dos o tres líneas, antes de tocar código: quién es, qué tareas suyas ya están cerradas, cuál toca ahora (issue, rama y spec) y de qué depende. Espera su confirmación.
6. Crea la rama de esa tarea con **el nombre exacto que dice el issue**, desde la rama que indica (los PRs de la Parte 1 van encadenados: cada rama sale de la anterior; los de la Parte 2 salen de `main` actualizado).

## Al terminar una tarea

1. Corre `pytest -q` (si hay tests) y verifica los criterios de aceptación de la spec.
2. Actualiza la rama con su base (`git merge origin/main`, o la rama anterior si es un PR encadenado) y resuelve conflictos si los hay.
3. `git push -u origin <rama>` y abre el PR:
   - Título **`[<número de tarea>] tipo(ámbito): descripción`**, por ejemplo `[1.3] feat(nlp): stop words con negaciones conservadas`. La CI rechaza otro formato.
   - En la descripción, **`Closes #<issue>`**: así el issue se cierra solo al integrar.
   - Apunta a la base correcta y pide la revisión al otro integrante: `gh pr create --base <rama> --reviewer <usuario>`.
4. Espera a que la CI (tests y build) quede en verde. Si falla, corrígelo en la misma rama.
5. Dile al integrante qué tarea sigue.

## Cuando te toca revisar un PR

Si el integrante te pide revisar un PR de un compañero: léelo contra su spec y contratos, pruébalo localmente (`gh pr checkout <N>` y luego `pytest -q`), revisa que la CI esté en verde y redacta comentarios concretos. **El integrante es quien aprueba** (`gh pr review <N> --approve` o desde la web) **y después integra** con "Create a merge commit" (`gh pr merge <N> --merge`). Nunca integres sin aprobar primero.

## Antes de escribir código

1. Lee, en este orden:
   1. `specs/00-vision.md`: qué construimos y por qué.
   2. `specs/01-arquitectura.md`: capas, carpetas y artefactos.
   3. `specs/02-contratos.md`: interfaces compartidas. **No se cambian sin acuerdo del equipo.**
   4. `specs/03-flujo-git.md`: cómo se trabaja con Git y GitHub.
   5. `specs/04-plan-de-trabajo.md`: qué tarea le toca al integrante y en qué orden.
   6. La spec del área en la que trabaja el integrante (`10-` a `60-`).
2. Confirma que la tarea elegida en "Al iniciar cada sesión" es la que el integrante quiere hacer.
3. Verifica que esté en su propia rama (`git branch --show-current`), nunca en `main`.
4. Verifica que Git tenga **su** identidad: `git config user.name` y `git config user.email`.

## Mientras trabajas

- Toca **solo** los archivos que la spec asigna a esa área. Si necesitas algo de otra área, usa lo que define `02-contratos.md`. Si el contrato no alcanza, avisa al integrante para que lo hable con el equipo; no lo cambies por tu cuenta.
- Haz cambios **pequeños**: un commit por idea, no un commit gigante al final.
- Escribe código **simple y explicable**. El integrante debe poder explicar y modificar en vivo cada línea que suba; si no puede explicarla, ese commit no cuenta para su nota.
- Después de cada cambio, explícale al integrante **qué hiciste, por qué y qué alternativas había**. Eso es lo que le van a preguntar en la defensa.
- Usa semilla fija `SEED` (de `src/config.py`) en todo lo aleatorio.
- Los parámetros ajustables (stop words, TF-IDF, grillas de hiperparámetros, límites de la API) se leen de `params.yaml` a través de `src/config.py`. **No los escribas fijos en el código.**
- Si reutilizas código de documentación o de librerías, cita la fuente en un comentario.
- Marca en la checklist de la spec (`- [x]`) lo que quede terminado.

## Commits

- Formato **Conventional Commits** en español: `tipo(ámbito): descripción en imperativo`.
  - Ejemplos: `feat(nlp): conservar negaciones al quitar stop words`, `test(api): validar texto vacío en /predict`.
  - Tipos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `exp` (experimentos).
- El cuerpo del commit explica **qué y por qué**.
- El autor del commit es **el integrante**, con su propia cuenta. No agregues líneas de coautoría de herramientas ni firmes como agente.
- Si dos integrantes trabajaron juntos, agrega `Co-authored-by: Nombre <correo>` del **compañero**.
- El uso de IA se declara una sola vez, en el informe técnico (`docs/informe.md`), como pide el enunciado.

## Proyecto de ejemplo del docente

El docente publicó un ejemplo del mismo tema: <https://github.com/kenjikv/opiniometro>. Sirve como **referencia de qué se espera** (nivel de detalle, documentación, tipo de pruebas), pero:

- **No copies su código.** El enunciado (sección 10) considera plagio copiar un repositorio externo sin atribución, y cada integrante debe poder explicar lo que sube.
- Si una idea concreta viene de ahí, **cítala** en un comentario y en el informe (por ejemplo: "idea de params.yaml tomada del ejemplo del docente").
- Usamos **datos reales**, no sintéticos: el docente lo exige.

## Prohibido

- Hacer commit o push directo a `main`. Todo entra por pull request revisado por otro integrante.
- `git push --force`, `git rebase` sobre `main` o cualquier reescritura de historia compartida.
- Hacer commits con la cuenta o el nombre de otro integrante.
- Reimplementar el preprocesamiento en el backend: el backend **carga** el pipeline serializado.
- Usar el conjunto de prueba para ajustar hiperparámetros o tomar decisiones.
- Subir datasets pesados (más de 50 MB) o credenciales.
