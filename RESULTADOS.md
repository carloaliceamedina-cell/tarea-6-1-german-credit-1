# Resultados de modelado — German Credit

Rol: ingeniero de modelos · MAI 540, Tarea 6.1 · Fecha: 2026-10-12

Entrada: `datos/RESUMEN.md` (analista) y `datos/credit_g.csv` (solo lectura;
MD5 `19d37d4238836d135ab13d73dc42d5e4`, igual al del RESUMEN antes y después
de ejecutar). Entorno: Python 3, scikit-learn 1.9.1.

## Protocolo

- **Datos** (`datos.py` → `cargar_datos()`): `y = 1` si `clase == "bad"`;
  `clase` se quita de `X` (1000 × 20). Columnas con texto detectadas por tipo:
  las 13 que lista el RESUMEN (se comprobó que coinciden). 7 numéricas.
- **Pipeline** (`modelos.py` → `crear_pipeline()`): `ColumnTransformer` con
  `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)` para
  las 13 de texto y `remainder="passthrough"` para las numéricas, seguido del
  modelo. Al ir dentro del `Pipeline`, el codificador se ajusta solo con el
  entrenamiento de cada pliegue/partición.
- **Modelos**: `DecisionTreeClassifier(random_state=42)` y
  `RandomForestClassifier(random_state=42)`, resto de hiperparámetros por
  defecto. No se ajustó nada tras ver resultados.
- **Validación cruzada**: `StratifiedKFold(n_splits=5, shuffle=True,
  random_state=42)` (200 filas y 60 `bad` por pliegue de prueba, verificado).
  - Exactitud: `cross_val_score` → media y desviación (np.std, ddof=0).
  - Malos detectados: recall de `bad` (`pos_label=1`) sobre las predicciones
    de `cross_val_predict` con el mismo `cv`. Además se reporta la desviación
    del recall por pliegue (ver Decisiones).
- **Partición única**: `train_test_split(test_size=0.25, stratify=y)` con
  semillas 0–9 fijadas de antemano; `clone()` del pipeline en cada semilla.
- **Piso**: decir siempre `good` → exactitud 0.70 y 0/300 malos detectados.

Ejecución (desde la raíz): `python3 tabla_cv.py` y `python3 particion_vs_cv.py`.
Se ejecutaron dos veces y los tres CSV salieron idénticos byte a byte.

## Tabla de validación cruzada (5 pliegues)

| Modelo | Exactitud media | Desv. | Malos detectados (recall `bad`) | Desv. por pliegue | Detectados | ¿Supera 0.70? |
|---|---:|---:|---:|---:|---:|:---:|
| Árbol de decisión | 0.6980 | 0.0169 | 0.5300 | 0.0414 | 159/300 | No |
| Random Forest | 0.7590 | 0.0058 | 0.3767 | 0.0170 | 113/300 | Sí |

Archivo: `resultados/tabla_cv.csv`.

Lectura: el árbol no supera el piso de exactitud (0.698 < 0.70), aunque
detecta más malos (53 %). El Random Forest supera el piso por ~6 puntos, pero
deja sin detectar a casi dos de cada tres malos (62 %). Ninguno de los dos es
claramente "bueno" para la clase de interés.

## Partición única (10 semillas) frente a validación cruzada — exactitud

| Modelo | Mín. | Máx. | Rango | Media | Desv. | Media CV | Desv. CV | Diferencia (media − CV) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Árbol de decisión | 0.6080 | 0.7200 | 0.1120 | 0.6744 | 0.0291 | 0.6980 | 0.0169 | −0.0236 |
| Random Forest | 0.7120 | 0.7960 | 0.0840 | 0.7532 | 0.0264 | 0.7590 | 0.0058 | −0.0058 |

Archivos: `resultados/particion_unica.csv` (20 filas: modelo × semilla, con
exactitud y recall de `bad`) y `resultados/particion_vs_cv.csv`.

Lectura: con una sola partición, la exactitud depende mucho de la semilla
(rango de 11 puntos en el árbol y 8 en el RF). Según la semilla, el árbol
parecería "superar el piso" (semilla 4: 0.704; semilla 9: 0.720) o quedar muy
por debajo (semilla 0: 0.608). Por eso la cifra de referencia es la de la
validación cruzada.

## Salida de consola (tal cual)

```
$ python3 tabla_cv.py
Validación cruzada: StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
Piso (siempre 'good'): exactitud 0.70, malos detectados 0.00 (0/300)

           modelo  exactitud_media  exactitud_desv  malos_detectados  malos_detectados_desv malos_detectados_n  supera_piso_0.70
Árbol de decisión           0.6980          0.0169            0.5300                 0.0414            159/300             False
    Random Forest           0.7590          0.0058            0.3767                 0.0170            113/300              True

Guardado: resultados/tabla_cv.csv
```

