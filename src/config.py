"""Configuración central: lee params.yaml y expone constantes y rutas (contrato C1)."""

from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent

with open(RAIZ / "params.yaml", encoding="utf-8") as f:
    PARAMS = yaml.safe_load(f)

SEED = PARAMS["seed"]
ETIQUETAS = PARAMS["labels"]

RUTA_DATOS_RAW = RAIZ / PARAMS["data"]["raw_dir"]
RUTA_DATOS_PROCESADOS = RAIZ / PARAMS["data"]["processed_path"]
TEST_SIZE = PARAMS["data"]["test_size"]

RUTA_MODELOS = RAIZ / "models"
RUTA_MODELO = RUTA_MODELOS / "modelo_produccion.joblib"
RUTA_METRICAS = RUTA_MODELOS / "metricas.json"

LONGITUD_MAX_TEXTO = PARAMS["api"]["max_chars"]
MAX_TEXTOS_LOTE = PARAMS["api"]["max_textos_lote"]
