# Tarea 6.1 — Flujo de trabajo con agentes especializados (German Credit)

MAI 540: Machine Learning · Atlantis University · Prof. Kevin A. García Gallardo
Autor: Carlo E. Alicea Medina

Evaluación de un árbol de decisión y un Random Forest sobre German Credit
(1,000 solicitudes, 20 variables, clase `good`/`bad`), repartiendo el trabajo
entre tres roles especializados que se entregan archivos entre sí.

## Estructura

```
.claude/agents/            definiciones de los tres roles (analista, ingeniero, auditor)
ROLES.md                   tabla de roles: responsabilidad, límites, entregable y destinatario
datos/credit_g.csv         datos (convertidos del xlsx de Moodle con datos/convertir_desde_xlsx.py)
datos/RESUMEN.md           entregable del analista de datos
datos.py, modelos.py,      código del ingeniero de modelos (Pipeline con codificación
validacion.py              dentro de cada pliegue, validación cruzada, partición única)
tabla_cv.py                tabla de validación cruzada (5 pliegues, semilla 42)
particion_vs_cv.py         partición 75/25 con 10 semillas frente a la validación cruzada
resultados/                CSV generados por los dos scripts anteriores
RESULTADOS.md              entregable del ingeniero de modelos
auditoria.py               comprobaciones independientes del auditor
AUDIT_REPORT.md            entregable del auditor (veredicto y hallazgos H1–H7)
evidencia/                 respuesta de cada rol, mi revisión y bitácora del flujo
versiones_exactas.txt      entorno exacto con el que se obtuvieron las cifras
```

## Cómo reproducir

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tabla_cv.py          # Tabla de validación cruzada
python particion_vs_cv.py   # Partición única ×10 frente a la validación cruzada
python auditoria.py         # Comprobaciones del auditor (~20 s)
```

## Resultados principales (validación cruzada estratificada, 5 pliegues, semilla 42)

| Modelo | Exactitud (media ± desv.) | Malos detectados | Partición única ×10 (rango) |
|---|---|---|---|
| Árbol de decisión | 0.698 ± 0.017 | 0.53 (159/300) | 0.608 – 0.720 |
| Random Forest | 0.759 ± 0.006 | 0.38 (113/300) | 0.712 – 0.796 |

Piso de referencia: decir siempre `good` acierta 0.70 y no detecta ningún
crédito malo.

## Flujo

Analista → Ingeniero → Auditor → correcciones de cada rol → segunda revisión
del auditor. Detalle en `ROLES.md` y `evidencia/bitacora_flujo.md`.
