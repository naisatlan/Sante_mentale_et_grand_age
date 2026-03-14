import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import numpy as np
import zipfile
import seaborn as sns

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    FIGURE_DPI,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON, 
    COLOR_MAP
)

# Paramètres
usecols = [
  "annee",
  "patho_niv1", "patho_niv2", "patho_niv3",
  "top",
  "cla_age_5", "libelle_classe_age",
  "sexe", "libelle_sexe",
  "region", "dept",
  "Npop", "Ntop"
]
ANNEE = 2023
AGE_65PLUS_CODES = ["65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95et+"]
try : 
    df = pd.read_csv("./datasets/effectifs.csv", sep=";", dtype=str, usecols=usecols)
except Exception as e:
    with zipfile.ZipFile("./datasets/effectifs.zip", "r") as zip_ref:
        zip_ref.extractall("./datasets/")
    df = pd.read_csv("./datasets/effectifs.csv", sep=";", dtype=str, usecols=usecols)

ATLAS_XLSX_PATH = "./datasets/MAJ_IND_ATLAS.xlsx"
ATLAS_SHEET = "Personnes Agées"
ATLAS_DEP_COL = "DEP"
ATLAS_UNITS_COL = "PA05_2019"  # nb d'unités spécialisées psy (2019)

# Fond de carte
GEOJSON_DEPTS = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def normalize_dept_code(x) -> str:
    """Normalise un code département au format attendu: '01'..'95', '2A','2B', '971'.., et garde '9A'..'9F'."""
    if pd.isna(x):
        return pd.NA
    s = str(x).strip().upper()

    if s.endswith(".0"):
        s = s[:-2]

    # codes alphanum (2A/2B, 9A..9F, etc.) -> on garde tel quel
    if any(ch.isalpha() for ch in s):
        return s

    # codes numériques
    if s.isdigit():
        # Métropole: 2 chiffres
        if len(s) <= 2:
            return s.zfill(2)
        # DOM/TOM: 3 chiffres (971..)
        return s

    return s

# Charger effectifs et calculer population 65+ par département (année ANNEE)
usecols = [
    "annee",
    "patho_niv1", "patho_niv2", "patho_niv3",
    "top",
    "cla_age_5",
    "sexe",
    "dept",
    "Npop"
]

df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
df["Npop"]  = pd.to_numeric(df["Npop"], errors="coerce")

df_year = df[(df["annee"] == ANNEE) & (df["dept"] != "999")].copy()
df_year = df_year[df_year["cla_age_5"].isin(AGE_65PLUS_CODES)].copy()

mask_pop = (
    (df_year["patho_niv1"] == "Total consommants tous régimes") &
    (df_year["patho_niv2"] == "Total consommants tous régimes") &
    (df_year["patho_niv3"] == "Total consommants tous régimes") &
    (df_year["top"] == "POP_TOT_IND")
)

pop_65 = df_year[mask_pop].copy()

# Ici on somme hommes+femmes (sexe 1 et 2), comme dans ton code
pop_65 = pop_65[pop_65["sexe"].isin(["1", "2"])].copy()

pop_dept_age_sex = (
    pop_65
    .groupby(["dept", "cla_age_5", "sexe"], dropna=False)["Npop"]
    .max()
    .reset_index()
)

pop_dept_65 = (
    pop_dept_age_sex
    .groupby("dept", dropna=False)["Npop"]
    .sum()
    .reset_index()
    .rename(columns={"Npop": "Npop_65plus"})
)

# Charger l'atlas (unités spécialisées psy) et normaliser les codes DEP
atlas = pd.read_excel(
    ATLAS_XLSX_PATH,
    sheet_name=ATLAS_SHEET,
    usecols=[ATLAS_DEP_COL, ATLAS_UNITS_COL],
    dtype={ATLAS_DEP_COL: "string"}
).rename(columns={ATLAS_DEP_COL: "dept", ATLAS_UNITS_COL: "units_psy_pa"})

atlas["dept"] = atlas["dept"].map(normalize_dept_code)
atlas["units_psy_pa"] = pd.to_numeric(atlas["units_psy_pa"], errors="coerce")  # garde 0

# Si plusieurs lignes par dept -> on somme (0 reste 0, NA reste NA si tout est NA)
atlas_dept = (
    atlas
    .groupby("dept", dropna=False)["units_psy_pa"]
    .sum(min_count=1)
    .reset_index()
)

# Fusion + calcul indicateur
df_ind = pop_dept_65.merge(atlas_dept, on="dept", how="left")

# Indicateur : unités pour 100 000 habitants de 65+
df_ind["units_per_100k_65plus"] = np.where(
    df_ind["Npop_65plus"] > 0,
    df_ind["units_psy_pa"] / df_ind["Npop_65plus"] * 100_000,
    np.nan
)

# Carte
gdf_depts = gpd.read_file(GEOJSON_DEPTS)
gdf_map = gdf_depts.merge(df_ind, left_on="code", right_on="dept", how="left")

norm = mcolors.PowerNorm(
    gamma=0.5,
    vmin=0,
    vmax=df_ind["units_per_100k_65plus"].max()
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.set_style("whitegrid")

gdf_map.plot(
    ax=ax,
    column="units_per_100k_65plus",
    legend=True,
    cmap=COLOR_MAP,
    norm=norm,
    edgecolor="0.4",
    linewidth=0.4,
    legend_kwds={
        "label": "Unités pour 100 000 habitants de 65 ans et +",
        "shrink": 0.7
    },
    missing_kwds={
        "color": "lightgrey",
        "edgecolor": "white",
        "hatch": "///",
        "label": "Données manquantes"
    }
)

cbar = ax.get_figure().axes[-1]
cbar.tick_params(labelsize=LEGEND_FONT_SIZE)
cbar.set_ylabel(
    "Unités pour 100 000 habitants de 65 ans et +",
    fontsize=LEGEND_FONT_SIZE, 
    labelpad=10
)

ax.set_axis_off()

ax.set_title(
    "Unités spécialisées en gérontopsychiatrie\n"
    f"pour 100 000 habitants de 65+ ans ({ANNEE}), par département",
    fontsize=TITLE_FONT_SIZE,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC,
    pad=15
)

plt.figtext(
    0,
    0.01,
    "Sources : CNAM – Effectifs de patients par pathologie ; DREES - Atlas de la santé mentale en 2023 (PA05_2019)",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()

plt.savefig(
    "./figures/figure2b.png",
    dpi=FIGURE_DPI,
    bbox_inches="tight"
)

plt.show()