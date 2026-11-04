"""Raíces (stemming) y lemas (spec 20, contrato C3)."""

from nltk.stem import SnowballStemmer

_stemmer = SnowballStemmer("spanish")


def stemizar(tokens: list[str]) -> list[str]:
    """Corta cada palabra a su raíz por reglas. Rápido y sin modelo, pero la raíz puede no ser una palabra.

    Ejemplo: ["confirmaron", "vacunas"] -> ["confirm", "vacun"]
    """
    return [_stemmer.stem(t) for t in tokens]


# spaCy se carga la primera vez que se usa (tarda ~1 s) y queda en el módulo, no en el
# TextPreprocessor: así no entra al pickle del modelo.
_nlp = None


def _spacy():
    global _nlp
    if _nlp is None:
        import spacy

        _nlp = spacy.load("es_core_news_sm", disable=["parser", "ner"])
    return _nlp


def lematizar(tokens: list[str]) -> list[str]:
    """Devuelve la forma de diccionario de cada palabra. Necesita las tildes: "afirmó" -> "afirmar".

    Se arma el Doc con nuestros tokens para que spaCy no los vuelva a separar (1 lema por token).
    Ejemplo: ["afirmó", "vacunas"] -> ["afirmar", "vacuna"]
    """
    if not tokens:
        return []
    from spacy.tokens import Doc

    nlp = _spacy()
    doc = Doc(nlp.vocab, words=tokens)
    for _, paso in nlp.pipeline:
        doc = paso(doc)
    # Con pronombre pegado spaCy da dos palabras ("permitirlo" -> "permitir él"): se deja el verbo.
    return [(t.lemma_.lower().split() or [t.text.lower()])[0] for t in doc]
