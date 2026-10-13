# AUDIT_REPORT — Boosting 5:1 sin variables sensibles (German Credit, Tarea 6.2)

| Campo | Valor |
|---|---|
| Archivos auditados | `datos.py`, `modelos.py`, `validacion.py`, `busqueda.py`, `defecto_vs_afinado.py`, `numero_honesto.py`, `comparar_tres.py`, `sin_variables_sensibles.py`, `curvas.py`, `curvas_comparadas.py`; salidas en `resultados/*.csv` y `evidencia/6_2_salida_*.txt`; plan previo `PLAN_6_2.md`; descripción de datos `datos/RESUMEN.md` |
| Fecha | 2026-10-12 |
| Versión de la Skill | `auditoria-modelos` v2.1-r (`.claude/skills/auditoria-modelos/SKILL.md`) |
| Modelo auditado | `HistGradientBoostingClassifier(class_weight={0: 1, 1: 5}, random_state=42)` (`modelos.py:58-59`) dentro de `crear_pipeline` (`modelos.py:9-23`), entrenado sin `age`, `personal_status` ni `foreign_worker` (`datos.py:25-33`), 17 predictoras |
| Protocolo | `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` de `datos.cargar_datos()` (`datos.py:19`); predicciones fuera de pliegue con `cross_val_predict` |
| Objetivo y clase positiva | `clase`; positiva = `bad` → y = 1 (`datos.py:14`) |
| Costo del error | aprobar un malo (FN) = 5, rechazar un bueno (FP) = 1 (`PLAN_6_2.md:34-36`, `validacion.py:51-61`) |
| Métrica prioritaria | recall de `bad` (proporción de malos detectados) |
| Subgrupos | `housing`, `personal_status`, edad (`age` ≤ 25 / > 25) y, añadido por el auditor, `foreign_worker`. Las sensibles no entran al modelo; solo se usan para auditar |
| Supuestos | (a) Para V4.2 el n relevante es el número de `bad` del subgrupo. (b) La brecha de V4.2 es de un solo lado (global − subgrupo). (c) El "mejor subgrupo" del cociente se busca dentro de la misma variable y solo entre subgrupos con n_bad ≥ 30. Las decisiones (b) y (c) se tomaron por mi cuenta; se explican en Limitaciones y `evidencia/v4_subgrupos.txt` muestra qué cambia con las alternativas |
| Entorno | Python 3.13.16, pandas 3.0.5, numpy 2.5.3, scikit-learn 1.9.1 (coincide con `versiones_exactas.txt`) |

## Resumen

**PASA 16 · FALLA 1 · NSPD 1** (18 verificaciones).

El hallazgo más grave es que **el proyecto no calcula la métrica prioritaria por subgrupo** para el modelo que recomienda (V4.1 FALLA). `PLAN_6_2.md:57-60` deja ese paso a la auditoría. Al reproducirla, el modelo **cumple los umbrales de V4.2** en los 8 subgrupos con al menos 30 `bad`: la brecha más grande es 0.034 y el cociente más bajo es 0.843. Aun así, los intervalos son anchos y la proporción de buenos rechazados no es pareja entre grupos (ver V4). No existe una función de validación de datos que se ejecute antes del `fit` (V6.2 NSPD).

## Verificaciones

