"""Entrenamiento: python -m src.models.train (spec 30, contrato C6).

Va de data/raw a models/ sin pasos manuales: carga, split, entrena, evalúa y guarda.
"""

from sklearn.model_selection import train_test_split

from src.config import SEED, TEST_SIZE
from src.data.cargar import cargar_procesado


def dividir(df):
    """Split estratificado 80/20 con SEED. El test no se usa para ajustar nada."""
    return train_test_split(
        df["texto"].tolist(), df["etiqueta"].tolist(),
        test_size=TEST_SIZE, stratify=df["etiqueta"], random_state=SEED,
    )


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = dividir(cargar_procesado())
    print(f"train: {len(X_train)} · test: {len(X_test)}")
