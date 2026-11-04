# Datos originales: The Spanish Fake News Corpus

| Campo | Valor |
|---|---|
| Nombre | The Spanish Fake News Corpus, versiones 1.0 y 2.0 (la 2.0 fue la base de FakeDeS en IberLEF 2021) |
| URL | <https://github.com/jpposadas/FakeNewsCorpusSpanish> |
| Licencia | CC BY 4.0 (uso académico permitido citando a los autores) |
| Fecha de obtención | 2026-11-04 |
| Registros | 1.543 noticias: 777 verdaderas y 766 falsas |
| Etiquetado | Manual, por los autores, contrastando con sitios de verificación (fact-checking) |

## Archivos

| Archivo | Versión | Período | Noticias | Verdaderas / falsas | Etiqueta |
|---|---|---|---|---|---|
| `train.xlsx` | 1.0 | ene–jul 2018 | 676 | 338 / 338 | `True` / `Fake` (texto) |
| `development.xlsx` | 1.0 | ene–jul 2018 | 295 | 153 / 142 | `True` / `Fake` (texto) |
| `test.xlsx` | 2.0 | nov 2020–mar 2021 | 572 | 286 / 286 | `True` / `False` (booleano) |

## Columnas originales

- v1: `Id`, `Category`, `Topic`, `Source`, `Headline`, `Text`, `Link`.
- v2: las mismas en mayúsculas, y `Topic` se llama `TOPICS`. Faltan 72 titulares, 7 fuentes y 3 enlaces; 90 de las falsas son posts de Facebook y WhatsApp.

`src/data/cargar.py` unifica los tres archivos en `data/processed/noticias.csv` (contrato C2).

## Cómo citar

1. Gómez-Adorno, H., Posadas-Durán, J. P., Enguix, G. B., & Capetillo, C. P. (2021). Overview of FakeDeS at IberLEF 2021: Fake News Detection in Spanish Shared Task. *Procesamiento del Lenguaje Natural*, 67, 223-231.
2. Posadas-Durán, J. P., Gómez-Adorno, H., Sidorov, G., & Escobar, J. J. M. (2019). Detection of fake news in a new corpus for the Spanish language. *Journal of Intelligent & Fuzzy Systems*, 36(5), 4869-4876.
