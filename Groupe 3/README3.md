
 6 Auteurs  actifs pour ce travail **d'équipe**, dans le but d'**insérer cette fonctionnalité dans le bot discord**: 
 
**Grégoire Fuchs

Eelai

Vasile

Laurentiu

Sayqin**

## 📌 Sommaire

- [Partie 1 : Webscrapping des offres d'alternance](#partie-1--webscraping--des-offres-dalternance)
  - [But](#but)
  - [Prérequis](#prérequis)
  - [Exécution du script](#exécution-du-script)
  - [Limites](#limites)
- [Partie 2 : Webscrapping des offres de stage](#partie-2--webscraping-des-offres-de-stage)
  - [Introduction](#introduction)
  - [1. Webscraping des stages sur Indeed](#1-webscraping-des-stages-sur-indeed)
  - [2. Webscraping via Google Jobs](#2-webscraping-des-stages-via-google-jobs)
  - [3. Optimisation et perspectives](#3-optimisation-et-perspectives)

# Partie 1 : Webscraping  des offres d'alternance 

## But
Ce script permet de collecter, nettoyer, analyser et sauvegarder des offres d'emploi en **alternance** dans le domaine de la Data Science (et métiers connexes), publiées sur Indeed France à l’aide de la bibliothèque python-jobspy.

## Prérequis
Avant d'exécuter le script, assurez-vous d'avoir Python installé (par exemple 3.12.4) et d'installer les dépendances nécessaires.

1. Installer **python-jobspy**
   Pour installer le package `python-jobspy`, utilisez la commande suivante dans votre terminal :
   (%ou ! ) pip install python-jobspy

   2. Autres utilispendances (installées automatiquement avec pip dans un environnement propre)
**pandas**, **datetime**, **logging**, **re**, **json**, **csv**, **sys**

## Exécution du script 

Le script effectuera les actions suivantes :

🔍 Scraping des offres d’emploi sur Indeed.fr avec les mots-clés :
"alternance" ET ("data scientist", "data science", "data analyst", "data analyse", "quantitative", "statisticien")

🧹Nettoyage des données : suppression des doublons, nettoyage du texte, mise en forme des champs (dates, salaires, type de contrat...).

 Analyse simple :

-Entreprises les plus présentes
-Localisations les plus fréquentes
-Types de contrat
-Plage de dates de publication

 Formats de sauvegarde :

- **CSV** : fichier tabulaire classique (`.csv`)  
- **JSON** : fichier structuré pour usage API ou traitement (`.json`)  
- **Python** : fichier `.py` contenant une variable `job_data = [...]` avec les données sous forme de dictionnaires


## Limites
Les données sur l’alternance concernent uniquement la France, mais pour les stages, nous avons élargi le périmètre à l'international. En effet, pour des raisons juridiques et financières, les contrats d'alternance ne sont pas éligibles à un financement hors de France.
En revanche, cela reste envisageable pour les stages, qui ne sont pas soumis aux mêmes contraintes.

Nos sources sont donc basées sur le Github de python-job, que nous remercions énormément ! 

# Partie 2 : Webscraping des offres de stage

## Introduction

Afin d’augmenter le volume et la diversité des offres d’emploi collectées, il a paru évident d’ouvrir le champ de recherche **aux stages**. Cela permet de collecter davantage d’offres, de s’adresser à un public plus varié (étudiants, jeunes diplômés) et d’analyser les tendances du marché à différents niveaux d’expérience.
Les mots-clés utilisés sont "data" ainsi que les différentes traductions de "stage" selon le pays ciblé.
Auteur: Grégoire Fuchs


## 1. Webscraping des stages sur Indeed

La première étape consiste à utiliser le package [`jobspy`](https://github.com/cullenwatson/JobSpy) pour scraper les offres de stage sur Indeed.  
Le mot-clé utilisé est **"stage"** ou sa traduction selon la langue et le pays ciblé :

- **France** : `stage` 
- **UK/USA** : `trainee`
- **Allemagne** : `praktikum`

Pour chaque recherche, un filtrage géographique est appliqué :
- **France** : les deux dernières recherches ciblent spécifiquement la France
- **UK** : ciblage sur le Royaume-Uni
- **USA** : ciblage sur les États-Unis
- **Allemagne** : ciblage sur l’Allemagne

L’objectif est d’obtenir un maximum d’offres pertinentes pour chaque zone géographique, en adaptant le mot-clé à la langue locale.

---

## 2. Webscraping des stages via Google Jobs

Dans un second temps, le même package `jobspy` est utilisé pour interroger **Google Jobs**.  
Google Jobs agrège des offres provenant de multiples plateformes, ce qui permet d’optimiser la couverture et la diversité des résultats.

La démarche reste similaire :
- Utilisation des mots-clés adaptés à chaque pays (`trainee`, `praktikum`, `stage`, etc.)
- Filtrage par pays (France, UK, USA, Allemagne)

Cela permet de croiser les résultats d’Indeed avec ceux de Google Jobs, pour maximiser les chances de trouver des offres variées et récentes.

---

## 3. Optimisation et perspectives

- **Optimisation** :  
  Les recherches sont pensées pour maximiser la pertinence (mot-clé adapté, filtrage géographique) et la diversité des sources.
- **Fusion des résultats** :  
  À ce stade, les résultats de chaque recherche (Indeed, Google Jobs) sont conservés séparément.  
  Une amélioration possible serait de fusionner les résultats par langue ou par pays, afin de faciliter l’analyse comparative et d’éviter les doublons.
- **Scalabilité** :  
  Le package `jobspy` permet d’étendre facilement la collecte à d’autres plateformes (Glassdoor, LinkedIn, etc.) ou à d’autres mots-clés.
  **Perspectives**:
  Intégration possible de nouvelles plateformes comme LinkedIn ou Glassdoor
  Ajout d’une interface web pour visualiser les offres
  Export direct des données vers Google Sheets ou Notion

