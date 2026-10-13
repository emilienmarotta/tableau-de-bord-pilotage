# 05 — dbt : tests et documentation

**Statut :** Approved

## Objectif

Donner confiance dans les chiffres affichés dans Metabase, et produire un
graphe de lignage présentable sur le profil Malt.

## Tests génériques (complète la liste déjà posée en staging, spec 03)

- `unique` + `not_null` sur toutes les clés primaires des marts
  (`fct_ventes.ligne_id`, `mart_performance_produits.produit_id`,
  `mart_stock_sante.produit_id`).
- `accepted_values` sur `mart_stock_sante.statut_stock`
  (`rupture`, `a_reapprovisionner`, `ok`, `surstock`).
- `relationships` entre `fct_ventes.produit_id`/`client_id` et les
  dimensions.

## Tests métier personnalisés (`dbt_project/tests/`, tests singuliers)

1. **`assert_ca_net_non_negatif`** : échoue si une ligne de `fct_ventes` a un
   `ca_net < 0` (une remise mal appliquée ne doit jamais rendre le CA
   négatif).
2. **`assert_marge_coherente`** : échoue si `marge_brute != ca_net -
   cout_total` à `0.01` près (non-régression du calcul si quelqu'un modifie
   `fct_ventes` plus tard sans mettre à jour la formule partout).
3. **`assert_stock_jamais_negatif`** : échoue si `mart_stock_sante` contient
   une `quantite_stock < 0`.

## Documentation

- Chaque modèle (`staging`, `intermediate`, `marts`) a une `description:`
  dans son fichier YAML.
- Chaque colonne qui porte un KPI (CA, marge, couverture, statut) a une
  `description:` qui reprend exactement la définition de la spec
  [01-cadrage-kpi-dashboard.md](01-cadrage-kpi-dashboard.md) — le but est que
  `dbt docs` serve de documentation KPI officielle, cohérente avec le README.
- `dbt docs generate` + `dbt docs serve` pour vérifier localement.
- Capture d'écran du graphe de lignage (DAG complet staging → marts) dans
  `docs/dbt-lineage.png`.

## Critères d'acceptation

- [ ] `dbt test` passe à 100% (génériques + personnalisés).
- [ ] `dbt docs generate` ne lève aucune erreur/warning de documentation
  manquante sur les modèles marts.
- [ ] `docs/dbt-lineage.png` capturé et lisible (zoomé sur les marts, pas
  juste une vignette illisible).
