# Date de réaction du marché à un événement.
# Un événement détecté par scripts/detect_ev.py est daté par son jour de pic d'articles ("date_pic"). 
import pandas as pd
from spreads_souverains import config


def load_events(path=config.EVENTS_FILE):
    # Lit outputs/tables/events.csv, avec la colonne "date_pic" convertie en dates.
    return pd.read_csv(path, parse_dates=["date_pic"], encoding="utf-8-sig")


def reaction_date(date, calendrier):
    # Première séance du calendrier (dates triées) à partir de date, NaT s'il n'y en a pas.
    seances_suivantes = calendrier[calendrier >= pd.Timestamp(date)]
    if len(seances_suivantes) == 0:
        return pd.NaT
    return seances_suivantes[0]


def add_reaction_dates(events, calendrier):
    # Ajoute la colonne "date_reaction" au tableau des événements.
    events = events.copy()  # on ne modifie pas le tableau d'origine
    events["date_reaction"] = [reaction_date(date, calendrier) for date in events["date_pic"]]
    return events
