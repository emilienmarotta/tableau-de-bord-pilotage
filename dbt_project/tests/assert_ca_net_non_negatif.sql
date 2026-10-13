-- Échoue si une ligne de fct_ventes a un CA net négatif (une remise mal
-- appliquée ne doit jamais rendre le CA négatif).
select *
from {{ ref('fct_ventes') }}
where ca_net < 0
