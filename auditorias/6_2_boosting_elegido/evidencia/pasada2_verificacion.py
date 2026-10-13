"""Segunda pasada (Skill v2.2-r): comprueba las correcciones de V6.2 y V4.1,
vuelve a aplicar V4.2 con las reglas fijadas, re-ejecuta los scripts (V0.1) y pytest.

Ejecutar desde la raíz del proyecto:
    python3 -B auditorias/6_2_boosting_elegido/evidencia/pasada2_verificacion.py

No escribe en el proyecto: todo se ejecuta en /tmp/claude-0/auditoria_6_2/pasada2/copia/.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
RAIZ = Path.cwd()
COPIA = Path("/tmp/claude-0/auditoria_6_2/pasada2/copia")
PYTEST_PATH = "/root/.local/share/uv/tools/pytest/lib/python3.13/site-packages"
EVID = RAIZ / "auditorias/6_2_boosting_elegido/evidencia"

MODULOS = ["datos.py", "modelos.py", "validacion.py", "busqueda.py", "curvas.py"]
SCRIPTS = {
    "defecto_vs_afinado.py": ("6_2_salida_defecto_vs_afinado.txt", ["busqueda_arbol.csv"]),
    "numero_honesto.py": ("6_2_salida_numero_honesto.txt", ["numero_honesto.csv"]),
    "comparar_tres.py": (None, ["comparacion_modelos.csv"]),  # columna de tiempo variable
    "sin_variables_sensibles.py": ("6_2_salida_sin_sensibles.txt", ["sin_variables_sensibles.csv"]),
    "curvas_comparadas.py": ("6_2_salida_curvas.txt", ["curvas_aprendizaje.csv"]),
    "auditoria_subgrupos.py": ("6_2_salida_auditoria_subgrupos.txt", ["auditoria_subgrupos.csv"]),
}


def titulo(t):
    print(f"\n{'=' * 90}\n{t}\n{'=' * 90}")


if COPIA.exists():
    shutil.rmtree(COPIA)
COPIA.mkdir(parents=True)
for f in MODULOS + list(SCRIPTS) + ["pytest.ini"]:
    shutil.copy2(RAIZ / f, COPIA / f)
shutil.copytree(RAIZ / "datos", COPIA / "datos")
shutil.copytree(RAIZ / "tests", COPIA / "tests")
(COPIA / "resultados").mkdir()

# ---------------------------------------------------------------------------
titulo("V0.1 Re-ejecución de los scripts (con el datos.py corregido)")
for script, (txt, csvs) in SCRIPTS.items():
    r = subprocess.run([sys.executable, "-B", script], cwd=COPIA, capture_output=True, text=True)
    print(f"\n--- {script}: código de salida {r.returncode} | Traceback: {'Traceback' in r.stderr}")
    if txt:
        print(f"  salida idéntica a evidencia/{txt}: {r.stdout.strip() == (RAIZ / 'evidencia' / txt).read_text().strip()}")
    for c in csvs:
        nuevo, viejo = pd.read_csv(COPIA / "resultados" / c), pd.read_csv(RAIZ / "resultados" / c)
        cols = [k for k in viejo.columns if k != "tiempo_ajuste_s"]
        try:
            pd.testing.assert_frame_equal(nuevo[cols], viejo[cols], check_exact=False, atol=1e-9)
            print(f"  resultados/{c} reproducido (sin tiempo): True")
        except AssertionError as e:
            print(f"  resultados/{c} reproducido (sin tiempo): False -> {e}")
    if script == "auditoria_subgrupos.py":
        for linea in r.stdout.strip().splitlines():
            print("   |", linea)

# ---------------------------------------------------------------------------
titulo("pytest (en la copia; -p no:cacheprovider para no crear .pytest_cache)")
env = dict(os.environ, PYTHONPATH=PYTEST_PATH, PYTHONDONTWRITEBYTECODE="1")
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-v", "-p", "no:cacheprovider"],
                   cwd=COPIA, capture_output=True, text=True, env=env)
print(r.stdout.strip())
print("código de salida:", r.returncode)

# ---------------------------------------------------------------------------
titulo("V6.2 validar_datos(): existe, se llama antes del fit y rechaza datos defectuosos")
sys.path.insert(0, str(COPIA))
import datos  # noqa: E402  (copia idéntica al datos.py del proyecto)

fuente = (RAIZ / "datos.py").read_text().splitlines()
for i, l in enumerate(fuente, 1):
    if "def validar_datos" in l or "validar_datos(df)" in l or "def cargar_datos" in l or "pd.read_csv" in l:
        print(f"  datos.py:{i}: {l.strip()}")
print("  cargar_datos_sin_sensibles() pasa por cargar_datos():",
      "cargar_datos(ruta)" in (RAIZ / "datos.py").read_text())
df = pd.read_csv(RAIZ / "datos" / "credit_g.csv")
datos.validar_datos(df)
print("  CSV real: acepta sin error")
casos = {
    "sin columna clase": df.drop(columns="clase"),
    "clase con valor 'regular'": df.assign(clase=df["clase"].where(df.index != 0, "regular")),
    "un faltante en credit_amount": df.assign(credit_amount=df["credit_amount"].where(df.index != 5, np.nan)),
    "una fila menos": df.iloc[:-1],
    "una columna extra": df.assign(extra=1),
}
for nombre, d in casos.items():
    try:
        datos.validar_datos(d)
        print(f"  {nombre:<32} -> NO lanzó error")
    except ValueError as e:
        print(f"  {nombre:<32} -> ValueError: {e}")
no_cubre = {
    "'clase' con espacios (' bad')": df.assign(clase=df["clase"].where(df.index != 0, " bad")),
    "age = -5 (fuera de rango)": df.assign(age=df["age"].where(df.index != 0, -5)),
    "housing con categoría nueva": df.assign(housing=df["housing"].where(df.index != 0, "boat")),
}
print("  Casos que no forman parte del contrato declarado (solo informativos):")
for nombre, d in no_cubre.items():
    try:
        datos.validar_datos(d)
        print(f"    {nombre:<32} -> acepta")
    except ValueError as e:
        print(f"    {nombre:<32} -> ValueError: {e}")

# ---------------------------------------------------------------------------
titulo("V4.1 / V4.2 con la Skill v2.2-r (n = positivos reales; brecha hacia abajo; mejor elegible por variable)")
proy = pd.read_csv(RAIZ / "resultados" / "auditoria_subgrupos.csv")
propio = pd.read_csv(EVID / "v4_subgrupos_modelo_auditado.csv")
propio = propio[propio.variable.isin(["housing", "personal_status", "edad"])]
m = proy.merge(propio, on=["variable", "grupo"], suffixes=("_proy", "_aud"))
m["d_recall"] = (m["malos_detectados"] - m["recall_bad"]).abs()
m["d_exact"] = (m["exactitud_proy"] - m["exactitud_aud"]).abs()
m["d_fpr"] = (m["buenos_rechazados"] - m["prop_good_rechazados"]).abs()
print("  Proyecto (resultados/auditoria_subgrupos.csv) frente a la reproducción del auditor (pasada 1):")
print(m[["variable", "grupo", "n_proy", "n_bad_proy", "malos_detectados", "recall_bad", "d_recall", "d_exact", "d_fpr"]]
      .to_string(index=False, float_format="%.4f"))
print(f"  Filas: {len(proy)} | máx. |Δ| recall {m.d_recall.max():.4f} | exactitud {m.d_exact.max():.4f} | buenos rechazados {m.d_fpr.max():.4f}"
      f" | n y n_bad idénticos: {bool((m.n_proy == m.n_aud).all() and (m.n_bad_proy == m.n_bad_aud).all())}")

GLOBAL = 0.640
p = proy.copy()
p["elegible"] = p["n_bad"] >= 30                               # n = positivos reales (recall)
p["brecha"] = GLOBAL - p["malos_detectados"]                   # solo hacia abajo
mejor = p[p.elegible].groupby("variable")["malos_detectados"].max()
p["cociente"] = p["malos_detectados"] / p["variable"].map(mejor)
p["veredicto"] = np.where(~p.elegible, "lista, no decide",
                          np.where((p.brecha <= 0.05) & (p.cociente >= 0.80), "PASA", "FALLA"))
print(f"\n  Global (todas las predicciones fuera de pliegue juntas) = {GLOBAL:.3f}")
print(p[["variable", "grupo", "n", "n_bad", "malos_detectados", "brecha", "cociente", "buenos_rechazados", "veredicto"]]
      .to_string(index=False, float_format="%.3f"))
el = p[p.elegible]
print(f"\n  Elegibles {len(el)} | FALLA {int((el.veredicto == 'FALLA').sum())} | brecha máx {el.brecha.max():.3f}"
      f" | cociente mín {el.cociente.min():.3f} -> V4.2 = {'FALLA' if (el.veredicto == 'FALLA').any() else 'PASA'}")
print("  V1.1 (CSV nuevo) métricas en [0,1]:",
      bool(proy[["exactitud", "malos_detectados", "buenos_rechazados"]].apply(lambda s: s.between(0, 1)).all().all()))

print("\n__pycache__ / .pytest_cache en la copia:",
      [str(x) for x in COPIA.rglob("__pycache__")] + [str(x) for x in COPIA.rglob(".pytest_cache")])
