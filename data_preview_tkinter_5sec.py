#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface tkinter pour prévisualiser les données - VERSION 5 SECONDES
Reste ouverte exactement 5 secondes puis se ferme automatiquement
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from typing import List, Dict, Any, Optional
import threading
import os
import time
from datetime import datetime
import traceback


class DataPreviewTkinter5Seconds:
    def __init__(self, data_source_id: int = None, api_base_url: str = "http://localhost:8000", auth_token: str = None):
        self.data_source_id = data_source_id
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.data = []
        self.total_rows = 0
        self.schema = None
        self.data_source = None
        self.window_created = False
        self.initialization_error = None
        self.start_time = None
        
        # Configuration de l'affichage
        self.display_mode = "first"
        self.row_count = 50
        self.start_row = 0
        self.end_row = 49
        self.search_term = ""
        self.visible_columns = []
        
        print("🔄 Initialisation de l'interface tkinter (5 secondes)")
        
        try:
            self.setup_ui()
            if not self.window_created:
                raise Exception("La fenêtre n'a pas pu être créée")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ Erreur lors de l'initialisation: {e}")
            self.create_fallback_interface()
    
    def setup_ui(self):
        """Configure l'interface utilisateur tkinter"""
        print("🔧 Création de la fenêtre tkinter...")
        
        try:
            self.root = tk.Tk()
            self.root.title("Prévisualisation des Données - 5 secondes")
            self.root.geometry("1000x600")
            self.root.minsize(600, 400)
            
            # Empêcher la fermeture manuelle
            self.root.protocol("WM_DELETE_WINDOW", self.ignore_close)
            
            # Empêcher le redimensionnement pour éviter les bugs
            self.root.resizable(False, False)
            
            print("✅ Objet Tk() créé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur création Tk(): {e}")
            raise e
        
        try:
            # Configuration du style
            style = ttk.Style()
            style.theme_use('clam')
            
            style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#0056D2')
            style.configure('Timer.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#FF4500')
            style.configure('Status.TLabel', font=('Segoe UI', 10), foreground='#666666')
            style.configure('Treeview', background='#f9f9f9', foreground='black', fieldbackground='#f9f9f9')
            style.map('Treeview', background=[('selected', '#4a6baf')], foreground=[('selected', 'white')])
            
            print("✅ Style configuré")
            
        except Exception as e:
            print(f"⚠️ Erreur configuration style: {e}")
        
        try:
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Titre avec timer
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X, pady=(0, 15))
            
            self.title_label = ttk.Label(
                title_frame,
                text="Prévisualisation des Données - NexusBi",
                style='Title.TLabel'
            )
            self.title_label.pack(side=tk.LEFT)
            
            # Timer
            self.timer_label = ttk.Label(
                title_frame,
                text="5.0s",
                style='Timer.TLabel'
            )
            self.timer_label.pack(side=tk.RIGHT)
            
            print("✅ Titre et timer créés")
            
        except Exception as e:
            print(f"❌ Erreur création titre: {e}")
            raise e
        
        try:
            # Info frame
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.info_label = ttk.Label(
                info_frame,
                text="Interface en cours d'initialisation...",
                style='Status.TLabel'
            )
            self.info_label.pack(side=tk.LEFT)
            
            # Boutons (désactivés)
            button_frame = ttk.Frame(info_frame)
            button_frame.pack(side=tk.RIGHT)
            
            ttk.Button(button_frame, text="Actualiser", state="disabled").pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Exporter", state="disabled").pack(side=tk.LEFT)
            
            print("✅ Info et boutons créés")
            
        except Exception as e:
            print(f"❌ Erreur création info: {e}")
            raise e
        
        try:
            # Frame du tableau
            table_frame = ttk.LabelFrame(main_frame, text="Données", padding="10")
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            # Treeview
            self.tree = ttk.Treeview(table_frame, height=15)
            self.tree.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.configure(yscrollcommand=scrollbar.set)
            
            # Configuration des couleurs
            self.tree.tag_configure('even_row', background='#f0f8ff')
            self.tree.tag_configure('odd_row', background='#ffffff')
            self.tree.tag_configure('loading', background='#fffacd')
            
            print("✅ Tableau créé")
            
        except Exception as e:
            print(f"❌ Erreur création tableau: {e}")
            raise e
        
        try:
            # Frame de statut
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill=tk.X, pady=(10, 0))
            
            self.status_label = ttk.Label(status_frame, text="Prêt", relief=tk.SUNKEN)
            self.status_label.pack(fill=tk.X)
            
            print("✅ Statut créé")
            
        except Exception as e:
            print(f"❌ Erreur création statut: {e}")
            raise e
        
        try:
            print("✅ Interface créée avec succès")
            
            # Démarrer le timer
            self.start_time = time.time()
            self.update_timer()
            
            # Charger les données si data_source_id est fourni
            if self.data_source_id:
                self.load_data()
            else:
                self.show_welcome_message()
            
            self.window_created = True
            
        except Exception as e:
            print(f"❌ Erreur finalisation interface: {e}")
            raise e
    
    def create_fallback_interface(self):
        """Interface de fallback en cas d'erreur"""
        print("🔧 Création d'une interface de fallback...")
        
        try:
            self.root = tk.Tk()
            self.root.title("Interface tkinter - Mode Dépannage")
            self.root.geometry("600x400")
            
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Timer pour cette interface aussi
            self.start_time = time.time()
            self.timer_label = ttk.Label(main_frame, text="5.0s", font=('Arial', 20, 'bold'), foreground='red')
            self.timer_label.pack(pady=10)
            
            # Message d'erreur
            error_text = f"""
Erreur lors de l'initialisation:

{self.initialization_error}

Interface de dépannage activée.

Configuration:
- DISPLAY: {os.getenv('DISPLAY', 'Non définie')}
- Utilisateur: {os.getenv('USER', 'inconnu')}
- Time: {datetime.now().strftime('%H:%M:%S')}
            """
            
            error_label = ttk.Label(main_frame, text=error_text, justify=tk.LEFT)
            error_label.pack(pady=10)
            
            self.window_created = True
            self.update_timer()
            
        except Exception as e:
            print(f"❌ Erreur création fallback: {e}")
    
    def update_timer(self):
        """Met à jour le timer et gère la fermeture automatique"""
        if not self.start_time:
            return
        
        elapsed = time.time() - self.start_time
        remaining = max(0, 5.0 - elapsed)
        
        # Mettre à jour l'affichage du timer
        try:
            if hasattr(self, 'timer_label'):
                self.timer_label.config(text=f"{remaining:.1f}s")
            
            # Mettre à jour la couleur selon le temps restant
            if remaining <= 1.0:
                if hasattr(self, 'timer_label'):
                    self.timer_label.config(foreground='red')
            elif remaining <= 2.0:
                if hasattr(self, 'timer_label'):
                    self.timer_label.config(foreground='orange')
        except:
            pass  # Ignorer les erreurs d'affichage
        
        if remaining > 0:
            # Continuer le timer
            self.root.after(100, self.update_timer)
        else:
            # Temps écoulé - fermer automatiquement
            self.auto_close()
    
    def auto_close(self):
        """Fermeture automatique après 5 secondes"""
        print("⏰ 5 secondes écoulées - Fermeture automatique...")
        
        try:
            # Mettre à jour l'interface
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Fermeture automatique dans 0.5 secondes...")
            
            # Attendre 0.5 secondes puis fermer
            self.root.after(500, self.close_window)
            
        except Exception as e:
            print(f"Erreur fermeture auto: {e}")
            self.close_window()
    
    def ignore_close(self):
        """Ignore les tentatives de fermeture manuelle"""
        print("🚫 Fermeture manuelle ignorée - Attendez la fermeture automatique")
        # Ne rien faire - la fermeture se fait automatiquement
    
    def show_welcome_message(self):
        """Affiche un message d'accueil"""
        self.tree['columns'] = ('Message',)
        self.tree.heading('Message', text='Message')
        
        messages = [
            ('🎯 Bienvenue dans l\'interface de prévisualisation!',),
            ('⏰ Cette fenêtre se fermera automatiquement dans 5 secondes',),
            ('📊 Pour voir des données réelles, spécifiez un data_source_id',),
            ('',),
            ('💡 Exemple d\'utilisation:',),
            ('  python data_preview_tkinter_5sec.py --data-source-id 1',),
            ('',),
            ('✅ Interface testée et fonctionnelle!',)
        ]
        
        for i, message in enumerate(messages):
            self.tree.insert('', tk.END, text=str(i+1), values=message)
        
        self.update_status("Interface prête - Fermeture automatique dans 5 secondes")
    
    def load_data(self):
        """Charge les données depuis l'API"""
        if not self.data_source_id:
            return
        
        def load_thread():
            try:
                self.update_status("Chargement des données...")
                
                headers = {}
                if self.auth_token:
                    headers['Authorization'] = f'Bearer {self.auth_token}'
                
                # Charger les données
                response = requests.get(
                    f"{self.api_base_url}/api/v1/preview/preview-data/{self.data_source_id}?limit=100",
                    headers=headers,
                    timeout=5  # Timeout court pour respecter les 5 secondes
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.data = result.get('rows', [])
                    self.total_rows = result.get('total_rows', len(self.data))
                    
                    self.data_source = {
                        'name': result.get('data_source_name', 'Source inconnue'),
                        'type': result.get('data_source_type', 'inconnu')
                    }
                    
                    if self.data:
                        self.visible_columns = list(self.data[0].keys())[:8]  # Limiter pour l'affichage
                    
                    self.root.after(0, self.update_display)
                    self.root.after(0, lambda: self.update_status(f"Données chargées: {len(self.data)} lignes"))
                    
                else:
                    error_msg = f"Erreur API: {response.status_code}"
                    self.root.after(0, lambda: self.update_status(error_msg))
                    
            except Exception as e:
                error_msg = f"Erreur: {str(e)}"
                self.root.after(0, lambda: self.update_status(error_msg))
        
        # Lancer le chargement dans un thread séparé
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_status(self, message):
        """Met à jour le label de statut"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message)
        except Exception as e:
            print(f"Erreur mise à jour statut: {e}")
    
    def update_display(self):
        """Met à jour l'affichage du tableau"""
        try:
            # Vider le treeview existant
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not self.data:
                self.tree['columns'] = ('Message',)
                self.tree.heading('Message', text='Message')
                self.tree.insert('', tk.END, values=('Aucune donnée disponible',))
                return
            
            # Obtenir les données (limiter pour l'affichage)
            display_data = self.data[:20]  # Maximum 20 lignes pour les 5 secondes
            
            # Déterminer les colonnes à afficher
            if self.visible_columns:
                columns = self.visible_columns
            else:
                columns = list(display_data[0].keys()) if display_data else []
            
            # Configurer les colonnes du treeview
            self.tree['columns'] = columns
            self.tree.heading('#0', text='#')
            
            # Configurer les en-têtes
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, minwidth=50)
            
            # Insérer les données
            for i, row in enumerate(display_data):
                values = [str(row.get(col, ''))[:30] for col in columns]  # Limiter la longueur
                item_id = self.tree.insert('', tk.END, text=str(i + 1), values=values)
                
                # Couleurs alternées
                if i % 2 == 0:
                    self.tree.item(item_id, tags=('even_row',))
                else:
                    self.tree.item(item_id, tags=('odd_row',))
            
            # Mettre à jour le titre
            if self.data_source:
                title = f"Données: {self.data_source.get('name', 'Source inconnue')}"
                if self.total_rows:
                    title += f" ({self.total_rows} total)"
                if hasattr(self, 'title_label'):
                    self.title_label.config(text=title)
            
            # Mettre à jour le statut
            status_msg = f"Affichage de {len(display_data)} lignes"
            if self.total_rows > len(display_data):
                status_msg += f" (sur {self.total_rows} total)"
            self.update_status(status_msg)
            
        except Exception as e:
            print(f"Erreur mise à jour affichage: {e}")
    
    def close_window(self):
        """Ferme la fenêtre"""
        print("🪟 Fermeture de la fenêtre...")
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
    
    def run(self):
        """Lance l'interface avec timer de 5 secondes"""
        if not self.window_created:
            print("❌ Impossible de lancer l'interface - fenêtre non créée")
            return False
        
        print("🚀 Lancement de l'interface tkinter (5 secondes)...")
        print(f"📊 Data source ID: {self.data_source_id}")
        print(f"⏰ Timer démarré: {datetime.now().strftime('%H:%M:%S')}")
        print("🎯 L'interface se fermera automatiquement dans 5 secondes")
        
        try:
            # Forcer la mise à jour de la fenêtre
            self.root.update()
            self.root.update_idletasks()
            
            # Message de confirmation
            self.root.after(500, lambda: print("✅ Interface stable et visible"))
            
            # Démarrer la boucle principale
            self.root.mainloop()
            
            print(f"✅ Interface fermée à: {datetime.now().strftime('%H:%M:%S')}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur dans mainloop: {e}")
            traceback.print_exc()
            return False


