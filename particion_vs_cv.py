"""Partición única (10 semillas) frente a la media de la validación cruzada."""
from pathlib import Path

import pandas as pd

from datos import cargar_datos
from modelos import crear_pipeline, modelos_base
from validacion import SEMILLAS_PARTICION, particion_unica, validar


def main():
    X, y, cols_cat, cv = cargar_datos()
    detalle, resumen = [], []
    for nombre, modelo in modelos_base().items():
        pipe = crear_pipeline(modelo, cols_cat)
        media_cv, desv_cv, _ = validar(pipe, X, y, cv)
        df = particion_unica(pipe, X, y)
        df.insert(0, "modelo", nombre)
        detalle.append(df)
        acc = df["exactitud"]
        resumen.append({
            "modelo": nombre,
            "minimo": acc.min(),
            "maximo": acc.max(),
            "rango": acc.max() - acc.min(),
            "media": acc.mean(),
            "desviacion": acc.std(ddof=0),  # misma convención que la CV (np.std)
            "media_cv": media_cv,
            "desv_cv": desv_cv,
            "diferencia_vs_cv": acc.mean() - media_cv,
        })
    detalle = pd.concat(detalle, ignore_index=True)
    resumen = pd.DataFrame(resumen)

    fmt = lambda v: f"{v:.4f}"
    print(f"Partición única: train_test_split(test_size=0.25, stratify=y), semillas {SEMILLAS_PARTICION}\n")
    print("Detalle por modelo y semilla:")
    print(detalle.to_string(index=False, float_format=fmt))
    print("\nExactitud en partición única frente a validación cruzada (5 pliegues):")
    print(resumen.to_string(index=False, float_format=fmt))

    carpeta = Path(__file__).resolve().parent / "resultados"
    carpeta.mkdir(exist_ok=True)
    detalle.to_csv(carpeta / "particion_unica.csv", index=False)
    resumen.to_csv(carpeta / "particion_vs_cv.csv", index=False)
    print("\nGuardado: resultados/particion_unica.csv, resultados/particion_vs_cv.csv")


if __name__ == "__main__":
    main()
