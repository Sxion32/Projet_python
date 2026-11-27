import re

import matplotlib.pyplot as plt
import pandas as pd

from spreads_souverains.config import EVENTS_FILE, FIG_DIR, TITRES_POLITIQUES_FILE

# 1. Réglages 

# Base créée par import_cleaning/nettoyage_titres.py (titres politiques, sans les vidéos de JT)
FICHIER_TITRES = TITRES_POLITIQUES_FILE
FICHIER_EVENTS = EVENTS_FILE
FICHIER_GRAPHIQUE = FIG_DIR / "events_graphique.png"

# Nombre de jours utilisés pour calculer le niveau "habituel"
FENETRE = 30

# Un jour est un pic s'il a au moins SEUIL fois plus d'articles que d'habitude
SEUIL = 2.0

# Nombre minimum d'articles pour qu'un jour soit considéré comme un pic (cela permet d'éviter les faux pics quand l'archive contient très peu d'articles)
MINIMUM_ARTICLES = 20

# Deux pics séparés de moins de ECART_MAX jours = un seul événement
ECART_MAX = 2

# Mots trop courants, à ignorer quand on cherche les mots-clés d'un événement
MOTS_VIDES = set("""
le la les un une des du de d l au aux et ou en dans sur pour par avec sans
ce cet cette ces son sa ses leur leurs qui que quoi dont il elle ils elles on
nous vous je tu se ne pas plus moins est sont a ont été être avoir fait faire
comme mais aussi tout tous toute toutes après avant entre contre vers chez
quand comment pourquoi selon face lors depuis encore déjà très bien
direct vidéo info infos franceinfo entretien replay partie 1ère
lundi mardi mercredi jeudi vendredi samedi dimanche
janvier février mars avril mai juin juillet août septembre octobre novembre décembre
""".split())


# 2. Chargement de la base de titres politiques

def charger_titres(fichier_titres=FICHIER_TITRES):
    """Lit la base de titres politiques, avec la colonne "date" convertie en dates."""
    base = pd.read_csv(fichier_titres, encoding="utf-8-sig", parse_dates=["date"])
    print("Titres politiques chargés :", len(base))
    return base


# 3. Compter les articles par jour 

def compter_articles_par_jour(base):
    """Tableau (un jour par ligne) du nombre d'articles, les jours sans article comptent 0."""
    par_jour = base.groupby("date").size()
    tous_les_jours = pd.date_range(par_jour.index.min(), par_jour.index.max(), freq="D")
    par_jour = par_jour.reindex(tous_les_jours, fill_value=0)
    return pd.DataFrame({"nb_articles": par_jour})


# 4. Calculer le niveau "habituel" et repérer les pics 
# Niveau habituel = la MÉDIANE des 30 jours précédents. (La médiane est peu sensible aux pics, contrairement à la moyenne, shift pour ne pas compter le jour lui-même.)

def reperer_pics(jours):
    """Ajoute les colonnes habituel, ratio et est_un_pic au tableau des jours."""
    jours = jours.copy()
    jours["habituel"] = jours["nb_articles"].shift(1).rolling(FENETRE, min_periods=10).median()

    # Combien de fois plus d'articles que d'habitude ? 
    jours["ratio"] = jours["nb_articles"] / jours["habituel"] 
    jours["est_un_pic"] = (jours["ratio"] >= SEUIL) & (jours["nb_articles"] >= MINIMUM_ARTICLES)
    print("Nombre de jours de pic :", jours["est_un_pic"].sum())
    return jours


# 5. Regrouper les jours de pic proches en un seul événement 
# Exemple : une crise qui dure 3 jours donne 3 jours de pic, mais 1 seul événement.
# On parcourt les jours de pic dans l'ordre et on change de numéro d'événement quand l'écart avec le pic précédent dépasse ECART_MAX jours.

def regrouper_pics(jours):
    """Renvoie les jours de pic avec une colonne "evenement" (numéro de l'événement)."""
    pics = jours[jours["est_un_pic"]].copy()
    numeros = []
    numero = 0
    jour_precedent = None
    for jour in pics.index:
        if jour_precedent is not None and (jour - jour_precedent).days > ECART_MAX:
            numero = numero + 1
        numeros.append(numero)
        jour_precedent = jour

    pics["evenement"] = numeros
    return pics


# 6. Trouver les mots caractéristiques d'un jour 
# Idée : un mot est caractéristique s'il est BEAUCOUP plus fréquent ce jour-là que d'habitude. On compare donc sa fréquence du jour à sa fréquence moyenne.

def decouper_en_mots(titre):
    mots = re.findall(r"[a-zàâäéèêëîïôöùûüç0-9\.]+", titre.lower())
    mots = [m.strip(".") for m in mots]
    # On enlève les mots courts, les mots vides et les nombres (dates, années),
    # sauf "49.3" qui est un vrai mot politique
    mots_gardes = []
    for m in mots:
        contient_un_chiffre = re.search(r"\d", m) is not None
        if len(m) >= 4 and m not in MOTS_VIDES and (not contient_un_chiffre or m == "49.3"):
            mots_gardes.append(m)
    return mots_gardes

