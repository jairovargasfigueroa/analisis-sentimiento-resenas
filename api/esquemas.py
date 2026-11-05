"""Esquemas de request/response y formato de error único de la API (contrato C8)."""

from pydantic import BaseModel, Field

from src.config import LONGITUD_MAX_TEXTO, MAX_TEXTOS_LOTE, MIN_PALABRAS_TEXTO

EJEMPLO = (
    "El Ministerio de Salud informó este lunes que la campaña de vacunación contra la "
    "influenza comenzará la próxima semana en todos los centros de salud del país, "
    "con prioridad para adultos mayores y niños menores de cinco años."
)


class ErrorAPI(Exception):
    """Error con el formato único {"error": {"codigo", "mensaje"}}."""

    def __init__(self, codigo: str, mensaje: str, status: int = 422):
        self.codigo, self.mensaje, self.status = codigo, mensaje, status


def validar_texto(texto: str) -> str:
    """Rechaza textos vacíos, demasiado cortos o demasiado largos. Fácil de extender en vivo."""
    if not texto.strip():
        raise ErrorAPI("TEXTO_VACIO", "El texto no puede estar vacío.")
    if len(texto.split()) < MIN_PALABRAS_TEXTO:
        raise ErrorAPI("TEXTO_DEMASIADO_CORTO",
                       f"La noticia debe tener al menos {MIN_PALABRAS_TEXTO} palabras.")
    if len(texto) > LONGITUD_MAX_TEXTO:
        raise ErrorAPI("TEXTO_DEMASIADO_LARGO",
                       f"La noticia no puede superar los {LONGITUD_MAX_TEXTO} caracteres.")
    return texto


def validar_lote(textos: list[str]) -> list[str]:
    """Rechaza el lote entero si está vacío, es demasiado grande o alguna noticia no es válida.

    El mensaje dice qué noticia falla ("Noticia 3: ...") para que se pueda corregir el archivo.
    """
    if not 1 <= len(textos) <= MAX_TEXTOS_LOTE:
        raise ErrorAPI("LOTE_INVALIDO",
                       f"El lote debe tener entre 1 y {MAX_TEXTOS_LOTE} noticias (tiene {len(textos)}).")
    for i, texto in enumerate(textos, start=1):
        try:
            validar_texto(texto)
        except ErrorAPI as e:
            raise ErrorAPI("LOTE_INVALIDO", f"Noticia {i}: {e.mensaje}") from e
    return textos


class EntradaPrediccion(BaseModel):
    texto: str = Field(description="Noticia completa: titular y cuerpo.",
                       json_schema_extra={"example": EJEMPLO})


class EntradaLote(BaseModel):
    textos: list[str] = Field(description=f"Entre 1 y {MAX_TEXTOS_LOTE} noticias completas.",
                              json_schema_extra={"example": [EJEMPLO, EJEMPLO]})


class ResultadoLote(BaseModel):
    texto: str
    clase: str
    probabilidad: float
    probabilidades: dict[str, float]


class PrediccionLote(BaseModel):
    resultados: list[ResultadoLote]
    resumen: dict[str, int] = Field(json_schema_extra={"example": {"falsa": 1, "verdadera": 1}})


class Preprocesamiento(BaseModel):
    original: str
    normalizado: str
    tokens: list[str]
    stopwords_eliminadas: list[str]
    tokens_sin_stopwords: list[str]
    modo: str
    raices_o_lemas: list[str]
    texto_final: str


class Prediccion(BaseModel):
    clase: str = Field(json_schema_extra={"example": "verdadera"})
    probabilidad: float = Field(json_schema_extra={"example": 0.94})
    probabilidades: dict[str, float] = Field(
        json_schema_extra={"example": {"falsa": 0.06, "verdadera": 0.94}})
    modelo: str = Field(json_schema_extra={"example": "regresion_logistica"})
    preprocesamiento: Preprocesamiento


class Estado(BaseModel):
    status: str = Field(json_schema_extra={"example": "ok"})
    modelo_cargado: bool
    modelo: str | None = Field(json_schema_extra={"example": "regresion_logistica"})
    version: str = Field(json_schema_extra={"example": "1.0.0"})
