import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.interpolate import PchipInterpolator

# Naturkonstanten für Plancksches Strahlungsgesetz
h = 6.626e-34  # Plancksches Wirkungsquantum [J s]
c = 3.0e8      # Lichtgeschwindigkeit [m/s]
k_B = 1.38e-23 # Boltzmann-Konstante [J/K]

def planck_law(lam_nm, T=3200):
    lam_m = lam_nm * 1e-9
    numerator = 1.0 / (lam_m**5)
    denominator = np.exp((h * c) / (lam_m * k_B * T)) - 1.0
    return numerator / denominator

def main():
    dir_path = Path(__file__).resolve().parent
    csv_path = dir_path / 'spektralEmpf.csv'

    df = pd.read_csv(csv_path, sep=';', decimal=',')
    df = df[df['lambda'] != 'Dunkelstrom'].copy()
    
    df['lambda'] = pd.to_numeric(df['lambda'])
    df['I [uA]'] = pd.to_numeric(df['I [uA]'])
    df['I_2'] = pd.to_numeric(df['I_2'].astype(str).str.replace(',', '.'))
    
    df['u_lambda'] = planck_law(df['lambda'], T=3200)

    # Tatsächliche Empfindlichkeit berechnen
    df['E1_roh'] = df['I [uA]'] / df['u_lambda']
    df['E2_roh'] = df['I_2'] / df['u_lambda']

    # --- FILTER FÜR NORMALE AUSWERTUNG ---
    # Wir ignorieren für die Normierung und Analyse das Rauschen unterhalb von 450 nm
    df_plot = df[df['lambda'] >= 450].copy()

    # Normierung auf das Maximum (das nun realistisch im roten/IR Bereich liegt)
    df_plot['Empfindlichkeit_1_norm'] = df_plot['E1_roh'] / df_plot['E1_roh'].max()
    df_plot['Empfindlichkeit_2_norm'] = df_plot['E2_roh'] / df_plot['E2_roh'].max()

    # Werte zur Kontrolle ausgeben
    print("=== BERECHNETE WERTE (ab 450 nm) ===")
    print(df_plot[['lambda', 'I [uA]', 'u_lambda', 'Empfindlichkeit_1_norm']].to_string(index=False))
    print("===================================\n")

    # Plot generieren
    l_smooth = np.linspace(df_plot['lambda'].min(), df_plot['lambda'].max(), 300)
    
    fit_1 = PchipInterpolator(df_plot['lambda'], df_plot['Empfindlichkeit_1_norm'])
    fit_2 = PchipInterpolator(df_plot['lambda'], df_plot['Empfindlichkeit_2_norm'])
    
    empf_smooth_1 = fit_1(l_smooth)
    empf_smooth_2 = fit_2(l_smooth)

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(l_smooth, empf_smooth_1, color='black', linewidth=1.5, zorder=2)
    ax.plot(l_smooth, empf_smooth_2, color='red', linewidth=1.5, zorder=2)

    ax.plot(df_plot['lambda'], df_plot['Empfindlichkeit_1_norm'], 'o', color='black', 
            markersize=5, label='Messung 1', zorder=3)
    ax.plot(df_plot['lambda'], df_plot['Empfindlichkeit_2_norm'], 'o', color='red', 
            markersize=5, label='Messung 2', zorder=3)

    ax.set_xlim(400, 950)
    ax.set_ylim(0, 1.1)
    
    ax.set_xlabel('Wellenlänge [nm]')
    ax.set_ylabel('Tatsächliche Spektralempfindlichkeit (normiert)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.8)

    fig.tight_layout()
    fig.savefig(dir_path / 'tatsaechliche_Spektralempfindlichkeit.png', format='png', bbox_inches='tight', dpi=600)
    print("Plot gespeichert.")

if __name__ == '__main__':
    main()
