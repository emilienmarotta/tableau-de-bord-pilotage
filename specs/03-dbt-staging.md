# 03 — dbt : staging

**Statut :** Implemented

## Objectif

Une couche `staging` qui renomme/type/nettoie légèrement les tables `raw.*`,
sans aucune logique métier (pas de jointure, pas de calcul de KPI). Une
source dbt par table physique, un modèle `stg_*` par source.

## Sources (`models/staging/_raw__sources.yml`)

Schéma source : `raw`. Tables déclarées : `clients`, `produits`, `commandes`,
`lignes_commande`, `stocks`, `mouvements_stock`. Test de fraîcheur
(`loaded_at`/`date_releve`) sur `stocks` uniquement (c'est la seule table où
la "fraîcheur du relevé" a un sens métier) ; pas pertinent sur les autres
tables qui sont un historique figé rechargé en bloc.

## Modèles

- `stg_clients` : `client_id`, `nom`, `region`, `segment`, `date_creation`.
- `stg_produits` : `produit_id`, `libelle`, `categorie`, `prix_achat`,
  `prix_vente_catalogue`.
- `stg_commandes` : `commande_id`, `client_id`, `date_commande`.
- `stg_lignes_commande` : `ligne_id`, `commande_id`, `produit_id`,
  `quantite`, `prix_unitaire_facture`, `remise`.
- `stg_stocks` : `produit_id`, `quantite_stock`, `seuil_reappro`,
  `date_releve`.
- `stg_mouvements_stock` : `mouvement_id`, `produit_id`, `date_mouvement`,
  `quantite`, `type_mouvement`.

## Conventions

- Matérialisation : `view` (configuré au niveau du dossier dans
  `dbt_project.yml`).
- Nommage des colonnes déjà cohérent en base (`raw` généré directement avec
  les bons noms) : le staging sert surtout de point de contrat stable et
  d'endroit où ajouter un cast/nettoyage si besoin, pas à renommer en masse.
- Aucune colonne calculée (ex. pas de `ca_net` ici) : ça commence en
  `intermediate`.

## Tests (génériques, détail complet dans la spec 05)

- `not_null` + `unique` sur chaque clé primaire (`client_id`, `produit_id`,
  `commande_id`, `ligne_id`, `mouvement_id`).
- `accepted_values` sur `segment` (`grand_compte`, `pme`, `detaillant`) et
  `type_mouvement` (`entree`, `sortie`).
- `relationships` : `lignes_commande.commande_id` → `commandes.commande_id`,
  `lignes_commande.produit_id` → `produits.produit_id`,
  `commandes.client_id` → `clients.client_id`, `stocks.produit_id` →
  `produits.produit_id`, `mouvements_stock.produit_id` →
  `produits.produit_id`.

## Critères d'acceptation

- [ ] `dbt run --select staging` passe sans erreur sur une base chargée par
  le générateur (spec 02).
- [ ] `dbt test --select staging` passe (tests de la section ci-dessus).
- [ ] Chaque modèle et chaque colonne clé est documenté dans un fichier YAML
  (`description:`), même brièvement.
