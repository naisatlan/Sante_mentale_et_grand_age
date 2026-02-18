# Facteurs associés au syndrome dépressif - Régression multivariée

# Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE, LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON,
    FIGURE_DPI, 
    COLOR_BLUE, COLOR_RED, 
    TICK_FONT_SIZE, 
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA
)

file_path = './datasets/ER1340-Epicov_MEL.xlsx'
sheet_name = 'Graphique 5'

df = pd.read_excel(file_path, engine='openpyxl', sheet_name=sheet_name, header=4)

# Renommer et sélectionner les colonnes utiles
df = df.rename(columns={
    "Caractéristiques des répondants": "facteur",
    "Rapports de prévalence": "rapport de prévalence",
    "IC-95%": "IC95",
    "p-valeur2": "pvalue"
})
df = df[["facteur", "rapport de prévalence", "IC95", "pvalue"]]

# Nettoyer les lignes vides ou invalides et remplacer 
df = df[df["rapport de prévalence"].notna()]
df = df[df["rapport de prévalence"].astype(str).str.strip() != ""]
df = df[~df["rapport de prévalence"].astype(str).str.contains("Manquant", na=False)]
df = df[~df["rapport de prévalence"].astype(str).str.contains("NS", na=False)]
df = df[~df["rapport de prévalence"].astype(str).str.contains("-", na=False)]
df["is_ref"] = df["rapport de prévalence"].astype(str).str.contains("Réf.")
df.loc[df["is_ref"], "rapport de prévalence"] = 1.0

