"""Tests de la date de réaction du marché (étape 10).

Lancement depuis la racine du dépôt : python3 -m tests.test_events
(ou pytest, une fois installé).
"""

import pandas as pd

from spreads.events import add_reaction_dates, reaction_date

# Séances du lundi 3 au vendredi 14 juin 2024 (jours ouvrés seulement).
CALENDRIER = pd.bdate_range("2024-06-03", "2024-06-14")


def test_dissolution_du_dimanche():
    # Annonce le dimanche 9 juin 2024 au soir : première séance le lundi 10 juin.
    assert reaction_date(pd.Timestamp("2024-06-09"), 1, CALENDRIER) == pd.Timestamp("2024-06-10")


def test_vendredi_apres_cloture():
    # Annonce le vendredi 7 juin après la clôture : réaction le lundi 10 juin.
    assert reaction_date(pd.Timestamp("2024-06-07"), 1, CALENDRIER) == pd.Timestamp("2024-06-10")


def test_jour_de_marche_avant_cloture():
    # Annonce le mardi 4 juin avant la clôture : réaction le jour même.
    assert reaction_date(pd.Timestamp("2024-06-04"), 0, CALENDRIER) == pd.Timestamp("2024-06-04")


def test_apres_la_derniere_seance():
    # Aucune séance après le 14 juin dans ce calendrier : pas de date de réaction.
    assert pd.isna(reaction_date(pd.Timestamp("2024-06-20"), 0, CALENDRIER))


def test_ajout_de_la_colonne():
    events = pd.DataFrame({
        "date": pd.to_datetime(["2024-06-09", "2024-06-04"]),
        "apres_cloture": [1, 0],
    })
    resultat = add_reaction_dates(events, CALENDRIER)
    assert list(resultat["date_reaction"]) == [pd.Timestamp("2024-06-10"), pd.Timestamp("2024-06-04")]
    assert "date_reaction" not in events.columns  # le tableau d'origine n'est pas modifié


if __name__ == "__main__":
    test_dissolution_du_dimanche()
    test_vendredi_apres_cloture()
    test_jour_de_marche_avant_cloture()
    test_apres_la_derniere_seance()
    test_ajout_de_la_colonne()
    print("Les 5 tests passent.")
