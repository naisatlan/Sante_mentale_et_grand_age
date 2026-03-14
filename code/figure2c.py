import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gzip
import json
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
import seaborn as sns

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    FIGURE_DPI,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA,
    LEGEND_FONT_SIZE,
    COLOR_MAP
)

# Paramètres

DATA_DIR = "./datasets"
OUT_DIR = "./figures"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

APL_CSV_PATH = os.path.join(
    DATA_DIR,
    "APL.csv"
)

CONTOURS_BASE = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2024/geojson"
COMMUNES_URL = f"{CONTOURS_BASE}/communes-100m.geojson.gz"

COMMUNES_LOCAL = os.path.join(DATA_DIR, "communes-100m.geojson.gz")

# Fonctions utilitaires
def download_if_missing(url, dst):
    if os.path.exists(dst):
        return

    print("Téléchargement :", url)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()

    with open(dst, "wb") as f:
        for chunk in r.iter_content(1_048_576):
            if chunk:
                f.write(chunk)

def read_geojson_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        gj = json.load(f)
    return gpd.GeoDataFrame.from_features(gj["features"], crs="EPSG:4326")

def guess_insee_col(gdf):
    for c in gdf.columns:
        if "code" in c.lower() or "insee" in c.lower():
            return c
    raise ValueError("Colonne INSEE introuvable")

# Chargement APL
apl = pd.read_csv(APL_CSV_PATH, sep=None, engine="python")

apl.columns = [c.replace("\ufeff", "") for c in apl.columns]

apl["CODE_COM"] = apl["CODE_COM"].astype(str).str.strip()

for col in ["APL_EHPA", "APL_SAPA"]:
    apl[col] = pd.to_numeric(apl[col], errors="coerce")


# Chargement contours
download_if_missing(COMMUNES_URL, COMMUNES_LOCAL)

communes = read_geojson_gz(COMMUNES_LOCAL)

insee_col = guess_insee_col(communes)

communes[insee_col] = communes[insee_col].astype(str)

# Jointure
gdf = communes.merge(
    apl,
    left_on=insee_col,
    right_on="CODE_COM",
    how="inner"
)

# Fonction de carte
def plot_choropleth(gdf, column, title, filename):

    vmax = gdf[column].quantile(0.99)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_style("whitegrid")

    gdf.plot(
        ax=ax,
        column=column,
        legend=True,
        cmap=COLOR_MAP,
        vmax=vmax,
        linewidth=0,
        edgecolor="0.3",
        legend_kwds={
            "label": column,
            "shrink": 0.7
        }
    )
    label = column.replace("_", " ")

    cbar = ax.get_figure().axes[-1]
    cbar.tick_params(labelsize=LEGEND_FONT_SIZE)

    cbar.set_ylabel(
        label,
        fontsize=LEGEND_FONT_SIZE,
        labelpad=10
    )

    ax.set_axis_off()

    ax.set_title(
        title,
        fontsize=TITLE_FONT_SIZE,
        weight=TITLE_WEIGHT,
        loc=TITLE_LOC,
        pad=15
    )

    cbar = ax.get_figure().axes[-1]
    cbar.tick_params(labelsize=LEGEND_FONT_SIZE)

    plt.figtext(
        0,
        0.01,
        "Source : DREES – Accessibilité potentielle localisée aux structures médico-sociales destinées aux personnes âgées (2021)",
        ha=SOURCE_HA,
        fontsize=SOURCE_FONT_SIZE,
        style=SOURCE_STYLE
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(OUT_DIR, filename),
        dpi=FIGURE_DPI,
        bbox_inches="tight"
    )

    plt.show()

# Carte EHPA
plot_choropleth(
    gdf,
    "APL_EHPA",
    "Nombre de places en EHPA (hébergement pour sénior) à moins de 1 heure\n pour 100 000 personnes de 60+ ans",
    "figure2c1.png"
)

# Carte SAPA
plot_choropleth(
    gdf,
    "APL_SAPA",
    "Nombre d’aides à domicile à moins de 30 minutes\n pour 100 000 personnes de 60+ ans",
    "figure2c2.png"
)