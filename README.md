# Spreads souverains et risque politique en zone euro

Ce projet étudie l'écart de taux à 10 ans entre l'OAT française et le Bund allemand
autour d'événements politiques français, ainsi que l'écart entre la France et l'Espagne,
pour distinguer un risque propre à la France d'un mouvement commun.

## Problématique

Le risque politique est-il devenu une composante propre de la prime de risque française
depuis 2024 ? (formulation provisoire)

## Période d'étude

Nous partons du 1er janvier 2016, soit l'année précédant l'élection d'Emmanuel Macron,
afin de couvrir la période avant et après ce changement politique. La date de fin est
celle des données enregistrées dans `data/raw/`.

## Objectifs

- analyser les spreads à 10 ans France-Allemagne et France-Espagne ;
- identifier les mouvements propres à la France autour d'événements politiques ;
- distinguer les chocs communs à la zone euro des chocs purement nationaux.

## Structure du dépôt

- `main.ipynb` : rapport, livrable principal ; il s'exécute hors ligne à partir de `data/raw/` ;
- `main.py` : point d'entrée du projet ;
- `scripts/` : les seuls scripts qui se connectent à Internet :
  - `check_sources.py` : test de faisabilité des sources de taux ;
  - `download_cnbc.py`, `download_eurostat.py`, `download_national.py` : téléchargent les
    taux à 10 ans (CNBC, Eurostat, Banque de France, Bundesbank, Banco de España) et les
    enregistrent tels quels dans `data/raw/` ;
- `src/` : code utilisé par le notebook :
  - `load_rates.py` : lecture des fichiers bruts ;
  - `compare_sources.py` : comparaison des sources de taux ;
  - `figures.py` : figures, enregistrées dans `outputs/figures/` ;
- `data/raw/` : données brutes, versionnées pour l'exécution hors ligne ;
- `outputs/figures/` : figures produites par `src/figures.py` ;
- `docs/journal_decisions.md` : journal des choix de méthode et des biais ;
- `requirements.txt` : dépendances Python.

## Dépendances

Le projet s'exécute dans un environnement virtuel local, sans stockage de secrets dans le dépôt.

## Lancement

1. Créer un environnement virtuel :
   python -m venv .venv
2. L'activer :
   source .venv/bin/activate
3. Installer les dépendances :
   pip install -r requirements.txt
4. Ouvrir et exécuter le rapport `main.ipynb`, qui ne nécessite pas de connexion.
5. Pour retélécharger les données (facultatif, en ligne) :
   python scripts/download_cnbc.py
   python scripts/download_eurostat.py
   python scripts/download_national.py

## Sources

Taux souverains à 10 ans : CNBC, Eurostat (copie DBnomics), BCE, Banque de France,
Bundesbank, Banco de España. Le choix de la source quotidienne est en cours ; la
comparaison est documentée dans `main.ipynb` et dans le journal. Les données CNBC sont
soumises aux conditions d'utilisation de Versant (usage personnel et non commercial).
Sources des événements politiques : à déterminer.

## Notes méthodologiques

- Les séries mensuelles sont utiles pour la vue de long terme, mais pas pour mesurer l'effet d'un événement daté.
- Il faut raisonner en variations autour d'événements, pas seulement en niveaux.
- Le calendrier d'événements est construit et documenté dans le projet.
- La causalité doit être discutée avec prudence : une co-occurrence n'est pas une preuve.
