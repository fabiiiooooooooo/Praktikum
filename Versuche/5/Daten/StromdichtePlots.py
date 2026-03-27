import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


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
    print(f"ASC-Dateien: {len(asc_files)}")
    if not asc_files:
        print("Keine .asc-Dateien gefunden!")
        return

    for file in asc_files:
        print(f"Verarbeite Datei: {file.name}...")
        rp = RUHEPOTENZIALE.get(file.stem, 0.0)
        print(f"Verwende Ruhepotential: {rp} V für Datei: {file.name}")
        fig, ax = plt.subplots(figsize=(8, 5))
        temp_label = '30 °C' if '30' in file.stem else 'Raumtemperatur' if 'RT' in file.stem else 'Raumtemperatur'
        
        df = pd.read_csv(
            file, 
            sep='\s+', 
            header=None, 
            names=['Potenzial_V', 'Zeit_s', 'Strom_A', 'Stromdichte']
        )
        df['Ruhepotential_korrigiert'] = df['Potenzial_V'] + rp
        ax.plot(df['Ruhepotential_korrigiert'], df['Stromdichte'], color='blue', label=temp_label)
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
        # Achsenbeschriftungen passend zur Auswertung
        ax.set_xlabel('Potenzial [V]')
        ax.set_ylabel('Stromdichte [A/cm$^2$]')
        ax.set_xlim(rp, df['Ruhepotential_korrigiert'].max()+10)
        ax.set_ylim(df['Stromdichte'].min()*1.1, df['Stromdichte'].max() * 1.1)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        fig.tight_layout()
        
        fig.savefig(dir_path / f"{file.stem}_plot.png", format='png', dpi=600)
        plt.close(fig)
        
    print(f"Fertig! Es wurden {len(asc_files)} Plots generiert.")

if __name__ == '__main__':
    main()
