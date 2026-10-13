"""Métrica prioritaria por subgrupo del modelo recomendado (respuesta a V4.1).

Predicciones fuera de pliegue (misma CV). Las variables sensibles NO entran al
modelo; se usan solo para agrupar.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_predict

from datos import cargar_datos, cargar_datos_sin_sensibles
from modelos import crear_pipeline, variantes_con_coste

SALIDA = Path(__file__).resolve().parent / "resultados"


def tabla_por_subgrupo(grupos, y, pred):
    t = pd.DataFrame({"grupo": grupos, "y": np.asarray(y), "pred": pred})
    filas = []
    for g, d in t.groupby("grupo"):
        malos, buenos = d[d.y == 1], d[d.y == 0]
        filas.append({"grupo": g, "n": len(d), "n_bad": len(malos),
                      "exactitud": (d.y == d.pred).mean(),
                      "malos_detectados": (malos.pred == 1).mean(),
                      "buenos_rechazados": (buenos.pred == 1).mean()})
    return pd.DataFrame(filas)


if __name__ == "__main__":
    X_completo, y, _, cv = cargar_datos()
    X, _, cols_cat, _ = cargar_datos_sin_sensibles()
    modelo = crear_pipeline(variantes_con_coste()["Boosting (peso 5:1)"], cols_cat)
    pred = cross_val_predict(modelo, X, y, cv=cv)
    global_ = (pred[y.to_numpy() == 1] == 1).mean()
    print(f"Boosting 5:1 sin variables sensibles · malos detectados global: {global_:.3f}\n")
    variables = {
        "housing": X_completo["housing"],
        "personal_status": X_completo["personal_status"],
        "edad": np.where(X_completo["age"] <= 25, "<=25", ">25"),
    }
    partes = []
    for nombre, grupos in variables.items():
        tabla = tabla_por_subgrupo(grupos, y, pred)
        tabla.insert(0, "variable", nombre)
        partes.append(tabla)
    todo = pd.concat(partes, ignore_index=True)
    print(todo.to_string(index=False, float_format="%.3f"))
    todo.to_csv(SALIDA / "auditoria_subgrupos.csv", index=False)
    print("\nGuardado: resultados/auditoria_subgrupos.csv")
