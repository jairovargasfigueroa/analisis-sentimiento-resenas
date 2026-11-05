"""Tests de la carga del corpus (spec 10, contrato C2)."""

import pandas as pd
import pytest

from src.config import ETIQUETAS
from src.data.cargar import cargar_procesado, limpiar_y_etiquetar, quitar_vacios_y_duplicados


@pytest.fixture(scope="module")
def df():
    return cargar_procesado()


def test_columnas_c2(df):
    assert list(df.columns) == ["texto", "etiqueta", "tema", "fuente", "anio"]


def test_solo_dos_etiquetas_y_balanceadas(df):
    assert set(df["etiqueta"]) == set(ETIQUETAS)
    conteo = df["etiqueta"].value_counts(normalize=True)
    assert conteo.min() > 0.45


def test_textos_no_vacios_ni_duplicados(df):
    assert df["texto"].str.strip().ne("").all()
    assert not df["texto"].duplicated().any()


def test_tamano_y_versiones(df):
    assert len(df) >= 1500
    assert set(df["anio"]) == {2018, 2021}


def test_unifica_etiquetas_de_v1_y_v2():
    # v1 trae "Fake"/"True" como texto; v2 trae booleanos.
    crudo = pd.DataFrame({
        "category": ["Fake", "True", False, True],
        "topic": ["Política"] * 4,
        "source": ["El Dizque", None, "x", "y"],
        "headline": ["Titular", "Otro", None, "Repetido"],
        "text": ["Cuerpo uno", "Cuerpo dos", "Post sin titular", "Repetido. Cuerpo cuatro"],
        "anio": [2018, 2018, 2021, 2021],
    })
    out = limpiar_y_etiquetar(crudo)
    assert list(out["etiqueta"]) == ["falsa", "verdadera", "falsa", "verdadera"]
    assert out["texto"][0] == "Titular. Cuerpo uno"
    assert out["texto"][2] == "Post sin titular"  # sin titular: solo el cuerpo
    assert out["texto"][3] == "Repetido. Cuerpo cuatro"  # el cuerpo ya trae el titular: no se repite
    assert out["fuente"][1] == "desconocida"


def test_etiqueta_desconocida_falla():
    crudo = pd.DataFrame({"category": ["Quizás"], "topic": ["x"], "source": ["x"],
                          "headline": ["x"], "text": ["x"], "anio": [2018]})
    with pytest.raises(ValueError):
        limpiar_y_etiquetar(crudo)


def test_quita_vacios_y_duplicados():
    df = pd.DataFrame({"texto": ["a", "a", "  ", "b"], "etiqueta": ["falsa"] * 4})
    assert list(quitar_vacios_y_duplicados(df)["texto"]) == ["a", "b"]
