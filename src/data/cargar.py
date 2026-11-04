"""Carga y unificación de The Spanish Fake News Corpus (spec 10, contrato C2)."""

import pandas as pd

from src.config import ETIQUETAS, RUTA_DATOS_RAW

# archivo -> año de la versión (v1: ene–jul 2018; v2: nov 2020–mar 2021).
# shortcut: la v2 no trae fecha por noticia, así que toda ella queda como 2021.
ARCHIVOS = {"train.xlsx": 2018, "development.xlsx": 2018, "test.xlsx": 2021}

# La v1 etiqueta con texto ("True"/"Fake") y la v2 con booleanos (True/False).
MAPA_ETIQUETAS = {
    "true": ETIQUETAS[1], "fake": ETIQUETAS[0], "false": ETIQUETAS[0],
}


def cargar_crudo() -> pd.DataFrame:
    """Lee los tres .xlsx y los junta con columnas en minúsculas.

    La v2 trae los encabezados en mayúsculas y "TOPICS" en vez de "Topic":
    sin unificarlos, pd.concat dejaría columnas duplicadas llenas de nulos.
    """
    partes = []
    for archivo, anio in ARCHIVOS.items():
        df = pd.read_excel(RUTA_DATOS_RAW / archivo)
        df.columns = [c.lower() for c in df.columns]
        df = df.rename(columns={"topics": "topic"})
        df["anio"] = anio
        partes.append(df)
    return pd.concat(partes, ignore_index=True)


def limpiar_y_etiquetar(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve las columnas del contrato C2: texto, etiqueta, tema, fuente, anio.

    texto = titular + ". " + cuerpo; si no hay titular (72 noticias de la v2), solo el cuerpo.
    """
    titular = df["headline"].fillna("").astype(str).str.strip()
    cuerpo = df["text"].fillna("").astype(str).str.strip()
    texto = (titular + ". " + cuerpo).where(titular != "", cuerpo)

    etiqueta = df["category"].astype(str).str.strip().str.lower().map(MAPA_ETIQUETAS)
    if etiqueta.isna().any():
        raise ValueError(f"Etiquetas desconocidas: {df.loc[etiqueta.isna(), 'category'].unique()}")

    return pd.DataFrame({
        "texto": texto,
        "etiqueta": etiqueta,
        "tema": df["topic"].astype(str).str.strip(),
        "fuente": df["source"].fillna("desconocida").astype(str).str.strip(),
        "anio": df["anio"].astype(int),
    })
