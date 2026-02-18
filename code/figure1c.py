#Prévalence des limitations chez les seniors et évolution de ces limitations entre 60-74 ans et après 75 ans

#Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE,
    LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON,
    COLOR_BLUE, COLOR_LIGHT_BLUE,
    FIGURE_DPI
)

# Lecture des données
file_path = './datasets/enqueteVQS.ods'
sheet_name_aide = 'Aide ou aménagements'
sheet_name_activités = 'Difficultés pour les activités quotidiennes'
sheet_name_santé = 'Santé'

df_aide = pd.read_excel(file_path, engine='odf', sheet_name=sheet_name_aide)
print(f"Successfully loaded sheet '{sheet_name_aide}' from '{file_path}'.")

df_activités = pd.read_excel(file_path, engine='odf', sheet_name=sheet_name_activités)
print(f"Successfully loaded sheet '{sheet_name_activités}' from '{file_path}'.")

df_santé = pd.read_excel(file_path, engine='odf', sheet_name=sheet_name_santé)
print(f"Successfully loaded sheet '{sheet_name_santé}' from '{file_path}'.")

#Agrégation des données pour calculer les indicateurs
def extract_indicator(df, questions, rep_positive=["Oui", "Ne peut pas du tout"]):
    sub = df[df["QUESTION"].isin(questions)]
    sub_pos = sub[sub["REPONSE"].isin(rep_positive)]

    pos_tous = sub_pos["H et F (tous)"].sum()
    pos_60_74 = sub_pos["H et F (60-74 ans)"].sum()
    pos_75_plus = sub_pos["H et F (75 ans et +)"].sum()

    total = df[(df["QUESTION"].isin(questions)) & (df["REPONSE"].str.contains("Total"))]

    total_tous = total["H et F (tous)"].sum()
    total_60_74 = total["H et F (60-74 ans)"].sum()
    total_75_plus = total["H et F (75 ans et +)"].sum()

    return {
        "60_plus": pos_tous / total_tous,
        "60_74": pos_60_74 / total_60_74,
        "75_plus": pos_75_plus / total_75_plus
    }

# Fonctionnels
questions_fonctionnel = [
    q for q in df_activités["QUESTION"].unique()
    if "monter un étage" in q.lower()
    or "se pencher" in q.lower()
    or "se laver" in q.lower()
    or "500 mètres" in q.lower()
    or "se servir de ses mains" in q.lower()
    or "sortir de son logement" in q.lower()
    or "lever le bras" in q.lower()
]

# Cognitifs
questions_cognitif = [
    q for q in df_activités["QUESTION"].unique()
    if "concentrer" in q.lower()
    or "souvenir" in q.lower()
    or "résoudre" in q.lower()
    or "comprendre" in q.lower()
]

# Sensoriels
questions_sensoriel = [
    q for q in df_activités["QUESTION"].unique()
    if "entendre" in q.lower()
    or "voir" in q.lower()
]

# Dépendance (df_aide)
questions_dependance = [
    q for q in df_aide["QUESTION"].unique()
    if "aide" in q.lower()
    or "aménagements" in q.lower()
    or "aide technique" in q.lower()
]

# Santé (df_santé)
questions_santé = [
    q for q in df_santé["QUESTION"].unique()
    if "maladie" in q.lower() and "chronique" in q.lower()
]

ind_fonctionnel = extract_indicator(df_activités, questions_fonctionnel)
ind_cognitif = extract_indicator(df_activités, questions_cognitif)
ind_sensoriel = extract_indicator(df_activités, questions_sensoriel)
ind_dependance = extract_indicator(df_aide, questions_dependance, rep_positive=["Oui"])  # ici pas de "ne peut pas du tout"
ind_santé = extract_indicator(df_santé, questions_santé, rep_positive=["Oui"])

df_indicateurs = pd.DataFrame({
    "indicateur": ["fonctionnel", "cognitif", "sensoriel", "dependance", "santé"],
    "60_plus": [ind_fonctionnel["60_plus"], ind_cognitif["60_plus"], ind_sensoriel["60_plus"], ind_dependance["60_plus"], ind_santé["60_plus"]],
    "60_74": [ind_fonctionnel["60_74"], ind_cognitif["60_74"], ind_sensoriel["60_74"], ind_dependance["60_74"], ind_santé["60_74"]],
    "75_plus": [ind_fonctionnel["75_plus"], ind_cognitif["75_plus"], ind_sensoriel["75_plus"], ind_dependance["75_plus"], ind_santé["75_plus"]],
})

#Préparation des données
df_stack = df_indicateurs.copy()

rename_map = {
    "cognitif": "Limitations cognitives",
    "fonctionnel": "Problèmes de mobilité",
    "sensoriel": "Déficiences sensorielles",
    "dependance": "Dépendance \n(aide / équipements)",
    "santé": "Maladie chronique\n ou durable"
}
df_stack["indicateur"] = df_stack["indicateur"].replace(rename_map)
df_stack = df_stack.sort_values("75_plus", ascending=True).reset_index(drop=True)

df_stack["base_60"] = df_stack["60_74"]
df_stack["delta"] = df_stack["75_plus"] - df_stack["60_74"]
df_stack["delta"] = df_stack["delta"].clip(lower=0)


plt.figure(figsize=(12, 7))
sns.set_style("whitegrid")

plt.barh(df_stack["indicateur"], df_stack["base_60"], color=COLOR_LIGHT_BLUE, label="60 à 74 ans")
plt.barh(df_stack["indicateur"], df_stack["delta"], left=df_stack["base_60"],
         color=COLOR_BLUE, label="Progression jusqu'à 75 ans et plus")


for i, row in df_stack.iterrows():
    # Label pour 60-74 ans
    plt.text(row["base_60"] / 2,
             i,
             f"{row['base_60'] * 100:.1f}%",
             ha="center",
             va="center",
             fontsize=XLABEL_FONT_SIZE)

    # Label pour le delta
    if row["delta"] > 0.001:
        plt.text(row["base_60"] + row["delta"] / 2,
                 i,
                 f"+{row['delta'] * 100:.1f}%",
                 ha="center",
                 va="center",
                 fontsize=XLABEL_FONT_SIZE,
                 color="white")

    # Label final atteint chez les 75+
    plt.text(row["base_60"] + row["delta"] + 0.01,
             i,
             f"{row['75_plus'] * 100:.1f}%",
             ha="left",
             va="center",
             fontsize=XLABEL_FONT_SIZE,
             color="black")

ax = plt.gca()
ticks = ax.get_xticks()
ax.set_xticks(ticks)
ax.set_xticklabels([f"{t * 100:.0f}%" for t in ticks], fontsize=LEGEND_FONT_SIZE)
ax.tick_params(axis='y', labelsize=LEGEND_FONT_SIZE)

plt.title("Prévalence des limitations chez les seniors\n et évolution de ces limitations entre 60-74 ans et après 75 ans",
          fontsize=TITLE_FONT_SIZE, weight=TITLE_WEIGHT, loc=TITLE_LOC, pad=15)
plt.xlabel("Proportion des seniors concernés", fontsize=XLABEL_FONT_SIZE)
plt.legend(fontsize=LEGEND_FONT_SIZE, frameon=LEGEND_FRAMEON, loc=LEGEND_LOC)

plt.tight_layout()
plt.savefig("./figures/figure1c.png", dpi=FIGURE_DPI, bbox_inches="tight")
plt.show()
