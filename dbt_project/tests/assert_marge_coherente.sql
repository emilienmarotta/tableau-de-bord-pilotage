-- Échoue si marge_brute != ca_net - cout_total à 0.01 près, pour détecter
-- une régression si le calcul est modifié dans fct_ventes sans mettre à
-- jour la formule partout.
select *
from {{ ref('fct_ventes') }}
where abs(marge_brute - (ca_net - cout_total)) > 0.01
