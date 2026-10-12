"""Auditoría independiente — German Credit (MAI 540, Tarea 6.1).

Rol: auditor. Ejecutar desde la raíz del proyecto:  python3 auditoria.py

Qué hace (sin escribir NADA dentro del proyecto):
  0. Huella MD5 de los datos y versiones del entorno.
  1. Reproducibilidad: copia los scripts del ingeniero y los datos a una carpeta
     temporal, los ejecuta allí y compara byte a byte con resultados/*.csv.
     Además recalcula cada cifra con código propio y la compara con los CSV.
  2. Fuga: inspecciona el Pipeline del ingeniero, comprueba que el codificador
     se ajusta por pliegue (categorías aprendidas == categorías del
     entrenamiento de ese pliegue), que `clase` no es predictora y hace una
     prueba de etiquetas permutadas.
  3. Clase positiva: matriz de confusión propia sobre etiquetas de texto.
  4. Coherencia analista -> ingeniero y verificación de las cifras del RESUMEN.
  5. Partición: pliegues y semillas.
  6. Línea base "siempre good".
  7. Subgrupos por housing y personal_status (+ age y foreign_worker, que el
     ingeniero pidió revisar).
  8. Lectura de negocio: costes con la matriz de coste del German Credit y
     umbral (solo ilustrativo; no sustituye resultados).
"""
import sys

sys.dont_write_bytecode = True  # no dejar __pycache__ al importar código del ingeniero

import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from scipy.stats import chi2_contingency
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_val_score, cross_validate,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

RAIZ = Path(__file__).resolve().parent
CSV = RAIZ / "datos" / "credit_g.csv"
RES = RAIZ / "resultados"
TOL = 1e-12
SCRIPTS_ING = ["datos.py", "modelos.py", "validacion.py", "tabla_cv.py", "particion_vs_cv.py"]

veredictos = {}


