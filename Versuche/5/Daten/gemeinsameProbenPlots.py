import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

def main():
    dir_path = Path(__file__).resolve().parent
    asc_files = list(dir_path.glob('*.ASC'))
    print(f"Dir: {dir_path}")
    print(f"ASC-Dateien: {len(asc_files)}")
    if not asc_files:
        print("Keine .asc-Dateien gefunden!")
        return
    grouped_files = defaultdict(list)
    
    for file in asc_files:
        print(f"Verarbeite Datei: {file.name}...")
        
        basename= file.stem.replace('_bei 30 ', '').replace('_bei RT', '')
        grouped_files[basename].append(file)

    for basename, files in grouped_files.items():
        print(f"Erstelle Plot für Gruppe: {basename} mit {len(files)} Dateien...")
        fig, ax = plt.subplots(figsize=(8, 5))
        
        df = pd.read_csv(
            file, 
            sep='\s+', 
            header=None, 
            names=['Potenzial_V', 'Zeit_s', 'Strom_A', 'Stromdichte']
        )
        
        if '30' in file.stem:
            label_suffix = '30°C'
            label_color = 'red'
        elif 'RT' in file.stem:
            label_suffix = 'RT'
            label_color = 'blue'
        else:
            label_suffix = 'Unbekannt'
            label_color = 'black'
        
        ax.plot(df['Potenzial_V'], df['Stromdichte'], color=label_color, label=f"{file.stem} {label_suffix}")
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
        # Achsenbeschriftungen passend zur Auswertung
        ax.set_xlabel('Potenzial [V]')
        ax.set_ylabel('Stromdichte [A/cm$^2$]')
        ax.set_xlim(0, df['Potenzial_V'].max()*1.05)
        ax.set_ylim(df['Stromdichte'].min()*1.1, df['Stromdichte'].max() * 1.1)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        fig.tight_layout()
        
        fig.savefig(dir_path / f"{basename}_plot.png", format='png', dpi=600)
        plt.close(fig)
        
    print(f"Fertig! Es wurden {len(asc_files)} Plots generiert.")

if __name__ == '__main__':
    main()
