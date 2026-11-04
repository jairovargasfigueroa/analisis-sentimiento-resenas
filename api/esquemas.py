"""Esquemas de request/response y formato de error único de la API (contrato C8)."""

from pydantic import BaseModel, Field

EJEMPLO = (
    "El Ministerio de Salud informó este lunes que la campaña de vacunación contra la "
    "influenza comenzará la próxima semana en todos los centros de salud del país, "
    "con prioridad para adultos mayores y niños menores de cinco años."
)


class ErrorAPI(Exception):
    """Error con el formato único {"error": {"codigo", "mensaje"}}."""

    def __init__(self, codigo: str, mensaje: str, status: int = 422):
        self.codigo, self.mensaje, self.status = codigo, mensaje, status


class EntradaPrediccion(BaseModel):
    texto: str = Field(description="Noticia completa: titular y cuerpo.",
                       json_schema_extra={"example": EJEMPLO})


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
