# Groupe 1 - Interface Discord & Orchestration
## Projet JobHunterAI

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blueviolet.svg)

<div align="center">
  <p><em>Développement de l'interface Discord et intégration des modules - Master 1 DS2E</em></p>
  <img src="https://raw.githubusercontent.com/DS2E2025CP/bot_discord/main/assets/images/fseg_logo.png" alt="Logo FSEG" width="400"/>
</div>

## 📋 Sommaire

- [Présentation du module](#-présentation-du-module)
- [Architecture technique](#-architecture-technique)
- [Composants développés](#-composants-développés)
- [Commandes implémentées](#-commandes-implémentées)
- [Défis techniques résolus](#-défis-techniques-résolus)
- [Installation et déploiement](#-installation-et-déploiement)
- [Contribution](#-contribution)

## 📋 Présentation du module

Le Groupe 1 était responsable du **développement de l'interface Discord** et de **l'orchestration des différents modules** du bot JobHunterAI. Notre travail a consisté à créer l'architecture centrale du système, à implémenter les commandes slash Discord, et à assurer l'intégration harmonieuse des fonctionnalités développées par les autres groupes.

Notre module est le cœur du système, servant de point d'entrée pour les utilisateurs et de liaison entre les différentes fonctionnalités. Nous avons créé un framework extensible permettant d'ajouter de nouvelles commandes et fonctionnalités de manière modulaire.

## 🏗 Architecture technique

### Structure du code

```
├── bot.py                  # Point d'entrée principal et orchestration
├── extract_cv.py           # Analyse de CV (PDF/DOCX → structure)  
├── scrape_jobs.py          # Interface pour la recherche d'offres
├── scrape_jobs_g3.py       # Intégration Indeed (Groupe 3)
├── scrape_stages.py        # Recherche spécifique de stages
├── mistral_utils.py        # Utilitaires pour l'API Mistral
├── gemini_utils.py         # Utilitaires pour l'API Gemini
├── partieLLM_discord.py    # Interface pour les fonctions Groupe 5
└── utils/
    └── helper.py           # Gestion des données utilisateur et utilitaires
```

### Flux de données

1. **Entrée utilisateur** via commandes slash Discord
2. **Traitement des commandes** dans les modules spécifiques
3. **Stockage temporaire** des données utilisateur (CV, offres sélectionnées)
4. **Orchestration** des appels vers les services externes (APIs)
5. **Retour interactif** via embeds Discord et composants UI

### Technologies utilisées

- **discord.py 2.0+** : Framework Discord complet avec support des commandes slash
- **PyPDF2/docx** : Extraction de texte depuis les documents
- **APIs externes** : Mistral AI, Google Gemini, France Travail
- **Gestion asynchrone** : asyncio pour les opérations non-bloquantes
- **Logging structuré** : Suivi des actions et des erreurs

## 🔧 Composants développés

### Système de gestion des données utilisateur

Nous avons développé une structure de données centralisée (`UserData`) pour stocker et gérer les informations utilisateur entre les différentes commandes :

```python
# Structure simplifiée de la classe UserData
class UserData:
    def __init__(self):
        self.cv_raw = None          # Contenu brut du CV
        self.cv_structured = None    # CV analysé (format JSON)
        self.cv_file_name = None     # Nom du fichier CV
        self.job_offer = None        # Offre d'emploi sélectionnée
        self.lettre_infos = None     # Informations pour la lettre
```

Cette architecture nous permet de maintenir le contexte utilisateur à travers différentes commandes sans recourir à une base de données, parfaitement adaptée à un usage académique.

### Framework d'intégration des modules

Nous avons créé un système modulaire d'intégration permettant aux autres groupes d'ajouter facilement leurs fonctionnalités :

```python
# Exemple de notre méthode d'intégration depuis bot.py
def setup(bot):
    # Configuration des modules
    setup_scrape_command(bot)
    setup_cv_mistral_command(bot)
    setup_cv_gemini_command(bot)
    setup_upload_cv_command(bot)
    setup_compare_command(bot)
    setup_letter_command(bot)
    
    # Modules conditionnels
    if PARSE_CV_COMMANDS_AVAILABLE:
        setup_parse_cv_commands(bot)
    
    if GEMINI_API_KEY:
        setup_partillm_commands(bot, GEMINI_API_KEY)
```

### Interface utilisateur Discord

Nous avons développé des composants interactifs pour améliorer l'expérience utilisateur :
- **Embeds** : Affichage structuré et visuel des informations
- **Menus déroulants** : Sélection d'offres d'emploi
- **Messages éphémères** : Communication privée avec l'utilisateur
- **Modals** : Collecte d'informations supplémentaires

## 📋 Commandes implémentées

Nous avons implémenté et intégré les commandes slash suivantes :

### Gestion de CV
- `/telecharger_cv` : Upload et extraction du texte d'un CV (PDF/DOCX)
- `/extraire_cv_mistral` : Analyse structurée via Mistral AI
- `/extraire_cv_gemini` : Analyse structurée via Google Gemini

### Recherche d'emploi
- `/scrape` : Recherche multi-source (France Travail + Indeed)
- `/scrape_stage` : Recherche spécifique de stages

### Analyse et matching
- `/comparer_cv_offre` : Comparaison CV/offre (méthode standard)
- `/analyser_cv_offre` : Analyse détaillée de compatibilité (Groupe 5)

### Génération de documents
- `/infos_lettre_g5` : Collecte d'informations complémentaires
- `/generer_lettre` : Création de lettre de motivation (méthode standard)
- `/generer_lettre_g5` : Génération avancée via Gemini (Groupe 5)

## 🛠 Défis techniques résolus

### 1. Gestion des interactions Discord expirées

Les interactions Discord ont une durée de vie limitée (3 secondes), mais certaines opérations (analyse de CV, génération de lettre) prennent plus de temps. Nous avons implémenté un système robuste de réponses différées :

```python
@bot.tree.command(name="extraire_cv_gemini")
async def extraire_cv_gemini(interaction: discord.Interaction):
    # Différer la réponse immédiatement
    await interaction.response.defer(thinking=True)
    
    # Traitement long...
    
    # Répondre une fois le traitement terminé
    await interaction.followup.send(embed=embed)
```

### 2. Orchestration des modules

Nous avons dû concevoir une architecture permettant l'intégration de modules développés indépendamment par différentes équipes, avec des styles et approches variés. Notre solution :

1. Création d'interfaces standardisées
2. Système d'initialisation modulaire
3. Architecture de partage de données utilisateur
4. Gestion centralisée des erreurs

### 3. Extraction et traitement de texte

L'extraction fiable de texte depuis divers formats de CV a nécessité des techniques robustes :

```python
async def extract_text_from_file(attachment):
    file_bytes = await attachment.read()
    file_stream = io.BytesIO(file_bytes)
    text = ""
    
    if attachment.filename.lower().endswith('.pdf'):
        reader = PyPDF2.PdfReader(file_stream)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif attachment.filename.lower().endswith('.docx'):
        doc = docx.Document(file_stream)
        for para in doc.paragraphs:
            text += para.text + "\n"
    # ...
```

## 💻 Installation et déploiement

### Prérequis
- Python 3.10 ou supérieur
- Token de bot Discord
- Clés API (Mistral AI, Google Gemini)
- Identifiants France Travail

### Installation

1. Clonez le dépôt
```bash
git clone https://github.com/DS2E2025CP/bot_discord.git
cd bot_discord
```

2. Configurez les variables d'environnement
Créez un fichier `.env` à la racine du projet :
```
DISCORD_TOKEN=votre_token_discord

MISTRAL_API_KEY=votre_cle_mistral
GEMINI_API_KEY=votre_cle_gemini

FT_CLIENT_ID=
FT_CLIENT_SECRET=
```

3. Lancez le bot
```bash
python bot.py
```

### Déploiement

Pour un déploiement en production, nous recommandons :
- Utilisation d'un service comme Heroku, Railway ou un VPS
- Configuration d'un système de monitoring
- Mise en place de logs persistants

## 👥 Contribution

- Conception de l'architecture globale
- Développement du framework d'intégration Discord
- Implémentation des commandes slash
- Coordination avec les autres groupes
- Résolution des problèmes d'intégration
- Tests et debugging
- Documentation


---

<div align="center">
  <p><em>Projet JobHunterAI - Master 1 DS2E - Faculté des sciences économiques et de gestion de Strasbourg - 2025</em></p>
</div>