def main():
    """Fonction principale"""
    import sys
    
    print("🔄 Démarrage de data_preview_tkinter_5sec.py")
    print(f"📋 Arguments reçus: {sys.argv}")
    
    # Parser les arguments
    data_source_id = None
    api_base_url = "http://localhost:8000"
    auth_token = None
    
    for i in range(1, len(sys.argv), 2):
        if i + 1 < len(sys.argv):
            key, value = sys.argv[i], sys.argv[i + 1]
            if key == "--data-source-id":
                data_source_id = int(value)
            elif key == "--api-base-url":
                api_base_url = value
            elif key == "--auth-token":
                auth_token = value
    
    print(f"⚙️ Configuration:")
    print(f"   - data_source_id: {data_source_id}")
    print(f"   - api_base_url: {api_base_url}")
    
    # Créer et lancer l'interface
    print("🛠️ Création de l'interface (5 secondes)...")
    app = DataPreviewTkinter5Seconds(
        data_source_id=data_source_id,
        api_base_url=api_base_url,
        auth_token=auth_token
    )
    
    print("▶️ Lancement de l'interface...")
    success = app.run()
    
    if success:
        print("🎉 Interface fermée automatiquement après 5 secondes")
    else:
        print("❌ Erreur lors de l'exécution")


if __name__ == "__main__":
    main()