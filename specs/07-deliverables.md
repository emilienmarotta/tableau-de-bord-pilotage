# 07 — Livrables pour le profil Malt

**Statut :** Approved

## Objectif

Transformer le projet technique en livrables présentables sur le profil
Malt : captures, pitch, README final.

## Livrables

- **1 à 2 captures** de l'écran Metabase final (desktop, nette, sans donnée
  sensible réelle puisque tout est fictif) → `docs/dashboard-*.png`.
- **Capture du graphe de lignage dbt** (déjà produite en spec 05, reprise
  ici dans la présentation finale) → `docs/dbt-lineage.png`.
- **3 lignes d'explication** (problème / solution / bénéfice, bénéfice
  formulé comme hypothèse de scénario, jamais comme un résultat mesuré) —
  à mettre en tête du README et réutilisables telles quelles sur le profil
  Malt.
- **README final** : cadrage (questions dirigeant + définitions KPI, reprises
  de la spec 01), schéma d'architecture, instructions de relance
  (`docker compose up`, `generate`, `dbt build`), structure du dépôt,
  limites assumées, mention « projet démo, données fictives ».

## Critères d'acceptation

- [ ] Les captures sont présentes dans `docs/` et référencées dans le README.
- [ ] Le README se lit de bout en bout sans renvoyer ailleurs pour comprendre
  l'essentiel (les specs restent la référence détaillée, pas un prérequis de
  lecture).
- [ ] Les 3 lignes de présentation sont écrites et prêtes à copier sur le
  profil Malt.
- [ ] Tous les critères de réussite globaux de
  [00-vision.md](00-vision.md) sont cochés.
