# CLAUDE.md

Contexte et conventions de ce projet, pour que les prochaines sessions
Claude Code reprennent sans réexpliquer. La session change à chaque
milestone : ce fichier + [ROADMAP.md](ROADMAP.md) + la spec du milestone en
cours doivent suffire à redémarrer.

## Projet

Projet portfolio fictif (profil Malt, data engineer / BI) : tableau de bord
de pilotage (ventes, marges, stocks) pour une PME fictive de commerce de
gros. Données 100 % fictives. Vision complète :
[specs/00-vision.md](specs/00-vision.md).

## Méthode : specs-driven

Chaque fonctionnalité a une spec dans [specs/](specs/) **écrite et validée
avant d'être codée**. Ne pas coder en dehors d'une spec existante ; si le
besoin évolue en cours d'implémentation, mettre à jour la spec en premier,
puis le code. Statuts : `Draft` → `Approved` → `Implemented` (champ en haut
de chaque fichier spec, et dans [specs/README.md](specs/README.md)) — en fin
de milestone, repasser le statut de la/des spec(s) correspondantes à
`Implemented` et cocher la case du milestone dans
[ROADMAP.md](ROADMAP.md).

## Roadmap

Milestones dans [ROADMAP.md](ROADMAP.md), un par grande brique (squelette,
générateur, dbt staging, dbt marts, tests/doc dbt, Metabase, livrables).

## Contrainte de design critique

Répartition stricte des responsabilités (voir
[specs/00-vision.md](specs/00-vision.md)) :
- **Python (`generator/`)** : génération des données fictives et chargement
  dans le schéma `raw` de Postgres. Aucune logique métier.
- **dbt (`dbt_project/`)** : toute la logique métier et tous les KPI (CA,
  marge, couverture de stock, statuts, rangs), en SQL, dans les couches
  `staging` → `intermediate` → `marts`.
- **Metabase** : uniquement de la visualisation sur les marts dbt déjà
  calculés. Jamais de recalcul de KPI dans une requête ad hoc d'une carte.

Si un chiffre affiché dans Metabase n'existe pas déjà comme colonne d'un
mart, c'est qu'il manque une colonne dans un mart dbt — pas une requête
custom côté Metabase.

## Conventions dbt

- Préfixes : `stg_` (staging, vues), `int_` (intermediate, vues), `fct_`
  (table de faits), `mart_` (marts orientés usage, tables).
- Chaque modèle et chaque colonne-KPI documentés dans un fichier YAML, avec
  des descriptions qui reprennent mot pour mot les définitions de
  [specs/01-cadrage-kpi-dashboard.md](specs/01-cadrage-kpi-dashboard.md).
- Seuils de statut de stock centralisés (macro ou `vars`), jamais dupliqués
  en dur dans plusieurs modèles.

## Stack

Docker Compose (Postgres 16, Metabase), Python (venv à la racine du projet :
`.venv/`), dbt-postgres, SQL. Pas d'hébergement : tout tourne en local.

## Workflow Git

- Jamais de commit ni de push direct sur `main`.
- Une branche par milestone : `milestone/m{N}-{slug}` (ex.
  `milestone/m1-generateur`).
- À la fin d'un milestone : commit, push de la branche, ouverture d'une PR
  vers `main` avec `gh pr create`.
- Quand l'utilisateur confirme que la PR a été mergée (sur GitHub) :
  `git checkout main && git pull && git branch -d <branche>`. La branche
  distante est supprimée automatiquement au merge (option
  `delete_branch_on_merge` activée sur le repo) ; sinon, la supprimer
  explicitement (`git push origin --delete <branche>`).
- Dépôt GitHub public (`emilienmarotta/tableau-de-bord-pilotage`), aucun
  secret commité (`.env` est ignoré, seul `.env.example` est versionné).

## Honnêteté du contenu

Rappeler partout où c'est pertinent (README, dashboard, code) que les
données sont fictives et que tout gain de temps ou bénéfice annoncé est une
hypothèse de scénario, jamais un résultat mesuré (cf. spec 00).

## Relation avec le projet 1 (rapport-commercial-auto)

Même univers métier (même PME fictive de commerce de gros), mais dépôt
**techniquement autonome** — pas de Postgres partagé, pas de dépendance
d'infra entre les deux dépôts (raison détaillée dans
[specs/00-vision.md](specs/00-vision.md)).
