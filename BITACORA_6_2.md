# Bitácora de desarrollo asistido — Tarea 6.2

**Autor:** Carlo E. Alicea Medina · **Asistente:** Claude (Claude Code) · **Fecha:** 12 de octubre de 2026
**Repositorio:** el mismo de la Tarea 6.1; los commits de la 6.2 empiezan en `fe68fd1`.

## Cómo trabajé
Le di a Claude la consigna de la 6.2 y el instructivo del Módulo 6, y le pedí
que partiera del diagnóstico de la 6.1. Antes de medir nada fijé el plan y la
regla para elegir el modelo en `PLAN_6_2.md` (commit `fe68fd1`), para que los
criterios no se acomodaran a los resultados; fue la lección del hallazgo H2 del
auditor en la 6.1. La auditoría la hizo una sesión independiente de Claude que
solo recibió la Skill y el proyecto, no esta conversación.

## Registro

| # | Qué le pedí | Qué hizo la IA | Qué verifiqué | Qué se corrigió |
|---|---|---|---|---|
| 1 | Fijar el plan antes de medir | Escribió `PLAN_6_2.md`: espacio de búsqueda 8×5, CV anidada como número honesto, coste 5·FN + 1·FP, peso 5:1 tomado de la matriz de coste, regla de selección | Que la regla fuera aplicable sin mirar resultados (piso 0.70 + 1 DE, luego menor coste) | — |
| 2 | Búsqueda con `GridSearchCV` (≥ 2 hiperparámetros) | `busqueda.py` + `defecto_vs_afinado.py`: 40 combinaciones; ganador `max_depth=5`, `min_samples_leaf=1`; 0.698 → 0.730 | Coincide con el instructivo (0.730, mismo ganador). Revisé el CSV de las 40 combinaciones | Detecté un empate: `min_samples_leaf=5` también da 0.730; GridSearchCV toma el primero. Se documenta |
| 3 | Controlar el optimismo | `numero_honesto.py`: prueba reservada 20 % y CV anidada | La CV anidada dio **0.740 ± 0.013**, *más* que la búsqueda (0.730), al revés de lo esperado | No forcé la explicación de libro: la diferencia (−0.010) es menor que el ruido entre pliegues; se reporta tal cual |
| 4 | Comparar tres modelos con el mismo protocolo | `comparar_tres.py`: exactitud, DE, malos detectados, tiempo, coste; + variantes 5:1 del plan | Recalculé a mano el coste del RF: 5·187 + 54 = 989 | Al aplicar la regla, el RF 5:1 (coste 650, el más bajo) quedó fuera por exactitud 0.694. Mantuve la regla fijada y lo reporto como alternativa |
| 5 | Curvas de aprendizaje | `curvas.py` + `curvas_comparadas.py`, figura en `figs/` | Abrí la imagen | La leyenda tapaba la línea de entrenamiento y la etiqueta 0.70 chocaba con un punto: se reubicaron |
| 6 | Pruebas con pytest | `tests/test_modelo.py` | Las ejecuté (8 passed, 1 xfailed). Para comprobar que **detectan fallos**, cambié el modelo elegido por el RF por defecto en una copia: la prueba de recall falló como debía (`evidencia/6_2_salida_pytest_mutante.txt`) | pytest no aparecía con `pip`; se encontró instalado como herramienta. Los nombres de las pruebas salían como `\xc1rbol`: se les dio un id ASCII |
| 7 | Aplicar la Skill del Módulo 4 | No estaba: la carpeta `.claude/` no venía en la copia descargada del repositorio de la 4.1. Pedí acceso a mis carpetas y no apareció | Leí el informe y la bitácora de la 4.1 | Se **reconstruyó** como v2.1-r desde mi informe de la 4.1 (criterios V0–V6, umbrales, formato), con la procedencia escrita en el encabezado |
| 8 | Medir el modelo sin variables sensibles (H4 de la 6.1) | `sin_variables_sensibles.py`: misma exactitud (0.726), más malos detectados (0.640) y menor coste (706 frente a 749) | Revisé que los pliegues fueran idénticos | **Cambié el modelo recomendado** a la versión sin variables sensibles y actualicé curvas y pruebas para que apunten a él |
| 9 | Auditoría independiente con la Skill | 16 PASA, 1 FALLA (V4.1: el proyecto no calculaba la métrica por subgrupo), 1 NSPD (V6.2: sin validación de datos) | Leí el informe y sus scripts de evidencia | Se añadieron `auditoria_subgrupos.py` y `validar_datos()` |
| 10 | Segunda pasada | El auditor dejó escritas 3 decisiones que la Skill no resolvía (sentido de la brecha, qué es *n*, mejor subgrupo) | — | Refiné la Skill a **v2.2-r** (commit `e55f0d2`). Segunda pasada: **18 PASA, 0 FALLA, 0 NSPD** |

## Decisiones que tomó la IA por su cuenta (y que acepté)
- Usar el peso 5:1 en lugar de ajustar el umbral, porque sale de la matriz de coste y no de los datos (no necesita CV anidada).
- Reportar el coste junto a la exactitud en todas las tablas.
- Añadir `foreign_worker` a la auditoría (lo hizo el auditor).
- Marcar el árbol por defecto como `xfail` estricto para que la prueba documente el diagnóstico de la 6.1.

## Lo que queda abierto
- `validar_datos()` exige exactamente 1,000 filas: sirve para este dataset, no para lotes nuevos en producción.
- La tasa de **buenos rechazados** es mayor en menores de 25 años (0.318 frente a 0.222) y en `housing = for free` (0.375 frente a 0.213). La Skill no tiene umbral para esto; queda como riesgo a vigilar.
- La reconstrucción de la Skill debe sustituirse por el `SKILL.md` original si aparece.
