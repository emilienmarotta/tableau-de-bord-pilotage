"""Construit le dashboard Metabase (connexion DB + cartes + filtres) via
l'API REST de Metabase, à partir des marts dbt déjà calculés. Aucune carte
ne recalcule un KPI : chaque carte est une lecture directe d'un mart, ou un
GROUP BY/filtre simple dessus (cf. specs/06-metabase-dashboard.md).

Idempotent : relançable sans dupliquer le dashboard/les cartes (ceux créés
par un run précédent, identifiés par nom, sont supprimés puis recréés).

Usage :
    docker compose up -d
    python3 generator/generate.py --reset
    cd dbt_project && dbt build --profiles-dir . && cd ..
    pip install requests
    python3 metabase/setup_metabase.py
"""

import os
import time
import uuid

import requests

BASE = f"http://localhost:{os.environ.get('METABASE_PORT', '3000')}"
ADMIN_EMAIL = os.environ["METABASE_ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["METABASE_ADMIN_PASSWORD"]
# Vu depuis le conteneur Metabase (réseau docker compose), pas depuis l'hôte.
PG_HOST = "postgres"
PG_PORT = 5432
PG_DB = os.environ["POSTGRES_DB"]
PG_USER = os.environ["POSTGRES_USER"]
PG_PASSWORD = os.environ["POSTGRES_PASSWORD"]

DB_NAME = "tableau_de_bord_pilotage"
DASHBOARD_NAME = "Pilotage commercial"

session = requests.Session()


def wait_healthy(timeout=90):
    for _ in range(timeout):
        try:
            if session.get(f"{BASE}/api/health", timeout=3).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise SystemExit("Metabase ne répond pas (healthcheck timeout).")


def setup_or_login():
    props = session.get(f"{BASE}/api/session/properties").json()
    token = props.get("setup-token")
    if token:
        print("Premier démarrage : création de l'admin...")
        resp = session.post(
            f"{BASE}/api/setup",
            json={
                "token": token,
                "user": {
                    "first_name": "Admin",
                    "last_name": "Demo",
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                },
                "prefs": {
                    "site_name": "Tableau de bord de pilotage",
                    "site_locale": "fr",
                    "allow_tracking": False,
                },
            },
        )
    else:
        print("Admin déjà créé, connexion...")
        resp = session.post(
            f"{BASE}/api/session",
            json={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        )
    resp.raise_for_status()
    session.headers["X-Metabase-Session"] = resp.json()["id"]


def get_or_create_database():
    for db in session.get(f"{BASE}/api/database").json()["data"]:
        if db["name"] == DB_NAME:
            print(f"Connexion DB déjà existante (id={db['id']})")
            return db["id"]
    print("Création de la connexion Postgres (schéma marts uniquement)...")
    resp = session.post(
        f"{BASE}/api/database",
        json={
            "engine": "postgres",
            "name": DB_NAME,
            "details": {
                "host": PG_HOST,
                "port": PG_PORT,
                "dbname": PG_DB,
                "user": PG_USER,
                "password": PG_PASSWORD,
                "schema-filters-type": "inclusion",
                "schema-filters-patterns": "marts",
                "ssl": False,
            },
            "is_full_sync": True,
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def wait_tables(db_id, expected_tables, timeout=60):
    names = set()
    for _ in range(timeout):
        tables = session.get(f"{BASE}/api/table").json()
        names = {t["name"] for t in tables if t["db_id"] == db_id}
        if expected_tables <= names:
            return {t["name"]: t["id"] for t in tables if t["db_id"] == db_id}
        session.post(f"{BASE}/api/database/{db_id}/sync_schema")
        time.sleep(2)
    raise SystemExit(f"Tables marts non synchronisées à temps (trouvé : {names}).")


def fields_by_table(table_ids):
    out = {}
    for name, tid in table_ids.items():
        meta = session.get(f"{BASE}/api/table/{tid}/query_metadata").json()
        out[name] = {f["name"]: f["id"] for f in meta["fields"]}
    return out


def delete_existing(name_prefix):
    for c in session.get(f"{BASE}/api/card").json():
        if c["name"].startswith(name_prefix):
            session.delete(f"{BASE}/api/card/{c['id']}")
    for d in session.get(f"{BASE}/api/dashboard").json():
        if d["name"] == DASHBOARD_NAME:
            session.delete(f"{BASE}/api/dashboard/{d['id']}")


def create_card(database_id, name, query, display, viz_settings=None):
    resp = session.post(
        f"{BASE}/api/card",
        json={
            "name": name,
            "dataset_query": {"type": "query", "database": database_id, "query": query},
            "display": display,
            "visualization_settings": viz_settings or {},
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


def f(field_id):
    return ["field", field_id, None]


def main():
    wait_healthy()
    setup_or_login()
    db_id = get_or_create_database()

    expected = {
        "fct_ventes",
        "mart_ventes_mensuelles",
        "mart_performance_produits",
        "mart_stock_sante",
        "mart_ventes_par_region_client",
    }
    table_ids = wait_tables(db_id, expected)
    flds = fields_by_table(table_ids)

    ventes = flds["mart_ventes_mensuelles"]
    fct = flds["fct_ventes"]
    perf = flds["mart_performance_produits"]
    stock = flds["mart_stock_sante"]
    region = flds["mart_ventes_par_region_client"]

    delete_existing("Pilotage —")

    cards = {}

    # --- Bandeau 4 chiffres clés (vs mois précédent) -----------------------
    cards["ca_mois"] = create_card(
        db_id,
        "Pilotage — CA du mois",
        {
            "source-table": table_ids["mart_ventes_mensuelles"],
            "fields": [f(ventes["mois"]), f(ventes["ca_net"])],
            "order-by": [["asc", f(ventes["mois"])]],
        },
        "smartscalar",
    )
    cards["marge_mois"] = create_card(
        db_id,
        "Pilotage — Marge brute du mois (€)",
        {
            "source-table": table_ids["mart_ventes_mensuelles"],
            "fields": [f(ventes["mois"]), f(ventes["marge_brute"])],
            "order-by": [["asc", f(ventes["mois"])]],
        },
        "smartscalar",
    )
    cards["taux_marge_mois"] = create_card(
        db_id,
        "Pilotage — Taux de marge du mois (%)",
        {
            "source-table": table_ids["mart_ventes_mensuelles"],
            "fields": [f(ventes["mois"]), f(ventes["taux_marge"])],
            "order-by": [["asc", f(ventes["mois"])]],
        },
        "smartscalar",
        {"column_settings": {f'["name","taux_marge"]': {"number_style": "percent"}}},
    )
    cards["panier_moyen_mois"] = create_card(
        db_id,
        "Pilotage — Panier moyen du mois",
        {
            "source-table": table_ids["mart_ventes_mensuelles"],
            "fields": [f(ventes["mois"]), f(ventes["panier_moyen"])],
            "order-by": [["asc", f(ventes["mois"])]],
        },
        "smartscalar",
    )
    cards["produits_alerte"] = create_card(
        db_id,
        "Pilotage — Produits en alerte stock",
        {
            "source-table": table_ids["mart_stock_sante"],
            "aggregation": [["count"]],
            "filter": ["=", f(stock["statut_stock"]), "rupture", "a_reapprovisionner"],
        },
        "scalar",
    )

    # --- Évolution CA & marge (12 mois) ------------------------------------
    cards["evolution"] = create_card(
        db_id,
        "Pilotage — Évolution CA & marge (12 mois)",
        {
            "source-table": table_ids["mart_ventes_mensuelles"],
            "fields": [f(ventes["mois"]), f(ventes["ca_net"]), f(ventes["marge_brute"])],
            "order-by": [["asc", f(ventes["mois"])]],
        },
        "line",
        {"graph.dimensions": ["mois"], "graph.metrics": ["ca_net", "marge_brute"]},
    )

    # --- Marge par catégorie (GROUP BY simple sur fct_ventes) --------------
    cards["marge_categorie"] = create_card(
        db_id,
        "Pilotage — Marge brute par catégorie",
        {
            "source-table": table_ids["fct_ventes"],
            "aggregation": [["sum", f(fct["marge_brute"])]],
            "breakout": [f(fct["categorie"])],
            "order-by": [["desc", ["aggregation", 0]]],
        },
        "bar",
        {"graph.dimensions": ["categorie"], "graph.metrics": ["sum"]},
    )

    # --- Top 10 produits -----------------------------------------------------
    cards["top10"] = create_card(
        db_id,
        "Pilotage — Top 10 produits (CA + taux de marge)",
        {
            "source-table": table_ids["mart_performance_produits"],
            "fields": [
                f(perf["libelle"]),
                f(perf["categorie"]),
                f(perf["ca_net"]),
                f(perf["taux_marge"]),
                f(perf["quantite_vendue"]),
            ],
            "order-by": [["desc", f(perf["ca_net"])]],
            "limit": 10,
        },
        "table",
    )

    # --- Santé des stocks : répartition + liste critique --------------------
    cards["stock_donut"] = create_card(
        db_id,
        "Pilotage — Répartition des statuts de stock",
        {
            "source-table": table_ids["mart_stock_sante"],
            "aggregation": [["count"]],
            "breakout": [f(stock["statut_stock"])],
        },
        "pie",
    )
    cards["stock_critique"] = create_card(
        db_id,
        "Pilotage — Produits critiques (rupture / à réapprovisionner)",
        {
            "source-table": table_ids["mart_stock_sante"],
            "filter": ["=", f(stock["statut_stock"]), "rupture", "a_reapprovisionner"],
            "order-by": [["asc", f(stock["couverture_jours"])]],
        },
        "table",
    )

    # --- CA par région ---------------------------------------------------
    cards["ca_region"] = create_card(
        db_id,
        "Pilotage — CA par région",
        {
            "source-table": table_ids["mart_ventes_par_region_client"],
            "aggregation": [["sum", f(region["ca_net"])]],
            "breakout": [f(region["region"])],
            "order-by": [["desc", ["aggregation", 0]]],
        },
        "bar",
        {"graph.dimensions": ["region"], "graph.metrics": ["sum"]},
    )

    # --- Dashboard + layout --------------------------------------------------
    dash = session.post(f"{BASE}/api/dashboard", json={"name": DASHBOARD_NAME}).json()
    dash_id = dash["id"]

    param_periode = {"id": uuid.uuid4().hex[:8], "name": "Période", "slug": "periode", "type": "date/all-options", "sectionId": "date"}
    param_categorie = {"id": uuid.uuid4().hex[:8], "name": "Catégorie", "slug": "categorie", "type": "string/=", "sectionId": "string"}
    param_region = {"id": uuid.uuid4().hex[:8], "name": "Région", "slug": "region", "type": "string/=", "sectionId": "string"}

    def mapping(param, card_key, field_id):
        return {"parameter_id": param["id"], "card_id": cards[card_key], "target": ["dimension", f(field_id)]}

    dashcards = [
        # Bandeau (row 0, hauteur 3)
        {"id": -1, "card_id": cards["ca_mois"], "row": 0, "col": 0, "size_x": 5, "size_y": 3,
         "parameter_mappings": [mapping(param_periode, "ca_mois", ventes["mois"])]},
        {"id": -2, "card_id": cards["marge_mois"], "row": 0, "col": 5, "size_x": 5, "size_y": 3,
         "parameter_mappings": [mapping(param_periode, "marge_mois", ventes["mois"])]},
        {"id": -3, "card_id": cards["taux_marge_mois"], "row": 0, "col": 10, "size_x": 4, "size_y": 3,
         "parameter_mappings": [mapping(param_periode, "taux_marge_mois", ventes["mois"])]},
        {"id": -4, "card_id": cards["panier_moyen_mois"], "row": 0, "col": 14, "size_x": 5, "size_y": 3,
         "parameter_mappings": [mapping(param_periode, "panier_moyen_mois", ventes["mois"])]},
        {"id": -5, "card_id": cards["produits_alerte"], "row": 0, "col": 19, "size_x": 5, "size_y": 3,
         "parameter_mappings": []},
        # Évolution + marge par catégorie (row 3, hauteur 8)
        {"id": -6, "card_id": cards["evolution"], "row": 3, "col": 0, "size_x": 12, "size_y": 8,
         "parameter_mappings": [mapping(param_periode, "evolution", ventes["mois"])]},
        {"id": -7, "card_id": cards["marge_categorie"], "row": 3, "col": 12, "size_x": 12, "size_y": 8,
         "parameter_mappings": [
             mapping(param_periode, "marge_categorie", fct["date_commande"]),
             mapping(param_categorie, "marge_categorie", fct["categorie"]),
             mapping(param_region, "marge_categorie", fct["region"]),
         ]},
        # Top 10 + santé des stocks (row 11, hauteur 8 puis 4+4)
        {"id": -8, "card_id": cards["top10"], "row": 11, "col": 0, "size_x": 12, "size_y": 8,
         "parameter_mappings": [mapping(param_categorie, "top10", perf["categorie"])]},
        {"id": -9, "card_id": cards["stock_donut"], "row": 11, "col": 12, "size_x": 12, "size_y": 4,
         "parameter_mappings": [mapping(param_categorie, "stock_donut", stock["categorie"])]},
        {"id": -10, "card_id": cards["stock_critique"], "row": 15, "col": 12, "size_x": 12, "size_y": 4,
         "parameter_mappings": [mapping(param_categorie, "stock_critique", stock["categorie"])]},
        # CA par région (row 19, pleine largeur)
        {"id": -11, "card_id": cards["ca_region"], "row": 19, "col": 0, "size_x": 24, "size_y": 6,
         "parameter_mappings": [mapping(param_region, "ca_region", region["region"])]},
    ]

    resp = session.put(
        f"{BASE}/api/dashboard/{dash_id}",
        json={
            "dashcards": dashcards,
            "parameters": [param_periode, param_categorie, param_region],
        },
    )
    resp.raise_for_status()
    print(f"Dashboard '{DASHBOARD_NAME}' créé (id={dash_id}) avec {len(dashcards)} cartes.")
    print(f"-> {BASE}/dashboard/{dash_id}")


if __name__ == "__main__":
    main()
