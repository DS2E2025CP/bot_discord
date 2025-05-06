# 🤖 JobHunterAI
## Bot Discord d'aide à la recherche d'emploi et d'alternance
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

<div align="center">
  <p><em>Projet académique — Master 1 DS2E — Faculté des sciences économiques et de gestion de Strasbourg</em></p>
  
  <img src="https://github.com/DS2E2025CP/bot_discord/raw/main/assets/images/fseg_logo.png" alt="Logo FSEG" width="400"/>
</div>

## 📋 Table des matières

- [Présentation du projet](#-présentation-du-projet)
- [Fonctionnalités principales](#-fonctionnalités-principales)
- [Architecture du projet](#-architecture-du-projet)
- [Installation et configuration](#-installation-et-configuration)
- [Guide d'utilisation](#-guide-dutilisation)
  - [Rechercher des offres d'emploi (`/scrape`)](#rechercher-des-offres-demploi-chercher_emploi)
  - [Rechercher des stages (`/scrape_stage`)](#rechercher-des-stages-scrape_stage)
  - [Télécharger et analyser un CV (`/telecharger_cv`)](#télécharger-et-analyser-un-cv-telecharger_cv)
  - [Analyser la compatibilité CV/offre (`/analyser_cv_offre`)](#analyser-la-compatibilité-cvoffre-analyser_cv_offre)
  - [Ajouter des informations pour la lettre (`/infos_lettre_g5`)](#ajouter-des-informations-pour-la-lettre-infos_lettre_g5)
  - [Générer une lettre de motivation (`/generer_lettre_g5`)](#générer-une-lettre-de-motivation-generer_lettre)
- [Choix techniques et bonnes pratiques](#-choix-techniques-et-bonnes-pratiques)
- [Équipe et contributions](#-équipe-et-contributions)
- [Perspectives d'évolution](#-perspectives-dévolution)
- [Licence](#-licence)

## 🚀 Présentation du projet

JobHunterAI est un bot Discord académique développé dans le cadre du Master 1 DS2E (Data science pour l'économie et l'entreprise du futur) à la Faculté des sciences économiques et de gestion de Strasbourg. Ce projet innovant vise à faciliter le processus de recherche d'emploi et d'alternance pour les étudiants en automatisant plusieurs étapes clés:

- Recherche d'offres pertinentes en ligne depuis multiples sources (France Travail, Indeed)
- Analyse de CV au format PDF
- Évaluation de l'adéquation entre profil et offre d'emploi
- Génération de lettres de motivation personnalisées

L'intégration dans Discord permet une accessibilité immédiate et une utilisation intuitive, sans nécessiter d'installation supplémentaire pour les utilisateurs.

## 🔍 Fonctionnalités principales

### 1️⃣ Recherche d'offres d'emploi et d'alternance
Grâce aux commandes `/scrape` et `/scrape_stage`, le bot interroge différentes sources en ligne pour trouver des offres correspondant aux critères spécifiés:
- Métier ou titre de poste recherché
- Localisation géographique
- Type de contrat (CDI, alternance, stage)

Les résultats sont présentés directement dans Discord avec toutes les informations essentielles: titre du poste, entreprise, lieu et lien vers l'annonce complète. Le bot combine les résultats de France Travail et d'Indeed pour une couverture optimale du marché.

### 2️⃣ Analyse automatique de CV (PDF)
La commande `/telecharger_cv` suivie de l'utilisation des commandes d'extraction (`/extraire_cv_mistral`, `/extraire_cv_gemini`) permet de soumettre un CV au format PDF pour analyse. Le bot:
- Extrait le contenu textuel du document
- Identifie automatiquement les sections clés (formation, expériences, compétences)
- Organise les informations dans une structure cohérente
- Produit un résumé clair et structuré du profil professionnel

Cette fonctionnalité s'appuie sur des technologies avancées d'extraction de texte et d'analyse sémantique grâce à des modèles de langage (Mistral, Gemini).

### 3️⃣ Matching CV ↔ Offre d'emploi
Via les commandes `/comparer_cv_offre` ou `/analyser_cv_offre`, l'utilisateur peut évaluer l'adéquation entre son profil et une offre sélectionnée. L'analyse fournit:
- Un pourcentage de correspondance global
- Les points forts de la candidature
- Les compétences ou expériences manquantes
- Des recommandations personnalisées pour optimiser les chances de succès

Cette évaluation aide à prioriser les candidatures et à identifier les points à renforcer dans le CV ou à mettre en avant lors d'un entretien.

### 4️⃣ Génération de lettre de motivation personnalisée
Les commandes `/generer_lettre` et `/generer_lettre_g5` produisent automatiquement une lettre de motivation adaptée au profil du candidat et à l'offre visée. La commande `/infos_lettre_g5` permet d'ajouter des informations supplémentaires pour personnaliser davantage la lettre. Celle-ci:
- Mentionne explicitement l'entreprise et le poste
- Met en avant les compétences pertinentes du candidat
- Établit des liens entre le parcours et les besoins de l'entreprise
- Respecte les conventions formelles d'une lettre professionnelle

Le document généré est immédiatement téléchargeable et peut servir de base solide pour une candidature, nécessitant seulement quelques ajustements personnels avant envoi.

## 🏗️ Architecture du projet

Le projet est structuré en cinq modules principaux, chacun développé par un groupe d'étudiants distinct, puis intégrés en une solution cohérente:

### 🔸 Groupe 1 — Intégration Discord & Interface
**Fichiers principaux**: `bot.py`, `scrape_jobs.py`,`scrape_stages.py`, `extract_cv.py`, `parse_cv_commands.py`, `mistral_utils.py`, `gemini_utils.py`, `partieLLM_discord.py`

Ce module central assure:
- L'initialisation du bot Discord via la bibliothèque `discord.py`
- La gestion des permissions et l'enregistrement des commandes slash
- La coordination des différents composants du système
- L'interface utilisateur et l'expérience globale
- La gestion des données temporaires entre les commandes

Le groupe 1 a joué un rôle d'orchestrateur, veillant à l'harmonie entre les différentes fonctionnalités et à la fluidité des interactions.

### 🔸 Groupe 2 — Scraping d'offres (France Travail)
**Fichiers principaux**: `scraping_group2.py`

Ce module spécialisé dans la collecte d'offres d'emploi sur France Travail:
- Formule des requêtes de recherche paramétrées selon les critères utilisateur
- Exploite l'API officielle de France Travail avec authentification
- Extrait les informations pertinentes de chaque annonce (titre, entreprise, lieu)
- Gère la pagination et le volume de résultats
- Nettoie et standardise les données avant affichage

L'intégration avec le module principal transforme ces données brutes en affichage interactif dans Discord.

### 🔸 Groupe 3 — Scraping d'offres (Indeed)
**Fichiers principaux**: `Code_g3.py`, `Code Webscrapping de stages.ipynb`, `scrape_jobs_g3.py`, `scrape_stages.py`

Complémentaire au groupe 2, ce module:
- Collecte des offres sur Indeed.fr, particulièrement pour les alternances et stages
- Utilise la bibliothèque `python-jobspy` pour optimiser les requêtes
- Permet des recherches spécifiques pour les stages via la commande `/scrape_stage`
- Fournit des résultats avec URLs fonctionnelles vers les offres originales

Cette diversification des sources enrichit la pertinence des résultats proposés aux utilisateurs.

### 🔸 Groupe 4 — Parsing de CV PDF
**Fichiers principaux**: `extract_cv.py`, `parse_cv_commands.py`, `CV_Parser_Mistral_Discord.py`, `Gemini_CV_parser.py` 

Ce composant sophistiqué prend en charge l'analyse des CV:
- Extraction du texte brut depuis les fichiers PDF
- Analyse sémantique via Large Language Models (Mistral AI ou Google Gemini)
- Identification structurée des informations clés (compétences, expériences, formation)
- Production d'un format normalisé (fichier json) représentant le profil professionnel

L'approche par IA garantit une flexibilité face à la diversité des formats de CV tout en maintenant une qualité d'extraction élevée.

### 🔸 Groupe 5 — Matching CV ↔ Offre & Génération de lettre
**Fichiers principaux**: `partieLLM.py`, `partieLLM_discord.py`, `match_cv_offer.py`, `generate_cover_letter.py`

Ce dernier module exploite les technologies LLM pour deux tâches critiques:
1. **Évaluation d'adéquation**: analyse comparative entre le CV et l'offre
   - Calcul d'un score de correspondance
   - Identification des points forts et lacunes
   - Recommandations personnalisées
2. **Génération de lettre**: rédaction automatique d'une lettre de motivation
   - Adaptation au profil et à l'offre spécifique
   - Intégration d'informations supplémentaires fournies par l'utilisateur
   - Structure professionnelle et ton approprié

Le module utilise des prompts sophistiqués pour obtenir des résultats de haute qualité via l'API Google Gemini.

Cette architecture modulaire favorise la maintenance, l'évolutivité et la collaboration entre équipes de développement.

## 💻 Installation et configuration

### Prérequis
- Python 3.10 ou supérieur
- Un compte Discord
- Clés API pour France Travail, Mistral et Google Generative AI (Gemini)

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
# DISCORD
DISCORD_TOKEN=votre_token_discord

# FRANCE TRAVAIL
FT_CLIENT_ID=votre_ft_client_id
FT_CLIENT_SECRET=votre_ft_client_secret

#GEMINI ET MISTRAL 
GEMINI_API_KEY=votre_clé_google_generative_ai
MISTRAL_API_KEY=votre_clé_mistral

```

#### 5. Configurer France Travail API (Groupe 2)
1. Créez un compte sur [France Travail I/O](https://francetravail.io/)
2. Créez une application pour obtenir un Client ID et un Client Secret
3. Remplacez les identifiants dans `scraping_group2.py`

#### 6. Configurer l'application Discord

1. Rendez-vous sur le [Portail Développeurs Discord](https://discord.com/developers/applications)
2. Créez une nouvelle application (ex: "JobHunterAI")
3. Dans l'onglet "Bot", créez un bot et copiez son token
4. Activez les intents "Server Members" et "Message Content" dans les paramètres du bot
5. Dans OAuth2 > URL Generator:
   - Cochez les scopes "bot" et "applications.commands"
   - Sélectionnez les permissions appropriées (Admin recommandé pour les tests)
   - Utilisez l'URL générée pour inviter le bot sur votre serveur de test

#### 7. Lancer le bot
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

**Exemple**: `/scrape data analyst lieu:Lyon`

**Résultat**: Le bot affiche une liste d'offres correspondantes combinant France Travail et Indeed avec:
- Titre du poste
- Nom de l'entreprise
- Localisation
- Lien vers l'offre complète

Un menu déroulant permet de sélectionner l'offre qui vous intéresse pour les étapes suivantes.

### Rechercher des stages (`/scrape_stage`)

Cette commande est spécifiquement conçue pour rechercher des offres de stage.

**Syntaxe**: `/scrape_stage [lieu]`

**Paramètres**:
- `lieu` (optionnel): Localisation souhaitée (ville, région), Paris par défaut

**Exemple**: `/scrape_stage lyon`

**Résultat**: Le bot affiche une liste de stages disponibles dans la localisation spécifiée, avec des informations similaires aux recherches d'emploi.

### Télécharger et analyser un CV (`/telecharger_cv`)

Cette commande permet de télécharger et d'analyser votre CV.

**Syntaxe**: `/telecharger_cv`

**Procédure**:
1. Exécutez la commande
2. Le bot vous invite à téléverser un fichier
3. Uploadez votre CV au format PDF. Vous pouvez utilisez `parse_cv_mistral`ou `parse_cv_gemini` pour obtenir votre CV en format json
4. Le CV est stocké temporairement
5. Utilisez `/extraire_cv_mistral` ou `/extraire_cv_gemini` pour l'analyse

**Résultat**: Le bot affiche un résumé structuré de votre CV avec:
- Informations personnelles (nom, contact)
- Compétences techniques identifiées
- Expériences professionnelles
- Formation et diplômes
- Langues et certifications

Ces informations sont stockées pour les commandes suivantes.


### Analyser la compatibilité CV/offre (`/analyser_cv_offre`)

Cette commande évalue l'adéquation entre votre profil et une offre d'emploi sélectionnée. Elle utilise des modèles de langage pour une analyse détaillée.

**Syntaxe**: `/analyser_cv_offre`

**Prérequis**:
- Avoir téléchargé et analysé votre CV
- Avoir sélectionné une offre d'emploi

**Résultat**: Le bot affiche:
- Un pourcentage de correspondance global
- Les points forts de votre candidature (✅)
- Les compétences ou expériences manquantes (⚠️)
- Des conseils personnalisés pour améliorer votre candidature (💡)

Cette analyse vous aide à décider si l'offre correspond à votre profil et comment adapter votre candidature pour maximiser vos chances.

### Ajouter des informations pour la lettre (`/infos_lettre_g5`)

Cette commande vous permet d'ajouter des informations supplémentaires pour personnaliser votre lettre de motivation.

**Syntaxe**: `/infos_lettre_g5`

**Informations demandées**:
- Pourquoi cette entreprise vous intéresse
- Vos disponibilités
- Autres informations personnelles pertinentes

**Résultat**: Ces informations sont stockées et utilisées pour enrichir la lettre de motivation générée.

### Générer une lettre de motivation (`/generer_lettre`)

Cette commande produit une lettre de motivation personnalisée pour l'offre sélectionnée.

**Syntaxe**: `/generer_lettre` ou `/generer_lettre_g5` (version améliorée du Groupe 5)

**Prérequis**:
- Avoir téléchargé et analysé votre CV
- Avoir sélectionné une offre d'emploi
- (Optionnel) Avoir fourni des informations supplémentaires via `/infos_lettre_g5`

**Résultat**: Le bot génère:
- Un fichier texte contenant la lettre de motivation complète
- Un aperçu de la lettre dans le chat Discord

La lettre générée respecte les conventions professionnelles:
- En-tête avec vos coordonnées
- Objet mentionnant le poste et l'entreprise
- Corps de texte personnalisé (environ 350 mots)
- Formule de politesse adaptée

Il vous suffit de télécharger le fichier, d'y apporter vos dernières touches personnelles et de l'inclure dans votre candidature.


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
- **Structure de données centralisée**: Classe `UserData` pour stocker les informations utilisateur
- **Sécurité des informations**: CV et analyses visibles uniquement par l'utilisateur concerné
- **Variables d'environnement**: Gestion sécurisée des tokens et clés d'API

### Multi-source pour les offres d'emploi
- **France Travail API**: Utilisation de l'API officielle avec authentification
- **Indeed via jobspy**: Scraping optimisé avec gestion des erreurs
- **Combinaison des résultats**: Présentation unifiée des offres de différentes sources
- **Filtrage intelligent**: Recherche par mots-clés et localisation

### Intégration de l'IA
- **Google Gemini**: Utilisation de l'API Gemini pour l'analyse et la génération de contenu
- **Prompts optimisés**: Instructions précises pour obtenir des résultats structurés
- **Extraction intelligente**: Identification des informations clés indépendamment du format
- **Génération de contenu**: Production de textes cohérents et personnalisés

### Robustesse et expérience utilisateur
- **Gestion des erreurs**: Messages clairs en cas de problème ou d'étape manquante
- **Logging détaillé**: Enregistrement des actions et erreurs pour faciliter le débogage
- **Guide utilisateur**: Instructions et suggestions pour une utilisation optimale
- **Documentation complète**: Description détaillée des commandes et fonctionnalités

## 👥 Équipe et contributions

Ce projet a été réalisé par les étudiants du Master 1 DS2E de la Faculté des sciences économiques et de gestion de Strasbourg, organisés en cinq groupes de travail:

### Groupe 1: Intégration Discord & Interface utilisateur
- Développement du bot principal et coordination
- Intégration des différents modules
- Interface utilisateur et expérience globale

### Groupe 2: Scraping d'offres sur France Travail
- Développement de l'API France Travail
- Gestion des requêtes et authentification
- Extraction et formatage des offres d'emploi

### Groupe 3: Scraping d'offres sur Indeed
- Développement du scraping Indeed
- Recherche d'offres d'emploi et de stages
- Extraction des URLs et informations pertinentes

### Groupe 4: Analyse de CV PDF
- Extraction du texte des PDF
- Analyse structurée des informations
- Formatage des données pour l'utilisation par le bot

### Groupe 5: Matching CV-Offre & Génération de lettre
- Analyse de compatibilité entre CV et offres
- Génération de lettres de motivation personnalisées
- Intégration avec Google Gemini API

Nous remercions particulièrement les encadrants du projet pour leur soutien et leurs conseils tout au long du développement.

## 🔮 Perspectives d'évolution

Le projet JobHunterAI pourrait être enrichi par les fonctionnalités suivantes:

- **Multilinguisme**: Prise en charge de CV et génération de lettres en plusieurs langues
- **Système de profils persistants**: Sauvegarde des CV et préférences utilisateurs
- **Dashboard statistique**: Visualisation des tendances du marché de l'emploi
- **Assistant de préparation d'entretien**: Questions probables basées sur l'offre
- **Intégration d'APIs officielles supplémentaires**: Connexion à davantage de plateformes d'emploi
- **Suivi de candidatures**: Gestion du statut des postulations envoyées
- **Recommandations de formation**: Suggestions pour combler les lacunes identifiées

Ces améliorations pourraient faire l'objet de travaux futurs dans le cadre universitaire ou d'un développement open-source.

## 📄 Licence

Ce projet est distribué sous licence MIT. Il a été développé dans un cadre académique et peut être librement utilisé, modifié et partagé à des fins non commerciales, sous réserve de mentionner la source originale.

---

<div align="center">
  <p>
    <strong>JobHunterAI</strong> — Développé par les étudiants du Master 1 DS2E<br>
    Faculté des sciences économiques et de gestion de Strasbourg — 2024-2025
  </p>
</div>
