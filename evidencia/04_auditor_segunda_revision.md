# Evidencia — Rol 3: auditor (segunda revisión)

- **Ejecución:** misma sesión del auditor, reanudada con la lista de correcciones, 2026-10-12.
- **Instrucción recibida:** "Comprueba cada corrección (no confíes en la descripción), verifica que no hay enlaces rotos en README.md y ROLES.md, y vuelve a ejecutar los scripts para confirmar que las cifras no cambiaron […] Solo puedes modificar AUDIT_REPORT.md."
- **Recibió de:** analista (H5, H6), ingeniero (H2, H3, H7) y Carlo (H1, H7).
- **Entregó:** sección "Segunda revisión" de `AUDIT_REPORT.md` → **a:** Carlo.

## Veredicto final: APROBADO

| Hallazgo | Estado |
|---|---|
| H1. Referencias rotas en README/ROLES | CERRADO (31 rutas citadas comprobadas: todas existen) |
| H2. Elegir por exactitud lleva al modelo más caro | ACEPTADO COMO DECISIÓN (pasa a la Tarea 6.2 con CV anidada) |
| H3. Árbol "por debajo" del piso | CERRADO ("indistinguible, −0.002 ± 0.017") |
| H4. Variables sensibles como predictoras | ACEPTADO COMO DECISIÓN (variante sin ellas en la 6.2) |
| H5. Método de la V de Cramér | CERRADO |
| H6. `handle_unknown` "necesario" | CERRADO |
| H7. Entorno incompleto | CERRADO |

Las cifras no cambiaron: los tres CSV regenerados salieron idénticos byte a byte y `python3 auditoria.py` mantiene las 8 revisiones en PASA.

## Observaciones menores de la segunda revisión
- **O1 (Carlo):** la bitácora citaba este archivo antes de que existiera → creado.
- **O2 (ingeniero):** RESULTADOS aún decía que `requirements.txt` "se fijaría" → devuelto al ingeniero, corregido en dos frases.

Detalle: el auditor también encontró en esta segunda vuelta un enlace roto que yo mismo había introducido al escribir la bitácora (O1). Es el mismo tipo de error que H1.
