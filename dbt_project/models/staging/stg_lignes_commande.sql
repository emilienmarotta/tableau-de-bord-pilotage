select
    ligne_id,
    commande_id,
    produit_id,
    quantite,
    prix_unitaire_facture,
    remise
from {{ source('raw', 'lignes_commande') }}
