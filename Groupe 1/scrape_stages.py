import pandas as pd
import logging
import traceback

def scrape_stages_indeed(location: str, max_results: int = 30):
    """
    Scrape des offres de stage sur Indeed pour une ville donnée en utilisant jobspy.
    
    :param location: Ville cible (ex: "lyon")
    :param max_results: Nombre maximum d'offres à récupérer
    :return: DataFrame contenant les offres de stage
    """
    try:
        print(f"Recherche de stages à {location} via jobspy")
        
        from jobspy import scrape_jobs
        
        # Utilisation de jobspy pour une recherche fiable
        search_term = "stage data"
        
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=search_term,
            location=location,
            results_wanted=max_results,
            hours_old=96,  # Les 4 derniers jours
            country_indeed='France'
        )
        
        # Si aucun résultat n'est retourné
        if jobs.empty:
            print(f"Aucun stage trouvé à {location}")
            return pd.DataFrame()
            
        # Filtrer uniquement les stages
        stages = jobs[jobs['title'].str.contains('stage|intern|alternance|stagiaire', case=False, na=False)]
        
        if stages.empty:
            # Si aucun stage n'a été trouvé après filtrage, essayer une recherche plus spécifique
            print(f"Aucun stage trouvé parmi les {len(jobs)} offres à {location}, tentative avec un terme plus spécifique")
            
            jobs = scrape_jobs(
                site_name=["indeed"],
                search_term="stage",
                location=location,
                results_wanted=max_results,
                hours_old=168,  # La dernière semaine
                country_indeed='France'
            )
            
            if jobs.empty:
                print(f"Aucun stage trouvé avec la recherche spécifique à {location}")
                return pd.DataFrame()
                
            stages = jobs
            
        # Préparation des résultats
        results = []
        for _, job in stages.iterrows():
            results.append({
                "job_title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "link": job.get("job_url", "")
            })
            
        print(f"Récupération de {len(results)} stages à {location}")
        return pd.DataFrame(results)
        
    except Exception as e:
        print(f"Erreur lors du scraping de stages Indeed: {e}")
        traceback.print_exc()
        return pd.DataFrame()