import pandas as pd
from pathlib import Path
import re

# 1. Réglages

RACINE = Path(__file__).resolve().parents[1]   # le script est dans data/, la racine est un niveau au-dessus
FICHIER_TITRES = RACINE / "data" / "raw" / "titres_franceinfo_mediacloud.csv"
FICHIER_SORTIE = RACINE / "data" / "cleaned" / "titres_franceinfo_politiques.csv"

# Un titre est gardé seulement s'il contient au moins un de ces mots. Liste à compléter si besoin.
MOTS_POLITIQUES = [
    "gouvernement", "premier ministre", "ministre", "matignon", "élysée",
    "assemblée", "sénat", "député", "députés", "sénateur", "parlement",
    "motion de censure", "censure", "dissolution", "49.3", "remaniement", "démission",
    "élection", "élections", "législatives", "présidentielle", "municipales",
    "européennes", "régionales", "scrutin", "sondage", "référendum",
    "budget", "réforme", "projet de loi", "conseil constitutionnel",
    "macron", "philippe", "castex", "borne", "attal", "barnier", "bayrou", "lecornu",
    "le pen", "bardella", "mélenchon", "rassemblement national", "rn", "lfi",
    "insoumis", "républicains", "socialiste", "renaissance", "nupes",
    "nouveau front populaire", "nfp", "gilets jaunes", "retraites",
]

# Titres de vidéos de journaux télévisés à enlever (ex : "Le JT du vendredi 19.01.2018, 1ère partie")
MOTIF_VIDEOS = r"\d{1,2}\.\d{1,2}\.\d{4}|1ère partie|2e partie|2ème partie|replay"


# 2. Chargement du fichier CSV

base = pd.read_csv(FICHIER_TITRES, encoding="utf-8-sig")
base = base.dropna(subset=["titre"])
print("Nombre de titres chargés :", len(base))

# Enlever les vidéos de journaux télévisés
est_une_video = base["titre"].str.contains(MOTIF_VIDEOS, case=False, regex=True)
base = base[~est_une_video]
print("Après suppression des vidéos de JT :", len(base))

# Garder seulement les titres politiques.
# \b = "frontière de mot" : "rn" ne doit pas être trouvé dans "gouvernement".
# re.escape protège les caractères spéciaux (le point de "49.3").
# (?: ... ) regroupe les mots sans créer de groupe de capture (évite un avertissement de pandas).
mots_proteges = [re.escape(mot) for mot in MOTS_POLITIQUES]
motif_politique = r"\b(?:" + "|".join(mots_proteges) + r")\b"
est_politique = base["titre"].str.contains(motif_politique, case=False, regex=True)
base = base[est_politique]
print("Titres politiques gardés :", len(base))


# 3. Enregistrement dans data/cleaned/

base.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8-sig")
print("Fichier enregistré :", FICHIER_SORTIE)
