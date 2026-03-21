import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    dir_path = Path(__file__).resolve().parent
    csv_path = dir_path / 'messwerte_solarzelle_auswertung.csv'
    
    # Daten laden
    df = pd.read_csv(csv_path, sep=';', decimal=',')
    df_100 = df[df['Beleuchtung'] == '100%'].dropna(subset=['U [V]', 'I [mA]']).sort_values('U [V]').reset_index(drop=True)
    df_50  = df[df['Beleuchtung'] == '50%'].dropna(subset=['U [V]', 'I [mA]']).sort_values('U [V]').reset_index(drop=True)

    # 100%-Artefakte entfernen
    df_100 = df_100[~df_100['U [V]'].isin([1.97, 1.917])].reset_index(drop=True)

    # erste Punkte für den Plot entfernen
    df_50_plot  = df_50.iloc[1:].reset_index(drop=True)
    df_100_plot = df_100.iloc[2:].reset_index(drop=True)

    # ===========================
    # 1) Plot 50%
    # ===========================
    u_oc_50 = df_50['U [V]'].max()
    i_sc_50 = df_50['I [mA]'].max()
    idx_mpp_50 = df_50['Leistung [mW]'].idxmax()
    u_mpp_50 = df_50.loc[idx_mpp_50, 'U [V]']
    i_mpp_50 = df_50.loc[idx_mpp_50, 'I [mA]']

    fig1, ax1 = plt.subplots(figsize=(7, 5))
    I_50_uA = df_50_plot['I [mA]'] * 1000.0
    i_sc_50_uA = i_sc_50 * 1000.0
    i_mpp_50_uA = i_mpp_50 * 1000.0

    ax1.plot(df_50_plot['U [V]'], df_50_plot['I [mA]'], color='black', linewidth=2.0, zorder=3)

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
    fig1.savefig(dir_path / 'kennlinie_IV_50.png', format='png',
                 bbox_inches='tight', dpi=600)

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
    
    ax2.plot(df_100_plot['U [V]'], df_100_plot['I [mA]'],
             color='red', linewidth=2.0, zorder=3)

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
    fig2.savefig(dir_path / 'kennlinie_IV_100.png', format='png',
                 bbox_inches='tight', dpi=600)

    # ==========================================
    # 3) Leistungsplots P(U)
    # ==========================================

       # ==========================================
    # 3) Leistungsplots P(U) mit MPP-Markern
    # ==========================================

    # 50 %: MPP schon oben bestimmt (u_mpp_50, p_mpp_50 aus df_50)
    p_mpp_50 = df_50.loc[idx_mpp_50, 'Leistung [mW]']

    # 100 %: MPP schon oben bestimmt (u_mpp_100, p_mpp_100 aus df_100)
    p_mpp_100 = df_100.loc[idx_mpp_100, 'Leistung [mW]']

    # ---------- 3a) Leistung 50 % ----------
    fig3, ax3 = plt.subplots(figsize=(7, 5))

    ax3.plot(df_50['U [V]'], df_50['Leistung [mW]'],
             color='black', linewidth=2.0)

    # MPP markieren
    ax3.plot(u_mpp_50, p_mpp_50,
             marker='D', markersize=10,
             markerfacecolor='white', markeredgecolor='black',
             markeredgewidth=2.0, linestyle='None', label='MPP')

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
    fig3.savefig(dir_path / 'leistung_50.png', format='png',
                 bbox_inches='tight', dpi=600)
    plt.close(fig3)

    # ---------- 3b) Leistung 100 % ----------
    fig4, ax4 = plt.subplots(figsize=(7, 5))

    ax4.plot(df_100['U [V]'], df_100['Leistung [mW]'],
             color='red', linewidth=2.0)

    ax4.plot(u_mpp_100, p_mpp_100,
             marker='D', markersize=10,
             markerfacecolor='white', markeredgecolor='red',
             markeredgewidth=2.0, linestyle='None', label='MPP')

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
    fig4.savefig(dir_path / 'leistung_100.png', format='png',
                 bbox_inches='tight', dpi=600)
    plt.close(fig4)

    # ---------- 3c) Gemeinsamer Leistungsplot ----------
    fig5, ax5 = plt.subplots(figsize=(7, 5))

    ax5.plot(df_50['U [V]'], df_50['Leistung [mW]'],
             color='black', linewidth=2.0, label='50 %')
    ax5.plot(df_100['U [V]'], df_100['Leistung [mW]'],
             color='red', linewidth=2.0, label='100 %')

    # MPPs markieren
    ax5.plot(u_mpp_50, p_mpp_50,
             marker='D', markersize=9,
             markerfacecolor='white', markeredgecolor='black',
             markeredgewidth=2.0, linestyle='None', label='MPP 50 %')
    ax5.plot(u_mpp_100, p_mpp_100,
             marker='D', markersize=9,
             markerfacecolor='white', markeredgecolor='red',
             markeredgewidth=2.0, linestyle='None', label='MPP 100 %')

    ax5.set_xlabel('Spannung [V]')
    ax5.set_ylabel('Leistung [mW]')
    ax5.grid(True, alpha=0.3)

    u_min_all = min(df_50['U [V]'].min(), df_100['U [V]'].min())
    u_max_all = max(df_50['U [V]'].max(), df_100['U [V]'].max())
    p_max_all = max(p_max_50, p_max_100)
    ax5.set_xlim(u_min_all, u_max_all * 1.05)
    ax5.set_ylim(0, p_max_all * 1.05)

    ax5.legend(loc='upper right')
    fig5.tight_layout()
    fig5.savefig(dir_path / 'leistung_50_100.png', format='png',
                 bbox_inches='tight', dpi=600)
    plt.close(fig5)
    results_path = dir_path / 'kennwerte_solarzelle.txt'

    text = (
        f"50 %: U_oc = {u_oc_50:.3f} V, I_sc = {i_sc_50:.3f} mA, "
        f"U_mpp = {u_mpp_50:.3f} V, I_mpp = {i_mpp_50:.3f} mA, "
        f"P_mpp = {p_mpp_50:.3f} mW\n"
        f"100 %: U_oc = {u_oc_100:.3f} V, I_sc = {i_sc_100:.3f} mA, "
        f"U_mpp = {u_mpp_100:.3f} V, I_mpp = {i_mpp_100:.3f} mA, "
        f"P_mpp = {p_mpp_100:.3f} mW\n"
    )

    with open(results_path, "w", encoding="utf-8") as f:
        f.write(text)


    print("Plots generiert")
    print(f"50 %: U_oc = {u_oc_50:.3f} V, I_sc = {i_sc_50:.3f} mA, U_mpp = {u_mpp_50:.3f} V, I_mpp = {i_mpp_50:.3f} mA, P_mpp = {p_mpp_50:.3f} mW")
    print(f"100 %: U_oc = {u_oc_100:.3f} V, I_sc = {i_sc_100:.3f} mA, U_mpp = {u_mpp_100:.3f} V, I_mpp = {i_mpp_100:.3f} mA, P_mpp = {p_mpp_100:.3f} mW")


if __name__ == '__main__':
    main()
