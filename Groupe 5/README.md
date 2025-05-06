## Groupe 5 – Utilisation des LLMs pour l’analyse de CV et la génération de lettres de motivation 

## Objectif : Ce projet explore l’utilisation de Large Language Models (LLMs)  – Gemini – pour : 
* Comparer un CV avec une fiche de poste afin de vérifier la pertinence de la candidature.
* Générer automatiquement une lettre de motivation personnalisée en s’appuyant sur le CV, la fiche de poste et d’éventuelles informations complémentaires fournies par l’utilisateur.
  L’objectif est de proposer un bot capable de livrer un retour rapide et personnalisé.

## 📁 Étapes de fonctionnement :
   1. Analyse de pertinence :Après réception du CV (via le bot Discord, traité par le groupe 4) et de l’offre d’emploi (scrapée par les groupes 2 & 3), un premier traitement est effectué pour nettoyer et structurer les textes. Un prompt court et ciblé est ensuite envoyé à Gemini afin d’évaluer la compatibilité entre les deux documents.
Si ≥ 70 % des exigences de l’offre sont couvertes par le CV, la réponse est “oui”.
Dans le cas contraire, le processus s’arrête ou propose des pistes d’amélioration au candidat (ex. : formations à envisager, formulation à retravailler dans le CV).

   2. Rédaction de la lettre : Lorsque le CV est jugé pertinent, un prompt plus complexe est généré pour demander à Gemini de rédiger une lettre de motivation sur mesure, professionnelle, claire et engageante (environ 350 mots).
Le texte est ensuite traité automatiquement via un script Python qui vérifie la qualité linguistique, la longueur, et corrige d’éventuelles fautes d’orthographe.
   
   3. Enrichir le prompt : Afin d’enrichir le contenu et d’assurer une vraie personnalisation, l’utilisateur est invité à répondre à quelques questions complémentaires via Discord (ex. : disponibilités, aspirations, réalisations marquantes, préférences géographiques). Ces éléments sont automatiquement intégrés dans le prompt transmis au LLM, ce qui renforce la cohérence du discours.
  
   4. Une fois la lettre de motivation validée, elle est automatiquement mise en page à l’aide de la bibliothèque python-docx. L’objectif est de produire un document Word directement exploitable, conforme aux standards de présentation professionnels.

Le fichier final respecte les éléments suivants :

  Police : Calibri, taille 11 pt

  Format : A4, avec marges classiques

  En-tête : coordonnées complètes du candidat (nom, adresse, contact)

  Nom du fichier : Lettre_{Nom}_{Date}.docx

Ce fichier est enregistré localement, prêt à être transmis à un recruteur.

## ⚙️ Prérequis :
Python ≥ 3.10 
Clé API Google Gemini 

```python 
# imports Python : 

prompts.py
import requests

main.py
import requests
from docx import Document
```

## Auteurs :

Aymane AIBICHI,
Zineb MANAR,
Ali BOUGUERRA,
Nawel ARIF,
Nhung Nguyen.
