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
df_illec = pd.read_excel(
    './datasets/illectronisme_insee.xlsx',
    sheet_name='Tableau complémentaire 2',
    skiprows=[0,1]
)

df_illec_metier = df_illec.iloc[8:13,:]

# Graphique
fig, ax = plt.subplots(figsize=(10,6))
sns.set_style("whitegrid")

bars = ax.bar(
    df_illec_metier["Caractéristique"],
    df_illec_metier["Personnes âgées de 60 ans ou plus"],
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
    "Part des 60 ans et plus en situation d’illectronisme\nselon le niveau d’études",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

ax.set_xticklabels([
    "Aucun diplôme\n ou CEP",
    "CAP / BEP",
    "Bac ou équivalent",
    "Bac+2",
    "Bac+3 ou plus"
])

ax.set_xlabel(
    "Niveau d'études",
    fontsize=XLABEL_FONT_SIZE
)

ax.set_ylabel(
    "Part des 60 ans et plus (%)",
    fontsize=YLABEL_FONT_SIZE
)

ax.set_ylim(0, 67)

ax.tick_params(axis='both', labelsize=TICK_FONT_SIZE)

ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
ax.set_axisbelow(True)

plt.figtext(
    0,
    0.01,
    "Source des données : INSEE - Enquête TIC ménages 2021",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()

plt.savefig(
    "./figures/figure2e1.png",
    dpi=FIGURE_DPI,
    bbox_inches="tight"
)

plt.show()