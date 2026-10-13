"""V0.1 — Ejecución de los scripts de la Tarea 6.2 en una COPIA del proyecto.

Ejecutar desde la raíz del proyecto:
    python3 -B auditorias/6_2_boosting_elegido/evidencia/v0_ejecucion.py

No escribe dentro del proyecto: copia scripts y datos a
/tmp/claude-0/auditoria_6_2/copia/, ejecuta allí cada script con `python3 -B`
(sin __pycache__) y compara:
  - la salida estándar con evidencia/6_2_salida_*.txt del proyecto;
  - los CSV generados con resultados/*.csv del proyecto (sin la columna de
    tiempo, que depende del equipo).
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path.cwd()
COPIA = Path("/tmp/claude-0/auditoria_6_2/copia")
MODULOS = ["datos.py", "modelos.py", "validacion.py", "busqueda.py", "curvas.py"]
SCRIPTS = {  # script -> (evidencia de texto, CSV que escribe)
    "defecto_vs_afinado.py": ("6_2_salida_defecto_vs_afinado.txt", ["busqueda_arbol.csv"]),
    "numero_honesto.py": ("6_2_salida_numero_honesto.txt", ["numero_honesto.csv"]),
    "comparar_tres.py": ("6_2_salida_comparar_tres.txt", ["comparacion_modelos.csv"]),
    "sin_variables_sensibles.py": ("6_2_salida_sin_sensibles.txt", ["sin_variables_sensibles.csv"]),
    "curvas_comparadas.py": ("6_2_salida_curvas.txt", ["curvas_aprendizaje.csv"]),
}

if COPIA.exists():
    shutil.rmtree(COPIA)
COPIA.mkdir(parents=True)
for f in MODULOS + list(SCRIPTS):
    shutil.copy2(RAIZ / f, COPIA / f)
shutil.copytree(RAIZ / "datos", COPIA / "datos")
(COPIA / "resultados").mkdir()

print(f"Python {sys.version.split()[0]} | copia de trabajo: {COPIA}\n")

print("== Importación de módulos ==")
for m in MODULOS:
    r = subprocess.run([sys.executable, "-B", "-c", f"import {m[:-3]}"], cwd=COPIA,
                       capture_output=True, text=True)
    print(f"  {m:<16} código de salida {r.returncode} {r.stderr.strip()[-200:]}")

print("\n== Ejecución de scripts ==")
for script, (txt, csvs) in SCRIPTS.items():
    r = subprocess.run([sys.executable, "-B", script], cwd=COPIA, capture_output=True, text=True)
    error = "Traceback" in r.stderr or r.returncode != 0
    print(f"\n--- {script}: código de salida {r.returncode} | error: {error}")
    if r.stderr.strip():
        print("  stderr (últimas líneas):", r.stderr.strip().splitlines()[-3:])
    evid = (RAIZ / "evidencia" / txt).read_text().strip()
    if script == "comparar_tres.py":
        # la columna de tiempo cambia en cada equipo: se compara por CSV
        print(f"  salida vs evidencia/{txt}: se compara por CSV (columna de tiempo variable)")
    else:
        igual = r.stdout.strip() == evid
        print(f"  salida idéntica a evidencia/{txt}: {igual}")
        if not igual:
            print("  SALIDA OBTENIDA:\n" + r.stdout)
    for c in csvs:
        nuevo = pd.read_csv(COPIA / "resultados" / c)
        viejo = pd.read_csv(RAIZ / "resultados" / c)
        cols = [k for k in viejo.columns if k != "tiempo_ajuste_s"]
        try:
            pd.testing.assert_frame_equal(nuevo[cols], viejo[cols], check_exact=False, atol=1e-9)
            print(f"  resultados/{c} reproducido (sin tiempo): True")
        except AssertionError as e:
            print(f"  resultados/{c} reproducido (sin tiempo): False -> {e}")
    print("  salida:")
    for linea in r.stdout.strip().splitlines():
        print("   |", linea)

print("\n__pycache__ en la copia:", [str(p) for p in COPIA.rglob("__pycache__")])
