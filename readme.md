# Spreads souverains et risque politique en zone euro

Ce projet étudie la dynamique des spreads souverains entre l'OAT française et le Bund allemand autour d'événements politiques, en les comparant aux spreads italien et espagnol.

## Problématique

Depuis 2016, dans quelle mesure l'actualité politique française explique-t-elle les variations des taux des OAT, et donc du spread français face à l'Allemagne ? Quels types d'événements font réellement bouger les marchés ?

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

- **Taux à 10 ans** : CNBC (source principale, journalière, France, Allemagne, Italie, Espagne), contrôlée par la Bundesbank (taux allemand journalier) et par Eurostat (taux de convergence mensuels des quatre pays).
- **Actualité politique** : titres d'articles de France Info depuis 2016, collectés avec l'API de Media Cloud (clé personnelle à placer dans un fichier `.env`, voir `.env.example`).

## Méthode

1. Nettoyage des taux : jours ouvrés uniquement, trous de 1 ou 2 jours comblés par la dernière valeur, correction d'une valeur erronée de CNBC (novembre 2022).
2. Spreads contre le Bund allemand, en points de base, pour la France, l'Italie et l'Espagne.
3. Détection automatique des grands événements politiques : jours où France Info publie au moins deux fois plus d'articles politiques que d'habitude.
4. Étude d'événements : variation des spreads le jour de réaction, rapportée à la volatilité des 60 séances précédentes, avec un test de permutation. L'Italie et l'Espagne servent de témoins.
5. Indice quotidien d'actualité politique (titres contenant « censure », « 49.3 », « dissolution » ou « Premier ministre ») et corrélation avec l'ampleur des variations du spread français.

## Principaux résultats

Données jusqu'au 9 novembre 2026.

- Les grands mouvements du spread français sont surtout européens : une seule de ses 10 plus fortes variations quotidiennes suit un événement politique détecté.
- Les jours d'événement politique, le spread français est significativement plus agité qu'à l'ordinaire (p-valeur de 3 %), mais l'effet n'est plus significatif une fois le mouvement commun avec l'Espagne et l'Italie retiré.
- Ce sont les crises de gouvernement (dissolution, 49.3, démission d'un Premier ministre) qui font réagir le spread, pas l'actualité politique ordinaire : la corrélation entre l'indice d'actualité et l'ampleur des variations n'est que de 0,06.
- Le spread français a changé de niveau : la France emprunte plus cher que l'Espagne depuis septembre 2024 et que l'Italie depuis octobre 2025.

## L'utilisation de l'intelligence artificielle

Au cours de ce projet, nous avons utiliser des outils d'IA générative comme une aide ponctuelle principalement pour comprendre des messages d'erreurs, retrouver plus facilement les bonnes syntaxes de code et repérer des incohérences. 

La conception de la problématique et les choix de fond restent les nôtres.

## Lancement

Depuis la racine du dépôt :

```
pip install -r requirements.txt
python3 main.py                                              # toute la chaîne de calcul
jupyter nbconvert --to notebook --execute --inplace main.ipynb  # réexécute le rapport
python3 -m tests.test_events                                 # tests
```
