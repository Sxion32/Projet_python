# Dans ce script, on nettoie les données brutes (data/raw) et on les enregistre dans data/cleaned

import json
from pathlib import Path

import pandas as pd


# définition des chemins d'accès 
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"          # données brutes
CLEANED_DIR = ROOT / "data" / "cleaned"  # données nettoyées

COUNTRIES = ["FR", "DE", "IT", "ES"] 
START_DATE = pd.Timestamp("2016-01-01")
FFILL_LIMIT = 2  # on comble au plus 2 jours ouvrés manquants d'affilée


# 1. Lecture des données brutes.

def load_cnbc():
    """Tableau (dates x pays) des rendements à 10 ans CNBC, en %."""
    series = []
    for country in COUNTRIES:
        path = RAW_DIR / f"cnbc_{country}10Y.json"
        bars = json.loads(path.read_text())["barData"]["priceBars"] #Récupération des données sous forme d'une liste de dictionnaires

        # On ne garde que la date et le taux de fin de journée
        dates = [pd.Timestamp(bar["tradeTime"][:8]) for bar in bars]  # "20160104000000" -> 2016-01-04
        values = [float(bar["close"]) for bar in bars]                # le taux de fin de journée est converti en float
        series.append(pd.Series(values, index=dates, name=country))   # Rajout du pays à la série

    frame = pd.concat(series, axis=1)  # une colonne par pays
    frame = frame.sort_index()
    frame.index.name = "date"
    return frame


def load_bundesbank():
    """Tableau (dates x 1 colonne) du taux à 10 ans allemand de la Bundesbank, en %."""
    raw = pd.read_csv(
        RAW_DIR / "bundesbank_10y.csv",
        skiprows=9,                       # les 9 premières lignes sont des métadonnées
        header=None,
        names=["date", "value", "flag"],
        na_values=["."],                  # "." signifie "pas de valeur"
        encoding="utf-8-sig",
    )
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw = raw.dropna(subset=["date"])     # on enlève les lignes sans date valide

    frame = raw.set_index("date")[["value"]]
    frame.columns = ["DE_bundesbank"]
    return frame


def load_eurostat():
    """Tableau (mois x pays) des taux de convergence à 10 ans Eurostat, en %."""
    raw = pd.read_csv(RAW_DIR / "eurostat_irt_lt_mcby_m.csv")
    #  changement de format : une ligne par pays et par mois -> une colonne par pays
    frame = raw.pivot(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    frame.index.name = "mois"  # les mois restent au format texte "AAAA-MM"
    frame.columns.name = None
    return frame[COUNTRIES]


# 2. Nettoyage

def clean_yields(raw):
    """Nettoie un tableau journalier de taux.

    Étapes :
    1. on garde les jours ouvrés (lundi à vendredi) à partir de START_DATE ;
    2. on comble les trous de 1 ou 2 jours avec la dernière valeur connue ;
    3. Suppression des lignes encore incomplètes.

    Renvoie le tableau nettoyé et le nombre de jours comblés par colonne.
    """
    frame = raw.loc[START_DATE:]

    # 1. jours ouvrés uniquement
    frame = frame[frame.index.dayofweek < 5]

    # On remet tous les jours ouvrés du calendrier : un jour absent pour toutes les colonnes n'a pas de ligne, et ffill ne pourrait pas le combler.
    all_business_days = pd.bdate_range(frame.index.min(), frame.index.max())
    frame = frame.reindex(all_business_days)
    frame.index.name = "date"

    # étape 2 : on comble les trous courts et on compte le nombre de trous comblés (ou pas)
    missing_before = frame.isna().sum()
    frame = frame.ffill(limit=FFILL_LIMIT)
    missing_after = frame.isna().sum()
    n_filled = missing_before - missing_after

    # étape 3 : on supprime les lignes où il manque encore une valeur
    frame = frame.dropna()

    return frame, n_filled


def clean_monthly(raw):
    """Nettoie le tableau mensuel Eurostat : période d'étude et mois complets."""
    frame = raw.sort_index()
    frame = frame.loc[START_DATE.strftime("%Y-%m"):]  # à partir de "2016-01"
    frame = frame.dropna()
    return frame


# 3. Fonctions de vérification

def check_daily(frame, n_filled, name):
    """Vérifie un tableau journalier nettoyé et affiche un résumé."""
    n_weekend = (frame.index.dayofweek >= 5).sum()
    n_missing = frame.isna().sum().sum()
    assert n_weekend == 0, f"{name} : il reste {n_weekend} samedis ou dimanches"
    assert n_missing == 0, f"{name} : il reste {n_missing} valeurs manquantes"

    print(f"\n   {name} : aucun samedi ni dimanche, aucune valeur manquante")
    print(f"   {len(frame)} jours ouvrés, du {frame.index.min().date()} au {frame.index.max().date()}")
    print("   Jours comblés par ffill :")
    for column in frame.columns:
        print(f"   - {column} : {n_filled[column]}")


def check_monthly(frame, name):
    """Vérifie le tableau mensuel nettoyé et affiche un résumé."""
    n_missing = frame.isna().sum().sum()
    assert n_missing == 0, f"{name} : il reste {n_missing} valeurs manquantes"

    expected = pd.period_range(frame.index.min(), frame.index.max(), freq="M").astype(str)
    missing_months = [month for month in expected if month not in frame.index]

    print(f"\n   {name} : {len(frame)} mois, du {frame.index.min()} au {frame.index.max()}")
    print(f"   Mois manquants : {missing_months if missing_months else 'aucun'}")



# 4. Programme principal

CLEANED_DIR.mkdir(parents=True, exist_ok=True)

cnbc, cnbc_filled = clean_yields(load_cnbc())
check_daily(cnbc, cnbc_filled, "CNBC 10 ans")

bundesbank, bundesbank_filled = clean_yields(load_bundesbank())
check_daily(bundesbank, bundesbank_filled, "Bundesbank DE 10 ans")

eurostat = clean_monthly(load_eurostat())
check_monthly(eurostat, "Eurostat 10 ans (mensuel)")

# enregistrement (4 à décimales près)
cnbc.to_csv(CLEANED_DIR / "yields_10y_cnbc_daily.csv", float_format="%.4f")
bundesbank.to_csv(CLEANED_DIR / "de10y_bundesbank_daily.csv", float_format="%.4f")
eurostat.to_csv(CLEANED_DIR / "yields_10y_eurostat_monthly.csv", float_format="%.4f")
print(f"\nFichiers enregistrés dans {CLEANED_DIR}")

