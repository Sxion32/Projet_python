#dans ce script, on transforme les taux bruts en spreads souverains et on prépare le tableau qui regrouppent les données afin de l'utilisé par la suite. 
#On utilise les données nétoyées. 

from pathlib import Path
import sys


import pandas as pd
from spreads_souverains import config


def compute_spreads(yields): #Calcule les spreads  par rapport à l'Allemagne. (ne point de base)
    spreads = pd.DataFrame(index=yields.index)
    for country in ["FR", "IT", "ES"]:
        spreads[f"s_{country}"] = (yields[country] - yields["DE"]) * 100
    return spreads


def build_panel(yields, export=True): #regroupe les données de taux dans un seul tableau 
    spreads = compute_spreads(yields)
    panel = pd.concat([yields, spreads], axis=1)
    panel.index.name = "date"
    if export:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        panel.to_csv(config.DATA_DIR / "yields.csv", float_format="%.4f")

    return panel
