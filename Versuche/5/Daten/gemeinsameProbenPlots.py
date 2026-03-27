import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

# 1. Ruhepotenziale (Tippfehler-resistent durch Umwandlung in Kleinbuchstaben)
RUHEPOTENZIALE = {
    'EIsen_in_NHCl(2)': -0.538,   
    'EIsen_in_NHCl_besonderheit(1)': -0.607,   
    'EIsen_in_H2So4_bei RT': -0.481,  
    'EIsen_in_H2So4_bei 30': -0.455,
    'Chromstahl_in_H2So4_bei RT': 0.230,
}

def main():
    dir_path = Path(__file__).resolve().parent
    asc_files = list(dir_path.glob('*.ASC'))
    
    print(f"Dir: {dir_path}")
    print(f"ASC-Dateien: {len(asc_files)}\n")
    
    if not asc_files:
        print("Keine .ASC-Dateien gefunden!")
        return

    # 2. Dateien nach Basisnamen gruppieren
    grouped_files = defaultdict(list)
    for file in asc_files:
        basename = file.stem.replace('_bei 30', '').replace('_bei RT', '').strip()
        grouped_files[basename].append(file)

    # 3. Für jede Gruppe (Basisname) EINEN gemeinsamen Plot erstellen
    for basename, files in grouped_files.items():
        print(f"\nErstelle Plot für Gruppe: '{basename}' (enthält {len(files)} Datei(en))")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Um die minimalen und maximalen Werte für die Achsenskalierung zu sammeln
        all_x_vals = []
        all_y_vals = []
        
        # JETZT: Schleife über alle Dateien INNERHALB dieser Gruppe
        for file in files:
            print(f"  -> Füge hinzu: {file.name}")
            
            df = pd.read_csv(
                file, 
                sep=r'\s+', 
                header=None, 
                names=['Potenzial_V', 'Zeit_s', 'Strom_A', 'Stromdichte'],
                engine='python'
            )
            
            # Ruhepotenzial anwenden

            rp = RUHEPOTENZIALE.get(file.stem, 0.0)
            df['Potenzial_V_absolut'] = df['Potenzial_V'] + rp
            
            # Label und Farbe festlegen
            if '30' in file.stem:
                label_name = '30 °C'
                line_color = '#d62728' # Rot
            elif 'RT' in file.stem:
                label_name = 'Raumtemperatur'
                line_color = '#1f77b4' # Blau
            else:
                label_name = file.stem
                line_color = 'black'
            
            # Kurve zeichnen
            ax.plot(df['Potenzial_V_absolut'], df['Stromdichte'], color=line_color, label=label_name)
            
            # Werte für die Achsenskalierung merken
            all_x_vals.append(df['Potenzial_V_absolut'])
            all_y_vals.append(df['Stromdichte'])

        # 4. Plot formatieren
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
        ax.set_xlabel('Potenzial [V]')
        ax.set_ylabel('Stromdichte [A/cm$^2$]')
        
        # Dynamische Achsenskalierung über alle Kurven im Plot hinweg
        if all_x_vals and all_y_vals:
            global_x_min = pd.concat(all_x_vals).min()
            global_x_max = pd.concat(all_x_vals).max()
            x_pad = (global_x_max - global_x_min) * 0.05
            ax.set_xlim(global_x_min, global_x_max + x_pad)
            
            global_y_min = pd.concat(all_y_vals).min()
            global_y_max = pd.concat(all_y_vals).max()
            y_pad = (global_y_max - global_y_min) * 0.1
            ax.set_ylim(global_y_min - y_pad, global_y_max + y_pad)
            
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        fig.tight_layout()
        
        # Speichern mit dem Namen der Gruppe (z.B. "Eisen_in_H2SO4_plot.png")
        save_path = dir_path / f"{basename}_Vergleich.png"
        fig.savefig(save_path, format='png', dpi=600)
        plt.close(fig)
        
    print(f"\nFertig! Es wurden {len(grouped_files)} Gruppen-Plots generiert.")

if __name__ == '__main__':
    main()
