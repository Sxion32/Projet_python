"""Lecture hors ligne des taux à 10 ans enregistrés dans data/raw/.

Chaque fonction lit un fichier brut écrit par un script de scripts/ et renvoie une
Series pandas : index de dates (DatetimeIndex), valeurs en % par an, triée, sans
valeur manquante. Aucune fonction de ce module n'accède à Internet.
"""

import csv
import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
START = "2016-01-01"


def load_cnbc(symbol, keep_weekends=False):
    """Lit les clôtures quotidiennes d'un symbole CNBC et retire les week-ends.

    Paramètres
    ----------
    symbol : str, symbole CNBC, par exemple "FR10Y-FR".
    keep_weekends : bool, True pour garder les barres du samedi et du dimanche.
        Utile au diagnostic de l'heure de relevé : si CNBC date certaines journées
        avec un jour de retard, la barre du samedi porte la séance du vendredi.

    Retourne
    --------
    pd.Series nommée d'après le symbole : date -> taux de clôture en %.

    Hypothèses
    ----------
    - La date est celle de la barre CNBC, découpée à l'heure de New York (EST5EDT).
    - Les barres datées d'un samedi ou d'un dimanche sont retirées : le marché
      européen des emprunts d'État est fermé ces jours-là (règle du journal, D7).

    Exemple
    -------
    >>> load_cnbc("DE10Y-DE").loc["2024-06-10"]
    2.675
    """
    with open(RAW_DIR / "cnbc" / f"{symbol}.json", encoding="utf-8") as file:
        bars = json.load(file)["barData"]["priceBars"]
    table = pd.DataFrame(bars)
    dates = pd.to_datetime(table["tradeTime"].str[:8], format="%Y%m%d")
    closes = pd.Series(table["close"].astype(float).values, index=dates, name=symbol)
    if not keep_weekends:
        is_weekday = closes.index.dayofweek < 5
        closes = closes[is_weekday]
    return closes.sort_index().loc[START:]


def load_eurostat(country):
    """Lit la série quotidienne Eurostat irt_lt_mcby_d d'un pays (copie DBnomics).

    Paramètres
    ----------
    country : str, code pays à deux lettres, par exemple "FR".

    Retourne
    --------
    pd.Series nommée "Eurostat <pays>" : date -> taux en %, jours sans valeur retirés.

    Hypothèses
    ----------
    - DBnomics note "NA" les jours sans valeur ; nous les retirons.
    - La série s'arrête en avril 2025 (journal, D4).

    Exemple
    -------
    >>> load_eurostat("FR").index.max()
    Timestamp('2025-03-31 00:00:00')
    """
    with open(RAW_DIR / "eurostat" / f"{country}.json", encoding="utf-8") as file:
        doc = json.load(file)["series"]["docs"][0]
    values = pd.to_numeric(pd.Series(doc["value"]), errors="coerce")
    rates = pd.Series(values.values, index=pd.to_datetime(doc["period"]), name=f"Eurostat {country}")
    return rates.dropna().sort_index().loc[START:]


BDE_MONTHS = {"ENE": 1, "FEB": 2, "MAR": 3, "ABR": 4, "MAY": 5, "JUN": 6,
              "JUL": 7, "AGO": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DIC": 12}


def load_banque_de_france():
    """Lit le TEC 10 quotidien de la Banque de France (copie DBnomics).

    Retourne
    --------
    pd.Series nommée "Banque de France" : date -> taux en %, jours sans valeur retirés.

    Hypothèse
    ---------
    Le TEC 10 est le taux d'une OAT fictive d'échéance exactement 10 ans, interpolé
    entre les OAT cotées. Sa méthode diffère de celle d'Eurostat (journal, D5).
    """
    with open(RAW_DIR / "nationales" / "banque_de_france.json", encoding="utf-8") as file:
        doc = json.load(file)["series"]["docs"][0]
    values = pd.to_numeric(pd.Series(doc["value"]), errors="coerce")
    rates = pd.Series(values.values, index=pd.to_datetime(doc["period"]), name="Banque de France")
    return rates.dropna().sort_index().loc[START:]


def load_bundesbank():
    """Lit le rendement quotidien à 10 ans des titres fédéraux publié par la Bundesbank.

    Retourne
    --------
    pd.Series nommée "Bundesbank" : date -> taux en %, jours sans valeur retirés.

    Hypothèses
    ----------
    - Le CSV commence par des lignes de métadonnées ; les lignes de données sont celles
      qui commencent par une année (quatre chiffres).
    - Un point "." signale l'absence de valeur.
    - Le taux est lu sur une courbe estimée, pas sur un titre coté (journal, D5).
    """
    with open(RAW_DIR / "nationales" / "bundesbank.csv", encoding="utf-8-sig") as file:
        lines = file.read().splitlines()
    rows = [line.split(",")[:2] for line in lines if line[:4].isdigit()]
    table = pd.DataFrame(rows, columns=["date", "value"])
    values = pd.to_numeric(table["value"].replace(".", None), errors="coerce")
    rates = pd.Series(values.values, index=pd.to_datetime(table["date"]), name="Bundesbank")
    return rates.dropna().sort_index().loc[START:]


def load_banco_de_espana():
    """Lit le taux quotidien à 10 ans des obligations de l'État espagnol (Banco de España, TI 1.3).

    Retourne
    --------
    pd.Series nommée "Banco de España" : date -> taux en %, jours sans valeur retirés.

    Hypothèses
    ----------
    - Le fichier est encodé en latin-1 et regroupe plusieurs séries en colonnes ; la
      bonne colonne est repérée par sa description ("10 Años" et "obligaciones").
    - Les dates s'écrivent avec un mois abrégé en espagnol ("30 SEP 2026").
    - "_" signale l'absence de valeur.
    """
    with open(RAW_DIR / "nationales" / "banco_de_espana.csv", encoding="latin-1") as file:
        rows = list(csv.reader(file))
    descriptions = next(row for row in rows if row and row[0].startswith("DESCRIPCIÓN DE LA SERIE"))
    column = next(i for i, text in enumerate(descriptions) if "10 Años" in text and "obligaciones" in text.lower())
    data = [row for row in rows if row and row[0][:1].isdigit()]
    dates = []
    for row in data:
        day, month, year = row[0].split()
        dates.append(f"{year}-{BDE_MONTHS[month.upper()]:02d}-{int(day):02d}")
    values = pd.to_numeric(pd.Series([row[column] for row in data]).replace({"_": None, "": None}), errors="coerce")
    rates = pd.Series(values.values, index=pd.to_datetime(dates), name="Banco de España")
    return rates.dropna().sort_index().loc[START:]
