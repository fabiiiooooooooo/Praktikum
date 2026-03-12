import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_and_save(df, title, filename, marker="o", color=None, base_dir=None, show_resistance=False, swap_axes=False):
    fig, ax = plt.subplots(figsize=(6, 5))
    # pick data depending on orientation
    if swap_axes:
        x = df["U_V"]
        y = df["I_mA"]
        
        xerr = None
        yerr = df.get("I_err", None)
        xlabel = "Spannung U [V]"
        ylabel = "Stromstärke I [mA]"
    else:
        x = df["I_mA"]
        y = df["U_V"]
        xerr = df.get("I_err", None)
        yerr = df.get("U_err", None)
        xlabel = "Stromstärke I [mA]"
        ylabel = "Spannung U [V]"

    ax.errorbar(
        x, y,
        xerr=xerr, yerr=yerr,
        fmt=marker, capsize=3, linestyle="-",
        linewidth=1.5, markersize=5, color=color,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    # was resistance requested?
    if show_resistance and "R_Ohm" in df.columns:
        ax2 = ax.twinx()
        if swap_axes:
            ax2.plot(df["U_V"], df["R_Ohm"], "r--", alpha=0.7)
        else:
            ax2.plot(df["I_mA"], df["R_Ohm"], "r--", alpha=0.7)
        ax2.set_ylabel("Widerstand R [Ω]", color="r")
        r_min, r_max = df["R_Ohm"].min(), df["R_Ohm"].max()
        r_margin = (r_max - r_min) * 0.05
        ax2.set_ylim(max(0, r_min - r_margin), r_max + r_margin)

    # scaling
    if swap_axes:
        x_min, x_max = df["U_V"].min(), df["U_V"].max()
        y_min, y_max = df["I_mA"].min(), df["I_mA"].max()
    else:
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
    

    # einzeln speichern (I‑U)
    plot_and_save(df_auf, "", "I-Ukennlinie_aufwaerts.png", marker="o", color="blue", base_dir=base_dir)
    plot_and_save(df_ab,  "", "I-Ukennlinie_abwaerts.png", marker="s", color="red", base_dir=base_dir)

    # zusätzlich U‑I Kennlinien (getauschte Achsen)
    plot_and_save(
        df_auf,
        "",
        "U-I-kennlinie_aufwaerts.png",
        marker="o",
        color="blue",
        base_dir=base_dir,
        swap_axes=True,
    )
    plot_and_save(
        df_ab,
        "",
        "U-I-kennlinie_abwaerts.png",
        marker="s",
        color="red",
        base_dir=base_dir,
        swap_axes=True,
    )

    plt.show()


if __name__ == "__main__":
    main()
