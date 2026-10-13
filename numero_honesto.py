"""Control del optimismo de la búsqueda: prueba reservada y CV anidada (Tarea 6.2, punto 2)."""
from pathlib import Path

import pandas as pd

from busqueda import buscar, buscar_con_prueba, validacion_anidada
from datos import cargar_datos
from modelos import crear_pipeline, tres_modelos

SALIDA = Path(__file__).resolve().parent / "resultados"

if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    arbol = crear_pipeline(tres_modelos()["Árbol"], cols_cat)

    _, puntaje_busqueda, _ = buscar(arbol, X, y, cv)
    mejor_80, busqueda_80, prueba = buscar_con_prueba(arbol, X, y, cv)
    media_anidada, desv_anidada, por_pliegue = validacion_anidada(arbol, X, y, cv)

    print(f"Número de la búsqueda (todos los datos):  {puntaje_busqueda:.3f}")
    print(f"Prueba reservada (20 %): la búsqueda sobre el 80 % dijo {busqueda_80:.3f} "
          f"y la prueba dio {prueba:.3f}  | ganador en el 80 %: {mejor_80}")
    print(f"CV anidada (5 externos × 5 internos):     {media_anidada:.3f} ± {desv_anidada:.3f}")
    print("  por pliegue externo:", " ".join(f"{p:.3f}" for p in por_pliegue))
    print(f"Optimismo de la búsqueda (búsqueda − anidada): {puntaje_busqueda - media_anidada:+.3f}")

    SALIDA.mkdir(exist_ok=True)
    pd.DataFrame([
        {"medida": "busqueda_todos_los_datos", "exactitud": puntaje_busqueda, "desv": None},
        {"medida": "busqueda_80", "exactitud": busqueda_80, "desv": None},
        {"medida": "prueba_reservada_20", "exactitud": prueba, "desv": None},
        {"medida": "cv_anidada", "exactitud": media_anidada, "desv": desv_anidada},
    ]).to_csv(SALIDA / "numero_honesto.csv", index=False)
    print("Guardado: resultados/numero_honesto.csv")
