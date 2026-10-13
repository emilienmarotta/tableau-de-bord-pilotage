-- Échoue si mart_stock_sante contient une quantité en stock négative.
select *
from {{ ref('mart_stock_sante') }}
where quantite_stock < 0
