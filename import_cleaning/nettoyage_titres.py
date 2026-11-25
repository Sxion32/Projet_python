import re

import pandas as pd

from spreads_souverains.config import TITRES_BRUTS_FILE, TITRES_POLITIQUES_FILE

# 1. Réglages

FICHIER_TITRES = TITRES_BRUTS_FILE
FICHIER_SORTIE = TITRES_POLITIQUES_FILE

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


# 2. Filtrage des titres

def filtrer_titres_politiques(fichier_titres=FICHIER_TITRES, fichier_sortie=FICHIER_SORTIE):
    """Enlève les vidéos de JT, garde les titres politiques et enregistre le résultat dans data/cleaned/."""
    base = pd.read_csv(fichier_titres, encoding="utf-8-sig")
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

    # Enregistrement dans data/cleaned/
    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    base.to_csv(fichier_sortie, index=False, encoding="utf-8-sig")
    print("Fichier enregistré :", fichier_sortie)
    return base
