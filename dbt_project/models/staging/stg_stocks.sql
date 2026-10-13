select
    produit_id,
    quantite_stock,
    seuil_reappro,
    date_releve
from {{ source('raw', 'stocks') }}
