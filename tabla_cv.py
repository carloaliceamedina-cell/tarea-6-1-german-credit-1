"""Tabla de validación cruzada (5 pliegues estratificados) para árbol y Random Forest."""
from pathlib import Path

import pandas as pd

from datos import cargar_datos
from modelos import crear_pipeline, modelos_base
from validacion import proporcion_malos_detectados, validar

PISO_EXACTITUD = 0.70  # decir siempre 'good' (RESUMEN)


def calcular_tabla_cv():
    X, y, cols_cat, cv = cargar_datos()
    filas = []
    for nombre, modelo in modelos_base().items():
        pipe = crear_pipeline(modelo, cols_cat)
        media, desv, _ = validar(pipe, X, y, cv)
        rec, rec_pl, det, total = proporcion_malos_detectados(pipe, X, y, cv)
        filas.append({
            "modelo": nombre,
            "exactitud_media": media,
            "exactitud_desv": desv,
            "malos_detectados": rec,
            "malos_detectados_desv": rec_pl.std(),
            "malos_detectados_n": f"{det}/{total}",
            "supera_piso_0.70": media > PISO_EXACTITUD,
        })
    return pd.DataFrame(filas)


def main():
    tabla = calcular_tabla_cv()
    print("Validación cruzada: StratifiedKFold(n_splits=5, shuffle=True, random_state=42)")
    print(f"Piso (siempre 'good'): exactitud {PISO_EXACTITUD:.2f}, malos detectados 0.00 (0/300)\n")
    print(tabla.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    salida = Path(__file__).resolve().parent / "resultados" / "tabla_cv.csv"
    salida.parent.mkdir(exist_ok=True)
    tabla.to_csv(salida, index=False)
    print(f"\nGuardado: resultados/{salida.name}")


if __name__ == "__main__":
    main()
