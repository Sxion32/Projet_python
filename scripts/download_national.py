"""Téléchargement des taux à 10 ans quotidiens publiés par les banques centrales nationales.

Ces séries servent d'arbitre entre CNBC et Eurostat (journal, D9) : elles ne sont
pas utilisées pour calculer nos spreads, puisque chacune est construite selon sa
propre méthode (journal, D5). Les réponses brutes sont enregistrées telles quelles
dans data/raw/nationales/, avec un fichier metadata.csv.

Sources :
- Banque de France, TEC 10 (copie DBnomics, JSON) ;
- Bundesbank, rendement à 10 ans des titres fédéraux issu de la courbe des taux (CSV) ;
- Banco de España, obligations de l'État à 10 ans, tableau TI 1.3 (CSV).

Usage : python scripts/download_national.py
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

import requests

SOURCES = {
    "banque_de_france.json": "https://api.db.nomics.world/v22/series/BDF/FM/D.FR.EUR.FR2.BB.FRMOYTEC10.HSTA?observations=1",
    "bundesbank.csv": (
        "https://www.bundesbank.de/statistic-rmi/StatisticDownload"
        "?tsId=BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A"
        "&its_csvFormat=en&its_fileFormat=csv&mode=its&its_from=2016-01-01"
    ),
    "banco_de_espana.csv": "https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_3.csv",
}
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "nationales"


def download(file_name, url):
    """Télécharge une source et l'enregistre telle quelle sous data/raw/nationales/.

    Paramètres
    ----------
    file_name : str, nom du fichier à écrire, par exemple "bundesbank.csv".
    url : str, adresse de la source.

    Retourne
    --------
    Path du fichier écrit.

    Exemple
    -------
    >>> download("bundesbank.csv", SOURCES["bundesbank.csv"])
    PosixPath('.../data/raw/nationales/bundesbank.csv')
    """
    # La Bundesbank et le Banco de España refusent les requêtes sans navigateur déclaré.
    response = requests.get(url, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    path = OUTPUT_DIR / file_name
    path.write_bytes(response.content)
    return path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    with open(OUTPUT_DIR / "metadata.csv", "w", newline="", encoding="utf-8") as metadata_file:
        writer = csv.writer(metadata_file)
        writer.writerow(["fichier", "url", "telecharge_le_utc"])
        for file_name, url in SOURCES.items():
            path = download(file_name, url)
            writer.writerow([file_name, url, now.isoformat(timespec="seconds")])
            print(f"{file_name} -> {path.relative_to(OUTPUT_DIR.parent.parent.parent)}")


if __name__ == "__main__":
    main()
