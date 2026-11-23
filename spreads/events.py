"""Date de réaction du marché à un événement (étape 10).

La date d'un événement n'est pas forcément un jour de marché : une annonce un
dimanche soir ou après la clôture ne peut se voir dans les taux qu'à la séance
suivante. On appelle cette séance la date de réaction.
"""

import pandas as pd

from spreads import config


def load_events(path=config.DATA_DIR / "events.csv"):
    """Lit la base d'événements, avec la colonne "date" convertie en dates.

    Exemple : events = load_events()
    """
    return pd.read_csv(path, parse_dates=["date"])


def reaction_date(date, apres_cloture, calendrier):
    """Renvoie la première séance où le marché peut réagir à l'événement.

    Si apres_cloture vaut 1, on part du lendemain ; puis on prend la première
    séance du calendrier (index de dates triées) supérieure ou égale à cette date.
    Renvoie NaT si l'événement est après la dernière séance disponible.
    Exemple : reaction_date(pd.Timestamp("2024-06-09"), 1, panel.index)
    """
    if apres_cloture == 1:
        date = date + pd.Timedelta(days=1)

    seances_suivantes = calendrier[calendrier >= date]
    if len(seances_suivantes) == 0:
        return pd.NaT
    return seances_suivantes[0]


def add_reaction_dates(events, calendrier):
    """Ajoute à la base d'événements la colonne "date_reaction".

    Exemple : events = add_reaction_dates(events, panel.index)
    """
    events = events.copy()  # on ne modifie pas le tableau d'origine
    events["date_reaction"] = events.apply(
        lambda ligne: reaction_date(ligne["date"], ligne["apres_cloture"], calendrier),
        axis=1,
    )
    return events
