import sys
import os
import zipfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.lines import Line2D

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE,
    LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON,
    FIGURE_DPI,
    COLOR_BLUE, COLOR_LIGHT_BLUE,
    TICK_FONT_SIZE,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    GRID_COLOR, GRID_LINEWIDTH
)

usecols = [
  "annee",
  "patho_niv1", "patho_niv2", "patho_niv3",
  "top",
  "cla_age_5", "libelle_classe_age",
  "sexe", "libelle_sexe",
  "region", "dept",
  "Npop", "Ntop"
]

try : 
    df = pd.read_csv("./datasets/effectifs.csv", sep=";", dtype=str, usecols=usecols)
except Exception as e:
    with zipfile.ZipFile("./datasets/effectifs.zip", "r") as zip_ref:
        zip_ref.extractall("./datasets/")
    df = pd.read_csv("./datasets/effectifs.csv", sep=";", dtype=str, usecols=usecols)

df["annee"] = df["annee"].astype(int)
for col in ["Npop", "Ntop"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

ANNEE_ETUDE = 2023
df_etude = df[df["annee"] == ANNEE_ETUDE].copy()

classes_65plus_ordered = ["65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95et+"]
#classes_age_ordered = ["0-4","5-9", "10-14","15-19", "20-24","25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95et+"]


# 1) DÉNOMINATEUR : population par classe d'âge et sexe (2023)
mask_pop_study = (
    (df_etude["patho_niv1"] == "Total consommants tous régimes") &
    (df_etude["patho_niv2"] == "Total consommants tous régimes") &
    (df_etude["patho_niv3"] == "Total consommants tous régimes") &
    (df_etude["top"] == "POP_TOT_IND") &
    (df_etude["cla_age_5"].isin(classes_65plus_ordered)) &
    (df_etude["sexe"].isin(["1", "2"]))
)

pop_study = df_etude[mask_pop_study].copy()
pop_study["Npop"] = pd.to_numeric(pop_study["Npop"], errors="coerce")

pop_age_sex = (
    pop_study
    .groupby(["cla_age_5", "sexe"], dropna=True)["Npop"]
    .sum()
    .reset_index()
)

# 2) NUMÉRATEUR : antidépresseurs par classe d'âge et sexe (2023)
mask_ad_study = (
    (df_etude["top"] == "TPS_ADR_EXC") &
    (df_etude["cla_age_5"].isin(classes_65plus_ordered)) &
    (df_etude["sexe"].isin(["1", "2"]))
)

ad_study = df_etude[mask_ad_study].copy()
ad_study["Ntop"] = pd.to_numeric(ad_study["Ntop"], errors="coerce")

ad_age_sex = (
    ad_study
    .groupby(["cla_age_5", "sexe"], dropna=True)["Ntop"]
    .sum()
    .reset_index()
)

# 3) Fusion et calcul de prévalence
prev_age_sex = pop_age_sex.merge(
    ad_age_sex,
    on=["cla_age_5", "sexe"],
    how="left"
)

prev_age_sex["prev_pct"] = prev_age_sex["Ntop"] / prev_age_sex["Npop"] * 100

# Calcul de l'intervalle de confiance à 95% pour la prévalence
prev_age_sex["p"] = prev_age_sex["Ntop"] / prev_age_sex["Npop"]

prev_age_sex["se"] = np.sqrt(
    (prev_age_sex["p"] * (1 - prev_age_sex["p"])) /
    prev_age_sex["Npop"]
)

prev_age_sex["ci95"] = 1.96 * prev_age_sex["se"]

prev_age_sex["prev_pct"] = prev_age_sex["p"] * 100
prev_age_sex["ci95_pct"] = prev_age_sex["ci95"] * 100

# Séparer femmes et hommes
prev_femmes = prev_age_sex[prev_age_sex["sexe"] == "2"].sort_values("cla_age_5")
prev_hommes = prev_age_sex[prev_age_sex["sexe"] == "1"].sort_values("cla_age_5")


prev_femmes["cla_age_5"] = pd.Categorical(prev_femmes["cla_age_5"],
                                          categories=classes_65plus_ordered,
                                          ordered=True)
prev_hommes["cla_age_5"] = pd.Categorical(prev_hommes["cla_age_5"],
                                          categories=classes_65plus_ordered,
                                          ordered=True)

# Affichage de la figure
fig, ax = plt.subplots(figsize=(10, 6))
sns.set_style("whitegrid")
# Utiliser les classes qui ont des données
prev_femmes_clean = prev_femmes.dropna(subset=["prev_pct"])
prev_hommes_clean = prev_hommes.dropna(subset=["prev_pct"])

classes_with_data = prev_femmes_clean["cla_age_5"].values

x = np.arange(len(classes_with_data))
width = 0.35

error_kw = dict(
    elinewidth=5
)

bars1 = ax.bar(
    x - width/2,
    prev_femmes_clean["prev_pct"].values,
    width,
    yerr=prev_femmes_clean["ci95_pct"],
    capsize=0,
    error_kw=error_kw,
    label="Femmes",
    color=COLOR_LIGHT_BLUE
)

bars2 = ax.bar(
    x + width/2,
    prev_hommes_clean["prev_pct"].values,
    width,
    yerr=prev_hommes_clean["ci95_pct"],
    capsize=0,
    error_kw=error_kw,
    label="Hommes",
    color=COLOR_BLUE
)

# Ajout des valeurs sur les barres
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if not pd.isna(height) and height > 0:
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + 0.2,
                f"{height:.1f}%",
                ha="center",
                fontsize=TICK_FONT_SIZE
            )

ax.set_xlabel("Classe d'âge", fontsize=XLABEL_FONT_SIZE)
ax.set_ylabel("Part de la classe d'âge (%)", fontsize=YLABEL_FONT_SIZE)

ax.set_title(
    f"Part des 65 ans et plus ayant eu au moins un remboursement\npour antidépresseur en France en {ANNEE_ETUDE}, par sexe",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

ax.set_xticks(x)
ax.set_xticklabels(classes_65plus_ordered, fontsize=TICK_FONT_SIZE)
ax.tick_params(axis='y', labelsize=TICK_FONT_SIZE)

ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
ax.set_axisbelow(True)

ic_handle = Line2D(
    [0], [0],
    color="black",
    marker="|",
    markersize=9,
    linestyle="None",
    markeredgewidth=5
)

handles, labels = ax.get_legend_handles_labels()

ax.legend(
    handles + [ic_handle],
    labels + ["IC 95 %"],
    fontsize=LEGEND_FONT_SIZE,
    loc=LEGEND_LOC,
    frameon=LEGEND_FRAMEON
)

plt.figtext(
    0,
    0.01,
    "Source des données : CNAM - Effectifs de patients par pathologie 2025",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()
plt.savefig("./figures/figure2a.png",
            dpi=FIGURE_DPI,
            bbox_inches="tight")

plt.show()