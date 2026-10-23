# Journal des décisions

Nous consignons ici chaque choix de méthode et chaque biais repéré, avec sa date, les
alternatives écartées, notre justification et le biais qu'il peut introduire. Une décision
marquée « en cours » n'est pas encore tranchée.

## D1. Seule la vie politique française est recensée (2026-10-16)

- **Décision.** Le calendrier d'événements ne recense que des événements français.
  L'Allemagne et l'Espagne servent uniquement de référence de taux.
- **Alternative écartée.** Un calendrier symétrique pour la France, l'Allemagne et l'Espagne.
- **Justification.** Notre question porte sur le risque politique français. Un calendrier
  symétrique nous exposait à recenser plus d'événements français, parce que nous connaissons
  mieux la vie politique française.
- **Biais possible.** Un événement allemand fait bouger le Bund, donc tous les spreads, et un
  événement espagnol fait bouger le spread de comparaison. Ces jours-là, une variation du
  spread OAT-Bund peut ne rien dire du risque français. Le traitement de ces jours reste
  à décider (en cours).

## D2. Schéma du calendrier d'événements (2026-10-16)

- **Décision.** `data/raw/evenements.csv` suit un schéma de 21 colonnes : `id`, `pays`,
  `canal_spread`, `type_evenement`, `acteur`, `date_evenement`, `heure_evenement`,
  `fuseau`, `precision_heure`, `date_annoncee`, `issue`, `issue_anticipee`, `episode`,
  `description`, `url_source`, `type_source`, `url_source_heure`, `date_consultation`,
  `collecte`, `verifie_par`, `notes`. Les chocs communs à la zone euro sont recensés dans
  un fichier séparé au même schéma.
- **Principes.** Le fichier ne contient que des faits lus dans une source. Ce qui se calcule
  (premier jour de marché, chevauchement des fenêtres, coïncidence avec un choc commun) est
  calculé par du code. Le vocabulaire des types est fonctionnel, pas institutionnel.
- **Alternatives écartées.** Un fichier à quatre colonnes (date, type, description, lien),
  insuffisant pour distinguer la date de l'événement de la date de réaction du marché et
  les deux notions de prévisibilité ; un fichier unique mêlant événements nationaux et
  chocs communs.
- **Biais possible.** La colonne `issue_anticipee` est la plus subjective : elle expose au
  biais rétrospectif. Avec D1, `pays` et `canal_spread` sont constants dans ce fichier ;
  nous les gardons pour partager le schéma avec le fichier des chocs.

## D3. Extraction et catégorisation par règles Python, sans IA (2026-10-16)

- **Décision.** Les événements sont extraits et catégorisés par des règles explicites
  écrites en Python : filtres sur les champs des données ouvertes, expressions régulières
  sur les intitulés. Aucune catégorisation n'est confiée à une IA.
- **Alternative écartée.** Une catégorisation par un modèle de langage, ou au cas par cas
  à la main.
- **Justification.** Une règle écrite est reproductible, vérifiable par des tests et
  défendable à l'oral.
- **Biais possible.** Une expression régulière peut mal classer un intitulé atypique. Nous
  le limitons par des tests et par une relecture ligne par ligne.

## D4. Lacune de la série quotidienne Eurostat (2026-10-16)

- **Constat.** La série quotidienne `irt_lt_mcby_d` n'est plus diffusée par l'API Eurostat.
  Sa copie sur DBnomics s'arrête au 2025-04-04 (2025-03-31 pour la France). La série
  mensuelle de la BCE (jeu IRS) couvre les trois pays sans lacune depuis 2016.
- **Conséquence.** Il nous faut une autre source quotidienne après avril 2025 (voir D6).

## D5. Ne pas mélanger deux sources dans un même spread (2026-10-16)

- **Constat.** Comparées à la série mensuelle de la BCE, le TEC 10 de la Banque de France
  s'écarte jusqu'à 12 pb, et la série à 10 ans de la Bundesbank est en moyenne 4 pb
  au-dessus, entre -2 et +10 pb selon les mois.
