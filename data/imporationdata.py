#Dans ce script, on importe les données

from __future__ import annotations

import json
from datetime import date

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
COUNTRIES = ["FR", "DE", "IT", "ES"]
RAW_DIR = DATA_DIR / "raw"
START_DATE = pd.Timestamp("2016-01-01")


HEADERS = {"User-Agent": "Mozilla/5.0 (projet ENSAE - spreads souverains)"}
TIMEOUT = 60

CNBC_SYMBOLS = {c: f"{c}10Y-{c}" for c in COUNTRIES}
CNBC_URL = (
    "https://ts-api.cnbc.com/harmony/app/bars/{symbol}/1D/"
    "{start}000000/{end}000000/adjusted/EST5EDT.json"
)
BUNDESBANK_URL = (
    "https://api.statistiken.bundesbank.de/rest/download/BBSIS/"
    "D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv&lang=en"
)
EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "irt_lt_mcby_m/M.MCBY.{geos}?format=SDMX-CSV&startPeriod={start}"
)


def _get(url: str) -> requests.Response:
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response



# CNBC

def fetch_cnbc_country(country: str, refresh: bool = False) -> pd.Series:
    """Rendement à 10 ans journalier (clôture, en %) d'un pays."""
    cache = RAW_DIR / f"cnbc_{country}10Y.json"
    if refresh or not cache.exists():
        url = CNBC_URL.format(
            symbol=CNBC_SYMBOLS[country],
            start=START_DATE.strftime("%Y%m%d"),
            end=date.today().strftime("%Y%m%d"),
        )
        cache.write_text(_get(url).text)

    bars = json.loads(cache.read_text())["barData"]["priceBars"]
    series = pd.Series(
        {pd.Timestamp(bar["tradeTime"][:8]): float(bar["close"]) for bar in bars},
        name=country,
    )
    return series.sort_index()


def fetch_cnbc(refresh: bool = False) -> pd.DataFrame:
    """Tableau (dates x pays) des rendements à 10 ans CNBC, en %."""
    frame = pd.concat(
        [fetch_cnbc_country(c, refresh=refresh) for c in COUNTRIES], axis=1
    )
    frame.index.name = "date"
    return frame


# Bundesbank

def fetch_bundesbank(refresh: bool = False) -> pd.Series:
    """Taux à 10 ans des titres fédéraux allemands (Svensson), en %."""
    cache = RAW_DIR / "bundesbank_10y.csv"
    if refresh or not cache.exists():
        cache.write_bytes(_get(BUNDESBANK_URL).content)

    raw = pd.read_csv(
        cache,
        skiprows=9,
        header=None,
        names=["date", "value", "flag"],
        na_values=["."],
        encoding="utf-8-sig",
    )
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    series = raw.dropna(subset=["date", "value"]).set_index("date")["value"]
    series = pd.to_numeric(series, errors="coerce").dropna()
    return series.loc[START_DATE:].rename("DE_bundesbank")


# Données Eurostat

def fetch_eurostat_monthly(refresh: bool = False) -> pd.DataFrame:
    """Taux de convergence à 10 ans (moyennes mensuelles), en %."""
    cache = RAW_DIR / "eurostat_irt_lt_mcby_m.csv"
    if refresh or not cache.exists():
        url = EUROSTAT_URL.format(
            geos="+".join(COUNTRIES), start=START_DATE.strftime("%Y-%m")
        )
        cache.write_bytes(_get(url).content)

    raw = pd.read_csv(cache)
    frame = raw.pivot(index="TIME_PERIOD", columns="geo", values="OBS_VALUE")
    frame.index = pd.PeriodIndex(frame.index, freq="M")
    frame.index.name = "mois"
    return frame[COUNTRIES]


# Appel des fonctions pour récupérer les données

RAW_DIR.mkdir(parents=True, exist_ok=True)
fetch_cnbc(refresh=True)
fetch_bundesbank(refresh=True)
fetch_eurostat_monthly(refresh=True)