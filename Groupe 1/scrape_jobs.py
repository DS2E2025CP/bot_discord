import discord
from discord import app_commands
from discord.ext import commands
import logging
import traceback
from utils.helper import get_user_data
from scrape_jobs_g3 import scrape_indeed
from scrape_stages import scrape_stages_indeed

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('job_search.log'), logging.StreamHandler()]
)

class OffreSelectionView(discord.ui.View):
    def __init__(self, offres):
        super().__init__(timeout=300)  # Timeout de 5 minutes
        self.offres = offres
        
        # Ne pas créer de sélecteur si la liste est vide
        if not offres:
            logging.warning("Tentative de création d'un sélecteur avec une liste d'offres vide")
            return
            
        # Vérifier que nous n'avons pas trop d'options (max 25 pour Discord)
        if len(offres) > 25:
            logging.warning(f"Trop d'offres pour un seul sélecteur ({len(offres)}), limitation à 25")
            self.offres = offres[:25]
            
        select = OffreSelect(self.offres)
        self.add_item(select)
        
    async def on_timeout(self):
        # Désactiver les composants après le timeout
        for item in self.children:
            item.disabled = True

class OffreSelect(discord.ui.Select):
    def __init__(self, offres):
        # Créer les options du menu déroulant en s'assurant qu'elles ne dépassent pas 100 caractères
        options = []
        for i, offre in enumerate(offres):
            titre = offre.get('titre', 'Sans titre')
            entreprise = offre.get('entreprise', 'Entreprise inconnue')
            # Tronquer le titre et l'entreprise pour rester dans la limite de 100 caractères
            label = f"{i+1}. {titre} - {entreprise}"
            if len(label) > 97:  # 97 pour laisser place aux "..."
                label = label[:97] + "..."
            options.append(discord.SelectOption(label=label, value=str(i)))

        super().__init__(placeholder="Sélectionner une offre pour l'analyser", options=options)

    async def callback(self, interaction: discord.Interaction):
        # CORRECTION: Différer la réponse immédiatement pour éviter l'expiration du webhook
        await interaction.response.defer(ephemeral=True)
        
        try:
            index = int(self.values[0])
            offre = self.view.offres[index]
            
            # Créer une copie de l'offre pour éviter les problèmes de référence
            offre_copy = dict(offre)
            
            user = get_user_data(interaction.user.id)
            user.job_offer = offre_copy
            
            # Journalisation de la sélection d'offre
            logging.info(f"Offre sélectionnée par {interaction.user.name}: {offre['titre']} - {offre['entreprise']}")

            embed = discord.Embed(
                title="Offre sélectionnée",
                description=(
                    f"Vous avez sélectionné: {offre['titre']} - {offre['entreprise']}\n"
                    f"Pour comparer avec votre CV, utilisez la commande `/comparer_cv_offre`\n"
                    f"Pour générer une lettre de motivation, utilisez `/generer_lettre`"
                ),
                color=discord.Color.green()
            )
            
            # Ajouter l'URL si disponible
            if "url" in offre and offre["url"]:
                embed.add_field(name="Lien vers l'annonce", value=f"[Voir l'offre]({offre['url']})", inline=False)
                
            # Utiliser followup.send car nous avons déjà utilisé defer
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Erreur lors de la sélection d'offre: {e}")
            traceback.print_exc()
            try:
                await interaction.followup.send("Une erreur est survenue lors de la sélection de l'offre.")
            except:
                logging.error("Impossible d'envoyer le message d'erreur via followup")

