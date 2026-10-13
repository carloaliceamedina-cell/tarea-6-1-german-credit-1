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
informe/                   informe técnico en APA 7 (.docx)
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

---

# Tarea 6.2 — Optimización y auditoría del modelo

Continúa este mismo repositorio. El plan y la regla de selección se fijaron
antes de medir en `PLAN_6_2.md`; el registro de trabajo está en `BITACORA_6_2.md`.

| Archivo | Qué hace |
|---|---|
| `busqueda.py`, `defecto_vs_afinado.py` | GridSearchCV del árbol (40 combinaciones) y mejora frente al defecto |
| `numero_honesto.py` | Prueba reservada (20 %) y validación cruzada anidada |
| `comparar_tres.py` | Árbol afinado, Random Forest y boosting (+ variantes con peso 5:1): exactitud, malos detectados, tiempo y coste |
| `sin_variables_sensibles.py` | Modelo elegido con y sin `age`, `personal_status`, `foreign_worker` |
| `curvas.py`, `curvas_comparadas.py` | Curvas de aprendizaje → `figs/curvas_aprendizaje.png` |
| `auditoria_subgrupos.py` | Malos detectados y buenos rechazados por subgrupo del modelo elegido |
| `tests/test_modelo.py` | Pruebas pytest (piso 0.70, estabilidad, recall ≥ 0.50, Pipeline, sin variables sensibles) |
| `.claude/skills/auditoria-modelos/` | Skill de auditoría (reconstrucción v2.2-r de la Tarea 4.1) |
| `auditorias/6_2_boosting_elegido/` | Informe de la Skill sobre el modelo elegido y su evidencia |

```bash
python defecto_vs_afinado.py
python numero_honesto.py        # ~30 s
python comparar_tres.py
python sin_variables_sensibles.py
python curvas_comparadas.py
python auditoria_subgrupos.py
pytest -v                       # 8 passed, 1 xfailed
```

**Modelo recomendado:** `HistGradientBoostingClassifier(class_weight={0: 1, 1: 5})`
sin variables sensibles: exactitud 0.726 ± 0.020, detecta 0.64 de los créditos
malos y tiene coste 706 (frente a 989 del Random Forest y 1,500 de «siempre good»).