| ID | Verificación | Resultado | Evidencia |
|---|---|---|---|
| V0.1 | Ejecución | **PASA** | Los 5 módulos se importan sin error y los 5 scripts terminan con código 0. La salida coincide byte a byte con `evidencia/6_2_salida_*.txt`, salvo la columna de tiempo de `comparar_tres.py`. Los 5 CSV se reproducen sin contar la columna de tiempo: `evidencia/v0_ejecucion.txt`. Se ejecutaron en una copia; ver Limitaciones |
| V1.1 | Rango | **PASA** | Las 13 columnas de métricas de los 5 CSV de la 6.2 están en [0, 1]. Mínimo 0.0058 (desviación) y máximo 1.000 (exactitud de entrenamiento): `evidencia/v1_v3_metricas_y_fuga.txt` (V1.1) |
| V1.2 | Coherencia | **PASA** | Matriz propia del modelo auditado: TN 534, FP 166, FN 108, TP 192. Da exactitud 0.726, recall 0.640 y costo 706, igual que `resultados/sin_variables_sensibles.csv` fila 2 (Δ = 0.000). Las 8 filas de `comparacion_modelos.csv` y `sin_variables_sensibles.csv` también coinciden al recalcularlas desde FN y FP: `evidencia/v1_v3_metricas_y_fuga.txt` (V1.2) |
| V1.3 | Desbalance | **PASA** | p_min = 0.300 < 0.8/K = 0.400, y se reporta la métrica por clase (recall de `bad`): `validacion.py:17-30`, `comparar_tres.py:29`, `evidencia/v1_v3_metricas_y_fuga.txt` (V1.3) |
| V1.4 | Costo del error | **PASA** | La métrica prioritaria y el costo 5·FN + 1·FP se justifican con la matriz de costo del conjunto (`PLAN_6_2.md:34-41,43-50`). Se comparan con "siempre good" (exactitud 0.700, recall 0.00, costo 1500) en `comparar_tres.py:48`. Lo recalculé: el modelo auditado tiene costo 706, el 47.1 % de la línea base (`evidencia/v1_v3_metricas_y_fuga.txt`, V1.4) |
| V2.1 | Orden | **PASA** | `OrdinalEncoder` dentro de `ColumnTransformer` + `Pipeline` (`modelos.py:15-23`). No hay `fit_transform` fuera del Pipeline (`evidencia/inventario.txt`). En cada pliegue, las categorías aprendidas son exactamente las del entrenamiento (`evidencia/v1_v3_metricas_y_fuga.txt`, V2.1/V3.1) |
| V2.2 | Semilla | **PASA** | `random_state=42` en la CV (`datos.py:19`) y en todos los modelos (`modelos.py:29-30,47-49,57,59`). También se fijan semillas en `train_test_split` (`validacion.py:38`, `busqueda.py:21`) y en la CV externa (`busqueda.py:28`). `early_stopping='auto'` queda desactivado con n = 800 < 10 000 (`evidencia/v1_v3_metricas_y_fuga.txt`) |
| V2.3 | Estratificación | **PASA** | `StratifiedKFold` (`datos.py:19`, `busqueda.py:28`); `stratify=y` (`validacion.py:38`, `busqueda.py:21`). Cada pliegue de prueba tiene 200 filas y 60 `bad` (`evidencia/v1_v3_metricas_y_fuga.txt`) |
| V2.4 | Misma partición | **PASA** | Todos los modelos comparados usan el `cv` de `cargar_datos()` (`comparar_tres.py:38,22-23`; `sin_variables_sensibles.py:13,18-19`; `curvas_comparadas.py:13,19,23`). Los índices de prueba son idénticos con X completo y con X sin sensibles (`evidencia/v1_v3_metricas_y_fuga.txt`, V2.4) |
| V2.5 | Hiperparámetros | **PASA** | El modelo auditado no se presenta con hiperparámetros elegidos por CV. `class_weight={0:1, 1:5}` sale de la matriz de costo y se fijó antes de medir (`PLAN_6_2.md:38-41`, `modelos.py:37-39`); el resto queda por defecto. El único hiperparámetro presentado como elegido es el del árbol afinado, `max_depth=5, min_samples_leaf=1`, que sale de `GridSearchCV` con la CV (`busqueda.py:13-14`, `evidencia/6_2_salida_defecto_vs_afinado.txt`) y se reutiliza fijo (`comparar_tres.py:17`). Su optimismo se controló con CV anidada (0.740 ± 0.013) y con una prueba reservada (`busqueda.py:18-31`, `evidencia/v0_ejecucion.txt`) |
| V3.1 | Transformaciones | **PASA** | Todas las métricas de generalización salen de `cross_validate`, `cross_val_predict`, `cross_val_score` o `learning_curve` sobre el Pipeline completo (`comparar_tres.py:22-23`, `validacion.py:13,23`, `curvas.py:16-17`). No hay ajuste previo con todas las filas (`evidencia/inventario.txt`, `evidencia/v1_v3_metricas_y_fuga.txt`) |
| V3.2 | Columnas del futuro | **PASA** | `clase` se excluye de X (`datos.py:16`). Ninguna predictora tiene una categoría con n ≥ 20 de una sola clase (`evidencia/v1_v3_metricas_y_fuga.txt`, V3.2). La asociación máxima con `clase` es V de Cramér = 0.352 y la descripción de los datos no marca ninguna variable registrada después del resultado (`datos/RESUMEN.md`, sección "Riesgos") |
| V4.1 | Métrica por subgrupo | **FALLA** | Ningún script de la 6.2 calcula el recall de `bad` por `housing`, `personal_status` ni edad para el modelo auditado: la búsqueda de `housing` y `groupby` no da coincidencias en `evidencia/inventario.txt`. `PLAN_6_2.md:57-60` lo delega a la auditoría. El cálculo por subgrupo de `auditoria.py` (6.1) es para otros modelos y queda fuera del alcance |
| V4.2 | Brecha | **PASA** | Hay 8 subgrupos con n_bad ≥ 30 y ninguno supera los umbrales. Brecha máxima: 0.034 (`personal_status` = female div/dep/mar). Cociente mínimo: 0.843 (`housing` = own frente a for free). Tres subgrupos se listan sin decidir porque tienen n_bad < 30. Detalle en la sección V4 y en `evidencia/v4_subgrupos.txt` |
| V5.1 | Dependencias | **PASA** | Ruta de datos relativa al archivo (`datos.py:7`). La huella MD5 del CSV, 19d37d42…, coincide con la de `datos/RESUMEN.md` (`evidencia/integridad.txt`). Las versiones exactas están en `versiones_exactas.txt` y coinciden con el entorno usado |
| V5.2 | Estado aleatorio | **PASA** | No hay `np.random` ni `default_rng` en los 10 scripts (`evidencia/inventario.txt`). `cargar_datos()` es determinista y crea su propia CV con semilla (`datos.py:10-20`) |
| V6.1 | Divisiones seguras | **PASA** | No existe ninguna división entre columnas. Las 17 apariciones de `/` son operadores de `pathlib` o texto de rutas (`evidencia/inventario.txt`, última sección). Ver Limitaciones (caso sin divisiones) |
| V6.2 | Validación antes de entrenar | **NSPD** | No existe ninguna función de validación de datos. `validacion.py` contiene protocolos de medición (`validar` en `validacion.py:11-14` es CV, no validación de datos). Las aserciones de esquema de `tests/test_modelo.py:62-72` se ejecutan con pytest y no antes del `fit` |

