import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re 

def extract_value(df_raw, r_label, col_name):
    matches = df_raw.loc[df_raw['R'].astype(str).str.contains(r_label, na=False), col_name]
    if not matches.empty:
        val_str = str(matches.iloc[0]).replace(',', '.')
        
        # Falls jemand 'mA' in eine 'uA'-Spalte geschrieben hat: Faktor 1000
        multiplier = 1.0
        if 'mA' in val_str and 'uA' in col_name:
            multiplier = 1000.0
            
        # Entfernt alle Buchstaben/Leerzeichen (behält nur Ziffern, Punkt und Minus)
        num_str = re.sub(r'[^\d.-]', '', val_str)
        
        try:
            return float(num_str) * multiplier
        except ValueError:
            # Falls die Zelle komplett leer war
            pass 
            
    # Fallback auf den Maximalwert der Spalte, falls die Markierung fehlt oder kaputt ist
    return pd.to_numeric(df_raw[col_name], errors='coerce').max()


def main():
    dir_path = Path(__file__).resolve().parent
    csv1_path = dir_path / '0teOrdnung_Messung1_50%.csv'
    csv2_path = dir_path / '0teOrdnung_Messung2_50%.csv'

    # ===========================
    # 1. Daten roh laden
    # ===========================
    df1_raw = pd.read_csv(csv1_path, sep=';', decimal=',')
    df2_raw = pd.read_csv(csv2_path, sep=';', decimal=',')
    
    # ===========================
    # 2. U_L und I_K Werte extrahieren (vor der Bereinigung)
    # ===========================
    u_oc_1 = extract_value(df1_raw, 'U_L', 'U [V]')
    print(f"Messung 1: U_L = {u_oc_1} V")
    i_sc_1 = extract_value(df1_raw, 'I_K', 'I [uA]')
    print(f"Messung 1: I_K = {i_sc_1} uA")

    u_oc_2 = extract_value(df2_raw, 'U_L', 'U [mV]')
    i_sc_2 = extract_value(df2_raw, 'I_K', 'I [uA]')
    print(f"Messung 2: I_K = {i_sc_2} uA")
    print(f"Messung 2: U_L = {u_oc_2} mV")
    
    # ===========================
    # 3. Daten für Plots bereinigen
    # ===========================
    df1 = df1_raw.copy()
    df1['U [V]'] = pd.to_numeric(df1['U [V]'], errors='coerce')
    df1['I [uA]'] = pd.to_numeric(df1['I [uA]'], errors='coerce')

    df2 = df2_raw.copy()
    df2['U [mV]'] = pd.to_numeric(df2['U [mV]'], errors='coerce')
    df2['I [uA]'] = pd.to_numeric(df2['I [uA]'], errors='coerce')

    # ===========================
    # U_L und I_K aus dem Plot-Datensatz entfernen
    # ===========================
    df1 = df1[~df1['R'].astype(str).str.contains('U_L|I_K', na=False)].reset_index(drop=True)
    df2 = df2[~df2['R'].astype(str).str.contains('U_L|I_K', na=False)].reset_index(drop=True)

    # ===========================
    # FEHLERWERTE DEFINIEREN (Platzhalter - Bitte anpassen!)
    # ===========================
    u_err_1 = 0.0  # Fehler Spannung Messung 1 (in V)
    i_err_1 = 20.5   # Fehler Strom Messung 1 (in uA)
    
    u_err_2 = 0.0    # Fehler Spannung Messung 2 (in mV)
    i_err_2 = 20.5   # Fehler Strom Messung 2 (in uA)

    # ===========================
    # 4. Plot Messung 1
    # ===========================
    df1 = df1.sort_values(by='U [V]')
    fig1, ax1 = plt.subplots(figsize=(7, 5))

    ax1.errorbar(df1['U [V]'], df1['I [uA]'], 
                 xerr=u_err_1, yerr=i_err_1, 
                 fmt='-o', color='black', ecolor='gray', 
                 capsize=3, markersize=5, linewidth=2.0, zorder=3)

    u_min_1 = df1['U [V]'].min()
    u_max_1 = df1['U [V]'].max()
    i_max_1 = df1['I [uA]'].max()

    ax1.set_xlim(u_min_1, u_max_1 * 1.05)
    ax1.set_ylim(0, (i_max_1 + i_err_1) * 1.05)

    ax1.set_xlabel('Spannung [V]')
    ax1.set_ylabel('Strom [uA]')
    ax1.grid(True, alpha=0.3)

    fig1.tight_layout()
    fig1.savefig(dir_path / 'nullOrdnung_Messung1.png', format='png',
                 bbox_inches='tight', dpi=600)

    # ===========================
    # 5. Plot 2.Messung
    # ===========================
    df2 = df2.sort_values(by='U [mV]')
    fig2, ax2 = plt.subplots(figsize=(7, 5))

    ax2.errorbar(df2['U [mV]'], df2['I [uA]'], 
                 xerr=u_err_2, yerr=i_err_2,
                 fmt='-o', color='red', ecolor='salmon', 
                 capsize=3, markersize=5, linewidth=2.0, zorder=3)
    
    u_min_2 = df2['U [mV]'].min()
    u_max_2 = df2['U [mV]'].max()
    i_max_2 = df2['I [uA]'].max()

    ax2.set_xlim(u_min_2, u_max_2 * 1.05)
    ax2.set_ylim(0, (i_max_2 + i_err_2) * 1.05)
    
    ax2.set_xlabel('Spannung [mV]')
    ax2.set_ylabel('Strom [uA]')
    ax2.grid(True, alpha=0.3)

    fig2.tight_layout()
    fig2.savefig(dir_path / 'nullOrdnung_Messung2.png', format='png',
                 bbox_inches='tight', dpi=600)

    print("Plots generiert")

if __name__ == '__main__':
    main()
