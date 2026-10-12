# Evidencia — Rol 3: auditor (primera revisión)

- **Ejecución:** subagente independiente (contexto propio, no vio las sesiones del analista ni del ingeniero), 2026-10-12.
- **Duración:** 340 s · 13 llamadas a herramientas · ~132 k tokens (el rol más caro del flujo).
- **Instrucción recibida:** "Tu rol: AUDITOR. Lee primero tu definición en `.claude/agents/auditor.md` […] No confíes en lo que dicen: compruébalo ejecutando. […] Si al reproducir los scripts del ingeniero se sobrescriben archivos de resultados/, guarda antes una copia fuera del proyecto […] y deja resultados/ exactamente como estaba."
- **Recibió de:** analista (`datos/RESUMEN.md`) e ingeniero (`RESULTADOS.md`, `resultados/`, código).
- **Entregó:** `auditoria.py`, `AUDIT_REPORT.md` → **a:** responsable del proyecto (Carlo) y roles con hallazgos.

## Veredicto: APROBADO CON OBSERVACIONES

| # | Revisión | Veredicto |
|---|---|---|
| 1 | Reproducibilidad (68 cifras recalculadas, CSV idénticos byte a byte) | PASA |
| 2 | Fuga (codificador por pliegue; etiquetas permutadas → RF 0.676) | PASA |
| 3 | Clase positiva (matriz de confusión propia: 159/300 y 113/300) | PASA |
| 4 | Coherencia analista → ingeniero (0 discrepancias en cifras) | PASA |
| 5 | Partición (5 × 200 filas con 60 `bad`; 10 conjuntos de prueba distintos) | PASA |
| 6 | Línea base "siempre good" | PASA |
| 7 | Subgrupos (`housing`, `personal_status`, + `age`, `foreign_worker`) | PASA con avisos |
| 8 | Lectura de negocio (coste 5:1 → árbol 866, RF 989) | PASA (obs. H2) |

## Hallazgos y a quién se devolvieron

| Hallazgo | Tipo | Responsable | Acción |
|---|---|---|---|
| H1. `README.md` cita `docs/flujo.md` y `ROLES.md` cita `evidencia/bitacora_flujo.md`; ninguno existe | **Error real** | Carlo (orquestación) | Crear la bitácora y corregir el README |
| H2. El RF "supera el piso" pero solo detecta 113/300 y cuesta más que el árbol con la matriz 5:1 | Observación | Ingeniero / decisión de Carlo | Reportar coste o recall junto a la exactitud; umbral o `class_weight` solo con CV anidada (Tarea 6.2) |
| H3. "El árbol no supera el piso" es engañoso: −0.002 ± 0.019, indistinguible | **Error de redacción** | Ingeniero | Matizar |
| H4. `age`, `personal_status`, `foreign_worker` usadas como predictoras; buenos rechazados distintos por subgrupo | Observación | Carlo con el ingeniero | Decidir de antemano si se excluyen |
| H5. Método de la V de Cramér mal descrito ("quintiles") | **Error de documentación** | Analista | Escribir el método exacto |
| H6. "`handle_unknown` es necesario" es exagerado (0 categorías nuevas en prueba) | Observación | Analista | Reformular |
| H7. Entorno incompleto (solo cita scikit-learn) y `requirements.txt` sin versiones fijas | **Error de reproducibilidad** | Ingeniero (+ Carlo para `requirements.txt`) | Anotar y fijar versiones |

Hallazgo del auditor que **no** vio el ingeniero: la auditoría por subgrupo. Los hombres divorciados o separados (`male div/sep`, n = 50) tienen la exactitud más baja con el RF (0.620 frente a 0.783 en `male single`), pero con un IC del recall de [0.15, 0.52] no permite conclusiones firmes.

## Mi revisión
- Verifiqué que `python3 auditoria.py` corre desde la raíz y reproduce las cifras del reporte.
- H1 es real: al reestructurar el repositorio siguiendo el instructivo, dejé el README con una referencia al `docs/flujo.md` que había borrado. Ningún otro rol tenía motivo para revisar el README; el auditor lo encontró porque su definición le pide leer todo el proyecto.
