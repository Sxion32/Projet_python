"""Tests de la date de réaction du marché.

Lancement depuis la racine du dépôt : python3 -m tests.test_events
(ou pytest, une fois installé).
"""

import pandas as pd

from spreads_souverains.events import add_reaction_dates, reaction_date

# Séances du lundi 3 au vendredi 14 juin 2024 (jours ouvrés seulement).
CALENDRIER = pd.bdate_range("2024-06-03", "2024-06-14")


def test_pic_un_dimanche():
    # Pic d'articles le dimanche 9 juin 2024 : première séance le lundi 10 juin.
    assert reaction_date(pd.Timestamp("2024-06-09"), CALENDRIER) == pd.Timestamp("2024-06-10")


def test_pic_un_jour_de_marche():
    # Pic d'articles le mardi 4 juin : réaction le jour même.
    assert reaction_date(pd.Timestamp("2024-06-04"), CALENDRIER) == pd.Timestamp("2024-06-04")


def test_apres_la_derniere_seance():
    # Aucune séance après le 14 juin dans ce calendrier : pas de date de réaction.
    assert pd.isna(reaction_date(pd.Timestamp("2024-06-20"), CALENDRIER))


def test_ajout_de_la_colonne():
    events = pd.DataFrame({"date_pic": pd.to_datetime(["2024-06-09", "2024-06-04"])})
    resultat = add_reaction_dates(events, CALENDRIER)
    assert list(resultat["date_reaction"]) == [pd.Timestamp("2024-06-10"), pd.Timestamp("2024-06-04")]
    assert "date_reaction" not in events.columns  # le tableau d'origine n'est pas modifié


if __name__ == "__main__":
    test_pic_un_dimanche()
    test_pic_un_jour_de_marche()
    test_apres_la_derniere_seance()
    test_ajout_de_la_colonne()
    print("Les 4 tests passent.")
