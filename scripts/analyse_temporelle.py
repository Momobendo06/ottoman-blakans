"""
Analyse A — Distribution temporelle des batailles par sultan
Projet : L'expansion ottomane dans les Balkans (1354–1683)
Auteur  : Muhamed Mehic
Cours   : Data Science – Université de Neuchâtel, 2026

Description :
    Ce script produit deux visualisations complémentaires à partir du CSV nettoyé :
    1. Un barplot du nombre de batailles par sultan
    2. Une courbe cumulative des batailles dans le temps
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─── 0. CONFIGURATION ────────────────────────────────────────────────────────

INPUT_CSV  = "data/ottoman_balkans_battles_clean.csv"
OUTPUT_BAR = "outputs/output_barplot_sultans.png"
OUTPUT_CUM = "outputs/output_courbe_cumulative.png"

# Palette cohérente avec le site web (parchemin / rouille / teal)
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

# Ordre chronologique des sultans
ORDRE_SULTANS = [
    "Orhan", "Murad Iᵉʳ", "Bayezid Iᵉʳ", "Interrègne",
    "Mehmed Iᵉʳ", "Murad II", "Mehmed II", "Bayezid II",
    "Selim Iᵉʳ", "Soliman Iᵉʳ", "Selim II",
    "Murad III", "Mehmed III", "Ahmed Iᵉʳ", "Mustafa Iᵉʳ",
    "Osman II", "Murad IV", "Ibrahim Iᵉʳ", "Mehmed IV"
]

# ─── 1. CHARGEMENT DES DONNÉES ───────────────────────────────────────────────

df = pd.read_csv(INPUT_CSV)

# Conversion de la colonne date en datetime (les dates approximatives ont été
# normalisées à "YYYY-01-01" lors du nettoyage Python — on extrait l'année)
df["annee"] = pd.to_datetime(df["date"], errors="coerce").dt.year

# Supprimer les lignes sans année valide
df = df.dropna(subset=["annee"])
df["annee"] = df["annee"].astype(int)

# Uniformiser les noms de sultans absents
df["sultan"] = df["sultan"].fillna("Inconnu")

print(f"Entrées chargées : {len(df)}")
print(f"Sultans présents : {df['sultan'].unique()}")

# ─── 2. ANALYSE A — BARPLOT PAR SULTAN ───────────────────────────────────────

# Compter le nombre de batailles par sultan
compte = df.groupby("sultan").size().reset_index(name="nb_batailles")

# Réordonner selon l'ordre chronologique défini
ordre_existant = [s for s in ORDRE_SULTANS if s in compte["sultan"].values]
compte["sultan"] = pd.Categorical(
    compte["sultan"], categories=ordre_existant, ordered=True
)
compte = compte.sort_values("sultan").dropna(subset=["sultan"])
compte["sultan"] = compte["sultan"].astype(str)

# Associer les couleurs
couleurs = [COULEURS_SULTANS.get(s, "#aaaaaa") for s in compte["sultan"]]

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#f5edd8")   # fond parchemin
ax.set_facecolor("#ede0c4")

barres = ax.bar(
    compte["sultan"],
    compte["nb_batailles"],
    color=couleurs,
    edgecolor="#1a1208",
    linewidth=0.6,
    width=0.65
)

# Annoter chaque barre avec le nombre de batailles
for barre, val in zip(barres, compte["nb_batailles"]):
    ax.text(
        barre.get_x() + barre.get_width() / 2,
        barre.get_height() + 0.4,
        str(val),
        ha="center", va="bottom",
        fontsize=9, color="#1a1208", fontweight="bold"
    )

ax.set_title(
    "Nombre de batailles par sultan dans les Balkans (1354–1683)",
    fontsize=14, fontweight="bold", color="#1a1208", pad=16
)
ax.set_xlabel("Sultan", fontsize=11, color="#5c4a2a", labelpad=10)
ax.set_ylabel("Nombre de batailles", fontsize=11, color="#5c4a2a", labelpad=10)
ax.tick_params(axis="x", rotation=35, labelsize=9, colors="#1a1208")
ax.tick_params(axis="y", labelsize=9, colors="#1a1208")
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#5c4a2a")
ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#5c4a2a")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(OUTPUT_BAR, dpi=150, bbox_inches="tight")
plt.close()
print(f"Barplot sauvegardé → {OUTPUT_BAR}")

# ─── 3. ANALYSE A (bis) — COURBE CUMULATIVE ──────────────────────────────────

# Trier par année et calculer le cumul
df_sorted = df.sort_values("annee")
df_sorted["cumul"] = range(1, len(df_sorted) + 1)

# Dates de règne pour les lignes verticales
regnes = {
    "Orhan"        : (1326, 1362),
    "Murad Iᵉʳ"   : (1362, 1389),
    "Bayezid Iᵉʳ" : (1389, 1402),
    "Mehmed Iᵉʳ"  : (1413, 1421),
    "Murad II"     : (1421, 1451),
    "Mehmed II"    : (1451, 1481),
    "Bayezid II"   : (1481, 1512),
    "Selim Iᵉʳ"   : (1512, 1520),
    "Soliman Iᵉʳ" : (1520, 1566),
    "Selim II"     : (1566, 1574),
    "Murad III"    : (1574, 1595),
    "Mehmed III"   : (1595, 1603),
    "Ahmed Iᵉʳ"   : (1603, 1617),
    "Mustafa Iᵉʳ" : (1617, 1618),
    "Osman II"     : (1618, 1622),
    "Murad IV"     : (1623, 1640),
    "Ibrahim Iᵉʳ" : (1640, 1648),
    "Mehmed IV"    : (1648, 1683),
}

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#f5edd8")
ax.set_facecolor("#ede0c4")

# Zones colorées par règne (alternance rouille/teal)
couleurs_zones = ["#8b3a1a", "#1a5c5c"]
for i, (sultan, (debut, fin)) in enumerate(regnes.items()):
    ax.axvspan(
        debut, fin,
        alpha=0.12,
        color=couleurs_zones[i % 2],
        zorder=0
    )
    # Étiquette du sultan au centre de la zone
    milieu = (debut + fin) / 2
    ax.text(
        milieu, -8, sultan,
        ha="center", va="top",
        fontsize=7, color="#5c4a2a", rotation=30
    )

# Courbe cumulative
ax.plot(
    df_sorted["annee"],
    df_sorted["cumul"],
    color="#8b3a1a",
    linewidth=2,
    zorder=2
)
ax.fill_between(
    df_sorted["annee"],
    df_sorted["cumul"],
    alpha=0.15,
    color="#8b3a1a",
    zorder=1
)

ax.set_title(
    "Cumul des batailles ottomanes dans les Balkans (1354–1683)",
    fontsize=14, fontweight="bold", color="#1a1208", pad=16
)
ax.set_xlabel("Année", fontsize=11, color="#5c4a2a", labelpad=30)
ax.set_ylabel("Nombre cumulé de batailles", fontsize=11, color="#5c4a2a", labelpad=10)
ax.set_xlim(1350, 1690)
ax.tick_params(axis="both", labelsize=9, colors="#1a1208")
ax.spines[["top", "right"]].set_visible(False)
ax.spines[["left", "bottom"]].set_color("#5c4a2a")
ax.yaxis.grid(True, linestyle="--", alpha=0.4, color="#5c4a2a")
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(OUTPUT_CUM, dpi=150, bbox_inches="tight")
plt.close()
print(f"Courbe cumulative sauvegardée → {OUTPUT_CUM}")