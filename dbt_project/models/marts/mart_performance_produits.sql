with ventes as (
    select * from {{ ref('fct_ventes') }}
),

produits as (
    select produit_id, libelle from {{ ref('stg_produits') }}
),

agrege as (
    select
        ventes.produit_id,
        ventes.categorie,
        produits.libelle,
        sum(ventes.ca_net) as ca_net,
        sum(ventes.marge_brute) as marge_brute,
        sum(ventes.marge_brute) / sum(ventes.ca_net) as taux_marge,
        sum(ventes.quantite) as quantite_vendue
    from ventes
    inner join produits on ventes.produit_id = produits.produit_id
    group by 1, 2, 3
)

select
    produit_id,
    categorie,
    libelle,
    ca_net,
    marge_brute,
    taux_marge,
    quantite_vendue,
    dense_rank() over (order by ca_net desc) as rang_ca_global,
    dense_rank() over (partition by categorie order by ca_net desc) as rang_ca_categorie
from agrege
