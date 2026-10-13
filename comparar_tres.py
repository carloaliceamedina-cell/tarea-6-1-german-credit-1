"""Árbol afinado, Random Forest y boosting con el mismo protocolo (Tarea 6.2, punto 3).

Por modelo: exactitud (media y desviación), malos detectados, tiempo de ajuste y
coste (5·FN + 1·FP). Incluye la extensión con peso 5:1 fijada en PLAN_6_2.md.
"""
from pathlib import Path

import pandas as pd
from sklearn.metrics import recall_score
from sklearn.model_selection import cross_val_predict, cross_validate

from datos import cargar_datos
from modelos import crear_pipeline, tres_modelos, variantes_con_coste
from validacion import coste

SALIDA = Path(__file__).resolve().parent / "resultados"
GANADOR = {"max_depth": 5, "min_samples_leaf": 1}  # de defecto_vs_afinado.py


def evaluar(nombre, modelo, X, y, cols_cat, cv):
    pipe = crear_pipeline(modelo, cols_cat)
    r = cross_validate(pipe, X, y, cv=cv, scoring="accuracy")
    pred = cross_val_predict(pipe, X, y, cv=cv)
    c, fn, fp = coste(y, pred)
    return {
        "modelo": nombre,
        "exactitud_media": r["test_score"].mean(),
        "exactitud_desv": r["test_score"].std(),
        "malos_detectados": recall_score(y, pred),
        "malos_aprobados_FN": fn,
        "buenos_rechazados_FP": fp,
        "coste": c,
        "tiempo_ajuste_s": r["fit_time"].sum(),
    }


if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    modelos = {
        "Árbol por defecto (6.1)": tres_modelos()["Árbol"],
        "Árbol afinado": tres_modelos(**GANADOR)["Árbol"],
        "Random Forest": tres_modelos()["Random Forest"],
        "Boosting": tres_modelos()["Boosting"],
        **variantes_con_coste(),
    }
    tabla = pd.DataFrame([evaluar(n, m, X, y, cols_cat, cv) for n, m in modelos.items()])
    print("Mismo protocolo: StratifiedKFold(5, shuffle=True, random_state=42); coste = 5·FN + 1·FP")
    print("Línea base 'siempre good': exactitud 0.700, malos detectados 0.00, coste 1500\n")
    print(tabla.to_string(index=False, float_format="%.3f"))
    SALIDA.mkdir(exist_ok=True)
    tabla.to_csv(SALIDA / "comparacion_modelos.csv", index=False)
    print("\nGuardado: resultados/comparacion_modelos.csv")
    print("(Los tiempos dependen del equipo; las demás cifras son deterministas.)")
