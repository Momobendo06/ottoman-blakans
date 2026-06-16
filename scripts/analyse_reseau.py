"""
Analyse B — Réseau sultan ↔ guerre
Projet : L'expansion ottomane dans les Balkans (1354–1683)
Auteur  : Muhamed Mehic
Cours   : Data Science – Université de Neuchâtel, 2026

Description :
    Ce script construit un graphe bipartite reliant chaque sultan aux conflits
    (part_ofLabel) dans lesquels il a participé. La taille des nœuds reflète
    le nombre de batailles ; l'épaisseur des arêtes reflète le nombre de
    batailles partagées entre un sultan et une guerre donnée.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

# ─── 0. CONFIGURATION ────────────────────────────────────────────────────────

INPUT_CSV     = "data/ottoman_balkans_battles_clean.csv"
OUTPUT_RESEAU = "outputs/output_reseau_sultan_guerre.png"

COULEURS_SULTANS = {
    "Orhan"        : "#8b3a1a",
    "Murad Iᵉʳ"   : "#a0522d",
    "Bayezid Iᵉʳ" : "#b8860b",
    "Interrègne"   : "#888888",
    "Mehmed Iᵉʳ"  : "#1a5c5c",
    "Murad II"     : "#2e7d7d",
    "Mehmed II"    : "#c0392b",
    "Bayezid II"   : "#d35400",
    "Selim Iᵉʳ"   : "#7f8c8d",
    "Soliman Iᵉʳ" : "#1a3a5c",
    "Selim II"     : "#4a235a",
    "Murad III"    : "#1e8449",
    "Mehmed III"   : "#117a65",
    "Mehmed IV"    : "#6e2f1a",
}

# ─── 1. CHARGEMENT ET PRÉPARATION ────────────────────────────────────────────

df = pd.read_csv(INPUT_CSV)

# Garder uniquement les lignes avec une guerre associée
df = df.dropna(subset=["part_ofLabel"])
df = df[df["part_ofLabel"].str.strip() != ""]
df["sultan"] = df["sultan"].fillna("Inconnu")

print(f"Entrées avec guerre associée : {len(df)}")
print(f"Guerres uniques : {df['part_ofLabel'].nunique()}")

# ─── 2. CONSTRUCTION DU GRAPHE BIPARTITE ─────────────────────────────────────

# Compter le nombre de batailles par paire (sultan, guerre)
paires = (
    df.groupby(["sultan", "part_ofLabel"])
    .size()
    .reset_index(name="poids")
)

# Créer le graphe
G = nx.Graph()

# Ajouter les nœuds sultans
sultans_uniques = paires["sultan"].unique()
for s in sultans_uniques:
    nb = df[df["sultan"] == s].shape[0]
    G.add_node(s, type="sultan", nb=nb)

# Ajouter les nœuds guerres
guerres_uniques = paires["part_ofLabel"].unique()
for g in guerres_uniques:
    nb = df[df["part_ofLabel"] == g].shape[0]
    G.add_node(g, type="guerre", nb=nb)

# Ajouter les arêtes avec poids
for _, row in paires.iterrows():
    G.add_edge(row["sultan"], row["part_ofLabel"], weight=row["poids"])

print(f"Nœuds : {G.number_of_nodes()} | Arêtes : {G.number_of_edges()}")

# ─── 3. MISE EN PAGE (LAYOUT BIPARTITE) ──────────────────────────────────────

# Séparer les deux ensembles de nœuds pour le layout
noeuds_sultans = [n for n, d in G.nodes(data=True) if d["type"] == "sultan"]
noeuds_guerres = [n for n, d in G.nodes(data=True) if d["type"] == "guerre"]

# Positionner manuellement : sultans à gauche, guerres à droite
pos = {}
for i, s in enumerate(sorted(noeuds_sultans)):
    pos[s] = (0, -i * 1.8)
for i, g in enumerate(sorted(noeuds_guerres)):
    pos[g] = (4, -i * 1.1)

# ─── 4. VISUALISATION ────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(16, 14))
fig.patch.set_facecolor("#f5edd8")
ax.set_facecolor("#f5edd8")

# Taille des nœuds sultans proportionnelle au nombre de batailles
tailles_sultans = [G.nodes[n]["nb"] * 40 for n in noeuds_sultans]
couleurs_sultans_list = [COULEURS_SULTANS.get(n, "#aaaaaa") for n in noeuds_sultans]

# Taille des nœuds guerres proportionnelle au nombre de batailles
tailles_guerres = [G.nodes[n]["nb"] * 30 for n in noeuds_guerres]

# Épaisseur des arêtes proportionnelle au poids
edges = G.edges(data=True)
edge_list = [(u, v) for u, v, d in edges]
edge_weights = [d["weight"] for u, v, d in G.edges(data=True)]
max_w = max(edge_weights) if edge_weights else 1
edge_widths = [1 + (w / max_w) * 5 for w in edge_weights]

# Dessiner les arêtes
nx.draw_networkx_edges(
    G, pos,
    edgelist=edge_list,
    width=edge_widths,
    edge_color="#b8860b",
    alpha=0.5,
    ax=ax
)

# Dessiner les nœuds sultans
nx.draw_networkx_nodes(
    G, pos,
    nodelist=noeuds_sultans,
    node_size=tailles_sultans,
    node_color=couleurs_sultans_list,
    edgecolors="#1a1208",
    linewidths=1.0,
    ax=ax
)

# Dessiner les nœuds guerres
nx.draw_networkx_nodes(
    G, pos,
    nodelist=noeuds_guerres,
    node_size=tailles_guerres,
    node_color="#e0d0a8",
    edgecolors="#5c4a2a",
    linewidths=0.8,
    ax=ax
)

# Étiquettes sultans (à gauche des nœuds)
for s in noeuds_sultans:
    x, y = pos[s]
    ax.text(
        x - 0.15, y, s,
        ha="right", va="center",
        fontsize=9, fontweight="bold", color="#1a1208"
    )

# Étiquettes guerres (à droite des nœuds, texte raccourci si trop long)
for g in noeuds_guerres:
    x, y = pos[g]
    label = g if len(g) <= 32 else g[:30] + "…"
    ax.text(
        x + 0.15, y, label,
        ha="left", va="center",
        fontsize=7.5, color="#1a1208"
    )

ax.set_title(
    "Réseau sultan ↔ conflits dans les Balkans (1354–1683)\n"
    "Taille des nœuds ∝ nombre de batailles · Épaisseur des arêtes ∝ batailles partagées",
    fontsize=13, fontweight="bold", color="#1a1208", pad=16
)

# Légende
patch_sultan = mpatches.Patch(color="#8b3a1a", label="Sultan")
patch_guerre  = mpatches.Patch(facecolor="#e0d0a8", edgecolor="#5c4a2a", label="Conflit / Guerre")
ax.legend(handles=[patch_sultan, patch_guerre], loc="lower right", fontsize=10)

ax.axis("off")
plt.tight_layout()
plt.savefig(OUTPUT_RESEAU, dpi=150, bbox_inches="tight")
plt.close()
print(f"Réseau sauvegardé → {OUTPUT_RESEAU}")