# Brief pour la présentation du projet sur le profil Malt

> Ce document rassemble tout le matériau nécessaire pour rédiger la fiche
> projet du profil Malt (description, images, résultat, compétences
> démontrées). Il est destiné à être donné tel quel à une autre session
> Claude, avec une consigne du type : « aide-moi à remplir mon profil Malt
> à partir de ce brief ». Toutes les images référencées sont dans ce même
> dossier (`docs/`).

## Lien du projet

- Dépôt GitHub (public) : https://github.com/emilienmarotta/tableau-de-bord-pilotage
- README du projet (point d'entrée) : https://github.com/emilienmarotta/tableau-de-bord-pilotage/blob/main/README.md
- Projet complémentaire du même portfolio (même PME fictive, dépôt
  technique autonome) : https://github.com/emilienmarotta/rapport-commercial-auto

## Pitch court (2-3 lignes, pour un champ "résumé")

Tableau de bord de pilotage commercial (ventes, marges, stocks) pour une
PME fictive de commerce de gros : données générées par script, modélisées
et calculées avec dbt (staging → marts, testées et documentées), puis
visualisées dans Metabase. Projet portfolio avec données 100 % fictives,
construit en méthode specs-driven (chaque brique spécifiée puis codée).

## Contexte / problème (pour un champ "description", partie 1)

Scénario fictif : dans une PME de commerce de gros, le dirigeant passe des
heures chaque mois sur Excel pour savoir où en sont ses ventes, ses marges
et ses stocks — consolider plusieurs exports, recalculer des totaux à la
main, repérer les produits qui partent en rupture ou en surstock. Un
travail répétitif et peu fiable, qui ne répond pas vite à la question
simple : « est-ce que ça va bien ? ».

## Solution (pour un champ "description", partie 2)

Un pipeline de données complet, bout en bout :

```
Générateur de données fictives (Python + Faker, graine fixe)
        ↓ (chargement direct, pas de logique métier)
PostgreSQL — schéma raw
        ↓
dbt : staging → intermediate → marts
      (toute la logique métier et tous les KPI, testés et documentés)
        ↓
Metabase — uniquement de la visualisation sur les marts déjà calculés
```

Le dirigeant ouvre un seul écran Metabase et voit, en 30 secondes : 4 KPI
clés du mois avec leur variation vs le mois précédent (CA, marge brute,
panier moyen, produits en alerte stock), l'évolution CA & marge sur 12
mois, la marge par catégorie, le top 10 produits, la santé des stocks
(donut + liste des produits critiques), et le CA par région. Le tout
filtrable nativement par période, catégorie et région — sans aucune
requête SQL ad hoc côté Metabase : chaque chiffre affiché est une colonne
d'un mart dbt déjà calculé, jamais un recalcul caché dans une carte.

### Vue d'ensemble du dashboard

![Tableau de bord Pilotage commercial : bandeau de 4 KPI (CA, marge, panier moyen, alertes stock), évolution CA et marge sur 12 mois, marge par catégorie, top 10 produits, répartition des statuts de stock, CA par région](./dashboard-pilotage-commercial.png)

### Filtres natifs en action

Exemple avec le filtre Catégorie actif sur « textile » : les cartes
concernées (marge par catégorie, top 10, stocks) se restreignent
immédiatement, sans requête custom — juste un filtre Metabase natif mappé
sur les colonnes des marts.

![Même dashboard filtré sur la catégorie textile](./dashboard-pilotage-commercial-filtre-categorie.png)

### Lignage dbt (staging → intermediate → marts)

![Graphe de lignage dbt généré depuis le manifest, montrant le flux staging vers intermediate vers marts](./dbt-lineage.png)

## Résultat (pour un champ "résultat" / "démo")

Les chiffres affichés ont été vérifiés à la main, indépendamment de
Metabase, par requête SQL directe sur les marts : pour septembre 2026, CA
net 479 190,69 €, marge brute 163 188,55 €, taux de marge 34,06 %, et 29
produits en alerte stock — identiques aux chiffres affichés sur le
dashboard. `dbt build` passe à 51/51 tests (génériques + personnalisés) de
bout en bout.

## Ce que le projet démontre techniquement (pour un champ "compétences")

- **Modélisation de données (dbt)** : couches `staging` → `intermediate` →
  `marts`, toute la logique métier et tous les KPI (CA net, marge brute,
  taux de marge, couverture de stock, statuts de stock) portés par du SQL
  testé et documenté — jamais recalculés côté outil de visualisation.
- **Tests et documentation dbt** : tests génériques (unicité, non-nullité,
  valeurs acceptées, relations) et tests métier personnalisés (ex. marge
  cohérente, stock jamais négatif), documentation YAML reprenant les
  définitions métier, graphe de lignage généré depuis le manifest dbt.
- **Python** : génération de données fictives réalistes et volumineuses
  (saisonnalité, produits stars, marges faibles/négatives, ruptures,
  surstocks délibérément injectés pour que le jeu de données soit
  intéressant à analyser), chargement direct en base, sans logique métier
  côté Python.
- **PostgreSQL** : stockage du schéma brut et des marts calculés.
- **Metabase (via API REST)** : construction du dashboard pilotée par un
  script Python idempotent (connexion base scopée au schéma `marts`,
  création des questions, assemblage du dashboard et de ses filtres
  natifs) plutôt qu'à la main dans l'interface — configuration
  reproductible et versionnée comme du code.
- **Docker / Docker Compose** : stack à deux services (PostgreSQL,
  Metabase), 100 % reproductible en local.
- **Conception et rigueur** : répartition stricte des responsabilités entre
  les couches (Python ne fait aucun calcul métier, dbt porte tous les KPI,
  Metabase ne fait que de la visualisation), méthode *specs-driven* (une
  spec écrite et validée avant chaque brique de code), workflow Git avec
  une branche et une pull request par milestone.
- **Résolution de contrainte réelle** : la fonctionnalité de sérialisation
  export/import de Metabase (qui permettrait un export YAML classique de la
  configuration) s'est révélée réservée à l'édition Entreprise sur l'image
  utilisée. Contournement documenté et mis en œuvre : piloter l'API REST de
  Metabase avec un script Python idempotent, qui sert à la fois d'outil de
  construction et de configuration versionnée dans le dépôt.

## Compétences / tags suggérés

dbt · SQL · PostgreSQL · Metabase · Business Intelligence · modélisation de
données · data engineering · Python · Docker / Docker Compose · tests de
données · documentation technique · spécification technique
(specs-driven development) · Git / GitHub (PR, revue, branches) ·
tableau de bord / reporting décisionnel.

## Méthodologie de travail (bon point pour un profil freelance)

Projet découpé en 7 milestones (M0 à M6), chacun livré via une branche
dédiée et une pull request vers `main`, avec des spécifications écrites
avant le code dans [`specs/`](../specs/) :

1. Squelette, cadrage (questions dirigeant, définitions KPI, maquette) et
   environnement Docker.
2. Générateur de données fictives, chargement direct en PostgreSQL.
3. dbt staging (un modèle par source, tests de fraîcheur).
4. dbt intermediate et marts (tous les KPI calculés et documentés).
5. Tests dbt (génériques + personnalisés), documentation, lignage.
6. Dashboard Metabase (construit via API REST, filtres natifs).
7. Livrables portfolio (ce document, README final, captures).

Détail : [ROADMAP.md](../ROADMAP.md) et [specs/README.md](../specs/README.md).

## Honnêteté / limites assumées (à ne pas occulter dans la présentation)

- Toutes les données sont **fictives**, générées par script — aucun lien
  avec une vraie PME.
- Le gain de temps n'est **pas mesuré** : c'est une hypothèse de scénario
  (remplacer une consolidation Excel manuelle mensuelle), présentée comme
  telle.
- Démo locale uniquement (`docker compose up`), pas d'hébergement, pas
  d'authentification multi-utilisateurs avancée.
- Pas de volumétrie réaliste de grande entreprise, pas de prévisions /
  machine learning : le projet démontre une démarche BI de bout en bout
  (cadrage → modélisation → visualisation), pas un produit prêt pour la
  production.
- La lecture du dashboard "en 30 secondes" a été conçue pour ça (peu de
  blocs, titres parlants, palette limitée) mais le test avec une personne
  réellement extérieure au projet reste à faire par l'utilisateur — ne pas
  la présenter comme déjà validée par un tiers si ce n'est pas encore fait.

## Pour la session Claude qui reçoit ce brief

Objectif : aider à remplir une fiche de projet sur le profil Malt de
l'utilisateur (probablement : titre, description courte, description
longue, compétences/tags, rôle sur le projet, lien vers le dépôt, visuels).
Utiliser le contenu ci-dessus comme matière première, l'adapter au format
et à la longueur exacte demandés par les champs du profil Malt, en gardant
le ton honnête sur le caractère "démo / données fictives" du projet (ne
jamais présenter le gain de temps comme un résultat mesuré, ni le test de
lisibilité en 30 secondes comme déjà validé par un tiers si ce n'est pas le
cas).
