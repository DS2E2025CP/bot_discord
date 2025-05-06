import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import tempfile
import json
from discord import File
import sys
import traceback

# Configuration du gestionnaire d'erreurs
def handle_exception(exc_type, exc_value, exc_traceback):
    print("\n=== ERREUR NON GÉRÉE DÉTECTÉE ===")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("=== FIN DE L'ERREUR ===\n")
    return

sys.excepthook = handle_exception

print("\n=== DÉMARRAGE DU BOT PRINCIPAL ===")

# Charger les variables d'environnement
load_dotenv()

# Création du dossier utils s'il n'existe pas
if not os.path.exists('utils'):
    os.makedirs('utils')

# Importation des modules personnalisés
from scrape_jobs import setup_scrape_command
from extract_cv import setup_cv_mistral_command, setup_cv_gemini_command, setup_upload_cv_command
from match_cv_offer import setup_compare_command
from generate_cover_letter import setup_letter_command
from utils.helper import UserData, user_data
# Import des nouvelles fonctionnalités du groupe 5
from partieLLM_discord import setup_partillm_commands
# Import des commandes de parsing de CV (version originale)
try:
    from parse_cv_commands import setup_parse_cv_commands
    PARSE_CV_COMMANDS_AVAILABLE = True
except ImportError:
    print("⚠️ Module parse_cv_commands non trouvé. Les commandes parse_cv_* ne seront pas disponibles.")
    PARSE_CV_COMMANDS_AVAILABLE = False

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes synchronisées: {len(synced)}")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes: {e}")

# Configuration des commandes
def setup(bot):
    # Récupérer la clé API Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("⚠️ AVERTISSEMENT: Clé API Gemini non trouvée. Les fonctionnalités PartieLLM ne seront pas disponibles.")
    
    # Configurer les commandes existantes
    setup_scrape_command(bot)
    setup_cv_mistral_command(bot)
    setup_cv_gemini_command(bot)
    setup_upload_cv_command(bot)  # Ajout de la commande de téléchargement de CV
    setup_compare_command(bot)
    setup_letter_command(bot)
    
    # Configurer les commandes de parsing de CV (version originale)
    if PARSE_CV_COMMANDS_AVAILABLE:
        setup_parse_cv_commands(bot)
        print("✅ Commandes de parsing de CV originales configurées")
    
    # Configurer les nouvelles commandes du groupe 5
    if GEMINI_API_KEY:
        setup_partillm_commands(bot, GEMINI_API_KEY)
        print("✅ Commandes PartieLLM configurées avec succès")
    else:
        print("❌ Commandes PartieLLM non configurées (clé API manquante)")

# Initialiser les commandes
setup(bot)

# Démarrer le bot
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("❌ Le token Discord est introuvable. Vérifie ton fichier .env.")
else:
    print(f"Démarrage du bot avec le token: {'*' * len(TOKEN)}")
    
    print("\n📋 Commandes disponibles :")
    print("  Commandes slash (/) :")
    print("  - /telecharger_cv - Télécharger un CV pour analyse")
    print("  - /extraire_cv - Extraire les informations d'un CV avec Mistral")
    print("  - /extraire_cv_gemini - Extraire les informations d'un CV avec Gemini")
    if PARSE_CV_COMMANDS_AVAILABLE:
        print("  - /parse_cv_mistral - Analyser un CV avec Mistral et générer un fichier JSON")
        print("  - /parse_cv_gemini - Analyser un CV avec Gemini et générer un fichier JSON")
    print("  - /chercher_emploi - Rechercher des offres d'emploi")
    print("  - /selectionner_offre - Sélectionner une offre d'emploi")
    print("  - /comparer_cv_offre - Comparer votre CV avec la fiche de poste")
    print("  - /analyser_cv_offre - Analyser la compatibilité CV/offre (Groupe 5)")
    print("  - /infos_lettre_g5 - Ajouter des informations pour la lettre (Groupe 5)")
    print("  - /generer_lettre - Générer une lettre de motivation")
    print("  - /generer_lettre_g5 - Générer une lettre avec Gemini (Groupe 5)")
    
    print("\n  Commandes préfixées (!) :")
    if PARSE_CV_COMMANDS_AVAILABLE:
        print("  - !parse_cv - Analyser un CV avec Mistral (ancienne méthode)")
    
    print("\nDémarrage du bot...")
    bot.run(TOKEN)