- **Décision.** Les deux jambes d'un spread viennent de la même source.
- **Biais évité.** Calculer l'OAT-Bund avec le TEC 10 et la Bundesbank mélangerait au spread
  un écart de méthode variable dans le temps.

## D6. Source quotidienne des taux : CNBC (2026-10-16, en cours)

- **Décision.** Nous retenons CNBC (symboles `FR10Y-FR`, `DE10Y-DE`, `ES10Y-ES`) comme source
  quotidienne, parce qu'elle couvre 2016 à 2026 pour les trois pays et qu'elle est proche
  de la série Eurostat jusqu'en avril 2025.
- **Alternatives écartées.** Eurostat via DBnomics (s'arrête en avril 2025) ; les sources
  nationales (arrêtées ou en retard, et de méthodes différentes, voir D5).
- **Constats de notre comparaison.** Même jour, écart avec Eurostat : France 0,5 pb en
  médiane ; Allemagne +4,4 pb en moyenne, systématiquement ; Espagne 3,1 pb en médiane.
  CNBC publie aussi des barres datées du samedi.
- **Vérifications en cours.** Heure de la clôture retenue par CNBC ; sens des barres du
  samedi ; écart sur les variations quotidiennes ; conditions d'utilisation des données et
  droit de les publier dans un dépôt public.

## D7. Critère de choix entre CNBC et Eurostat, fixé avant la comparaison (2026-10-23)

- **Décision.** CNBC devient notre source quotidienne si, pour chacun des trois pays, sur
  les jours communs avec Eurostat entre 2016 et avril 2025 : l'écart absolu moyen des
  niveaux est inférieur à 3 pb, et la corrélation des variations quotidiennes dépasse 0,95.
  Nous calculons aussi les mêmes indicateurs sur les spreads France-Allemagne et
  Espagne-Allemagne, à titre d'information.
- **Règles de préparation.** Nous retirons les barres CNBC datées d'un samedi ou d'un
  dimanche. Nous ne comparons que les jours où les deux sources ont une valeur ; une
  variation est calculée entre deux jours communs consécutifs.
- **Alternatives écartées.** Un critère sur les seuls niveaux, alors que l'étude
  d'événements porte sur des variations ; un critère choisi après avoir vu les résultats.
- **Limite.** Le critère n'est pas totalement aveugle : la comparaison rapide de D6 nous
  avait déjà montré un écart systématique d'environ 4 pb sur l'Allemagne. Nous gardons
  malgré tout les seuils proposés avant d'écrire le code.
- **Biais possible.** Eurostat est lui-même une référence, pas la vérité : un écart peut
  venir de l'heure de relevé (CNBC découpe ses journées à l'heure de New York) plutôt que
  d'une erreur de CNBC.
- **Résultats (2026-10-23).** Sur les jours communs de 2016 à avril 2025, le critère n'est
  respecté pour aucun pays :

  | Série | Jours communs | Écart moyen | Écart abs. moyen | Écart abs. max | Corr. des variations |
  |---|---|---|---|---|---|
  | France | 2 356 | +0,1 pb | 0,8 pb | 16,9 pb | 0,93 |
  | Allemagne | 2 346 | +4,4 pb | 5,0 pb | 24,5 pb | 0,50 |
  | Espagne | 2 344 | +1,3 pb | 4,0 pb | 25,6 pb | 0,38 |
  | Spread FR-DE | 2 328 | -4,2 pb | 5,0 pb | 25,5 pb | 0,30 |
  | Spread ES-DE | 2 322 | -3,1 pb | 4,7 pb | 28,9 pb | 0,33 |

