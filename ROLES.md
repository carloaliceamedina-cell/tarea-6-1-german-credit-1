# Roles del flujo

Definiciones completas en `.claude/agents/`. Cada rol se ejecuta en una sesión
**separada** (subagente con contexto propio): ningún rol ve la conversación de
otro, solo los archivos que le entregan.

| Rol | Responsabilidad | Puede tocar | No puede tocar | Entrega | A quién |
|---|---|---|---|---|---|
| Analista de datos | Entender y resumir los datos sin transformarlos | `datos/credit_g.csv` (solo lee), `datos/RESUMEN.md` | Código de modelado, `RESULTADOS.md`, `AUDIT_REPORT.md` | `datos/RESUMEN.md` | Ingeniero de modelos |
| Ingeniero de modelos | Construir el Pipeline y medir árbol y Random Forest (CV 5 pliegues + partición única ×10) | `datos.py`, `modelos.py`, `validacion.py`, `tabla_cv.py`, `particion_vs_cv.py`, `resultados/`, `RESULTADOS.md` | Datos, `RESUMEN.md`, archivos del auditor; semillas tras ver resultados | `RESULTADOS.md` + `resultados/*.csv` | Auditor |
| Auditor | Comprobar reproducibilidad, fuga, clase positiva, coherencia y subgrupos; emitir veredicto | Lee todo; crea `auditoria.py` y `AUDIT_REPORT.md` | Código y entregables ajenos (no corrige: devuelve hallazgos) | `AUDIT_REPORT.md` | Responsable del proyecto y roles con hallazgos |

**Orden:** Analista → Ingeniero → Auditor → (si hay hallazgos) rol responsable → Auditor.

**Regla contra conflictos:** un solo rol modifica cada archivo.

**Por qué tres roles y no cuatro:** el instructivo propone además un
*responsable de pruebas*. Las pruebas automáticas se califican en la Tarea 6.2,
así que ese rol se añadirá allí, partiendo de las reglas de `AUDIT_REPORT.md`.

## Registro de entregas

Ver `evidencia/bitacora_flujo.md` (instrucción que recibió cada rol, qué
entregó, a quién, y qué revisé yo antes de pasarlo al siguiente).
