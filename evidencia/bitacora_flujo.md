# Bitácora del flujo distribuido

Responsable del proyecto: Carlo E. Alicea Medina. Herramienta: Claude Code, con
cada rol ejecutado como **subagente independiente** (contexto propio; solo ve
los archivos del repositorio, no la conversación de los otros roles).
Fecha de ejecución: 12 de octubre de 2026.

## Entregas (quién entregó qué a quién)

| # | Rol | Recibió | Entregó | A quién | Duración | Llamadas a herramientas | Tokens aprox. | Commit |
|---|---|---|---|---|---:|---:|---:|---|
| 1 | Analista de datos | `datos/credit_g.csv` | `datos/RESUMEN.md` | Ingeniero | 73 s | 7 | 83 k | `Analista: entregar datos/RESUMEN.md…` |
| 2 | Ingeniero de modelos | `RESUMEN.md` + datos | 5 scripts, `resultados/*.csv`, `RESULTADOS.md` | Auditor | 101 s | 5 | 83 k | `Ingeniero: Pipeline…` y `Ingeniero: entregar RESULTADOS.md…` |
| 3 | Auditor | todo lo anterior | `auditoria.py`, `AUDIT_REPORT.md` (H1–H7) | Carlo + analista + ingeniero | 340 s | 13 | 132 k | `Auditor: entregar AUDIT_REPORT.md…` |
| 4 | Analista (corrección) | H5, H6 | `RESUMEN.md` corregido | Auditor | — | — | — | `Analista: corregir H5…` |
| 5 | Ingeniero (corrección) | H2, H3, H7 | `RESULTADOS.md` corregido | Auditor | — | — | — | `Ingeniero: corregir H2, H3 y H7…` |
| 6 | Carlo (corrección) | H1, H7 | esta bitácora, `README.md`, `versiones_exactas.txt` | Auditor | — | — | — | `Corregir H1 y H7…` |
| 7 | Auditor (segunda revisión) | correcciones 4–6 | sección "Segunda revisión" en `AUDIT_REPORT.md` | Carlo | ver evidencia 04 | | | `Auditor: segunda revisión…` |

La respuesta textual de cada rol y mi revisión antes de pasar al siguiente
están en `evidencia/01_analista_respuesta.md`, `02_ingeniero_respuesta.md`,
`03_auditor_respuesta.md` y `04_auditor_segunda_revision.md`.

## Qué le pedí, qué hizo, qué verifiqué, qué corregí

| Qué le pedí | Qué hizo el rol | Qué verifiqué yo | Qué se corrigió |
|---|---|---|---|
| Analista: resumir los datos siguiendo su definición | Resumen completo, con cifras calculadas y MD5 del CSV | Forma, 700/300, 13 columnas de texto, 0 faltantes: coinciden | Leyó la definición del ingeniero (fuera de su rol) y copió el codificador en sus indicaciones; lo registré como observación |
| Analista: indicar métricas al ingeniero | Pidió recall "con media y desviación entre pliegues" | Vi que contradecía la definición del ingeniero (recall global con `cross_val_predict`) | No intervine, para ver cómo lo resolvía el ingeniero |
| Ingeniero: construir y medir los dos modelos | Reportó ambas formas del recall y explicó por qué coinciden (60 `bad` por pliegue) | Cifras idénticas a las de referencia del instructivo | Nada en ese momento |
| Auditor: comprobar todo ejecutando | Recalculó 68 cifras, hizo prueba de etiquetas permutadas, matriz de confusión propia y auditoría por subgrupo | `python3 auditoria.py` reproduce sus cifras | Encontró 7 hallazgos; uno era mío (H1: README con un enlace a un archivo que yo había borrado) |
| Analista e ingeniero: corregir sus hallazgos | Corrigieron solo sus propios archivos | Revisé los `git diff` | H3, H5, H6 corregidos en redacción; H7 versiones anotadas |

## Decisiones del responsable del proyecto (H2 y H4)

- **H2 (umbral / `class_weight`):** no se cambia en la Tarea 6.1. La tarea pide
  medir los modelos por defecto; ajustar el umbral después de ver los datos
  sería optimista. Queda como punto de partida de la Tarea 6.2, con validación
  cruzada anidada.
- **H4 (variables sensibles como predictoras):** se mantienen las 20
  predictoras en la 6.1 para que la medición siga el protocolo del curso. En la
  6.2 se medirá la variante sin `age`, `personal_status` y `foreign_worker` con
  el mismo protocolo, decidido antes de ver resultados.