df["rapport de prévalence"] = df["rapport de prévalence"].astype(str).str.replace(",", ".", regex=False)
df["IC95_cleaned"] = df["IC95"].astype(str).str.replace(",", ".", regex=False).str.replace("\u0096", "-", regex=False)
df["pvalue"] = df["pvalue"].astype(str).str.replace("<", "", regex=False)
df["IC95_cleaned"] = (
    df["IC95"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.replace("\u2013", "-", regex=False)
)

# Créer les colonnes d'IC95 inférieure et supérieure
df[["IC95_inf", "IC95_sup"]] = (
    df["IC95_cleaned"]
    .str.split("-", expand=True)
)

df["IC95_inf"] = pd.to_numeric(df["IC95_inf"].str.strip(), errors="coerce")
df["IC95_sup"] = pd.to_numeric(df["IC95_sup"].str.strip(), errors="coerce")

df = df.drop(columns=["IC95_cleaned"])
df = df.drop(columns=["IC95"])

# Créer des catégories pour les facteurs
def categorize(f):
    f = f.lower()

    if "homme" in f or "femme" in f:
        return "Démographie"
    
    if "couple" in f or "ménages complexes" in f or "personne seule" in f:
        return "Structure du foyer"
    
    if ("oui, beaucoup" in f or "certain" in f
        or "pas sûr" in f or "non, peu" in f or "pas du tout" in f
        or "intérêt de l’entourage" in f):
        return "Soutien des proches"

    if ("aide des voisins" in f or "facilement" in f
        or "c’est possible" in f or "possible" in f
        or "difficilement" in f):
        return "Voisinage"

    if ("aucun" in f or "un ou deux" in f
        or "trois à cinq" in f or "six ou plus" in f
        or "proches sur lesq" in f):
        return "Amis"

    if "hétérosex" in f or "homo" in f or "bisex" in f or "souhaite pas répondre" in f:
        return "Orientation sexuelle"

    if "discriminations" in f:
        return "Discriminations"

    if "emploi" in f or "hors emploi" in f :
        return "Emploi"

    if "juste" in f or "difficile" in f or "n’y arrive pas" in f or "aise" in f:
        return "Situation financière"

    if "oui" in f or "non" in f:
        return "Maladie chronique"

    if "heures" in f or "Moins d" in f :
        return "Temps d'écran"

    if "fois par jour" in f or "fois par heure" in f:
        return "Réseaux sociaux"

    if "poids" in f or "obésité" in f or "surpoids" in f or "insuffisance pondérale" in f:
        return "Corpulence"

    if "18-24 ans" in f or "25-34 ans" in f or "35-64 ans" in f or "65 ans ou plus" in f :
        return "Classe d'âge"

    return "Autres"


df["categorie"] = df["facteur"].apply(categorize)

# Exclure les catégories pas pertinentes
categories_exclues = [
    "Démographie",
    "Orientation sexuelle",
    "Temps d'écran",
    "Réseaux sociaux",
    "Autres"
]
df = df[~df["categorie"].isin(categories_exclues)]

df_plot = df.sort_values(
    ["categorie", "is_ref", "rapport de prévalence"]
).reset_index(drop=True)

# Renommer les modalités pour chaque catégorie
rename_dict = {
    "Un ou deux": "1 ou 2",
    "Trois à cinq": "3 à 5",
    "Six ou plus": "6 ou plus",
    "Aucun": "0",

    "Discriminations sur le sexe" : "Sexe",
    "Discriminations sur l’âge" : "Âge",
    "Discriminations sur le poids, le handicap ou l’état de santé" : "Poids, handicap ou santé",
    "Discriminations sur l’origine, la couleur de peau ou la religion" : "Origine, couleur de peau ou religion",
    "Autres discriminations" : "Autres",

    "Oui, beaucoup/Certain" : "Elevé",
    "Pas sûr" : "Moyen",
    "Non, peu/Pas du tout" : "Faible",

    "Facilement/Très facilement" : "Très disponible",
    "C’est possible" : "Peu disponible",
    "Difficilement/Très difficilement" : "Pas disponible"
}

df_plot["facteur"] = df_plot["facteur"].replace(rename_dict)

# Nettoyer
df_plot["rapport de prévalence"] = (
    df_plot["rapport de prévalence"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .str.extract(r"(\d+\.?\d*)")
        .astype(float)
)

# Réordonner les modalités au sein de chaque catégorie
ordre_modalites = {
    "AMIS": ["0", "1 ou 2", "3 à 5", "6 ou plus"],
    "CORPULENCE": ["Insuffisance pondérale", "Poids normal", "Surpoids", "Obésité"],
    "EMPLOI": ["En emploi", "Hors emploi"],
    "SITUATION FINANCIÈRE": [
        "À l'aise/Ça va",
        "Juste",
        "Difficile/N'y arrive pas"
    ],
    "DISCRIMINATIONS": [
        "Âge",
        "Sexe",
        "Poids, handicap ou santé",
        "Origine, couleur de peau ou religion",
        "Autres"],
  "CLASSE D'ÂGE": ["18-24 ans", "25-34 ans", "35-64 ans", "65 ans ou plus"],
    "SOUTIEN DES PROCHES":["Elevé", "Moyen", "Faible"],
    "VOISINAGE":["Très disponible", "Peu disponible", "Pas disponible"],
    "STRUCTURE DU FOYER":["En couple (avec ou sans enfant)","Monoparents et ménages complexes","Personne seule"]

}

# Classer les catégories
ordre_categories = [
    "CLASSE D'ÂGE",
    "CORPULENCE",
    "MALADIE CHRONIQUE",
    "EMPLOI",
    "SITUATION FINANCIÈRE",
    "STRUCTURE DU FOYER",
    "SOUTIEN DES PROCHES",
    "AMIS",
    "VOISINAGE",
    "DISCRIMINATIONS"
]

df_plot["categorie"] = df_plot["categorie"].astype("string").str.strip()
df_plot["facteur"]   = df_plot["facteur"].astype("string").str.strip()

df_sorted = []

# Réordonner les modalités au sein de chaque catégorie
for cat in df_plot["categorie"].unique():
    subset = df_plot[df_plot["categorie"] == cat].copy()
    cat_key = cat.upper()

    if cat_key in ordre_modalites:
        subset["facteur_ord"] = pd.Categorical(
            subset["facteur"],
            categories=ordre_modalites[cat_key],
            ordered=True
        )
        subset = subset.sort_values("facteur_ord", na_position="last")

    df_sorted.append(subset)

df_plot = pd.concat(df_sorted, ignore_index=True)

plt.figure(figsize=(12, 20))

y_positions = []
y_labels = []
y = 0
espace_cat = 1.5

pr_min = min(df_plot["rapport de prévalence"].min(), 0.6)
pr_max = max(df_plot["rapport de prévalence"].max(), 1.8)

pr_min = np.floor(pr_min * 10) / 10
pr_max = np.ceil(pr_max * 10) / 10

# Classer les catégories
categories = [
    cat for cat in ordre_categories
    if cat in df_plot["categorie"].str.upper().unique()
]

# Boucle pour tracer les points et les IC95 pour chaque modalité, en les regroupant par catégorie
for i, cat in enumerate(categories):

    subset = df_plot[df_plot["categorie"].str.upper() == cat]

    if i != 0:
        y += espace_cat
        plt.hlines(
            y - 1.3,
            pr_min - 0.3,
            pr_max,
            color="lightgray",
            linewidth=1
        )

    plt.text(
        pr_min - 0.05,
        y - espace_cat / 2,
        cat.upper(),
        ha="right",
        va="center",
        fontsize=TITLE_FONT_SIZE,
        fontweight=TITLE_WEIGHT
    )

    for _, row in subset.iterrows():

        if row["is_ref"]:
            color = "black"
            x_value = 1
        elif row["rapport de prévalence"] > 1:
            color = COLOR_RED
            x_value = row["rapport de prévalence"]
        else:
            color = COLOR_BLUE
            x_value = row["rapport de prévalence"]

        # IC95
        if not row["is_ref"]:
            x = (row["IC95_inf"] + row["IC95_sup"]) / 2
            xerr = [[x - row["IC95_inf"]], [row["IC95_sup"] - x]]

            plt.errorbar(
                x,
                y,
                xerr=xerr,
                fmt='none',
                ecolor='black',
                elinewidth=1.5,
                capsize=5,
                capthick=1.5,
                zorder=1
            )

        plt.hlines(
            y,
            1,
            x_value,
            color=color,
            linewidth=2
        )
        
        plt.plot(
            row["rapport de prévalence"] if not row["is_ref"] else 1,
            y,
            "o",
            color=color,
            markersize=6,
            zorder=2
        )

        y_positions.append(y)
        y_labels.append(row["facteur"])
        y += 1

plt.axvline(1, linestyle="--", color="black", alpha=0.7)

legend_elements = [
    Line2D([0], [0], marker='o', color='w',markerfacecolor=COLOR_RED,markersize = 8, label='PR > 1 : risque augmenté'),
    Line2D([0], [0], marker='o', color='w',markerfacecolor=COLOR_BLUE,markersize = 8, label='PR < 1 : effet protecteur'),
    Line2D([0], [0], marker='o', color='w',markerfacecolor='black',markersize = 8, label='Modalité de référence (PR = 1)'),
    Line2D([0, 1], [0, 0],color='black', marker='|',markersize=10,markeredgewidth=2,markevery=None, label='Intervalle de confiance à 95%')
]

plt.legend(
    handles=legend_elements,
    loc=LEGEND_LOC,
    bbox_to_anchor=(0.9, -0.04),
    frameon=LEGEND_FRAMEON,
    fontsize=LEGEND_FONT_SIZE
)

plt.figtext(
    0,
    0.01,
    "Source des données : DREES - Enquête EpiCov 2022 – Insee",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

xticks = np.arange(pr_min, pr_max + 0.1, 0.1)
plt.xlim(pr_min, pr_max)
plt.xticks(xticks)

plt.yticks(y_positions, y_labels, fontsize=TICK_FONT_SIZE)
plt.gca().invert_yaxis()

plt.xlabel("Rapport de prévalence (PR)", fontsize=XLABEL_FONT_SIZE)
plt.title(
    r"$\bf{Facteurs\ associés\ au\ syndrome\ dépressif}$" "\n"
    "Régression multivariée",
    fontsize=TITLE_FONT_SIZE,
    pad=20,
    weight=TITLE_WEIGHT,
    loc=TITLE_LOC
)

plt.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("./figures/figure1d.png", dpi=FIGURE_DPI, bbox_inches="tight")
plt.show()
