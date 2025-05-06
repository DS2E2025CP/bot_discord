# utils/helper.py
import json
from typing import Dict, Any, Optional, List, Union

# Classe pour stocker les données des utilisateurs
class UserData:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cv_raw = None  # Texte brut du CV
        self.cv_structured = {}  # CV structuré en dictionnaire
        self.cv_file_name = None  # Nom du fichier CV original
        self.job_offers = []  # Liste des offres d'emploi
        self.job_offer = None  # Offre d'emploi sélectionnée
        self.lettre_infos = None  # Informations supplémentaires pour la lettre
        self.analysis_results = None  # Résultats d'analyse CV/offre

# Dictionnaire pour stocker les instances UserData par ID utilisateur
user_data = {}

def get_user_data(user_id: str) -> UserData:
    """Récupère ou crée les données pour un utilisateur"""
    if user_id not in user_data:
        user_data[user_id] = UserData(user_id)
    return user_data[user_id]

def check_user_prerequisites(user_id: str, need_cv: bool = False, need_job_offer: bool = False) -> Optional[str]:
    """
    Vérifie si l'utilisateur a les prérequis nécessaires (CV et/ou offre d'emploi)
    Retourne un message d'erreur si les prérequis ne sont pas remplis, None sinon
    """
    if user_id not in user_data:
        return "❌ Vous n'avez pas encore interagi avec le bot. Commencez par télécharger votre CV."
    
    user = user_data[user_id]
    
    if need_cv and not user.cv_raw:
        return "❌ Vous devez d'abord télécharger votre CV avec la commande `/telecharger_cv`."
    
    if need_job_offer and not user.job_offer:
        if not user.job_offers:
            return "❌ Vous devez d'abord rechercher des offres d'emploi avec la commande `/chercher_emploi`."
        else:
            return "❌ Vous devez d'abord sélectionner une offre d'emploi avec la commande `/selectionner_offre`."
    
    return None

def cv_to_dict(structured_text: str) -> Dict[str, Any]:
    """
    Convertit un texte structuré d'analyse de CV en dictionnaire
    Pour être utilisé après l'extraction du CV par un LLM
    """
    try:
        # Essaie de parser directement si c'est déjà du JSON
        if structured_text.strip().startswith('{') and structured_text.strip().endswith('}'):
            return json.loads(structured_text)
        
        # Sinon, essaie de construire un dictionnaire à partir du texte structuré
        cv_dict = {
            "prenom_nom": "",
            "email": "",
            "telephone": "",
            "linkedin": "",
            "github": "",
            "formation": [],
            "experience": [],
            "competences_techniques": [],
            "soft_skills": [],
            "langues": [],
            "certifications": []
        }
        
        current_section = None
        
        for line in structured_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Détection des sections
            if ":" in line and len(line.split(":", 1)[0]) < 30:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Informations de contact
                if key in ["nom", "prenom_nom", "nom complet"]:
                    cv_dict["prenom_nom"] = value
                elif key in ["email", "courriel", "e-mail"]:
                    cv_dict["email"] = value
                elif key in ["telephone", "téléphone", "tel", "tél"]:
                    cv_dict["telephone"] = value
                elif key in ["linkedin", "profil linkedin"]:
                    cv_dict["linkedin"] = value
                elif key in ["github"]:
                    cv_dict["github"] = value
                # Sections principales
                elif key in ["formation", "formations", "education", "études"]:
                    current_section = "formation"
                elif key in ["experience", "expérience", "experiences", "expériences"]:
                    current_section = "experience"
                elif key in ["competences", "compétences", "competences techniques", "compétences techniques"]:
                    current_section = "competences_techniques"
                    if value:
                        cv_dict["competences_techniques"].extend([v.strip() for v in value.split(',')])
                elif key in ["soft skills", "compétences comportementales"]:
                    current_section = "soft_skills"
                    if value:
                        cv_dict["soft_skills"].extend([v.strip() for v in value.split(',')])
                elif key in ["langues", "langue"]:
                    current_section = "langues"
                    if value:
                        cv_dict["langues"].extend([v.strip() for v in value.split(',')])
                elif key in ["certifications", "certification"]:
                    current_section = "certifications"
                    if value:
                        cv_dict["certifications"].extend([v.strip() for v in value.split(',')])
            
            # Traitement des éléments de liste
            elif line.startswith('-') or line.startswith('•'):
                value = line[1:].strip()
                if current_section == "competences_techniques":
                    cv_dict["competences_techniques"].append(value)
                elif current_section == "soft_skills":
                    cv_dict["soft_skills"].append(value)
                elif current_section == "langues":
                    cv_dict["langues"].append(value)
                elif current_section == "certifications":
                    cv_dict["certifications"].append(value)
        
        return cv_dict
    except Exception as e:
        print(f"Erreur lors de la conversion du CV en dictionnaire: {e}")
        return {}

def format_job_offer_from_api(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formate les données d'une offre d'emploi provenant d'une API
    pour correspondre au format attendu par notre système
    """
    return {
        "titre": job_data.get("title", ""),
        "entreprise": job_data.get("company", ""),
        "lieu": job_data.get("location", ""),
        "type_contrat": job_data.get("contract_type", ""),
        "description_entreprise": job_data.get("company_description", ""),
        "missions": job_data.get("description", ""),
        "profil_recherche": job_data.get("requirements", "")
    }
