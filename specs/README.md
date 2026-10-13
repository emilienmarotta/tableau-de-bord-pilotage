# Specs — tableau-de-bord-pilotage

Méthode : chaque fonctionnalité a une spec écrite et validée avant d'être codée.
Une spec ne change pas en cours d'implémentation sans être mise à jour ici en premier.

Statut possible : `Draft` (à valider) · `Approved` (prête à implémenter) · `Implemented` (code conforme livré).

| Spec | Domaine | Statut |
|---|---|---|
| [00-vision.md](00-vision.md) | Vision, contraintes, critères de réussite globaux | Approved |
| [01-cadrage-kpi-dashboard.md](01-cadrage-kpi-dashboard.md) | Questions dirigeant, définitions KPI, maquette | Approved |
| [02-data-generator.md](02-data-generator.md) | Générateur de données fictives + chargement Postgres | Implemented |
| [03-dbt-staging.md](03-dbt-staging.md) | Modèles dbt staging | Implemented |
| [04-dbt-marts.md](04-dbt-marts.md) | Modèles dbt intermediate + marts | Approved |
| [05-dbt-tests-docs.md](05-dbt-tests-docs.md) | Tests dbt + documentation + lignage | Approved |
| [06-metabase-dashboard.md](06-metabase-dashboard.md) | Dashboard Metabase | Approved |
| [07-deliverables.md](07-deliverables.md) | Livrables portfolio Malt | Approved |

Ordre d'implémentation recommandé : 00/01 → 02 → 03 → 04 → 05 → 06 → 07
(chaque spec consomme le contrat produit par la précédente). Correspondance
avec les milestones de la [ROADMAP](../ROADMAP.md) : 00+01 → M0,
02 → M1, 03 → M2, 04 → M3, 05 → M4, 06 → M5, 07 → M6.
