# Tableau de bord de pilotage

> Projet de démonstration (portfolio Malt, profil data engineer / BI).
> **Données 100 % fictives.**

## Le problème

Dans une PME fictive de commerce de gros, le dirigeant passe des heures sur
Excel pour savoir où en sont ses ventes, ses marges et ses stocks.

## La solution

Les données sont préparées de façon fiable avec dbt + SQL (staging → marts,
testées et documentées), puis affichées dans un tableau de bord Metabase qui
répond à « est-ce que ça va bien ? » en 30 secondes.

## Architecture

```
Générateur de données fictives (Python + Faker)
        ↓
PostgreSQL (schéma raw)
        ↓
dbt : staging → intermediate → marts (+ tests + documentation)
        ↓
Metabase (tableau de bord)
```

Détail complet des choix et des contrats entre composants : voir
[`specs/`](specs/).

## Statut du projet

Projet construit en suivant une approche *specs-driven* : chaque brique est
spécifiée dans [`specs/`](specs/) avant d'être codée. Avancement par
milestone : [`ROADMAP.md`](ROADMAP.md). État détaillé de chaque spec :
[`specs/README.md`](specs/README.md).

Le cadrage (questions du dirigeant, définitions précises des KPI, maquette
du dashboard) est figé dans
[`specs/01-cadrage-kpi-dashboard.md`](specs/01-cadrage-kpi-dashboard.md) et
[`docs/maquette-dashboard.md`](docs/maquette-dashboard.md).

## Lancer la démo

```bash
cp .env.example .env
docker compose up -d
```

- Metabase : http://localhost:3000
- Postgres : localhost:5433 (identifiants dans `.env`) — port volontairement
  différent du standard 5432 pour pouvoir tourner en parallèle du projet 1
  ([rapport-commercial-auto](https://github.com/emilienmarotta/rapport-commercial-auto))
  sans conflit.

Puis générer les données fictives (schéma `raw`, 12 mois d'historique,
reproductible à l'identique grâce à une graine fixe) :

```bash
python3 -m venv .venv
.venv/bin/pip install -r generator/requirements.txt
.venv/bin/python generator/generate.py --reset
```

Le build dbt (staging → marts) sera documenté ici au fil des prochains
milestones (voir [`ROADMAP.md`](ROADMAP.md)).

## Structure du dépôt

```
tableau-de-bord-pilotage/
├── docker-compose.yml
├── .env.example
├── specs/                 # spécifications (lues avant d'écrire du code)
├── generator/              # génération des données fictives
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/              # tests métier personnalisés
│   └── macros/
├── metabase/               # export / instructions de configuration
└── docs/                   # captures, maquette, lignage dbt
```

## Limites assumées

- Données entièrement fictives, aucun lien avec une vraie PME.
- Démo locale uniquement (pas d'hébergement).
- Pas de volumétrie réaliste de grande entreprise, pas de prévisions : ce
  projet démontre une démarche BI, pas un produit prêt pour la production.
