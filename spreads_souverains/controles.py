# Dans ce script, on contrôle la qualité des données CNBC en les comparant
# à deux sources officielles : Eurostat (mensuel) et la Bundesbank (journalier),
# puis on étudie les valeurs manquantes et les valeurs aberrantes.

import json

import matplotlib.pyplot as plt
import pandas as pd

from spreads_souverains import config
from spreads_souverains.events import load_events


def save_figure(fig, filename):
    """Enregistre une figure en PNG dans outputs/figures/"""
    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIG_DIR / f"{filename}.png", dpi=150)


def charger_donnees_nettoyees():
    """Lit les taux nettoyés (data/cleaned/) : CNBC, Bundesbank et Eurostat."""
    cnbc = pd.read_csv(config.CLEANED_DIR / "yields_10y_cnbc_daily.csv", index_col=0, parse_dates=True)
    bundesbank = pd.read_csv(config.CLEANED_DIR / "de10y_bundesbank_daily.csv", index_col=0, parse_dates=True)
    eurostat = pd.read_csv(config.CLEANED_DIR / "yields_10y_eurostat_monthly.csv", index_col=0)
    eurostat.index = pd.to_datetime(eurostat.index)  # "2016-01" -> 2016-01-01
    return cnbc, bundesbank, eurostat


# CNBC contre Eurostat (mensuel)

def comparer_eurostat(cnbc, eurostat):
    """Affiche l'écart CNBC - Eurostat par pays et enregistre la figure 1."""
    # Moyenne mensuelle de CNBC ("MS" : un point par mois, daté du 1er)
    cnbc_monthly = cnbc.resample("MS").mean()

    # Écart CNBC - Eurostat par pays, en points de base
    gap_monthly = (cnbc_monthly - eurostat).dropna() * 100
    print("Écart CNBC - Eurostat (pb) :")
    print(pd.DataFrame({
        "ecart_moyen_pb": gap_monthly.mean(),
        "ecart_abs_moyen_pb": gap_monthly.abs().mean(),
        "ecart_abs_max_pb": gap_monthly.abs().max(),
    }).round(2))

    # Figure 1 : CNBC mensuel et Eurostat superposés, un graphique par pays
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    for ax, country in zip(axes.flatten(), config.COUNTRIES):
        ax.plot(cnbc_monthly[country], color=config.COLORS[country], label="CNBC (moyenne mensuelle)")
        ax.plot(eurostat[country], color="black", linestyle="--", linewidth=1, label="Eurostat")
        ax.set_title(country)
        ax.set_ylabel("Taux à 10 ans (%)")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Figure 1 : CNBC et Eurostat, moyennes mensuelles")
    fig.tight_layout()
    save_figure(fig, "1_cnbc_eurostat_mensuel")
    return fig


# CNBC contre Bundesbank (journalier, Bund allemand)

def comparer_bundesbank(cnbc, bundesbank):
    """Affiche les corrélations CNBC - Bundesbank sur le Bund et enregistre la figure 2."""
    # Les deux taux allemands côte à côte, jour par jour
    daily = pd.DataFrame({"cnbc": cnbc["DE"], "bundesbank": bundesbank["DE_bundesbank"]}).dropna()

    # Corrélations : en niveaux, puis en variations à 1 et 2 jours
    print("\nCorrélation CNBC - Bundesbank :")
    print("- niveaux :", round(daily["cnbc"].corr(daily["bundesbank"]), 3))
    for step in [1, 2]:
        changes = daily.diff(step).dropna()
        print(f"- variations à {step} jour(s) :", round(changes["cnbc"].corr(changes["bundesbank"]), 3))

    # Figure 2 : écart CNBC - Bundesbank dans le temps, en pb
    gap_daily = (daily["cnbc"] - daily["bundesbank"]) * 100
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(gap_daily, color=config.COLORS["DE"], linewidth=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Figure 2 : écart CNBC - Bundesbank sur le Bund à 10 ans")
    ax.set_ylabel("Points de base")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, "2_ecart_cnbc_bundesbank")
    return fig


# Nombre de jours comblés par pays et par année

def compter_jours_combles():
    """Affiche et renvoie le nombre de jours comblés par ffill, par pays et par année."""
    # On relit les taux CNBC bruts et on refait les étapes du nettoyage (jours ouvrés depuis START_DATE)
    raw_series = {}
    for country in config.COUNTRIES:
        bars = json.loads((config.RAW_DIR / f"cnbc_{country}10Y.json").read_text())["barData"]["priceBars"]
        raw_series[country] = pd.Series({pd.Timestamp(bar["tradeTime"][:8]): float(bar["close"]) for bar in bars})
    cnbc_raw = pd.DataFrame(raw_series).sort_index().loc[config.START_DATE:]
    cnbc_raw = cnbc_raw[cnbc_raw.index.dayofweek < 5]
    cnbc_raw = cnbc_raw.reindex(pd.bdate_range(cnbc_raw.index.min(), cnbc_raw.index.max()))

    # Un jour est "comblé" s'il était vide avant ffill et rempli après
    comble = cnbc_raw.isna() & cnbc_raw.ffill(limit=2).notna()
    par_annee = comble.groupby(comble.index.year).sum()
    print("\nJours comblés par pays et par année :")
    print(par_annee)
    return par_annee


# Les 10 plus fortes variations quotidiennes de chaque spread, confrontées aux événements

def calculer_spreads(cnbc):
    """Spreads FR, IT et ES contre l'Allemagne, en points de base."""
    return cnbc[["FR", "IT", "ES"]].sub(cnbc["DE"], axis=0) * 100


def confronter_variations_evenements(spreads):
    """Affiche, pour chaque spread, ses 10 plus fortes variations et les événements des 3 jours précédents."""
    events = load_events()

    for country in ["FR", "IT", "ES"]:
        variation = spreads[country].diff().dropna()
        top_dates = variation.abs().sort_values(ascending=False).head(10).index
        print(f"\nSpread {country} : 10 plus fortes variations quotidiennes")
        for d in top_dates:
            # Événements dans les 3 jours précédents (un événement du week-end se lit le lundi)
            proches = events[(events["date_pic"] >= d - pd.Timedelta(days=3)) & (events["date_pic"] <= d)]
            mots = " / ".join(proches["mots_cles"]) if len(proches) > 0 else "aucun événement"
            print(f"- {d.date()} : {variation[d]:+.1f} pb | {mots}")


# Figure 3 : histogramme des variations quotidiennes du spread français

def histogramme_spread_fr(spreads):
    """Enregistre l'histogramme des variations quotidiennes du spread français (figure 3)."""
    var_fr = spreads["FR"].diff().dropna()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(var_fr, bins=60, color=config.COLORS["FR"], edgecolor="white")
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_title("Figure 3 : variations quotidiennes du spread français")
    ax.set_xlabel("Variation quotidienne (pb)")
    ax.set_ylabel("Nombre de séances")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, "3_histogramme_variations_s_FR")
    return fig
