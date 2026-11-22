#dans ce script, on transforme les taux bruts en spreads souverains et on prépare le tableau qui regrouppent les données afin de l'utilisé par la suite. 
#On utilise les données nétoyées. 

from pathlib import Path
import sys


import pandas as pd
from spreads import config


def compute_spreads(yields):
    """Calcule les spreads (en points de base) par rapport à l'Allemagne."""
    spreads = pd.DataFrame(index=yields.index)
    for country in ["FR", "IT", "ES"]:
        spreads[f"s_{country}"] = (yields[country] - yields["DE"]) * 100
    return spreads


def build_panel(yields, export=True):
    """Regroupe les rendements et les spreads dans un seul tableau."""
    spreads = compute_spreads(yields)
    panel = pd.concat([yields, spreads], axis=1)
    panel.index.name = "date"

    if export:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        panel.to_csv(config.DATA_DIR / "yields.csv", float_format="%.4f")

    return panel


if __name__ == "__main__":
    yields = pd.read_csv(
        config.DATA_DIR / "cleaned" / "yields_10y_cnbc_daily.csv",
        index_col=0,
        parse_dates=True,
    )
    panel = build_panel(yields, export=True)
    print(panel.tail())
    print("Spread FR le 07/06/2024 :", round(panel.loc["2024-06-07", "s_FR"], 2), "pb")
