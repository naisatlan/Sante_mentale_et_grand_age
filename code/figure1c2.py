import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE,
    TICK_FONT_SIZE,
    COLOR_BLUE, COLOR_RED, COLOR_LIGHT_BLUE,
    GRID_COLOR, GRID_LINEWIDTH,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    FIGURE_DPI,
    LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON
)

# Dataset 1 : contacts sociaux
df_contacts = pd.read_excel(
    "./datasets/contacts_amis_famille.xlsx",
    skiprows=3
)

age = df_contacts[df_contacts.columns[0]].iloc[7:12]

contacts_famille = df_contacts[df_contacts.columns[5]].iloc[7:12]
contacts_amis = df_contacts[df_contacts.columns[6]].iloc[7:12]

# Dataset 2 : personnes seules
df_seul = pd.read_excel(
    "./datasets/personnes_ages_seules.xlsx",
    skiprows=4
)

df_seul = df_seul.drop(index=[1, 4, 7])
age_seul = df_seul[df_seul.columns[0]].iloc[0:7]

seul = df_seul[df_seul.columns[18]].iloc[0:7]

# Positions d'âge (milieu des tranches)
age_mid = [20, 32, 45, 57, 70]

age_seul_mid = [17, 22, 32, 47, 59.5, 72, 80]

# Graphique
fig, ax = plt.subplots(figsize=(10,6))
sns.set_style("whitegrid")

ax.plot(
    age_seul_mid,
    seul,
    color=COLOR_RED,
    label="Personnes vivant seules"
)

ax.plot(
    age_mid,
    contacts_amis,
    color=COLOR_BLUE,
    label="Contact hebdomadaire avec les amis"
)

ax.plot(
    age_mid,
    contacts_famille,
    color=COLOR_LIGHT_BLUE,
    label="Contact hebdomadaire avec la famille"
)

ax.axvspan(70, 80, ymin=0.53, ymax=1, alpha=0.15, color="grey")

ax.set_title(
    "Isolement et contacts sociaux \n(communication ou recontres) selon l’âge (2022)",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

ax.set_xlabel(
    "Âge",
    fontsize=XLABEL_FONT_SIZE
)

ax.set_xlim(20, 80)

ax.set_ylabel(
    "Part de la population (%)",
    fontsize=YLABEL_FONT_SIZE
)

# graduations tous les 5 ans
ax.set_xticks(range(20, 80, 5))

ax.tick_params(labelsize=TICK_FONT_SIZE)

ax.grid(color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
ax.set_axisbelow(True)

plt.legend(fontsize=LEGEND_FONT_SIZE, frameon=LEGEND_FRAMEON, loc="lower right")

plt.figtext(
    0,
    -0.03,
    "Sources des données : Insee – Recensement de la population 2022 ; Insee - enquête SRCV 2022",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()

plt.savefig(
    "./figures/figure1c2.png",
    dpi=FIGURE_DPI,
    bbox_inches="tight"
)

plt.show()