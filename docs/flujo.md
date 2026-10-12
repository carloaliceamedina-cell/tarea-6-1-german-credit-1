# Flujo de trabajo con roles especializados

```
data/credit_g.csv
      │ (solo lectura)
      ▼
┌──────────────────┐  resumen_datos.json / .md  ┌────────────────────┐  métricas CSV + reporte  ┌──────────┐
│ 1. Analista      │ ─────────────────────────▶ │ 2. Ingeniero de    │ ───────────────────────▶ │ 3. Auditor│
│    de datos      │                            │    modelos         │                          │          │
└──────────────────┘                            └────────────────────┘                          └────┬─────┘
        ▲                                                ▲                                           │
        └──────────── hallazgos devueltos al rol responsable (si los hay) ◀─────────────────────────┘
```

| Rol | Definición | Recibe | Entrega | A quién |
|---|---|---|---|---|
| Analista de datos | `.claude/agents/analista-datos.md` | `data/credit_g.csv` | `entregables/01_analista/resumen_datos.{json,md}` | Ingeniero |
| Ingeniero de modelos | `.claude/agents/ingeniero-modelos.md` | resumen del analista + datos | `entregables/02_ingeniero/*.csv`, `reporte_ingeniero.md` | Auditor |
| Auditor | `.claude/agents/auditor.md` | todo lo anterior | `entregables/03_auditor/reporte_auditor.md`, `auditoria.json` | Analista / ingeniero (hallazgos) y responsable del proyecto |

## Reglas de ejecución
- Cada rol se ejecuta en una sesión **separada** (subagente de Claude Code con
  su propio contexto). Ningún rol ve la conversación de otro: solo los
  archivos de entrega. Así el ingeniero no hereda supuestos no escritos del
  analista, y el auditor no "sabe" lo que el ingeniero quiso hacer.
- Orden: analista → ingeniero → auditor. Si el auditor emite hallazgos, el rol
  responsable los corrige en una nueva ejecución y el auditor vuelve a revisar.
- Cada entrega queda en un commit propio.
- La bitácora de cada ejecución (instrucción recibida, archivos tocados,
  duración y resumen devuelto) se guarda en `entregables/bitacora_flujo.md`.
