"""Stop words en español con las negaciones conservadas (spec 20, contrato C3)."""

from functools import lru_cache

from nltk.corpus import stopwords

from src.config import PARAMS
from src.nlp.normalizacion import quitar_tildes


@lru_cache(maxsize=1)
def obtener_stopwords() -> frozenset[str]:
    """NLTK en español, menos params.yaml -> nlp.conservar, más nlp.agregar. Todo sin tildes."""
    base = {quitar_tildes(p) for p in stopwords.words("spanish")}
    conservar = {quitar_tildes(str(p)) for p in PARAMS["nlp"]["conservar"]}
    agregar = {quitar_tildes(str(p)) for p in PARAMS["nlp"]["agregar"]}
    return frozenset((base - conservar) | agregar)


def quitar_stopwords(tokens: list[str]) -> tuple[list[str], list[str]]:
    """Devuelve (tokens_conservados, stopwords_eliminadas).

    Se compara sin tildes para que "está" y "esta" se traten igual.
    Ejemplo: ["no", "hay", "la", "vacuna"] -> (["no", "vacuna"], ["hay", "la"])
    """
    lista = obtener_stopwords()
    conservados, eliminadas = [], []
    for t in tokens:
        (eliminadas if quitar_tildes(t) in lista else conservados).append(t)
    return conservados, eliminadas
