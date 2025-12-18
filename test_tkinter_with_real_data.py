#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test direct de l'interface tkinter avec les vraies données API
Vérifie si tkinter peut récupérer et afficher les données SQL dump
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

def test_tkinter_with_api_data():
    """Test tkinter avec les vraies données de l'API"""
    print("🧪 === TEST TKINTER AVEC DONNÉES RÉELLES ===")
    
    try:
        # Récupérer les données depuis l'API
        print("📡 Récupération des données depuis l'API...")
        response = requests.get("http://localhost:8000/api/v1/preview/preview-data/1", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return
        
        api_data = response.json()
        rows = api_data.get('rows', [])
        total_rows = api_data.get('total_rows', 0)
        source_name = api_data.get('data_source_name', 'Inconnu')
        
        print(f"✅ Données récupérées: {len(rows)} lignes de {total_rows} total")
        print(f"📊 Source: {source_name}")
        
        if not rows:
            print("❌ Aucune donnée récupérée!")
            return
        
        # Créer l'interface tkinter
        print("🖼️ Création de l'interface tkinter...")
        
        root = tk.Tk()
        root.title(f"Test tkinter - {source_name}")
        root.geometry("1200x800")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text=f"Données: {source_name}", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text=f"Affichage de {len(rows)} lignes sur {total_rows} total",
                              font=("Arial", 10))
        info_label.pack(pady=(0, 10))
        
        # Treeview pour afficher les données
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Créer le treeview
        tree = ttk.Treeview(tree_frame)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Configurer les colonnes
        if rows:
            columns = list(rows[0].keys())
            tree['columns'] = columns
            tree['show'] = 'headings'
            
            # Configurer les en-têtes
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, minwidth=50)
            
            # Insérer les données
            print(f"📊 Insertion de {len(rows)} lignes dans le Treeview...")
            for i, row in enumerate(rows):
                values = [str(row.get(col, '')) for col in columns]
                tree.insert('', tk.END, text=str(i+1), values=values)
            
            print(f"✅ {len(rows)} lignes insérées dans l'interface")
        else:
            tree['columns'] = ('Message',)
            tree.heading('Message', text='Message')
            tree.insert('', tk.END, values=('Aucune donnée à afficher',))
        
        # Bouton de fermeture
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Fermer", 
                  command=root.destroy, 
                  style="Accent.TButton").pack()
        
        # Message de succès
        success_label = ttk.Label(main_frame, 
                                 text=f"✅ Interface créée avec succès! {len(rows)} lignes affichées",
                                 foreground="green")
        success_label.pack(pady=5)
        
        print("🎯 Interface tkinter lancée - Vérifiez qu'elle s'affiche!")
        print("💡 Si vous voyez une fenêtre avec des données, le problème est résolu!")
        
        # Lancer la boucle principale
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

def test_data_parsing():
    """Test le parsing des données pour voir leur structure"""
    print(f"\n🔍 === ANALYSE DES DONNÉES ===")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/preview/preview-data/1", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get('rows', [])
            
            if rows:
                print(f"✅ {len(rows)} lignes trouvées")
                
                # Analyser la première ligne
                first_row = rows[0]
                print(f"\n📋 Structure de la première ligne:")
                for key, value in first_row.items():
                    print(f"   {key}: {value} ({type(value).__name__})")
                
                # Analyser les colonnes
                columns = list(first_row.keys())
                print(f"\n📊 Colonnes trouvées: {columns}")
                
                # Sauvegarder les données pour inspection
                with open('api_data_inspection.json', 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Données sauvegardées dans: api_data_inspection.json")
                
            else:
                print("❌ Aucune ligne dans les données")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")

def main():
    """Fonction principale"""
    print("🧪 TEST TKINTER AVEC DONNÉES RÉELLES")
    print("Ce script teste si tkinter peut afficher les vraies données API")
    print("=" * 60)
    
    # 1. Analyser les données
    test_data_parsing()
    
    # 2. Test tkinter
    test_tkinter_with_api_data()
    
    print(f"\n" + "=" * 60)
    print("🏁 TEST TERMINÉ")
    print(f"\n💡 Si tkinter affiche les données:")
    print(f"   ✅ Le problème était dans le chargement automatique")
    print(f"   ✅ L'interface fonctionne, il faut ajuster la synchronisation")
    print(f"\n💡 Si tkinter n'affiche pas les données:")
    print(f"   ❌ Problème dans l'interface tkinter elle-même")
    print(f"   ❌ Problème dans la récupération des données")

if __name__ == "__main__":
    main()