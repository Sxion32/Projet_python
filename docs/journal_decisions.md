# Journal des décisions

Nous consignons ici chaque choix de méthode et chaque biais repéré, avec sa date, les
alternatives écartées, notre justification et le biais qu'il peut introduire. Une décision
marquée « en cours » n'est pas encore tranchée.

## Date de rupture : le 10 juin 2024 (2026-11-20)

- **Décision.** `BREAK_DATE` vaut le lundi 10 juin 2024, premier jour de marché après
  l'annonce de la dissolution de l'Assemblée nationale, le dimanche 9 juin 2024 au soir
  (décret du 9 juin 2024 portant dissolution de l'Assemblée nationale).
- **Alternatives écartées.** Le 9 juin 2024, jour de l'annonce, qui est un dimanche sans
  marché ; une date de rupture estimée à partir des données (le jour où le spread change
  le plus), qui ferait choisir la rupture par le résultat qu'elle doit expliquer.
- **Justification.** La date vient d'un événement daté par une source officielle,
  indépendamment de l'évolution du spread.
- **Biais possible.** Le marché a pu anticiper une partie du choc, ou le digérer sur
  plusieurs jours : une rupture ponctuelle simplifie un ajustement progressif. Les
  élections législatives anticipées (30 juin et 7 juillet 2024) tombent dans la période
  « après ».

## Deux sous-périodes : avant et après la dissolution (2026-11-20)

- **Décision.** Les statistiques descriptives par période utilisent deux sous-périodes :
  du 1er janvier 2016 au 9 juin 2024, puis du 10 juin 2024 à la dernière séance
  disponible (`PERIODS` dans `spreads/config.py`).
- **Alternative écartée.** Un découpage plus fin (2016-2019, Covid 2020-2021, hausse des
  taux de 2022 à juin 2024, après la dissolution). Il serait plus riche, mais chaque borne
  demanderait sa propre justification par un événement daté indépendamment.
- **Justification.** Notre question porte sur ce qui change après la dissolution ; deux
  périodes suffisent et restent cohérentes avec la date de rupture.
- **Biais possible.** La période « avant » mélange des régimes très différents : taux
  négatifs, Covid, hausse des taux de la BCE à partir de 2022. Sa moyenne peut masquer une
  dégradation de la position française déjà engagée avant juin 2024.
