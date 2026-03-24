# Santé mentale et grand âge

## Contexte du Projet

Ce projet s'inscrit dans le cadre de l'**OpenData University** et du **projet ADAD** (Analyse de Données et Aide à la Décision) de troisième année à l'école Centrale Méditerranée. Il vise à explorer et analyser les données relatives à la santé mentale des personnes âgées en France, en exploitant des sources de données ouvertes et accessibles.

### À propos de l'OpenData University
OpenData University est une initiative qui favorise l'utilisation des données ouvertes pour l'enseignement, la recherche et l'innovation. Elle encourage les étudiants et les chercheurs à travailler avec des données publiques pour développer des compétences en analyse de données et en science des données.

### À propos des étudiants
Ce projet est réalisé par 4 étudiants de 2 options différentes : Naïs Atlan et Florian Mourey de l'option d'informatique, Célestine Adam et Timothée Huang de l'option de données et finances.

## Objectifs

Les objectifs de ce projet sont :

- **Analyser les données** relatives à la santé mentale des personnes âgées
- **Identifier les tendances** dans les données
- **Créer des visualisations** intuitives pour comprendre ces données.

## Documentation Complète

Pour plus de détails sur ce projet, sa méthodologie, les données utilisées et les résultats, consultez notre rapport complet :

**[Rapport Notion - Santé mentale et grand âge](https://jungle-brain-583.notion.site/Sant-mentale-et-grand-ge-30a97e2d9a5480d7a9c7ea165624ee6f)**

## Structure du Projet

```
Sante_mentale_et_grand_age/
├── code/                          # Scripts d'analyse et de visualisation
│   ├── figure1a.py, figure1b.py   # Figures section 1
│   ├── figure2a.py, figure2b.py   # Figures section 2
│   └── ...                         # Autres figures
├── datasets/                       # Données en entrée
│   ├── APL.csv
│   ├── effectifs.csv
│   └── gestes_autoinfliges.csv
├── figures/                        # Figures générées
├── charte_graphique.py            # Configuration des styles graphiques
├── requirements.txt               # Dépendances Python
├── README.md                       # Ce fichier
└── .venv/                         # Environnement virtuel (local)
```

## Installation et Configuration

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
   ```bash
   git clone https://github.com/naisatlan/Sante_mentale_et_grand_age.git
   cd Sante_mentale_et_grand_age
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   ```

3. **Activer l'environnement virtuel**

   **Sous Windows (PowerShell):**
   ```bash
   .\.venv\Scripts\Activate.ps1
   ```

   **Sous macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## Dépendances

Le projet utilise les bibliothèques Python suivantes :

- **numpy** : Calculs numériques
- **pandas** : Manipulation et analyse de données
- **matplotlib** : Création de visualisations
- **seaborn** : Visualisations statistiques avancées
- **geopandas** : Analyse de données géographiques
- **scikit-learn** : Machine learning et analyse statistique
- **statsmodels** : Modèles statistiques
- **openpyxl** : Manipulation de fichiers Excel
- **odfpy** : Support des formats ODF
- **requests** : Requêtes HTTP
- **zipfile36** : Manipulation de fichiers ZIP

## Exécution des Scripts

Après avoir activé votre environnement virtuel et installé les dépendances :

**Lancer un script spécifique**
   ```bash
   cd code
   python figure1a.py
   ```

Les figures générées seront sauvegardées dans le dossier `figures/`.

**Dernière mise à jour** : Mars 2026
