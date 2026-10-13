---
name: auditoria-modelos
description: Audita un proyecto de clasificación (notebook o scripts .py) SIN modificarlo y entrega AUDIT_REPORT_<proyecto>.md con veredictos PASA / FALLA / NO SE PUEDE DETERMINAR, cada uno con evidencia citada. Úsala antes de recomendar o desplegar un modelo, o cuando se pida "auditar", "revisar fuga", "revisar métricas" o "revisar subgrupos".
---

> **Procedencia.** Versión **v2.2-r** (v2.1-r + refinamiento 6): reconstrucción de la Skill de la Tarea 4.1
> (v2.1, commit `fe73cdc` del repositorio `mai540-tarea-4.1`), hecha el
> 12-oct-2026 porque la carpeta `.claude/` no estaba en la copia descargada del
> repositorio. Fuentes: `docs/Tarea_4_1_Informe_APA.pdf` (Tabla 1, criterios
> V0–V6 y umbrales), `auditorias/ESTABILIDAD_Y_REFINAMIENTO.md` (refinamientos
> 1–5) y el formato de `AUDIT_REPORT_biopsias_corregido.md`. Único cambio de
> fondo: el formato de cita admite scripts `.py` (`archivo.py:L`) además de
> notebooks, porque el proyecto German Credit está en scripts. El script
> `scripts/extraer_evidencia.py` de la v2.1 no se reconstruyó; el inventario se
> hace con `grep` (paso 2). Si aparece el SKILL.md original, reemplaza este archivo.

# Propósito
Comprobar, con evidencia citada y sin tocar el código, que las métricas de un
modelo de clasificación son válidas, que la partición y el preprocesamiento no
filtran información y que el desempeño no se degrada en subgrupos relevantes.

# Entradas esperadas
- **Proyecto:** notebook `.ipynb` o scripts `.py`, con sus salidas (o la
  posibilidad de ejecutarlos).
- **Columna objetivo y clase positiva** (p. ej. `clase`, positiva = `bad`).
- **Columnas que definen los subgrupos** (p. ej. `housing`, `personal_status`, edad).
- **Modelo auditado:** cuál es el modelo que se reporta o se desplegaría.
- Opcional: costo relativo de los errores (p. ej. FN = 5, FP = 1).

# Reglas
1. **La Skill audita, no modifica.** No edita código, datos ni resultados del
   proyecto. Solo crea el informe y, si hace falta reproducir algo, scripts
   propios dentro de `auditorias/<proyecto>/evidencia/`.
2. **Sin evidencia observada no hay PASA.** Si no encuentra la evidencia, el
   veredicto es NO SE PUEDE DETERMINAR (NSPD), nunca PASA por omisión.
3. Cada veredicto cita su evidencia con formato estable:
   notebook → `celda N (id X), l. L`; script → `archivo.py:L`;
   salida reproducida → `evidencia/<archivo>.txt`.
4. Una sospecha sin evidencia en el código o en los datos es NSPD, no FALLA.
5. **Alcance (refinamiento 5):** se audita el modelo que se reporta o se
   despliega. Una demostración rotulada explícitamente como contraejemplo
   (p. ej. "con fuga") no hace FALLAR V3.2, pero se menciona.

# Pasos
1. Leer el proyecto completo e identificar el modelo auditado, el objetivo,
   la clase positiva y los subgrupos.
2. **Inventario de evidencia:** buscar `fit`, `fit_transform`,
   `train_test_split`, `StratifiedKFold`, `random_state`, `Pipeline`,
   `ColumnTransformer`, `GridSearchCV`, divisiones `/` entre columnas y
   funciones de validación; anotar archivo y línea de cada hallazgo.
3. **Ejecutar o leer salidas** (V0). Si algo termina en error, las métricas
   que dependen de ello quedan NSPD.
4. Aplicar V1 a V6 en orden con la tabla de criterios; escribir el veredicto
   con su evidencia en el momento, no al final.
5. Para V4.2, reproducir la métrica por subgrupo con un script propio en
   `auditorias/<proyecto>/evidencia/` y guardar su salida.
6. Redactar el informe con el formato de **Salida**.
7. Releer cada PASA y confirmar que cita evidencia observada.

# Criterios de verificación

