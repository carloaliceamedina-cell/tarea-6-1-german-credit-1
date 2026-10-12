# Resumen de datos — German Credit (`datos/credit_g.csv`)

Rol: analista de datos · MAI 540, Tarea 6.1 · Fecha: 2026-10-12

El archivo se describió tal como está, sin transformarlo (solo lectura con
`pandas.read_csv`). Huella MD5 del archivo leído:
`19d37d4238836d135ab13d73dc42d5e4` (la misma antes y después del análisis).
Todas las cifras de este resumen salen de cálculos ejecutados con pandas sobre
ese archivo.

## Tamaño y clase

- **Filas:** 1,000 · **Columnas:** 21 (20 predictoras + 1 objetivo).
- **Columna objetivo:** `clase` (nombre exacto, en minúscula).
- **Valores exactos de `clase`:** `good` y `bad` (sin espacios ni variantes).

| clase | filas | proporción |
|---|---:|---:|
| `good` | 700 | 0.70 |
| `bad` | 300 | 0.30 |

- **Clase de interés (positiva):** `bad` → codificar `y = 1` si `clase == "bad"`.
- **Piso a superar:** decir siempre `good` da una exactitud de **0.70** y
  detecta **0 de 300** malos (recall de `bad` = 0.00). Un modelo con exactitud
  cercana a 0.70 no aporta nada aunque el número "parezca alto".

## Columnas

**Numéricas (7, tipo entero):**

| columna | mín | mediana | máx | media | notas |
|---|---:|---:|---:|---:|---|
| `duration` | 4 | 18 | 72 | 20.90 | meses |
| `credit_amount` | 250 | 2,319.5 | 18,424 | 3,271.26 | asimétrica a la derecha |
| `installment_commitment` | 1 | 3 | 4 | 2.97 | ordinal 1–4 (136/231/157/476) |
| `residence_since` | 1 | 3 | 4 | 2.85 | ordinal 1–4 (130/308/149/413) |
| `age` | 19 | 33 | 75 | 35.55 | **sensible** |
| `existing_credits` | 1 | 1 | 4 | 1.41 | 1:633, 2:333, 3:28, 4:6 |
| `num_dependents` | 1 | 1 | 2 | 1.16 | 1:845, 2:155 |

**Con texto (13 predictoras + `clase`), con número de categorías:**

| columna | categorías | valores (filas) |
|---|---:|---|
| `checking_status` | 4 | no checking 394 · <0 274 · 0<=X<200 269 · >=200 63 |
| `credit_history` | 5 | existing paid 530 · critical/other existing credit 293 · delayed previously 88 · all paid 49 · no credits/all paid 40 |
| `purpose` | 10 | radio/tv 280 · new car 234 · furniture/equipment 181 · used car 103 · business 97 · education 50 · repairs 22 · domestic appliance 12 · other 12 · retraining 9 |
| `savings_status` | 5 | <100 603 · no known savings 183 · 100<=X<500 103 · 500<=X<1000 63 · >=1000 48 |
| `employment` | 5 | 1<=X<4 339 · >=7 253 · 4<=X<7 174 · <1 172 · unemployed 62 |
| `personal_status` | 4 | male single 548 · female div/dep/mar 310 · male mar/wid 92 · male div/sep 50 — **sensible** |
| `other_parties` | 3 | none 907 · guarantor 52 · co applicant 41 |
| `property_magnitude` | 4 | car 332 · real estate 282 · life insurance 232 · no known property 154 |
| `other_payment_plans` | 3 | none 814 · bank 139 · stores 47 |
| `housing` | 3 | own 713 · rent 179 · for free 108 |
| `job` | 4 | skilled 630 · unskilled resident 200 · high qualif/self emp/mgmt 148 · unemp/unskilled non res 22 |
| `own_telephone` | 2 | none 596 · yes 404 |
| `foreign_worker` | 2 | yes 963 · no 37 — **sensible** |
| `clase` | 2 | good 700 · bad 300 (objetivo, no es predictora) |

## Calidad de los datos

- **Valores faltantes:** 0 en las 21 columnas (también se buscaron `""`, `"?"`,
  `"NA"`, `"nan"` y `"None"` como texto: 0 casos).
- **Espacios al inicio/final en columnas de texto:** 0 casos.
- **Filas duplicadas:** 0 (y 0 si se ignora `clase`, así que no hay
  solicitudes idénticas con etiqueta contradictoria).
