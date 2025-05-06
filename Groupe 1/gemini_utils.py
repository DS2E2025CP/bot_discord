import io
import json
import PyPDF2
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Gemini - Obtenir la clé API depuis les variables d'environnement
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# Fonction pour lister les modèles disponibles
def list_available_models():
    """
    Liste tous les modèles disponibles pour votre clé API.
    """
    try:
        print("Tentative de récupération des modèles disponibles...")
        models = genai.list_models()
        print("Modèles disponibles:")
        for model in models:
            print(f" - {model.name}")
            print(f"   Supported generation methods: {model.supported_generation_methods}")
        return models
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_text_from_pdf(pdf_bytes):
    """
    Extrait le texte d'un fichier PDF.
    Args:
        pdf_bytes (bytes): contenu binaire du PDF.
    Returns:
        str: texte extrait.
    """
    try:
        texte = ""
        pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in pdf.pages:
            texte += page.extract_text() + "\n"
        return texte
    except Exception as e:
        print(f"Erreur extraction PDF Gemini : {e}")
        return None

def extract_with_gemini(pdf_bytes):
    """
    Utilise Gemini pour analyser un CV et générer un JSON structuré.
    Args:
        pdf_bytes (bytes): contenu du fichier PDF.
    Returns:
        str: JSON structuré ou None si échec.
    """
    # Modèle à utiliser, en se basant sur la liste des modèles disponibles
    # Utilisons directement un des modèles qui supporte generateContent selon la liste
    MODEL_NAME = "gemini-1.5-pro"
    
    texte_cv = extract_text_from_pdf(pdf_bytes)
    if not texte_cv:
        return None
    
    prompt = f"""Voici un CV. Convertis-le en JSON structuré :
    {{
        "prenom_nom": "",
        "email": "",
        "telephone": "",
        "linkedin": "",
        "github": "",
        "competences_techniques": [],
        "soft_skills": [],
        "langues": [],
        "certifications": [],
        "formation": [{{"titre": "", "etablissement": "", "periode": "", "details": []}}],
        "experience": [{{"titre": "", "entreprise": "", "lieu": "", "periode": "", "details": []}}]
    }}
    Texte :
    {texte_cv}
    """
    
    try:
        print(f"Tentative de génération avec le modèle: {MODEL_NAME}")
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Configuration de la génération (options pour améliorer la qualité)
        generation_config = {
            "temperature": 0.2,  # Plus bas pour des réponses plus cohérentes
            "max_output_tokens": 8192,  # Limite la taille de la réponse
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Vérifier si la réponse contient du texte
        if hasattr(response, 'text'):
            content = response.text
        elif hasattr(response, 'parts') and len(response.parts) > 0:
            content = response.parts[0].text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            if hasattr(response.candidates[0], 'content'):
                content = response.candidates[0].content.parts[0].text
            else:
                content = response.candidates[0].text
        else:
            print("Format de réponse non reconnu")
            print(f"Réponse brute: {response}")
            print(f"Type de réponse: {type(response)}")
            print(f"Attributs de réponse: {dir(response)}")
            return None
            
        json_pattern = r"```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$"
        match = re.search(json_pattern, content)
        json_str = match.group(1) or match.group(2) if match else content
        
        # Nettoyer le JSON pour éviter les erreurs de parsing
        json_str = json_str.strip()
        
        # Débogage
        print(f"JSON extrait: {json_str[:200]}...")
        
        json_obj = json.loads(json_str)
        
        # Ajouter les champs manquants
        for champ in ["linkedin", "github", "competences_techniques", "soft_skills", "certifications"]:
            if champ not in json_obj:
                json_obj[champ] = "" if champ in ["linkedin", "github"] else []
                
        return json.dumps(json_obj, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        import traceback
        traceback.print_exc()
        return None

# Pour tester avec un autre modèle si le premier échoue
def extract_with_gemini_fallback(pdf_bytes):
    """
    Version alternative qui essaie différents modèles Gemini si le premier échoue.
    """
    # Liste des modèles à essayer dans l'ordre
    models_to_try = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-2.0-pro-exp",
        "gemini-2.0-flash"
    ]
    
    texte_cv = extract_text_from_pdf(pdf_bytes)
    if not texte_cv:
        return None
    
    prompt = f"""Voici un CV. Convertis-le en JSON structuré :
    {{
        "prenom_nom": "",
        "email": "",
        "telephone": "",
        "linkedin": "",
        "github": "",
        "competences_techniques": [],
        "soft_skills": [],
        "langues": [],
        "certifications": [],
        "formation": [{{"titre": "", "etablissement": "", "periode": "", "details": []}}],
        "experience": [{{"titre": "", "entreprise": "", "lieu": "", "periode": "", "details": []}}]
    }}
    Texte :
    {texte_cv}
    """
    
    last_error = None
    
    for model_name in models_to_try:
        try:
            print(f"Tentative avec le modèle: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Traitement de la réponse similaire à la fonction principale
            if hasattr(response, 'text'):
                content = response.text
            elif hasattr(response, 'parts') and len(response.parts) > 0:
                content = response.parts[0].text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                content = response.candidates[0].content.parts[0].text
            else:
                print(f"Format de réponse non reconnu pour {model_name}")
                continue
                
            json_pattern = r"```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$"
            match = re.search(json_pattern, content)
            json_str = match.group(1) or match.group(2) if match else content
            json_str = json_str.strip()
            
            json_obj = json.loads(json_str)
            
            for champ in ["linkedin", "github", "competences_techniques", "soft_skills", "certifications"]:
                if champ not in json_obj:
                    json_obj[champ] = "" if champ in ["linkedin", "github"] else []
                    
            print(f"Succès avec le modèle {model_name}")
            return json.dumps(json_obj, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"Échec avec le modèle {model_name}: {e}")
            last_error = e
            continue
    
    # Si nous arrivons ici, tous les modèles ont échoué
    print("Tous les modèles ont échoué")
    if last_error:
        import traceback
        traceback.print_exc()
    return None

# Exécuter cette fonction si le script est lancé directement
if __name__ == "__main__":
    print("Vérification des modèles disponibles...")
    list_available_models()