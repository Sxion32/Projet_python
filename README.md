# Spreads souverains et risque politique en zone euro

Ce projet étudie l'écart de taux à 10 ans entre l'OAT française et le Bund allemand
autour d'événements politiques français, en le comparant à l'écart entre l'Espagne et
l'Allemagne, pour distinguer un risque propre à la France d'un mouvement commun.

## Problématique

Le risque politique est-il devenu une composante propre de la prime de risque française
depuis 2024 ? (formulation provisoire)

## Période d'étude

Nous partons du 1er janvier 2016, soit l'année précédant l'élection d'Emmanuel Macron,
afin de couvrir la période avant et après ce changement politique. La date de fin est
celle des données enregistrées dans `data/raw/`.

## Objectifs

- analyser les écarts de taux à 10 ans de la France et de l'Espagne face à l'Allemagne ;
- identifier les mouvements propres à la France autour d'événements politiques ;
- distinguer les chocs communs à la zone euro des chocs purement nationaux.

## Structure du dépôt

- `main.ipynb` : rapport, livrable principal ;
- `main.py` : point d'entrée du projet ;
- `scripts/check_sources.py` : test de faisabilité des sources de taux ;
- `requirements.txt` : dépendances Python ;
- `data/` : données ; `data/raw/` est versionné pour l'exécution hors ligne.

## Dépendances

Le projet s'exécute dans un environnement virtuel local, sans stockage de secrets dans le dépôt.

## Lancement

1. Créer un environnement virtuel :
   python -m venv .venv
2. L'activer :
   source .venv/bin/activate
3. Installer les dépendances :
   pip install -r requirements.txt
4. Lancer le projet :
   python main.py

## Sources

Taux souverains à 10 ans : Eurostat, BCE, Banque de France, Bundesbank, Banco de España
(en cours de validation). Sources des événements politiques : à déterminer.

## Notes méthodologiques

- Les séries mensuelles sont utiles pour la vue de long terme, mais pas pour mesurer l'effet d'un événement daté.
- Il faut raisonner en variations autour d'événements, pas seulement en niveaux.
- Le calendrier d'événements est construit et documenté dans le projet.
- La causalité doit être discutée avec prudence : une co-occurrence n'est pas une preuve.
