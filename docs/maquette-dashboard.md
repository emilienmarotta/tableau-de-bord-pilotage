# Maquette du tableau de bord

Croquis réalisé avant codage (cadrage, voir
[`specs/01-cadrage-kpi-dashboard.md`](../specs/01-cadrage-kpi-dashboard.md)).
Un seul écran, lisible en 30 secondes, 6 blocs + un bandeau de filtres.

```
┌───────────────────────────────────────────────────────────────────────┐
│ Filtres :  [ Période ▾ ]   [ Catégorie ▾ ]   [ Région ▾ ]              │
├───────────────────────────────────────────────────────────────────────┤
│  CA du mois        Marge brute          Panier moyen     Produits en   │
│  142 k€  (+6%)     38 k€ / 27%  (+1pt)  312 €  (+3%)     alerte : 14   │
├─────────────────────────────────────┬───────────────────────────────── │
│ Évolution CA & marge (12 mois)       │ Marge par catégorie              │
│                                       │                                  │
│   €   ╭─╮  ╭──╮                      │  Emballage       ████████ 31%   │
│  CA ──╯ ╰──╯  ╰──── (courbe)          │  Hygiène         ██████ 26%     │
│  Marge - - - - - - - (courbe pointillé)│  Boissons       ████ 18%       │
│                                       │  Alimentaire     ██ 9%          │
├─────────────────────────────────────┼───────────────────────────────── │
│ Top 10 produits (CA + taux marge)    │ Santé des stocks                 │
│                                       │                                  │
│  Produit X     18k€   32%            │   ╭──────╮   OK : 142            │
│  Produit Y     15k€   29%            │  │ donut │   Réappro : 11       │
│  Produit Z     12k€    4%  ⚠         │   ╰──────╯   Rupture : 3        │
│  ...                                 │               Surstock : 9      │
│                                       │  Liste des produits critiques → │
├─────────────────────────────────────┴───────────────────────────────── │
│ CA par région                                                           │
│  Île-de-France ████████████  Occitanie ██████  Grand Est ████  ...     │
└───────────────────────────────────────────────────────────────────────┘
```

Règles de design : palette limitée (2-3 couleurs cohérentes), titres qui
disent quelque chose plutôt que « Graphique 3 », pas plus de 6-8 blocs. Ces
règles et le contenu exact de chaque bloc sont détaillés dans
[`specs/06-metabase-dashboard.md`](../specs/06-metabase-dashboard.md).
