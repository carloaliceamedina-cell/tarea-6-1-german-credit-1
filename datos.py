"""Carga de German Credit: X, y, columnas de texto y esquema de validación cruzada."""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedKFold

RUTA_CSV = Path(__file__).resolve().parent / "datos" / "credit_g.csv"


def validar_datos(df):
    """Comprueba el CSV antes de entrenar (respuesta a V6.2 de la auditoría 6.2).

    Lanza ValueError si falta la clase, si hay valores fuera de good/bad, si hay
    faltantes o si cambia el número de filas/columnas esperado.
    """
    if "clase" not in df.columns:
        raise ValueError("Falta la columna objetivo 'clase'")
    extra = set(df["clase"].unique()) - {"good", "bad"}
    if extra:
        raise ValueError(f"Valores de 'clase' no esperados: {extra}")
    if df.isna().any().any():
        raise ValueError("Hay valores faltantes: " + str(df.columns[df.isna().any()].tolist()))
    if df.shape != (1000, 21):
        raise ValueError(f"Forma inesperada {df.shape}; se esperaba (1000, 21)")


def cargar_datos(ruta=RUTA_CSV):
    """Devuelve X, y, cols_cat, cv (sin transformar los datos)."""
    df = pd.read_csv(ruta)
    validar_datos(df)  # antes de cualquier fit
    # Clase positiva: 'bad' -> 1 (indicación 1 del RESUMEN)
    y = (df["clase"] == "bad").astype(int)
    # 'clase' nunca es predictora
    X = df.drop(columns=["clase"])
    # Columnas con texto (13 según el RESUMEN); el resto son numéricas
    cols_cat = X.select_dtypes(include=["object", "string"]).columns.tolist()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    return X, y, cols_cat, cv


# --- Tarea 6.2 ---------------------------------------------------------------
# Variables sensibles: se usan para AUDITAR, no para decidir (consigna de la 6.2).
SENSIBLES = ["age", "personal_status", "foreign_worker"]


def cargar_datos_sin_sensibles(ruta=RUTA_CSV):
    """Como cargar_datos(), sin las variables sensibles (modelo recomendado)."""
    X, y, cols_cat, cv = cargar_datos(ruta)
    X = X.drop(columns=SENSIBLES)
    cols_cat = [c for c in cols_cat if c not in SENSIBLES]
    return X, y, cols_cat, cv
