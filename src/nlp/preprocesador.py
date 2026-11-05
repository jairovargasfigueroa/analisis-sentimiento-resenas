"""TextPreprocessor: el preprocesamiento como paso de un Pipeline de sklearn (contrato C4)."""

from functools import lru_cache

from sklearn.base import BaseEstimator, TransformerMixin

from src.nlp.normalizacion import normalizar, quitar_tildes
from src.nlp.raices import lematizar, stemizar
from src.nlp.stopwords import obtener_stopwords, quitar_stopwords
from src.nlp.tokenizacion import tokenizar

MODOS = {"lema": lematizar, "stem": stemizar, "ninguno": lambda tokens: tokens}


def pasos(texto: str, modo: str = "lema", quitar_stop: bool = True) -> dict:
    """Aplica el pipeline y devuelve cada paso intermedio (lo usa también explicar.py).

    El resultado se memoriza: en la validación cruzada cada noticia pasa por 5 particiones y,
    sin caché, se lematizaría 5 veces. La lista de stop words vigente es parte de la clave,
    así que cambiarla (params.yaml, EDA, tests) nunca devuelve un resultado viejo.
    No modificar el dict devuelto: es compartido.
    """
    return _pasos(texto, modo, quitar_stop, obtener_stopwords())


@lru_cache(maxsize=8192)
def _pasos(texto: str, modo: str, quitar_stop: bool, _stopwords: frozenset) -> dict:
    if modo not in MODOS:
        raise ValueError(f"modo debe ser uno de {sorted(MODOS)}, no {modo!r}")
    normalizado = normalizar(texto)
    tokens = tokenizar(normalizado)
    sin_stop, eliminadas = quitar_stopwords(tokens) if quitar_stop else (tokens, [])
    # Las tildes se quitan al final: spaCy las necesita para lematizar ("afirmó" -> "afirmar").
    raices = [quitar_tildes(r) for r in MODOS[modo](sin_stop)]
    return {
        "normalizado": normalizado,
        "tokens": tokens,
        "stopwords_eliminadas": eliminadas,
        "tokens_sin_stopwords": sin_stop,
        "modo": modo,
        "raices_o_lemas": raices,
        "texto_final": " ".join(raices),
    }


class TextPreprocessor(BaseEstimator, TransformerMixin):
    """normalizar -> tokenizar -> quitar stop words -> lema | raíz | nada -> quitar tildes.

    Ejemplo:
        TextPreprocessor("lema").transform(["¡La OMS no aprobó la vacuna!"])
        -> ["exclamacion oms no aprobar vacuna exclamacion"]
    """

    def __init__(self, modo: str = "lema", quitar_stop: bool = True):
        self.modo = modo
        self.quitar_stop = quitar_stop

    def fit(self, X, y=None):
        return self

    def transform(self, X) -> list[str]:
        return [pasos(t, self.modo, self.quitar_stop)["texto_final"] for t in X]
