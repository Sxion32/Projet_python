# Exécute toute la chaîne du projet, de la collecte des données aux figures.

import matplotlib.pyplot as plt

from import_cleaning import cleaning, import_titres, importation_donnees, nettoyage_titres
from scripts import detect_ev, graph_nb_art_jour
from spreads_souverains import config, controles, descriptives, indice_articles, panel


def importer_taux():
    # 1. Taux à 10 ans bruts : CNBC, Bundesbank et Eurostat (dans data/raw/).
    importation_donnees.fetch_cnbc(config.REFRESH)
    importation_donnees.fetch_bundesbank(config.REFRESH)
    importation_donnees.fetch_eurostat_monthly(config.REFRESH)


def nettoyer_taux():
    # 2. Nettoyage des taux et enregistrement dans data/cleaned/.
    cnbc, cnbc_filled = cleaning.clean_yields(cleaning.retirer_anomalies(cleaning.load_cnbc()))
    cleaning.check_daily(cnbc, cnbc_filled, "CNBC 10 ans")

    bundesbank, bundesbank_filled = cleaning.clean_yields(cleaning.load_bundesbank())
    cleaning.check_daily(bundesbank, bundesbank_filled, "Bundesbank DE 10 ans")

    eurostat = cleaning.clean_monthly(cleaning.load_eurostat())
    cleaning.check_monthly(eurostat, "Eurostat 10 ans (mensuel)")

    cleaning.save_cleaned(cnbc, bundesbank, eurostat)
    return cnbc


def construire_panel(cnbc):
    #3. Spreads contre l'Allemagne, enregistrés dans data/yields.csv.
    tableau = panel.build_panel(cnbc, export=True)
    print(tableau.tail())
    print("Spread FR le 07/06/2024 :", round(tableau.loc["2024-06-07", "s_FR"], 2), "pb")
    return tableau


def importer_titres():
    #4. Titres France Info via Media Cloud (plusieurs heures), puis filtrage des titres politiques.
    if config.REFRESH or not import_titres.FICHIER_SORTIE.exists():
        annuaire, recherche = import_titres.connexion_mediacloud()
        ids_franceinfo = import_titres.trouver_ids_franceinfo(annuaire)
        import_titres.collecter_titres(recherche, ids_franceinfo)
        titres = import_titres.dedoublonner_titres()
        if titres is not None:
            import_titres.afficher_statistiques(titres)

    nettoyage_titres.filtrer_titres_politiques()
    graph_nb_art_jour.tracer_articles_par_jour()


def detecter_evenements():
    #5. Pics d'articles politiques : outputs/tables/events.csv et outputs/figures/events_graphique.png.
    # La date de réaction du marché est recalculée à chaque lecture (spreads_souverains/events.py).
    base = detect_ev.charger_titres()
    jours = detect_ev.reperer_pics(detect_ev.compter_articles_par_jour(base))
    pics = detect_ev.regrouper_pics(jours)
    events = detect_ev.construire_events(base, pics)
    detect_ev.enregistrer_events(events)
    detect_ev.tracer_events(jours, events)


def controler_donnees():
    #6. Fiabilité de CNBC et grosses variations des spreads (figures dans outputs/figures/).
    cnbc, bundesbank, eurostat = controles.charger_donnees_nettoyees()
    controles.comparer_eurostat(cnbc, eurostat)
    controles.tracer_ecarts_eurostat(cnbc, eurostat)
    controles.comparer_bundesbank(cnbc, bundesbank)
    controles.tracer_nuage_bundesbank(cnbc, bundesbank)
    controles.compter_jours_combles()

    spreads = controles.calculer_spreads(cnbc)
    controles.confronter_variations_evenements(spreads)
    controles.histogramme_spread_fr(spreads)



def analyser_indice_articles():
    #7. Indice quotidien d'articles politiques et corrélation avec les variations du spread français.
    tableau = descriptives.charger_panel()
    indice = indice_articles.construire_indice(indice_articles.charger_titres(), tableau.index)
    variations = indice_articles.variations_absolues(tableau)
    correlations = indice_articles.tableau_correlations(indice, variations)
    print(correlations)
    indice_articles.enregistrer_indice(indice, correlations)
    indice_articles.tracer_indice(indice, variations)
    indice_articles.tracer_classes(indice_articles.variations_par_classe(indice, variations))


if __name__ == "__main__":
    importer_taux()
    cnbc = nettoyer_taux()
    construire_panel(cnbc)
    detecter_evenements()
    controler_donnees()
    importer_titres()
    analyser_indice_articles()
    plt.close("all")