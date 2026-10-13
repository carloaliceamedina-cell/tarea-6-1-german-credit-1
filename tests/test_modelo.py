"""Pruebas automáticas de la Tarea 6.2 (reglas del plan y de la auditoría).

Umbrales (justificados en PLAN_6_2.md):
- 0.70: exactitud de decir siempre «good»; un modelo que no la supera no aporta.
- 0.05: desviación máxima entre pliegues; ±2 desviaciones = ±10 puntos, el máximo
  tolerable para comparar modelos que difieren en 3-6 puntos (la peor de la 6.1 fue 0.017).
- 0.50: el modelo elegido debe detectar al menos la mitad de los créditos malos
  (el Random Forest por defecto detecta 0.38).
"""
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder

from datos import SENSIBLES, cargar_datos, cargar_datos_sin_sensibles
from modelos import crear_pipeline, tres_modelos, variantes_con_coste
from validacion import proporcion_malos_detectados, validar

X, y, cols_cat, cv = cargar_datos()
X_sin, _, cols_cat_sin, _ = cargar_datos_sin_sensibles()

MODELOS = {
    "Árbol por defecto": tres_modelos()["Árbol"],
    "Árbol afinado": tres_modelos(max_depth=5, min_samples_leaf=1)["Árbol"],
    "Random Forest": tres_modelos()["Random Forest"],
    "Boosting": tres_modelos()["Boosting"],
    "Boosting 5:1 (elegido)": variantes_con_coste()["Boosting (peso 5:1)"],
}
ELEGIDO = "Boosting 5:1 (elegido)"  # se evalúa SIN variables sensibles


def pipe(nombre):
    return crear_pipeline(MODELOS[nombre], cols_cat_sin if nombre == ELEGIDO else cols_cat)


def datos(nombre):
    return X_sin if nombre == ELEGIDO else X


@pytest.mark.parametrize("nombre", [
    pytest.param("Árbol por defecto", id="arbol_defecto", marks=pytest.mark.xfail(
        strict=True, reason="Diagnóstico de la 6.1: 0.698, no supera a 'siempre good'")),
    pytest.param("Árbol afinado", id="arbol_afinado"),
    pytest.param("Random Forest", id="random_forest"),
    pytest.param("Boosting", id="boosting"),
    pytest.param(ELEGIDO, id="boosting_5a1_elegido"),
])
def test_supera_a_siempre_bueno(nombre):
    media, _, _ = validar(pipe(nombre), datos(nombre), y, cv)
    assert media > 0.70


def test_resultado_estable():
    _, desv, _ = validar(pipe(ELEGIDO), X_sin, y, cv)
    assert desv < 0.05


def test_detecta_al_menos_la_mitad_de_los_malos():
    recall, _, _, _ = proporcion_malos_detectados(pipe(ELEGIDO), X_sin, y, cv)
    assert recall >= 0.50


def test_codificacion_dentro_del_pipeline_y_sin_objetivo():
    p = pipe(ELEGIDO)
    prep = p.steps[0][1]
    assert isinstance(prep, ColumnTransformer)
    assert isinstance(prep.transformers[0][1], OrdinalEncoder)
    assert "clase" not in X_sin.columns
    assert len(cols_cat_sin) == 11


def test_modelo_elegido_no_usa_variables_sensibles():
    assert not set(SENSIBLES) & set(X_sin.columns)
