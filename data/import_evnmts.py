# attention il faut pip install mediacloud 

import mediacloud.api
import pandas as pd
import datetime as dt
import os

# 1. Les réglages 

CLE_API = "16c2786a664269f65085691cd07362167a027312"

# Le numéro de France Info (francetvinfo.fr) dans Media Cloud
ID_FRANCEINFO = 107654

# Période (année, mois, jour).
DATE_DEBUT = dt.date(2018, 5, 1)
DATE_FIN = dt.date(2018, 5, 31)

# Mots-clés de recherche pour les articles à récupérer
RECHERCHE = ('gouvernement OR "Premier ministre" OR Assemblée OR Sénat OR élection '
             'OR élections OR Élysée OR "motion de censure" OR dissolution OR législatives '
             'OR présidentielle OR ministre OR député OR députés OR "49.3" OR budget')

DOSSIER_CLEANED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw")
os.makedirs(DOSSIER_CLEANED, exist_ok=True)
FICHIER_SORTIE = os.path.join(DOSSIER_CLEANED, "titres_franceinfo_mediacloud.csv")


# 2. Connection à Media Cloud 

recherche = mediacloud.api.SearchApi(CLE_API)


# 3. Préparation de la liste des mois 

debuts_de_mois = pd.date_range(start=DATE_DEBUT.replace(day=1), end=DATE_FIN, freq="MS")
print("Nombre de mois à traiter :", len(debuts_de_mois))


# 4. Récupération des les articles, mois par mois 

for debut_mois in debuts_de_mois:
    # Premier et dernier jour du mois (sans sortir de la période choisie)
    debut = max(debut_mois.date(), DATE_DEBUT)
    fin = min((debut_mois + pd.offsets.MonthEnd(0)).date(), DATE_FIN)

    articles_du_mois = []
    jeton_page = None          # le "jeton" indique à Media Cloud quelle page donner ensuite

    while True:
        try:
            page, jeton_page = recherche.story_list(
                RECHERCHE, debut, fin,
                source_ids=[ID_FRANCEINFO],
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
        deja_la = os.path.exists(FICHIER_SORTIE)
        tableau.to_csv(FICHIER_SORTIE, mode="a", header=not deja_la,
                       index=False, encoding="utf-8")


# 5. Nettoyage du fichier final 

if not os.path.exists(FICHIER_SORTIE):
    print("Aucun article récupéré.")
    exit()

tableau = pd.read_csv(FICHIER_SORTIE, encoding="utf-8-sig")
tableau["date"] = pd.to_datetime(tableau["date"])

# Enlever les doublons (même date et même titre) et trier par date
tableau = tableau.drop_duplicates(subset=["date", "titre"])
tableau = tableau.sort_values("date")
tableau.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8-sig")


#6. Impression des statistiques

print()
print("Nombre total d'articles :", len(tableau))
print()
print("Nombre d'articles par année :")
print(tableau["date"].dt.year.value_counts().sort_index().to_string())
