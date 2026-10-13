# 01 — Cadrage : questions, KPI, maquette

**Statut :** Approved

Cadrage rédigé comme pour un vrai client, avant toute ligne de code. But :
montrer sur le profil Malt une démarche « je cadre le besoin avant de coder ».

## Questions auxquelles le dirigeant veut répondre

1. Mon chiffre d'affaires progresse-t-il mois après mois ?
2. Ma marge progresse-t-elle au même rythme que mon CA, ou se dégrade-t-elle ?
3. Quelles catégories de produits sont les plus rentables ?
4. Quels sont mes produits qui font le plus de CA, et sont-ils aussi ceux qui
   font le plus de marge ?
5. Quels produits me font perdre de la marge (marge faible ou négative) ?
6. Quels produits vont tomber en rupture, ou dormissent en surstock ?
7. Quelle région génère le plus de CA, et laquelle est en retard ?

## Définitions des KPI (référence unique, reprise dans le README final)

- **CA net** = somme (quantité × prix unitaire facturé × (1 − remise)).
- **Marge brute (€)** = CA net − somme (quantité × prix d'achat).
- **Taux de marge (%)** = marge brute ÷ CA net.
- **Panier moyen** = CA net ÷ nombre de commandes.
- **Couverture de stock (jours)** = quantité en stock ÷ ventes moyennes
  journalières des 30 derniers jours.
- **Statut de stock** (seuils paramétrables en macro/variable dbt) :
  - `rupture` : stock = 0 ;
  - `à réapprovisionner` : stock sous le seuil de réapprovisionnement OU
    couverture < 7 jours ;
  - `surstock` : couverture > 90 jours ;
  - `OK` : sinon.
- **Variation vs période précédente** : comparaison du mois en cours
  (ou dernier mois complet disponible) au mois précédent, en valeur et en %.

## Maquette du tableau de bord (croquis texte, voir aussi `docs/maquette-dashboard.md`)

Un seul écran principal, pensé pour se lire en 30 secondes, pas plus de 6-8
blocs :

```
┌─────────────────────────────────────────────────────────────────────┐
│ Filtres : [Période ▾] [Catégorie ▾] [Région ▾]                       │
├─────────────────────────────────────────────────────────────────────┤
│  CA du mois     Marge brute      Panier moyen     Produits en alerte │
│  XXX k€ (+X%)   XXX k€ / XX%     XXX €  (+X%)      XX produits       │
├───────────────────────────────────┬───────────────────────────────── │
│ Évolution CA & marge (12 mois)     │ Marge par catégorie (barres)    │
│ [courbe double axe]                │ [barres horizontales triées]   │
├───────────────────────────────────┼───────────────────────────────── │
│ Top 10 produits (CA + taux marge)  │ Santé des stocks                │
│ [table triée par CA]               │ [donut rupture/réappro/OK/sur-  │
│                                     │  stock] + liste produits critq.│
├───────────────────────────────────┴───────────────────────────────── │
│ CA par région (barres)                                               │
└─────────────────────────────────────────────────────────────────────┘
```

Règles de design (reprises dans la spec Metabase) :
- peu de couleurs, cohérentes sur tout l'écran ;
- titres qui disent quelque chose (« Marge en baisse sur la catégorie X »
  plutôt que « Graphique 3 ») — autant que possible dynamique, sinon au moins
  parlant dans son libellé statique ;
- pas plus de 6 à 8 blocs sur l'écran principal.

## Hors cadrage (reporté si le temps le permet)

- Comparaison N vs N-1 (année précédente) : non demandée explicitement par le
  dirigeant dans ce scénario, à ne pas ajouter sans mise à jour de cette spec.
- Segmentation par segment client (grand compte / PME / détaillant) : le
  champ existe dans les données (`clients.segment`) pour la richesse du
  modèle dbt, mais n'apparaît pas forcément sur l'écran principal — possible
  filtre bonus si le temps le permet, pas un engagement.
