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


# --- Tarea 6.2 ---------------------------------------------------------------
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

# Peso de la clase 'bad' tomado de la matriz de coste del dataset (5:1), fijado
# en PLAN_6_2.md antes de ver resultados; no se ajusta con los datos.
PESO_COSTE = {0: 1, 1: 5}


def tres_modelos(max_depth=None, min_samples_leaf=1):
    """Árbol (por defecto o afinado), Random Forest y boosting, semilla 42."""
    return {
        "Árbol": DecisionTreeClassifier(max_depth=max_depth,
                                        min_samples_leaf=min_samples_leaf,
                                        random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Boosting": HistGradientBoostingClassifier(random_state=42),
    }


def variantes_con_coste():
    """Extensión (respuesta a H2): RF y boosting con peso 5 para la clase 'bad'."""
    return {
        "Random Forest (peso 5:1)": RandomForestClassifier(class_weight=PESO_COSTE,
                                                           random_state=42),
        "Boosting (peso 5:1)": HistGradientBoostingClassifier(class_weight=PESO_COSTE,
                                                              random_state=42),
    }
