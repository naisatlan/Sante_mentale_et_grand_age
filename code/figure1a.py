# Gestes autoinfligés chez les seniors

# Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from charte_graphique import (
    TITLE_FONT_SIZE, TITLE_WEIGHT, TITLE_LOC,
    XLABEL_FONT_SIZE, YLABEL_FONT_SIZE, LEGEND_FONT_SIZE, LEGEND_LOC, LEGEND_FRAMEON,
    FIGURE_DPI, 
    COLOR_BLUE, COLOR_RED, 
    TICK_FONT_SIZE,
    SOURCE_FONT_SIZE, SOURCE_STYLE, SOURCE_HA
)


# Chargement des données INSEE avec colonnes clés : 0=Année, 6=65-74 ans, 7=75+ ans
df_pop = pd.read_excel('./datasets/population_age.xlsx', header=None, skiprows=4)
df_pop = df_pop[[0, 6, 7]].copy()
df_pop.columns = ['annee', 'pop_65_74', 'pop_75_plus']

# Conversion numérique
for col in df_pop.columns:
    df_pop[col] = pd.to_numeric(df_pop[col], errors='coerce')

# Calcul Population Senior Totale (65+)
df_pop['pop_seniors'] = df_pop['pop_65_74'] + df_pop['pop_75_plus']
df_pop = df_pop[(df_pop['annee'] >= 2012)].copy()

# Le fichier fichier s'arrête en 2022. On ajoute les estimations officielles INSEE pour prolonger l'analyse.
# Source : INSEE Bilan démographique & Projections 2025
new_rows = pd.DataFrame([
    {'annee': 2023, 'pop_seniors': 14445992}, # Estimation interpolée INSEE
    {'annee': 2024, 'pop_seniors': 14684997}  # Estimation interpolée INSEE
])
df_pop = pd.concat([df_pop, new_rows], ignore_index=True)

#Chargement des données d'hospitalisations pour les gestes autoinfligés
df_hosp = pd.read_csv('./datasets/gestes_autoinfliges.csv', sep=';')

# Nettoyage selon l'âge
def clean_age(x):
    x = str(x).strip()
    if x.isdigit(): return int(x)
    if '+' in x: return int(x.replace('+', ''))
    return np.nan
df_hosp['age_num'] = df_hosp['age'].apply(clean_age)
df_hosp = df_hosp.dropna(subset=['age_num'])

# Filtres : MCO + SEJOURS (car on parle "d'hospitalisations") + SENIORS
df_seniors = df_hosp[(df_hosp['champ'] == 'mco') &
                     (df_hosp['unite'] == 'sejours') &
                     (df_hosp['age_num'] >= 65)].copy()

# Agrégation par année
df_hosp_agg = df_seniors.groupby('annee')['nombre'].sum().reset_index()
df_hosp_agg.columns = ['annee', 'nb_hospitalisations']

#Fusion 
df_viz = pd.merge(df_hosp_agg, df_pop, on='annee', how='inner')

# Calcul Base 100 en 2012 pour comparer les rythmes de croissance
base_pop = df_viz.loc[df_viz['annee'] == 2012, 'pop_seniors'].values[0]
base_hosp = df_viz.loc[df_viz['annee'] == 2012, 'nb_hospitalisations'].values[0]

df_viz['index_pop'] = (df_viz['pop_seniors'] / base_pop) * 100
df_viz['index_hosp'] = (df_viz['nb_hospitalisations'] / base_hosp) * 100

#Visualisation
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

sns.lineplot(data=df_viz, x='annee', y='index_pop', color=COLOR_BLUE, linewidth=3,
             label="Population seniors (65+)", linestyle='--')

sns.lineplot(data=df_viz, x='annee', y='index_hosp', color=COLOR_RED, linewidth=3,
             label="Hospitalisations seniors (65+)", linestyle='-')

plt.fill_between(df_viz['annee'], df_viz['index_pop'], df_viz['index_hosp'],
                 where=(df_viz['index_pop'] > df_viz['index_hosp']),
                 color=COLOR_BLUE, alpha=0.2, interpolate=True)

plt.xticks(fontsize=TICK_FONT_SIZE)
plt.yticks(fontsize=TICK_FONT_SIZE)
last_idx_pop = df_viz['index_pop'].iloc[-1]
last_idx_hosp = df_viz['index_hosp'].iloc[-1]
plt.text(2024.2, last_idx_pop, f"Démographie : +{last_idx_pop-100:.0f}%", color=COLOR_BLUE, weight='bold', fontsize = LEGEND_FONT_SIZE)
plt.text(2024.2, last_idx_hosp, f"Hospitalisations : +{last_idx_hosp-100:.0f}%", color= COLOR_RED, weight='bold', fontsize = LEGEND_FONT_SIZE)

plt.title("Evolution des hospitalisations pour gestes autoinfligés chez les seniors\n(Comparaison base 100 en 2012)",
          fontsize=TITLE_FONT_SIZE, weight=TITLE_WEIGHT, loc=TITLE_LOC)
plt.ylabel("Évolution du nombre d'hospitalisations\n (base 100 = 2012)", fontsize = YLABEL_FONT_SIZE)
plt.xlabel("", fontsize = XLABEL_FONT_SIZE)
plt.legend(fontsize = LEGEND_FONT_SIZE, frameon=LEGEND_FRAMEON, loc=LEGEND_LOC)
sns.despine()

plt.figtext(
    0,
    -0.05,
    "Source des données : DREES - Patients hospitalisés pour gestes autoinfligés 2024 – Insee \n INED - Données démographiques 2024",
    ha=SOURCE_HA,
    fontsize=SOURCE_FONT_SIZE,
    style=SOURCE_STYLE
)

plt.tight_layout()
plt.savefig("./figures/figure1a.png", dpi=FIGURE_DPI, bbox_inches="tight")
plt.show()