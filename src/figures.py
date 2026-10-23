"""Figures du projet, tracées avec matplotlib à partir des fonctions de src/.

Usage : python -m src.figures   (depuis la racine du dépôt)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.compare_sources import (
    CNBC_SYMBOLS,
    MIN_CHANGE_CORRELATION,
    MIN_CHANGES_PER_PERIOD,
    SPREADS,
    align,
    change_correlation_by_period,
    correlation_with_arbiter,
    gap_bp,
)
from src.load_rates import (
    load_banco_de_espana,
    load_banque_de_france,
    load_bundesbank,
    load_cnbc,
    load_eurostat,
)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "outputs" / "figures"
COUNTRY_NAMES = {"FR": "France", "DE": "Allemagne", "ES": "Espagne"}
SAME_DAY_COLOR = "#2a78d6"  # bleu : CNBC et Eurostat à la même date
SHIFTED_COLOR = "#eb6834"  # orange : barre CNBC de la veille
TEXT_COLOR = "#52514e"


def plot_change_correlation(period="M"):
    """Trace, pour chaque pays, la corrélation des variations CNBC et Eurostat par mois ou par année.

    Deux courbes par pays : CNBC comparé à Eurostat à la même date, puis la barre
    CNBC datée J comparée au taux Eurostat de J+1. Une ligne pointillée marque le
    seuil de 0,95 du critère D7. Si la courbe orange passe au-dessus de la bleue,
    la barre CNBC datée J porte la séance qu'Eurostat date J+1.

    Paramètres
    ----------
    period : str, "M" pour une corrélation par mois (environ 20 variations chacune),
        "Y" par année.

    Retourne
    --------
    Path du fichier PNG écrit dans outputs/figures/.
    """
    is_monthly = period == "M"
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, (country, symbol) in zip(axes, CNBC_SYMBOLS.items()):
        cnbc = load_cnbc(symbol, keep_weekends=True)
        eurostat = load_eurostat(country)
        same_day = change_correlation_by_period(cnbc, eurostat, lag_days=0, period=period)
        shifted = change_correlation_by_period(cnbc, eurostat, lag_days=1, period=period)

        marker_size = 3 if is_monthly else 5
        line_width = 1.2 if is_monthly else 2
        ax.axhline(MIN_CHANGE_CORRELATION, color=TEXT_COLOR, linewidth=1, linestyle="--")
        ax.plot(same_day.index.to_timestamp(), same_day.values, color=SAME_DAY_COLOR, linewidth=line_width,
                marker="o", markersize=marker_size, label="même date")
        ax.plot(shifted.index.to_timestamp(), shifted.values, color=SHIFTED_COLOR, linewidth=line_width,
                marker="s", markersize=marker_size, label="CNBC J contre Eurostat J+1")
        ax.set_title(COUNTRY_NAMES[country], color=TEXT_COLOR, loc="left")
        ax.set_ylim(-0.6 if is_monthly else -0.1, 1.05)
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)

    unit = "mois" if is_monthly else "année"
    period_phrase = "Un mois comptant" if is_monthly else "Une année comptant"
    not_drawn = "n'est pas tracé" if is_monthly else "n'est pas tracée"
    axes[0].set_ylabel(f"Corrélation des variations quotidiennes, par {unit}", color=TEXT_COLOR)
    axes[1].text(same_day.index[0].to_timestamp(), MIN_CHANGE_CORRELATION + 0.02, "seuil D7 (0,95)",
                 color=TEXT_COLOR, fontsize=8)  # panneau Allemagne : aucune courbe ne touche le seuil
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=2, frameon=False, fontsize=9)
    fig.suptitle("CNBC suit mal Eurostat d'un jour à l'autre, sauf pour la France jusqu'en juin 2024",
                 x=0.01, ha="left", fontsize=12)
    fig.text(0.01, -0.02, "Sources : CNBC, Eurostat (irt_lt_mcby_d, copie DBnomics). Jours communs, 2016 à avril 2025. "
             f"{period_phrase} moins de {MIN_CHANGES_PER_PERIOD} variations {not_drawn}.",
             fontsize=8, color=TEXT_COLOR)
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "mensuelle" if is_monthly else "annuelle"
    path = FIGURES_DIR / f"correlation_cnbc_eurostat_{suffix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_gaps_bp():
    """Trace l'écart quotidien CNBC - Eurostat, en pb, pour chaque pays et chaque spread.

    Un panneau par série : France, Allemagne, Espagne, puis les spreads France-Allemagne
    et France-Espagne, calculés dans chaque source avant comparaison (règle D5).
    Tous les panneaux partagent la même échelle verticale. Une ligne pointillée marque
    l'écart moyen sur la période.

    Retourne
    --------
    Path du fichier PNG écrit dans outputs/figures/.
    """
    cnbc = {country: load_cnbc(symbol) for country, symbol in CNBC_SYMBOLS.items()}
    eurostat = {country: load_eurostat(country) for country in CNBC_SYMBOLS}
    series = {COUNTRY_NAMES[country]: (cnbc[country], eurostat[country]) for country in CNBC_SYMBOLS}
    for first, second in SPREADS:
        name = f"Spread {COUNTRY_NAMES[first]}-{COUNTRY_NAMES[second]}"
        series[name] = (cnbc[first] - cnbc[second], eurostat[first] - eurostat[second])

    fig, axes = plt.subplots(2, 3, figsize=(12, 6.5), sharex=True, sharey=True)
    for ax, (name, (cnbc_series, eurostat_series)) in zip(axes.flat, series.items()):
        gaps = gap_bp(align(cnbc_series, eurostat_series))
        ax.axhline(0, color=TEXT_COLOR, linewidth=0.8)
        ax.plot(gaps.index, gaps.values, color=SAME_DAY_COLOR, linewidth=0.6)
        ax.axhline(gaps.mean(), color=SHIFTED_COLOR, linewidth=1.5, linestyle="--")
        ax.text(gaps.index[0], 27, f"moyenne {gaps.mean():+.1f} pb".replace(".", ","),
                color=TEXT_COLOR, fontsize=8)
        ax.set_title(name, color=TEXT_COLOR, loc="left", fontsize=10)
        ax.set_ylim(-32, 32)
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    axes.flat[-1].set_visible(False)
    axes[0, 2].xaxis.set_tick_params(labelbottom=True)  # la case du dessous est vide

    for ax in axes[:, 0]:
        ax.set_ylabel("CNBC - Eurostat (pb)", color=TEXT_COLOR)
    fig.suptitle("Les écarts quotidiens atteignent 25 pb ; l'Allemagne est décalée de +4 pb en moyenne",
                 x=0.01, ha="left", fontsize=12)
    fig.text(0.01, -0.02, "Sources : CNBC, Eurostat (irt_lt_mcby_d, copie DBnomics). Jours communs, 2016 à avril 2025. "
             "Pointillés : écart moyen.", fontsize=8, color=TEXT_COLOR)
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "ecarts_cnbc_eurostat_pb.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def plot_arbiter_correlation():
    """Trace, pour chaque pays, la corrélation mensuelle de CNBC et d'Eurostat avec la banque centrale.

    La banque centrale sert d'arbitre (journal, D9) : Banque de France (TEC 10),
    Bundesbank, Banco de España. Une ligne verticale marque juillet 2024, mois où
    Eurostat commence à recopier le TEC 10 pour la France.

    Retourne
    --------
    Path du fichier PNG écrit dans outputs/figures/.
    """
    arbiters = {"FR": load_banque_de_france(), "DE": load_bundesbank(), "ES": load_banco_de_espana()}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, (country, symbol) in zip(axes, CNBC_SYMBOLS.items()):
        table = correlation_with_arbiter(load_cnbc(symbol), load_eurostat(country), arbiters[country], period="M")
        months = table.index.to_timestamp()
        ax.axvline(pd.Timestamp("2024-07-01"), color=TEXT_COLOR, linewidth=1, linestyle=":")
        ax.plot(months, table["Eurostat"], color=SAME_DAY_COLOR, linewidth=1.2, marker="o", markersize=3,
                label="Eurostat contre banque centrale")
        ax.plot(months, table["CNBC"], color=SHIFTED_COLOR, linewidth=1.2, marker="s", markersize=3,
                label="CNBC contre banque centrale")
        ax.set_title(f"{COUNTRY_NAMES[country]} ({arbiters[country].name})", color=TEXT_COLOR, loc="left")
        ax.set_ylim(-0.6, 1.05)
        ax.grid(axis="y", color="#e6e5e1", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)

    axes[0].text(pd.Timestamp("2024-06-01"), -0.5, "juillet 2024", color=TEXT_COLOR, fontsize=8, ha="right")
    axes[0].set_ylabel("Corrélation des variations quotidiennes, par mois", color=TEXT_COLOR)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.01, -0.07), ncol=2, frameon=False, fontsize=9)
    fig.suptitle("Eurostat suit les banques centrales, CNBC non ; dès juillet 2024, Eurostat recopie le TEC 10",
                 x=0.01, ha="left", fontsize=12)
    fig.text(0.01, -0.1, "Sources : CNBC, Eurostat (copie DBnomics), Banque de France, Bundesbank, Banco de España. "
             f"Un mois comptant moins de {MIN_CHANGES_PER_PERIOD} variations communes n'est pas tracé.",
             fontsize=8, color=TEXT_COLOR)
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "arbitrage_banques_centrales.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    print(plot_change_correlation("Y"))
    print(plot_change_correlation("M"))
    print(plot_gaps_bp())
    print(plot_arbiter_correlation())
