# Evidencia — Rol 2: ingeniero de modelos

- **Ejecución:** subagente independiente (contexto propio, no vio la sesión del analista), 2026-10-12.
- **Duración:** 101 s · 5 llamadas a herramientas · ~83 k tokens.
- **Instrucción recibida:** "Tu rol: INGENIERO DE MODELOS. Lee primero tu definición en `.claude/agents/ingeniero-de-modelos.md` y síguela al pie de la letra […] Tu entrada es `datos/RESUMEN.md`, que te entregó el analista de datos: léelo antes de escribir código. […] Copia en RESULTADOS.md la salida de consola tal cual salió."
- **Recibió de:** analista-de-datos (`datos/RESUMEN.md`).
- **Entregó:** `datos.py`, `modelos.py`, `validacion.py`, `tabla_cv.py`, `particion_vs_cv.py`, `resultados/*.csv`, `RESULTADOS.md` → **a:** auditor.

## Respuesta devuelta por el rol (resumen fiel)

> **Archivos creados:** los cinco scripts, tres CSV en `resultados/` y `RESULTADOS.md`. No modificó archivos existentes. MD5 del CSV de datos sin cambios. Ejecutó los scripts dos veces: CSV idénticos byte a byte.
>
> **Resultados (CV 5 pliegues):** Árbol 0.6980 ± 0.0169, malos detectados 0.5300 (159/300), no supera el piso 0.70. Random Forest 0.7590 ± 0.0058, malos detectados 0.3767 (113/300).
> **Partición única (10 semillas):** Árbol 0.608–0.720 (rango 0.112, media 0.6744); RF 0.712–0.796 (rango 0.084, media 0.7532).
>
> **Conflicto RESUMEN ↔ definición:** el RESUMEN pedía media y desviación del recall por pliegue; la definición, recall global con `cross_val_predict`. Hizo ambas: cifra global desde `cross_val_predict` y desviación por pliegue con las mismas predicciones (con 60 `bad` por pliegue, la global coincide con la media por pliegue). Usó ddof=0 en ambos protocolos para comparar con justicia.
>
> **Dudas para el auditor:** (1) ¿aceptar `age`, `personal_status`, `foreign_worker` como predictoras? (2) el árbol por defecto no supera el piso; (3) recall del RF bajo (0.377) — umbral/`class_weight` no le corresponde; (4) codificación ordinal arbitraria para nominales; (5) `requirements.txt` pide scikit-learn ≥ 1.3 pero las cifras salieron con 1.9.1.

## Mi revisión antes de pasarlo al auditor
- Leí `datos.py`, `modelos.py` y `validacion.py`: el codificador está dentro del `Pipeline`, `clase` se excluye de `X`, `clone()` en cada semilla.
- Las cifras coinciden con las de referencia del instructivo del curso (paso 26 y 27): 0.698 ± 0.017 / 0.53 y 0.759 ± 0.006 / 0.38; rangos 0.608–0.720 y 0.712–0.796.
- **Observación:** el ingeniero resolvió solo y por escrito el conflicto de instrucciones del analista (Observación 2 de la evidencia 01), en vez de elegir uno en silencio.
- **Observación:** renombró la función del curso `tres_modelos()` como `modelos_base()` (solo dos modelos). Correcto para esta tarea; habrá que añadir el boosting en la 6.2.
