# Metabase — reproduire le dashboard

L'édition Metabase utilisée ici est l'édition open-source. Les commandes CLI
`export`/`import` (sérialisation YAML d'une collection) appartiennent à
Metabase Enterprise Edition et échouent sur cette image avec :

```
Command failed with exception: The 'v2-dump!' command is only available in Metabase Enterprise Edition.
```

La configuration du dashboard est donc reproduite via l'**API REST de
Metabase**, pilotée par [`setup_metabase.py`](setup_metabase.py). Ce script
est la source de vérité de la configuration (équivalent code d'un export
YAML) : il recrée la connexion à la base, les 11 questions et le dashboard
avec ses filtres, de façon idempotente (relançable sans dupliquer quoi que
ce soit — les cartes/dashboard d'un run précédent sont supprimés puis
recréés).

## Recréer le dashboard à l'identique

```bash
docker compose up -d
python3 generator/generate.py --reset
cd dbt_project && dbt build --profiles-dir . && cd ..
python3 -m venv .venv && source .venv/bin/activate   # si pas déjà fait
pip install requests
set -a && source .env && set +a
python3 metabase/setup_metabase.py
```

Le script affiche l'URL du dashboard créé (ex.
`http://localhost:3000/dashboard/<id>`). Identifiants admin : voir
`METABASE_ADMIN_EMAIL` / `METABASE_ADMIN_PASSWORD` dans `.env`.

## Ce que le script crée

- **Connexion base** `tableau_de_bord_pilotage` sur Postgres, limitée au
  schéma `marts` (aucune exposition de `raw`/`staging`/`intermediate` dans
  Metabase).
- **11 cartes**, chacune une lecture directe d'un mart dbt ou un `GROUP BY`
  simple dessus (jamais de recalcul de KPI) :
  - Bandeau (5 cartes) : CA du mois, marge brute du mois, taux de marge du
    mois, panier moyen du mois (toutes `mart_ventes_mensuelles`, en
    `smartscalar` pour la comparaison automatique au mois précédent),
    produits en alerte stock (`mart_stock_sante`).
  - Évolution CA & marge 12 mois (`mart_ventes_mensuelles`, courbe).
  - Marge brute par catégorie (`fct_ventes`, `GROUP BY categorie`, barres).
  - Top 10 produits (`mart_performance_produits`, table).
  - Répartition des statuts de stock (`mart_stock_sante`, donut) + liste des
    produits critiques (table).
  - CA par région (`mart_ventes_par_region_client`, barres).
- **1 dashboard** « Pilotage commercial » avec la disposition en grille et
  **3 filtres natifs** (Période, Catégorie, Région) mappés sur les colonnes
  correspondantes des cartes concernées — pas de requête paramétrée custom.

## Limite connue

Les cartes du bandeau et « Évolution CA & marge » s'appuient sur
`mart_ventes_mensuelles`, qui n'a pas de colonne catégorie/région (agrégat
mensuel toutes catégories/régions confondues) : le filtre Période leur est
mappé, mais pas Catégorie/Région. C'est une conséquence du grain des marts
dbt, pas une limitation du dashboard.
