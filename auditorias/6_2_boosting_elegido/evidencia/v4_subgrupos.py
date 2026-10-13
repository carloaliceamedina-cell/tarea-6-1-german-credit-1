"""V4.2 — Métrica prioritaria (recall de 'bad') por subgrupo, fuera de pliegue.

Ejecutar desde la raíz del proyecto:
    python3 -B auditorias/6_2_boosting_elegido/evidencia/v4_subgrupos.py

Modelo auditado: HistGradientBoostingClassifier(class_weight={0: 1, 1: 5},
random_state=42) dentro de modelos.crear_pipeline, entrenado SIN variables
sensibles (datos.cargar_datos_sin_sensibles()), con la CV de datos.cargar_datos().
Las variables sensibles solo se usan aquí para formar los subgrupos.

Umbrales de la Skill (V4.2): en todo subgrupo con n >= 30,
  brecha = recall global − recall del subgrupo <= 0.05   y
  cociente = recall del subgrupo / recall del mejor subgrupo >= 0.80.
Con el recall de 'bad', el n relevante es el número de 'bad' del subgrupo.
Decisiones del auditor (no las fija la Skill; ver "Limitaciones" del informe):
  - la brecha es de un solo lado (solo cuenta si el subgrupo queda POR DEBAJO
    de la global: la Skill la justifica como "máxima pérdida"); se imprime
    también la brecha absoluta;
  - el "mejor subgrupo" se toma dentro de la misma variable y solo entre los
    subgrupos elegibles (n_bad >= 30); se imprime también el cociente frente al
    mejor subgrupo incluyendo los de n < 30.
"""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, ".")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import recall_score  # noqa: E402
from sklearn.model_selection import cross_val_predict  # noqa: E402

from datos import cargar_datos, cargar_datos_sin_sensibles  # noqa: E402
from modelos import crear_pipeline, variantes_con_coste  # noqa: E402

BRECHA_MAX, COCIENTE_MIN, N_MIN = 0.05, 0.80, 30

X, y, cols_cat, cv = cargar_datos()          # X completo: solo para formar subgrupos
X_sin, _, cols_cat_sin, _ = cargar_datos_sin_sensibles()
y_np = y.to_numpy()


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


SUBGRUPOS = {
    "housing": X["housing"].to_numpy(),
    "personal_status": X["personal_status"].to_numpy(),
    "edad": np.where(X["age"] <= 25, "<=25", ">25"),
    "foreign_worker (añadido)": X["foreign_worker"].to_numpy(),
}


def tabla_subgrupos(pred):
    rec_global = recall_score(y_np, pred)
    filas = []
    for var, g in SUBGRUPOS.items():
        for nivel in sorted(pd.unique(g)):
            m = g == nivel
            n, nb = int(m.sum()), int(y_np[m].sum())
            ng = n - nb
            tp = int(((pred == 1) & (y_np == 1) & m).sum())
            fp = int(((pred == 1) & (y_np == 0) & m).sum())
            fn = nb - tp
            lo, hi = wilson(tp, nb)
            filas.append({
                "variable": var, "grupo": nivel, "n": n, "n_bad": nb, "n_good": ng,
                "detectados": tp, "recall_bad": tp / nb, "ic95_bajo": lo, "ic95_alto": hi,
                "exactitud": float((pred[m] == y_np[m]).mean()),
                "good_rechazados": fp, "prop_good_rechazados": fp / ng,
                "coste_por_solicitud": (5 * fn + fp) / n,
                "elegible": nb >= N_MIN,
            })
    t = pd.DataFrame(filas)
    t["brecha"] = rec_global - t["recall_bad"]                 # > 0: el subgrupo queda por debajo
    t["brecha_abs"] = t["brecha"].abs()
    mejor_eleg = t[t.elegible].groupby("variable")["recall_bad"].max()
    mejor_todos = t.groupby("variable")["recall_bad"].max()
    t["cociente"] = t["recall_bad"] / t["variable"].map(mejor_eleg)
    t["cociente_vs_mejor_incl_n<30"] = t["recall_bad"] / t["variable"].map(mejor_todos)
    t["pasa_brecha"] = t["brecha"] <= BRECHA_MAX
    t["pasa_cociente"] = t["cociente"] >= COCIENTE_MIN
    t["veredicto"] = np.where(~t.elegible, "no decide (n_bad<30)",
                              np.where(t.pasa_brecha & t.pasa_cociente, "PASA", "FALLA"))
    return rec_global, t


