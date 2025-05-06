import discord
from discord import app_commands
import os
import io
import PyPDF2
import tempfile
import requests
import json
import re
from datetime import datetime
import google.generativeai as genai
from utils.helper import get_user_data

# Configuration de l'API Gemini
def setup_gemini_api():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return True
    return False

# Configuration de l'API Mistral
def setup_mistral_api():
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    return MISTRAL_API_KEY is not None

# Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(file_bytes):
    try:
        text = ""
        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Erreur extraction PDF: {e}")
        return None

async def parse_cv_with_gemini(cv_bytes, cv_filename):
    """
    Utilise l'API Gemini pour analyser un CV au format PDF
    """
    try:
        # Configuration de Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            return None, "❌ Clé API Gemini non configurée."
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Extraction du texte du PDF
        cv_text = extract_text_from_pdf(cv_bytes)
        if not cv_text:
            return None, "❌ Impossible d'extraire le texte du PDF."
        
        # Création du prompt
        prompt = f"""
        Voici le texte complet d'un CV extrait d'un fichier PDF. Analyse-le et convertis-le directement en JSON avec la structure suivante:

        ```json
        {{
          "prenom_nom": "string",
          "email": "string",
          "telephone": "string",
          "linkedin": "string (seulement le nom d'utilisateur, pas l'URL complète, ou vide si non présent)",
          "github": "string (seulement le nom d'utilisateur, pas l'URL complète, ou vide si non présent)",
          "competences_techniques": [
            "compétence technique 1",
            "compétence technique 2"
          ],
          "soft_skills": [
            "soft skill 1",
            "soft skill 2"
          ],
          "langues": [
            "string (langue et niveau)"
          ],
          "certifications": [
            "string (certification 1)",
            "string (certification 2)"
          ],
          "formation": [
            {{
              "titre": "string (diplôme et spécialité)",
              "etablissement": "string (nom de l'école/université)",
              "periode": "string (dates de début et fin)",
              "details": [
                "string (enseignements, mentions, etc.)"
              ]
            }}
          ],
          "experience": [
            {{
              "titre": "string (intitulé du poste)",
              "entreprise": "string (nom de l'entreprise)",
              "lieu": "string (ville/pays ou télétravail)",
              "periode": "string (dates de début et fin)",
              "details": [
                "string (responsabilités, accomplissements)"
              ]
            }}
          ]
        }}
        ```

        Instructions spéciales:
        - Inclus TOUJOURS les champs "linkedin" et "github" dans le JSON, même s'ils sont vides ("").
        - Pour LinkedIn, si tu trouves une URL comme "linkedin.com/in/nom-utilisateur", n'inclus que "nom-utilisateur". Si tu trouves directement "/linkedin-innom-utilisateur", n'inclus que "nom-utilisateur".
        - Pour GitHub, si tu trouves une URL comme "github.com/nom-utilisateur", n'inclus que "nom-utilisateur". Si tu trouves directement "/githubnom-utilisateur", n'inclus que "nom-utilisateur".
        - Si aucun profil LinkedIn ou GitHub n'est mentionné dans le CV, laisse ces champs vides: "linkedin": "", "github": "".

        - IMPORTANT: Pour les compétences techniques, inclus UNIQUEMENT les langages de programmation, logiciels, et outils concrets.
          * Ne pas inclure dans cette section les domaines de connaissances théoriques comme l'économie, la finance, les mathématiques, etc.
          * Limite-toi aux compétences techniques concrètes et opérationnelles (langages, logiciels, frameworks, etc.)

        - Identifie et liste toutes les soft skills (compétences personnelles, interpersonnelles et transversales).

        - CERTIFICATIONS:
          * Recherche et inclus toutes les certifications mentionnées dans le CV.
          * Permis de conduire (B, BVA, etc.), certifications de langue (TOEIC, TOEFL, etc.), certifications informatiques (PIX, etc.)
          * Si aucune certification n'est mentionnée, laisse la liste vide: []

        - Tu dois ABSOLUMENT inclure les champs "competences_techniques", "soft_skills" et "certifications" dans le JSON final, même s'ils sont vides.

        Texte du CV:
        {cv_text}

        Retourne UNIQUEMENT le JSON sans aucun autre commentaire. Assure-toi que le format est valide.
        """
        
        # Appel de l'API Gemini
        response = model.generate_content(prompt)
        
        # Récupération de la réponse
        if hasattr(response, 'text'):
            result_json = response.text
        else:
            result_json = response.parts[0].text
        
        # Vérification et nettoyage de la réponse JSON
        # Parfois Gemini ajoute des ```json et ``` autour du JSON
        json_pattern = r"```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$"
        match = re.search(json_pattern, result_json)
        
        if match:
            result_json = match.group(1) or match.group(2)
        
        # Vérifier que le JSON est valide
        try:
            json_obj = json.loads(result_json)
            
            # Créer un fichier temporaire pour stocker le JSON
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                temp_file.write(json.dumps(json_obj, ensure_ascii=False, indent=2).encode('utf-8'))
                temp_path = temp_file.name
            
            return temp_path, "✅ Analyse terminée avec succès!"
            
        except json.JSONDecodeError as e:
            return None, f"❌ Erreur de format JSON: {str(e)}"
            
    except Exception as e:
        return None, f"❌ Erreur lors de l'analyse: {str(e)}"

