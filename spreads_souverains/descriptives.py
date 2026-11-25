# Dans ce script, on décrit les taux et les spreads : niveaux (étape 14), puis écarts
# entre pays et volatilité (étape 15). On part du panel de data/yields.csv
# (taux en %, spreads s_FR, s_IT, s_ES en points de base contre l'Allemagne).

import matplotlib.pyplot as plt
import pandas as pd

from spreads_souverains import config
from spreads_souverains.controles import save_figure

SPREADS = ["s_FR", "s_IT", "s_ES"]
FENETRE = 60  # nombre de séances des statistiques glissantes (environ 3 mois)


def charger_panel():
    """Lit le panel des taux et des spreads (data/yields.csv), indexé par date."""
    return pd.read_csv(config.DATA_DIR / "yields.csv", index_col="date", parse_dates=True)


def ligne_dissolution(ax):
    """Trace une ligne verticale grise à la date de rupture (dissolution)."""
    ax.axvline(config.BREAK_DATE, color="grey", linestyle="--", label="Dissolution")


# Étape 14 : niveaux

def tracer_rendements(panel):
    """Figure 6 : taux à 10 ans des 4 pays."""
    fig, ax = plt.subplots(figsize=(12, 5))
    for country in config.COUNTRIES:
        ax.plot(panel[country], color=config.COLORS[country], linewidth=1, label=country)
    ligne_dissolution(ax)
    ax.set_title("Figure 6 : taux souverains à 10 ans")
    ax.set_ylabel("Taux (%)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "6_rendements_10_ans")
    return fig


def tracer_spreads(panel):
    """Figure 7 : spreads FR, IT et ES contre le Bund, en points de base."""
    fig, ax = plt.subplots(figsize=(12, 5))
    for spread in SPREADS:
        country = spread[2:]  # "s_FR" -> "FR"
        ax.plot(panel[spread], color=config.COLORS[country], linewidth=1, label=f"{country} - DE")
    ligne_dissolution(ax)
    ax.set_title("Figure 7 : spreads à 10 ans contre le Bund allemand")
    ax.set_ylabel("Points de base")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "7_spreads_contre_bund")
    return fig


def statistiques_par_periode(panel):
    """Spread moyen et écart-type des variations quotidiennes, par sous-période (config.PERIODS)."""
    tableau = panel[SPREADS].copy()

    # Colonne "periode" : on repère les dates de chaque sous-période (fin None = jusqu'au bout)
    tableau["periode"] = None
    for nom, (debut, fin) in config.PERIODS.items():
        dans_periode = tableau.index >= debut
        if fin is not None:
            dans_periode = dans_periode & (tableau.index <= fin)
        tableau.loc[dans_periode, "periode"] = nom

    # Variations quotidiennes des spreads (pb), calculées sur toute la série
    variations = tableau[SPREADS].diff()
    variations["periode"] = tableau["periode"]

    moyennes = tableau.groupby("periode")[SPREADS].mean().add_prefix("moyenne_")
    ecarts_types = variations.groupby("periode")[SPREADS].std().add_prefix("ecart_type_var_")
    resultat = pd.concat([moyennes, ecarts_types], axis=1).round(1)
    resultat = resultat.reindex(list(config.PERIODS))  # ordre chronologique, pas alphabétique
    print("Spreads par sous-période (pb) :")
    print(resultat.to_string())
    return resultat


# Étape 15 : écarts entre pays et volatilité

def tracer_ecarts(panel):
    """Figure 8 : écarts France - Espagne et France - Italie, en points de base."""
    ecart_es = panel["s_FR"] - panel["s_ES"]  # = (taux FR - taux ES) en pb
    ecart_it = panel["s_FR"] - panel["s_IT"]

    # Premier jour où la France emprunte plus cher que l'Espagne
    print("Premier jour où l'écart France - Espagne est positif :", ecart_es[ecart_es > 0].index[0].date())

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(ecart_es, color=config.COLORS["ES"], linewidth=1, label="France - Espagne")
    ax.plot(ecart_it, color=config.COLORS["IT"], linewidth=1, label="France - Italie")
    ax.axhline(0, color="black", linewidth=0.8)
    ligne_dissolution(ax)
    ax.set_title("Figure 8 : écart de taux de la France avec l'Espagne et l'Italie")
    ax.set_ylabel("Points de base (positif : la France paie plus)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "8_ecarts_france_espagne_italie")
    return fig


def tracer_volatilite_correlation(panel):
    """Figure 9 : volatilité glissante des spreads et corrélation glissante FR-IT et FR-ES."""
    variations = panel[SPREADS].diff()  # variations quotidiennes en pb

    fig, (ax_haut, ax_bas) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Panneau du haut : écart-type des variations sur les 60 dernières séances
    for spread in SPREADS:
        country = spread[2:]
        ax_haut.plot(variations[spread].rolling(FENETRE).std(),
                     color=config.COLORS[country], linewidth=1, label=f"{country} - DE")
    ligne_dissolution(ax_haut)
    ax_haut.set_title(f"Volatilité : écart-type des variations quotidiennes sur {FENETRE} séances")
    ax_haut.set_ylabel("Points de base")
    ax_haut.grid(alpha=0.3)
    ax_haut.legend()

    # Panneau du bas : corrélation des variations du spread français avec les deux autres
    for other in ["IT", "ES"]:
        correlation = variations["s_FR"].rolling(FENETRE).corr(variations[f"s_{other}"])
        ax_bas.plot(correlation, color=config.COLORS[other], linewidth=1, label=f"FR - {other}")
    ligne_dissolution(ax_bas)
    ax_bas.set_title(f"Corrélation des variations quotidiennes sur {FENETRE} séances")
    ax_bas.set_ylabel("Corrélation")
    ax_bas.grid(alpha=0.3)
    ax_bas.legend()

    fig.suptitle("Figure 9 : volatilité et corrélation glissantes des spreads")
    fig.tight_layout()
    save_figure(fig, "9_volatilite_correlation")
    return fig