def setup_scrape_command(bot):
    @bot.tree.command(name="scrape", description="Rechercher des offres d'emploi")
    async def scrape(interaction: discord.Interaction, termes: str, lieu: str = None):
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

        try:
            logging.info(f"Recherche d'offres pour '{termes}' à '{lieu or 'Paris'}'")
            
            # France Travail
            try:
                from scraping_group2 import FranceTravailAPI
                api = FranceTravailAPI()
                resultats = api.recherche_offres(ville_input=lieu or "Paris", mots_cles=termes)
                logging.info(f"Résultats France Travail: {len(resultats.get('offres', []))} offres trouvées")
                
                if "erreur" in resultats:
                    logging.warning(f"Erreur France Travail: {resultats['erreur']}")
                    resultats = {"offres": [], "ville": lieu or "non précisée"}
            except Exception as e:
                logging.error(f"❌ Erreur API France Travail : {e}")
                traceback.print_exc()
                resultats = {"offres": [], "ville": lieu or "non précisée"}

            offres_ft = resultats.get("offres", [])[:15]
            for offre in offres_ft:
                offre["source"] = "France Travail"
                # Vérifier si l'URL est présente
                if "url" not in offre:
                    offre["url"] = "https://francetravail.io"

            # Indeed
            try:
                offres_indeed = scrape_indeed(termes, lieu)
                logging.info(f"Résultats Indeed: {len(offres_indeed)} offres trouvées")
            except Exception as e:
                logging.error(f"❌ Erreur Indeed: {e}")
                traceback.print_exc()
                offres_indeed = []

            for offre in offres_indeed:
                offre["source"] = "Indeed"

            offres = offres_ft + offres_indeed

            if not offres:
                await interaction.followup.send("❌ Aucune offre trouvée pour ces critères.")
                return

            embed = discord.Embed(
                title=f"Offres d'emploi pour '{termes}'",
                description=f"Résultats pour {resultats.get('ville', lieu or 'non précisé')} - {len(offres)} offres trouvées",
                color=discord.Color.blue()
            )

            total_chars = len(embed.title) + len(embed.description)
            max_fields = 0

            for i, offre in enumerate(offres):
                titre = f"{i+1}. {offre.get('titre', 'Sans titre')} - {offre.get('entreprise', 'Entreprise inconnue')}"
                if len(titre) > 256:
                    titre = titre[:253] + "..."

                url = offre.get('url', '')
                if not isinstance(url, str) or not url.startswith("http"):
                    url = "https://example.com"
                else:
                    url = url.strip().replace(" ", "%20")

                description = (
                    f"📍 {offre.get('lieu', 'Inconnu')}\n"
                    f"🔗 [Voir l'annonce]({url})\n"
                    f"📰 Source : {offre.get('source', 'Inconnue')}"
                )

                if len(description) > 1024:
                    description = description[:1021] + "..."

                if total_chars + len(titre) + len(description) > 5800 or max_fields >= 25:
                    break

                embed.add_field(name=titre, value=description, inline=False)
                total_chars += len(titre) + len(description)
                max_fields += 1

            if max_fields < len(offres):
                embed.set_footer(text=f"⚠️ {len(offres) - max_fields} offres non affichées (limite Discord atteinte)")

            view = OffreSelectionView(offres[:max_fields])
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            logging.error(f"Erreur lors du scraping: {e}")
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ Une erreur est survenue : {str(e)[:1900]}",
                ephemeral=True
            )

    @bot.tree.command(name="scrape_stage", description="Rechercher des offres de stage (Indeed)")
    async def scrape_stage(interaction: discord.Interaction, lieu: str = "Paris"):
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

        try:
            logging.info(f"Recherche de stages à {lieu}")
            
            # Utilisation du scraping amélioré pour les stages
            offres_df = scrape_stages_indeed(location=lieu, max_results=20)
            
            if offres_df.empty:
                await interaction.followup.send(f"❌ Aucun stage trouvé à {lieu}.")
                return
            
            # Conversion du DataFrame en liste de dictionnaires
            offres_dict = []
            for _, row in offres_df.iterrows():
                offres_dict.append({
                    "titre": row.get("job_title", ""),
                    "entreprise": row.get("company", ""),
                    "lieu": row.get("location", ""),
                    "url": row.get("link", ""),
                    "source": "Indeed"
                })
                
            if not offres_dict:
                await interaction.followup.send(f"❌ Aucun stage trouvé à {lieu} après traitement.")
                return

            embed = discord.Embed(
                title=f"Offres de stage à {lieu}",
                description=f"{len(offres_dict)} résultats trouvés",
                color=discord.Color.orange()
            )

            max_fields = 0
            total_chars = len(embed.title) + len(embed.description)

            for i, offre in enumerate(offres_dict):
                titre = f"{i+1}. {offre.get('titre', 'Sans titre')} - {offre.get('entreprise', 'Entreprise inconnue')}"
                
                if len(titre) > 256:
                    titre = titre[:253] + "..."
                    
                url = offre.get('url', '')
                if not isinstance(url, str) or not url.startswith("http"):
                    url = "https://fr.indeed.com"
                else:
                    url = url.strip().replace(" ", "%20")

                description = (
                    f"📍 {offre.get('lieu', 'Inconnu')}\n"
                    f"🔗 [Voir l'annonce]({url})\n"
                    f"📰 Source : Indeed"
                )

                if len(description) > 1024:
                    description = description[:1021] + "..."

                if total_chars + len(titre) + len(description) > 5800 or max_fields >= 25:
                    break

                embed.add_field(name=titre, value=description, inline=False)
                total_chars += len(titre) + len(description)
                max_fields += 1

            if max_fields < len(offres_dict):
                embed.set_footer(text=f"⚠️ {len(offres_dict) - max_fields} offres non affichées (limite Discord atteinte)")

            view = OffreSelectionView(offres_dict[:max_fields])
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            logging.error(f"Erreur lors du scraping de stage: {e}")
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ Une erreur est survenue : {str(e)[:1900]}",
                ephemeral=True
            )