async def parse_cv_with_mistral(cv_bytes, cv_filename):
    """
    Utilise l'API Mistral pour analyser un CV au format PDF
    """
    try:
        # Configuration de Mistral
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        if not MISTRAL_API_KEY:
            return None, "❌ Clé API Mistral non configurée."
        
        API_URL = "https://api.mistral.ai/v1/chat/completions"
        
        # Extraction du texte du PDF
        cv_text = extract_text_from_pdf(cv_bytes)
        if not cv_text:
            return None, "❌ Impossible d'extraire le texte du PDF."
        
        # Liste des compétences techniques et soft skills à rechercher pour aider le modèle
        liste_competences = """
        Exemples de compétences techniques à identifier (UNIQUEMENT les outils concrets et langages de programmation):
        
        # Langages de programmation
        Python, R, Java, C, C++, C#, JavaScript, TypeScript, PHP, Ruby, Swift, Kotlin, Go, Rust, SQL, Scala, Perl, Shell, Bash, PowerShell, MATLAB, VBA
        
        # Data Science et ML (outils uniquement)
        TensorFlow, PyTorch, Keras, Scikit-learn, Pandas, NumPy, SciPy, NLTK, spaCy, Matplotlib, Seaborn
        
        # Web et Frontend
        HTML, CSS, Bootstrap, React, Angular, Vue.js, jQuery, REST API, GraphQL, Node.js, Express
        
        # Bases de données
        MySQL, PostgreSQL, SQLite, Oracle, MongoDB, Redis, Elasticsearch, NoSQL, SQL Server, MariaDB
        
        # DevOps et Cloud
        AWS, Azure, GCP, Docker, Kubernetes, Git, GitHub, GitLab, CI/CD, Jenkins, Linux, Unix, Windows, MacOS
        
        # Bureautique et outils
        Microsoft Office, Microsoft 365, Office 365, Suite Office, Excel, Word, PowerPoint, Access, Outlook, OneNote, SharePoint, OneDrive, Teams, Microsoft Teams, Tableau, Power BI, SAP, Salesforce, Jira, Confluence, Trello, MS Project
        
        # Autres outils techniques
        LaTeX, RStudio, Jupyter, Orange, SAS, SPSS
        
        ATTENTION: N'inclus PAS les domaines de connaissances ou sujets théoriques comme compétences techniques.
        Par exemple, n'inclus PAS: Économie, Microéconomie, Macroéconomie, Comptabilité, Finance, Droit, Mathématiques, 
        Statistiques théoriques, Machine Learning théorique, etc. 
        
        Inclus UNIQUEMENT les outils et langages concrets que la personne sait utiliser.
        
        Exemples de soft skills à identifier:
        Communication, leadership, travail d'équipe, résolution de problèmes, gestion de projet, organisation, autonomie, adaptabilité, créativité, esprit critique, négociation, intelligence émotionnelle, gestion du temps, gestion du stress, écoute active, empathie, flexibilité, prise de décision, persuasion, présentation, prise de parole en public
        
        Exemples de certifications:
        Permis B, Permis BVA, TOEIC, TOEFL, IELTS, Cambridge Certificate, DELF, DALF, HSK, PIX, Google Analytics, Certification Microsoft, Certification AWS, Certification Azure, ITIL, PMP, PRINCE2
        """
        
        # Créer le prompt pour Mistral
        prompt = f"""
        Voici le texte complet d'un CV extrait d'un fichier PDF. Analyse-le et convertis-le directement en JSON avec la structure suivante:

        ```json
        {{
          "prenom_nom": "string",
          "email": "string",
          "telephone": "string",
          "linkedin": "string (seulement le nom d'utilisateur, pas l'URL complète, ou vide si non présent)",
          "github": "string (seulement le nom d'utilisateur, pas l'URL complète, ou vide si non présent)",
          "competences_techniques": [
            "compétence technique 1",
            "compétence technique 2"
          ],
          "soft_skills": [
            "soft skill 1",
            "soft skill 2"
          ],
          "langues": [
            "string (langue et niveau)"
          ],
          "certifications": [
            "string (certification 1)",
            "string (certification 2)"
          ],
          "formation": [
            {{
              "titre": "string (diplôme et spécialité)",
              "etablissement": "string (nom de l'école/université)",
              "periode": "string (dates de début et fin)",
              "details": [
                "string (enseignements, mentions, etc.)"
              ]
            }}
          ],
          "experience": [
            {{
              "titre": "string (intitulé du poste)",
              "entreprise": "string (nom de l'entreprise)",
              "lieu": "string (ville/pays ou télétravail)",
              "periode": "string (dates de début et fin)",
              "details": [
                "string (responsabilités, accomplissements)"
              ]
            }}
          ]
        }}
        ```

        Instructions spéciales:
        - Inclus TOUJOURS les champs "linkedin" et "github" dans le JSON, même s'ils sont vides ("").
        - Pour LinkedIn, si tu trouves une URL comme "linkedin.com/in/nom-utilisateur", n'inclus que "nom-utilisateur". Si tu trouves directement "/linkedin-innom-utilisateur", n'inclus que "nom-utilisateur".
        - Pour GitHub, si tu trouves une URL comme "github.com/nom-utilisateur", n'inclus que "nom-utilisateur". Si tu trouves directement "/githubnom-utilisateur", n'inclus que "nom-utilisateur".
        - Si aucun profil LinkedIn ou GitHub n'est mentionné dans le CV, laisse ces champs vides: "linkedin": "", "github": "".
        
        - IMPORTANT: Pour les compétences techniques, inclus UNIQUEMENT les langages de programmation, logiciels, et outils concrets.
          * Ne pas inclure dans cette section les domaines de connaissances théoriques comme l'économie, la finance, les mathématiques, etc.
          * Limite-toi aux compétences techniques concrètes et opérationnelles (langages, logiciels, frameworks, etc.)
          * Assure-toi d'inclure les outils de la suite Microsoft Office (Word, Excel, PowerPoint) et Microsoft 365 s'ils sont mentionnés dans le CV
        
        - Identifie et liste toutes les soft skills (compétences personnelles, interpersonnelles et transversales).
        
        - CERTIFICATIONS:
          * Recherche et inclus toutes les certifications mentionnées dans le CV.
          * Permis de conduire (B, BVA, etc.), certifications de langue (TOEIC, TOEFL, etc.), certifications informatiques (PIX, etc.)
          * Si aucune certification n'est mentionnée, laisse la liste vide: []
        
        - Tu dois ABSOLUMENT inclure les champs "competences_techniques", "soft_skills" et "certifications" dans le JSON final, même s'ils sont vides.

        {liste_competences}

        Texte du CV:
        {cv_text}

        Retourne UNIQUEMENT le JSON sans aucun autre commentaire. Assure-toi que le format est valide.
        """
        
        # Configuration des en-têtes pour l'API Mistral
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        
        # Préparation des données pour l'API
        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        # Envoi de la requête à l'API Mistral
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extraction du JSON de la réponse
            json_pattern = r"```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$"
            match = re.search(json_pattern, content)
            
            if match:
                json_str = match.group(1) or match.group(2)
                
                # Vérifier que le JSON est valide
                try:
                    json_obj = json.loads(json_str)
                    
                    # Post-traitement pour détecter Microsoft Office et ses composants
                    if "competences_techniques" in json_obj:
                        # Liste des termes bureautiques à rechercher dans le texte du CV
                        bureautique_terms = [
                            "Microsoft Office", "MS Office", "Office", "Suite Office", 
                            "Microsoft 365", "Office 365", "M365", "O365",
                            "Excel", "Word", "PowerPoint", "PPT", "Access", "Outlook",
                            "OneNote", "SharePoint", "OneDrive", "Teams", "Microsoft Teams"
                        ]
                        
                        # Vérifier si ces termes sont dans le texte du CV mais pas dans les compétences
                        found_terms = set()
                        for term in bureautique_terms:
                            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                            if pattern.search(cv_text):
                                # Normaliser le nom de la compétence (première lettre de chaque mot en majuscule)
                                normalized_term = ' '.join(word.capitalize() for word in term.split())
                                found_terms.add(normalized_term)
                        
                        # Ajouter les termes trouvés qui ne sont pas déjà dans les compétences
                        for term in found_terms:
                            if not any(comp.lower() == term.lower() for comp in json_obj["competences_techniques"]):
                                json_obj["competences_techniques"].append(term)
                    
                    # Vérifier que tous les champs requis sont présents, sinon les ajouter
                    champs_requis = ["linkedin", "github", "competences_techniques", "soft_skills", "certifications"]
                    for champ in champs_requis:
                        if champ not in json_obj:
                            if champ in ["linkedin", "github"]:
                                json_obj[champ] = ""
                            elif champ in ["competences_techniques", "soft_skills", "certifications"]:
                                json_obj[champ] = []
                    
                    # Créer un fichier temporaire pour stocker le JSON
                    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                        temp_file.write(json.dumps(json_obj, ensure_ascii=False, indent=2).encode('utf-8'))
                        temp_path = temp_file.name
                    
                    return temp_path, "✅ Analyse terminée avec succès!"
                    
                except json.JSONDecodeError as e:
                    return None, f"❌ Erreur de format JSON: {str(e)}"
            else:
                return None, "❌ Impossible d'extraire un JSON valide de la réponse."
        else:
            return None, f"❌ Erreur API Mistral: {response.status_code} - {response.text}"
            
    except Exception as e:
        return None, f"❌ Erreur lors de l'analyse: {str(e)}"