| ID | Verificación | PASA si… | FALLA si… | NSPD si… |
|---|---|---|---|---|
| V0.1 | Ejecución | Ninguna salida usada para métricas es un error | Alguna celda/script de métricas termina en error | No hay salidas ni se puede ejecutar |
| V1.1 | Rango | Todas las métricas reportadas están en [0, 1] | Alguna fuera de rango | No hay métricas impresas |
| V1.2 | Coherencia | Precisión/exhaustividad/accuracy recalculadas desde la matriz de confusión coinciden (±0.01) | No coinciden | No hay matriz ni conteos |
| V1.3 | Desbalance | p_min ≥ 0.8/K, o con p_min < 0.8/K se reportan métricas por clase (K = nº de clases) | p_min < 0.8/K y solo se reporta accuracy | No se conoce la distribución de clases |
| V1.4 | Costo del error | La métrica prioritaria se justifica por el costo del error y se compara con la línea base de la clase mayoritaria | Se presenta el modelo como apto solo por accuracy con costos asimétricos | No hay contexto de uso |
| V2.1 | Orden | La división (o la CV) ocurre antes de todo `fit` que aprende de los datos, o los transformadores van dentro de un `Pipeline` | Un transformador se ajusta con todas las filas antes de dividir | — |
| V2.2 | Semilla | Particiones y modelos con `random_state` fijo | Falta semilla en partición o modelo estocástico | — |
| V2.3 | Estratificación | `stratify=y` o `StratifiedKFold` | Partición de clasificación sin estratificar | — |
| V2.4 | Misma partición | Los modelos comparados usan la misma partición/CV | Particiones distintas entre modelos comparados | — |
| V2.5 | Hiperparámetros | Los que se presentan como elegidos salen de validación (CV o búsqueda) sin ver la prueba | Se eligieron a mano y se rotulan como "por CV", o se eligieron mirando la prueba | No se presenta ningún hiperparámetro como elegido |
| V3.1 | Transformaciones | Ninguna métrica de generalización proviene de un ajuste que vio esas filas | Alguna métrica de prueba sale de un ajuste que vio la prueba | — |
| V3.2 | Columnas del futuro | Ningún predictor se deriva del objetivo en el código ni se registra después del resultado según la descripción | Un predictor se deriva del objetivo o se registra después del resultado | Hay sospecha por dominio sin evidencia |
| V4.1 | Métrica por subgrupo | El proyecto calcula la métrica prioritaria por cada subgrupo relevante | No la calcula | No hay subgrupos identificables |
| V4.2 | Brecha | En todo subgrupo con n ≥ 30: brecha frente a la global ≤ 0.05 **y** cociente frente al mejor subgrupo ≥ 0.80 | Algún subgrupo con n ≥ 30 supera la brecha o el cociente | Ningún subgrupo tiene n ≥ 30 |
| V5.1 | Dependencias | Los datos y librerías se cargan de forma reproducible | Dependen de rutas o estados no versionados | — |
| V5.2 | Estado aleatorio | No se consume un `rng` global en varias cargas | Una función de carga usa un `rng` global y se llama más de una vez | — |
| V6.1 | Divisiones seguras | Las divisiones entre columnas están protegidas contra cero | Hay división sin protección | — |
| V6.2 | Validación antes de entrenar | Existe una validación de datos y se llama antes del `fit` | Existe pero nunca se llama | No existe función de validación |

**Cómo se calcula V4.2 (refinamiento 6, v2.2-r).** La auditoría de la Tarea 6.2
tuvo que decidir tres cosas fuera del archivo; quedan fijadas aquí:
- **Sentido de la brecha:** solo cuenta hacia abajo, `brecha = global − subgrupo`.
  Un subgrupo por encima de la métrica global no FALLA por brecha.
- **"n" depende de la métrica:** si la métrica prioritaria es exhaustividad
  (recall), n = número de positivos reales del subgrupo; si es precisión, n =
  número de positivos predichos; si es exactitud, n = filas del subgrupo.
- **Mejor subgrupo para el cociente:** el de mejor métrica dentro de la misma
  variable, elegido solo entre los subgrupos con n ≥ 30.
- La métrica global es la de todas las predicciones fuera de pliegue juntas.
- Si el modelo usa pesos o umbral por costo, reportar además la tasa de falsos
  positivos por subgrupo como contexto (no decide el veredicto).

**Justificación de los umbrales de V4.2.** 0.05 es la máxima pérdida que se
acepta frente a la métrica global; el cociente 0.80 replica la regla de las
cuatro quintas partes (Equal Employment Opportunity Commission, 1978); n ≥ 30
evita decidir con estimaciones inestables. Los subgrupos con n < 30 se listan
pero no deciden el veredicto.

# Salida
Archivo `AUDIT_REPORT_<proyecto>.md` con:
1. Encabezado: archivo(s), fecha, versión de la Skill, objetivo y clase
   positiva, subgrupos, supuestos.
2. **Resumen:** conteo PASA / FALLA / NSPD y lo más grave en una o dos frases.
3. **Verificaciones:** tabla `ID | Verificación | Resultado | Evidencia`.
4. **Acciones recomendadas:** lista numerada con el ID que origina cada una.
5. **Limitaciones de esta auditoría:** qué no se pudo comprobar y por qué.
