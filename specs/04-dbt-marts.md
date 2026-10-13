# 04 — dbt : intermediate et marts

**Statut :** Implemented

## Objectif

Couche où vit toute la logique métier : CA, marge, couverture de stock,
statuts, rangs. Chaque KPI affiché dans Metabase doit être une colonne d'un
de ces modèles — jamais recalculé côté Metabase (cf. contrainte de design,
spec 00).

## Intermediate

### `int_lignes_vente_enrichies`
Une ligne par ligne de commande (`stg_lignes_commande`), jointe à
`stg_produits` (coût, catégorie) et à `stg_commandes`/`stg_clients`
(date, client, région, segment). Colonnes calculées :
- `ca_net` = `quantite * prix_unitaire_facture * (1 - remise)`
- `cout_total` = `quantite * prix_achat`
- `marge_brute` = `ca_net - cout_total`

Matérialisation : `view`.

## Marts (matérialisation : `table`)

### `fct_ventes`
Une ligne par ligne de commande (= `int_lignes_vente_enrichies` avec les
colonnes finalisées) : `ligne_id`, `commande_id`, `date_commande`,
`client_id`, `region`, `segment`, `produit_id`, `categorie`, `quantite`,
`ca_net`, `cout_total`, `marge_brute`. Table de faits de référence pour tous
les autres marts de ventes (évite de recalculer `ca_net`/`marge_brute`
plusieurs fois).

### `mart_ventes_mensuelles`
Group by mois (`date_trunc('month', date_commande)`) : `ca_net` (somme),
`marge_brute` (somme), `taux_marge` (`marge_brute / ca_net`),
`nb_commandes` (distinct `commande_id`), `panier_moyen`
(`ca_net / nb_commandes`). Une ligne par mois sur les 12 mois.

### `mart_performance_produits`
Group by `produit_id` (+ `categorie`, `libelle`) : `ca_net`, `marge_brute`,
`taux_marge`, `quantite_vendue`. Colonnes de rang : `rang_ca_global`
(`dense_rank` sur `ca_net` toutes catégories), `rang_ca_categorie`
(`dense_rank` sur `ca_net` au sein de la catégorie).

### `mart_stock_sante`
Une ligne par produit, à partir de `stg_stocks` + `stg_produits` +
agrégation de `stg_mouvements_stock` (sorties) sur les 30 derniers jours
disponibles :
- `vente_moy_jour_30j` = somme des sorties des 30 derniers jours ÷ 30
- `couverture_jours` = `quantite_stock / vente_moy_jour_30j` (NULL/∞ géré
  explicitement si `vente_moy_jour_30j = 0` → traité comme surstock si
  `quantite_stock > 0`, sinon rupture)
- `statut_stock` (seuils définis une seule fois dans une macro dbt
  `get_stock_thresholds()` ou des variables `dbt_project.yml`, pas en dur
  dans plusieurs modèles) : `rupture` / `a_reapprovisionner` / `ok` /
  `surstock`, selon les règles de la spec 01.

### `mart_ventes_par_region_client`
Group by `region` (+ `segment` en colonne secondaire) : `ca_net`,
`marge_brute`, `nb_clients_actifs` (distinct `client_id` ayant commandé).

## Conventions

- Préfixes cohérents : `stg_`, `int_`, `fct_`, `mart_`.
- Pas de logique métier dans `staging` (déjà couvert spec 03) ; toute
  nouvelle colonne calculée doit vivre en `intermediate` ou `marts`, jamais
  directement dans une requête Metabase.
- Les seuils de stock (`rupture`, `a_reapprovisionner`, `surstock`) sont
  centralisés (macro ou `vars` dans `dbt_project.yml`), pour rester
  paramétrables sans dupliquer la logique.

## Critères d'acceptation

- [ ] `dbt run` (staging + intermediate + marts) passe de bout en bout.
- [ ] Chaque mart contient au moins une ligne cohérente avec les règles de la
  spec 02 (ex. au moins un produit `rupture`, un `surstock`).
- [ ] Les définitions de KPI calculées correspondent mot pour mot à la spec
  [01-cadrage-kpi-dashboard.md](01-cadrage-kpi-dashboard.md).
