import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

def main():
    dir_path = Path(__file__).resolve().parent
    csv_path = dir_path / 'messwerte_solarzelle_auswertung.csv'
    
    # Daten laden
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    df_100 = df[df['Beleuchtung'] == '100%'].dropna(subset=['U [V]', 'I [mA]']).sort_values('U [V]').reset_index(drop=True)
    df_50  = df[df['Beleuchtung'] == '50%'].dropna(subset=['U [V]', 'I [mA]']).sort_values('U [V]').reset_index(drop=True)

    # 100%-Artefakte entfernen
    df_100 = df_100[~df_100['U [V]'].isin([1.97, 1.917])].reset_index(drop=True)

    # ===========================
    # FEHLERBERECHNUNG (Größtfehler)
    # ===========================
    u_err = 0.001  # V
    i_err = 0.1  # mA
    
    # Leistung P = U * I (in mW, da V * mA = mW)
    df_50['P_err [mW]'] = df_50['I [mA]'].abs() * u_err + df_50['U [V]'].abs() * i_err
    df_100['P_err [mW]'] = df_100['I [mA]'].abs() * u_err + df_100['U [V]'].abs() * i_err

    # Für die Interpolation dürfen keine doppelten X-Werte (Spannung) existieren
    df_50 = df_50.drop_duplicates(subset=['U [V]']).reset_index(drop=True)
    df_100 = df_100.drop_duplicates(subset=['U [V]']).reset_index(drop=True)

    # erste Punkte für den Plot entfernen
    df_50_plot  = df_50.iloc[1:].reset_index(drop=True)
    df_100_plot = df_100.iloc[2:].reset_index(drop=True)

    # ===========================
    # GLÄTTUNGS-FITS (PCHIP) ERSTELLEN
    # ===========================
    # 50% IV-Kurve
    u_smooth_50 = np.linspace(df_50_plot['U [V]'].min(), df_50_plot['U [V]'].max(), 300)
    fit_50 = PchipInterpolator(df_50_plot['U [V]'], df_50_plot['I [mA]'])
    i_smooth_50 = fit_50(u_smooth_50)

    # 100% IV-Kurve
    u_smooth_100 = np.linspace(df_100_plot['U [V]'].min(), df_100_plot['U [V]'].max(), 300)
    fit_100 = PchipInterpolator(df_100_plot['U [V]'], df_100_plot['I [mA]'])
    i_smooth_100 = fit_100(u_smooth_100)

    # 50% Leistungskurve
    u_p_smooth_50 = np.linspace(df_50['U [V]'].min(), df_50['U [V]'].max(), 300)
    fit_p_50 = PchipInterpolator(df_50['U [V]'], df_50['Leistung [mW]'])
    p_smooth_50 = fit_p_50(u_p_smooth_50)

    # 100% Leistungskurve
    u_p_smooth_100 = np.linspace(df_100['U [V]'].min(), df_100['U [V]'].max(), 300)
    fit_p_100 = PchipInterpolator(df_100['U [V]'], df_100['Leistung [mW]'])
    p_smooth_100 = fit_p_100(u_p_smooth_100)


    # ===========================
    # 1) Plot 50%
    # ===========================
    u_oc_50 = df_50['U [V]'].max()
    i_sc_50 = df_50['I [mA]'].max()
    idx_mpp_50 = df_50['Leistung [mW]'].idxmax()
    u_mpp_50 = df_50.loc[idx_mpp_50, 'U [V]']
    i_mpp_50 = df_50.loc[idx_mpp_50, 'I [mA]']

    fig1, ax1 = plt.subplots(figsize=(7, 5))

    # Glatte Kurve plotten
    ax1.plot(u_smooth_50, i_smooth_50, color='black', linewidth=1.5, zorder=2)
    # Datenpunkte als alleinstehende Punkte mit Fehlerbalken (fmt='o')
    ax1.errorbar(df_50_plot['U [V]'], df_50_plot['I [mA]'], 
                 xerr=u_err, yerr=i_err, 
                 fmt='o', color='black', ecolor='gray', capsize=3, zorder=3)

    ax1.add_patch(plt.Rectangle((0, 0), u_oc_50, i_sc_50,
                                fill=False, edgecolor='gray', linestyle='--',
                                linewidth=1.2, zorder=2))
    ax1.add_patch(plt.Rectangle((0, 0), u_mpp_50, i_mpp_50,
                                fill=True, facecolor='lightgray', alpha=0.5,
                                edgecolor='black', linestyle='-', linewidth=1.0, zorder=1))

    u_min_50 = df_50_plot['U [V]'].min()
    u_max_50 = df_50_plot['U [V]'].max()
    i_max_50 = df_50_plot['I [mA]'].max()

    ax1.set_xlim(u_min_50, u_max_50 * 1.05)
    ax1.set_ylim(0, i_max_50 * 1.05)

    ax1.plot(u_min_50, i_sc_50, marker="X", markersize=10,
             markeredgecolor='black', markerfacecolor='white', markeredgewidth=2.0,
             linestyle='None', label='I_K', clip_on=False, zorder=5)
    ax1.plot(u_oc_50, 0, marker="X", markersize=10,
             markeredgecolor='red', markerfacecolor='white', markeredgewidth=1.0,
             linestyle='None', label='U_L', clip_on=False, zorder=5)
    ax1.plot(u_mpp_50, i_mpp_50, marker='D', markersize=10,
             markerfacecolor='white', markeredgecolor='black',
             markeredgewidth=2.0, linestyle='None', label='MPP', zorder=4)

    ax1.set_xlabel('Spannung [V]')
    ax1.set_ylabel('Strom [mA]')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower left')

    fig1.tight_layout()
    fig1.savefig(dir_path / 'kennlinie_IV_50.png', format='png', bbox_inches='tight', dpi=600)

    # ===========================
    # 2) Plot 100%
    # ===========================
    u_oc_100 = df_100['U [V]'].max()
    i_sc_100 = df_100['I [mA]'].max()
    idx_mpp_100 = df_100['Leistung [mW]'].idxmax()
    u_mpp_100 = df_100.loc[idx_mpp_100, 'U [V]']
    i_mpp_100 = df_100.loc[idx_mpp_100, 'I [mA]']

    u_min_100 = df_100_plot['U [V]'].min()
    u_max_100 = df_100_plot['U [V]'].max()
    i_max_100 = max(i_sc_100, df_100_plot['I [mA]'].max())
    
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    
    ax2.plot(u_smooth_100, i_smooth_100, color='red', linewidth=1.5, zorder=2)
    ax2.errorbar(df_100_plot['U [V]'], df_100_plot['I [mA]'], 
                 xerr=u_err, yerr=i_err, 
                 fmt='o', color='red', ecolor='salmon', capsize=3, zorder=3)

    ax2.add_patch(plt.Rectangle((0, 0), u_oc_100, i_sc_100,
                                fill=False, edgecolor='gray', linestyle='--',
                                linewidth=1.2, zorder=2))
    ax2.add_patch(plt.Rectangle((0, 0), u_mpp_100, i_mpp_100,
                                fill=True, facecolor='mistyrose', alpha=0.5,
                                edgecolor='red', linestyle='-', linewidth=1.0, zorder=1))

    ax2.plot(u_min_100, i_sc_100, marker="X", markersize=10,
             markeredgecolor='red', markerfacecolor='white', markeredgewidth=2.0,
             linestyle='None', label='I_K', clip_on=False, zorder=4)
    ax2.plot(u_oc_100, 0, marker="X", markersize=10,
             markeredgecolor='black', markerfacecolor='white', markeredgewidth=2.0,
             linestyle='None', label='U_L', clip_on=False, zorder=4)
    ax2.plot(u_mpp_100, i_mpp_100, marker='D', markersize=10,
             markerfacecolor='white', markeredgecolor='red',
             markeredgewidth=2.0, linestyle='None', label='MPP', zorder=4)

    ax2.set_xlim(u_min_100, u_max_100 * 1.05)
    ax2.set_ylim(0, i_max_100 * 1.05)
    ax2.set_xlabel('Spannung [V]')
    ax2.set_ylabel('Strom [mA]')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower left')

    fig2.tight_layout()
    fig2.savefig(dir_path / 'kennlinie_IV_100.png', format='png', bbox_inches='tight', dpi=600)

    # ==========================================
    # 3) Leistungsplots P(U) mit MPP-Markern
    # ==========================================
    p_mpp_50 = df_50.loc[idx_mpp_50, 'Leistung [mW]']
    p_err_mpp_50 = df_50.loc[idx_mpp_50, 'P_err [mW]']
    
    p_mpp_100 = df_100.loc[idx_mpp_100, 'Leistung [mW]']
    p_err_mpp_100 = df_100.loc[idx_mpp_100, 'P_err [mW]']

    # ---------- 3a) Leistung 50 % ----------
    fig3, ax3 = plt.subplots(figsize=(7, 5))

    ax3.plot(u_p_smooth_50, p_smooth_50, color='black', linewidth=1.5, zorder=2)
    ax3.errorbar(df_50['U [V]'], df_50['Leistung [mW]'],
                 xerr=u_err, yerr=df_50['P_err [mW]'],
                 fmt='o', color='black', ecolor='gray', capsize=3, zorder=3)

    ax3.errorbar(u_mpp_50, p_mpp_50,
                 xerr=u_err, yerr=p_err_mpp_50,
                 marker='D', markersize=10, markerfacecolor='white', markeredgecolor='black',
                 markeredgewidth=2.0, linestyle='None', label='MPP', zorder=4)

    ax3.set_xlabel('Spannung [V]')
    ax3.set_ylabel('Leistung [mW]')
    ax3.grid(True, alpha=0.3)

    u_min_50_p = df_50['U [V]'].min()
    u_max_50_p = df_50['U [V]'].max()
    p_max_50 = df_50['Leistung [mW]'].max()
    ax3.set_xlim(u_min_50_p, u_max_50_p * 1.05)
    ax3.set_ylim(0, p_max_50 * 1.05)

    ax3.legend(loc='upper right')
    fig3.tight_layout()
    fig3.savefig(dir_path / 'leistung_50.png', format='png', bbox_inches='tight', dpi=600)
    plt.close(fig3)

    # ---------- 3b) Leistung 100 % ----------
    fig4, ax4 = plt.subplots(figsize=(7, 5))

    ax4.plot(u_p_smooth_100, p_smooth_100, color='red', linewidth=1.5, zorder=2)
    ax4.errorbar(df_100['U [V]'], df_100['Leistung [mW]'],
                 xerr=u_err, yerr=df_100['P_err [mW]'],
                 fmt='o', color='red', ecolor='salmon', capsize=3, zorder=3)

    ax4.errorbar(u_mpp_100, p_mpp_100,
                 xerr=u_err, yerr=p_err_mpp_100,
                 marker='D', markersize=10, markerfacecolor='white', markeredgecolor='red',
                 markeredgewidth=2.0, linestyle='None', label='MPP', zorder=4)

    ax4.set_xlabel('Spannung [V]')
    ax4.set_ylabel('Leistung [mW]')
    ax4.grid(True, alpha=0.3)

    u_min_100_p = df_100['U [V]'].min()
    u_max_100_p = df_100['U [V]'].max()
    p_max_100 = df_100['Leistung [mW]'].max()
    ax4.set_xlim(u_min_100_p, u_max_100_p * 1.05)
    ax4.set_ylim(0, p_max_100 * 1.05)

    ax4.legend(loc='upper right')
    fig4.tight_layout()
    fig4.savefig(dir_path / 'leistung_100.png', format='png', bbox_inches='tight', dpi=600)
    plt.close(fig4)

    # ---------- 3c) Gemeinsamer Leistungsplot ----------
    fig5, ax5 = plt.subplots(figsize=(7, 5))

    # Glatte Linien
    ax5.plot(u_p_smooth_50, p_smooth_50, color='black', linewidth=1.5, zorder=2)
    ax5.plot(u_p_smooth_100, p_smooth_100, color='red', linewidth=1.5, zorder=2)

    # Datenpunkte
    ax5.errorbar(df_50['U [V]'], df_50['Leistung [mW]'],
                 xerr=u_err, yerr=df_50['P_err [mW]'], 
                 fmt='o', color='black', ecolor='gray', capsize=3, label='50 %', zorder=3)
    
    ax5.errorbar(df_100['U [V]'], df_100['Leistung [mW]'],
                 xerr=u_err, yerr=df_100['P_err [mW]'], 
                 fmt='o', color='red', ecolor='salmon', capsize=3, label='100 %', zorder=3)

    # MPP-Marker
    ax5.errorbar(u_mpp_50, p_mpp_50,
                 xerr=u_err, yerr=p_err_mpp_50,
                 marker='D', markersize=9, markerfacecolor='white', markeredgecolor='black',
                 markeredgewidth=2.0, linestyle='None', label='MPP 50 %', zorder=4)
                 
    ax5.errorbar(u_mpp_100, p_mpp_100,
                 xerr=u_err, yerr=p_err_mpp_100,
                 marker='D', markersize=9, markerfacecolor='white', markeredgecolor='red',
                 markeredgewidth=2.0, linestyle='None', label='MPP 100 %', zorder=4)

    ax5.set_xlabel('Spannung [V]')
    ax5.set_ylabel('Leistung [mW]')
    ax5.grid(True, alpha=0.3)

    u_min_all = min(df_50['U [V]'].min(), df_100['U [V]'].min())
    u_max_all = max(df_50['U [V]'].max(), df_100['U [V]'].max())
    p_max_all = max(p_max_50, p_max_100)
    ax5.set_xlim(u_min_all, u_max_all * 1.05)
    ax5.set_ylim(0, p_max_all * 1.05)

    ax5.legend(loc='upper left')
    fig5.tight_layout()
    fig5.savefig(dir_path / 'leistung_50_100.png', format='png', bbox_inches='tight', dpi=600)
    plt.close(fig5)

    # ==========================================
    # Textausgabe speichern
    # ==========================================
    results_path = dir_path / 'kennwerte_solarzelle.txt'

    text = (
        f"50 %: U_oc = {u_oc_50:.3f} V, I_sc = {i_sc_50:.3f} mA, "
        f"U_mpp = {u_mpp_50:.3f} V, I_mpp = {i_mpp_50:.3f} mA, "
        f"P_mpp = {p_mpp_50:.3f} +/- {p_err_mpp_50:.3f} mW\n"
        f"100 %: U_oc = {u_oc_100:.3f} V, I_sc = {i_sc_100:.3f} mA, "
        f"U_mpp = {u_mpp_100:.3f} V, I_mpp = {i_mpp_100:.3f} mA, "
        f"P_mpp = {p_mpp_100:.3f} +/- {p_err_mpp_100:.3f} mW\n"
    )

    with open(results_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("Plots generiert")
    print(text.strip())

if __name__ == '__main__':
    main()
