import requests                      # Pour effectuer des requêtes HTTP vers des API
import difflib                       # Utile pour comparer des séquences, comme des chaînes de caractères
from urllib.parse import urlencode   # Pour construire des URLs en encodant des paramètres
import re                            # Fournit des opérations d'expressions régulières
import pprint                        # Utile pour mieux voir la structure du dictionnaire qui comprend les données

# Avant de commencer (Important)
#  1. Création du compte sur France Travail IO
#  2. Création d'une application dans votre espace France Travail IO : Lors de la création, vous allez avoir: 
#               Client ID (un identifiant unique pour votre application)
#               Client secret (un mot de passe pour authentifier votre application)
#  3. Copier et coller ces identifiants dans les guillemets des lignes correspondantes dans le code python

#  4. Ici, j'ai laissé mes identifiants pour l'instant, mais si vous voulez que le code fonctionne à l'avenir, il faudra faire les étapes au dessus

class FranceTravailAPI:
   def __init__(self, client_id=None, client_secret=None):
       self.client_id = client_id or "PAR_recuperateuroffressel_201263b93beec49e65d91dd35e577cc10da48c610f24e5185947ec13702f76fd" # Rentrer le client id
       self.client_secret = client_secret or "1200839c51315a11b6619dcbab857711dc67f6591696feddc6169c191590f158"  # Rentrer le code secret
      
       try:
           # Récupère le jeton d'accès nécessaire pour les requêtes à l'API.
           self.token = self.get_token()
           # Charge la liste des communes depuis l'API ou une source locale.
           self.communes = self.get_communes()
       except Exception as e:
           # En cas d'erreur lors de l'initialisation (récupération du token ou des communes), affiche un message et propage l'exception.
           print(f"Erreur d'initialisation : {str(e)}")
           raise


   def get_token(self):
       # Fonction pour obtenir un jeton d'accès depuis l'API d'authentification de France Travail.
       # Le token est obligatoire pour pouvoir faire des requêtes par la suite
       url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
       # Paramètres à envoyer dans le corps de la requête POST pour l'obtention du jeton.
       payload = {
           "grant_type": "client_credentials",
           "client_id": self.client_id,
           "client_secret": self.client_secret,
           "scope": "api_offresdemploiv2 o2dsoffre"
       }
       # En-têtes de la requête HTTP, indiquant que les données sont formatées comme un formulaire URL-encodé.
       headers = {
           "Content-Type": "application/x-www-form-urlencoded"
       }
      
       try:
           # Envoi de la requête POST à l'URL d'authentification avec les données et les en-têtes.
           response = requests.post(url, data=payload, headers=headers)
          
           # Vérification du statut de la réponse HTTP. Si le code n'est pas 200 (OK), une exception est levée.
           if response.status_code != 200:
               if response.status_code == 401:
                   error_msg = "Erreur d'authentification: vérifiez vos identifiants"
               elif response.status_code == 429:
                   error_msg = "Trop de requêtes envoyées à l'API"
               else:
                   error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
               raise Exception(error_msg)
              
           # Tentative de décodage de la réponse JSON.
           data = response.json()
           # Vérification que la clé 'access_token' est présente dans la réponse JSON.
           if "access_token" not in data:
               raise Exception("Token non trouvé dans la réponse")
              
           # Retourne le jeton d'accès extrait de la réponse JSON.
           return data["access_token"]
           # Donc en somme, quand cette fonction est appelée, elle renvoie le token qui permettra de faire des requêtes à l'API france travail

          
       # Gestion des exceptions liées aux problèmes de connexion.
       except requests.exceptions.ConnectionError:
           raise Exception("Impossible de se connecter au serveur d'authentification")
       # Gestion des exceptions liées aux délais d'attente dépassés lors de la requête.
       except requests.exceptions.Timeout:
           raise Exception("Délai d'attente dépassé lors de l'authentification")
       # Gestion des autres exceptions liées aux problèmes lors de l'envoi de la requête HTTP.
       except requests.exceptions.RequestException as e:
           raise Exception(f"Erreur lors de la requête d'authentification: {str(e)}")
       # Gestion des exceptions si la réponse du serveur n'est pas au format JSON attendu.
       except ValueError:
           raise Exception("Réponse non-JSON reçue")


   def get_communes(self):
       # Récupère la liste complète des communes françaises depuis l'API de France Travail.
       # Cette fonction est importante car l'API ne fonctionne qu'avec des codes INSEE (équivalent du code postal)
       # C'est à dire que l'url permettant de faire une requête, ne prend pas en compte les villes mais plutôt les code INSEE
       # Mais dans notre code, on souhaite que l'on puisse rentrer le nom d'une ville et non pas un code postal/INSEE
       # France travail offre la possibilité de récupérer tout les codes INSEE et leurs villes associées
       # Ce sera pratique car quand on rentrera le nom d'une ville, alors il ira chercher directement dans ce dictionnaire le code INSEE
       url = "https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/communes"
       # En-têtes de la requête HTTP, incluant le jeton d'autorisation et l'acceptation du format JSON.
       headers = {
           "Authorization": f"Bearer {self.token}",
           "Accept": "application/json"
       }
      
       try:
           # Envoi de la requête GET à l'URL spécifiée avec les en-têtes.
           response = requests.get(url, headers=headers)
          
           # Vérification du statut de la réponse HTTP. Si le code n'est pas 200 (OK), une exception est levée
           if response.status_code != 200:
               if response.status_code == 401:
                   raise Exception("Token d'authentification invalide ou expiré")
               else:
                   raise Exception(f"Erreur HTTP {response.status_code}: {response.text}")
                  
           # Si la requête est réussie, retourne les données JSON contenant la liste des communes.
           # C'est un dictionnaire, il contient toutes les villes/village, et leur code INSEE associé.
           return response.json()
          
       # Gestion des exceptions qui peuvent survenir lors de la requête HTTP.
       except requests.exceptions.RequestException as e:
           raise Exception(f"Erreur lors de la récupération des communes: {str(e)}")


   def find_commune_code(self, input_name):
        # Recherche un code de commune dans la liste des communes chargées, en tolérant les erreurs de frappe.
        # Exemple : on rentre Renne au lieu de Rennes, il va quand même prendre le code INSEE de Rennes
        # Retourne un dictionnaire contenant le nom corrigé et le code INSEE de la commune trouvée, ou None si aucune correspondance n'est trouvée.
       if not input_name or not isinstance(input_name, str):
           return None # Retourne None si l'entrée est vide ou n'est pas une chaîne de caractères.
      
       # Nettoie la saisie de l'utilisateur en la mettant en majuscules, en remplaçant les tirets par des espaces et en supprimant les espaces superflus
       # Car la structure du dictionnaire récupéré depuis france travail est comme ça, par exemple les villes sont en majuscules 
       # Ex : LILLE 
       # Et il n'y a pas de tirets
       # Ex : SAINT DENIS
       input_cleaned = input_name.upper().replace("-", " ").strip()
  
       try:
           # Extraction des noms de communes depuis la liste chargée (self.communes).
           noms_communes = [commune["libelle"] for commune in self.communes]
           # Recherche de la meilleure correspondance pour le nom de commune saisi en utilisant l'algorithme de comparaison de séquences de difflib.
           best_match = difflib.get_close_matches(input_cleaned, noms_communes, n=1, cutoff=0.6)


           # Si une correspondance est trouvée.
           if best_match:
               # Parcours de la liste des communes pour trouver celle qui correspond à la meilleure correspondance.
               for commune in self.communes:
                   if commune["libelle"] == best_match[0]:
                       # Retourne un dictionnaire contenant le nom corrigé et le code INSEE de la commune.
                       # Ce code INSEE sera ajouté à la requête plus tard, pour l'API
                       return {
                           "nom_corrige": best_match[0],
                           "code_insee": commune["code"]
                       }
           return None # Si aucune correspondance n'est trouvée, retourne None.
      
       # Gestion des exceptions qui pourraient survenir lors du processus de recherche.
       except Exception as e:
           print(f"Erreur lors de la recherche de code commune pour '{input_name}': {str(e)}")
           return None


   def determine_zone_recherche(self, ville_input):
        # L'inconvénient de l'API  de France travail est qu'il ne fonctionne pas si l'on tape juste Paris ou Lyon
        # Car ils ont un code INSEE différent pour chaque arrondissement. 
        # Dans le cas où l'on rentre Paris ou Lyon, alors l'url de requête n'utile plus le code INSEE mais le département, soit 75 ou 69


        # Détermine le type de zone de recherche (département ou commune) à partir de la saisie utilisateur.
        # Retourne un dictionnaire contenant le type de zone ('departement' ou 'commune'), sa valeur (code département ou code INSEE) et le nom corrigé de la ville.
        # Retourne None si la ville n'est pas trouvée.
       if not ville_input:
           return None # Retourne None si l'entrée de la ville est vide.
      
        # Dictionnaire associant certaines grandes villes à leur code département spécifique.
       villes_specifiques = {
           "PARIS": "75",
           "LYON": "69"
       }
  
       try:
           # Nettoie la saisie de l'utilisateur en la mettant en majuscules et en supprimant les espaces superflus.
           ville_upper = ville_input.upper().strip()
      
           # Vérifie si la ville saisie correspond à une entrée dans le dictionnaire des villes spécifiques.
           if ville_upper in villes_specifiques:
               return {
                   "type": "departement",
                   "valeur": villes_specifiques[ville_upper],
                   "nom_corrige": ville_upper
               }
           else:
               # Si la ville n'est pas dans le dictionnaire, tente de trouver des informations sur la commune via la méthode find_commune_code.
               commune_info = self.find_commune_code(ville_input)
               if commune_info:
                   return {
                       "type": "commune",
                       "valeur": commune_info["code_insee"],
                       "nom_corrige": commune_info["nom_corrige"]
                   }
               return None
              
       # Gestion des erreurs potentielles lors du traitement de la saisie ou de la recherche de la commune.
       except Exception as e:
           print(f"Erreur lors de la détermination de la zone pour '{ville_input}': {str(e)}")
           return None


   def search_offres(self, zone_type, zone_code, mots_cles):
       # Effectue une recherche d'offres d'emploi auprès de l'API France Travail en fonction du type et du code de la zone géographique et des mots-clés.
       # Retourne les résultats bruts de l'API au format JSON.
       # Lève une ValueError si le type de zone est invalide ou si le code de zone est manquant.
       if not zone_type or zone_type not in ["commune", "departement"]:
           raise ValueError(f"Type de zone invalide: {zone_type}")
          
       if not zone_code:
           raise ValueError("Code de zone obligatoire")
          
       # URL de l'API de recherche d'offres d'emploi.
       url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
       # Paramètres de la requête à envoyer à l'API.
       params = {
           "motsCles": mots_cles,       # Voir plus bas
           "distance": "40",            # Par défaut 40 pour avoir un rayon large
           "sort": "0",                 # Trie par pertinence
           "offresPartenaires": "true"  # Inclue à la fois les offres France travail, et des partenaires
       }


       # Ajout du paramètre de filtre géographique en fonction du type de zone.
       # Typiquement les paramètres de l'URL change pour être département, si Paris et Lyon a été saisis
       if zone_type == "commune":
           params["commune"] = zone_code
       elif zone_type == "departement":
           params["departement"] = zone_code


       # En-têtes de la requête HTTP, incluant le jeton d'autorisation et l'acceptation du format JSON.
       headers = {
           "Authorization": f"Bearer {self.token}",
           "Accept": "application/json"
       }
      
       try:
           # Envoi de la requête GET à l'API avec les paramètres et les en-têtes.
           response = requests.get(url, headers=headers, params=params)
          
           # Vérification du statut de la réponse HTTP. Lève une exception en cas d'erreur.
           if response.status_code != 200:
               if response.status_code == 401:
                   raise Exception("Token d'authentification expiré")
               elif response.status_code == 404:
                   raise Exception("Ressource non trouvée")
               elif response.status_code == 429:
                   raise Exception("Trop de requêtes. Veuillez réessayer plus tard")
               else:
                   raise Exception(f"Erreur HTTP {response.status_code}: {response.text}")
                  
           # Si la requête est réussie, retourne les données JSON de la réponse.
           return response.json()
          
       # Gestion des exceptions liées aux problèmes de connexion, aux délais d'attente ou aux erreurs réseau lors de la requête.
       except requests.exceptions.ConnectionError:
           raise Exception("Impossible de se connecter au serveur")
       except requests.exceptions.Timeout:
           raise Exception("Délai d'attente dépassé")
       except requests.exceptions.RequestException as e:
           raise Exception(f"Erreur réseau: {str(e)}")


   def nettoyer_description(self, description):
        # Nettoie le texte de la description d'une offre d'emploi en supprimant les sauts de ligne, les espaces multiples et les espaces avant la ponctuation.
        # Retourne la description nettoyée. Si la description est vide, retourne un message indiquant l'absence de description
       if not description:
           return "Aucune description disponible."
          
       # Remplace les sauts de ligne par un espace
       cleaned = re.sub(r'\n', ' ', description)
      
       # Remplace les espaces multiples par un seul
       cleaned = re.sub(r'\s+', ' ', cleaned)
      
       # Enlève les espaces avant la ponctuation
       cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
      
       # Supprime les espaces en début et fin de chaîne et retourne le résultat.
       return cleaned.strip()


   def recherche_offres(self, ville_input, mots_cles):
       # Recherche des offres d'emploi en fonction de la ville et des mots-clés fournis.
       # Utilise les méthodes determine_zone_recherche et search_offres pour effectuer la requête à l'API.
       # Formate et retourne les résultats de manière structurée, incluant des informations sur la ville recherchée et la liste des offres.
       # Gère les erreurs potentielles, y compris les problèmes de connexion, les erreurs d'API et l'expiration du token d'authentification (avec une tentative de renouvellement)
       try:
           if not ville_input:
               return {"erreur": "Ville obligatoire"}
              
           if not mots_cles:
               print("Avertissement: recherche sans mots-clés")
              
           # Détermine la zone de recherche (commune ou département) à partir de la ville saisie.
           zone = self.determine_zone_recherche(ville_input)
           if not zone:
               return {"erreur": "Commune introuvable. Vérifiez l'orthographe."}


           try:
               # Effectue la recherche d'offres d'emploi via l'API.
               offres = self.search_offres(zone["type"], zone["valeur"], mots_cles)
              
               # Vérifie si des résultats ont été trouvés.
               if not offres.get("resultats"):
                   return {"message": f"Aucune offre trouvée pour '{mots_cles}' à {zone['nom_corrige']}."}


               # Liste pour stocker les informations formatées des offres.
               resultats_utiles = []
               # Parcours les résultats bruts de l'API pour extraire et formater les informations pertinentes.
               for offre in offres["resultats"]:
                   try:
                       resultat = {
                           "titre": offre.get("intitule", "Titre non renseigné"),
                           "entreprise": offre.get("entreprise", {}).get("nom", "Entreprise non précisée"),
                           "lieu": offre.get("lieuTravail", {}).get("libelle", "Lieu non précisé"),
                           "contrat": offre.get("typeContratLibelle", "Type de contrat non précisé"),
                           "description": self.nettoyer_description(offre.get("description"))
                       }
                       resultats_utiles.append(resultat)
                   except Exception as e:
                       print(f"Erreur sur une offre: {str(e)}")  # Affiche une erreur si le traitement d'une offre échoue.
                       continue # Passe à l'offre suivante en cas d'erreur.


               # Retourne un dictionnaire contenant des informations sur la recherche et la liste des offres formatées
               return {
                   "ville": zone["nom_corrige"],
                   "nombre_offres": len(resultats_utiles),
                   "offres": resultats_utiles
               }
              
            # Gestion des erreurs spécifiques liées à la requête d'offres (y compris l'expiration du token).
           except Exception as e:
               if "Token d'authentification expiré" in str(e):
                   print("Token expiré. Tentative de renouvellement...")
                   try:
                       self.token = self.get_token() # Tente de renouveler le token.
                       return self.recherche_offres(ville_input, mots_cles)  # Réessaie la recherche avec le nouveau token.
                   except Exception as token_error:
                       return {"erreur": f"Impossible de renouveler le token: {str(token_error)}"}  # Retourne une erreur si le renouvellement du token échoue.
               else:
                   return {"erreur": f"Erreur lors de la recherche: {str(e)}"} # Retourne une erreur générique si la recherche échoue


       # Gestion des erreurs de connexion réseau.
       except requests.exceptions.RequestException as e:
           return {"erreur": f"Problème de connexion: {str(e)}"}
          
       # Gestion des erreurs inattendues.
       except Exception as e:
           return {"erreur": f"Erreur inattendue: {str(e)}"}


