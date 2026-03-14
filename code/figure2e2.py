import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE,
    FIGURE_DPI,
    COLOR_BLUE,
    TICK_FONT_SIZE,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    GRID_COLOR, GRID_LINEWIDTH
)

# Chargement des données
df_illec_csp = pd.read_excel(
    "./datasets/illectronisme_insee.xlsx",
    sheet_name="Tableau complémentaire 1",
    skiprows=[0,1]
)

# On garde uniquement les 5 premières catégories socioprofessionnelles
df_illec_csp = df_illec_csp.iloc[:5, :]

df_illec_csp["Catégorie socioprofessionnelle ou statut d'activité"] = \
df_illec_csp["Catégorie socioprofessionnelle ou statut d'activité"].replace({
    "Agriculteurs, artisans et commerçants": "Agriculteurs,\nartisans, commerçants",
    "Cadres et professions libérales": "Cadres et\nprofessions libérales",
    "Professions intermédiaires": "Professions\nintermédiaires"
})

df_illec_csp = df_illec_csp.sort_values("Retraités", ascending=False)

# Graphique
fig, ax = plt.subplots(figsize=(10,6))
sns.set_style("whitegrid")

bars = ax.bar(
    df_illec_csp["Catégorie socioprofessionnelle ou statut d'activité"],
    df_illec_csp["Retraités"],
    color=COLOR_BLUE
)

# annotations
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.1f}%",
        ha="center",
        fontsize=TICK_FONT_SIZE
    )

ax.set_title(
    "Part des retraités en situation d’illectronisme\nselon leur ancienne catégorie socioprofessionnelle",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

ax.set_xlabel(
    "Ancienne catégorie socioprofessionnelle",
    fontsize=XLABEL_FONT_SIZE, 
    labelpad=10
)

ax.set_ylabel(
    "Part des retraités (%)",
    fontsize=YLABEL_FONT_SIZE
)

ax.set_ylim(0, 60)

ax.tick_params(axis='both', labelsize=TICK_FONT_SIZE)

ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
ax.set_axisbelow(True)

plt.figtext(
    0,
    -0.03,
    "Source des données : INSEE - Enquête TIC ménages 2021",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()

plt.savefig(
    "./figures/figure2e2.png",
    dpi=FIGURE_DPI,
    bbox_inches="tight"
)

plt.show()