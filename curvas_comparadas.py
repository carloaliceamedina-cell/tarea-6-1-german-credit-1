"""Curvas de aprendizaje: diagnóstico de la 6.1 frente al árbol afinado y al modelo elegido."""
from pathlib import Path

import pandas as pd

from curvas import curva_aprendizaje, graficar_paneles
from datos import cargar_datos, cargar_datos_sin_sensibles
from modelos import crear_pipeline, tres_modelos, variantes_con_coste

RAIZ = Path(__file__).resolve().parent

if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    modelos = {
        "Árbol por defecto (6.1)": tres_modelos()["Árbol"],
        "Árbol afinado": tres_modelos(max_depth=5, min_samples_leaf=1)["Árbol"],
        "Boosting 5:1 sin sensibles (elegido)": variantes_con_coste()["Boosting (peso 5:1)"],
    }
    X_sin, _, cols_cat_sin, _ = cargar_datos_sin_sensibles()
    curvas, filas = {}, []
    for nombre, modelo in modelos.items():
        Xm, cc = (X_sin, cols_cat_sin) if "sin sensibles" in nombre else (X, cols_cat)
        t, ent, val = curva_aprendizaje(crear_pipeline(modelo, cc), Xm, y, cv)
        curvas[nombre] = (t, ent, val)
        for ti, e, v in zip(t, ent, val):
            filas.append({"modelo": nombre, "n_entrenamiento": ti, "entrenamiento": e,
                          "validacion": v, "brecha": e - v})
        print(f"{nombre:36s} entrenamiento {ent[-1]:.3f} | validación {val[-1]:.3f} | "
              f"brecha {ent[-1] - val[-1]:.3f} | validación en {t[0]} → {t[-1]}: {val[0]:.3f} → {val[-1]:.3f}")
    (RAIZ / "figs").mkdir(exist_ok=True)
    graficar_paneles(curvas, RAIZ / "figs" / "curvas_aprendizaje.png")
    pd.DataFrame(filas).to_csv(RAIZ / "resultados" / "curvas_aprendizaje.csv", index=False)
    print("Guardado: figs/curvas_aprendizaje.png, resultados/curvas_aprendizaje.csv")
