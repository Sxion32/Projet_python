# Spread souverains et risque politique en zone euro

Ce projet étudie la dynamique des spreads souverains entre l'OAT française et le Bund allemand autour d'événements politiques, en les comparant aux spreads italien et espagnol.

## Problématique

Le risque politique est-il devenu une composante propre de la prime de risque française depuis 2024 ?

## Période d'étude

Nous partons du 1er janvier 2016, soit l'année précédant l'élection d'Emmanuel Macron, afin de couvrir la période avant et après ce changement politique. Les données vont jusqu'à la dernière séance disponible au moment de l'exécution.

## Objectifs

- analyser les écarts de taux à 10 ans entre pays de la zone euro ;
- identifier les mouvements spécifiques à la France autour d'événements politiques ;
- comparer les évolutions françaises, italiennes et espagnoles ;
- distinguer les chocs européens des chocs purement nationaux.

## Structure du dépôt

```
.
├── main.ipynb                  # Rapport (livrable principal)
├── main.py                     # Exécute toute la chaîne : python3 main.py
├── requirements.txt            # Bibliothèques nécessaires : pip install -r requirements.txt
├── .env.example                # Modèle du fichier .env (clé Media Cloud), à copier en .env
├── spreads_souverains/
│   ├── config.py               # Constantes : chemins, période, pays, couleurs, date de rupture
│   ├── panel.py                # Calcul des spreads contre l'Allemagne
│   ├── controles.py            # Fiabilité de CNBC (Eurostat, Bundesbank)
│   └── events.py               # Date de réaction du marché à un événement
├── import_cleaning/
│   ├── importation_donnees.py  # Téléchargement des taux (CNBC, Bundesbank, Eurostat)
│   ├── cleaning.py             # Nettoyage des taux
│   ├── import_titres.py        # Collecte des titres France Info (Media Cloud)
│   └── nettoyage_titres.py     # Filtrage des titres politiques
├── scripts/
│   ├── detect_ev.py            # Détection des événements (pics d'articles)
│   └── graph_nb_art_jour.py    # Nombre d'articles par jour
├── data/
│   ├── raw/                    # Données brutes téléchargées
│   └── cleaned/                # Données nettoyées
├── outputs/
│   ├── figures/                # Graphiques
│   └── tables/                 # Tableaux (events.csv)
├── docs/
│   └── journal_decisions.md    # Choix de méthode, alternatives écartées et biais
└── tests/                      # Tests : python3 -m tests.test_events
```


## Sources

- CBNC pour l'évolution du taux des OAT européennes.
- Canal d'information à déterminer pour les évènements politiques.

## Méthode

## Principaux résultats 
