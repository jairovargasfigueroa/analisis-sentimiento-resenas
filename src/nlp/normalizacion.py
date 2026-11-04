"""Normalización del texto de una noticia (spec 20, contrato C3)."""

import re
import unicodedata

import emoji

URL = re.compile(r"https?://\S+|www\.\S+")
MENCION = re.compile(r"@\w+")
HASHTAG = re.compile(r"#(\w+)")
EXCLAMACION = re.compile(r"[!¡]+")
NUMERO = re.compile(r"\d+(?:[.,]\d+)*")
PUNTUACION = re.compile(r"[^\w\s]|_")
REPETIDAS = re.compile(r"(\w)\1{2,}")
ESPACIOS = re.compile(r"\s+")


def normalizar(texto: str) -> str:
    """Limpia el texto sin quitar tildes (spaCy las necesita para lematizar).

    Ejemplo:
        "¡¡URGENTE!! La OMS confirmó 3 casos 😱 https://x.com"
        -> "exclamacion urgente exclamacion la oms confirmó num casos emoji"
    """
    t = URL.sub(" ", texto)
    t = MENCION.sub(" ", t)
    t = HASHTAG.sub(r" \1 ", t)
    # Exclamaciones y emojis se vuelven tokens: el tono sensacionalista puede ser señal.
    t = EXCLAMACION.sub(" exclamacion ", t)
    t = emoji.replace_emoji(t, replace=" emoji ")
    t = t.lower()
    t = NUMERO.sub(" num ", t)
    t = PUNTUACION.sub(" ", t)
    t = REPETIDAS.sub(r"\1\1", t)
    return ESPACIOS.sub(" ", t).strip()


def quitar_tildes(texto: str) -> str:
    """Quita tildes y diéresis conservando la ñ ("año" no es "ano").

    Ejemplo: "afirmó que el niño" -> "afirmo que el niño"
    """
    t = texto.replace("ñ", "\0").replace("Ñ", "\1")
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return t.replace("\0", "ñ").replace("\1", "Ñ")
