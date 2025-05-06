def scrape_indeed(keywords, location=None):
    try:
        from jobspy import scrape_jobs
        import pandas as pd
        import time
        
        print(f"Recherche d'offres Indeed pour '{keywords}' à '{location or 'France'}'")
        
        # Utilisation directe de jobspy pour plus de fiabilité
        jobs = scrape_jobs(
            site_name=["indeed"],
            search_term=keywords,
            location=location or "France",
            results_wanted=30,
            hours_old=72,
            country_indeed='France'
        )
        
        if jobs.empty:
            print("Aucun résultat trouvé sur Indeed")
            return []
            
        # Nettoyer et formater les résultats
        formatted_results = []
        for _, job in jobs.iterrows():
            try:
                # Extraction des valeurs avec gestion des valeurs manquantes
                title = str(job.get("title", "")) if job.get("title") is not None else ""
                company = str(job.get("company", "")) if job.get("company") is not None else ""
                location = str(job.get("location", "")) if job.get("location") is not None else ""
                url = str(job.get("job_url", "")) if job.get("job_url") is not None else ""
                
                # Vérification de l'URL
                if not url or not isinstance(url, str) or not url.startswith("http"):
                    continue
                    
                formatted_results.append({
                    "titre": title,
                    "entreprise": company,
                    "lieu": location,
                    "url": url.strip()
                })
            except Exception as e:
                print(f"Erreur avec une offre Indeed : {e}")
                continue
                
        print(f"Récupération de {len(formatted_results)} offres Indeed")
        return formatted_results
        
    except Exception as e:
        print(f"Erreur scraping Indeed : {e}")
        import traceback
        traceback.print_exc()
        return []