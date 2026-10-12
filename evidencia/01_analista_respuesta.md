# Evidencia — Rol 1: analista de datos

- **Ejecución:** subagente independiente (contexto propio), 2026-10-12.
- **Duración:** 73 s · 7 llamadas a herramientas · ~83 k tokens.
- **Instrucción recibida:** "Tu rol: ANALISTA DE DATOS. Lee primero tu definición en `.claude/agents/analista-de-datos.md` y síguela al pie de la letra […] No uses git. No crees archivos fuera de lo que tu definición permite […] Cada cifra de `datos/RESUMEN.md` debe salir de un cálculo que hayas ejecutado."
- **Entregó:** `datos/RESUMEN.md` → **a:** ingeniero-de-modelos.

## Respuesta devuelta por el rol (copiada tal cual)

> **(1) Archivos creados o modificados:** Creé `datos/RESUMEN.md`. No modifiqué nada más: MD5 de `datos/credit_g.csv` igual antes y después (`19d37d4238836d135ab13d73dc42d5e4`). No dejé scripts en disco. No usé git.
>
> **(2) Comandos de verificación:** lectura de la definición del rol, `ROLES.md`, `README.md`, `ingeniero-de-modelos.md` y `convertir_desde_xlsx.py`; `md5sum` y `wc -l` del CSV; con pandas: forma, tipos, conteos de `clase`, columnas numéricas/texto y categorías; faltantes (incl. `""`, `?`, `NA`, `nan`, `None`), espacios y duplicados con y sin `clase`; `describe()`; tablas cruzadas y V de Cramér de cada columna con `clase`; tasas de `bad` por edad, `personal_status` y `foreign_worker`; comprobación de que `StratifiedKFold(5, shuffle=True, random_state=42)` deja 200 filas y 60 `bad` por pliegue (solo partición, sin entrenar).
>
> **(3) Lo que entrega:** 1,000 × 21; `good` 700 / `bad` 300; piso "siempre good" = 0.70 con recall 0. 7 numéricas (passthrough) y 13 de texto (OrdinalEncoder dentro del Pipeline). Sin faltantes ni duplicados. Sin columnas de fuga (máx. V de Cramér 0.352, `checking_status`); el riesgo de fuga es de procedimiento. Variables sensibles con tasas de `bad` distintas (≤25 años 0.421 vs 0.272; `foreign_worker = no` solo 37 filas). Pendiente: documentar si `age`, `personal_status` y `foreign_worker` se usan como predictoras.

## Mi revisión antes de pasarlo al ingeniero
- Comprobé por mi cuenta forma (1000, 21), 700/300, 13 columnas de texto, 0 faltantes, 0 duplicados: coinciden.
- **Observación 1 (límite de rol):** el analista leyó `ingeniero-de-modelos.md` y copió en sus "Indicaciones" el codificador exacto de la definición del ingeniero. No rompió nada, pero muestra que los roles se "espían" si pueden leer todo el repositorio.
- **Observación 2 (instrucciones en conflicto):** el analista pide reportar el recall de `bad` "con media y desviación entre pliegues", mientras la definición del ingeniero pide un recall agregado con `cross_val_predict`. Lo dejo pasar sin corregir para ver cómo lo resuelve el ingeniero.
