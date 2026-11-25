# Constantes du projet

from pathlib import Path

import pandas as pd

# Chemins. ROOT est la racine du dépôt : ce fichier est dans spreads_souverains/, donc un
# niveau en dessous. __file__ existe ici parce que config.py est un module importé.
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"              # données brutes, versionnées (exécution hors ligne)
CLEANED_DIR = DATA_DIR / "cleaned"      # données nettoyées, produites par le code
OUTPUTS_DIR = ROOT / "outputs"
FIG_DIR = OUTPUTS_DIR / "figures"
TABLE_DIR = OUTPUTS_DIR / "tables"

TITRES_BRUTS_FILE = RAW_DIR / "titres_franceinfo_mediacloud.csv"
TITRES_POLITIQUES_FILE = CLEANED_DIR / "titres_franceinfo_politiques.csv"
EVENTS_FILE = TABLE_DIR / "events.csv"

# Période d'étude : à partir du 1er janvier 2016, jusqu'à la dernière séance
# disponible dans les données (pas de date de fin fixée).
START_DATE = pd.Timestamp("2016-01-01")

# Pays dont nous collectons les taux à 10 ans
COUNTRIES = ["FR", "DE", "IT", "ES"]
BENCHMARK = "DE"  # dénominateur des spreads : le Bund allemand

# Une couleur fixe par pays, la même dans tous les graphiques.
COLORS = {
    "FR": "#2a78d6",  # bleu
    "ES": "#eb6834",  # orange
    "IT": "#1baf7a",  # aqua
    "DE": "#4a3aa7",  # violet
}

# Date de rupture : premier jour de marché après l'annonce de la dissolution de
# l'Assemblée nationale, le dimanche 9 juin 2024 au soir.
# Source : décret du 9 juin 2024 portant dissolution de l'Assemblée nationale, publié au Journal officiel du 10 juin 2024.
BREAK_DATE = pd.Timestamp("2024-06-10")

# Sous-périodes des statistiques descriptives : avant et après la rupture.
# Une fin à None signifie « jusqu'à la dernière séance disponible ».
PERIODS = {
    "avant_dissolution": (START_DATE, BREAK_DATE - pd.Timedelta(days=1)),
    "apres_dissolution": (BREAK_DATE, None),
}

# False : on lit les fichiers de data/raw/ sans rien télécharger.
# True : on retélécharge les données brutes (connexion internet nécessaire).
REFRESH = False
