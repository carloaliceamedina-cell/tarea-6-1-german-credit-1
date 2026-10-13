# Plan de la Tarea 6.2 (fijado ANTES de ver resultados)

Parte del diagnóstico de la Tarea 6.1 (`RESULTADOS.md`, `AUDIT_REPORT.md`):
árbol por defecto 0.698 ± 0.017 (indistinguible del piso 0.70), Random Forest
0.759 ± 0.006 pero solo 0.38 de malos detectados; hallazgos H2 (umbral /
pesos) y H4 (variables sensibles) quedaron pendientes para esta tarea.

Este archivo se versiona antes de ejecutar cualquier experimento de la 6.2,
para que los criterios no se ajusten a los resultados.

## 1. Búsqueda de hiperparámetros del árbol
- `GridSearchCV` sobre el Pipeline de la 6.1, `scoring="accuracy"`, misma
  `StratifiedKFold(5, shuffle=True, random_state=42)`.
- Espacio: `max_depth ∈ {2, 3, 4, 5, 6, 8, 10, None}` ×
  `min_samples_leaf ∈ {1, 5, 10, 20, 50}` = 40 combinaciones (200 ajustes).
  `None` incluye la configuración por defecto para que la comparación sea justa.
- Mejora = puntaje del ganador − exactitud CV del árbol por defecto (0.698).

## 2. Número honesto
Se aplican los dos controles:
- **Prueba reservada:** 20 % estratificado (`random_state=1`), la búsqueda solo
  ve el 80 % y la prueba se abre una sola vez.
- **CV anidada:** `cross_val_score(GridSearchCV(...), cv=externa)` con
  `StratifiedKFold(5, shuffle=True, random_state=7)` externa.
- Se reporta como número honesto la **CV anidada** (usa todos los datos y da
  media y desviación); la prueba reservada se reporta como contraste.

## 3. Comparación con el mismo protocolo
Árbol afinado (ganador de la búsqueda), `RandomForestClassifier(random_state=42)`
y `HistGradientBoostingClassifier(random_state=42)`, mismo Pipeline y misma CV.
Por modelo: exactitud media y desviación, malos detectados (recall de `bad`,
`cross_val_predict`), tiempo total de ajuste de los 5 pliegues y **coste**.

**Coste:** matriz de coste documentada del propio German Credit (Hofmann,
1994): aprobar un malo (falso negativo) = 5, rechazar un bueno (falso
positivo) = 1. Coste = 5·FN + 1·FP sobre las 1,000 predicciones fuera de pliegue.

**Extensión (respuesta a H2, decidida aquí):** variantes del Random Forest y
del boosting con `class_weight={0: 1, 1: 5}`. El peso 5 sale de la matriz de
coste, no de los datos, así que no se elige mirando resultados y no necesita CV
anidada. No se ajusta el umbral de decisión.

## 4. Criterio para elegir el modelo (regla fijada de antemano)
1. Descartar los modelos cuya exactitud media no supere 0.70 por más de una
   desviación estándar.
2. Entre los restantes, elegir el de **menor coste**.
3. Si dos modelos difieren en coste menos de 5 %, preferir el más
   interpretable y luego el más rápido.

El error que más preocupa es aprobar un crédito malo (cuesta 5 veces más).

## 5. Curva de aprendizaje
`learning_curve` con `train_sizes = linspace(0.15, 1.0, 7)` y la misma CV, para
el árbol por defecto (diagnóstico de la 6.1, que no generó curva) y el modelo
elegido. Se reporta la brecha entrenamiento − validación en el último punto.

## 6. Auditoría y pruebas
- Auditoría del modelo elegido con la Skill `auditoria-modelos` del Módulo 4
  (o a mano si no está disponible), por `housing`, `personal_status` y edad
  (≤25 / >25), con número de casos.
- **Respuesta a H4:** medir el modelo elegido sin `age`, `personal_status` ni
  `foreign_worker`, con el mismo protocolo.
- Pruebas pytest (`tests/test_modelo.py`), umbrales justificados:
  - el modelo elegido supera 0.70 (piso de «siempre good»);
  - desviación de la CV < 0.05 (un rango de ±2 desviaciones menor a ±10 puntos;
    la peor desviación de la 6.1 fue 0.017);
  - la codificación está dentro del Pipeline y `clase` no es predictora;
  - el modelo elegido detecta más del 50 % de los malos (más que el RF por defecto, 0.38);
  - el árbol por defecto NO supera 0.70 (marcada `xfail`, documenta el diagnóstico).
