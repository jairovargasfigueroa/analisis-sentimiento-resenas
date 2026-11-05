"""Tokenización (spec 20, contrato C3)."""

import re

PALABRA = re.compile(r"\b\w+\b")


def tokenizar(texto_normalizado: str) -> list[str]:
    """Separa en palabras. Basta una regex porque normalizar() ya quitó puntuación y URLs.

    Ejemplo: "la oms confirmó num casos" -> ["la", "oms", "confirmó", "num", "casos"]
    """
    return PALABRA.findall(texto_normalizado)
