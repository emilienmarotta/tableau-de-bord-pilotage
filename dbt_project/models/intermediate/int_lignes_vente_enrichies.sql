with lignes as (
    select * from {{ ref('stg_lignes_commande') }}
),

commandes as (
    select * from {{ ref('stg_commandes') }}
),

clients as (
    select * from {{ ref('stg_clients') }}
),

produits as (
    select * from {{ ref('stg_produits') }}
)

select
    lignes.ligne_id,
    lignes.commande_id,
    commandes.date_commande,
    clients.client_id,
    clients.region,
    clients.segment,
    lignes.produit_id,
    produits.categorie,
    lignes.quantite,
    lignes.prix_unitaire_facture,
    lignes.remise,
    produits.prix_achat,
    lignes.quantite * lignes.prix_unitaire_facture * (1 - lignes.remise) as ca_net,
    lignes.quantite * produits.prix_achat as cout_total,
    (lignes.quantite * lignes.prix_unitaire_facture * (1 - lignes.remise))
        - (lignes.quantite * produits.prix_achat) as marge_brute
from lignes
inner join commandes on lignes.commande_id = commandes.commande_id
inner join clients on commandes.client_id = clients.client_id
inner join produits on lignes.produit_id = produits.produit_id
