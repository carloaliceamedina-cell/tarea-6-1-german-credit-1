"""Protocolos de medición: validación cruzada y partición única repetida."""
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import cross_val_predict, cross_val_score, train_test_split

SEMILLAS_PARTICION = list(range(10))  # fijadas antes de ver resultados


def validar(pipeline, X, y, cv):
    """Media y desviación de la exactitud en los pliegues de cv."""
    puntuaciones = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
    return puntuaciones.mean(), puntuaciones.std(), puntuaciones


def proporcion_malos_detectados(pipeline, X, y, cv):
    """Recall de 'bad' (y=1) con cross_val_predict.

    Cada solicitud la predice un modelo que no la vio. Devuelve el recall
    global y, como apoyo, el recall por pliegue (mismos pliegues de cv).
    """
    pred = cross_val_predict(pipeline, X, y, cv=cv)
    global_ = recall_score(y, pred, pos_label=1)
    por_pliegue = np.array([
        recall_score(y.iloc[prueba], pred[prueba], pos_label=1)
        for _, prueba in cv.split(X, y)
    ])
    detectados = int(((pred == 1) & (y.to_numpy() == 1)).sum())
    return global_, por_pliegue, detectados, int(y.sum())


def particion_unica(pipeline, X, y, semillas=SEMILLAS_PARTICION):
    """Exactitud y recall de 'bad' con train_test_split 75/25 estratificado por semilla."""
    filas = []
    for s in semillas:
        X_ent, X_pru, y_ent, y_pru = train_test_split(
            X, y, test_size=0.25, stratify=y, random_state=s)
        p = clone(pipeline)  # pipeline nuevo, sin estado previo
        p.fit(X_ent, y_ent)
        pred = p.predict(X_pru)
        filas.append({
            "semilla": s,
            "exactitud": accuracy_score(y_pru, pred),
            "recall_bad": recall_score(y_pru, pred, pos_label=1),
        })
    return pd.DataFrame(filas)
