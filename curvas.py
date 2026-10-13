"""Curva de aprendizaje y su gráfica (Tarea 6.2, punto 4)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.model_selection import learning_curve  # noqa: E402

# Paleta categórica validada (azul / naranja: ΔE CVD 24.7); además de color,
# las series se distinguen por trazo y marcador (lectura en blanco y negro).
AZUL, NARANJA, GRIS, TINTA = "#2a78d6", "#eb6834", "#8a8984", "#2b2b29"


def curva_aprendizaje(pipeline, X, y, cv, scoring="accuracy"):
    """Entrena con 15 %…100 % del entrenamiento de cada pliegue; devuelve medias por tamaño."""
    tamanos, ent, val = learning_curve(
        pipeline, X, y, cv=cv, train_sizes=np.linspace(0.15, 1.0, 7), scoring=scoring)
    return tamanos, ent.mean(axis=1), val.mean(axis=1)


def graficar_paneles(curvas, ruta, piso=0.70):
    """Un panel por modelo, mismo eje Y; entrenamiento y validación en cada panel."""
    fig, ejes = plt.subplots(1, len(curvas), figsize=(3.2 * len(curvas), 3.0),
                             sharey=True, constrained_layout=True)
    for ax, (nombre, (t, ent, val)) in zip(np.atleast_1d(ejes), curvas.items()):
        ax.axhline(piso, color=GRIS, lw=1, ls=(0, (2, 2)))
        ax.plot(t, ent, color=AZUL, lw=2, marker="o", ms=4.5, label="Entrenamiento")
        ax.plot(t, val, color=NARANJA, lw=2, ls="--", marker="s", ms=4.5, label="Validación")
        brecha = ent[-1] - val[-1]
        ax.set_title(f"{nombre}\nbrecha final {brecha:.2f}", fontsize=9.5, color=TINTA)
        ax.set_xlabel("Solicitudes de entrenamiento", fontsize=8.5, color=TINTA)
        ax.set_ylim(0.6, 1.02)
        ax.tick_params(labelsize=8, colors=TINTA)
        ax.grid(axis="y", color="#e4e3df", lw=0.6)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    primero = np.atleast_1d(ejes)[0]
    primero.set_ylabel("Exactitud", fontsize=8.5, color=TINTA)
    primero.text(np.mean(t), piso + 0.006, "siempre «good» 0.70", fontsize=7.5,
                 color=GRIS, ha="center", va="bottom")
    np.atleast_1d(ejes)[-1].legend(fontsize=8, frameon=False, loc="lower right")
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
