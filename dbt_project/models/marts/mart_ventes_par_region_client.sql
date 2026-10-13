select
    region,
    segment,
    sum(ca_net) as ca_net,
    sum(marge_brute) as marge_brute,
    count(distinct client_id) as nb_clients_actifs
from {{ ref('fct_ventes') }}
group by 1, 2
order by 1, 2
