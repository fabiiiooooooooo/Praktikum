import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def extract_value(df_raw, r_label, col_name):
    return pd.to_numeric(df_raw[col_name], errors='coerce').max()

def main():
    dir_path = Path(__file__).resolve().parent
    csv_path = dir_path / 'spektralEmpf.csv'

    # ===========================
    # 1. Daten roh laden
    # ===========================
    df_raw = pd.read_csv(csv_path, sep=';', decimal=',')
    
    # ===========================
    # 3. Daten für Plots bereinigen
    # ===========================
    df = df_raw.copy()
    
    df1 = df.copy()
    df1['lambda'] = pd.to_numeric(df1['lambda'], errors='coerce')
    df1['I [uA]'] = pd.to_numeric(df1['I [uA]'], errors='coerce')
    
    df2 = df_raw.copy()
    df2['lambda'] = pd.to_numeric(df2['lambda'], errors='coerce')
    df2['I_2'] = pd.to_numeric(df2['I_2'], errors='coerce')

    # ===========================
    # FEHLERWERTE DEFINIEREN 
    # ===========================
    # Das können feste Zahlen sein oder Spalten aus deiner CSV, z.B. df1['Fehler_I']
    y_err_1 = 0.5     # Angenommener Fehler des Stroms 1 in uA
    y_err_2 = 0.5    # Angenommener Fehler des Stroms 2 in uA

    # ===========================
    # 4. Plot Messung 1
    # ===========================
    fig1, ax1 = plt.subplots(figsize=(7, 5))

    # errorbar statt plot verwenden
    ax1.errorbar(df1['lambda'], df1['I [uA]'], 
                yerr=y_err_1, 
                 fmt='-o',            # Linie '-' mit Kreispunkten 'o'
                 color='black', 
                 ecolor='gray',       # Farbe der Fehlerbalken
                 capsize=3,           # Querstriche an den Fehlerbalken
                 markersize=5, 
                 linewidth=1.5, 
                 zorder=3)

    u_min_1 = df1['lambda'].min()
    u_max_1 = df1['lambda'].max()
    i_max_1 = df1['I [uA]'].max()

    ax1.set_xlim(u_min_1, u_max_1 * 1.05)
    ax1.set_ylim(0, (i_max_1 + y_err_1) * 1.05) # Limit leicht erhöht, damit der Fehlerbalken passt

    ax1.set_xlabel('Wellenlänge [nm]')
    ax1.set_ylabel('Strom [uA]')
    ax1.grid(True, alpha=0.3)

    fig1.tight_layout()
    fig1.savefig(dir_path / 'SpektralEmpf_Messung1.png', format='png',
                 bbox_inches='tight', dpi=600)

    # ===========================
    # 5. Plot 2.Messung
    # ===========================
    fig2, ax2 = plt.subplots(figsize=(7, 5))

    ax2.errorbar(df2['lambda'], df2['I_2'], 
                yerr=y_err_2,
                 fmt='-o', color='red', ecolor='salmon', 
                 capsize=3, markersize=5, linewidth=1.5, zorder=3)
    
    u_min_2 = df2['lambda'].min()
    u_max_2 = df2['lambda'].max()
    i_max_2 = df2['I_2'].max()

    ax2.set_xlim(u_min_2, u_max_2 * 1.05)
    ax2.set_ylim(0, (i_max_2 + y_err_2) * 1.05)
    ax2.set_xlabel('Wellenlänge [nm]')
    ax2.set_ylabel('Strom [uA]')
    ax2.grid(True, alpha=0.3)

    fig2.tight_layout()
    fig2.savefig(dir_path / 'SpektralEmpf_Messung2.png', format='png',
                 bbox_inches='tight', dpi=600)

    # ===========================
    # 6. Plot 1 und 2 im Vergleich
    # ===========================
    fig3, ax3 = plt.subplots(figsize=(7, 5))   
    
    ax3.errorbar(df1['lambda'], df1['I [uA]'], yerr=y_err_1, 
                 fmt='-o', color='black', ecolor='gray', capsize=3, markersize=4, 
                 label='Messung 1', zorder=3)
    ax3.errorbar(df2['lambda'], df2['I_2'], xerr=None, yerr=y_err_2, 
                 fmt='-o', color='red', ecolor='salmon', capsize=3, markersize=4, 
                 label='Messung 2', zorder=3)
    
    ax3.set_xlim(min(u_min_1, u_min_2), max(u_max_1, u_max_2) * 1.05)
    ax3.set_ylim(0, max(i_max_1 + y_err_1, i_max_2 + y_err_2) * 1.05)
    ax3.set_xlabel('Wellenlänge [nm]')
    ax3.set_ylabel('Strom [uA]')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=9, framealpha=0.8)  
    
    fig3.tight_layout()
    fig3.savefig(dir_path / 'SpektralEmpf_Vergleich.png', format='png',
                 bbox_inches='tight', dpi=600)
    
    print("Plots generiert")

if __name__ == '__main__':
    main()
