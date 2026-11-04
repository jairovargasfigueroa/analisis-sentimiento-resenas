"""Tests del pipeline de NLP (spec 20, contratos C3, C4 y C5)."""

import joblib
import pytest

from src.nlp.explicar import explicar_preprocesamiento
from src.nlp.normalizacion import normalizar, quitar_tildes
from src.nlp.preprocesador import TextPreprocessor
from src.nlp.raices import lematizar, stemizar
from src.nlp.stopwords import quitar_stopwords
from src.nlp.tokenizacion import tokenizar

TEXTOS = [
    "¡¡URGENTE!! La OMS confirmó 3 casos 😱 https://x.com",
    "El Ministerio de Salud informó que la campaña de vacunación empieza el lunes.",
    "No es cierto que el niño haya muerto por la vacuna, afirmó el médico.",
    "@usuario comparte esto #QuédateEnCasa noooooo puede ser!!!",
    "",
]


def test_url_y_mencion_eliminadas():
    t = normalizar("Mira esto @juan https://x.com/nota y www.sitio.com")
    assert "http" not in t and "www" not in t and "juan" not in t


def test_senales_de_estilo_como_tokens():
    assert normalizar("¡¡Increíble!! 😱 3.500 muertos") == "exclamacion increíble exclamacion emoji num muertos"


def test_marcadores_de_la_v1_igual_que_la_v2():
    # La v1 trae *NUMBER*, *PHONE* y *URL*; deben quedar igual que los dígitos y URLs de la v2.
    assert normalizar("Murieron *NUMBER* personas *URL*") == normalizar("Murieron 35 personas https://x.com")
    assert normalizar("Llama al *PHONE*") == "llama al num"


def test_hashtag_y_letras_repetidas():
    assert normalizar("#Vacunas graveeeee") == "vacunas gravee"


def test_normalizar_conserva_tildes_y_quitar_tildes_conserva_ene():
    assert normalizar("Afirmó") == "afirmó"
    assert quitar_tildes("afirmó que el niño") == "afirmo que el niño"


def test_tokenizar():
    assert tokenizar("la oms confirmó num casos") == ["la", "oms", "confirmó", "num", "casos"]


def test_negaciones_conservadas():
    conservados, eliminadas = quitar_stopwords(["no", "hay", "la", "vacuna", "nunca", "sin", "ni", "tampoco"])
    assert conservados == ["no", "vacuna", "nunca", "sin", "ni", "tampoco"]
    assert eliminadas == ["hay", "la"]


def test_stopwords_sin_importar_tildes():
    _, eliminadas = quitar_stopwords(["está", "esta"])
    assert eliminadas == ["está", "esta"]


def test_stemizar():
    assert stemizar(["confirmaron", "vacunas"]) == ["confirm", "vacun"]


def test_lematizar_necesita_tildes():
    assert lematizar(["afirmó"]) == ["afirmar"]
    assert lematizar(["afirmo"]) != ["afirmar"]  # sin tilde spaCy se equivoca: por eso se quitan al final


def test_lematizar_un_lema_por_token():
    assert lematizar(["permitirlo", "adueñarse"]) == ["permitir", "adueñar"]


def test_modo_invalido():
    with pytest.raises(ValueError):
        TextPreprocessor(modo="otro").transform(["hola"])


@pytest.mark.parametrize("modo", ["lema", "stem", "ninguno"])
def test_preprocesador_se_serializa(tmp_path, modo):
    prep = TextPreprocessor(modo=modo)
    ruta = tmp_path / "prep.joblib"
    joblib.dump(prep, ruta)
    assert joblib.load(ruta).transform(TEXTOS) == prep.transform(TEXTOS)


def test_explicar_tiene_claves_c5():
    claves = {"original", "normalizado", "tokens", "stopwords_eliminadas",
              "tokens_sin_stopwords", "modo", "raices_o_lemas", "texto_final"}
    assert set(explicar_preprocesamiento(TEXTOS[0])) == claves


@pytest.mark.parametrize("modo", ["lema", "stem"])
@pytest.mark.parametrize("texto", TEXTOS)
def test_explicar_coincide_con_preprocesador(texto, modo):
    assert explicar_preprocesamiento(texto, modo)["texto_final"] == TextPreprocessor(modo).transform([texto])[0]
