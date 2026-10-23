"""Téléchargement de la série quotidienne Eurostat irt_lt_mcby_d via DBnomics.

L'API Eurostat ne diffuse plus cette série (voir D4 dans le journal) ; DBnomics en
conserve une copie, arrêtée en avril 2025. Elle nous sert de référence publique
pour juger CNBC. La réponse brute est enregistrée telle quelle dans
data/raw/eurostat/, avec un fichier metadata.csv.

Usage : python scripts/download_eurostat.py
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

import requests

COUNTRIES = ["FR", "DE", "ES"]
SERIES_URL = "https://api.db.nomics.world/v22/series/Eurostat/IRT_LT_MCBY_D/D.MCBY.{country}?observations=1"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "eurostat"


def download_country(country):
    """Télécharge la série quotidienne Eurostat d'un pays et l'enregistre telle quelle.

    Paramètres
    ----------
    country : str, code pays à deux lettres, par exemple "FR".

    Retourne
    --------
    tuple (chemin du fichier écrit, URL interrogée).

    Exemple
    -------
    >>> download_country("DE")
    (PosixPath('.../data/raw/eurostat/DE.json'), 'https://api.db.nomics.world/...')
    """
    url = SERIES_URL.format(country=country)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    path = OUTPUT_DIR / f"{country}.json"
    path.write_bytes(response.content)
    return path, url


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    with open(OUTPUT_DIR / "metadata.csv", "w", newline="", encoding="utf-8") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["pays", "url", "telecharge_le_utc"])
        for country in COUNTRIES:
            path, url = download_country(country)
            writer.writerow([country, url, now.isoformat(timespec="seconds")])
            print(f"{country} -> {path.relative_to(OUTPUT_DIR.parent.parent.parent)}")


if __name__ == "__main__":
    main()