### V4 — Hallazgos por subgrupo (modelo auditado)

Predicciones fuera de pliegue con la misma CV (`evidencia/v4_subgrupos.py`). Valores globales: recall de `bad` **0.640** (192/300), exactitud 0.726 y buenos rechazados 166/700 = 0.237. Brecha = 0.640 − recall del subgrupo; un valor positivo significa que el subgrupo queda por debajo. Cociente = recall del subgrupo / mejor subgrupo elegible de la misma variable.

| Variable | Grupo | n | n_bad | Recall `bad` (IC 95 % Wilson) | Brecha | Cociente | Exactitud | Buenos rechazados | Veredicto |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| housing | for free | 108 | 44 | 0.727 (0.58–0.84) | −0.087 | 1.000 | 0.667 | 24/64 = 0.375 | PASA |
| housing | own | 713 | 186 | 0.613 (0.54–0.68) | 0.027 | 0.843 | 0.742 | 112/527 = 0.213 | PASA |
| housing | rent | 179 | 70 | 0.657 (0.54–0.76) | −0.017 | 0.904 | 0.698 | 30/109 = 0.275 | PASA |
| personal_status | female div/dep/mar | 310 | 109 | 0.606 (0.51–0.69) | 0.034 | 0.921 | 0.726 | 42/201 = 0.209 | PASA |
| personal_status | male div/sep | 50 | 20 | 0.700 (0.48–0.86) | −0.060 | — | 0.640 | 12/30 = 0.400 | no decide (n_bad < 30) |
| personal_status | male mar/wid | 92 | 25 | 0.640 (0.45–0.80) | 0.000 | — | 0.696 | 19/67 = 0.284 | no decide (n_bad < 30) |
| personal_status | male single | 548 | 146 | 0.658 (0.58–0.73) | −0.018 | 1.000 | 0.739 | 93/402 = 0.231 | PASA |
| edad | ≤ 25 | 190 | 80 | 0.613 (0.50–0.71) | 0.027 | 0.942 | 0.653 | 35/110 = 0.318 | PASA |
| edad | > 25 | 810 | 220 | 0.650 (0.59–0.71) | −0.010 | 1.000 | 0.743 | 131/590 = 0.222 | PASA |
| foreign_worker | no | 37 | 4 | 1.000 (0.51–1.00) | −0.360 | — | 0.865 | 5/33 = 0.152 | no decide (n_bad < 30) |
| foreign_worker | yes | 963 | 296 | 0.635 (0.58–0.69) | 0.005 | 1.000 | 0.721 | 161/667 = 0.241 | PASA |

