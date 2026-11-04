"""Carga y unificación de The Spanish Fake News Corpus (spec 10, contrato C2)."""

import pandas as pd

from src.config import ETIQUETAS, RUTA_DATOS_PROCESADOS, RUTA_DATOS_RAW

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


def quitar_vacios_y_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina textos vacíos y duplicados exactos de texto, e imprime cuántos quitó."""
    n_inicial = len(df)
    df = df[df["texto"].str.strip() != ""]
    n_vacios = n_inicial - len(df)
    df = df.drop_duplicates(subset="texto").reset_index(drop=True)
    print(f"Eliminadas: {n_vacios} vacías y {n_inicial - n_vacios - len(df)} duplicadas. Quedan {len(df)}.")
    return df


def generar_procesado() -> pd.DataFrame:
    """data/raw/*.xlsx -> data/processed/noticias.csv (C2)."""
    df = quitar_vacios_y_duplicados(limpiar_y_etiquetar(cargar_crudo()))
    RUTA_DATOS_PROCESADOS.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_DATOS_PROCESADOS, index=False, encoding="utf-8")
    return df


def cargar_procesado() -> pd.DataFrame:
    """Lee noticias.csv; si todavía no existe, lo genera."""
    if not RUTA_DATOS_PROCESADOS.exists():
        return generar_procesado()
    return pd.read_csv(RUTA_DATOS_PROCESADOS, encoding="utf-8")


if __name__ == "__main__":
    df = generar_procesado()
    print(df["etiqueta"].value_counts().to_string())
