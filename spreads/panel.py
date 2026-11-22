#dans ce script, on transforme les taux bruts en spreads souverains et on prépare le tableau qui regrouppent les données afin de l'utilisé par la suite. 
#On utilise les données nétoyées. 

import pandas as pd

from spreads import config


def compute_spreads(yields: pd.DataFrame) -> pd.DataFrame:
    """Calcule les spreads à 10 ans contre le Bund allemand, en points de base."""
    spread_countries = [c for c in config.COUNTRIES if c != config.BENCHMARK]
    spreads = pd.DataFrame(index=yields.index)
    for country in spread_countries:
        spreads[f"s_{country}"] = (yields[country] - yields[config.BENCHMARK]) * 100
    return spreads


def build_panel(yields: pd.DataFrame, export: bool = True) -> pd.DataFrame:
    """Réunit rendements (%) et spreads (pb) dans un seul DataFrame et l'exporte."""
    spreads = compute_spreads(yields)
    panel = pd.concat([yields, spreads], axis=1)
    panel.index.name = "date"

    if export:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        panel.to_csv(config.DATA_DIR / "yields.csv", float_format="%.4f")

    return panel

