"""Convierte el archivo descargado de Moodle (credit_g.csv.xlsx) a datos/credit_g.csv.

El archivo de Moodle llegó como libro de Excel con una hoja "credit_g".
Se convierte sin tocar valores: mismas 1,000 filas, 21 columnas y orden.
Uso: python datos/convertir_desde_xlsx.py ruta/al/credit_g.csv.xlsx
"""
import sys
from pathlib import Path

import pandas as pd

origen = Path(sys.argv[1])
destino = Path(__file__).with_name("credit_g.csv")
df = pd.read_excel(origen, sheet_name="credit_g")
df.to_csv(destino, index=False)
print(f"{origen.name} -> {destino} | forma {df.shape}")
