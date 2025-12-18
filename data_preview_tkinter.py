#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface tkinter pour la prévisualisation des données
Version avec auto-update des colonnes sélectionnées
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import requests
import pandas as pd
from typing import List, Dict, Any, Optional
import threading
import os
import time
from datetime import datetime


class DataPreviewTkinter:
    def __init__(self, data_source_id: int = None, api_base_url: str = "http://localhost:8000", auth_token: str = None):
        self.data_source_id = data_source_id
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.data = []
        self.total_rows = 0
        self.schema = None
        self.data_source = None
        
        # Configuration de l'affichage
        self.display_mode = "first"  # first, last, range
        self.row_count = 50
        self.start_row = 0
        self.end_row = 49
        self.search_term = ""
        self.visible_columns = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur tkinter"""
        print("🔧 Création de la fenêtre tkinter...")
        
        try:
            self.root = tk.Tk()
            print("✅ Objet Tk() créé avec succès")
        except Exception as e:
            print(f"❌ Erreur création Tk(): {e}")
            print("⚠️ Impossible de créer l'interface graphique. Vérifiez que X11 est configuré et que la variable DISPLAY est correcte.")
            return
        
        self.root.title("Prévisualisation des Données")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Empêcher la fermeture automatique
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuration du style avec couleurs sur boutons et labels
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurer les couleurs pour les boutons et labels
        style.configure('Accent.TButton', font=('Segoe UI', 12, 'bold'))
        style.map('Accent.TButton', 
                  background=[('active', '#0056D2'), ('!disabled', '#007BFF')],
                  foreground=[('!disabled', 'white')])
        
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#0056D2')
        style.configure('Control.TLabel', font=('Segoe UI', 10), foreground='#0056D2')
        
        # Configuration des couleurs pour les lignes alternées uniquement
        style.configure('Treeview', background='#f0f0f0', foreground='black', fieldbackground='#f0f0f0')
        style.map('Treeview', background=[('selected', '#4a6baf')], foreground=[('selected', 'white')])
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration de la grille
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de titre et boutons
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        # Titre avec style coloré
        self.title_label = ttk.Label(
            title_frame,
            text="Prévisualisation des Données",
            style='Title.TLabel'
        )
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Boutons avec couleurs
        button_frame = ttk.Frame(title_frame)
        button_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Button(button_frame, text="Actualiser", command=self.refresh_data, style='Accent.TButton').grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Exporter CSV", command=self.export_csv, style='Accent.TButton').grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Fermer", command=self.close_window).grid(row=0, column=2)
        
        # Frame de contrôle avec labels colorés
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(3, weight=1)
        
        # Contrôles des lignes avec labels colorés
        ttk.Label(control_frame, text="Lignes à afficher:", style='Control.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.display_mode_var = tk.StringVar(value="first")
        mode_combo = ttk.Combobox(control_frame, textvariable=self.display_mode_var, 
                                  values=["Premières lignes", "Dernières lignes", "Plage personnalisée"],
                                  state="readonly", width=20)
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        self.row_count_var = tk.IntVar(value=50)
        ttk.Label(control_frame, text="Nombre:", style='Control.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        row_spin = ttk.Spinbox(control_frame, from_=1, to=1000, textvariable=self.row_count_var, width=10)
        row_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # Contrôles de plage
        self.range_frame = ttk.Frame(control_frame)
        self.range_frame.grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
        
        ttk.Label(self.range_frame, text="De:", style='Control.TLabel').pack(side=tk.LEFT)
        self.start_row_var = tk.IntVar(value=0)
        start_spin = ttk.Spinbox(self.range_frame, from_=0, to=999999, textvariable=self.start_row_var, width=8)
        start_spin.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(self.range_frame, text="À:", style='Control.TLabel').pack(side=tk.LEFT)
        self.end_row_var = tk.IntVar(value=49)
        end_spin = ttk.Spinbox(self.range_frame, from_=0, to=999999, textvariable=self.end_row_var, width=8)
        end_spin.pack(side=tk.LEFT, padx=(5, 0))
        
        # Recherche avec label coloré
        ttk.Label(control_frame, text="Rechercher:", style='Control.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0), padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Sélection des colonnes avec label coloré
        ttk.Label(control_frame, text="Colonnes:", style='Control.TLabel').grid(row=1, column=3, sticky=tk.W, pady=(10, 0), padx=(20, 5))
        self.columns_var = tk.StringVar(value="Toutes")
        columns_combo = ttk.Combobox(control_frame, textvariable=self.columns_var,
                                     values=["Toutes", "10 premières", "Sélectionner..."],
                                     state="readonly", width=15)
        columns_combo.grid(row=1, column=4, sticky=tk.W, pady=(10, 0))
        columns_combo.bind('<<ComboboxSelected>>', self.on_columns_change)
        
        # Frame du tableau
        table_frame = ttk.LabelFrame(main_frame, text="Données", padding="5")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview pour afficher les données
        self.tree = ttk.Treeview(table_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurer les tags pour les couleurs alternées uniquement
        self.tree.tag_configure('even_row', background='#e8f4f8')  # Bleu clair pour les lignes paires
        self.tree.tag_configure('odd_row', background='#ffffff')   # Blanc pour les lignes impaires
        self.tree.tag_configure('missing_values', background='#ffebee', foreground='#c62828')  # Rouge clair pour valeurs manquantes
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Frame de statut
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Prêt", relief=tk.SUNKEN)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Masquer le frame de plage par défaut
        self.range_frame.grid_remove()
        
        print("✅ Interface créée avec succès")
        
        # Charger les données si data_source_id est fourni
        if self.data_source_id:
            self.load_data()
    
    def on_closing(self):
        """Gestion de la fermeture de la fenêtre"""
        print("🪟 Fermeture de la fenêtre...")
        self.root.quit()
        self.root.destroy()
    
    def on_mode_change(self, event=None):
        """Gère le changement de mode d'affichage"""
        mode = self.display_mode_var.get()
        if mode == "Plage personnalisée":
            self.range_frame.grid()
        else:
            self.range_frame.grid_remove()
        self.update_display()
    
    def on_search_change(self, event=None):
        """Gère le changement de terme de recherche"""
        self.search_term = self.search_var.get()
        self.update_display()
    
    def on_columns_change(self, event=None):
        """Gère le changement de sélection des colonnes"""
        choice = self.columns_var.get()
        if choice == "Sélectionner...":
            self.show_column_selection()
        elif choice == "Toutes":
            # Afficher toutes les colonnes
            self.visible_columns = []
            self.update_display()
        elif choice == "10 premières":
            # Afficher les 10 premières colonnes
            if self.data:
                self.visible_columns = list(self.data[0].keys())[:10]
                self.update_display()
    
    def show_column_selection(self):
        """Affiche une fenêtre pour sélectionner les colonnes avec auto-update"""
        if not self.data:
            return
            
        column_window = tk.Toplevel(self.root)
        column_window.title("Sélectionner les Colonnes")
        column_window.geometry("400x300")
        
        all_columns = list(self.data[0].keys()) if self.data else []
        
        # Frame avec scrollbar
        canvas = tk.Canvas(column_window)
        scrollbar = ttk.Scrollbar(column_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variables pour les colonnes
        column_vars = {}
        for col in all_columns:
            var = tk.BooleanVar(value=True if col in self.visible_columns or not self.visible_columns else False)
            column_vars[col] = var
            
            # Créer le checkbox avec auto-update
            checkbox = ttk.Checkbutton(
                scrollable_frame, 
                text=col, 
                variable=var,
                command=lambda col=col, var=var: self.update_columns_from_selection(column_vars, column_window)
            )
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Boutons
        button_frame = ttk.Frame(column_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def apply_selection():
            self.update_columns_from_selection(column_vars, column_window)
        
        ttk.Button(button_frame, text="Appliquer", command=apply_selection, style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Fermer", command=column_window.destroy).pack(side=tk.RIGHT)
    
    def update_columns_from_selection(self, column_vars, window=None):
        """Met à jour les colonnes sélectionnées et l'affichage"""
        # Mettre à jour la liste des colonnes visibles
        self.visible_columns = [col for col, var in column_vars.items() if var.get()]
        
        # Mettre à jour l'affichage immédiatement
        self.update_display()
        
        # Mettre à jour le label de statut pour montrer les colonnes sélectionnées
        if self.visible_columns:
            status_msg = f"Colonnes sélectionnées: {len(self.visible_columns)} • Affichage de {len(self.get_filtered_data())} lignes"
        else:
            status_msg = f"Affichage de {len(self.get_filtered_data())} lignes (toutes les colonnes)"
        
        self.update_status(status_msg)
    
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
                
                # Charger les données - essayer d'abord l'endpoint principal
                response = requests.get(
                    f"{self.api_base_url}/api/v1/data-sources/{self.data_source_id}/data?limit=1000",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.data = result.get('rows', [])
                    self.total_rows = result.get('total_rows', len(self.data))
                    
                    # Charger les informations de la source de données
                    ds_response = requests.get(
                        f"{self.api_base_url}/api/v1/data-sources/{self.data_source_id}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if ds_response.status_code == 200:
                        self.data_source = ds_response.json()
                    
                    # Charger le schéma si disponible
                    if self.data_source and self.data_source.get('schema_info'):
                        try:
                            self.schema = json.loads(self.data_source['schema_info'])
                        except:
                            self.schema = None
                    
                    # Initialiser les colonnes visibles
                    if self.data:
                        self.visible_columns = list(self.data[0].keys())[:10]  # 10 premières par défaut
                    
                    self.root.after(0, self.update_display)
                    self.root.after(0, lambda: self.update_status(f"Données chargées: {len(self.data)} lignes"))
                    
                elif response.status_code == 401:
                    # Erreur d'authentification - essayer l'endpoint public
                    print("🔓 Tentative d'accès à l'endpoint public...")
                    public_response = requests.get(
                        f"{self.api_base_url}/api/v1/preview/preview-data/{self.data_source_id}?limit=1000",
                        timeout=30
                    )
                    
                    if public_response.status_code == 200:
                        result = public_response.json()
                        self.data = result.get('rows', [])
                        self.total_rows = result.get('total_rows', len(self.data))
                        
                        # Créer un objet data_source minimal pour le titre
                        self.data_source = {
                            'name': result.get('data_source_name', 'Source inconnue'),
                            'type': result.get('data_source_type', 'inconnu')
                        }
                        
                        # Initialiser les colonnes visibles
                        if self.data:
                            self.visible_columns = list(self.data[0].keys())[:10]
                        
                        self.root.after(0, self.update_display)
                        self.root.after(0, lambda: self.update_status(f"Données chargées (mode public): {len(self.data)} lignes"))
                    else:
                        print(f"❌ Erreur endpoint public: {public_response.status_code}")
                        # Les deux endpoints ont échoué
                        error_msg = "Authentification requise pour accéder aux données."
                        self.root.after(0, lambda: self.update_status("Connectez-vous pour voir les données"))
                        self.root.after(0, lambda: self.show_auth_required_message())
                    
                else:
                    error_msg = f"Erreur HTTP {response.status_code}"
                    self.root.after(0, lambda: self.update_status(error_msg))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", f"Impossible de charger les données: {error_msg}"))
                    
            except Exception as e:
                error_msg = f"Erreur: {str(e)}"
                self.root.after(0, lambda: self.update_status(error_msg))
                self.root.after(0, lambda: messagebox.showerror("Erreur", error_msg))
        
        # Lancer le chargement dans un thread séparé
        threading.Thread(target=load_thread, daemon=True).start()
    
    def refresh_data(self):
        """Actualise les données depuis l'API"""
        if self.data_source_id:
            print("🔄 Actualisation des données...")
            self.load_data()
        else:
            messagebox.showwarning("Attention", "Aucune source de données configurée")
    
    def show_auth_required_message(self):
        """Affiche un message quand l'authentification est requise"""
        # Afficher un message dans le tableau
        self.tree['columns'] = ('Message',)
        self.tree.heading('Message', text='Message')
        self.tree.insert('', tk.END, values=('Accès limité - Connectez-vous pour voir toutes les données',))
        
        # Afficher un message popup informatif
        messagebox.showinfo(
            "Mode Accès Limité",
            "L'application fonctionne en mode accès public.\n\n"
            "Certaines fonctionnalités peuvent être limitées.\n\n"
            "Pour un accès complet, connectez-vous dans l'application web et relancez la prévisualisation."
        )
    
    def export_csv(self):
        """Exporte les données affichées vers un fichier CSV"""
        if not self.data:
            messagebox.showwarning("Attention", "Aucune donnée à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                # Appliquer les filtres actuels pour l'export
                display_data = self.get_filtered_data()
                df = pd.DataFrame(display_data)
                df.to_csv(filename, index=False, encoding='utf-8')
                messagebox.showinfo("Succès", f"Données exportées vers: {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def close_window(self):
        """Ferme la fenêtre"""
        print("🪟 Fermeture de la fenêtre via bouton...")
        self.root.quit()
        self.root.destroy()
    
    def update_status(self, message):
        """Met à jour le label de statut"""
        self.status_label.config(text=message)
    
    def get_filtered_data(self):
        """Retourne les données filtrées selon les paramètres actuels"""
        if not self.data:
            return []
        
        data = self.data.copy()
        
        # Appliquer la recherche
        if self.search_term:
            data = [row for row in data if self.search_term.lower() in str(row).lower()]
        
        # Appliquer le mode d'affichage
        if self.display_mode_var.get() == "Premières lignes":
            data = data[:self.row_count_var.get()]
        elif self.display_mode_var.get() == "Dernières lignes":
            data = data[-self.row_count_var.get():]
        elif self.display_mode_var.get() == "Plage personnalisée":
            start = self.start_row_var.get()
            end = min(self.end_row_var.get() + 1, len(data))
            data = data[start:end]
        
        # Appliquer le filtrage des colonnes
        if self.visible_columns:
            data = [{col: row.get(col, '') for col in self.visible_columns} for row in data]
        
        return data
    
    def has_missing_values(self, row):
        """Vérifie si une ligne contient des valeurs manquantes"""
        if not row:
            return False
        
        missing_values = ['nan', 'null', 'none', '', 'na', 'missing']
        for key, value in row.items():
            value_str = str(value).strip().lower()
            if value_str in missing_values or not value_str:
                return True
        return False
    
    def update_display(self):
        """Met à jour l'affichage du tableau"""
        # Vider le treeview existant
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.data:
            self.tree['columns'] = ()
            return
        
        # Obtenir les données filtrées
        display_data = self.get_filtered_data()
        
        if not display_data:
            self.tree['columns'] = ('Message',)
            self.tree.heading('Message', text='Message')
            self.tree.insert('', tk.END, values=('Aucune donnée à afficher',))
            return
        
        # Déterminer les colonnes à afficher
        if self.visible_columns:
            columns = self.visible_columns
        else:
            columns = list(display_data[0].keys())
        
        # Configurer les colonnes du treeview
        self.tree['columns'] = columns
        self.tree.heading('#0', text='#')
        
        # Configurer les en-têtes
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=50)
        
        # Insérer les données avec couleurs alternées ET surlignage des valeurs manquantes
        for i, row in enumerate(display_data):
            values = [str(row.get(col, '')) for col in columns]
            item_id = self.tree.insert('', tk.END, text=str(i + 1), values=values)
            
            # Déterminer les tags à appliquer
            has_missing = self.has_missing_values(row)
            
            if has_missing:
                # Ligne avec valeurs manquantes - surligner en rouge
                self.tree.item(item_id, tags=('missing_values',))
            else:
                # Ligne normale - couleurs alternées
                if i % 2 == 0:  # Ligne paire
                    self.tree.item(item_id, tags=('even_row',))
                else:  # Ligne impaire
                    self.tree.item(item_id, tags=('odd_row',))
        
        # Mettre à jour le titre
        if self.data_source:
            title = f"Données: {self.data_source.get('name', 'Source inconnue')}"
            if self.total_rows:
                title += f" ({self.total_rows} lignes totales)"
            self.title_label.config(text=title)
        
        # Mettre à jour le statut
        status_msg = f"Affichage de {len(display_data)} lignes"
        if self.search_term:
            status_msg += f" • Recherche: '{self.search_term}'"
        if self.visible_columns:
            status_msg += f" • Colonnes: {len(self.visible_columns)}"
        self.update_status(status_msg)
    
    def run(self):
        """Lance l'interface"""
        print("🚀 Lancement de l'interface tkinter...")
        print(f"📊 Data source ID: {self.data_source_id}")
        print(f"🌐 API URL: {self.api_base_url}")
        print("🎯 Démarrage de la boucle principale...")
        
        try:
            # Afficher un message après 1 seconde
            self.root.after(1000, lambda: print("✅ Interface initialisée - 1s écoulée"))
            
            print("🔄 Entrée dans mainloop...")
            print("✅ Interface lancée - rester ouverte indéfiniment")
            self.root.mainloop()
            print("✅ Interface fermée proprement")
            
        except Exception as e:
            print(f"❌ Erreur dans mainloop: {e}")
            import traceback
            traceback.print_exc()
    
    def keep_window_open(self):
        """Empêche la fermeture automatique de la fenêtre"""
        print("✅ Fenêtre stabilisée et prête pour interaction")
        print("🎯 L'interface devrait maintenant être visible")


def main():
    """Fonction principale pour test"""
    import sys
    
    print("🔄 Démarrage de data_preview_tkinter.py")
    print(f"📋 Arguments reçus: {sys.argv}")
    
    # Parser les arguments de ligne de commande
    data_source_id = None
    api_base_url = "http://localhost:8000"
    auth_token = None
    
    for i in range(1, len(sys.argv), 2):
        if i + 1 < len(sys.argv):
            key, value = sys.argv[i], sys.argv[i + 1]
            print(f"🔧 Traitement argument: {key} = {value}")
            if key == "--data-source-id":
                data_source_id = int(value)
            elif key == "--api-base-url":
                api_base_url = value
            elif key == "--auth-token":
                auth_token = value
    
    print(f"⚙️ Configuration finale:")
    print(f"   - data_source_id: {data_source_id}")
    print(f"   - api_base_url: {api_base_url}")
    print(f"   - auth_token: {'***' if auth_token else None}")
    
    # Créer et lancer l'interface
    print("🛠️ Création de l'interface DataPreviewTkinter...")
    app = DataPreviewTkinter(
        data_source_id=data_source_id,
        api_base_url=api_base_url,
        auth_token=auth_token
    )
    
    print("▶️ Lancement de l'interface...")
    app.run()


if __name__ == "__main__":
    main()