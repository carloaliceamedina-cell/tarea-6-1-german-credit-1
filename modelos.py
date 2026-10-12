"""Pipelines: codificación dentro del Pipeline + modelo con valores por defecto."""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier


def crear_pipeline(modelo, cols_cat):
    """Codificador ordinal para texto (numéricas en passthrough) + modelo.

    Al ir dentro del Pipeline, el codificador se ajusta solo con el
    entrenamiento de cada pliegue (sin fuga de procedimiento).
    """
    prep = ColumnTransformer(
        transformers=[
            ("cat",
             OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
             cols_cat),
        ],
        remainder="passthrough",  # numéricas sin escalar ni imputar
    )
    return Pipeline([("prep", prep), ("modelo", modelo)])


def modelos_base():
    """Los dos modelos a comparar, con hiperparámetros por defecto y semilla 42."""
    return {
        "Árbol de decisión": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
    }