def titulo(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def comparar(nombre, propio, entregado, tol=TOL):
    ok = abs(float(propio) - float(entregado)) <= tol
    print(f"  {'OK ' if ok else 'DIF'} {nombre:<45} propio={float(propio):.6f}  entregado={float(entregado):.6f}")
    return ok


# ---------------------------------------------------------------------------
titulo("0. Datos y entorno")
md5_antes = md5(CSV)
print(f"MD5 datos/credit_g.csv: {md5_antes}")
print(f"Python {sys.version.split()[0]} | pandas {pd.__version__} | numpy {np.__version__} | scikit-learn {sklearn.__version__}")
md5_res_antes = {p.name: md5(p) for p in sorted(RES.glob("*.csv"))}

df = pd.read_csv(CSV)
TEXTO = ["checking_status", "credit_history", "purpose", "savings_status", "employment",
         "personal_status", "other_parties", "property_magnitude", "other_payment_plans",
         "housing", "job", "own_telephone", "foreign_worker"]          # 13 del RESUMEN
NUM = ["duration", "credit_amount", "installment_commitment", "residence_since", "age",
       "existing_credits", "num_dependents"]                          # 7 del RESUMEN
X = df.drop(columns=["clase"])
y = (df["clase"] == "bad").astype(int)

# Pipeline propio, construido a partir de lo que declara el RESUMEN (no del código del ingeniero)
def pipe_auditor(modelo):
    prep = ColumnTransformer(
        [("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), TEXTO)],
        remainder="passthrough")
    return Pipeline([("prep", prep), ("modelo", modelo)])


MODELOS = {"Árbol de decisión": DecisionTreeClassifier(random_state=42),
           "Random Forest": RandomForestClassifier(random_state=42)}
CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ---------------------------------------------------------------------------
titulo("1. Reproducibilidad")
ok_repro = True
with tempfile.TemporaryDirectory(prefix="auditor_repro_") as tmp:
    tmp = Path(tmp)
    for s in SCRIPTS_ING:
        shutil.copy2(RAIZ / s, tmp / s)
    (tmp / "datos").mkdir()
    shutil.copy2(CSV, tmp / "datos" / "credit_g.csv")
    consola_md = dict(re.findall(r"```\n\$ python3 (\S+)\n(.*?)```", (RAIZ / "RESULTADOS.md").read_text(), re.S))
    for s in ["tabla_cv.py", "particion_vs_cv.py"]:
        r = subprocess.run([sys.executable, "-B", s], cwd=tmp, capture_output=True, text=True)
        igual_consola = r.stdout == consola_md.get(s)
        print(f"  Ejecutado {s} en carpeta temporal: código de salida {r.returncode}; "
              f"salida de consola idéntica a la copiada en RESULTADOS.md: {igual_consola}")
        ok_repro &= r.returncode == 0 and igual_consola
    for nombre in ["tabla_cv.csv", "particion_unica.csv", "particion_vs_cv.csv"]:
        igual = (tmp / "resultados" / nombre).read_bytes() == (RES / nombre).read_bytes()
        print(f"  {nombre:<22} idéntico byte a byte al entregado: {igual}")
        ok_repro &= igual

print("\n  Recalculo independiente (código propio) frente a resultados/*.csv:")
tabla = pd.read_csv(RES / "tabla_cv.csv").set_index("modelo")
pu = pd.read_csv(RES / "particion_unica.csv")
pvc = pd.read_csv(RES / "particion_vs_cv.csv").set_index("modelo")
pred_oof, proba_oof = {}, {}
for nombre, m in MODELOS.items():
    print(f" [{nombre}]")
    pipe = pipe_auditor(m)
    acc = cross_val_score(pipe, X, y, cv=CV, scoring="accuracy")
    pred = cross_val_predict(pipe, X, y, cv=CV)
    pred_oof[nombre] = pred
    rec_pl = np.array([recall_score(y.iloc[te], pred[te]) for _, te in CV.split(X, y)])
    det = int(((pred == 1) & (y == 1)).sum())
    ok_repro &= comparar("CV exactitud media", acc.mean(), tabla.loc[nombre, "exactitud_media"])
    ok_repro &= comparar("CV exactitud desv (ddof=0)", acc.std(), tabla.loc[nombre, "exactitud_desv"])
    ok_repro &= comparar("CV recall bad global", det / 300, tabla.loc[nombre, "malos_detectados"])
    ok_repro &= comparar("CV recall bad media por pliegue", rec_pl.mean(), tabla.loc[nombre, "malos_detectados"])
    ok_repro &= comparar("CV recall bad desv por pliegue", rec_pl.std(), tabla.loc[nombre, "malos_detectados_desv"])
    ok_n = f"{det}/300" == tabla.loc[nombre, "malos_detectados_n"]
    print(f"  {'OK ' if ok_n else 'DIF'} {'malos detectados (n)':<45} propio={det}/300  entregado={tabla.loc[nombre, 'malos_detectados_n']}")
    ok_repro &= ok_n
    print(f"      exactitud por pliegue: {np.round(acc, 4).tolist()} | recall bad por pliegue: {np.round(rec_pl, 4).tolist()}")
    accs = []
    for s in range(10):
        Xe, Xp, ye, yp = train_test_split(X, y, test_size=0.25, stratify=y, random_state=s)
        p = clone(pipe).fit(Xe, ye)
        pr = p.predict(Xp)
        fila = pu[(pu.modelo == nombre) & (pu.semilla == s)].iloc[0]
        a, r = accuracy_score(yp, pr), recall_score(yp, pr)
        accs.append(a)
        ok_repro &= abs(a - fila.exactitud) <= TOL and abs(r - fila.recall_bad) <= TOL
    accs = np.array(accs)
    print(f"  {'OK ' if ok_repro else 'DIF'} 10 semillas x (exactitud, recall_bad) frente a particion_unica.csv")
    for col, v in [("minimo", accs.min()), ("maximo", accs.max()), ("rango", accs.max() - accs.min()),
                   ("media", accs.mean()), ("desviacion", accs.std()), ("media_cv", acc.mean()),
                   ("desv_cv", acc.std()), ("diferencia_vs_cv", accs.mean() - acc.mean())]:
        ok_repro &= comparar(f"partición única {col}", v, pvc.loc[nombre, col])
    proba_oof[nombre] = cross_val_predict(pipe, X, y, cv=CV, method="predict_proba")[:, 1]
veredictos[1] = "PASA" if ok_repro else "FALLA"

# ---------------------------------------------------------------------------
titulo("2. Fuga de datos")
sys.path.insert(0, str(RAIZ))
import datos as ing_datos      # noqa: E402  (código del ingeniero, solo lectura)
import modelos as ing_modelos  # noqa: E402

Xi, yi, cols_cat_i, cv_i = ing_datos.cargar_datos()
ok_fuga = True
print(f"  'clase' en X del ingeniero: {'clase' in Xi.columns} | forma X {Xi.shape}")
ok_fuga &= "clase" not in Xi.columns
ok_fuga &= yi.equals(y)
print(f"  y del ingeniero == (clase=='bad'): {yi.equals(y)}")
pipe_i = ing_modelos.crear_pipeline(RandomForestClassifier(random_state=42), cols_cat_i)
print(f"  Pasos del Pipeline: {[n for n, _ in pipe_i.steps]} (el codificador es el paso 0 del Pipeline)")
ok_fuga &= isinstance(pipe_i.steps[0][1], ColumnTransformer)
res = cross_validate(ing_modelos.crear_pipeline(DecisionTreeClassifier(random_state=42), cols_cat_i),
                     Xi, yi, cv=cv_i, return_estimator=True, return_indices=True)
ids = set()
faltas_total = 0
for k, (est, tr, te) in enumerate(zip(res["estimator"], res["indices"]["train"], res["indices"]["test"])):
    enc = est.named_steps["prep"].named_transformers_["cat"]
    ids.add(id(enc))
    iguales = all(set(c) == set(Xi.iloc[tr][col].unique()) for col, c in zip(cols_cat_i, enc.categories_))
    faltas = [f"{col}={v}" for col in cols_cat_i for v in set(Xi[col]) - set(Xi.iloc[tr][col])]
    faltas_total += len(faltas)
    entradas = est.named_steps["modelo"].n_features_in_
    print(f"  Pliegue {k}: categorías del codificador == las del entrenamiento del pliegue: {iguales}; "
          f"categorías ausentes en entrenamiento: {faltas or 'ninguna'}; predictores del modelo: {entradas}")
    ok_fuga &= iguales and entradas == 20
print(f"  Codificadores distintos (uno por pliegue): {len(ids)} de 5")
ok_fuga &= len(ids) == 5
# Prueba de sensibilidad: la comprobación SÍ detectaría un codificador ajustado con todo el conjunto,
# pues sus categorías serían las de los 1000 casos. Se cuantifica con partición única:
faltas_pu = 0
for s in range(10):
    Xe, Xp, ye, yp = train_test_split(Xi, yi, test_size=0.25, stratify=yi, random_state=s)
    faltas_pu += sum(len(set(Xp[c]) - set(Xe[c])) for c in cols_cat_i)
print(f"  Categorías de prueba nunca vistas en entrenamiento: CV={faltas_total}, partición única (10 semillas)={faltas_pu}")
# Etiquetas permutadas: sin fuga, la exactitud debe caer al nivel de 'siempre good' o por debajo
rng = np.random.RandomState(0)
y_perm = pd.Series(rng.permutation(yi.to_numpy()), index=yi.index)
acc_perm = cross_val_score(ing_modelos.crear_pipeline(RandomForestClassifier(random_state=42), cols_cat_i),
                           Xi, y_perm, cv=cv_i).mean()
print(f"  RF con etiquetas permutadas (semilla 0): exactitud CV = {acc_perm:.4f} (piso 0.70)")
ok_fuga &= acc_perm <= 0.72
# Correlación máxima de cada predictor numérico con y (una copia de la clase daría |r|=1)
rmax = max(abs(np.corrcoef(Xi[c], yi)[0, 1]) for c in NUM)
print(f"  |r| máximo predictor numérico vs y: {rmax:.3f}")
veredictos[2] = "PASA" if ok_fuga else "FALLA"

# ---------------------------------------------------------------------------
titulo("3. Clase positiva")
ok_pos = True
clase_txt = df["clase"].to_numpy()
for nombre, pred in pred_oof.items():
    pred_txt = np.where(pred == 1, "bad", "good")
    cm = confusion_matrix(clase_txt, pred_txt, labels=["bad", "good"])
    tp, fn, fp, tn = cm[0, 0], cm[0, 1], cm[1, 0], cm[1, 1]
    rec_bad = tp / (tp + fn)
    rec_good = tn / (tn + fp)
    print(f"  {nombre}: filas=real, columnas=predicho, orden [bad, good]")
    print(f"      real bad : {tp:4d} {fn:4d}   -> recall bad  = {tp}/{tp + fn} = {rec_bad:.4f}")
    print(f"      real good: {fp:4d} {tn:4d}   -> recall good = {tn}/{tn + fp} = {rec_good:.4f}")
    rep = tabla.loc[nombre, "malos_detectados"]
    coincide = abs(rec_bad - rep) <= TOL and abs(rec_good - rep) > 0.05
    print(f"      Reportado {rep:.4f} coincide con recall de bad (y no con el de good): {coincide}")
    ok_pos &= coincide
veredictos[3] = "PASA" if ok_pos else "FALLA"

# ---------------------------------------------------------------------------
titulo("4. Coherencia analista -> ingeniero y cifras del RESUMEN")
ok_coh = True
print(f"  cols_cat del ingeniero == 13 del RESUMEN (mismo orden de X): {cols_cat_i == TEXTO}")
ok_coh &= cols_cat_i == TEXTO
num_i = [c for c in Xi.columns if c not in cols_cat_i]
print(f"  numéricas (passthrough) == 7 del RESUMEN: {num_i == NUM}")
ok_coh &= num_i == NUM
enc_i = pipe_i.named_steps["prep"].transformers[0][1]
print(f"  Codificador: {enc_i} | remainder={pipe_i.named_steps['prep'].remainder}")
ok_coh &= (enc_i.handle_unknown == "use_encoded_value" and enc_i.unknown_value == -1
           and pipe_i.named_steps["prep"].remainder == "passthrough")
print(f"  random_state modelos: árbol={ing_modelos.modelos_base()['Árbol de decisión'].random_state}, "
      f"RF={ing_modelos.modelos_base()['Random Forest'].random_state}")

errores_resumen = []
def chequear(desc, real, declarado, tol=0.0):
    ok = (abs(real - declarado) <= tol) if isinstance(real, (int, float, np.floating, np.integer)) else real == declarado
    if not ok:
        errores_resumen.append(f"{desc}: RESUMEN dice {declarado}, real {real}")
    return ok

chequear("forma", df.shape, (1000, 21))
chequear("good", int((df.clase == "good").sum()), 700)
chequear("bad", int((df.clase == "bad").sum()), 300)
print(f"  dtypes numéricas: {sorted(set(str(df[c].dtype) for c in NUM))}")
decl_num = {"duration": (4, 18, 72, 20.90), "credit_amount": (250, 2319.5, 18424, 3271.26),
            "installment_commitment": (1, 3, 4, 2.97), "residence_since": (1, 3, 4, 2.85),
            "age": (19, 33, 75, 35.55), "existing_credits": (1, 1, 4, 1.41), "num_dependents": (1, 1, 2, 1.16)}
for c, (mn, med, mx, me) in decl_num.items():
    chequear(f"{c} mín", df[c].min(), mn); chequear(f"{c} mediana", df[c].median(), med)
    chequear(f"{c} máx", df[c].max(), mx); chequear(f"{c} media", df[c].mean(), me, tol=0.005 + 1e-9)
    print(f"  {c:<24} mín={df[c].min()} mediana={df[c].median()} máx={df[c].max()} media={df[c].mean():.4f}")
decl_dist = {"installment_commitment": [136, 231, 157, 476], "residence_since": [130, 308, 149, 413],
             "existing_credits": [633, 333, 28, 6], "num_dependents": [845, 155]}
for c, v in decl_dist.items():
    real = df[c].value_counts().sort_index().tolist()
    chequear(f"distribución {c}", real, v)
decl_cat = {
    "checking_status": {"no checking": 394, "<0": 274, "0<=X<200": 269, ">=200": 63},
    "credit_history": {"existing paid": 530, "critical/other existing credit": 293, "delayed previously": 88,
                       "all paid": 49, "no credits/all paid": 40},
    "purpose": {"radio/tv": 280, "new car": 234, "furniture/equipment": 181, "used car": 103, "business": 97,
                "education": 50, "repairs": 22, "domestic appliance": 12, "other": 12, "retraining": 9},
    "savings_status": {"<100": 603, "no known savings": 183, "100<=X<500": 103, "500<=X<1000": 63, ">=1000": 48},
    "employment": {"1<=X<4": 339, ">=7": 253, "4<=X<7": 174, "<1": 172, "unemployed": 62},
    "personal_status": {"male single": 548, "female div/dep/mar": 310, "male mar/wid": 92, "male div/sep": 50},
    "other_parties": {"none": 907, "guarantor": 52, "co applicant": 41},
    "property_magnitude": {"car": 332, "real estate": 282, "life insurance": 232, "no known property": 154},
    "other_payment_plans": {"none": 814, "bank": 139, "stores": 47},
    "housing": {"own": 713, "rent": 179, "for free": 108},
    "job": {"skilled": 630, "unskilled resident": 200, "high qualif/self emp/mgmt": 148, "unemp/unskilled non res": 22},
    "own_telephone": {"none": 596, "yes": 404},
    "foreign_worker": {"yes": 963, "no": 37},
}
for c, d in decl_cat.items():
    chequear(f"categorías {c}", df[c].value_counts().to_dict(), d)
chequear("faltantes", int(df.isna().sum().sum()), 0)
chequear("duplicados", int(df.duplicated().sum()), 0)
chequear("duplicados sin clase", int(X.duplicated().sum()), 0)
chequear("espacios", int(sum((df[c].str.strip() != df[c]).sum() for c in TEXTO + ["clase"])), 0)
chequear("texto tipo faltante", int(df[TEXTO].isin(["", "?", "NA", "nan", "None"]).sum().sum()), 0)

# V de Cramér. Numéricas en quintiles con pd.qcut(duplicates="drop"); si los quintiles colapsan
# en un solo intervalo (num_dependents), se usan los valores tal cual. Es la única variante que
# reproduce las cifras del RESUMEN (se probó también con rangos y con valores sin agrupar).
def cramer(a, b):
    t = pd.crosstab(a, b)
    chi2 = chi2_contingency(t, correction=False)[0]
    return np.sqrt(chi2 / (t.values.sum() * (min(t.shape) - 1))), t
vs, puras = {}, []
for c in X.columns:
    col = pd.qcut(df[c], 5, duplicates="drop") if c in NUM else df[c]
    if c in NUM:
        bins = col.nunique()
        if bins < 2:
            col = df[c]
        if bins < 5:
            print(f"  Aviso: {c} no admite 5 quintiles (queda con {bins} intervalo(s){'; se usan valores tal cual' if bins < 2 else ''})")
    v, t = cramer(col, df["clase"])
    vs[c] = v
    puras += [f"{c}={i}" for i, fila in t.iterrows() if (fila == 0).any()]
vs = pd.Series(vs).sort_values(ascending=False)
print("  V de Cramér (top 5):", {k: round(v, 3) for k, v in vs.head(5).items()},
      f"| resto: {vs.iloc[5:].min():.3f}–{vs.iloc[5:].max():.3f}")
decl_v = {"checking_status": 0.352, "credit_history": 0.248, "duration": 0.214,
          "savings_status": 0.190, "purpose": 0.183}
for c, v in decl_v.items():
    chequear(f"V Cramér {c}", round(vs[c], 3), v, tol=0.0005)
chequear("V Cramér resto mín", round(vs.iloc[5:].min(), 3), 0.003, tol=0.0005)
chequear("V Cramér resto máx", round(vs.iloc[5:].max(), 3), 0.154, tol=0.0005)
chequear("categorías 100 % de una clase", puras, [])
# Tasas de bad en variables sensibles
decl_tasas = [("age", "<=25", 190, 80), ("age", ">25", 810, 220),
              ("personal_status", "female div/dep/mar", 310, 109), ("personal_status", "male div/sep", 50, 20),
              ("personal_status", "male mar/wid", 92, 25), ("personal_status", "male single", 548, 146),
              ("foreign_worker", "no", 37, 4), ("foreign_worker", "yes", 963, 296)]
for var, g, n, b in decl_tasas:
    if var == "age":
        m = df.age <= 25 if g == "<=25" else df.age > 25
    else:
        m = df[var] == g
    chequear(f"{var}={g} filas", int(m.sum()), n); chequear(f"{var}={g} bad", int(y[m].sum()), b)
# Pliegues 200/60 (indicación 4)
chequear("pliegues 200/60", [(len(te), int(y.iloc[te].sum())) for _, te in CV.split(X, y)], [(200, 60)] * 5)
print(f"  Cifras del RESUMEN comprobadas con discrepancias: {len(errores_resumen)}")
for e in errores_resumen:
    print("   -", e)
ok_coh &= not errores_resumen
veredictos[4] = "PASA" if ok_coh else "FALLA"

# ---------------------------------------------------------------------------
titulo("5. Partición")
ok_par = (cv_i.n_splits == 5 and cv_i.shuffle and cv_i.random_state == 42 and isinstance(cv_i, StratifiedKFold))
print(f"  cv del ingeniero: {cv_i}")
tests = [te for _, te in cv_i.split(Xi, yi)]
todos = np.concatenate(tests)
print(f"  Pliegues de prueba disjuntos y cubren las 1000 filas: {len(set(todos)) == 1000 == len(todos)}")
print(f"  (filas, bad) por pliegue: {[(len(t), int(yi.iloc[t].sum())) for t in tests]}")
ok_par &= len(set(todos)) == 1000 == len(todos)
import validacion as ing_val  # noqa: E402
print(f"  Semillas de la partición única: {ing_val.SEMILLAS_PARTICION}")
conjuntos = []
for s in ing_val.SEMILLAS_PARTICION:
    _, Xp, _, yp = train_test_split(Xi, yi, test_size=0.25, stratify=yi, random_state=s)
    conjuntos.append(frozenset(Xp.index))
    ok_par &= len(Xp) == 250 and int(yp.sum()) == 75
print(f"  10 semillas distintas: {len(set(ing_val.SEMILLAS_PARTICION)) == 10}; "
      f"10 conjuntos de prueba distintos: {len(set(conjuntos)) == 10}; cada uno 250 filas / 75 bad: {ok_par}")
ok_par &= len(set(ing_val.SEMILLAS_PARTICION)) == 10 and len(set(conjuntos)) == 10
veredictos[5] = "PASA" if ok_par else "FALLA"

# ---------------------------------------------------------------------------
titulo("6. Línea base 'siempre good'")
dummy = DummyClassifier(strategy="constant", constant=0)
acc_d = cross_val_score(dummy, X, y, cv=CV)
pred_d = cross_val_predict(dummy, X, y, cv=CV)
print(f"  Siempre good: exactitud CV {acc_d.mean():.4f} (por pliegue {acc_d.tolist()}), recall bad {recall_score(y, pred_d):.4f}")
for nombre, m in MODELOS.items():
    acc = cross_val_score(pipe_auditor(m), X, y, cv=CV)
    dif = acc - acc_d
    sup = int((acc > acc_d).sum())
    pu_m = pu[pu.modelo == nombre]
    print(f"  {nombre}: exactitud {acc.mean():.4f} | diferencia con piso {dif.mean():+.4f} "
          f"(± {dif.std(ddof=1):.4f} entre pliegues) | pliegues que superan el piso: {sup}/5 | "
          f"semillas de partición única que superan 0.70: {int((pu_m.exactitud > 0.70).sum())}/10 | "
          f"malos detectados {int(((pred_oof[nombre] == 1) & (y == 1)).sum())}/300 vs 0/300")
veredictos[6] = "PASA"

# ---------------------------------------------------------------------------
titulo("7. Subgrupos (predicciones fuera de pliegue de la CV)")
def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h

grupos_vars = {"housing": df["housing"], "personal_status": df["personal_status"],
               "age (extra)": np.where(df.age <= 25, "<=25", ">25"),
               "foreign_worker (extra)": df["foreign_worker"]}
pocos = []
for nombre, pred in pred_oof.items():
    print(f"\n  [{nombre}]")
    print(f"  {'variable':<23}{'grupo':<20}{'n':>5}{'bad':>5}{'exact.':>8}{'detect.':>9}{'recall bad':>11}  IC95% recall   good rechaz.  aviso")
    for var, g in grupos_vars.items():
        g = pd.Series(np.asarray(g), index=df.index)
        for nivel in sorted(g.unique()):
            m = (g == nivel).to_numpy()
            n, nb = int(m.sum()), int(y[m].sum())
            det = int(((pred[m] == 1) & (y[m] == 1)).sum())
            acc = accuracy_score(y[m], pred[m])
            lo, hi = wilson(det, nb)
            ng = n - nb
            fp = int(((pred[m] == 1) & (y[m] == 0)).sum())
            aviso = "POCOS CASOS" if (n < 100 or nb < 30) else ""
            if aviso and nombre == "Random Forest":
                pocos.append(f"{var}={nivel} (n={n}, bad={nb})")
            print(f"  {var:<23}{nivel:<20}{n:>5}{nb:>5}{acc:>8.3f}{det:>5}/{nb:<3}{det / nb:>11.3f}  [{lo:.2f}, {hi:.2f}]"
                  f"  {fp:>3}/{ng:<3}={fp / ng:.3f}  {aviso}")
print(f"\n  Grupos con pocos casos (n<100 o <30 bad): {pocos}")
veredictos[7] = "PASA"

# ---------------------------------------------------------------------------
titulo("8. Lectura de negocio")
print("  Matriz de coste del German Credit (documentación del conjunto): bad clasificado como good = 5, good como bad = 1.")
filas = [("Siempre good", pred_d)] + list(pred_oof.items())
for nombre, pred in filas:
    fn = int(((pred == 0) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
    print(f"  {nombre:<18} exactitud {accuracy_score(y, pred):.3f} | malos no detectados {fn:3d} | buenos rechazados {fp:3d} | coste {5 * fn + fp:4d} ({(5 * fn + fp) / 1000:.3f} por solicitud)")
print("\n  Ilustrativo (mismos modelos y semillas; solo cambia el umbral de decisión sobre probabilidades fuera de pliegue):")
for nombre, pr in proba_oof.items():
    for u in [0.5, 0.4, 0.3, 1 / 6]:
        pred = (pr >= u).astype(int) if u != 0.5 else (pr > 0.5).astype(int)
        fn = int(((pred == 0) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
        print(f"  {nombre:<18} umbral {u:.3f}: exactitud {accuracy_score(y, pred):.3f} | recall bad {recall_score(y, pred):.3f} | coste {5 * fn + fp}")
veredictos[8] = "PASA"

# ---------------------------------------------------------------------------
titulo("Extra: referencias de documentación")
for doc, ref in [("README.md", "docs/flujo.md"), ("ROLES.md", "evidencia/bitacora_flujo.md")]:
    citado = ref in (RAIZ / doc).read_text()
    print(f"  {doc} cita {ref}: {citado} | existe: {(RAIZ / ref).exists()}")
md_req = (RAIZ / "requirements.txt").read_text().split()
print(f"  requirements.txt: {md_req} (solo mínimos; cifras obtenidas con las versiones de la sección 0)")

titulo("Integridad: el proyecto no se modificó")
md5_res_despues = {p.name: md5(p) for p in sorted(RES.glob("*.csv"))}
print(f"  MD5 datos sin cambios: {md5(CSV) == md5_antes} | resultados/ sin cambios: {md5_res_despues == md5_res_antes}")
titulo("Resumen de veredictos (cálculo automático)")
for k in sorted(veredictos):
    print(f"  Revisión {k}: {veredictos[k]}")
print("  (Revisiones 6–8 son de lectura: PASA significa que la comprobación se pudo hacer; "
      "el juicio está en AUDIT_REPORT.md.)")
