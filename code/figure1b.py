#Part des personnes avec au moins un remboursement d'antidépresseurs selon l'âge

# Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import zipfile
import seaborn as sns
from statsmodels.stats.proportion import proportion_confint

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE,
    GRID_COLOR, GRID_LINEWIDTH,
    FIGURE_DPI, 
    COLOR_BLUE, 
    TICK_FONT_SIZE, 
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA
)

# Colonnes utiles 
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
#Filtrer pour l'année 2023
df["annee"] = df["annee"].astype(int)
for col in ["Npop", "Ntop"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

ANNEE = 2023
df_year = df[df["annee"] == ANNEE].copy()
df_year = df_year[df_year["dept"] != "999"].copy()

# Population totale par classe d'âge (total consommants / POP_TOT_IND)
mask_pop = (
    (df_year["patho_niv1"] == "Total consommants tous régimes") &
    (df_year["patho_niv2"] == "Total consommants tous régimes") &
    (df_year["patho_niv3"] == "Total consommants tous régimes") &
    (df_year["top"] == "POP_TOT_IND")
)

pop = df_year[mask_pop].copy()
pop = pop[pop["sexe"].isin(["1", "2"])]  # H + F

# Fusion du département, de la classe d'âge et du sexe
pop_dept_age_sex = (
    pop
    .groupby(["dept", "cla_age_5", "libelle_classe_age", "sexe"], dropna=False)["Npop"]
    .max()
    .reset_index()
)

# Population France entière tous sexes par classe d'âge
pop_nat_age = (
    pop_dept_age_sex
    .groupby(["cla_age_5", "libelle_classe_age"], dropna=False)["Npop"]
    .sum()
    .reset_index()
    .rename(columns={"Npop": "Npop_all"})
)

# Antidépresseurs (TPS_ADR_EXC) par classe d'âge
mask_ad = (df_year["top"] == "TPS_ADR_EXC")
ad = df_year[mask_ad].copy()
ad = ad[ad["sexe"].isin(["1", "2"])]

ad_dept_age_sex = (
    ad
    .groupby(["dept", "cla_age_5", "libelle_classe_age", "sexe"], dropna=False)["Ntop"]
    .sum()
    .reset_index()
)

ad_nat_age = (
    ad_dept_age_sex
    .groupby(["cla_age_5", "libelle_classe_age"], dropna=False)["Ntop"]
    .sum()
    .reset_index()
    .rename(columns={"Ntop": "Ntop_all"})
)

# 4) Fusion + prévalence
prev_age = pop_nat_age.merge(
    ad_nat_age,
    on=["cla_age_5", "libelle_classe_age"],
    how="left"
)

prev_age["prev_pct"] = prev_age["Ntop_all"] / prev_age["Npop_all"] * 100

# On enlève la ligne 'tous âges' pour le graphique
prev_age_plot = prev_age[prev_age["cla_age_5"] != "tsage"].copy()
prev_age_plot = prev_age_plot.sort_values("cla_age_5")

# Créer une colonne numérique "age_debut" à partir de cla_age_5
def extraire_age_debut(code):
    # Exemples : "00-04", "05-09", "65-69", "95et+"
    if "-" in code:
        return int(code.split("-")[0])
    if code.startswith("95"):  # "95et+" par ex.
        return 95
    return None  # au cas où, mais ici on a filtré tsage etc.

prev_age_plot["age_debut"] = prev_age_plot["cla_age_5"].apply(extraire_age_debut)

# On trie selon cet âge numérique
prev_age_plot = prev_age_plot.sort_values("age_debut")

def calculate_binomial_ci(n_success, n_total, confidence=0.99):
    if n_total == 0 or pd.isna(n_success) or pd.isna(n_total):
        return np.nan, np.nan

    ci_low, ci_high = proportion_confint(
        count=n_success,
        nobs=n_total,
        alpha=1-confidence,
        method='wilson'
    )

    return ci_low * 100, ci_high * 100

prev_age_plot[["ci_lower", "ci_upper"]] = prev_age_plot.apply(
    lambda row: pd.Series(calculate_binomial_ci(row["Ntop_all"], row["Npop_all"])),
    axis=1
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.set_theme(style="whitegrid", context="notebook")

# Zone d'incertitude (intervalle de confiance)
ax.fill_between(prev_age_plot["age_debut"], 
                prev_age_plot["ci_lower"], 
                prev_age_plot["ci_upper"], 
                alpha=0.2, color=COLOR_BLUE, label='IC 95%')

# Courbe principale
ax.plot(prev_age_plot["age_debut"], prev_age_plot["prev_pct"], marker="o", color=COLOR_BLUE, linewidth=2, markersize=6)

# Ticks/grille tous les 10 ans (au lieu de 5)
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_major_locator(MultipleLocator(5))

ax.set_ylabel("Pourcentage de la population (%)", fontsize=YLABEL_FONT_SIZE)
ax.set_xlabel("Âge", fontsize=XLABEL_FONT_SIZE)
ax.set_title(
    f"Part des personnes avec au moins un remboursement \nd'antidépresseur selon l'âge ({ANNEE}, France)",
    fontsize=TITLE_FONT_SIZE, weight=TITLE_WEIGHT, loc=TITLE_LOC
)
plt.xticks(fontsize=TICK_FONT_SIZE)
plt.yticks(fontsize=TICK_FONT_SIZE)

ax.grid(True, which="major", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)

ax.legend(loc='upper left', fontsize=11)

plt.figtext(
    0,
    -0.05,
    "Source des données : CNAM - Effectifs de patients par pathologie 2025",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

fig.tight_layout()
plt.savefig("./figures/figure1b.png", dpi=FIGURE_DPI, bbox_inches="tight")
plt.show()


# A faire : calculer la variance pour faire un serpent.