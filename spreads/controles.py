"""Contrôles de qualité de la source CNBC (étapes 11 et 12).

Étape 11 : CNBC contre Eurostat en moyenne mensuelle pour les 4 pays
Étape 12 : CNBC contre la Bundesbank au jour le jour pour le Bund allemand

Figures enregistrées dans outputs/figures/
"""

import matplotlib.pyplot as plt
import pandas as pd

from spreads import config


# Étape 11 : CNBC contre Eurostat (mensuel)

def compare_monthly(cnbc_daily, eurostat_monthly):
    """Met CNBC en moyenne mensuelle et le place à côté d'Eurostat

    Renvoie une ligne par mois commun aux deux sources, deux colonnes par pays
    ("FR_cnbc", "FR_eurostat"...). Hyp : Eurostat est aussi une moyenne
    mensuelle des taux quotidiens. Ex : compare_monthly(cnbc, eurostat)
    """
    cnbc_monthly = cnbc_daily.resample("MS").mean()  # "MS" : un point par mois, daté du 1er

    eurostat = eurostat_monthly.copy()
    eurostat.index = pd.to_datetime(eurostat.index)  # "2016-01" devient 2016-01-01

    monthly = pd.merge(
        cnbc_monthly, eurostat,
        left_index=True, right_index=True,
        suffixes=("_cnbc", "_eurostat"),
    )
    return monthly


def monthly_gap_table(monthly):
    """Calcule, pour chaque pays, l'écart CNBC-Eurostat en points de base.

    Prend la sortie de compare_monthly. Renvoie une ligne par pays : écart moyen,
    écart absolu moyen et écart absolu maximal. Exemple : monthly_gap_table(monthly)
    """
    rows = []
    for country in config.COUNTRIES:
        gap = (monthly[f"{country}_cnbc"] - monthly[f"{country}_eurostat"]) * 100  # % -> pb
        rows.append({
            "pays": country,
            "ecart_moyen_pb": gap.mean(),
            "ecart_abs_moyen_pb": gap.abs().mean(),
            "ecart_abs_max_pb": gap.abs().max(),
        })
    return pd.DataFrame(rows).set_index("pays").round(2)


def plot_monthly_comparison(monthly):
    """Figure 00a : CNBC mensuel et Eurostat superposés, un graphique par pays."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    for ax, country in zip(axes.flatten(), config.COUNTRIES):
        ax.plot(monthly.index, monthly[f"{country}_cnbc"],
                color=config.COLORS[country], label="CNBC (moyenne mensuelle)")
        ax.plot(monthly.index, monthly[f"{country}_eurostat"],
                color="black", linestyle="--", linewidth=1, label="Eurostat")
        ax.set_title(country)
        ax.set_ylabel("Taux à 10 ans (%)")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Figure 00a : CNBC et Eurostat, moyennes mensuelles")
    fig.tight_layout()
    save_figure(fig, "00a_cnbc_eurostat_mensuel")
    return fig


def plot_mean_abs_gap(table):
    """Figure 00b : écart absolu moyen CNBC - Eurostat par pays, en barres."""
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = [config.COLORS[country] for country in table.index]
    ax.bar(table.index, table["ecart_abs_moyen_pb"], color=colors)
    ax.set_title("Figure 00b : écart absolu moyen CNBC - Eurostat")
    ax.set_ylabel("Points de base")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    save_figure(fig, "00b_ecart_abs_moyen")
    return fig


# Étape 12 : CNBC contre Bundesbank (journalier, Bund)

def compare_daily_bund(cnbc_de, bundesbank_de):
    """Place côte à côte le Bund de CNBC et celui de la Bundesbank jour par jour.

    Prend deux Series en %, renvoie les colonnes "cnbc" et "bundesbank" sur les
    jours communs. Ex : compare_daily_bund(cnbc["DE"], bundesbank["DE_bundesbank"])
    """
    daily = pd.DataFrame({"cnbc": cnbc_de, "bundesbank": bundesbank_de})
    return daily.dropna()


def daily_correlation_table(daily):
    """Corrélations entre CNBC et Bundesbank : niveaux, variations à 1 et 2 jours.

    diff(1) : taux du jour moins celui de la veille ; diff(2) : moins celui
    d'avant-hier. Prend la sortie de compare_daily_bund. Exemple : daily_correlation_table(daily)
    """
    rows = []
    for label, step in [("niveaux", 0), ("variations à 1 jour", 1), ("variations à 2 jours", 2)]:
        if step == 0:
            data = daily
        else:
            data = daily.diff(step).dropna()
        rows.append({
            "mesure": label,
            "correlation": data["cnbc"].corr(data["bundesbank"]),
            "nb_jours": len(data),
        })
    return pd.DataFrame(rows).set_index("mesure").round(3)


def plot_daily_gap(daily):
    """Figure 00c : écart CNBC - Bundesbank dans le temps en pb."""
    gap = (daily["cnbc"] - daily["bundesbank"]) * 100
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(gap.index, gap, color=config.COLORS["DE"], linewidth=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Figure 00c : écart CNBC - Bundesbank sur le Bund à 10 ans")
    ax.set_ylabel("Points de base")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, "00c_ecart_cnbc_bundesbank")
    return fig


def plot_daily_scatter(daily):
    """Figure 00d : variations quotidiennes CNBC contre Bundesbank en pb"""
    changes = daily.diff().dropna() * 100
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(changes["bundesbank"], changes["cnbc"],
               s=8, alpha=0.4, color=config.COLORS["DE"])
    ax.axline((0, 0), slope=1, color="black", linewidth=0.8, label="y = x")
    ax.set_title("Figure 00d : variations quotidiennes du Bund")
    ax.set_xlabel("Bundesbank (pb)")
    ax.set_ylabel("CNBC (pb)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, "00d_nuage_variations")
    return fig


def save_figure(fig, filename):
    """Enregistre une figure en PNG dans outputs/figures/"""
    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIG_DIR / f"{filename}.png", dpi=150)