- **Diagnostic : l'heure de relevé.** En décalant les dates CNBC d'un jour, année par
  année, la corrélation des variations change ainsi :
  - France : CNBC est aligné sur Eurostat le même jour (0,86 à 0,98 de 2016 à 2023), moins
    bien en 2024 (0,76) et 2025 (0,71) ;
  - Espagne : à partir de 2020, la corrélation passe de 0,18-0,51 le même jour à
    0,68-0,89 avec un jour de décalage : la barre CNBC datée J porte la séance
    qu'Eurostat date J+1 ;
  - Allemagne : autour de 0,5 le même jour comme avec un jour de décalage, chaque année.
    Nous l'interprétons comme une clôture prise entre deux journées européennes, sans doute
    en fin de journée à New York, si bien que chaque variation CNBC mélange deux jours de
    marché européen. C'est une hypothèse, pas un fait vérifié.
  Les figures `outputs/figures/correlation_cnbc_eurostat_annuelle.png` et
  `correlation_cnbc_eurostat_mensuelle.png` (`python -m src.figures`) montrent ces
  corrélations par année et par mois. Nous ne descendons pas à la semaine : 4 ou 5
  variations par semaine donnent une corrélation trop instable. Un mois comptant moins de
  15 variations communes n'est pas retenu.
- **Ce que montre la vue mensuelle.**
  - France : la corrélation le même jour reste entre 0,94 et 0,99 de janvier à juin 2024,
    puis chute brutalement à 0,31 en juillet 2024 et 0,10 en août 2024, sans revenir
    au-dessus de 0,84 ensuite. La rupture n'est pas progressive. Elle coïncide avec la
    dissolution de l'Assemblée nationale (9 juin 2024) et les élections législatives
    anticipées (30 juin et 7 juillet 2024), c'est-à-dire avec le cœur de notre période
    d'étude. L'arbitrage par les sources nationales montre qu'elle vient d'Eurostat, pas
    de CNBC (voir D9).
  - Espagne : la part des mois où le décalage d'un jour l'emporte passe de 42 à 67 % entre
    2016 et 2019 à 100 % en 2020, 2023 et 2024. Le décalage de date s'installe vers 2020.
  - Allemagne : aucune période de bon alignement, avec ou sans décalage.
  La figure `outputs/figures/ecarts_cnbc_eurostat_pb.png` montre l'écart quotidien
  CNBC - Eurostat en pb : décalage permanent d'environ +4 pb sur l'Allemagne, écarts
  ponctuels jusqu'à 25 pb, et pour la France un écart qui s'élargit à partir de 2024.
