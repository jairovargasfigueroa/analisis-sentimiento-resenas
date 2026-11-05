"""Explicación paso a paso del preprocesamiento para la API y el frontend (contrato C5)."""

from src.nlp.preprocesador import pasos


def explicar_preprocesamiento(texto: str, modo: str = "lema") -> dict:
    """Devuelve el texto original y cada paso intermedio con las claves de C5.

    Usa la misma función que TextPreprocessor, así "texto_final" siempre coincide con lo
    que recibe TF-IDF.
    """
    return {"original": texto, **pasos(texto, modo)}
