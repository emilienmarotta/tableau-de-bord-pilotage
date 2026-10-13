"""Régénère docs/dbt-lineage.png à partir de dbt_project/target/manifest.json.

Usage (après un `dbt build`/`dbt compile` pour avoir un manifest.json à jour) :
    pip install matplotlib
    python3 docs/render_lineage.py

Outil de documentation ponctuel, indépendant du pipeline generator/dbt/Metabase.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT / "dbt_project/target/manifest.json").read_text())
nodes = {
    v["name"]: v
    for v in manifest["nodes"].values()
    if v["resource_type"] == "model"
}

# "facts" est une colonne de mise en page uniquement (fct_ventes reste bien
# dans le schéma marts côté dbt) : l'isoler dans sa propre colonne évite que
# les flèches vers les 3 marts qui en dépendent traversent d'autres boîtes
# de la même colonne.
LAYER_ORDER = ["staging", "intermediate", "facts", "marts"]
LAYER_COLOR = {
    "staging": "#cfe8ff",
    "intermediate": "#ffe6b3",
    "facts": "#c8f0c8",
    "marts": "#c8f0c8",
}

by_layer = {layer: [] for layer in LAYER_ORDER}
for name, node in nodes.items():
    schema = node["config"]["schema"]
    layer = "facts" if name == "fct_ventes" else schema
    by_layer[layer].append(name)

for layer in LAYER_ORDER:
    by_layer[layer].sort()

by_layer["marts"] = [
    "mart_ventes_mensuelles",
    "mart_performance_produits",
    "mart_ventes_par_region_client",
    "mart_stock_sante",
]

positions = {}
x_gap = 4.2
y_gap = 1.1
for col, layer in enumerate(LAYER_ORDER):
    names = by_layer[layer]
    n = len(names)
    total_height = (n - 1) * y_gap
    for row, name in enumerate(names):
        y = total_height / 2 - row * y_gap
        positions[name] = (col * x_gap, y)

fig, ax = plt.subplots(figsize=(15, 9))
box_w, box_h = 3.4, 0.6

for name, (x, y) in positions.items():
    layer = nodes[name]["config"]["schema"]
    box = FancyBboxPatch(
        (x - box_w / 2, y - box_h / 2),
        box_w,
        box_h,
        boxstyle="round,pad=0.06,rounding_size=0.08",
        linewidth=1.4,
        edgecolor="#333333",
        facecolor=LAYER_COLOR[layer],
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(
        x,
        y,
        name,
        ha="center",
        va="center",
        fontsize=10.5,
        fontweight="bold" if layer == "marts" else "normal",
        zorder=4,
    )

for name, node in nodes.items():
    x2, y2 = positions[name]
    for dep in node["depends_on"]["nodes"]:
        dep_name = dep.split(".")[-1]
        if dep_name in positions:
            x1, y1 = positions[dep_name]
            arrow = FancyArrowPatch(
                (x1 + box_w / 2, y1),
                (x2 - box_w / 2, y2),
                arrowstyle="-|>",
                mutation_scale=14,
                linewidth=1.1,
                color="#555555",
                zorder=2,
                connectionstyle="arc3,rad=0.08",
            )
            ax.add_patch(arrow)

HEADER_LABEL = {"staging": "staging", "intermediate": "intermediate", "marts": "marts"}
HEADER_X = {"staging": 0, "intermediate": x_gap, "marts": 2.5 * x_gap}
for layer, label in HEADER_LABEL.items():
    ax.text(
        HEADER_X[layer],
        4.6,
        label,
        ha="center",
        va="bottom",
        fontsize=14,
        fontweight="bold",
        color="#444444",
    )

ax.set_xlim(-x_gap, (len(LAYER_ORDER) - 1) * x_gap + x_gap)
ax.set_ylim(-4, 5.2)
ax.axis("off")
ax.set_title(
    "Lignage dbt — tableau-de-bord-pilotage (staging -> intermediate -> marts)",
    fontsize=13,
    pad=14,
)
fig.tight_layout()
fig.savefig(ROOT / "docs/dbt-lineage.png", dpi=170)
print("saved docs/dbt-lineage.png")
