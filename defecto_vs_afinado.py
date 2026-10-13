"""Árbol por defecto frente al árbol afinado con GridSearchCV (Tarea 6.2, punto 1)."""
from pathlib import Path

import pandas as pd

from busqueda import PARAM_GRID, buscar
from datos import cargar_datos
from modelos import crear_pipeline, tres_modelos
from validacion import validar

SALIDA = Path(__file__).resolve().parent / "resultados"

if __name__ == "__main__":
    X, y, cols_cat, cv = cargar_datos()
    arbol = crear_pipeline(tres_modelos()["Árbol"], cols_cat)
    por_defecto, desv_defecto, _ = validar(arbol, X, y, cv)
    mejor, puntaje, busqueda = buscar(arbol, X, y, cv)

    print("Espacio de búsqueda:", PARAM_GRID, f"({len(busqueda.cv_results_['params'])} combinaciones)")
    print(f"Por defecto: {por_defecto:.3f} ± {desv_defecto:.3f}")
    print(f"Afinado:     {puntaje:.3f} ± {busqueda.cv_results_['std_test_score'][busqueda.best_index_]:.3f}")
    print(f"Mejora:      {puntaje - por_defecto:+.3f}")
    print("Configuración ganadora:", mejor)

    # Las 40 combinaciones, ordenadas por puntaje (evidencia del espacio explorado)
    tabla = pd.DataFrame(busqueda.cv_results_)[
        ["param_modelo__max_depth", "param_modelo__min_samples_leaf",
         "mean_test_score", "std_test_score", "rank_test_score"]]
    tabla.columns = ["max_depth", "min_samples_leaf", "exactitud_media", "exactitud_desv", "rango"]
    tabla = tabla.sort_values("rango")
    SALIDA.mkdir(exist_ok=True)
    tabla.to_csv(SALIDA / "busqueda_arbol.csv", index=False)
    print("\nLas 5 mejores combinaciones:")
    print(tabla.head(5).to_string(index=False, float_format="%.3f"))
    print("\nGuardado: resultados/busqueda_arbol.csv")
