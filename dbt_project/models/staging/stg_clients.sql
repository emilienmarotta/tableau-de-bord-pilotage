select
    client_id,
    nom,
    region,
    segment,
    date_creation
from {{ source('raw', 'clients') }}
