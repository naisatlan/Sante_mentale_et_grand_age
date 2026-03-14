# Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE, LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON,
    FIGURE_DPI, 
    COLOR_BLUE,
    TICK_FONT_SIZE, 
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA, 
    GRID_COLOR, GRID_LINEWIDTH
)

df_illec = pd.read_excel('./datasets/illectronisme_insee.xlsx', sheet_name='Tableau complémentaire 2', skiprows=[0,1])
df_illec.head()

df_illec_age = df_illec.iloc[:6,:2]
df_illec_age.drop([0], inplace=True)

# tracé d'un barplot de l'illectronisme par tranches d'âge
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
plt.bar(df_illec_age["Caractéristique"],df_illec_age["Personnes âgées de 15 ans ou plus"], color=COLOR_BLUE)
plt.title("Pourcentage d'illectronisme par tranche d'âge\n en France en 2021",fontsize=TITLE_FONT_SIZE, weight=TITLE_WEIGHT, loc=TITLE_LOC, pad=15)
plt.xlabel("Tranche d'âge", fontsize=XLABEL_FONT_SIZE)
plt.ylabel("Pourcentage (%)", fontsize=YLABEL_FONT_SIZE)
plt.xticks(fontsize=TICK_FONT_SIZE)
plt.yticks(fontsize=TICK_FONT_SIZE)
plt.ylim(0, 70)
plt.grid(axis='y', color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
plt.gca().set_axisbelow(True)

plt.figtext(
    0,
    0.01,
    "Source des données : INSEE - Enquête TIC ménages 2021",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

# ajout des valeurs au-dessus de chaque barre
for i, val in enumerate(df_illec_age["Personnes âgées de 15 ans ou plus"]):

  plt.text(i, val + 1, f"{val:.1f}%", ha='center', fontsize=TICK_FONT_SIZE)

plt.tight_layout()
plt.savefig("./figures/figure1e.png", dpi=FIGURE_DPI, bbox_inches="tight")
plt.show()