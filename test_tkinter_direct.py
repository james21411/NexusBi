#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test direct pour l'interface tkinter
Teste l'affichage de la fenêtre sans passer par le backend
"""

import sys
import os

# Ajouter le répertoire courant au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_preview_tkinter import DataPreviewTkinter

def test_tkinter_window():
    """Test direct de la fenêtre tkinter"""
    print("🧪 Test direct de l'interface tkinter")
    print("🖥️ Configuration de l'affichage...")
    
    # Configuration de l'affichage
    os.environ['DISPLAY'] = ':0'
    
    try:
        print("🛠️ Création de l'interface DataPreviewTkinter...")
        
        # Créer l'interface avec des données de test
        app = DataPreviewTkinter(
            data_source_id=None,  # Pas de data source pour le test
            api_base_url="http://localhost:8000",
            auth_token=None
        )
        
        print("✅ Interface créée avec succès")
        print("🎯 Ajout de données de test...")
        
        # Ajouter des données de test
        test_data = [
            {"Nom": "Alice", "Âge": 25, "Ville": "Paris", "Statut": "Active"},
            {"Nom": "Bob", "Âge": 30, "Ville": "Lyon", "Statut": ""},  # Valeur manquante
            {"Nom": "Charlie", "Âge": None, "Ville": "Marseille", "Statut": "Active"},
            {"Nom": "Diana", "Âge": 28, "Ville": "Toulouse", "Statut": "Inactive"},
            {"Nom": "Eve", "Âge": 22, "Ville": "", "Statut": "Active"},  # Valeur manquante
        ]
        
        app.data = test_data
        app.total_rows = len(test_data)
        app.visible_columns = list(test_data[0].keys())  # Toutes les colonnes
        
        print("📊 Données de test ajoutées")
        print("🔄 Mise à jour de l'affichage...")
        
        # Forcer la mise à jour de l'affichage
        app.update_display()
        
        print("✅ Affichage mis à jour")
        print("🚀 Lancement de la fenêtre...")
        print("📱 Vérification de la visibilité de la fenêtre...")
        
        # Vérifier que la fenêtre est créée et visible
        if hasattr(app, 'root') and app.root:
            print(f"✅ Fenêtre créée: {app.root.title()}")
            print(f"📐 Taille: {app.root.geometry()}")
            print(f"🔍 État de visibilité: {app.root.state()}")
            
            # Mettre la fenêtre au premier plan
            app.root.lift()
            app.root.attributes('-topmost', True)
            app.root.update()
            
            print("🎯 Fenêtre mise au premier plan")
            print("⏳ Lancement de mainloop dans 3 secondes...")
            
            # Attendre un peu puis lancer
            import time
            time.sleep(3)
            
            print("▶️ Lancement de mainloop...")
            app.run()
            
        else:
            print("❌ ERREUR: La fenêtre n'a pas été créée correctement!")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🔬 Démarrage du test tkinter direct")
    success = test_tkinter_window()
    if success:
        print("✅ Test terminé avec succès")
    else:
        print("❌ Test échoué")
    sys.exit(0 if success else 1)