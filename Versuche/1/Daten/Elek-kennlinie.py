import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches

def plot_and_save(df, title, filename, marker="o", color=None, base_dir=None):
    fig, ax = plt.subplots(figsize=(8, 6))

    x = df["U_V"].values
    y = df["I_mA"].values
    yerr = df["I_err"].values if "I_err" in df.columns else None

    # --- Messkurve ---
    ax.errorbar(
        x, y,
        xerr=None, yerr=yerr,
        fmt=marker, capsize=3, linestyle="-",
        linewidth=1.5, markersize=4, color=color, zorder=3,
    )

    # --- Tangente: Fit an den steilsten Bereich (letztes Drittel der Daten) ---
    # Steilsten linearen Abschnitt automatisch finden: größte Steigung per gleitendem Fenster
    U_z = 2.8
    # Fit im Bereich ab 3.3 V (steilster Anstieg deiner Kurve)
    mask_steep = (x >= 3.3)
    if mask_steep.sum() >= 2:
        coeffs = np.polyfit(x[mask_steep], y[mask_steep], 1)
    else:
        # Fallback: letztes Drittel
        n = len(x)
        coeffs = np.polyfit(x[n//2:], y[n//2:], 1)

    slope, intercept = coeffs
    # Nulldurchgang der Tangente = Schnittpunkt mit I=0 → Zersetzungsspannung
    U_cross = -intercept / slope
    print(f"Tangenten-Nulldurchgang (Zersetzungsspannung): {U_cross:.3f} V")

    # Tangente von Nulldurchgang bis rechts über den Plot zeichnen
    U_tang = np.linspace(U_cross, x.max() + (x.max() - x.min()) * 0.08, 200)
    I_tang = slope * U_tang + intercept
    ax.plot(
        U_tang, I_tang,
        linestyle=":", linewidth=1.8, color="black", zorder=4,
    )

    # --- Zersetzungsspannung: senkrechter Strich + Beschriftung ---
    ax.axvline(x=U_cross, color="black", linestyle="-.", linewidth=1.0,
               alpha=0.6, zorder=5, label=f"Zersetzungsspannung")

    # --- Achsenstil: mit Ticks und aussagekräftigen Labels ---
    ax.set_xlabel("Spannung U  -->", fontsize=11)
    ax.set_ylabel("Stromstärke I -->", fontsize=11)
    ax.grid(True, alpha=0.3)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Hide tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Margins
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    ax.set_xlim(max(0, x_min - (x_max - x_min) * 0.05),
                x_max + (x_max - x_min) * 0.1)
    ax.set_ylim(max(0, y_min - (y_max - y_min) * 0.05),
                y_max + (y_max - y_min) * 0.15)

    # # Add arrows to axes
    # x_min, x_max = ax.get_xlim()
    # y_min, y_max = ax.get_ylim()
    # # Arrow for x-axis at the end
    # ax.annotate('', xy=(x_max, y_min), xytext=(x_max - 0.05*(x_max - x_min), y_min), arrowprops=dict(arrowstyle='->', color='k', lw=1))
    # # Arrow for y-axis at the end
    # ax.annotate('', xy=(x_min, y_max), xytext=(x_min, y_max - 0.05*(y_max - y_min)), arrowprops=dict(arrowstyle='->', color='k', lw=1))

    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.8)

    fig.tight_layout()
    out = os.path.join(base_dir, filename)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Gespeichert: {out}")
    return fig, ax


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Elek_UI.csv")
    df = pd.read_csv(file_path, sep=";", decimal=",")
    df.columns = ["U_V", "I_mA"]
    df["I_err"] = 0.5  # estimated error in mA
    plot_and_save(df, "Elektronische Kennlinie", "elek_kennlinie.png", base_dir=base_dir)
    plt.show()


if __name__ == "__main__":
    main()
