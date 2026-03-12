import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_and_save(df, title, filename, marker="o", color=None, base_dir=None, show_resistance=False):
    fig, ax = plt.subplots(figsize=(6, 5))
  
    x = df["U_V"]
    y = df["I_mA"]
        
    xerr = None
    yerr = df.get("I_err", None)
    xlabel = "Spannung U [V]"
    ylabel = "Stromstärke I [mA]"


    ax.errorbar(
        x, y,
        xerr=xerr, yerr=yerr,
        fmt=marker, capsize=3, linestyle="-",
        linewidth=1.5, markersize=5, color=color,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    # Hervorhebung der Bereiche
    # Zersetzungsspannung: ca. 2.8 V
    ax.axvline(x=2.8, color='red', linestyle='--', linewidth=2, label='Zersetzungsspannung (~2.8 V)')
    
    # Linearer Bereich: 2.8 V bis 3.2 V
    ax.axvspan(2.8, 3.2, alpha=0.2, color='green', label='Linearer Anstieg')
    
    # Sättigungsbereich: ab 3.2 V
    ax.axvspan(3.2, df["U_V"].max(), alpha=0.2, color='orange', label='Sättigung')
    
    ax.legend()

    # scaling
    x_min, x_max = df["U_V"].min(), df["U_V"].max()
    y_min, y_max = df["I_mA"].min(), df["I_mA"].max()
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
    file = os.path.join(base_dir, "Elek_UI.csv")
    df = pd.read_csv(file, sep=";", decimal=",")
    
    # Spalten umbenennen und Einheiten anpassen
    df.columns = ["U_V", "I_mA"]

    # assign (constant) measurement uncertainties
    current_error = 0.5   # mA, geschätzt
    voltage_error = 0.005 # V, geschätzt
    df["I_err"] = current_error
    df["U_err"] = voltage_error

    # Sortiere nach Spannung aufsteigend für korrekte Darstellung
    df = df.sort_values("U_V")

    plot_and_save(df,"", "U-I_elek.png", marker="o", color="blue", base_dir=base_dir)

    plt.show()


if __name__ == "__main__":
    main()