```
$ python3 particion_vs_cv.py
Partición única: train_test_split(test_size=0.25, stratify=y), semillas [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Detalle por modelo y semilla:
           modelo  semilla  exactitud  recall_bad
Árbol de decisión        0     0.6080      0.3600
Árbol de decisión        1     0.6600      0.5200
Árbol de decisión        2     0.6640      0.4667
Árbol de decisión        3     0.6720      0.5467
Árbol de decisión        4     0.7040      0.4533
Árbol de decisión        5     0.6880      0.5467
Árbol de decisión        6     0.6640      0.5733
Árbol de decisión        7     0.6960      0.5067
Árbol de decisión        8     0.6680      0.4667
Árbol de decisión        9     0.7200      0.6533
    Random Forest        0     0.7320      0.3333
    Random Forest        1     0.7560      0.4267
    Random Forest        2     0.7320      0.3067
    Random Forest        3     0.7760      0.4133
    Random Forest        4     0.7120      0.2933
    Random Forest        5     0.7520      0.3467
    Random Forest        6     0.7960      0.4267
    Random Forest        7     0.7840      0.4533
    Random Forest        8     0.7240      0.3067
    Random Forest        9     0.7680      0.5067

Exactitud en partición única frente a validación cruzada (5 pliegues):
           modelo  minimo  maximo  rango  media  desviacion  media_cv  desv_cv  diferencia_vs_cv
Árbol de decisión  0.6080  0.7200 0.1120 0.6744      0.0291    0.6980   0.0169           -0.0236
    Random Forest  0.7120  0.7960 0.0840 0.7532      0.0264    0.7590   0.0058           -0.0058

Guardado: resultados/particion_unica.csv, resultados/particion_vs_cv.csv
```

## Decisiones tomadas

1. **Se usaron las 20 predictoras, incluidas `age`, `personal_status` y
   `foreign_worker`** (indicación 6 del RESUMEN). Así lo pide el flujo; no
   se excluyeron. Queda para el auditor evaluarlas por subgrupo.
2. **Desviación del recall.** Mi definición de rol pide el recall sobre
   `cross_val_predict` (una sola cifra global); el RESUMEN pide además media y
   desviación entre pliegues. Hice ambas: el recall global sale de
   `cross_val_predict` y la desviación se calcula por pliegue sobre esas mismas
   predicciones, partidas con los mismos pliegues de `cv`. Como cada pliegue
   tiene exactamente 60 `bad`, el recall global coincide con la media de los
   recalls por pliegue.
3. **Desviación con ddof=0** en ambos protocolos (la de `cross_val_score().std()`
   de NumPy), para que la comparación partición única vs CV sea homogénea.
4. **Columnas de texto detectadas por tipo** (`object`/`string`) en vez de
   escribirlas a mano; se verificó que son exactamente las 13 del RESUMEN.
5. **Ordinales sin reordenar** (`checking_status`, `savings_status`,
   `employment`): se codificaron con el orden alfabético por defecto del
   `OrdinalEncoder`, como sugiere el RESUMEN.
6. Se añadió `recall_bad` a `particion_unica.csv` como información extra; la
   tabla de comparación con CV es solo de exactitud, como pide el rol.

## Dudas abiertas para el auditor

1. **Variables sensibles**: ¿se aceptan `age`, `personal_status` y
   `foreign_worker` como predictoras? Conviene medir exactitud y recall de
   `bad` por subgrupo (edad ≤ 25 vs > 25, `personal_status`, `foreign_worker`),
   teniendo en cuenta que `foreign_worker = no` tiene solo 37 filas.
2. **Árbol bajo el piso**: con valores por defecto el árbol (0.698) no supera
   el 0.70 de "siempre `good`". No se ajustaron hiperparámetros por regla de
   rol; si se quisiera, tendría que hacerse con CV anidada y decidirse antes.
3. **Recall bajo del Random Forest** (0.377): el umbral de 0.5 por defecto
   favorece a `good`. Cambiar el umbral o usar `class_weight` es una decisión
   de negocio/protocolo que no tomé.
4. **Codificación ordinal arbitraria** en variables nominales (p. ej.
   `purpose`): para árboles es aceptable, pero el auditor puede querer
   comprobar si una codificación con orden natural o one-hot cambia algo.
5. **Reproducibilidad entre versiones**: las cifras son con scikit-learn 1.9.1;
   `requirements.txt` solo fija mínimos (`>=1.3`), así que otra versión podría
   dar decimales distintos.

Entregado a: auditor
