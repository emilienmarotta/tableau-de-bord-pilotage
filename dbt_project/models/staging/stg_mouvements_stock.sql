select
    mouvement_id,
    produit_id,
    date_mouvement,
    quantite,
    type_mouvement
from {{ source('raw', 'mouvements_stock') }}
