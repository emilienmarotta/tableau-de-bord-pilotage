select
    produit_id,
    libelle,
    categorie,
    prix_achat,
    prix_vente_catalogue
from {{ source('raw', 'produits') }}