# Compter, pour une liste de titres, dans combien de titres apparaît chaque mot.
# set() enlève les doublons
def compter_mots(titres):
    compteur = {}
    for titre in titres:
        for mot in set(decouper_en_mots(titre)):
            compteur[mot] = compteur.get(mot, 0) + 1
    return compteur

def mots_caracteristiques(titres_du_jour, compteur_global, nb_jours_total, combien=6):
    compteur_jour = compter_mots(titres_du_jour)
    scores = {}
    for mot, nb in compteur_jour.items():
        if nb >= 3:                                         # au moins 3 titres ce jour-là
            moyenne_par_jour = compteur_global[mot] / nb_jours_total
            scores[mot] = nb / (moyenne_par_jour + 1)       # combien de fois plus que d'habitude
    # On trie les mots du score le plus élevé au plus faible (à égalité, par ordre alphabétique)
    scores = pd.Series(scores).sort_index().sort_values(ascending=False, kind="stable")
    return list(scores.index[:combien])

# Choisir les titres les plus représentatifs : ceux qui contiennent le plus de mots-clés de l'événement (sans garder deux fois le même titre)
def titres_representatifs(titres_du_jour, mots_cles, combien=3):
    titres_uniques = titres_du_jour.drop_duplicates()
    nb_mots_cles = []
    for titre in titres_uniques:
        nb = 0
        for mot in set(decouper_en_mots(titre)):
            if mot in mots_cles:
                nb = nb + 1
        nb_mots_cles.append(nb)
    tableau = pd.DataFrame({"titre": titres_uniques.values, "nb_mots_cles": nb_mots_cles})
    tableau = tableau.sort_values("nb_mots_cles", ascending=False)
    return " | ".join(tableau["titre"].head(combien))


# 7. Construction du tableau des événements 

def construire_events(base, pics):
    """Une ligne par événement, classée de l'événement le plus intense au moins intense."""
    # Fréquence de chaque mot sur toute la base
    compteur_global = compter_mots(base["titre"])
    nb_jours_total = base["date"].nunique()

    lignes = []
    for numero, groupe in pics.groupby("evenement"):
        jour_max = groupe["nb_articles"].idxmax()               # le jour le plus intense
        titres_du_jour = base.loc[base["date"] == jour_max, "titre"]
        mots_cles = mots_caracteristiques(titres_du_jour, compteur_global, nb_jours_total)

        lignes.append({
            "date_pic": jour_max.date(),
            "nb_articles_pic": groupe["nb_articles"].max(),
            "niveau_habituel": round(groupe.loc[jour_max, "habituel"], 1),
            "ratio": round(groupe["ratio"].max(), 2),
            "mots_cles": ", ".join(mots_cles),
            "exemples_titres": titres_representatifs(titres_du_jour, mots_cles),
        })

    events = pd.DataFrame(lignes)

    # Classement : de l'événement le plus intense au moins intense
    events = events.sort_values("ratio", ascending=False).reset_index(drop=True)
    events.insert(0, "rang", events.index + 1)
    return events


# 8. Enregistrement et résultat dans le terminal 

def enregistrer_events(events, fichier_events=FICHIER_EVENTS):
    """Enregistre le tableau des événements dans outputs/tables/ et affiche les 15 plus gros."""
    fichier_events.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(fichier_events, index=False, encoding="utf-8-sig")

    print()
    print("Nombre d'événements détectés :", len(events))
    print()
    print("Les 15 plus gros événements :")
    print(events[["rang", "date_pic", "nb_articles_pic", "ratio", "mots_cles"]]
          .head(15).to_string(index=False))
    print()
    print("Fichier enregistré :", fichier_events)


# 9. Graphique de contrôle 
# Courbe du nombre d'articles par jour, avec un point rouge sur chaque événement.

def tracer_events(jours, events, fichier_graphique=FICHIER_GRAPHIQUE):
    """Enregistre le graphique des articles par jour et des événements dans outputs/figures/."""
    fig = plt.figure(figsize=(14, 5))
    plt.plot(jours.index, jours["nb_articles"], linewidth=0.6, color="grey",
             label="Articles politiques par jour")
    dates_pics = pd.to_datetime(events["date_pic"])
    plt.scatter(dates_pics, events["nb_articles_pic"], color="red", s=15,
                label="Événements détectés")
    plt.title("Articles politiques France Info par jour et événements détectés")
    plt.ylabel("Nombre d'articles")
    plt.legend()
    plt.tight_layout()
    fichier_graphique.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fichier_graphique, dpi=150)
    print("Graphique enregistré :", fichier_graphique)
    return fig
