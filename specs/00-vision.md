# 00 — Vision et contraintes

**Statut :** Approved

## Objectif

Démontrer, sous forme de projet portfolio, une vraie démarche BI : des données
fictives modélisées proprement avec dbt (staging → marts, testées et
documentées), affichées dans un tableau de bord lisible par un dirigeant non
technique en 30 secondes.

## Scénario (fictif)

PME fictive de commerce de gros (même univers métier que le projet portfolio
[rapport-commercial-auto](https://github.com/emilienmarotta/rapport-commercial-auto) :
même secteur, mêmes types de clients/produits/régions, pour que les deux
projets forment un portfolio cohérent). Le dirigeant passe des heures sur
Excel pour savoir où en sont ses ventes, ses marges et ses stocks. Il veut un
écran qui répond à « est-ce que ça va bien ? » en 30 secondes.

## Lien avec le projet 1 (rapport-commercial-auto)

Dépôt **autonome** : pas de dépendance d'infrastructure envers le projet 1
(pas de Postgres partagé entre les deux dépôts). Raison : le schéma de
données du projet 1 (`raw_ventes`, une seule table plate façon export ERP) ne
couvre pas ce dont ce projet a besoin (clients avec segment, produits avec
prix d'achat, stocks, mouvements de stock) — le réutiliser imposerait de le
réécrire quasi entièrement, ce qui contredirait l'objectif de reproductibilité
indépendante (`docker compose up` doit suffire, sans dépendre d'un autre
dépôt). Cohérence maintenue au niveau du **scénario métier** (même PME
fictive, même univers produit/client), pas au niveau de l'infra.

## Périmètre

- Données 100 % fictives, générées par script (Python + Faker), graine fixe.
- Tout tourne en local via `docker compose` : pas d'hébergement.
- Deux services principaux : **PostgreSQL** (stockage brut + marts dbt) et
  **Metabase** (visualisation). dbt tourne en local (venv Python), pas besoin
  d'un conteneur dédié.

## Outil de visualisation : Metabase

**Décision : Metabase**, en local via Docker.
- Tourne dans Docker (`docker compose up`), se branche directement sur le
  Postgres local → reproductible.
- Rendu professionnel pour un dirigeant, captures d'écran faciles.
- Alternative écartée : Streamlit (demande du code de mise en forme en plus,
  moins immédiat pour une démo "dirigeant"). Looker Studio écarté (exige une
  source de données accessible depuis le cloud).

## Répartition des responsabilités (contrainte de design critique)

- **Python (`generator/`)** : génération des données fictives et chargement
  dans le schéma `raw` de Postgres. Aucune logique métier (KPI, agrégation).
- **dbt (`dbt_project/`)** : toute la logique métier et tous les calculs de
  KPI (CA net, marge, couverture de stock, statuts, etc.), en SQL, dans les
  couches `staging` → `intermediate` → `marts`. Testée et documentée.
- **Metabase** : uniquement de la visualisation sur les marts dbt déjà
  calculés. Pas de logique métier cachée dans une requête SQL ad hoc d'une
  carte Metabase — si un chiffre a besoin d'un calcul, il doit déjà exister
  comme colonne d'un mart.

Cette séparation est un critère de qualité du projet : si les KPI sont
recalculés à la main dans Metabase, le projet ne démontre plus la
modélisation dbt qu'il est censé démontrer.

## Hors périmètre (non-goals)

- Pas d'authentification multi-utilisateurs avancée, pas de vrai ERP.
- Pas de volumétrie réaliste de grande entreprise : quelques centaines de
  clients/produits et 12 mois d'historique suffisent.
- Pas de prévisions / machine learning : uniquement du reporting descriptif.
- Pas de export Metabase "production-grade" (pas de SSO, pas de permissions
  multi-rôles) : une instance de démo locale.

## Honnêteté du portfolio

- Mentionner explicitement « projet démo, données fictives » dans le README
  et sur le profil Malt.
- Aucun bénéfice chiffré présenté comme un résultat mesuré : toujours formulé
  comme hypothèse de scénario.

## Critères de réussite globaux

- [x] `docker compose up` lance Postgres et Metabase sans erreur.
- [x] `dbt build` s'exécute de bout en bout : tous les modèles et tous les
  tests passent (51/51 au 2026-10-13).
- [x] Les KPI du tableau de bord correspondent aux définitions du README
  (vérifiés sur quelques cas calculés à la main — CA net, marge brute, taux
  de marge de septembre 2026 et nombre de produits en alerte stock,
  recoupés par requête SQL directe sur les marts, identiques aux chiffres
  affichés dans Metabase).
- [ ] Le tableau de bord se lit en 30 secondes (testé avec une personne
  extérieure au projet si possible) — validation humaine, à faire par
  l'utilisateur.
- [x] `dbt docs` est généré et le graphe de lignage est capturé.
- [x] README, captures et 3 lignes de présentation prêts pour le profil Malt.

## Risques identifiés

- Dérive de scope sur le nombre de marts/graphiques. → S'en tenir à la liste
  de la spec [01-cadrage-kpi-dashboard.md](01-cadrage-kpi-dashboard.md), pas
  d'ajout sans mise à jour de la spec.
- Logique métier qui migre dans Metabase par facilité (requête SQL custom
  dans une carte). → Revue explicite avant la spec
  [06-metabase-dashboard.md](06-metabase-dashboard.md) : tout chiffre affiché
  doit être traçable jusqu'à une colonne d'un mart dbt.
- Jeu de données trop lisse pour être intéressant (pas de rupture, pas de
  produit en perte). → Contraintes explicites dans
  [02-data-generator.md](02-data-generator.md) (saisonnalité, produits stars,
  marge faible/négative, ruptures, surstocks).
