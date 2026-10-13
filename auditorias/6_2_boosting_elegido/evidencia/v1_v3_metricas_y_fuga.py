"""V1.1–V1.4, V2.1–V2.4, V3.1–V3.2 — comprobaciones propias del auditor.

Ejecutar desde la raíz del proyecto:
    python3 -B auditorias/6_2_boosting_elegido/evidencia/v1_v3_metricas_y_fuga.py

Solo lee el proyecto (importa sus módulos sin generar __pycache__).
"""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, ".")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score  # noqa: E402
from sklearn.model_selection import cross_val_predict  # noqa: E402

from datos import SENSIBLES, cargar_datos, cargar_datos_sin_sensibles  # noqa: E402
from modelos import crear_pipeline, variantes_con_coste  # noqa: E402

X, y, cols_cat, cv = cargar_datos()
X_sin, y_sin, cols_cat_sin, cv_sin = cargar_datos_sin_sensibles()
modelo = variantes_con_coste()["Boosting (peso 5:1)"]
pipe = crear_pipeline(modelo, cols_cat_sin)


def titulo(t):
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


titulo("Modelo auditado")
print(pipe)
p = pipe.named_steps["modelo"].get_params()
print({k: p[k] for k in ["class_weight", "random_state", "early_stopping", "max_iter",
                         "learning_rate", "max_leaf_nodes", "min_samples_leaf"]})
print(f"Predictoras ({X_sin.shape[1]}): {list(X_sin.columns)}")
print(f"Sensibles fuera del modelo: {not set(SENSIBLES) & set(X_sin.columns)}")

# --------------------------------------------------------------------------
titulo("V1.1 Rango: métricas en [0, 1] en resultados/*.csv")
metricas = {
    "comparacion_modelos.csv": ["exactitud_media", "exactitud_desv", "malos_detectados"],
    "sin_variables_sensibles.csv": ["exactitud_media", "exactitud_desv", "malos_detectados"],
    "busqueda_arbol.csv": ["exactitud_media", "exactitud_desv"],
    "numero_honesto.csv": ["exactitud", "desv"],
    "curvas_aprendizaje.csv": ["entrenamiento", "validacion", "brecha"],
}
todo_ok = True
for archivo, cols in metricas.items():
    df = pd.read_csv(f"resultados/{archivo}")
    for c in cols:
        v = df[c].dropna()
        ok = bool(((v >= 0) & (v <= 1)).all())
        todo_ok &= ok
        print(f"  {archivo:<30}{c:<18} min {v.min():.4f}  max {v.max():.4f}  en [0,1]: {ok}")
print(f"  TODAS en [0, 1]: {todo_ok}")

# --------------------------------------------------------------------------
titulo("V1.2 Coherencia: recálculo desde la matriz de confusión (tolerancia 0.01)")
pred = cross_val_predict(pipe, X_sin, y, cv=cv)
tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
print(f"  Matriz propia (fuera de pliegue, modelo auditado): TN={tn} FP={fp} FN={fn} TP={tp}")
acc_cm, rec_cm, prec_cm = (tp + tn) / len(y), tp / (tp + fn), tp / (tp + fp)
print(f"  Desde la matriz: exactitud {acc_cm:.4f} | recall bad {rec_cm:.4f} | precisión bad {prec_cm:.4f}")
print(f"  sklearn:         exactitud {accuracy_score(y, pred):.4f} | recall bad {recall_score(y, pred):.4f}"
      f" | precisión bad {precision_score(y, pred):.4f}")
fila = pd.read_csv("resultados/sin_variables_sensibles.csv").iloc[1]
print(f"  Reportado ({fila['modelo']}): exactitud_media {fila['exactitud_media']:.4f} | malos_detectados "
      f"{fila['malos_detectados']:.4f} | FN {fila['malos_aprobados_FN']} | FP {fila['buenos_rechazados_FP']} | coste {fila['coste']}")
print(f"  |Δ exactitud| {abs(acc_cm - fila['exactitud_media']):.4f} | |Δ recall| {abs(rec_cm - fila['malos_detectados']):.4f}"
      f" | FN igual {fn == fila['malos_aprobados_FN']} | FP igual {fp == fila['buenos_rechazados_FP']}"
      f" | coste propio {5 * fn + fp} igual {5 * fn + fp == fila['coste']}")
print("  Nota: exactitud_media es la media de 5 pliegues de 200 filas, que coincide con la exactitud agregada.")

