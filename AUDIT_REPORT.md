# Informe de auditoría — German Credit

Rol: auditor · MAI 540, Tarea 6.1 · Fecha: 2026-10-12

Entradas revisadas: `datos/RESUMEN.md` (analista), `RESULTADOS.md`,
`resultados/*.csv` y `datos.py`, `modelos.py`, `validacion.py`, `tabla_cv.py`,
`particion_vs_cv.py` (ingeniero), y `datos/credit_g.csv`.

Todas las cifras de este informe salen de `python3 auditoria.py` (desde la
raíz; ~20 s). El script no escribe nada en el proyecto: ejecuta los scripts
del ingeniero en una carpeta temporal, recalcula todo con código propio y
comprueba al final que `datos/` y `resultados/` siguen con la misma huella MD5.
Entorno: Python 3.13.16, pandas 3.0.5, numpy 2.5.3, scikit-learn 1.9.1.
MD5 de `datos/credit_g.csv`: `19d37d4238836d135ab13d73dc42d5e4` (igual al
declarado por el analista y el ingeniero).

## Veredicto global: **APROBADO CON OBSERVACIONES**

Las cifras son correctas y reproducibles, no hay fuga de información, el recall
se mide para `bad` y el ingeniero siguió lo que declaró el analista. Ninguna
cifra del RESUMEN ni de RESULTADOS resultó incorrecta. Hay un error real, solo
de documentación (H1), y observaciones de método y de lectura (H2–H7). La más
importante es H2: elegir el modelo por su exactitud lleva a la conclusión
equivocada.

## Revisiones

