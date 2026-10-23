"""Téléchargement des taux à 10 ans quotidiens publiés par CNBC.

Ce script est le seul endroit où nous interrogeons CNBC. Il enregistre la réponse
brute, sans la modifier, dans data/raw/cnbc/, pour que le notebook puisse ensuite
tourner hors ligne. Il ajoute une ligne par fichier dans data/raw/cnbc/metadata.csv
(symbole, URL, date de téléchargement).

Hypothèses :
- l'API ts-api.cnbc.com n'est pas documentée : son format peut changer ;
- les barres quotidiennes sont découpées à l'heure de New York (EST5EDT) ;
- les conditions d'utilisation de CNBC (Versant) limitent l'usage à un usage
  personnel et non commercial : la publication des fichiers bruts reste à trancher.

Usage : python scripts/download_cnbc.py
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

import requests

SYMBOLS = ["FR10Y-FR", "DE10Y-DE", "ES10Y-ES"]
START = "20160101000000"
BARS_URL = "https://ts-api.cnbc.com/harmony/app/bars/{symbol}/1D/{start}/{end}/adjusted/EST5EDT.json"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "cnbc"


def download_symbol(symbol, end):
    """Télécharge les barres quotidiennes d'un symbole CNBC et les enregistre telles quelles.

    Paramètres
    ----------
    symbol : str, symbole CNBC, par exemple "FR10Y-FR".
    end : str, fin de la période au format AAAAMMJJhhmmss.

    Retourne
    --------
    tuple (chemin du fichier écrit, URL interrogée).

    Exemple
    -------
    >>> download_symbol("FR10Y-FR", "20261022000000")
    (PosixPath('.../data/raw/cnbc/FR10Y-FR.json'), 'https://ts-api.cnbc.com/...')
    """
    url = BARS_URL.format(symbol=symbol, start=START, end=end)
    response = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    if "priceBars" not in response.text:
        raise ValueError(f"Réponse CNBC inattendue pour {symbol} : {response.text[:200]}")
    path = OUTPUT_DIR / f"{symbol}.json"
    path.write_bytes(response.content)
    return path, url


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    end = now.strftime("%Y%m%d000000")
    metadata_path = OUTPUT_DIR / "metadata.csv"
    with open(metadata_path, "w", newline="", encoding="utf-8") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["symbole", "url", "telecharge_le_utc"])
        for symbol in SYMBOLS:
            path, url = download_symbol(symbol, end)
            writer.writerow([symbol, url, now.isoformat(timespec="seconds")])
            print(f"{symbol} -> {path.relative_to(OUTPUT_DIR.parent.parent.parent)}")


if __name__ == "__main__":
    main()
