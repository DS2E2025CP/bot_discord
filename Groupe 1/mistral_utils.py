import io
import requests
import json
import PyPDF2
import re
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Clé API Mistral depuis les variables d'environnement
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = "https://api.mistral.ai/v1/chat/completions"

def extraire_texte_pdf(fichier_pdf):
    """
    Extrait le texte d'un fichier PDF.
    
    Args:
        fichier_pdf (bytes): Contenu binaire du fichier PDF.
        
    Returns:
        str: Texte extrait du PDF ou None en cas d'erreur.
    """
    try:
        texte = ""
        pdf_stream = io.BytesIO(fichier_pdf)
        lecteur_pdf = PyPDF2.PdfReader(pdf_stream)
        for page in lecteur_pdf.pages:
            texte += page.extract_text() + "\n"
        return texte
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF: {e}")
        return None


def generer_json_avec_mistral(texte_cv):
    """
    Envoie le texte d'un CV à Mistral pour générer un JSON structuré.

    Args:
        texte_cv (str): Contenu textuel du CV.

    Returns:
        str: JSON structuré ou None si échec.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }

    prompt = f"""Voici un CV. Analyse-le et retourne un JSON structuré :
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

    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        resultat = response.json()
        content = resultat["choices"][0]["message"]["content"]

        json_pattern = r"```json\s*([\s\S]*?)\s*```|^\s*(\{[\s\S]*\})\s*$"
        match = re.search(json_pattern, content)
        json_str = match.group(1) or match.group(2) if match else content

        json_obj = json.loads(json_str)

        # Champs obligatoires par défaut
        for champ in ["linkedin", "github", "competences_techniques", "soft_skills", "certifications"]:
            if champ not in json_obj:
                json_obj[champ] = "" if champ in ["linkedin", "github"] else []

        return json.dumps(json_obj, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Erreur Mistral: {e}")
        return None