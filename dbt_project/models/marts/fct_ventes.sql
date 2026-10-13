select
    ligne_id,
    commande_id,
    date_commande,
    client_id,
    region,
    segment,
    produit_id,
    categorie,
    quantite,
    ca_net,
    cout_total,
    marge_brute
from {{ ref('int_lignes_vente_enrichies') }}
