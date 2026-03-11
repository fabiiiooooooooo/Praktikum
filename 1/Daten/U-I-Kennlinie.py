import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_and_save(df, title, filename, marker="o", color=None, base_dir=None):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.errorbar(
        df["I_mA"], df["U_V"],
        xerr=df["I_err"], yerr=df["U_err"],
        fmt=marker, capsize=3, linestyle="-",
        linewidth=1.5, markersize=5, color=color,
    )
    ax.set_xlabel("Strom I [mA]")
    ax.set_ylabel("Spannung U [V]")
    ax.grid(True, alpha=0.3)

    # sinnvolle Skalierung (mit kleinem Rand)
    x_min, x_max = df["I_mA"].min(), df["I_mA"].max()
    y_min, y_max = df["U_V"].min(), df["U_V"].max()
    x_margin = (x_max - x_min) * 0.05
    y_margin = (y_max - y_min) * 0.05
    ax.set_xlim(max(0, x_min - x_margin), x_max + x_margin)
    ax.set_ylim(max(0, y_min - y_margin), y_max + y_margin)

    ax.set_title(title)
    fig.tight_layout()
    out = os.path.join(base_dir, filename)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig, ax


def main():
    # CSVs einlesen (Komma als Dezimaltrennzeichen)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_auf = os.path.join(base_dir, "U-I_aufwärts.csv")
    file_ab  = os.path.join(base_dir, "U-I_abwärts.csv")
    df_auf = pd.read_csv(file_auf, sep=";", decimal=",")
    df_ab  = pd.read_csv(file_ab, sep=";", decimal=",")

    # Spalten umbenennen (I = Strom mA, U = Spannung V)
    df_auf.columns = ["I_mA", "U_V", "R_Ohm"]
    df_ab.columns  = ["I_mA", "U_V", "R_Ohm"]

    # assign (constant) measurement uncertainties
    current_error = 0.5   # mA, geschätzt
    voltage_error = 0.005 # V, geschätzt
    for df in (df_auf, df_ab):
        df["I_err"] = current_error
        df["U_err"] = voltage_error

    # einzeln speichern
    plot_and_save(df_auf, "Aufwärts (Leerlauf → Last)", "kennlinie_aufwaerts.png", marker="o", color="blue", base_dir=base_dir)
    plot_and_save(df_ab,  "Abwärts (Last → Kurzschluss)", "kennlinie_abwaerts.png", marker="s", color="red", base_dir=base_dir)

    plt.show()


if __name__ == "__main__":
    main()
