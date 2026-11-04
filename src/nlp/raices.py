"""Raíces (stemming) y lemas (spec 20, contrato C3)."""

from nltk.stem import SnowballStemmer

_stemmer = SnowballStemmer("spanish")


def stemizar(tokens: list[str]) -> list[str]:
    """Corta cada palabra a su raíz por reglas. Rápido y sin modelo, pero la raíz puede no ser una palabra.

    Ejemplo: ["confirmaron", "vacunas"] -> ["confirm", "vacun"]
    """
    return [_stemmer.stem(t) for t in tokens]
