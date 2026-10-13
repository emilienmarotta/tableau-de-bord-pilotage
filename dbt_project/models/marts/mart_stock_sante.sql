with stocks as (
    select * from {{ ref('stg_stocks') }}
),

produits as (
    select produit_id, libelle, categorie from {{ ref('stg_produits') }}
),

reference_date as (
    -- Dernier jour de mouvement disponible : le dataset couvre une fenêtre
    -- historique figée, pas la date du jour, donc "30 derniers jours" se
    -- calcule par rapport au dernier mouvement connu.
    select max(date_mouvement) as date_ref from {{ ref('stg_mouvements_stock') }}
),

sorties_30j as (
    select
        mouvements.produit_id,
        -- quantite est négative pour une sortie (convention staging) : on
        -- inverse le signe pour obtenir une quantité sortie positive.
        sum(-mouvements.quantite) as quantite_sortie_30j
    from {{ ref('stg_mouvements_stock') }} as mouvements
    cross join reference_date
    where mouvements.type_mouvement = 'sortie'
        and mouvements.date_mouvement > reference_date.date_ref - interval '30 days'
    group by 1
),

base as (
    select
        stocks.produit_id,
        produits.libelle,
        produits.categorie,
        stocks.quantite_stock,
        stocks.seuil_reappro,
        coalesce(sorties_30j.quantite_sortie_30j, 0) / 30.0 as vente_moy_jour_30j
    from stocks
    left join produits on stocks.produit_id = produits.produit_id
    left join sorties_30j on stocks.produit_id = sorties_30j.produit_id
)

select
    produit_id,
    libelle,
    categorie,
    quantite_stock,
    seuil_reappro,
    vente_moy_jour_30j,
    case
        when vente_moy_jour_30j = 0 then null
        else quantite_stock / vente_moy_jour_30j
    end as couverture_jours,
    case
        when quantite_stock = 0 then 'rupture'
        when quantite_stock <= seuil_reappro then 'a_reapprovisionner'
        when vente_moy_jour_30j = 0 then 'surstock'
        when quantite_stock / vente_moy_jour_30j < {{ var('stock_couverture_reappro_jours') }} then 'a_reapprovisionner'
        when quantite_stock / vente_moy_jour_30j > {{ var('stock_couverture_surstock_jours') }} then 'surstock'
        else 'ok'
    end as statut_stock
from base
