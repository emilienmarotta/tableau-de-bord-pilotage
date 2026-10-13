# 06 — Tableau de bord Metabase

**Statut :** Implemented

## Objectif

Un écran principal, conforme à la maquette de la spec
[01-cadrage-kpi-dashboard.md](01-cadrage-kpi-dashboard.md), compris en 30
secondes par un dirigeant non technique.

## Contenu de l'écran (6 blocs + bandeau de filtres)

1. **Bandeau 4 chiffres clés** (vs mois précédent) : CA du mois, marge brute
   (€ et %), panier moyen, nombre de produits en alerte stock
   (`rupture` + `a_reapprovisionner` dans `mart_stock_sante`).
2. **Évolution CA & marge sur 12 mois** : courbe, source `mart_ventes_mensuelles`.
3. **Marge par catégorie** : barres, source agrégation de `fct_ventes` par
   `categorie` (ou nouvelle question Metabase basée sur `fct_ventes`, sans
   recalcul de `ca_net`/`marge_brute` — uniquement un `GROUP BY`).
4. **Top 10 produits** par CA avec taux de marge : table, source
   `mart_performance_produits` triée par `ca_net` desc, limite 10.
5. **Santé des stocks** : donut rupture/à réapprovisionner/OK/surstock +
   liste des produits critiques (`rupture` ou `a_reapprovisionner`), source
   `mart_stock_sante`.
6. **CA par région** : barres, source `mart_ventes_par_region_client`.

Filtres du dashboard : période (sur `date_commande`), catégorie, région —
appliqués via les filtres natifs Metabase liés aux colonnes correspondantes
des marts, pas via des requêtes paramétrées custom.

## Règles de design

- Palette limitée (2-3 couleurs cohérentes sur tout l'écran, pas une couleur
  différente par graphique).
- Titres explicites et si possible dynamiques (ex. texte conditionnel
  "Marge en baisse sur [catégorie]" seulement si simple à faire en Metabase ;
  sinon titre statique mais parlant, ex. "Marge brute par catégorie").
- Pas plus de 6-8 blocs sur l'écran principal (respecté : 6 blocs + bandeau).

## Reproductibilité de la configuration Metabase

Metabase (édition open-source) expose une fonctionnalité de **sérialisation**
(export/import de collections en YAML) via la CLI du jar/image :
`docker compose exec metabase metabase export-dashboards ...` (selon version
disponible dans l'image utilisée). Si la sérialisation n'est pas disponible
dans l'édition utilisée, documenter précisément dans
`metabase/README.md` la séquence manuelle pour recréer le dashboard
(connexion à la base, questions une par une, dashboard, filtres) — avec
suffisamment de détail pour qu'une autre personne retrouve exactement le
même écran.

## Critères d'acceptation

- [ ] Le dashboard affiche les 6 blocs + filtres décrits ci-dessus.
- [ ] Chaque carte Metabase pointe sur un mart dbt (ou un `GROUP BY` simple
  dessus) — aucune carte ne recalcule un KPI déjà défini en dbt.
- [ ] La configuration est exportée dans `metabase/` ou documentée pour être
  recréée à l'identique.
- [ ] Testé en le montrant à une personne extérieure au projet : elle doit
  pouvoir dire "ça va bien / ça ne va pas bien" en moins de 30 secondes.
