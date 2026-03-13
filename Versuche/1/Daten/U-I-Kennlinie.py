import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Bereichsgrenzen aus Datenanalyse bestimmt
BEREICH_A_BIS = 10.0    # mA
BEREICH_B_BIS = 160.0   # mA


def find_region_boundaries(I, U):
    """Bestimmt Bereichsgrenzen automatisch aus Steigungsanalyse."""
    idx = np.argsort(I)
    I_s, U_s = I[idx], U[idx]
    dU = np.diff(U_s)
    dI = np.diff(I_s)
    slope = dU / dI
    I_mid = (I_s[:-1] + I_s[1:]) / 2

    # Bereich A/B: wo Steigung erstmals annähernd konstant wird
    slope_norm = np.abs(slope)
    median_slope = np.median(slope_norm)
    # Erster Punkt wo Steigung unter 2x Median fällt
    for i, (s, im) in enumerate(zip(slope_norm, I_mid)):
        if s < 2 * median_slope:
            grenze_ab = im
            break
    else:
        grenze_ab = BEREICH_A_BIS

    # Bereich B/C: letzter Punkt im linearen Bereich (R² Methode)
    mask_lin = I_s >= grenze_ab
    I_lin, U_lin = I_s[mask_lin], U_s[mask_lin]
    best_r2, best_end = 0, I_lin[-1]
    for j in range(3, len(I_lin)):
        coeffs = np.polyfit(I_lin[:j], U_lin[:j], 1)
        res = U_lin[:j] - np.polyval(coeffs, I_lin[:j])
        ss_res = np.sum(res**2)
        ss_tot = np.sum((U_lin[:j] - U_lin[:j].mean())**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        if r2 > 0.998:
            best_end = I_lin[j - 1]
        else:
            break

    return grenze_ab, best_end


def add_fuel_cell_regions(ax, x_min, x_max, y_min, y_max, grenze_ab, grenze_bc):
    """Zeichnet Bereiche A, B, C mit gestrichelten Linien und Labels.

    Die Grenzen werden auf den sichtbaren Bereich (
    x_min..x_max) begrenzt, damit die Linien immer innerhalb der Achse liegen.
    """
    # Clamp boundaries to visible axis range
    b_ab = min(max(grenze_ab, x_min), x_max)
    b_bc = min(max(grenze_bc, x_min), x_max)

    for b in [b_ab, b_bc]:
        if x_min <= b <= x_max:
            ax.axvline(x=b, color="black", linestyle="--", linewidth=1.0, alpha=0.6)

    # Only show regions that are within the visible range
    regions = []
    labels = []

    if x_min < b_ab:
        regions.append((x_min, b_ab)); labels.append("A")
    if b_ab < b_bc:
        regions.append((b_ab, b_bc)); labels.append("B")
    if b_bc < x_max:
        regions.append((b_bc, x_max)); labels.append("C")

    y_label = y_min + (y_max - y_min) * 0.25
    for (x0, x1), label in zip(regions, labels):
        ax.text((x0 + x1) / 2, y_label, label,
                fontsize=14, ha="center", va="center",
                color="black", alpha=0.6)


def plot_and_save(df, title, filename, marker="o", color=None, base_dir=None,
                  show_resistance=False, swap_axes=False, add_regions=False,
                  grenze_ab=None, grenze_bc=None):
    fig, ax = plt.subplots(figsize=(6, 5))

    if swap_axes:
        x = df["U_V"];  y = df["I_mA"]
        xerr = None;    yerr = df.get("I_err", None)
        xlabel = "Spannung U [V]";  ylabel = "Stromstärke I [mA]"
    else:
        x = df["I_mA"]; y = df["U_V"]
        xerr = df.get("I_err", None); yerr = df.get("U_err", None)
        xlabel = "Stromstärke I [mA]"; ylabel = "Spannung U [V]"

    ax.errorbar(x, y, xerr=xerr, yerr=yerr,
                fmt=marker, capsize=3, linestyle="-",
                linewidth=1.5, markersize=5, color=color, label="Messwerte")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    if show_resistance and "R_Ohm" in df.columns:
        ax2 = ax.twinx()
        x_r = df["U_V"] if swap_axes else df["I_mA"]
        ax2.plot(x_r, df["R_Ohm"], "r--", alpha=0.7, label="Widerstand")
        ax2.set_ylabel("Widerstand R [Ω]", color="r")
        r_min, r_max = df["R_Ohm"].min(), df["R_Ohm"].max()
        ax2.set_ylim(max(0, r_min - (r_max - r_min) * 0.05),
                     r_max + (r_max - r_min) * 0.05)

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

    if add_regions and not swap_axes and grenze_ab and grenze_bc:
        add_fuel_cell_regions(ax, x_min, x_max, y_min, y_max, grenze_ab, grenze_bc)

    ax.set_title(title)
    fig.tight_layout()
    out = os.path.join(base_dir, filename)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Gespeichert: {out}")
    return fig, ax


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df_auf = pd.read_csv(os.path.join(base_dir, "U-I_aufwärts.csv"), sep=";", decimal=",")
    df_ab  = pd.read_csv(os.path.join(base_dir, "U-I_abwärts.csv"),  sep=";", decimal=",")

    df_auf.columns = ["I_mA", "U_V", "R_Ohm"]
    df_ab.columns  = ["I_mA", "U_V", "R_Ohm"]

    for df in (df_auf, df_ab):
        df["I_err"] = 0.5
        df["U_err"] = 0.005
        df.sort_values("I_mA", inplace=True)

    # Bereichsgrenzen aus kombinierten Daten bestimmen
    I_all = np.concatenate([df_auf["I_mA"].values, df_ab["I_mA"].values])
    U_all = np.concatenate([df_auf["U_V"].values,  df_ab["U_V"].values])
    grenze_ab, grenze_bc = find_region_boundaries(I_all, U_all)
    print(f"Bereichsgrenzen: A/B = {grenze_ab:.1f} mA,  B/C = {grenze_bc:.1f} mA")

    # I-U Kennlinien einzeln MIT Bereichen
    plot_and_save(df_auf, "", "I-Ukennlinie_aufwaerts.png",
                  marker="o", color="blue", base_dir=base_dir,
                  add_regions=True, grenze_ab=grenze_ab, grenze_bc=grenze_bc)
    plot_and_save(df_ab, "", "I-Ukennlinie_abwaerts.png",
                  marker="s", color="red", base_dir=base_dir,
                  add_regions=True, grenze_ab=grenze_ab, grenze_bc=grenze_bc)

    # Kombinierter Plot (beide Kurven in einem Graphen)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.errorbar(df_auf["I_mA"], df_auf["U_V"], yerr=df_auf["U_err"],
                fmt="o-", capsize=3, linewidth=1.5, markersize=5,
                color="blue", label="Spannungsreihe aufwärts")
    ax.errorbar(df_ab["I_mA"],  df_ab["U_V"],  yerr=df_ab["U_err"],
                fmt="s-", capsize=3, linewidth=1.5, markersize=5,
                color="red",  label="Spannungsreihe abwärts")
    x_min = 0
    x_max = max(df_auf["I_mA"].max(), df_ab["I_mA"].max())
    y_min = min(df_auf["U_V"].min(), df_ab["U_V"].min())
    y_max = max(df_auf["U_V"].max(), df_ab["U_V"].max())
    ax.set_xlim(x_min, x_max * 1.05)
    ax.set_ylim(y_min * 0.98, y_max * 1.02)
    add_fuel_cell_regions(ax, x_min, x_max, y_min, y_max, grenze_ab, grenze_bc)
    ax.set_xlabel("Stromstärke I [mA]")
    ax.set_ylabel("Spannung U [V]")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(base_dir, "I-Ukennlinie_kombiniert.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"Gespeichert: {out}")

    # U-I Kennlinien (swap_axes)
    plot_and_save(df_auf, "", "U-I-kennlinie_aufwaerts.png",
                  marker="o", color="blue", base_dir=base_dir, swap_axes=True)
    plot_and_save(df_ab,  "",  "U-I-kennlinie_abwaerts.png",
                  marker="s", color="red",  base_dir=base_dir, swap_axes=True)

    plt.show()


if __name__ == "__main__":
    main()
