#!/bin/sh
# Paso 2 de la Skill: inventario de evidencia con grep (archivo:línea).
# Ejecutar desde la raíz del proyecto:
#   sh auditorias/6_2_boosting_elegido/evidencia/inventario.sh > auditorias/6_2_boosting_elegido/evidencia/inventario.txt
F="datos.py modelos.py validacion.py busqueda.py defecto_vs_afinado.py numero_honesto.py comparar_tres.py sin_variables_sensibles.py curvas.py curvas_comparadas.py"
for patron in '\.fit(' 'fit_transform' 'train_test_split' 'StratifiedKFold' 'random_state' 'Pipeline' 'ColumnTransformer' 'GridSearchCV' 'cross_val_score' 'cross_val_predict' 'cross_validate' 'learning_curve' 'class_weight' 'drop(columns' 'np\.random' 'default_rng' 'validar' 'housing' 'personal_status' 'groupby'; do
  echo "## $patron"
  grep -n -- "$patron" $F || echo "(sin coincidencias)"
  echo
done
echo "## Divisiones '/' en código (excluye comentarios, cadenas de rutas y operador de pathlib)"
grep -n '/' $F | grep -v '^\S*:[0-9]*:\s*#' | grep -v '"""' || echo "(sin coincidencias)"
