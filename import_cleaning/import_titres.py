# Collecte des titres d'articles politiques de France Info via Media Cloud.
# attention il faut pip install mediacloud

import datetime as dt
import os

import mediacloud.api
import pandas as pd
from dotenv import load_dotenv

from spreads_souverains.config import ROOT, TITRES_BRUTS_FILE


# 1. Les réglages

# La clé est lue dans le fichier .env (non versionné), voir .env.example
load_dotenv(ROOT / ".env")
CLE_API = os.getenv("MEDIACLOUD_API_KEY")

# Période (année, mois, jour).
DATE_DEBUT = dt.date(2016, 1, 1)
DATE_FIN = dt.date.today()

# Mots-clés de recherche pour les articles à récupérer
RECHERCHE = ('gouvernement OR "Premier ministre" OR Assemblée OR Sénat OR élection '
             'OR élections OR Élysée OR "motion de censure" OR dissolution OR législatives '
             'OR présidentielle OR ministre OR député OR députés OR "49.3" OR budget')

# France Info a changé d'adresse le 14 mai 2025 : Media Cloud les voit comme deux médias
NOMS_FRANCEINFO = ["francetvinfo.fr", "franceinfo.fr"]

FICHIER_SORTIE = TITRES_BRUTS_FILE


# 2. Connexion à Media Cloud

def connexion_mediacloud(cle_api=CLE_API):
    """Renvoie l'annuaire des médias et l'outil de recherche d'articles."""
    annuaire = mediacloud.api.DirectoryApi(cle_api)
    recherche = mediacloud.api.SearchApi(cle_api)
    return annuaire, recherche


# 3. Trouver les numéros de France Info dans l'annuaire

def trouver_ids_franceinfo(annuaire, noms=NOMS_FRANCEINFO):
    """Renvoie les numéros Media Cloud des médias dont le nom est exactement dans noms."""
    ids = []
    for nom in noms:
        resultats = annuaire.source_list(name=nom, platform="online_news", limit=50)["results"]
        for source in resultats:
            if source["name"] == nom:          # nom exact : on écarte mobile.francetvinfo.fr, etc.
                ids.append(source["id"])
                print("Trouvé :", nom, "-> numéro", source["id"])
    return ids


# 4. Récupération des articles, mois par mois

def collecter_titres(recherche, source_ids, date_debut=DATE_DEBUT, date_fin=DATE_FIN,
                     fichier_sortie=FICHIER_SORTIE):
    """Ajoute au CSV les titres (date, titre) de chaque mois de la période."""
    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    debuts_de_mois = pd.date_range(start=date_debut.replace(day=1), end=date_fin, freq="MS")
    print("Nombre de mois à traiter :", len(debuts_de_mois))

    for debut_mois in debuts_de_mois:
        # Premier et dernier jour du mois (sans sortir de la période choisie)
        debut = max(debut_mois.date(), date_debut)
        fin = min((debut_mois + pd.offsets.MonthEnd(0)).date(), date_fin)

        articles_du_mois = []
        jeton_page = None          # le "jeton" indique à Media Cloud quelle page donner ensuite

        while True:
            try:
                page, jeton_page = recherche.story_list(
                    RECHERCHE, debut, fin,
                    source_ids=source_ids,
                    page_size=1000,
                    pagination_token=jeton_page,
                )
            except Exception as erreur:
                print("   Erreur pour ce mois :", erreur)
                break

            articles_du_mois = articles_du_mois + page

            # S'il n'y a plus de jeton, c'est qu'on a eu la dernière page
            if jeton_page is None:
                break

        print(debut, "->", fin, ":", len(articles_du_mois), "articles")

        # Ajouter les articles du mois au fichier CSV
        if len(articles_du_mois) > 0:
            tableau = pd.DataFrame(articles_du_mois)
            tableau = tableau[["publish_date", "title"]]
            tableau.columns = ["date", "titre"]

            # On écrit les noms de colonnes seulement si le fichier n'existe pas encore
            deja_la = os.path.exists(fichier_sortie)
            tableau.to_csv(fichier_sortie, mode="a", header=not deja_la,
                           index=False, encoding="utf-8")


# 5. Nettoyage du fichier final

def dedoublonner_titres(fichier_sortie=FICHIER_SORTIE):
    """Enlève les doublons (même date et même titre), trie par date et réécrit le CSV."""
    if not os.path.exists(fichier_sortie):
        print("Aucun article récupéré.")
        return None

    tableau = pd.read_csv(fichier_sortie, encoding="utf-8-sig")
    tableau["date"] = pd.to_datetime(tableau["date"])
    tableau = tableau.drop_duplicates(subset=["date", "titre"])
    tableau = tableau.sort_values("date", kind="stable")
    tableau.to_csv(fichier_sortie, index=False, encoding="utf-8-sig")
    return tableau


# 6. Impression des statistiques

def afficher_statistiques(tableau):
    """Affiche le nombre total d'articles et le nombre d'articles par année."""
    print()
    print("Nombre total d'articles :", len(tableau))
    print()
    print("Nombre d'articles par année :")
    print(tableau["date"].dt.year.value_counts().sort_index().to_string())
