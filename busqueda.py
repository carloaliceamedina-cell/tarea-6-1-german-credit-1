"""Búsqueda de hiperparámetros del árbol y control de su optimismo (Tarea 6.2)."""
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split

# Espacio fijado en PLAN_6_2.md: 8 × 5 = 40 combinaciones (None = valor por defecto)
PARAM_GRID = {
    "modelo__max_depth": [2, 3, 4, 5, 6, 8, 10, None],
    "modelo__min_samples_leaf": [1, 5, 10, 20, 50],
}


def buscar(pipeline, X, y, cv):
    """GridSearchCV con la CV del proyecto. Devuelve (mejores parámetros, puntaje, objeto)."""
    busqueda = GridSearchCV(pipeline, PARAM_GRID, cv=cv, scoring="accuracy")
    busqueda.fit(X, y)  # 40 combinaciones × 5 pliegues = 200 ajustes
    return busqueda.best_params_, busqueda.best_score_, busqueda


def buscar_con_prueba(pipeline, X, y, cv):
    """Prueba reservada: 20 % apartado desde el inicio, abierto una sola vez."""
    X_ent, X_pru, y_ent, y_pru = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=1)
    busqueda = GridSearchCV(pipeline, PARAM_GRID, cv=cv, scoring="accuracy").fit(X_ent, y_ent)
    return busqueda.best_params_, busqueda.best_score_, busqueda.score(X_pru, y_pru)


def validacion_anidada(pipeline, X, y, cv):
    """CV anidada: la búsqueda se repite dentro de cada pliegue externo."""
    externa = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    interna = GridSearchCV(pipeline, PARAM_GRID, cv=cv, scoring="accuracy")
    puntajes = cross_val_score(interna, X, y, cv=externa)
    return puntajes.mean(), puntajes.std(), puntajes
