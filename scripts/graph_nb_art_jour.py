import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from spreads_souverains.config import FIG_DIR, TITRES_BRUTS_FILE

FICHIER_TITRES = TITRES_BRUTS_FILE
FICHIER_GRAPHIQUE = FIG_DIR / "nb_articles_par_jour.png"


def tracer_articles_par_jour(fichier_titres=FICHIER_TITRES, fichier_graphique=FICHIER_GRAPHIQUE):
    """Graphique du nombre de titres par jour et de sa moyenne mobile, enregistré dans outputs/figures/."""
    titres = pd.read_csv(fichier_titres, encoding="utf-8-sig", parse_dates=["date"])
    titres = titres[titres["date"] >= "2016-01-01"]

    # Nombre d'articles par jour (les jours sans article sont comptés 0)
    articles_par_jour = (
        titres.groupby(titres["date"].dt.normalize()).size()
        .reindex(pd.date_range(titres["date"].min().normalize(),
                               titres["date"].max().normalize(), freq="D"),
                 fill_value=0)
    )
    moyenne_30j = articles_par_jour.rolling(30, center=True, min_periods=15).mean()

    print(f"{len(titres)} articles du {articles_par_jour.index[0].date()} au {articles_par_jour.index[-1].date()}")
    print(f"Moyenne : {articles_par_jour.mean():.1f} articles/jour, "
          f"{(articles_par_jour == 0).sum()} jours sans article")

    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(articles_par_jour.index, articles_par_jour.values,
            color="#9ec5f4", linewidth=0.6, label="Nombre par jour")
    ax.plot(moyenne_30j.index, moyenne_30j.values,
            color="#1c5cab", linewidth=2, label="Moyenne mobile 30 jours")

    ax.set_title("France Info : nombre de titres d'articles politiques par jour depuis 2016",
                 loc="left", color="#0b0b0b")
    ax.set_ylabel("Articles par jour", color="#52514e")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)
    ax.tick_params(colors="#52514e")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()

    fichier_graphique.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(fichier_graphique, dpi=150)
    print("Graphique enregistré :", fichier_graphique)
    return fig
