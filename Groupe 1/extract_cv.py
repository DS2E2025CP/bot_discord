import discord
from discord import app_commands
import os
import io
import docx
import PyPDF2
import requests
import json
from utils.helper import get_user_data, cv_to_dict

def setup_cv_mistral_command(bot):
    """Configure la commande pour extraire les informations d'un CV avec Mistral"""
    
    @bot.tree.command(name="extraire_cv_mistral", description="Extraire les informations de votre CV avec Mistral")
    async def extraire_cv(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        # Vérifier si l'utilisateur a déjà téléchargé un CV
        user_data = get_user_data(interaction.user.id)
        if not user_data.cv_raw:
            await interaction.followup.send("❌ Vous devez d'abord télécharger votre CV avec la commande `/telecharger_cv`.", ephemeral=True)
            return
        
        try:
            # Utiliser l'API Mistral pour extraire les informations du CV
            MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
            if not MISTRAL_API_KEY:
                await interaction.followup.send("❌ Clé API Mistral non configurée sur le serveur.", ephemeral=True)
                return
            
            mistral_url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            }
            
            prompt = f"""
            Analyze the following CV and extract information in a structured format.
            Return a JSON object with the following fields:
            - prenom_nom: full name of the candidate
            - email: email address
            - telephone: phone number
            - linkedin: LinkedIn profile URL (if any)
            - github: GitHub profile URL (if any)
            - formation: array of education entries, each with titre, etablissement, periode, and details (array of strings)
            - experience: array of professional experience, each with titre, entreprise, lieu, periode, and details (array of strings)
            - competences_techniques: array of technical skills
            - soft_skills: array of soft skills
            - langues: array of languages and proficiency levels
            - certifications: array of certifications

            CV text:
            {user_data.cv_raw}
            """
            
            data = {
                "model": "mistral-large-latest",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            
            response = requests.post(mistral_url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extraire le JSON de la réponse
                start_index = content.find('{')
                end_index = content.rfind('}') + 1
                
                if start_index >= 0 and end_index > start_index:
                    json_content = content[start_index:end_index]
                    try:
                        cv_data = json.loads(json_content)
                        
                        # Stocker les données structurées
                        user_data.cv_structured = cv_data
                        
                        # Créer un résumé pour l'affichage
                        embed = discord.Embed(
                            title="✅ CV analysé avec succès",
                            description=f"Nom: {cv_data.get('prenom_nom', 'Non détecté')}\nEmail: {cv_data.get('email', 'Non détecté')}",
                            color=discord.Color.green()
                        )
                        
                        # Ajouter d'autres champs
                        if cv_data.get('formation'):
                            formations = "\n".join([f"• {f.get('titre', 'N/A')} - {f.get('etablissement', 'N/A')}" for f in cv_data.get('formation', [])[:2]])
                            embed.add_field(name="📚 Formation", value=formations, inline=False)
                        
                        if cv_data.get('experience'):
                            experiences = "\n".join([f"• {e.get('titre', 'N/A')} - {e.get('entreprise', 'N/A')}" for e in cv_data.get('experience', [])[:2]])
                            embed.add_field(name="💼 Expérience", value=experiences, inline=False)
                        
                        if cv_data.get('competences_techniques'):
                            competences = ", ".join(cv_data.get('competences_techniques', [])[:5])
                            embed.add_field(name="🛠️ Compétences techniques", value=competences, inline=False)
                        
                        # Suggestions pour les prochaines étapes
                        embed.add_field(
                            name="📋 Prochaine étape", 
                            value="1. Utilisez `/analyser_cv_offre` pour évaluer la compatibilité", 
                            inline=False
                        )
                        
                        await interaction.followup.send(embed=embed)
                    except json.JSONDecodeError:
                        # Si la réponse n'est pas du JSON valide, essayer de la convertir
                        structured_cv = cv_to_dict(content)
                        user_data.cv_structured = structured_cv
                        await interaction.followup.send("✅ CV analysé. Les données ont été structurées mais le format n'était pas optimal.")
                else:
                    await interaction.followup.send("❌ Impossible d'extraire les données structurées du CV.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erreur API Mistral: {response.status_code} - {response.text}", ephemeral=True)
                
        except Exception as e:
            print(f"Erreur lors de l'extraction du CV: {e}")
            await interaction.followup.send(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)

def setup_cv_gemini_command(bot):
    """Configure la commande pour extraire les informations d'un CV avec Gemini"""
    
    @bot.tree.command(name="extraire_cv_gemini", description="Extraire les informations de votre CV avec Gemini")
    async def extraire_cv_gemini(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        # Vérifier si l'utilisateur a déjà téléchargé un CV
        user_data = get_user_data(interaction.user.id)
        if not user_data.cv_raw:
            await interaction.followup.send("❌ Vous devez d'abord télécharger votre CV avec la commande `/telecharger_cv`.", ephemeral=True)
            return
        
        try:
            # Utiliser l'API Gemini pour extraire les informations du CV
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            if not GEMINI_API_KEY:
                await interaction.followup.send("❌ Clé API Gemini non configurée sur le serveur.", ephemeral=True)
                return
            
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": GEMINI_API_KEY}
            
            prompt = f"""
            Analyze the following CV and extract information in a structured format.
            Return a JSON object with the following fields:
            - prenom_nom: full name of the candidate
            - email: email address
            - telephone: phone number
            - linkedin: LinkedIn profile URL (if any)
            - github: GitHub profile URL (if any)
            - formation: array of education entries, each with titre, etablissement, periode, and details (array of strings)
            - experience: array of professional experience, each with titre, entreprise, lieu, periode, and details (array of strings)
            - competences_techniques: array of technical skills
            - soft_skills: array of soft skills
            - langues: array of languages and proficiency levels
            - certifications: array of certifications

            CV text:
            {user_data.cv_raw}
            """
            
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, params=params, json=data)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Extraire le JSON de la réponse
                start_index = content.find('{')
                end_index = content.rfind('}') + 1
                
                if start_index >= 0 and end_index > start_index:
                    json_content = content[start_index:end_index]
                    try:
                        cv_data = json.loads(json_content)
                        
                        # Stocker les données structurées
                        user_data.cv_structured = cv_data
                        
                        # Créer un résumé pour l'affichage
                        embed = discord.Embed(
                            title="✅ CV analysé avec succès (Gemini)",
                            description=f"Nom: {cv_data.get('prenom_nom', 'Non détecté')}\nEmail: {cv_data.get('email', 'Non détecté')}",
                            color=discord.Color.green()
                        )
                        
                        # Ajouter d'autres champs
                        if cv_data.get('formation'):
                            formations = "\n".join([f"• {f.get('titre', 'N/A')} - {f.get('etablissement', 'N/A')}" for f in cv_data.get('formation', [])[:2]])
                            embed.add_field(name="📚 Formation", value=formations, inline=False)
                        
                        if cv_data.get('experience'):
                            experiences = "\n".join([f"• {e.get('titre', 'N/A')} - {e.get('entreprise', 'N/A')}" for e in cv_data.get('experience', [])[:2]])
                            embed.add_field(name="💼 Expérience", value=experiences, inline=False)
                        
                        if cv_data.get('competences_techniques'):
                            competences = ", ".join(cv_data.get('competences_techniques', [])[:5])
                            embed.add_field(name="🛠️ Compétences techniques", value=competences, inline=False)
                        
                        # Suggestions pour les prochaines étapes
                        embed.add_field(
                            name="📋 Prochaine étape", 
                            value="1. Utilisez `/analyser_cv_offre` pour évaluer la compatibilité",
                            inline=False
                        )
                        
                        await interaction.followup.send(embed=embed)
                    except json.JSONDecodeError:
                        # Si la réponse n'est pas du JSON valide, essayer de la convertir
                        structured_cv = cv_to_dict(content)
                        user_data.cv_structured = structured_cv
                        await interaction.followup.send("✅ CV analysé. Les données ont été structurées mais le format n'était pas optimal.")
                else:
                    await interaction.followup.send("❌ Impossible d'extraire les données structurées du CV.", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Erreur API Gemini: {response.status_code} - {response.text}", ephemeral=True)
                
        except Exception as e:
            print(f"Erreur lors de l'extraction du CV avec Gemini: {e}")
            await interaction.followup.send(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)

# Fonction pour extraire le texte d'un fichier
async def extract_text_from_file(attachment):
    """Extrait le texte d'un fichier PDF, DOCX ou TXT"""
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
    elif attachment.filename.lower().endswith('.txt'):
        text = file_stream.read().decode('utf-8')
    else:
        text = "Format non supporté. Veuillez télécharger un fichier PDF, DOCX ou TXT."
    
    return text

# Commande pour télécharger un CV
def setup_upload_cv_command(bot):
    """Configure la commande pour télécharger un CV"""
    
    @bot.tree.command(name="telecharger_cv", description="Télécharger votre CV pour analyse")
    async def telecharger_cv(interaction: discord.Interaction, fichier: discord.Attachment):
        await interaction.response.defer(thinking=True)
        
        try:
            # Vérifier le type de fichier
            if not any(fichier.filename.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt']):
                await interaction.followup.send("❌ Format non supporté. Veuillez télécharger un fichier PDF, DOCX ou TXT.", ephemeral=True)
                return
            
            # Extraire le texte du fichier
            cv_text = await extract_text_from_file(fichier)
            
            # Stocker le CV pour cet utilisateur
            user_data = get_user_data(interaction.user.id)
            user_data.cv_raw = cv_text
            user_data.cv_file_name = fichier.filename
            
            # Afficher un aperçu du texte extrait
            preview = cv_text[:200] + "..." if len(cv_text) > 200 else cv_text
            
            embed = discord.Embed(
                title="✅ CV téléchargé avec succès",
                description=f"Fichier: {fichier.filename}\n\nAperçu du texte extrait:\n```\n{preview}\n```",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Prochaines étapes", 
                value="1. Utilisez `/extraire_cv_gemini` ou `extraire_cv_mistral` pour analyser votre CV\n2. Utilisez bien `/scrape` pour trouver des offres et en sélectionner une", 
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Erreur lors du téléchargement du CV: {e}")
            await interaction.followup.send(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)