"""Génère un jeu de données fictif de PME de commerce de gros et le charge
directement dans le schéma `raw` de Postgres (voir specs/02-data-generator.md).
"""

import argparse
import calendar
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras
from faker import Faker

SEED = 42

N_CLIENTS = 150
N_PRODUITS = 200
N_STARS = 10
N_MARGE_FAIBLE = 10
N_RUPTURE = 5
N_REAPPRO = 15
N_SURSTOCK = 15

START_DATE = date(2025, 10, 1)
END_DATE = date(2026, 9, 30)

REGIONS = [
    "Île-de-France",
    "Auvergne-Rhône-Alpes",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Hauts-de-France",
    "Grand Est",
]

SEGMENTS = ["grand_compte", "pme", "detaillant"]
SEGMENT_WEIGHTS = [15, 55, 30]

CATEGORIES = [
    "emballage",
    "hygiene",
    "boissons",
    "alimentaire",
    "papier",
    "protection",
    "entretien",
    "textile",
]

# Facteur saisonnier par mois (1 = normal) : creux en été, pic fin d'année.
SEASONAL_FACTOR = {
    1: 0.90, 2: 0.85, 3: 0.95, 4: 1.00, 5: 1.00, 6: 0.90,
    7: 0.60, 8: 0.55, 9: 0.95, 10: 1.05, 11: 1.30, 12: 1.50,
}

