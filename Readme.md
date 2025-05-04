# 🤖 JobHunterAI

## Bot Discord d'aide à la recherche d'emploi et d'alternance

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)


## 📋 Table des matières

- [Présentation du projet](#-présentation-du-projet)
- [Fonctionnalités principales](#-fonctionnalités-principales)
- [Architecture du projet](#-architecture-du-projet)
- [Installation et configuration](#-installation-et-configuration)
- [Guide d'utilisation](#-guide-dutilisation)
  - [Rechercher des offres d'emploi (`/scrape`)](#rechercher-des-offres-demploi-scrape)
  - [Analyser un CV PDF (`/analyser_cv`)](#analyser-un-cv-pdf-analyser_cv)
  - [Comparer le CV avec une offre (`/comparer_cv_offre`)](#comparer-le-cv-avec-une-offre-comparer_cv_offre)
  - [Générer une lettre de motivation (`/generer_lettre`)](#générer-une-lettre-de-motivation-generer_lettre)
- [Captures d'écran](#-captures-décran)
- [Choix techniques et bonnes pratiques](#-choix-techniques-et-bonnes-pratiques)
- [Équipe et contributions](#-équipe-et-contributions)
- [Perspectives d'évolution](#-perspectives-dévolution)
- [Licence](#-licence)

## 🚀 Présentation du projet

JobHunterAI est un bot Discord académique développé dans le cadre du Master 1 DS2E (Data Science et Environnement Économique) à l'Université de Strasbourg. Ce projet innovant vise à faciliter le processus de recherche d'emploi et d'alternance pour les étudiants en automatisant plusieurs étapes clés:

- Recherche d'offres pertinentes en ligne
- Analyse de CV au format PDF
- Évaluation de l'adéquation entre profil et offre d'emploi
- Génération de lettres de motivation personnalisées

L'intégration dans Discord permet une accessibilité immédiate et une utilisation intuitive, sans nécessiter d'installation supplémentaire pour les utilisateurs.

## 🔍 Fonctionnalités principales

### 1️⃣ Recherche d'offres d'emploi et d'alternance
Grâce à la commande `/scrape`, le bot interroge différentes sources en ligne (principalement France Travail et Indeed) pour trouver des offres correspondant aux critères spécifiés:
- Métier ou titre de poste recherché
- Compétences requises
- Localisation géographique
- Type de contrat (CDI, alternance, etc.)

Les résultats sont présentés directement dans Discord avec toutes les informations essentielles: titre du poste, entreprise, lieu et lien vers l'annonce complète.

### 2️⃣ Analyse automatique de CV (PDF)
La commande `/analyser_cv` permet de soumettre un CV au format PDF pour analyse. Le bot:
- Extrait le contenu textuel du document
- Identifie automatiquement les sections clés (formation, expériences, compétences)
- Organise les informations dans une structure cohérente
- Produit un résumé clair et structuré du profil professionnel

Cette fonctionnalité s'appuie sur des technologies avancées d'extraction de texte (PyPDF2) et d'analyse sémantique (Large Language Models).

### 3️⃣ Matching CV ↔ Offre d'emploi
Via la commande `/comparer_cv_offre`, l'utilisateur peut évaluer l'adéquation entre son profil et une offre sélectionnée. L'analyse fournit:
- Un pourcentage de correspondance global
- Les points forts de la candidature
- Les compétences ou expériences manquantes
- Des recommandations personnalisées pour optimiser les chances de succès

Cette évaluation aide à prioriser les candidatures et à identifier les points à renforcer dans le CV ou à mettre en avant lors d'un entretien.

### 4️⃣ Génération de lettre de motivation personnalisée
La commande `/generer_lettre` produit automatiquement une lettre de motivation adaptée au profil du candidat et à l'offre visée. La lettre:
- Mentionne explicitement l'entreprise et le poste
- Met en avant les compétences pertinentes du candidat
- Établit des liens entre le parcours et les besoins de l'entreprise
- Respecte les conventions formelles d'une lettre professionnelle

Le document généré est immédiatement téléchargeable et peut servir de base solide pour une candidature, nécessitant seulement quelques ajustements personnels avant envoi.

## 🏗️ Architecture du projet

Le projet est structuré en cinq modules principaux, chacun développé par un groupe d'étudiants distinct, puis intégrés en une solution cohérente:

### 🔸 Groupe 1 — Intégration Discord & Interface
**Fichier principal**: `bot.py`

Ce module central assure:
- L'initialisation du bot Discord via la bibliothèque `discord.py`
- La gestion des permissions et l'enregistrement des commandes slash
- La coordination des différents composants du système
- L'interface utilisateur et l'expérience globale
- La gestion des données temporaires entre les commandes

Le groupe 1 a joué un rôle d'orchestrateur, veillant à l'harmonie entre les différentes fonctionnalités et à la fluidité des interactions.

### 🔸 Groupe 2 — Scraping d'offres (France Travail)
**Fichiers**: `scraping_group2.py`, `scrape_jobs.py`

Ce module spécialisé dans la collecte d'offres d'emploi sur France Travail:
- Formule des requêtes de recherche paramétrées selon les critères utilisateur
- Extrait les informations pertinentes de chaque annonce (titre, entreprise, lieu)
- Gère la pagination et le volume de résultats
- Nettoie et standardise les données avant affichage

L'intégration via `scrape_jobs.py` transforme ces données brutes en affichage interactif dans Discord.

### 🔸 Groupe 3 — Scraping d'offres (Indeed)
**Fichier**: `Code_g3.py`

Complémentaire au groupe 2, ce module:
- Collecte des offres sur Indeed.fr, particulièrement pour les alternances
- Utilise la bibliothèque `python-jobspy` pour optimiser les requêtes
- Permet l'analyse statistique des offres (tendances par secteur, localisation)
- Offre la possibilité d'exporter les données en CSV/JSON

Cette diversification des sources enrichit la pertinence des résultats proposés aux utilisateurs.

### 🔸 Groupe 4 — Parsing de CV PDF
**Fichiers**: `CV_Parser_Mistral_Discord.py`, `Gemini_CV_parser.py`, `extract_cv.py`

Ce composant sophistiqué prend en charge l'analyse des CV:
- Extraction du texte brut depuis les fichiers PDF (PyPDF2)
- Analyse sémantique via Large Language Models (Mistral AI ou Google Gemini)
- Identification structurée des informations clés (compétences, expériences, formation)
- Production d'un JSON normalisé représentant le profil professionnel

L'approche par IA garantit une flexibilité face à la diversité des formats de CV tout en maintenant une qualité d'extraction élevée.

### 🔸 Groupe 5 — Matching CV ↔ Offre & Génération de lettre
**Fichiers**: `PartieLLM.py`, `match_cv_offer.py`, `generate_cover_letter.py`

Ce dernier module exploite les technologies LLM pour deux tâches critiques:
1. **Évaluation d'adéquation**: analyse comparative entre le CV et l'offre
   - Calcul d'un score de correspondance
   - Identification des points forts et lacunes
   - Recommandations personnalisées
2. **Génération de lettre**: rédaction automatique d'une lettre de motivation
   - Adaptation au profil et à l'offre spécifique
   - Structure professionnelle et ton approprié
   - Mise en forme exportable

Le module utilise des prompts sophistiqués pour obtenir des résultats de haute qualité via les API de modèles de langage.

Cette architecture modulaire favorise la maintenance, l'évolutivité et la collaboration entre équipes de développement.

## 💻 Installation et configuration

### Prérequis
- Python 3.10 ou supérieur
- Un compte Discord
- (Optionnel) Clés API pour Mistral AI et/ou Google Generative AI

### Étapes d'installation

#### 1. Cloner le dépôt
```bash
git clone https://github.com/universite-strasbourg/JobHunterAI.git
cd JobHunterAI
```

#### 2. Créer et activer un environnement virtuel (recommandé)
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Linux/macOS
source venv/bin/activate
```

#### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

#### 4. Configurer les variables d'environnement
Créez un fichier `.env` à la racine du projet avec les informations suivantes:

```
# Obligatoire
DISCORD_TOKEN=votre_token_discord

# Optionnel (pour fonctionnalités avancées)
MISTRAL_API_KEY=votre_clé_mistral_ai
GOOGLE_API_KEY=votre_clé_google_generative_ai
```

#### 5. Configurer l'application Discord

1. Rendez-vous sur le [Portail Développeurs Discord](https://discord.com/developers/applications)
2. Créez une nouvelle application (ex: "JobHunterAI")
3. Dans l'onglet "Bot", créez un bot et copiez son token
4. Activez l'intention "Message Content" dans les paramètres du bot
5. Dans OAuth2 > URL Generator:
   - Cochez les scopes "bot" et "applications.commands"
   - Sélectionnez les permissions: "Send Messages", "Embed Links", "Attach Files"
   - Utilisez l'URL générée pour inviter le bot sur votre serveur de test

#### 6. Lancer le bot
```bash
python bot.py
```

Si la configuration est correcte, vous devriez voir un message confirmant la connexion du bot et le nombre de commandes enregistrées.

## 📘 Guide d'utilisation

### Rechercher des offres d'emploi (`/scrape`)

Cette commande permet de rechercher des offres d'emploi ou d'alternance correspondant à vos critères.

**Syntaxe**: `/scrape <termes> [lieu]`

**Paramètres**:
- `termes` (obligatoire): Mots-clés décrivant le poste recherché (ex: "data scientist", "développeur python")
- `lieu` (optionnel): Localisation souhaitée (ville, région, département)

**Exemple**: `/scrape data analyst lieu:Paris`

**Résultat**: Le bot affiche une liste d'offres correspondantes avec:
- Titre du poste
- Nom de l'entreprise
- Localisation
- Lien vers l'offre complète

Un menu déroulant permet de sélectionner l'offre qui vous intéresse pour les étapes suivantes.

### Analyser un CV PDF (`/analyser_cv`)

Cette commande permet d'extraire et d'analyser les informations clés de votre CV.

**Syntaxe**: `/analyser_cv`

**Procédure**:
1. Exécutez la commande
2. Le bot vous invite à téléverser un fichier
3. Uploadez votre CV au format PDF
4. Patientez pendant l'analyse (quelques secondes)

**Résultat**: Le bot affiche un résumé structuré de votre CV avec:
- Informations personnelles (nom, contact)
- Compétences techniques identifiées
- Expériences professionnelles
- Formation et diplômes
- Langues et certifications

Ces informations sont stockées temporairement pour les commandes suivantes.

### Comparer le CV avec une offre (`/comparer_cv_offre`)

Cette commande évalue l'adéquation entre votre profil et une offre d'emploi sélectionnée.

**Syntaxe**: `/comparer_cv_offre`

**Prérequis**:
- Avoir sélectionné une offre via `/scrape`
- Avoir analysé votre CV via `/analyser_cv`

**Résultat**: Le bot affiche:
- Un pourcentage de correspondance global
- Les points forts de votre candidature (✅)
- Les compétences ou expériences manquantes (⚠️)
- Des conseils personnalisés pour améliorer votre candidature (💡)

Cette analyse vous aide à décider si l'offre correspond à votre profil et comment adapter votre candidature pour maximiser vos chances.

### Générer une lettre de motivation (`/generer_lettre`)

Cette commande produit une lettre de motivation personnalisée pour l'offre sélectionnée.

**Syntaxe**: `/generer_lettre`

**Prérequis**:
- Avoir sélectionné une offre via `/scrape`
- Avoir analysé votre CV via `/analyser_cv`

**Résultat**: Le bot génère:
- Un fichier texte contenant la lettre de motivation complète
- Un aperçu de la lettre dans le chat Discord

La lettre générée respecte les conventions professionnelles:
- En-tête avec vos coordonnées
- Objet mentionnant le poste et l'entreprise
- Corps de texte personnalisé (environ 350 mots)
- Formule de politesse adaptée

Il vous suffit de télécharger le fichier, d'y apporter vos dernières touches personnelles et de l'inclure dans votre candidature.

## 📸 Captures d'écran

### Recherche d'offres d'emploi
<div align="center">
  <img src="/api/placeholder/700/350" alt="Capture d'écran - Recherche d'offres" />
  <p><em>Résultats de recherche pour "data" avec sélecteur d'offre</em></p>
</div>

### Analyse de CV
<div align="center">
  <img src="/api/placeholder/700/350" alt="Capture d'écran - Analyse de CV" />
  <p><em>Résultat de l'analyse d'un CV au format PDF</em></p>
</div>

### Comparaison CV-Offre
<div align="center">
  <img src="/api/placeholder/700/350" alt="Capture d'écran - Comparaison CV-Offre" />
  <p><em>Évaluation de l'adéquation entre profil et offre (78% de correspondance)</em></p>
</div>

### Génération de lettre de motivation
<div align="center">
  <img src="/api/placeholder/700/350" alt="Capture d'écran - Lettre de motivation" />
  <p><em>Génération d'une lettre de motivation personnalisée</em></p>
</div>

## 🛠️ Choix techniques et bonnes pratiques

### Architecture modulaire
- **Séparation des préoccupations**: Chaque fonctionnalité est isolée dans un module distinct
- **Intégration centralisée**: Le fichier `bot.py` orchestre les différents composants
- **Facilité de maintenance**: Modification d'un module sans impacter les autres
- **Développement parallèle**: Travail simultané par différentes équipes

### Interface Discord moderne
- **Commandes slash** (`/command`): Auto-complétion, descriptions intégrées, paramètres typés
- **Messages enrichis** (Embeds): Formatage avancé, organisation visuelle des informations
- **Composants interactifs**: Menus déroulants, boutons pour une expérience utilisateur fluide
- **Messages éphémères**: Communication privée pour les informations sensibles ou temporaires

### Gestion des données utilisateur
- **Stockage temporaire en mémoire**: Conservation du contexte entre commandes
- **Pas de persistance sensible**: Données effacées à la fermeture du bot
- **Sécurité des informations**: CV et analyses visibles uniquement par l'utilisateur concerné
- **Variables d'environnement**: Gestion sécurisée des tokens et clés d'API

### Intégration de l'IA
- **Modèles de langage avancés**: Mistral AI et Google Gemini pour l'analyse sémantique
- **Prompts optimisés**: Instructions précises pour obtenir des résultats structurés
- **Extraction intelligente**: Identification des informations clés indépendamment du format
- **Génération de contenu**: Production de textes cohérents et personnalisés

### Robustesse et expérience utilisateur
- **Gestion des erreurs**: Messages clairs en cas de problème ou d'étape manquante
- **Retours visuels**: Indicateurs de chargement pendant les opérations longues
- **Guide utilisateur**: Instructions et suggestions pour une utilisation optimale
- **Documentation complète**: Description détaillée des commandes et fonctionnalités

## 👥 Équipe et contributions

Ce projet a été réalisé par les étudiants du Master 1 DS2E de l'Université de Strasbourg, organisés en cinq groupes de travail:

- **Groupe 1**: Intégration Discord & Interface utilisateur
- **Groupe 2**: Scraping d'offres sur France Travail
- **Groupe 3**: Scraping d'offres sur Indeed
- **Groupe 4**: Analyse de CV PDF
- **Groupe 5**: Matching CV-Offre & Génération de lettre


## 🔮 Perspectives d'évolution

Le projet JobHunterAI pourrait être enrichi par les fonctionnalités suivantes:

- **Multilinguisme**: Prise en charge de CV et génération de lettres en plusieurs langues
- **Système de profils persistants**: Sauvegarde des CV et préférences utilisateurs
- **Dashboard statistique**: Visualisation des tendances du marché de l'emploi
- **Assistant de préparation d'entretien**: Questions probables basées sur l'offre
- **Intégration d'APIs officielles**: Connexion directe aux plateformes d'emploi
- **Suivi de candidatures**: Gestion du statut des postulations envoyées
- **Recommandations de formation**: Suggestions pour combler les lacunes identifiées

Ces améliorations pourraient faire l'objet de travaux futurs dans le cadre universitaire ou d'un développement open-source.

## 📄 Licence

Ce projet est distribué sous licence MIT. Il a été développé dans un cadre académique et peut être librement utilisé, modifié et partagé à des fins non commerciales, sous réserve de mentionner la source originale.

---

<div align="center">
  <p>
    <strong>JobHunterAI</strong> — Développé avec 💻 et ☕ par les étudiants du Master 1 DS2E<br>
    Université de Strasbourg — 2024-2025
  </p>
</div>