# Exemple d'utilisation de la classe FranceTravailAPI en ligne de commande.
# Cette section s'exécute uniquement lorsque le script est lancé directement
if __name__ == "__main__":
   try:
       # Initialisation de l'objet FranceTravailAPI. Assurez-vous que les identifiants client sont correctement configurés.
       api = FranceTravailAPI()
       # Invite l'utilisateur à entrer le nom de la ville pour la recherche.
       ville = input("Entrez le nom de la ville : ")
       # Invite l'utilisateur à entrer les mots-clés de l'offre d'emploi recherchée.
       # La particularité est que l'on peut rentrer soit le nom d'un métier : 
       # Ex : Data analyst
       # Ou soit vraiment un mot clé 
       # Ex : Python, Data, ...
       mots_cles = input("Entrez les mots-clés de l'offre : ")
      
       # Appel de la méthode recherche_offres pour obtenir les résultats.
       # Tous les résultats sont stockés dans resultats, il s'agit d'un dictionnaire
       # Cela permet une manipulation facile des données en fonction de ce que vous voulez faire dans discord
       resultats = api.recherche_offres(ville, mots_cles)
      
       # Vérification si la réponse contient une clé 'erreur', indiquant un problème lors de la recherche.
       if "erreur" in resultats:
           print(f"Erreur : {resultats['erreur']}")
       # Vérification si la réponse contient une clé 'message', indiquant par exemple l'absence d'offres.
       elif "message" in resultats:
           print(resultats["message"])
       # Si aucune erreur ou message spécifique, affichage des résultats de la recherche.
       else:
           print(f"\nRésultats pour '{mots_cles}' à {resultats['ville']} ({resultats['nombre_offres']} offres trouvées) :\n")
          
           # Parcours de la liste des offres trouvées et affichage des informations principales.
           for i, offre in enumerate(resultats["offres"], 1):
               print(f"Offre {i}/{resultats['nombre_offres']}:")
               print(f"Titre: {offre['titre']}")
               print(f"Entreprise: {offre['entreprise']}")
               print(f"Lieu: {offre['lieu']}")
               print(f"Contrat: {offre['contrat']}")
               print(f"Description:\n{offre['description']}")
               print("\n" + "-"*50 + "\n")
   # Gestion des erreurs qui pourraient survenir lors de l'initialisation de l'API (par exemple, si les identifiants sont incorrects).
   except Exception as e:
       print(f"Erreur d'initialisation de l'API: {str(e)}")
       print("Vérifiez que vous avez bien renseigné votre client_id et client_secret.")

#pour bien voir la structure du dictionnaire
pprint.pprint(resultats)