#!/usr/bin/env python3
"""
Test simple pour l'API de statistiques
"""

import requests
import json

def test_statistics_api():
    # Test des sources disponibles
    print("1. Récupération des sources de données...")
    sources_response = requests.get("http://localhost:8000/api/v1/data-sources/")
    
    if sources_response.status_code == 200:
        sources = sources_response.json()
        print(f"✅ Trouvé {len(sources)} sources de données")
        
        # Tester la première source avec des données
        for source in sources:
            print(f"\n2. Test des statistiques pour la source: {source['name']} (ID: {source['id']})")
            
            stats_response = requests.get(f"http://localhost:8000/api/v1/statistics/data-sources/{source['id']}/statistics")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ Statistiques récupérées pour {source['name']}")
                print(f"   - Lignes: {stats.get('total_rows', 'N/A')}")
                print(f"   - Colonnes: {len(stats.get('columns', []))}")
                print(f"   - Erreurs: {stats.get('error', 'Aucune')}")
                break
            else:
                print(f"❌ Erreur {stats_response.status_code} pour {source['name']}")
                print(f"   Réponse: {stats_response.text}")
    else:
        print(f"❌ Erreur lors de la récupération des sources: {sources_response.status_code}")

if __name__ == "__main__":
    test_statistics_api()