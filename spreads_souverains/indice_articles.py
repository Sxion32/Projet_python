# Transformation des titres France Info en un indice quotidien d'actualité politique, puis mesure de son lien avec l'ampleur des variations du spread français
import re

import matplotlib.pyplot as plt
import pandas as pd

from spreads_souverains import config
from spreads_souverains.controles import save_figure
from spreads_souverains.descriptives import ligne_dissolution

MOTS_INDICE = ["censur", "49.3", "dissolution", "premier ministre", "première ministre"]

FENETRE = 60  # séances utilisées pour la volatilité habituelle, comme dans l'étude d'événements
CLASSES = [-1, 0, 2, 5, 1000]  # bornes des classes de l'indice : 0, 1-2, 3-5, 6 et plus
NOMS_CLASSES = ["0", "1-2", "3-5", "6 et plus"]


def charger_titres():
    # Lit les titres politiques France Info
    return pd.read_csv(config.TITRES_POLITIQUES_FILE, encoding="utf-8-sig", parse_dates=["date"])


def construire_indice(titres, calendrier):
    # Indice quotidien : nombre de titres et nombre de titres contenant un mot de MOTS_INDICE.

    titres = titres[(titres["date"] >= calendrier[0]) & (titres["date"] <= calendrier[-1])].copy()

    motif = "|".join(re.escape(mot) for mot in MOTS_INDICE)  # re.escape protège le point de "49.3"
    titres["contient_mot"] = titres["titre"].str.contains(motif, case=False, regex=True)
    titres["seance"] = calendrier[calendrier.searchsorted(titres["date"])]

    indice = titres.groupby("seance").agg(
        nb_titres=("titre", "size"),
        nb_mots=("contient_mot", "sum"),
    )

    # Séances sans aucun titre : 0, sur la période couverte par les titres
    seances = calendrier[(calendrier >= titres["date"].min()) & (calendrier <= titres["date"].max())]
    indice = indice.reindex(seances, fill_value=0)
    indice.index.name = "date"

    # Part des titres qui contiennent un mot de l'indice (corrige la taille variable de l'archive)
    indice["part_mots"] = 100 * indice["nb_mots"] / indice["nb_titres"].where(indice["nb_titres"] > 0)
    return indice


def variations_absolues(panel):
    # Ampleur des variations quotidiennes, en pb et rapportées à la volatilité habituelle (|z|).
    series = {
        "FR": panel["s_FR"],
        "IT": panel["s_IT"],
        "ES": panel["s_ES"],
        "FR_ES": panel["s_FR"] - panel["s_ES"],  # le taux allemand s'annule
    }
    resultat = pd.DataFrame(index=panel.index)
    for nom, serie in series.items():
        variation = serie.diff()
        resultat[f"var_{nom}"] = variation.abs()
        if nom in ["FR", "FR_ES"]:
            volatilite = variation.rolling(FENETRE).std().shift(1)  # 60 séances avant le jour
            resultat[f"z_{nom}"] = (variation / volatilite).abs()
    return resultat


def tableau_correlations(indice, variations, debut=None, fin=None):
    #Corrélations entre l'indice (nb_mots) et chaque variation, le jour même (J) et le lendemain (J+1).
    donnees = indice.join(variations, how="inner")
    if debut is not None:
        donnees = donnees.loc[debut:]
    if fin is not None:
        donnees = donnees.loc[:fin]

    lignes = []
    for colonne in variations.columns:
        for decalage, nom_decalage in [(0, "J"), (1, "J+1")]:
            variation = donnees[colonne].shift(-decalage)  # J+1 : variation de la séance suivante
            lignes.append({
                "variation": colonne,
                "jour": nom_decalage,
                "pearson": donnees["nb_mots"].corr(variation),
                "spearman": donnees["nb_mots"].corr(variation, method="spearman"),
            })
    return pd.DataFrame(lignes).set_index(["variation", "jour"]).round(3)


def variations_par_classe(indice, variations):
    # Moyenne des variations selon le nombre de titres de l'indice ce jour-là (classes 0, 1-2, 3-5, 6+).
    donnees = indice.join(variations, how="inner")
    classe = pd.cut(donnees["nb_mots"], CLASSES, labels=NOMS_CLASSES)
    tableau = donnees.groupby(classe, observed=True)[["var_FR", "z_FR", "z_FR_ES"]].mean()
    tableau["nb_seances"] = donnees.groupby(classe, observed=True).size()
    tableau.index.name = "titres_indice"
    return tableau.round(2)


def enregistrer_indice(indice, correlations):
    # Enregistre l'indice et le tableau des corrélations.
    config.TABLE_DIR.mkdir(parents=True, exist_ok=True)
    indice.to_csv(config.TABLE_DIR / "indice_articles.csv", float_format="%.2f")
    correlations.to_csv(config.TABLE_DIR / "correlations_indice_spreads.csv")
    print("Fichiers enregistrés dans", config.TABLE_DIR)


def tracer_indice(indice, variations):
    # Figure 12 : indice d'articles et ampleur des variations du spread français, en moyenne glissante.
    fig, (ax_haut, ax_bas) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    ax_haut.bar(indice.index, indice["nb_mots"], width=1, color="#c9c8c1", label="Par séance")
    ax_haut.plot(indice["nb_mots"].rolling(FENETRE).mean(), color=config.COLORS["FR"],
                 linewidth=1.5, label=f"Moyenne sur {FENETRE} séances")
    ligne_dissolution(ax_haut)
    ax_haut.set_title("Titres contenant « censure », « 49.3 », « dissolution » ou « Premier ministre »")
    ax_haut.set_ylabel("Nombre de titres")
    ax_haut.grid(alpha=0.3)
    ax_haut.legend()

    ax_bas.plot(variations["var_FR"].rolling(FENETRE).mean(), color=config.COLORS["FR"],
                linewidth=1.5, label="|Δs_FR| (FR - DE)")
    ax_bas.plot(variations["var_FR_ES"].rolling(FENETRE).mean(), color=config.COLORS["ES"],
                linewidth=1.5, label="|Δ(s_FR - s_ES)| (FR - ES)")
    ligne_dissolution(ax_bas)
    ax_bas.set_title(f"Ampleur des variations quotidiennes, moyenne sur {FENETRE} séances")
    ax_bas.set_ylabel("Points de base")
    ax_bas.grid(alpha=0.3)
    ax_bas.legend()

    fig.suptitle("Figure 12 : indice d'actualité politique et variations du spread français")
    fig.tight_layout()
    save_figure(fig, "12_indice_articles")
    return fig


def tracer_classes(tableau):
    # Figure 13 : |z| moyen du spread français et de l'écart France - Espagne selon la classe de l'indice.
    positions = range(len(tableau))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar([p - 0.2 for p in positions], tableau["z_FR"], width=0.4,
           color=config.COLORS["FR"], label="|z| spread FR - DE")
    ax.bar([p + 0.2 for p in positions], tableau["z_FR_ES"], width=0.4,
           color=config.COLORS["ES"], label="|z| écart FR - ES")
    ax.set_xticks(list(positions))
    ax.set_xticklabels([f"{classe}\n({n} séances)" for classe, n in zip(tableau.index, tableau["nb_seances"])])
    ax.set_xlabel("Nombre de titres de l'indice ce jour-là")
    ax.set_ylabel("|z| moyen")
    ax.set_title("Figure 13 : ampleur des variations selon l'actualité politique du jour")
    ax.grid(alpha=0.3, axis="y")
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "13_variations_par_classe")
    return fig
