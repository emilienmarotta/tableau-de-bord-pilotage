# Roadmap

Découpage en milestones, dans l'ordre d'implémentation. Chaque milestone est
livré via une branche dédiée et une pull request (voir [CLAUDE.md](CLAUDE.md)
pour le workflow Git).

- [x] **M0 — Squelette, cadrage et environnement.** `docker-compose.yml`
  (Postgres, Metabase), `.env.example`, `.gitignore`, specs/, README initial,
  maquette du dashboard. Specs :
  [00-vision.md](specs/00-vision.md),
  [01-cadrage-kpi-dashboard.md](specs/01-cadrage-kpi-dashboard.md).
- [x] **M1 — Générateur de données fictives.** Clients, produits, commandes,
  lignes de commande, stocks, mouvements de stock, chargés dans le schéma
  `raw` de Postgres. Spec : [02-data-generator.md](specs/02-data-generator.md).
- [x] **M2 — dbt staging.** Un `stg_*` par source, sources + tests de
  fraîcheur. Spec : [03-dbt-staging.md](specs/03-dbt-staging.md).
- [x] **M3 — dbt intermediate et marts.** `int_lignes_vente_enrichies`,
  `fct_ventes`, `mart_ventes_mensuelles`, `mart_performance_produits`,
  `mart_stock_sante`, `mart_ventes_par_region_client`. Spec :
  [04-dbt-marts.md](specs/04-dbt-marts.md).
- [x] **M4 — Tests et documentation dbt.** Tests génériques + personnalisés,
  documentation YAML, `dbt docs`, capture du lignage. Spec :
  [05-dbt-tests-docs.md](specs/05-dbt-tests-docs.md).
- [x] **M5 — Tableau de bord Metabase.** Écran principal (4 KPI + 5 blocs +
  filtres), export/documentation de la configuration. Spec :
  [06-metabase-dashboard.md](specs/06-metabase-dashboard.md).
- [ ] **M6 — Livrables portfolio Malt.** Captures, lignage, 3 lignes de
  présentation, README final. Spec :
  [07-deliverables.md](specs/07-deliverables.md).

Détail des exigences et critères d'acceptation de chaque milestone :
[specs/](specs/) (voir [specs/README.md](specs/README.md) pour le statut de
chaque spec).