def imprimir(nombre, pred):
    rec_global, t = tabla_subgrupos(pred)
    print(f"\n{'=' * 100}\n{nombre}\n{'=' * 100}")
    print(f"Global (n=1000, bad=300): recall bad {rec_global:.3f} | exactitud {(pred == y_np).mean():.3f}"
          f" | good rechazados {int(((pred == 1) & (y_np == 0)).sum())}/700"
          f" = {((pred == 1) & (y_np == 0)).sum() / 700:.3f}")
    print(f"Umbrales: brecha (global − subgrupo) <= {BRECHA_MAX} y cociente (subgrupo / mejor elegible de la "
          f"misma variable) >= {COCIENTE_MIN}; deciden solo subgrupos con n_bad >= {N_MIN}.\n")
    cols = ["variable", "grupo", "n", "n_bad", "detectados", "recall_bad", "ic95_bajo", "ic95_alto",
            "brecha", "cociente", "veredicto"]
    print(t[cols].to_string(index=False, float_format="%.3f"))
    print("\nContexto (no decide el veredicto):")
    cols2 = ["variable", "grupo", "n", "n_good", "exactitud", "good_rechazados", "prop_good_rechazados",
             "coste_por_solicitud", "brecha_abs", "cociente_vs_mejor_incl_n<30"]
    print(t[cols2].to_string(index=False, float_format="%.3f"))
    elig = t[t.elegible]
    falla = elig[elig.veredicto == "FALLA"]
    print(f"\nSubgrupos elegibles: {len(elig)} | FALLA: {len(falla)} -> V4.2 = {'FALLA' if len(falla) else 'PASA'}")
    for _, r in falla.iterrows():
        motivos = []
        if not r.pasa_brecha:
            motivos.append(f"brecha {r.brecha:.3f} > {BRECHA_MAX}")
        if not r.pasa_cociente:
            motivos.append(f"cociente {r.cociente:.3f} < {COCIENTE_MIN}")
        print(f"  - {r.variable}={r.grupo} (n={r.n}, bad={r.n_bad}): recall {r.recall_bad:.3f}; {'; '.join(motivos)}")
    no_dec = t[~t.elegible]
    print("Listados pero sin decidir (n_bad < 30): " +
          ", ".join(f"{r.variable}={r.grupo} (n={r.n}, bad={r.n_bad}, recall {r.recall_bad:.3f})"
                    for _, r in no_dec.iterrows()))
    # Sensibilidad a las decisiones del auditor
    alt = elig[(elig.brecha_abs > BRECHA_MAX) | (elig["cociente_vs_mejor_incl_n<30"] < COCIENTE_MIN)]
    print("Sensibilidad (brecha absoluta y cociente frente al mejor incluyendo n<30): subgrupos elegibles que "
          "fallarían -> " + (", ".join(f"{r.variable}={r.grupo}" for _, r in alt.iterrows()) or "ninguno"))
    return t


modelo = variantes_con_coste()["Boosting (peso 5:1)"]
pred_sin = cross_val_predict(crear_pipeline(modelo, cols_cat_sin), X_sin, y, cv=cv)
t = imprimir("MODELO AUDITADO: Boosting 5:1 SIN variables sensibles (17 predictoras)", pred_sin)
t.to_csv("auditorias/6_2_boosting_elegido/evidencia/v4_subgrupos_modelo_auditado.csv", index=False)

pred_con = cross_val_predict(crear_pipeline(variantes_con_coste()["Boosting (peso 5:1)"], cols_cat), X, y, cv=cv)
imprimir("CONTEXTO: mismo Boosting 5:1 CON las 20 variables (no es el modelo auditado)", pred_con)

print(f"\nControl: recall global del modelo auditado {recall_score(y_np, pred_sin):.4f} "
      f"(resultados/sin_variables_sensibles.csv reporta 0.6400)")