def setup_parse_cv_commands(bot):
    """Configure les commandes pour parser un CV avec Gemini ou Mistral"""
    
    # Commande pour parser un CV avec Gemini (slash command)
    @bot.tree.command(name="parse_cv_gemini", description="Analyse un CV avec Gemini et génère un fichier JSON")
    async def parse_cv_gemini(interaction: discord.Interaction, fichier: discord.Attachment):
        await interaction.response.defer(thinking=True)
        
        # Vérifier le type de fichier
        if not fichier.filename.lower().endswith('.pdf'):
            await interaction.followup.send("❌ Veuillez fournir un fichier PDF.", ephemeral=True)
            return
            
        try:
            # Télécharger le fichier
            file_bytes = await fichier.read()
            
            # Informer l'utilisateur que l'analyse est en cours
            await interaction.followup.send("⏳ Analyse du CV avec Gemini en cours... Veuillez patienter.")
            
            # Analyser le CV avec Gemini
            temp_path, message = await parse_cv_with_gemini(file_bytes, fichier.filename)
            
            if temp_path:
                # Stocker les données pour cet utilisateur
                user_data = get_user_data(interaction.user.id)
                user_data.cv_raw = extract_text_from_pdf(file_bytes)
                user_data.cv_file_name = fichier.filename
                
                with open(temp_path, 'r', encoding='utf-8') as f:
                    user_data.cv_structured = json.load(f)
                
                # Envoyer le fichier JSON
                filename = f"{fichier.filename.rsplit('.', 1)[0]}_gemini.json"
                await interaction.followup.send(
                    content="✅ Analyse terminée avec succès! Voici le fichier JSON généré:",
                    file=discord.File(temp_path, filename=filename)
                )
                
                # Supprimer le fichier temporaire
                os.unlink(temp_path)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)
    
    # Commande pour parser un CV avec Mistral (slash command)
    @bot.tree.command(name="parse_cv_mistral", description="Analyse un CV avec Mistral et génère un fichier JSON")
    async def parse_cv_mistral(interaction: discord.Interaction, fichier: discord.Attachment):
        await interaction.response.defer(thinking=True)
        
        # Vérifier le type de fichier
        if not fichier.filename.lower().endswith('.pdf'):
            await interaction.followup.send("❌ Veuillez fournir un fichier PDF.", ephemeral=True)
            return
            
        try:
            # Télécharger le fichier
            file_bytes = await fichier.read()
            
            # Informer l'utilisateur que l'analyse est en cours
            await interaction.followup.send("⏳ Analyse du CV avec Mistral en cours... Veuillez patienter.")
            
            # Analyser le CV avec Mistral
            temp_path, message = await parse_cv_with_mistral(file_bytes, fichier.filename)
            
            if temp_path:
                # Stocker les données pour cet utilisateur
                user_data = get_user_data(interaction.user.id)
                user_data.cv_raw = extract_text_from_pdf(file_bytes)
                user_data.cv_file_name = fichier.filename
                
                with open(temp_path, 'r', encoding='utf-8') as f:
                    user_data.cv_structured = json.load(f)
                
                # Envoyer le fichier JSON
                filename = f"{fichier.filename.rsplit('.', 1)[0]}_mistral.json"
                await interaction.followup.send(
                    content="✅ Analyse terminée avec succès! Voici le fichier JSON généré:",
                    file=discord.File(temp_path, filename=filename)
                )
                
                # Supprimer le fichier temporaire
                os.unlink(temp_path)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur s'est produite: {str(e)}", ephemeral=True)
            
    # Ces commandes utilisent l'ancienne syntaxe (commandes préfixées par !)
    @bot.command(name="parse_cv")
    async def parse_cv(ctx):
        """Commande pour parser un CV avec Mistral (ancienne syntaxe)"""
        # Vérifier s'il y a des pièces jointes
        if len(ctx.message.attachments) == 0:
            await ctx.send("❌ Veuillez attacher un fichier PDF contenant le CV à analyser.")
            return
        
        attachment = ctx.message.attachments[0]
        
        # Vérifier si le fichier est au format PDF
        if not attachment.filename.lower().endswith('.pdf'):
            await ctx.send("❌ Le fichier doit être au format PDF.")
            return
        
        # Informer l'utilisateur que le traitement commence
        processing_msg = await ctx.send("⏳ Traitement du CV en cours... Veuillez patienter.")
        
        try:
            # Télécharger le fichier PDF
            pdf_content = await attachment.read()
            
            # Analyser le CV avec Mistral
            await processing_msg.edit(content="⏳ Analyse du CV avec Mistral AI en cours...")
            temp_path, message = await parse_cv_with_mistral(pdf_content, attachment.filename)
            
            if temp_path:
                # Stocker les données pour cet utilisateur
                user_id = str(ctx.author.id)
                user_data = get_user_data(user_id)
                user_data.cv_raw = extract_text_from_pdf(pdf_content)
                user_data.cv_file_name = attachment.filename
                
                with open(temp_path, 'r', encoding='utf-8') as f:
                    user_data.cv_structured = json.load(f)
                
                # Envoyer le fichier JSON
                await processing_msg.edit(content="✅ Traitement terminé ! Voici le fichier JSON généré:")
                await ctx.send(file=discord.File(temp_path, f"{attachment.filename.rsplit('.', 1)[0]}.json"))
                
                # Supprimer le fichier temporaire
                os.unlink(temp_path)
            else:
                await processing_msg.edit(content=f"❌ {message}")
                
        except Exception as e:
            await processing_msg.edit(content=f"❌ Une erreur est survenue lors du traitement: {str(e)}")