Lectura:
- **V4.2 PASA con margen moderado.** El caso más ajustado es `housing` = own: cociente 0.843, a 0.043 del límite de 0.80. Todos los intervalos de confianza de los subgrupos elegibles se solapan.
- **Contexto que la Skill no evalúa.** El costo de los falsos positivos no se reparte igual. Se rechaza el 31.8 % de los buenos de ≤ 25 años frente al 22.2 % de los de > 25 (1.43 veces más), y el 37.5 % de los buenos de `housing` = for free frente al 21.3 % de own (1.76 veces). El modelo no usa `age`, pero `housing` sí es predictora, y otras variables pueden actuar como sustitutas de la edad. La exactitud también es más baja en ≤ 25 (0.653 frente a 0.743) y en for free (0.667).
- **Contraste con el mismo boosting con las 20 variables**, que no es el modelo auditado: su recall global es 0.603, y `housing` = own tiene cociente 0.799 < 0.80, así que FALLARÍA V4.2. Quitar las variables sensibles mejoró la paridad en `housing` y en edad (`evidencia/v4_subgrupos.txt`, segunda tabla).
- **Sensibilidad a las decisiones del auditor.** Con brecha absoluta, `housing` = for free superaría 0.05 (0.087), aunque su recall está *por encima* del global. Si el cociente se calcula frente al mejor subgrupo incluyendo los de n < 30, `foreign_worker` = yes daría 0.635 frente a un grupo con 4 `bad`. Si el n relevante fuera el número de filas en lugar de `bad`, `foreign_worker` = no (37 filas) sería elegible y `foreign_worker` = yes FALLARÍA por cociente (0.635). Con cualquier lectura, `housing`, `personal_status` y edad siguen pasando.

## Acciones recomendadas

1. **(V4.1)** Añadir al proyecto un script versionado, por ejemplo `subgrupos.py`, que calcule el recall de `bad` del modelo recomendado por `housing`, `personal_status` y edad, con n, n_bad, intervalo de confianza y proporción de buenos rechazados, y guarde su salida en `resultados/`. Puede partir de `evidencia/v4_subgrupos.py`.
2. **(V4.2, contexto)** Documentar en el informe la diferencia en buenos rechazados (≤ 25: 0.318 frente a 0.222; for free: 0.375 frente a 0.213). Decidir si esa diferencia es aceptable para el uso previsto, ya que la Skill solo controla el recall.
3. **(V4.2)** No sacar conclusiones sobre `personal_status` = male div/sep, male mar/wid ni `foreign_worker` = no: tienen menos de 30 `bad`. Decirlo explícitamente en el informe.
4. **(V6.2)** Crear una función de validación de datos (columnas esperadas, `clase` ∈ {good, bad}, sin faltantes, sensibles fuera de X) y llamarla en `cargar_datos()`, antes de cualquier `fit`. Las aserciones de `tests/test_modelo.py` pueden reutilizarse, pero hoy solo se ejecutan con pytest.
5. **(V2.5, menor)** Indicar en el informe que el modelo final, la variante sin sensibles, se eligió con la misma CV con la que se reporta su cifra (0.726 / 0.640 / costo 706). La regla se fijó de antemano, pero la cifra incluye un pequeño optimismo de selección entre 7 variantes.
6. **(V0.1 / V5.1, menor)** `requirements.txt` solo fija mínimos. Para reproducir las cifras exactas conviene instalar desde `versiones_exactas.txt`.

## Limitaciones de esta auditoría

