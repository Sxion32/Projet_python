"""Comparaison des taux à 10 ans CNBC et Eurostat, selon le critère D7 du journal.

Usage : python -m src.compare_sources   (depuis la racine du dépôt)
"""

import pandas as pd

from src.load_rates import (
    load_banco_de_espana,
    load_banque_de_france,
    load_bundesbank,
    load_cnbc,
    load_eurostat,
)

CNBC_SYMBOLS = {"FR": "FR10Y-FR", "DE": "DE10Y-DE", "ES": "ES10Y-ES"}
MAX_MEAN_ABS_GAP_BP = 3.0  # seuil D7 sur les niveaux, en points de base
MIN_CHANGE_CORRELATION = 0.95  # seuil D7 sur les variations quotidiennes
MIN_CHANGES_PER_PERIOD = 15  # en dessous, une corrélation mensuelle est trop instable
SPREADS = [("FR", "DE"), ("FR", "ES")]  # spreads étudiés : France-Allemagne et France-Espagne


def align(cnbc, eurostat):
    """Garde les seuls jours où les deux séries ont une valeur.

    Paramètres
    ----------
    cnbc, eurostat : pd.Series indexées par date, en %.

    Retourne
    --------
    pd.DataFrame à deux colonnes, "cnbc" et "eurostat", sur les jours communs.

    Exemple
    -------
    >>> align(load_cnbc("FR10Y-FR"), load_eurostat("FR")).columns.tolist()
    ['cnbc', 'eurostat']
    """
    both = pd.DataFrame({"cnbc": cnbc, "eurostat": eurostat})
    return both.dropna()


def gap_bp(aligned):
    """Écart quotidien CNBC - Eurostat, en points de base (1 pb = 0,01 point de %).

    Paramètres
    ----------
    aligned : pd.DataFrame renvoyé par align().

    Retourne
    --------
    pd.Series : date -> écart en pb, positif quand CNBC est au-dessus d'Eurostat.

    Exemple
    -------
    Un taux de 3,24 % chez CNBC et 3,20 % chez Eurostat donne un écart de 4 pb.
    """
    return (aligned["cnbc"] - aligned["eurostat"]) * 100


def summarize_gaps(aligned):
    """Mesure l'accord entre les deux colonnes d'un tableau aligné.

    Paramètres
    ----------
    aligned : pd.DataFrame renvoyé par align().

    Retourne
    --------
    dict : nombre de jours communs ; écart moyen (CNBC - Eurostat), écart absolu
    moyen et écart absolu maximal des niveaux, en pb ; corrélation des variations
    quotidiennes et écart absolu moyen de ces variations, en pb.

    Hypothèse
    ---------
    Une variation est calculée entre deux jours communs consécutifs : si un jour
    manque dans une source, la variation couvre deux jours pour les deux sources.
    """
    level_gap_bp = gap_bp(aligned)
    changes = aligned.diff().dropna()
    change_gap_bp = gap_bp(changes)
    return {
        "jours communs": len(aligned),
        "écart moyen (pb)": level_gap_bp.mean(),
        "écart abs. moyen (pb)": level_gap_bp.abs().mean(),
        "écart abs. max (pb)": level_gap_bp.abs().max(),
        "corr. variations": changes["cnbc"].corr(changes["eurostat"]),
        "écart abs. moyen variations (pb)": change_gap_bp.abs().mean(),
    }


def gap_relative_to_spread(cnbc_spread, eurostat_spread):
    """Rapporte l'écart CNBC - Eurostat à l'ordre de grandeur du spread, année par année.

    Paramètres
    ----------
    cnbc_spread, eurostat_spread : pd.Series, spread en % calculé dans chaque source
        (par exemple taux France - taux Allemagne), conformément à la règle D5.

    Retourne
    --------
    pd.DataFrame indexé par année, en pb sauf mention :
    - "spread abs. moyen" : taille moyenne du spread selon Eurostat, en valeur absolue,
      car le spread France-Espagne est négatif sur presque toute la période ;
    - "écart abs. niveau" et "écart / spread (%)" : écart absolu moyen des niveaux,
      en pb puis en % de la taille moyenne du spread ;
    - "variation abs. du spread" : variation quotidienne typique du spread selon Eurostat ;
    - "écart abs. variations" et "écart / variation (%)" : désaccord moyen des deux
      sources sur la variation du jour, en pb puis en % de la variation typique.

    Hypothèse
    ---------
    Eurostat sert d'échelle de référence ; un écart ne dit pas laquelle des deux
    sources se trompe. Quand le spread passe près de zéro (France-Espagne en 2024-2025),
    le rapport "écart / spread" grossit mécaniquement et doit être lu avec prudence.
    """
    aligned = align(cnbc_spread, eurostat_spread)
    changes = aligned.diff().dropna()
    levels = pd.DataFrame({
        "spread abs. moyen": aligned["eurostat"].abs() * 100,
        "écart abs. niveau": gap_bp(aligned).abs(),
    }).groupby(aligned.index.year).mean()
    moves = pd.DataFrame({
        "variation abs. du spread": changes["eurostat"].abs() * 100,
        "écart abs. variations": gap_bp(changes).abs(),
    }).groupby(changes.index.year).mean()
    table = levels.join(moves)
    table["écart / spread (%)"] = 100 * table["écart abs. niveau"] / table["spread abs. moyen"]
    table["écart / variation (%)"] = 100 * table["écart abs. variations"] / table["variation abs. du spread"]
    return table


