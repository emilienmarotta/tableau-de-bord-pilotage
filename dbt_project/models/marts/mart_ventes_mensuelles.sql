with ventes as (
    select * from {{ ref('fct_ventes') }}
)

select
    date_trunc('month', date_commande)::date as mois,
    sum(ca_net) as ca_net,
    sum(marge_brute) as marge_brute,
    sum(marge_brute) / sum(ca_net) as taux_marge,
    count(distinct commande_id) as nb_commandes,
    sum(ca_net) / count(distinct commande_id) as panier_moyen
from ventes
group by 1
order by 1