| # | Revisión | Veredicto | Evidencia (salida de `auditoria.py`) |
|---|---|---|---|
| 1 | Reproducibilidad | **PASA** | `tabla_cv.py` y `particion_vs_cv.py` se ejecutaron desde cero en una carpeta temporal. Los 3 CSV salen **idénticos byte a byte** a los entregados, y la salida de consola es idéntica a la copiada en RESULTADOS.md. Con código propio (sin `validacion.py`) recalculé las 68 cifras de los CSV: 6 de CV por modelo, 40 de `particion_unica.csv` (exactitud y recall en 20 filas modelo × semilla) y 16 de `particion_vs_cv.csv`. Todas coinciden con tolerancia 1e-12. |
| 2 | Fuga de datos | **PASA** | `clase` no está en `X` (1000 × 20); el modelo recibe 20 predictores en cada pliegue. El `ColumnTransformer` es el paso 0 del `Pipeline`. Con `cross_validate(return_estimator=True)` hay 5 codificadores distintos, y en cada pliegue las categorías aprendidas son **exactamente** las del entrenamiento de ese pliegue (con un ajuste sobre los 1000 casos no sería así). Con etiquetas permutadas, el RF cae a 0.676 de exactitud (por debajo del piso 0.70). El mayor \|r\| entre un predictor numérico e `y` es 0.215. |
| 3 | Clase positiva | **PASA** | Matriz de confusión propia sobre las etiquetas de texto (orden `bad`, `good`), con predicciones fuera de pliegue. Árbol: bad→bad 159, bad→good 141, good→bad 161, good→good 539. Su recall de `bad` es 159/300 = 0.5300 y el de `good` 0.7700. RF: 113 / 187 / 54 / 646, con recall de `bad` 113/300 = 0.3767 y de `good` 0.9229. Las cifras reportadas son las de `bad`. |
| 4 | Coherencia analista → ingeniero | **PASA** (obs. H5, H6) | `cols_cat` son exactamente las 13 del RESUMEN, y las 7 numéricas van en `passthrough`. El codificador es `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)` y `random_state=42` en los dos modelos. Comprobé **todas** las cifras del RESUMEN: forma, 700/300, mín/mediana/máx/media, distribuciones ordinales, los conteos de las 13 columnas de texto, faltantes, duplicados, espacios, V de Cramér (top 5 y rango 0.003–0.154), ninguna categoría pura, tasas de `bad` de los grupos sensibles y pliegues de 200/60. **0 discrepancias.** |
| 5 | Partición | **PASA** | Se usa `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. Los pliegues de prueba son disjuntos, cubren las 1000 filas y tienen 200 filas y 60 `bad` cada uno. Las semillas son 0–9: 10 distintas, con 10 conjuntos de prueba distintos de 250 filas y 75 `bad`. |
| 6 | Línea base "siempre good" | **PASA** | `DummyClassifier(constant=good)` da 0.700 en los 5 pliegues y 0/300 malos detectados. Árbol: −0.002 ± 0.019 frente al piso; supera el piso en 3/5 pliegues y en 2/10 semillas. RF: +0.059 ± 0.007; lo supera en 5/5 pliegues y 10/10 semillas. Malos detectados: árbol 159/300, RF 113/300, piso 0/300. |
| 7 | Subgrupos (`housing`, `personal_status`) | **PASA** (con avisos) | Tabla abajo, con n, número de `bad`, exactitud, malos detectados, IC 95 % de Wilson y buenos rechazados. Hay pocos casos en `male div/sep` (n = 50, 20 `bad`) y `male mar/wid` (n = 92, 25 `bad`). |
| 8 | Lectura de negocio | **PASA** (obs. H2) | RESULTADOS reconoce que "ninguno es claramente bueno". Pero con la matriz de coste del conjunto (malo aceptado = 5, bueno rechazado = 1), el **árbol cuesta menos que el RF** (866 frente a 989) aunque acierta menos. Respuesta abajo. |

### Revisión 7 — subgrupos (predicciones fuera de pliegue de la CV 5×)

"Detectados" = malos detectados / malos del grupo (recall de `bad`). "Buenos
rechazados" = buenos predichos como `bad` / buenos del grupo.

| Modelo | Variable | Grupo | n | `bad` | Exactitud | Detectados | IC 95 % recall | Buenos rechazados | Aviso |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| Árbol | housing | for free | 108 | 44 | 0.685 | 28/44 (0.636) | [0.49, 0.76] | 18/64 (0.281) | |
| Árbol | housing | own | 713 | 186 | 0.714 | 93/186 (0.500) | [0.43, 0.57] | 111/527 (0.211) | |
| Árbol | housing | rent | 179 | 70 | 0.642 | 38/70 (0.543) | [0.43, 0.65] | 32/109 (0.294) | |
| Árbol | personal_status | female div/dep/mar | 310 | 109 | 0.677 | 62/109 (0.569) | [0.48, 0.66] | 53/201 (0.264) | |
| Árbol | personal_status | male div/sep | 50 | 20 | 0.580 | 11/20 (0.550) | [0.34, 0.74] | 12/30 (0.400) | **Pocos casos** |
| Árbol | personal_status | male mar/wid | 92 | 25 | 0.750 | 13/25 (0.520) | [0.33, 0.70] | 11/67 (0.164) | **Pocos casos** |
| Árbol | personal_status | male single | 548 | 146 | 0.712 | 73/146 (0.500) | [0.42, 0.58] | 85/402 (0.211) | |
| RF | housing | for free | 108 | 44 | 0.676 | 22/44 (0.500) | [0.36, 0.64] | 13/64 (0.203) | |
| RF | housing | own | 713 | 186 | 0.781 | 61/186 (0.328) | [0.26, 0.40] | 31/527 (0.059) | |
| RF | housing | rent | 179 | 70 | 0.721 | 30/70 (0.429) | [0.32, 0.55] | 10/109 (0.092) | |
| RF | personal_status | female div/dep/mar | 310 | 109 | 0.735 | 46/109 (0.422) | [0.33, 0.52] | 19/201 (0.095) | |
| RF | personal_status | male div/sep | 50 | 20 | 0.620 | 6/20 (0.300) | [0.15, 0.52] | 5/30 (0.167) | **Pocos casos** |
| RF | personal_status | male mar/wid | 92 | 25 | 0.772 | 6/25 (0.240) | [0.11, 0.43] | 2/67 (0.030) | **Pocos casos** |
| RF | personal_status | male single | 548 | 146 | 0.783 | 55/146 (0.377) | [0.30, 0.46] | 28/402 (0.070) | |

Lectura:
- **Pocos casos.** Con 20–25 `bad`, una sola solicitud mueve el recall 4–5
  puntos y los intervalos tienen 30–40 puntos de ancho (RF en `male mar/wid`:
  0.24, IC [0.11, 0.43]). Las diferencias en esos grupos no permiten
  conclusiones.
- **`housing`.** El RF detecta muchos menos malos entre los propietarios
  (0.328) que entre quienes viven gratis (0.500). A cambio, rechaza a 20.3 % de
  los buenos que viven gratis frente al 5.9 % de los propietarios. Con n = 108,
  la diferencia en buenos rechazados (13/64 frente a 31/527) es grande, aunque
  el grupo es pequeño.
- Como pidió el ingeniero, también medí `age` y `foreign_worker`.
  - **`age`.** Los ≤ 25 años tienen más malos detectados (RF 0.463 frente a
    0.345) y más buenos rechazados (RF 0.100 frente a 0.073; árbol 0.282 frente
    a 0.220).
  - **`foreign_worker = no`.** Solo tiene 37 filas y 4 `bad`. Cualquier métrica
    en ese grupo es ruido (IC del recall del RF: [0.05, 0.70]).

### Revisión 8 — ¿es aceptable un modelo que acierta más pero detecta menos?

**No, tal como está.** El RF acierta más (0.759 frente a 0.698) porque predice
`good` casi siempre: aprueba a 187 de 300 malos. En crédito, aprobar a un
moroso cuesta mucho más que rechazar a un buen cliente. Con la matriz de coste
documentada del German Credit (5 : 1):

| Decisión | Exactitud | Malos aprobados | Buenos rechazados | Coste total | Coste por solicitud |
|---|---:|---:|---:|---:|---:|
| Siempre `good` | 0.700 | 300 | 0 | 1500 | 1.500 |
| Árbol de decisión | 0.698 | 141 | 161 | **866** | 0.866 |
| Random Forest | 0.759 | 187 | 54 | 989 | 0.989 |

El modelo con más exactitud es el más caro de los dos. La exactitud no debe ser
el criterio de elección; debe serlo el recall de `bad` y/o el coste.

*Ilustración, no es un resultado.* Cambié solo el umbral de decisión, con los
mismos modelos y semillas y sobre probabilidades fuera de pliegue. Así, el RF
pasaría a recall 0.603 / coste 739 con umbral 0.40, y a recall 0.800 /
coste 554 con umbral 0.30.

- El árbol completo da probabilidades 0/1, así que el umbral no lo cambia.
- Estas cifras son **optimistas**, porque el umbral se eligió después de ver los
  datos. Para usarlas, el umbral (o `class_weight`) se fija antes y se mide con
  CV anidada.

## Hallazgos

**Error real**

**H1. Referencias rotas en la documentación.** Responsable: Carlo (responsable
del proyecto).
- `README.md` remite a `docs/flujo.md`, y `ROLES.md` a
  `evidencia/bitacora_flujo.md`. Ninguno de los dos existe (comprobado en
  `auditoria.py`, sección "Extra").
- No afecta a las cifras, pero el registro de entregas que ROLES.md promete no
  está.
- **Acción:** crear esos archivos o corregir las referencias antes de entregar.

**Observaciones**

**H2. El criterio "supera el piso de exactitud" lleva a elegir mal.**
Responsable: ingeniero de modelos (reporte); la decisión es de Carlo.
- `supera_piso_0.70 = True` del RF y la lectura de RESULTADOS dejan al RF como
  el que "supera el piso".
- Pero detecta 113/300 malos y, con la matriz de coste 5 : 1, cuesta 989
  frente a 866 del árbol (revisión 8).
- **Acción:** añadir a RESULTADOS el coste (o malos aprobados / buenos
  rechazados) junto a la exactitud.
- **Acción:** no presentar al RF como mejor solo por exactitud.
- **Acción:** si se quiere ajustar el umbral o usar `class_weight`, declararlo
  antes y medirlo con CV anidada.

**H3. El árbol no está "por debajo" del piso, es indistinguible de él.**
Responsable: ingeniero de modelos.
- 0.698 frente a 0.700 es una diferencia de −0.002 ± 0.019 entre pliegues.
- El árbol supera el piso en 3 de 5 pliegues.
- **Acción:** matizar la redacción: "no mejora el piso" en lugar de "no lo
  supera" como si fuera peor. A cambio, detecta 159 malos frente a 0.

**H4. Variables sensibles como predictoras.** Responsable: Carlo (decisión),
con el ingeniero (ejecución).
- Usar `age`, `personal_status` y `foreign_worker` está documentado y
  justificado para el ejercicio.
- Los subgrupos muestran tasas distintas de buenos rechazados (por ejemplo,
  `housing = for free` 0.203 frente a `own` 0.059 en el RF; ≤ 25 años 0.100
  frente a 0.073).
- `personal_status` tiene dos grupos con pocos casos.
- **Acción:** para cualquier uso fuera del aula, decidir *antes de ver
  resultados* si se excluyen esas variables.
- **Acción:** medir esa variante con el mismo protocolo.
- **Acción:** reportar los buenos rechazados por subgrupo.
- No lo ejecuté porque produciría resultados con una configuración distinta a
  la declarada.

**H5. El método de la V de Cramér está descrito de forma imprecisa.**
Responsable: analista de datos.
- El RESUMEN dice "numéricas agrupadas en quintiles". Pero 4 de las 7
  numéricas no admiten 5 quintiles: `installment_commitment` queda en 3
  intervalos, `residence_since` y `existing_credits` en 2, y `num_dependents`
  en 1, por lo que se usan sus valores tal cual.
- Las cifras del RESUMEN (incluido el mínimo 0.003, que es `num_dependents`)
  solo se reproducen con `pd.qcut(..., duplicates="drop")` más ese caso
  especial.
- Con quintiles por rango salen otros valores (por ejemplo, `residence_since`
  0.080 en lugar de 0.007).
- La conclusión (no hay columna que filtre la clase) se mantiene y la confirma
  la prueba de etiquetas permutadas.
- **Acción:** escribir el método exacto.

**H6. "`handle_unknown` es necesario por las categorías raras" es exagerado.**
Responsable: analista de datos.
- En los 5 pliegues y en las 10 semillas no aparece **ninguna** categoría de
  prueba que falte en el entrenamiento (0 casos).
- Es una salvaguarda correcta, no una necesidad observada.
- **Acción:** reformular. No requiere cambiar el código.

**H7. Entorno de reproducción incompleto.** Responsable: ingeniero de modelos.
- RESULTADOS solo cita scikit-learn 1.9.1, y `requirements.txt` solo fija
  mínimos (`pandas>=2.0`, etc.).
- Las cifras se obtuvieron con Python 3.13.16, pandas 3.0.5 y numpy 2.5.3.
- **Acción:** anotar todas las versiones en RESULTADOS y fijarlas (o añadir un
  archivo de versiones exactas). El propio ingeniero lo señaló en su duda 5.

## Respuesta a las dudas abiertas del ingeniero

1. **Variables sensibles:** ver H4 y la revisión 7.
2. **Árbol bajo el piso:** ver H3. No se ajustan hiperparámetros sin CV anidada
   decidida de antemano.
3. **Recall bajo del RF:** ver H2 y la revisión 8. El umbral es una decisión de
   negocio que debe tomarse antes de medir.
4. **Codificación ordinal arbitraria:** no se probó otra codificación para no
   generar resultados con una configuración no declarada. Para árboles es
   aceptable. Queda como posible variante predeclarada en la Tarea 6.2.
5. **Versiones:** ver H7.

## Integridad de la auditoría

- No edité ningún archivo ajeno.
- Antes de ejecutar los scripts del ingeniero en el proyecto guardé una copia
  de `resultados/` fuera del proyecto. Los CSV regenerados salieron idénticos;
  aun así restauré la copia original (con su fecha) y borré los `__pycache__`.
- `auditoria.py` no escribe en el proyecto y lo verifica al final.

Entregado a: responsable del proyecto (Carlo) y roles con hallazgos (analista
de datos: H5, H6; ingeniero de modelos: H2, H3, H7; responsable del proyecto:
H1, H2, H4).