def change_correlation_by_period(cnbc, eurostat, lag_days, period="M"):
    """Corrélation des variations quotidiennes par mois ou par année, après décalage des dates CNBC.

    Paramètres
    ----------
    cnbc : pd.Series CNBC, de préférence avec les week-ends (load_cnbc(..., keep_weekends=True)).
    eurostat : pd.Series Eurostat.
    lag_days : int, nombre de jours civils ajoutés aux dates CNBC. Avec lag_days=1,
        la barre CNBC datée J est comparée au taux Eurostat du jour J+1.
    period : str, "M" pour une corrélation par mois, "Y" par année.

    Retourne
    --------
    pd.Series : période (pd.Period) -> corrélation des variations entre jours communs.
    Une période comptant moins de MIN_CHANGES_PER_PERIOD variations vaut NaN.

    Hypothèse
    ---------
    Si la corrélation est nettement plus forte avec lag_days=1 qu'avec 0, la barre
    CNBC datée J porte la séance européenne que Eurostat date J+1.

    Exemple
    -------
    >>> change_correlation_by_period(load_cnbc("ES10Y-ES", keep_weekends=True), load_eurostat("ES"), 1, "Y")
    2016    0.21
    ...
    """
    shifted = cnbc.copy()
    shifted.index = shifted.index + pd.Timedelta(days=lag_days)
    changes = align(shifted, eurostat).diff().dropna()
    groups = changes.groupby(changes.index.to_period(period))

    def correlation_if_enough_days(group):
        if len(group) < MIN_CHANGES_PER_PERIOD:
            return float("nan")
        return group["cnbc"].corr(group["eurostat"])

    return groups.apply(correlation_if_enough_days)


def correlation_with_arbiter(cnbc, eurostat, arbiter, period="M"):
    """Compare CNBC et Eurostat à une troisième source, par mois ou par année.

    Paramètres
    ----------
    cnbc, eurostat : pd.Series, taux ou spread en % selon chaque source.
    arbiter : pd.Series, le même taux ou spread selon une source nationale.
    period : str, "M" par mois, "Y" par année.

    Retourne
    --------
    pd.DataFrame indexé par période, deux colonnes : corrélation des variations
    quotidiennes de CNBC avec l'arbitre, puis d'Eurostat avec l'arbitre.

    Hypothèses
    ----------
    - Chaque corrélation est calculée sur les jours communs de la paire comparée :
      CNBC peut donc être comparé à l'arbitre après avril 2025, Eurostat non.
    - L'arbitre n'est pas la vérité : il a sa propre méthode et sa propre heure de
      relevé. La source qui s'en rapproche le plus est seulement la plus cohérente.
    """
    return pd.DataFrame({
        "CNBC": change_correlation_by_period(cnbc, arbiter, lag_days=0, period=period),
        "Eurostat": change_correlation_by_period(eurostat, arbiter, lag_days=0, period=period),
    })


def coverage_table():
    """Résume la couverture de chaque série enregistrée dans data/raw/.

    Retourne
    --------
    pd.DataFrame : une ligne par série, avec le pays, le nombre d'observations, la
    première et la dernière date.
    """
    series = [("CNBC", country, load_cnbc(symbol)) for country, symbol in CNBC_SYMBOLS.items()]
    series += [("Eurostat (copie DBnomics)", country, load_eurostat(country)) for country in CNBC_SYMBOLS]
    series += [
        ("Banque de France, TEC 10", "FR", load_banque_de_france()),
        ("Bundesbank", "DE", load_bundesbank()),
        ("Banco de España, TI 1.3", "ES", load_banco_de_espana()),
    ]
    rows = [
        {"source": source, "pays": country, "observations": len(rates),
         "début": rates.index.min().date(), "fin": rates.index.max().date()}
        for source, country, rates in series
    ]
    return pd.DataFrame(rows)


def share_identical_days(first, second, period="M", tolerance_bp=0.05):
    """Part des jours où deux séries sont égales, à tolerance_bp points de base près.

    Paramètres
    ----------
    first, second : pd.Series en %.
    period : str, "M" par mois, "Y" par année.
    tolerance_bp : float, écart en pb en dessous duquel deux valeurs sont jugées égales.

    Retourne
    --------
    pd.Series : période -> part des jours communs où les deux séries sont égales.

    Exemple
    -------
    Si Eurostat recopie le TEC 10 de la Banque de France, la part vaut 1 sur ces mois.
    """
    gap = gap_bp(align(first, second)).abs()
    is_identical = gap < tolerance_bp
    return is_identical.groupby(is_identical.index.to_period(period)).mean()


def compare_all():
    """Compare CNBC et Eurostat pour chaque pays, puis pour les deux spreads.

    Retourne
    --------
    pd.DataFrame : une ligne par série comparée (FR, DE, ES, FR-DE, FR-ES), les
    colonnes de summarize_gaps() et, pour les pays, une colonne "critère D7 respecté".
    """
    cnbc = {country: load_cnbc(symbol) for country, symbol in CNBC_SYMBOLS.items()}
    eurostat = {country: load_eurostat(country) for country in CNBC_SYMBOLS}

    rows = {}
    for country in CNBC_SYMBOLS:
        rows[country] = summarize_gaps(align(cnbc[country], eurostat[country]))
    for first, second in SPREADS:
        cnbc_spread = cnbc[first] - cnbc[second]
        eurostat_spread = eurostat[first] - eurostat[second]
        rows[f"{first}-{second}"] = summarize_gaps(align(cnbc_spread, eurostat_spread))

    table = pd.DataFrame(rows).T
    countries = list(CNBC_SYMBOLS)
    table.loc[countries, "critère D7 respecté"] = (
        (table.loc[countries, "écart abs. moyen (pb)"] < MAX_MEAN_ABS_GAP_BP)
        & (table.loc[countries, "corr. variations"] > MIN_CHANGE_CORRELATION)
    )
    return table


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(compare_all().round(3).to_string())
