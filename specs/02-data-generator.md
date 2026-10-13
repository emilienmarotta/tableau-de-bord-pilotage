# 02 — Générateur de données fictives

**Statut :** Approved

## Objectif

Script Python (Faker), déterministe (graine fixe), qui crée le schéma `raw`
dans Postgres et le remplit avec un jeu de données de PME de commerce de gros
sur 12 mois d'historique, avec des anomalies volontaires pour que le tableau
de bord ait des choses à raconter.

## Décision : chargement direct en base (pas de dbt seed)

Le générateur se connecte à Postgres (`psycopg2`) et charge directement les
tables du schéma `raw` (`TRUNCATE` puis `COPY`/`INSERT`), plutôt que d'écrire
des CSV rechargés ensuite par dbt seed. Raison : le volume (~150 clients,
~200 produits, 12 mois de commandes) dépasse largement ce qui est raisonnable
pour un `dbt seed` (recommandé pour de petits fichiers de référence, pas pour
des faits volumineux). Séquence de reproductibilité visée (cf. critères de
réussite) : `docker compose up` → `python generator/generate.py` →
`dbt build`.

Le script peut aussi écrire un échantillon CSV dans `data/` (ignoré par git,
sauf un petit échantillon versionné pour illustration) à titre de preuve/
debug, mais ce n'est pas le chemin de chargement principal.

## Schéma `raw` (DDL exécuté par le générateur, idempotent : `CREATE TABLE IF NOT EXISTS`)

### `raw.clients`
| Colonne | Type | Notes |
|---|---|---|
| client_id | integer PK | |
| nom | text | raison sociale fictive (Faker) |
| region | text | une des régions FR définies ci-dessous |
| segment | text | `grand_compte` \| `pme` \| `detaillant` |
| date_creation | date | ancienneté du client |

~150 lignes.

### `raw.produits`
| Colonne | Type | Notes |
|---|---|---|
| produit_id | integer PK | |
| libelle | text | |
| categorie | text | 6-8 catégories (ex. emballage, hygiène, boissons, alimentaire, papier, protection) |
| prix_achat | numeric(10,2) | coût unitaire |
| prix_vente_catalogue | numeric(10,2) | prix catalogue, > prix_achat sauf produits volontairement à marge faible/négative |

~200 lignes. Quelques produits (≈5%) ont un `prix_vente_catalogue` proche ou
inférieur au `prix_achat` (marge faible/négative volontaire).

### `raw.commandes`
| Colonne | Type | Notes |
|---|---|---|
| commande_id | integer PK | |
| client_id | integer FK | |
| date_commande | date | répartie sur 12 mois, avec saisonnalité (pics en fin d'année, creux en été) |

### `raw.lignes_commande`
| Colonne | Type | Notes |
|---|---|---|
| ligne_id | integer PK | |
| commande_id | integer FK | |
| produit_id | integer FK | |
| quantite | integer | |
| prix_unitaire_facture | numeric(10,2) | peut différer du prix catalogue (négociation) |
| remise | numeric(5,4) | taux de remise, 0 à ~0.15 |

Quelques produits « stars » (≈10 produits) apparaissent avec une fréquence et
des quantités nettement supérieures à la moyenne.

### `raw.stocks`
| Colonne | Type | Notes |
|---|---|---|
| produit_id | integer FK | une ligne par produit (dernier relevé) |
| quantite_stock | integer | peut être 0 (rupture volontaire sur quelques produits) ou très élevé (surstock volontaire sur quelques produits) |
| seuil_reappro | integer | seuil de réapprovisionnement |
| date_releve | date | date du relevé (la plus récente de l'historique généré) |

### `raw.mouvements_stock`
| Colonne | Type | Notes |
|---|---|---|
| mouvement_id | integer PK | |
| produit_id | integer FK | |
| date_mouvement | date | |
| quantite | integer | positive (entrée) ou négative (sortie) |
| type_mouvement | text | `entree` \| `sortie` |

Utilisé pour calculer la vente moyenne journalière sur 30 jours dans
`mart_stock_sante` (cf. spec 04) — cohérent avec les sorties de
`lignes_commande` pour ne pas raconter deux histoires différentes.

## Règles de réalisme à respecter

- Graine fixe (`SEED = 42`, comme dans le projet 1) : la génération est
  reproductible à l'identique.
- Saisonnalité sur les commandes (volume plus élevé en fin d'année).
- ≈10 produits « stars » (CA et quantités largement au-dessus de la moyenne).
- ≈5% des produits à marge faible ou négative.
- Quelques produits en rupture (stock = 0) et quelques produits en surstock
  (couverture largement > 90 jours), répartis entre plusieurs catégories pour
  que `mart_stock_sante` ait des cas de chaque statut.

## Régions (cohérentes avec le projet 1)

Île-de-France, Auvergne-Rhône-Alpes, Nouvelle-Aquitaine, Occitanie,
Hauts-de-France, Grand Est.

## Interface du script

```bash
python generator/generate.py --reset   # recrée le schéma raw et recharge tout
```

Pas d'autre mode nécessaire (contrairement au projet 1, pas de génération
jour par jour : ce projet travaille sur un historique figé de 12 mois,
rechargé en une fois).

## Critères d'acceptation

- [ ] `python generator/generate.py --reset` s'exécute sans erreur sur une
  base Postgres vide (créée par `docker compose up`).
- [ ] Les 6 tables `raw.*` existent et contiennent un volume cohérent avec le
  tableau ci-dessus.
- [ ] Rejouer le script donne exactement les mêmes données (vérifié par un
  hash ou un comptage de lignes + somme de contrôle sur le CA total).
- [ ] Au moins un produit en rupture, un produit en surstock, un produit à
  marge négative, un produit « star » sont visibles dans les données.
