"""Curvas de aprendizaje: diagnóstico de la 6.1 frente al árbol afinado y al modelo elegido."""
from pathlib import Path

import pandas as pd

from curvas import curva_aprendizaje, graficar_paneles
from datos import cargar_datos
from modelos import crear_pipeline, tres_modelos, variantes_con_coste

RAIZ = Path(__file__).resolve().parent

if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    modelos = {
        "Árbol por defecto (6.1)": tres_modelos()["Árbol"],
        "Árbol afinado": tres_modelos(max_depth=5, min_samples_leaf=1)["Árbol"],
        "Boosting 5:1 (elegido)": variantes_con_coste()["Boosting (peso 5:1)"],
    }
    curvas, filas = {}, []
    for nombre, modelo in modelos.items():
        t, ent, val = curva_aprendizaje(crear_pipeline(modelo, cols_cat), X, y, cv)
        curvas[nombre] = (t, ent, val)
        for ti, e, v in zip(t, ent, val):
            filas.append({"modelo": nombre, "n_entrenamiento": ti, "entrenamiento": e,
                          "validacion": v, "brecha": e - v})
        print(f"{nombre:24s} entrenamiento {ent[-1]:.3f} | validación {val[-1]:.3f} | "
              f"brecha {ent[-1] - val[-1]:.3f} | validación en {t[0]} → {t[-1]}: {val[0]:.3f} → {val[-1]:.3f}")
    (RAIZ / "figs").mkdir(exist_ok=True)
    graficar_paneles(curvas, RAIZ / "figs" / "curvas_aprendizaje.png")
    pd.DataFrame(filas).to_csv(RAIZ / "resultados" / "curvas_aprendizaje.csv", index=False)
    print("Guardado: figs/curvas_aprendizaje.png, resultados/curvas_aprendizaje.csv")