print("\n  Coherencia interna de comparacion_modelos.csv y sin_variables_sensibles.csv (P = 300, N = 700):")
for archivo in ["comparacion_modelos.csv", "sin_variables_sensibles.csv"]:
    for _, r in pd.read_csv(f"resultados/{archivo}").iterrows():
        tp_r = 300 - r["malos_aprobados_FN"]
        tn_r = 700 - r["buenos_rechazados_FP"]
        acc_r, rec_r = (tp_r + tn_r) / 1000, tp_r / 300
        c_r = 5 * r["malos_aprobados_FN"] + r["buenos_rechazados_FP"]
        ok = abs(acc_r - r["exactitud_media"]) <= 0.01 and abs(rec_r - r["malos_detectados"]) <= 0.01 and c_r == r["coste"]
        print(f"    {r['modelo'][:45]:<46} exact. {acc_r:.3f} vs {r['exactitud_media']:.3f} | recall {rec_r:.3f} vs "
              f"{r['malos_detectados']:.3f} | coste {c_r} vs {r['coste']} -> {'coincide' if ok else 'NO coincide'}")

# --------------------------------------------------------------------------
titulo("V1.3 Desbalance")
p_min, K = y.value_counts(normalize=True).min(), y.nunique()
print(f"  Distribución: {y.value_counts().to_dict()} | p_min = {p_min:.3f} | K = {K} | 0.8/K = {0.8 / K:.3f}")
print(f"  p_min < 0.8/K: {p_min < 0.8 / K} -> se exige métrica por clase (el proyecto reporta recall de 'bad')")

titulo("V1.4 Línea base 'siempre good'")
base = np.zeros(len(y), dtype=int)
fn_b = int(((y == 1) & (base == 0)).sum()); fp_b = int(((y == 0) & (base == 1)).sum())
print(f"  exactitud {accuracy_score(y, base):.3f} | recall bad {recall_score(y, base, zero_division=0):.3f}"
      f" | coste {5 * fn_b + fp_b}")
print(f"  Modelo auditado: exactitud {acc_cm:.3f} | recall bad {rec_cm:.3f} | coste {5 * fn + fp}"
      f" ({(5 * fn + fp) / (5 * fn_b + fp_b):.1%} del coste de la línea base)")

# --------------------------------------------------------------------------
titulo("V2.1 / V3.1 El codificador se ajusta por pliegue (solo con el entrenamiento)")
for k, (ent, pru) in enumerate(cv.split(X_sin, y)):
    pk = clone(pipe).fit(X_sin.iloc[ent], y.iloc[ent])
    enc = pk.named_steps["prep"].named_transformers_["cat"]
    iguales = all(set(cats) == set(X_sin.iloc[ent][col].unique())
                  for col, cats in zip(cols_cat_sin, enc.categories_))
    nuevas = sum(int((~X_sin.iloc[pru][col].isin(X_sin.iloc[ent][col])).sum()) for col in cols_cat_sin)
    print(f"  pliegue {k}: entren. {len(ent)} | prueba {len(pru)} (bad {int(y.iloc[pru].sum())}) | categorías "
          f"aprendidas == categorías del entrenamiento: {iguales} | valores de prueba no vistos: {nuevas}")

titulo("V2.4 Misma partición: pliegues con X completo y con X sin sensibles")
a = [tuple(p) for _, p in cv.split(X, y)]
b = [tuple(p) for _, p in cv_sin.split(X_sin, y_sin)]
print(f"  Índices de prueba idénticos en los 5 pliegues: {a == b}")
print(f"  Mismo objeto de CV: {cv!r} vs {cv_sin!r}")

# --------------------------------------------------------------------------
titulo("V3.2 Columnas del futuro / derivadas del objetivo")
print(f"  'clase' entre las predictoras: {'clase' in X_sin.columns}")
idem = [c for c in X_sin.columns if X_sin[c].astype(str).nunique() > 1 and
        (pd.crosstab(X_sin[c], y).min(axis=1) == 0).all()]
print(f"  Predictoras cuyas categorías separan la clase al 100 % (todas puras): {idem or 'ninguna'}")
puras = []
for c in X_sin.columns:
    if X_sin[c].nunique() <= 12:
        t = pd.crosstab(X_sin[c], y)
        for nivel, fila_t in t.iterrows():
            if fila_t.sum() >= 20 and fila_t.min() == 0:
                puras.append(f"{c}={nivel} (n={fila_t.sum()})")
print(f"  Categorías con n >= 20 de una sola clase: {puras or 'ninguna'}")
