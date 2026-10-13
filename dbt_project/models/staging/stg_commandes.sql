select
    commande_id,
    client_id,
    date_commande
from {{ source('raw', 'commandes') }}