BASE_ORDERS_PER_MONTH = 170

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.clients (
    client_id integer PRIMARY KEY,
    nom text NOT NULL,
    region text NOT NULL,
    segment text NOT NULL,
    date_creation date NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.produits (
    produit_id integer PRIMARY KEY,
    libelle text NOT NULL,
    categorie text NOT NULL,
    prix_achat numeric(10, 2) NOT NULL,
    prix_vente_catalogue numeric(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.commandes (
    commande_id integer PRIMARY KEY,
    client_id integer NOT NULL REFERENCES raw.clients (client_id),
    date_commande date NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.lignes_commande (
    ligne_id integer PRIMARY KEY,
    commande_id integer NOT NULL REFERENCES raw.commandes (commande_id),
    produit_id integer NOT NULL REFERENCES raw.produits (produit_id),
    quantite integer NOT NULL,
    prix_unitaire_facture numeric(10, 2) NOT NULL,
    remise numeric(5, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.stocks (
    produit_id integer PRIMARY KEY REFERENCES raw.produits (produit_id),
    quantite_stock integer NOT NULL,
    seuil_reappro integer NOT NULL,
    date_releve date NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.mouvements_stock (
    mouvement_id integer PRIMARY KEY,
    produit_id integer NOT NULL REFERENCES raw.produits (produit_id),
    date_mouvement date NOT NULL,
    quantite integer NOT NULL,
    type_mouvement text NOT NULL
);
"""

TRUNCATE = """
TRUNCATE TABLE
    raw.lignes_commande, raw.mouvements_stock, raw.stocks,
    raw.commandes, raw.produits, raw.clients
    RESTART IDENTITY CASCADE;
"""


def load_dotenv(path: Path) -> None:
    """Charge un .env minimal (KEY=VALUE) sans dépendance externe."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5433"),
        dbname=os.environ.get("POSTGRES_DB", "tableau_de_bord"),
        user=os.environ.get("POSTGRES_USER", "dashboard_user"),
        password=os.environ.get("POSTGRES_PASSWORD", "change_me"),
    )


def months_in_range(start: date, end: date) -> list[tuple[int, int]]:
    months = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        months.append((year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def random_day_in_month(rng: random.Random, year: int, month: int, start: date, end: date) -> date:
    last_day = calendar.monthrange(year, month)[1]
    day = rng.randint(1, last_day)
    d = date(year, month, day)
    if d < start:
        d = start
    if d > end:
        d = end
    return d


def build_clients(rng: random.Random, fake: Faker) -> list[dict]:
    clients = []
    for client_id in range(1, N_CLIENTS + 1):
        creation_offset_days = rng.randint(30, 5 * 365)
        clients.append({
            "client_id": client_id,
            "nom": fake.company(),
            "region": rng.choice(REGIONS),
            "segment": rng.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0],
            "date_creation": START_DATE - timedelta(days=creation_offset_days),
        })
    return clients


def build_produits(rng: random.Random, fake: Faker) -> tuple[list[dict], set[int], set[int]]:
    produits = []
    ids = list(range(1, N_PRODUITS + 1))
    stars = set(rng.sample(ids, N_STARS))
    remaining = [i for i in ids if i not in stars]
    marge_faible = set(rng.sample(remaining, N_MARGE_FAIBLE))

    for produit_id in ids:
        prix_achat = round(rng.uniform(2, 80), 2)
        if produit_id in marge_faible:
            prix_vente = round(prix_achat * rng.uniform(0.85, 1.03), 2)
        else:
            prix_vente = round(prix_achat * rng.uniform(1.3, 1.9), 2)
        produits.append({
            "produit_id": produit_id,
            "libelle": f"{fake.word().capitalize()} {rng.choice(CATEGORIES)} réf. {produit_id:04d}",
            "categorie": rng.choice(CATEGORIES),
            "prix_achat": prix_achat,
            "prix_vente_catalogue": prix_vente,
        })
    return produits, stars, marge_faible


def build_commandes_et_lignes(
    rng: random.Random, clients: list[dict], produits: list[dict], stars: set[int],
) -> tuple[list[dict], list[dict]]:
    client_ids = [c["client_id"] for c in clients]
    produit_ids = [p["produit_id"] for p in produits]
    produits_by_id = {p["produit_id"]: p for p in produits}
    weights = [5 if pid in stars else 1 for pid in produit_ids]

    commandes: list[dict] = []
    lignes: list[dict] = []
    commande_id = 1
    ligne_id = 1

    for year, month in months_in_range(START_DATE, END_DATE):
        factor = SEASONAL_FACTOR[month]
        n_orders = max(1, round(BASE_ORDERS_PER_MONTH * factor * rng.uniform(0.9, 1.1)))
        for _ in range(n_orders):
            client_id = rng.choice(client_ids)
            date_commande = random_day_in_month(rng, year, month, START_DATE, END_DATE)
            commandes.append({
                "commande_id": commande_id,
                "client_id": client_id,
                "date_commande": date_commande,
            })

            n_lignes = rng.randint(1, 5)
            chosen_produits = rng.choices(produit_ids, weights=weights, k=n_lignes)
            for produit_id in chosen_produits:
                produit = produits_by_id[produit_id]
                is_star = produit_id in stars
                quantite = rng.randint(5, 60) if is_star else rng.randint(1, 20)
                negociation = rng.uniform(0.95, 1.05)
                prix_unitaire = round(float(produit["prix_vente_catalogue"]) * negociation, 2)
                remise = rng.choices([0.0, 0.05, 0.1, 0.15], weights=[55, 20, 15, 10])[0]
                lignes.append({
                    "ligne_id": ligne_id,
                    "commande_id": commande_id,
                    "produit_id": produit_id,
                    "quantite": quantite,
                    "prix_unitaire_facture": prix_unitaire,
                    "remise": remise,
                })
                ligne_id += 1
            commande_id += 1

    return commandes, lignes


def build_stocks_et_mouvements(
    rng: random.Random, produits: list[dict], commandes: list[dict], lignes: list[dict],
) -> tuple[list[dict], list[dict]]:
    commandes_by_id = {c["commande_id"]: c for c in commandes}

    ventes_30j: dict[int, int] = {p["produit_id"]: 0 for p in produits}
    seuil_30j = END_DATE - timedelta(days=30)

    mouvements: list[dict] = []
    mouvement_id = 1

    for ligne in lignes:
        date_commande = commandes_by_id[ligne["commande_id"]]["date_commande"]
        mouvements.append({
            "mouvement_id": mouvement_id,
            "produit_id": ligne["produit_id"],
            "date_mouvement": date_commande,
            "quantite": -ligne["quantite"],
            "type_mouvement": "sortie",
        })
        mouvement_id += 1
        if date_commande > seuil_30j:
            ventes_30j[ligne["produit_id"]] += ligne["quantite"]

    # Réapprovisionnements périodiques (entrées), indépendants des ventes.
    for produit in produits:
        for year, month in months_in_range(START_DATE, END_DATE):
            if rng.random() < 0.7:
                date_mouvement = random_day_in_month(rng, year, month, START_DATE, END_DATE)
                mouvements.append({
                    "mouvement_id": mouvement_id,
                    "produit_id": produit["produit_id"],
                    "date_mouvement": date_mouvement,
                    "quantite": rng.randint(50, 300),
                    "type_mouvement": "entree",
                })
                mouvement_id += 1

    # Statuts de stock volontairement variés (cf. specs/02-data-generator.md).
    produit_ids = [p["produit_id"] for p in produits]
    rupture_ids = set(rng.sample(produit_ids, N_RUPTURE))
    reste = [pid for pid in produit_ids if pid not in rupture_ids]
    reappro_ids = set(rng.sample(reste, N_REAPPRO))
    reste = [pid for pid in reste if pid not in reappro_ids]
    surstock_ids = set(rng.sample(reste, N_SURSTOCK))

    stocks: list[dict] = []
    for produit in produits:
        produit_id = produit["produit_id"]
        vente_moy_jour = ventes_30j[produit_id] / 30

        if produit_id in rupture_ids:
            quantite_stock = 0
        elif produit_id in reappro_ids:
            if vente_moy_jour > 0:
                quantite_stock = max(1, round(vente_moy_jour * rng.uniform(1, 6)))
            else:
                quantite_stock = rng.randint(1, 5)
        elif produit_id in surstock_ids:
            if vente_moy_jour > 0:
                quantite_stock = round(vente_moy_jour * rng.uniform(100, 200))
            else:
                quantite_stock = rng.randint(500, 1000)
        elif vente_moy_jour > 0:
            coverage_target = rng.uniform(15, 60)
            quantite_stock = round(vente_moy_jour * coverage_target)
        else:
            quantite_stock = rng.randint(20, 80)

        seuil_reappro = round(vente_moy_jour * 10) if vente_moy_jour > 0 else rng.randint(5, 20)
        seuil_reappro = max(seuil_reappro, 5)

        stocks.append({
            "produit_id": produit_id,
            "quantite_stock": quantite_stock,
            "seuil_reappro": seuil_reappro,
            "date_releve": END_DATE,
        })

    return stocks, mouvements


def insert(conn, table: str, columns: list[str], rows: list[dict]) -> None:
    if not rows:
        return
    values = [[row[col] for col in columns] for row in rows]
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, query, values, page_size=1000)


def load_to_postgres(
    clients: list[dict], produits: list[dict], commandes: list[dict],
    lignes: list[dict], stocks: list[dict], mouvements: list[dict],
) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute(TRUNCATE)
        insert(conn, "raw.clients", ["client_id", "nom", "region", "segment", "date_creation"], clients)
        insert(conn, "raw.produits", ["produit_id", "libelle", "categorie", "prix_achat", "prix_vente_catalogue"], produits)
        insert(conn, "raw.commandes", ["commande_id", "client_id", "date_commande"], commandes)
        insert(conn, "raw.lignes_commande", ["ligne_id", "commande_id", "produit_id", "quantite", "prix_unitaire_facture", "remise"], lignes)
        insert(conn, "raw.stocks", ["produit_id", "quantite_stock", "seuil_reappro", "date_releve"], stocks)
        insert(conn, "raw.mouvements_stock", ["mouvement_id", "produit_id", "date_mouvement", "quantite", "type_mouvement"], mouvements)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Recrée le schéma raw et recharge toutes les données")
    args = parser.parse_args()

    if not args.reset:
        print("Spécifier --reset (voir --help)", file=sys.stderr)
        sys.exit(1)

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    rng = random.Random(SEED)
    fake = Faker("fr_FR")
    fake.seed_instance(SEED)

    clients = build_clients(rng, fake)
    produits, stars, marge_faible = build_produits(rng, fake)
    commandes, lignes = build_commandes_et_lignes(rng, clients, produits, stars)
    stocks, mouvements = build_stocks_et_mouvements(rng, produits, commandes, lignes)

    load_to_postgres(clients, produits, commandes, lignes, stocks, mouvements)

    print(
        f"Chargé : {len(clients)} clients, {len(produits)} produits "
        f"({len(stars)} stars, {len(marge_faible)} à marge faible), "
        f"{len(commandes)} commandes, {len(lignes)} lignes de commande, "
        f"{len(stocks)} relevés de stock, {len(mouvements)} mouvements de stock."
    )


if __name__ == "__main__":
    main()
