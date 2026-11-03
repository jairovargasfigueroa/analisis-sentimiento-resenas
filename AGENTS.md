# Reglas para agentes de IA (y para humanos)

Este repositorio es el **Proyecto Integrador – Primer Parcial** de *Tópicos y Programación Avanzada*.
El enunciado original del docente está en `docs/enunciado-proyecto-integrador.pdf`. Ante cualquier duda, **el enunciado manda**.

El proyecto se desarrolla **guiado por especificaciones**: todo lo que hay que construir está en `specs/`.

## Antes de escribir código

1. Lee, en este orden:
   1. `specs/00-vision.md`: qué construimos y por qué.
   2. `specs/01-arquitectura.md`: capas, carpetas y artefactos.
   3. `specs/02-contratos.md`: interfaces compartidas. **No se cambian sin acuerdo del equipo.**
   4. `specs/03-flujo-git.md`: cómo se trabaja con Git y GitHub.
   5. `specs/04-plan-de-trabajo.md`: qué tarea le toca al integrante y en qué orden.
   6. La spec del área en la que trabaja el integrante (`10-` a `60-`).
2. Pregunta al integrante **en qué spec va a trabajar** si no lo dijo.
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
