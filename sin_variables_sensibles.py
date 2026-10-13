"""Respuesta a H4 (6.1): el modelo elegido con y sin variables sensibles, mismo protocolo."""
from pathlib import Path

import pandas as pd

from comparar_tres import evaluar
from datos import SENSIBLES, cargar_datos
from modelos import variantes_con_coste

SALIDA = Path(__file__).resolve().parent / "resultados"

if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    X_sin = X.drop(columns=SENSIBLES)
    cols_cat_sin = [c for c in cols_cat if c not in SENSIBLES]
    modelo = variantes_con_coste()["Boosting (peso 5:1)"]
    tabla = pd.DataFrame([
        evaluar("Boosting 5:1 — 20 variables", modelo, X, y, cols_cat, cv),
        evaluar("Boosting 5:1 — sin age, personal_status, foreign_worker", modelo, X_sin, y, cols_cat_sin, cv),
    ])
    print(tabla.drop(columns="tiempo_ajuste_s").to_string(index=False, float_format="%.3f"))
    tabla.to_csv(SALIDA / "sin_variables_sensibles.csv", index=False)
    print("Guardado: resultados/sin_variables_sensibles.csv")