- **Écarts rapportés à l'ordre de grandeur du spread.** Calcul de
  `gap_relative_to_spread()` dans `src/compare_sources.py`, de 2016 à avril 2025 :
  - en niveau, l'écart absolu moyen vaut 11 % du spread France-Allemagne (47 pb en
    moyenne ; de 3 % en 2025 à 17 % en 2018 et 2021) et 5 % du spread Espagne-Allemagne
    (99 pb en moyenne). C'est un biais notable pour la France, modéré pour l'Espagne ;
  - en variation quotidienne, le désaccord moyen entre les deux sources (3,4 pb) est
    aussi grand que la variation typique du spread elle-même (3,5 pb pour la France,
    3,3 pb pour l'Espagne), soit 87 à 119 % selon les années. Pour une étude
    d'événements, c'est rédhibitoire : le bruit entre sources a la taille du signal.
  - Les spreads étudiés sont France-Allemagne et France-Espagne. Le second ne dépend pas
    du taux allemand ; comme il passe près de zéro en 2024-2025, nous le rapportons à sa
    taille moyenne en valeur absolue (4 % à 16 % de 2016 à 2024, rapport non interprétable
    en 2025). En variation, le désaccord vaut 91 à 110 % de la variation typique.
  - Limite : la variation quotidienne du spread France-Allemagne est plus dispersée chez
    Eurostat (écart-type 5,0 pb) que chez CNBC (1,9 pb). Le désaccord ne dit pas quelle
    source a tort ; Eurostat pourrait lui-même relever la France et l'Allemagne à des
    heures différentes. Nous ne l'avons pas vérifié.
- **Conséquence.** En l'état, les clôtures quotidiennes de CNBC ne conviennent pas à une
  étude d'événements, où un jour de décalage change le résultat, et le spread FR-DE
  mélangerait des relevés pris à des heures différentes. D6 est donc remis en cause.
- **Piste écartée (2026-10-23) : l'intraday CNBC.** Nous voulions reconstruire une clôture
  commune à 17 h 30, heure de Paris, à partir des barres de 5 minutes de CNBC. Sur quinze
  mardis tirés de 2016 à 2026, les trois pays n'ont des barres le même jour qu'à partir de
  mars 2026 ; avant, la plupart des jours sont vides pour au moins un pays (aucun pays le
  2016-06-28 ni le 2025-04-08). Une même requête répétée renvoie toujours le même
  résultat : ces trous sont des lacunes de l'historique, pas des pannes. Les résolutions
  30 minutes et 1 heure sont tout aussi lacunaires. L'intraday ne permet donc pas de
  reconstruire une clôture commune sur notre période.

## D8. Publication des données CNBC dans le dépôt (2026-10-23)

- **Décision.** Nous versionnons les fichiers bruts CNBC dans `data/raw/cnbc/`, comme les
  autres sources, pour que le notebook s'exécute hors ligne.
- **Alternative écartée.** Ne versionner que le script de téléchargement : le notebook ne
  tournerait plus hors ligne pour un lecteur extérieur, ce qui est une condition
  éliminatoire du projet.
- **Risque assumé.** Les conditions d'utilisation de Versant, qui gouvernent cnbc.com
  (https://versantmedia.com/terms/, en vigueur depuis le 2025-09-30), limitent l'usage à
  un usage personnel et non commercial et interdisent l'usage du contenu hors de leurs
  services sans accord écrit. Le dépôt étant public, la publication de ces fichiers n'est
  pas couverte par cette licence.

## D9. Arbitrage par les sources nationales : qui, de CNBC ou d'Eurostat, s'écarte ? (2026-10-23)

- **Méthode.** Nous comparons les variations quotidiennes de CNBC et d'Eurostat à celles
  d'une troisième source, la banque centrale de chaque pays : Banque de France (TEC 10),
  Bundesbank, Banco de España (`scripts/download_national.py`, `src/load_rates.py`,
  `correlation_with_arbiter()` dans `src/compare_sources.py`). Ces séries ne servent qu'à
  ce diagnostic : les spreads de l'analyse ne mélangent pas les sources (D5).
- **Allemagne.** Eurostat suit la Bundesbank presque parfaitement (corrélation des
  variations 0,96 à 0,99 chaque année, même date) ; CNBC non (0,41 à 0,57). C'est CNBC
  qui s'écarte.
- **Espagne.** Eurostat suit le Banco de España (0,78 à 0,89) ; CNBC non (0,11 à 0,49).
  C'est encore CNBC qui s'écarte.
- **France avant juillet 2024.** CNBC et Eurostat s'accordent entre eux (D7) et s'écartent
  tous deux du TEC 10 (0,33 à 0,52 pour Eurostat, 0,35 à 0,54 pour CNBC). Avec un jour de décalage, la corrélation avec le
  TEC 10 monte à 0,6 : le TEC 10 semble relevé à une autre heure de la journée. Nous ne
  l'avons pas vérifié dans la documentation de la Banque de France.
- **France à partir de juillet 2024 : Eurostat change de source.** À partir de juillet
  2024, la série Eurostat pour la France est identique au TEC 10 de la Banque de France :
  100 % des jours ont un écart inférieur à 0,05 pb, contre 3,7 pb en moyenne avant 2024.
  La rupture de juillet 2024 relevée en D7 vient donc d'Eurostat, pas de CNBC.
- **Conséquences.**
  - Eurostat n'est pas une série homogène pour la France : sa méthode change en juillet
    2024, au cœur de notre période. Après cette date, son spread France-Allemagne mélange
    le TEC 10 et une série allemande d'une autre méthode, ce que D5 interdit.
  - CNBC est stable dans le temps pour la France, mais pas aligné sur les banques
    centrales pour l'Allemagne et l'Espagne.
  - Aucune des deux sources n'est donc satisfaisante telle quelle ; le choix de la source
    quotidienne reste ouvert.