Qué no se pudo comprobar:
- **Ejecución en una copia.** Para no escribir en el proyecto (Regla 1), los scripts se ejecutaron en `/tmp/claude-0/auditoria_6_2/copia/` con `python3 -B`. Antes se guardó un respaldo de `resultados/`, `figs/` y `evidencia/` en `/tmp/claude-0/auditoria_6_2/respaldo/` y la huella MD5 de los 52 archivos. Al final el proyecto quedó idéntico y sin `__pycache__` (`evidencia/integridad.txt`). No se comparó la figura `figs/curvas_aprendizaje.png`, solo su CSV.
- **pytest no está instalado** y no hay internet, así que no pude volver a ejecutar `tests/test_modelo.py`. Solo se leyó `evidencia/6_2_salida_pytest.txt`. Ningún veredicto depende de las pruebas.
- **Sin git** (regla de esta ejecución). No se comprobó que `PLAN_6_2.md` se versionara antes de los resultados, como afirma `PLAN_6_2.md:8-9`, ni que `datos/credit_g.csv` esté versionado. Los tiempos de modificación de los archivos son compatibles con esa afirmación, pero no la prueban.
- **V3.2** se basa en la descripción de `datos/RESUMEN.md`, que no documenta en qué momento se registra cada variable. Que ninguna sea posterior al resultado es una inferencia a partir del dominio de una solicitud de crédito.
- **La curva de aprendizaje** del modelo auditado muestra una brecha final entrenamiento − validación de 0.257 (`evidencia/6_2_salida_curvas.txt`), que indica sobreajuste. La Skill no tiene criterio para esto y no se evaluó.

Decisiones que tomé porque la Skill no las define (la Skill necesita refinarse en estos puntos):
1. **V4.2, sentido de la brecha.** La tabla dice "brecha frente a la global ≤ 0.05" sin indicar si es absoluta o de un solo lado. La usé de un solo lado (global − subgrupo), porque la justificación la llama "máxima pérdida". Con brecha absoluta, `housing` = for free (0.087 por *encima* del global) FALLARÍA.
2. **V4.2, "mejor subgrupo".** La Skill no dice si el mejor subgrupo se busca dentro de cada variable o entre todas, ni si se incluyen los de n < 30. Lo busqué dentro de cada variable y solo entre los elegibles. Si se incluyen los de n < 30, `foreign_worker` = yes quedaría con cociente 0.635 frente a un grupo de 4 `bad`.
3. **V4.2, qué es "n".** La Skill dice "n ≥ 30" sin aclarar si son filas o casos de la clase sobre la que se calcula la métrica. Seguí la instrucción de esta ejecución: n = número de `bad`. Con n = filas, `foreign_worker` = yes FALLARÍA.
4. **V4.2, "global".** Tomé como global el recall fuera de pliegue de las 1000 filas (0.640), no la media de los recall por pliegue.
5. **V4.1, quién calcula.** La Skill exige que "el proyecto" calcule la métrica por subgrupo, pero el paso 5 manda reproducirla en la auditoría. Marqué FALLA porque el proyecto no la calcula, aunque el plan la delegue a esta Skill. Si delegar en la auditoría cuenta como cumplimiento, V4.1 sería PASA.
6. **V6.1 sin divisiones.** La Skill no contempla el caso sin divisiones entre columnas. Lo marqué PASA porque la ausencia está observada (inventario completo de `/`), no supuesta. Una lectura estricta de la Regla 2 podría pedir NSPD.
7. **V0.1, salidas con tiempo.** Para `comparar_tres.py` comparé el CSV sin la columna de tiempo en lugar del texto completo, porque el tiempo depende del equipo.
8. **Subgrupo añadido.** Añadí `foreign_worker` porque es la tercera variable sensible excluida (`datos.py:25`). La Skill no dice si el auditor puede ampliar los subgrupos pedidos.

## Archivos de evidencia (`auditorias/6_2_boosting_elegido/evidencia/`)

| Script | Salida | Verificaciones |
|---|---|---|
| `inventario.sh` | `inventario.txt` | Paso 2; V2.1, V2.2, V3.1, V4.1, V5.2, V6.1, V6.2 |
| `v0_ejecucion.py` | `v0_ejecucion.txt` | V0.1, V2.5 |
| `v1_v3_metricas_y_fuga.py` | `v1_v3_metricas_y_fuga.txt` | V1.1–V1.4, V2.1–V2.4, V3.1–V3.2 |
| `v4_subgrupos.py` | `v4_subgrupos.txt`, `v4_subgrupos_modelo_auditado.csv` | V4.2 |
| `integridad.sh` | `integridad.txt` | Regla 1, V5.1 (MD5 de los datos) |
