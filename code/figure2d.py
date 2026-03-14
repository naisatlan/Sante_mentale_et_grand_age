import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import requests
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE,
    FIGURE_DPI,
    TICK_FONT_SIZE,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    COLOR_BLUE, COLOR_RED,
    GRID_COLOR, GRID_LINEWIDTH
)

# Chargement données
df_psy = pd.read_excel(
    "./datasets/MAJ_IND_ATLAS.xlsx",
    sheet_name="Personnes Agées"
).iloc[1:]   # supprime la première ligne

# correction colonne sans nom
df_psy.rename(columns={'': 'PA05_2015'}, inplace=True)

# Chargement FDep (API)
url = "https://odisse.santepubliquefrance.fr/api/explore/v2.1/catalog/datasets/indice-de-defavorisation-sociale-fdep-par-iris/records?limit=-1"
data = requests.get(url).json()

df_fdep = pd.DataFrame(data["results"])

# variables FDep
vars_fdep = ['t1_rev_med', 't1_txbac09', 't1_txouvr0', 't1_txchom0']

# Calcul FDep via PCA : première composante de la PCA de 4 variables 
# - revenu médian par unité de consommation dans le ménage
# - pourcentage de bacheliers dans la population de plus de 15 ans,
# - pourcentage d’ouvriers dans la population active
# - taux de chômage.
scaler = StandardScaler()
X = scaler.fit_transform(df_fdep[vars_fdep])

pca = PCA(n_components=1)
df_fdep["FDep"] = -pca.fit_transform(X)  # inversion → défavorisation

# Agrégation départementaire : médiane des FDep des IRIS de chaque département
df_fdep["DEP"] = df_fdep["t1_com"].astype(str).str[:2]

df_fdep_dept = (
    df_fdep
    .groupby("DEP")["FDep"]
    .median()
    .reset_index()
)

# Fusion datasets
df = pd.merge(df_psy, df_fdep_dept, on="DEP", how="left")

# Moyenne des indicateurs 2015 / 2019
df_ind = pd.DataFrame({
    "DEP": df["DEP"],
    "FDep": df["FDep"],
    "Unités spécialisées": (df["PA05_2015"] + df["PA05_2019"]) / 2,
    "Hospitalisation psy TP": (df["PA07_2015"] + df["PA07_2019"]) / 2,
    "Recours ambulatoire psy": (df["PA08_2015"] + df["PA08_2019"]) / 2,
    "Hospitalisation TS": (df["PA09_2015"] + df["PA09_2019"]) / 2,
    "Hospitalisation MCO psy": (df["PA10_2015"] + df["PA10_2019"]) / 2
})

# Corrélations
corr = (
    df_ind
    .drop(columns="DEP")
    .corr(numeric_only=True)["FDep"]
    .drop("FDep")
    .sort_values()
)

corr = corr.rename({
    "Unités spécialisées": "Unités spécialisées\nen gérontopsychiatrie",
    "Hospitalisation psy TP": "Hospitalisation psychiatrique\n(temps plein)",
    "Recours ambulatoire psy": "Recours ambulatoire\nen psychiatrie",
    "Hospitalisation TS": "Hospitalisation après\ntentative de suicide",
    "Hospitalisation MCO psy": "Hospitalisation MCO\npour trouble psychiatrique"
})

# Graphique
fig, ax = plt.subplots(figsize=(10,6))
sns.set_style("whitegrid")

cmap = mcolors.LinearSegmentedColormap.from_list(
    "blue_red",
    [COLOR_BLUE, "white", COLOR_RED]
)

norm = plt.Normalize(-0.5, 0.4)

colors = cmap(norm(corr.values))
bars = ax.barh(
    corr.index,
    corr.values,
    color=colors
)

ax.axvline(0, color="black", linestyle="--", linewidth=1)

# annotations
for i, v in enumerate(corr.values):
    offset = 0.02

    ax.text(
        v + offset if v > 0 else v - offset,
        i,
        f"{v:.2f}",
        va="center",
        ha="left" if v > 0 else "right",
        fontsize=TICK_FONT_SIZE
    )

ax.set_xlim(-0.5, 0.4)

ax.set_title(
    "Lien entre la défavorisation sociale des départements (FDep)\n"
    "et les indicateurs psychiatriques des 65 ans et plus",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

ax.set_xlabel(
    "Corrélation avec l’indice de défavorisation sociale (FDep)",
    fontsize=XLABEL_FONT_SIZE
)

ax.grid(axis="x", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
ax.set_axisbelow(True)

ax.tick_params(axis='both', labelsize=TICK_FONT_SIZE)

plt.figtext(
    0,
    -0.03,
    "Sources : Santé Publique France - Indice de défavorisation sociale par IRIS ; DREES – Atlas de la santé mentale",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()

plt.savefig(
    "./figures/figure2d.png",
    dpi=FIGURE_DPI,
    bbox_inches="tight"
)

plt.show()