- **Categorías poco frecuentes:** `purpose = retraining` (9 filas),
  `domestic appliance` (12), `other` (12); `job = unemp/unskilled non res` (22);
  `existing_credits = 4` (6). En particiones pequeñas pueden faltar en el
  entrenamiento.
- **Variables ordinales guardadas como texto:** `checking_status`,
  `savings_status` y `employment` tienen orden natural, pero sus etiquetas no
  se ordenan bien alfabéticamente (p. ej. `no checking`, `no known savings`,
  `unemployed`). Se dejan tal cual; el orden de codificación no afecta a los
  árboles más allá de los cortes posibles.

## Riesgos

**Fuga de información: no se encontró ninguna columna que contenga o derive de
`clase`.** Comprobación ejecutada: para cada predictora (numéricas agrupadas en
quintiles) se calculó la tabla cruzada con `clase` y la V de Cramér. Ninguna
categoría es 100 % de una sola clase y la asociación más alta es moderada:

| columna | V de Cramér con `clase` |
|---|---:|
| `checking_status` | 0.352 |
| `credit_history` | 0.248 |
| `duration` | 0.214 |
| `savings_status` | 0.190 |
| `purpose` | 0.183 |
| resto (15 columnas) | entre 0.003 y 0.154 |

La fuga real que hay que evitar es **de procedimiento**: ajustar el codificador
(o cualquier preparación) con todos los datos antes de dividir.

**Variables sensibles** (no deberían usarse para decidir sobre personas; sí
para auditar por subgrupos). Tasas de `bad` observadas:

| variable | grupo | filas | `bad` | tasa `bad` |
|---|---|---:|---:|---:|
| `age` | <= 25 años | 190 | 80 | 0.421 |
| `age` | > 25 años | 810 | 220 | 0.272 |
| `personal_status` | female div/dep/mar | 310 | 109 | 0.352 |
| `personal_status` | male div/sep | 50 | 20 | 0.400 |
| `personal_status` | male mar/wid | 92 | 25 | 0.272 |
| `personal_status` | male single | 548 | 146 | 0.266 |
| `foreign_worker` | no | 37 | 4 | 0.108 |
| `foreign_worker` | yes | 963 | 296 | 0.307 |

- `personal_status` mezcla sexo y estado civil; no existe la categoría
  "mujer soltera", así que no permite separar limpiamente el efecto del sexo.
- `foreign_worker = no` tiene solo 37 filas (4 `bad`): cualquier métrica en ese
  subgrupo será muy inestable.
- El enunciado del flujo pide medir árbol y Random Forest con las 20
  predictoras; usar estas tres columnas en el modelo es una decisión que debe
  quedar documentada y revisada por el auditor.

**Desbalance:** 70/30. La exactitud sola esconde si el modelo detecta a los
malos (ver piso arriba).

## Indicaciones para el ingeniero de modelos

1. **Objetivo:** `y = (df["clase"] == "bad").astype(int)`; quitar `clase` de `X`.
   Nunca usar `clase` como predictora.
2. **Columnas a codificar (13):** `checking_status`, `credit_history`,
   `purpose`, `savings_status`, `employment`, `personal_status`,
   `other_parties`, `property_magnitude`, `other_payment_plans`, `housing`,
   `job`, `own_telephone`, `foreign_worker`. Codificarlas con
   `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)`
   **dentro** del `Pipeline` (vía `ColumnTransformer`) para que se ajuste en
   cada pliegue; `handle_unknown` es necesario por las categorías raras.
3. **Numéricas (7) en `passthrough`:** `duration`, `credit_amount`,
   `installment_commitment`, `residence_since`, `age`, `existing_credits`,
   `num_dependents`. No hace falta imputar ni escalar (no hay faltantes y los
   árboles no requieren escala).
4. **Semilla y estratificación:** `random_state=42` en modelos y en
   `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. Verifiqué que
   esa partición deja 200 filas y exactamente 60 `bad` en cada pliegue de
   prueba. En la partición única usar `stratify=y` con semillas 0–9 fijadas
   antes de ver resultados.
5. **Métricas que no deben faltar:** exactitud comparada contra el piso de
   **0.70**, y el **recall de la clase `bad`** (proporción de malos
   detectados), con `pos_label` = `bad` (y = 1). Reportar media y desviación
   entre pliegues.
6. Dejar anotado en `RESULTADOS.md` que `age`, `personal_status` y
   `foreign_worker` se usaron como predictoras (si se usan), para que el
   auditor las evalúe por subgrupo.

Entregado a: ingeniero-de-modelos
