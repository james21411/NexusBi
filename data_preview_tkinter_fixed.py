#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface tkinter pour la prévisualisation des données - VERSION CORRIGÉE
Version avec gestion d'erreurs améliorée et prévention de fermeture automatique
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
import traceback


class DataPreviewTkinterFixed:
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
        
        # Configuration de l'affichage
        self.display_mode = "first"  # first, last, range
        self.row_count = 50
        self.start_row = 0
        self.end_row = 49
        self.search_term = ""
        self.visible_columns = []
        
        # Tentative de création de l'interface
        try:
            self.setup_ui()
            if not self.window_created:
                raise Exception("La fenêtre n'a pas pu être créée")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ Erreur lors de l'initialisation: {e}")
            # Créer quand même une interface basique pour le débogage
            self.create_fallback_interface()
        
    def setup_ui(self):
        """Configure l'interface utilisateur tkinter avec gestion d'erreurs"""
        print("🔧 Création de la fenêtre tkinter...")
        
        try:
            # Créer la fenêtre avec des options de sécurité
            self.root = tk.Tk()
            self.root.title("Prévisualisation des Données - NexusBi")
            self.root.geometry("1200x800")
            self.root.minsize(800, 600)
            
            # Empêcher la fermeture accidentelle
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Configurer les propriétés de la fenêtre
            self.root.resizable(True, True)
            
            print("✅ Objet Tk() créé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur création Tk(): {e}")
            raise e
        
        try:
            # Configuration du style
            style = ttk.Style()
            style.theme_use('clam')
            
            style.configure('Accent.TButton', font=('Segoe UI', 12, 'bold'))
            style.map('Accent.TButton', 
                      background=[('active', '#0056D2'), ('!disabled', '#007BFF')],
                      foreground=[('!disabled', 'white')])
            
            style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#0056D2')
            style.configure('Control.TLabel', font=('Segoe UI', 10), foreground='#0056D2')
            style.configure('Treeview', background='#f0f0f0', foreground='black', fieldbackground='#f0f0f0')
            style.map('Treeview', background=[('selected', '#4a6baf')], foreground=[('selected', 'white')])
            
            print("✅ Style configuré")
            
        except Exception as e:
            print(f"⚠️ Erreur configuration style: {e}")
        
        try:
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configuration de la grille
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(2, weight=1)
            
            print("✅ Grille principale configurée")
            
        except Exception as e:
            print(f"❌ Erreur création frame principal: {e}")
            raise e
        
        try:
            # Frame de titre et boutons
            title_frame = ttk.Frame(main_frame)
            title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            title_frame.columnconfigure(1, weight=1)
            
            # Titre
            self.title_label = ttk.Label(
                title_frame,
                text="Prévisualisation des Données - NexusBi",
                style='Title.TLabel'
            )
            self.title_label.grid(row=0, column=0, sticky=tk.W)
            
            # Boutons
            button_frame = ttk.Frame(title_frame)
            button_frame.grid(row=0, column=1, sticky=tk.E)
            
            ttk.Button(button_frame, text="Actualiser", command=self.refresh_data, style='Accent.TButton').grid(row=0, column=0, padx=(0, 5))
            ttk.Button(button_frame, text="Exporter CSV", command=self.export_csv, style='Accent.TButton').grid(row=0, column=1, padx=(0, 5))
            ttk.Button(button_frame, text="Fermer", command=self.close_window).grid(row=0, column=2)
            
            print("✅ Titre et boutons créés")
            
        except Exception as e:
            print(f"❌ Erreur création titre/boutons: {e}")
            raise e
        
        try:
            # Frame de contrôle
            control_frame = ttk.LabelFrame(main_frame, text="Contrôles", padding="10")
            control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            control_frame.columnconfigure(1, weight=1)
            control_frame.columnconfigure(3, weight=1)
            
            # Contrôles des lignes
            ttk.Label(control_frame, text="Lignes à afficher:", style='Control.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            self.display_mode_var = tk.StringVar(value="Premières lignes")
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
            
            # Recherche
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
            
            print("✅ Contrôles créés")
            
        except Exception as e:
            print(f"❌ Erreur création contrôles: {e}")
            raise e
        
        try:
            # Frame du tableau
            table_frame = ttk.LabelFrame(main_frame, text="Données", padding="5")
            table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
            table_frame.columnconfigure(0, weight=1)
            table_frame.rowconfigure(0, weight=1)
            
            # Treeview
            self.tree = ttk.Treeview(table_frame)
            self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configuration des couleurs
            self.tree.tag_configure('even_row', background='#e8f4f8')
            self.tree.tag_configure('odd_row', background='#ffffff')
            self.tree.tag_configure('missing_values', background='#ffebee', foreground='#c62828')
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.tree.configure(yscrollcommand=v_scrollbar.set)
            
            h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            self.tree.configure(xscrollcommand=h_scrollbar.set)
            
            print("✅ Tableau créé")
            
        except Exception as e:
            print(f"❌ Erreur création tableau: {e}")
            raise e
        
        try:
            # Frame de statut
            status_frame = ttk.Frame(main_frame)
            status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
            status_frame.columnconfigure(0, weight=1)
            
            self.status_label = ttk.Label(status_frame, text="Prêt - Interface initialisée", relief=tk.SUNKEN)
            self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            print("✅ Statut créé")
            
        except Exception as e:
            print(f"❌ Erreur création statut: {e}")
            raise e
        
        try:
            # Masquer le frame de plage par défaut
            self.range_frame.grid_remove()
            
            print("✅ Interface créée avec succès")
            
            # Charger les données si data_source_id est fourni
            if self.data_source_id:
                self.load_data()
            else:
                # Afficher un message d'accueil si pas de data source
                self.show_welcome_message()
            
            self.window_created = True
            
        except Exception as e:
            print(f"❌ Erreur finalisation interface: {e}")
            raise e
    
    def create_fallback_interface(self):
        """Crée une interface de fallback en cas d'erreur"""
        print("🔧 Création d'une interface de fallback...")
        
        try:
            self.root = tk.Tk()
            self.root.title("Interface tkinter - Mode Dépannage")
            self.root.geometry("600x400")
            
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Message d'erreur
            error_text = f"""
Erreur lors de l'initialisation de l'interface principale:

{self.initialization_error}

Interface de dépannage activée.

Configuration:
- DISPLAY: {os.getenv('DISPLAY', 'Non définie')}
- Utilisateur: {os.getenv('USER', 'inconnu')}
- Répertoire: {os.getcwd()}
- Time: {datetime.now().strftime('%H:%M:%S')}
            """
            
            error_label = ttk.Label(main_frame, text=error_text, justify=tk.LEFT, font=("Courier", 9))
            error_label.pack(pady=10)
            
            # Boutons de test
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Test de clic", command=self.test_click).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Afficher infos système", command=self.show_system_info).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Fermer", command=self.close_window, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
            
            # Zone de logs
            log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
            log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            self.log_text = tk.Text(log_frame, height=8, font=("Courier", 8))
            scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
            self.log_text.configure(yscrollcommand=scrollbar.set)
            
            self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.window_created = True
            self.log("✅ Interface de fallback créée")
            
        except Exception as e:
            print(f"❌ Erreur création fallback: {e}")
            # Si même le fallback échoue, on se content d'un message
            print("❌ Impossible de créer une interface graphique")
            print(f"Erreur: {e}")
    
    def log(self, message):
        """Ajoute un message au log"""
        if hasattr(self, 'log_text'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
    
    def test_click(self):
        """Test de fonctionnalité de clic"""
        messagebox.showinfo("Test", "Le clic fonctionne ! L'interface est responsive.")
        self.log("✅ Test de clic réussi")
    
    def show_system_info(self):
        """Affiche les informations système"""
        info = f"""
Informations système:
- DISPLAY: {os.getenv('DISPLAY')}
- USER: {os.getenv('USER')}
- HOME: {os.getenv('HOME')}
- PWD: {os.getcwd()}
- Python: {os.sys.version.split()[0]}
- Time: {datetime.now()}
        """
        messagebox.showinfo("Informations système", info)
        self.log("ℹ️ Informations système affichées")
    
    def show_welcome_message(self):
        """Affiche un message d'accueil quand il n'y a pas de data source"""
        self.tree['columns'] = ('Message',)
        self.tree.heading('Message', text='Message')
        self.tree.insert('', tk.END, values=('Bienvenue dans l\'interface de prévisualisation!',))
        self.tree.insert('', tk.END, values=('Spécifiez un data_source_id pour charger les données.',))
        self.tree.insert('', tk.END, values=('',))
        self.tree.insert('', tk.END, values=('Utilisation:',))
        self.tree.insert('', tk.END, values=('  python data_preview_tkinter_fixed.py --data-source-id 1',))
        
        self.update_status("Interface prête - Aucune source de données spécifiée")
    
    def open_column_selection_window(self):
        """Ouvre une fenêtre de sélection personnalisée des colonnes"""
        if not self.data or not self.data[0]:
            messagebox.showwarning("Attention", "Aucune donnée chargée pour sélectionner les colonnes")
            return
        
        # Créer la fenêtre de sélection
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Sélection des Colonnes")
        selection_window.geometry("500x600")
        selection_window.resizable(True, True)
        
        # Centrer la fenêtre
        selection_window.transient(self.root)
        selection_window.grab_set()
        
        # Obtenir toutes les colonnes disponibles
        available_columns = list(self.data[0].keys())
        
        # Frame principal
        main_frame = ttk.Frame(selection_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Sélectionner les colonnes à afficher", 
                               font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame pour les boutons de sélection rapide
        quick_select_frame = ttk.LabelFrame(main_frame, text="Sélection Rapide", padding="5")
        quick_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_select_frame, text="Tout sélectionner", 
                  command=lambda: self.select_all_columns(checkboxes, available_columns)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_select_frame, text="Tout désélectionner", 
                  command=lambda: self.deselect_all_columns(checkboxes)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_select_frame, text="Sélectionner les 5 premières", 
                  command=lambda: self.select_first_n_columns(checkboxes, available_columns, 5)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame scrollable pour la liste des colonnes
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas et scrollbar
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas et scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Créer les checkboxes pour chaque colonne
        checkboxes = {}
        
        # Déterminer les colonnes déjà sélectionnées
        current_selection = set(self.visible_columns) if self.visible_columns else set(available_columns)
        
        for i, column in enumerate(available_columns):
            var = tk.BooleanVar(value=column in current_selection)
            
            # Frame pour chaque checkbox
            cb_frame = ttk.Frame(scrollable_frame)
            cb_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Checkbox
            checkbox = ttk.Checkbutton(cb_frame, text=column, variable=var)
            checkbox.pack(side=tk.LEFT)
            
            # Type de données (estimation)
            sample_values = [str(row.get(column, '')) for row in self.data[:10] if row.get(column)]
            data_type = self.estimate_data_type(sample_values)
            type_label = ttk.Label(cb_frame, text=f" ({data_type})", foreground="gray")
            type_label.pack(side=tk.LEFT, padx=(5, 0))
            
            checkboxes[column] = var
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Variables pour stocker les fonctions de callback
        def apply_selection():
            selected_cols = [col for col, var in checkboxes.items() if var.get()]
            
            if not selected_cols:
                messagebox.showwarning("Attention", "Veuillez sélectionner au moins une colonne")
                return
            
            self.visible_columns = selected_cols
            
            # Auto-update de l'affichage
            self.update_display()
            
            # Fermer la fenêtre
            selection_window.destroy()
            
            # Mettre à jour le combobox pour refléter la sélection
            if len(selected_cols) == len(available_columns):
                self.columns_var.set("Toutes")
            elif len(selected_cols) <= 10:
                # Vérifier si c'est exactement les 10 premières
                first_10 = available_columns[:10]
                if selected_cols == first_10:
                    self.columns_var.set("10 premières")
                else:
                    self.columns_var.set(f"Personnalisée ({len(selected_cols)})")
            else:
                self.columns_var.set(f"Personnalisée ({len(selected_cols)})")
        
        def cancel_selection():
            selection_window.destroy()
            # Restaurer la sélection précédente
            self.columns_var.set("Toutes" if not self.visible_columns else 
                               "10 premières" if len(self.visible_columns) == 10 and 
                               self.visible_columns == available_columns[:10] else 
                               f"Personnalisée ({len(self.visible_columns)})")
        
        # Boutons
        ttk.Button(button_frame, text="Appliquer", command=apply_selection, style="Accent.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", command=cancel_selection).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Tout sélectionner", command=lambda: self.select_all_columns(checkboxes, available_columns)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Tout désélectionner", command=lambda: self.deselect_all_columns(checkboxes)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Lier la molette de la souris au canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Centrer la fenêtre
        selection_window.update_idletasks()
        x = (selection_window.winfo_screenwidth() // 2) - (selection_window.winfo_width() // 2)
        y = (selection_window.winfo_screenheight() // 2) - (selection_window.winfo_height() // 2)
        selection_window.geometry(f"+{x}+{y}")
    
    def select_all_columns(self, checkboxes, available_columns):
        """Sélectionne toutes les colonnes"""
        for col in available_columns:
            checkboxes[col].set(True)
    
    def deselect_all_columns(self, checkboxes):
        """Désélectionne toutes les colonnes"""
        for var in checkboxes.values():
            var.set(False)
    
    def select_first_n_columns(self, checkboxes, available_columns, n):
        """Sélectionne les n premières colonnes"""
        for i, col in enumerate(available_columns):
            checkboxes[col].set(i < n)
    
    def estimate_data_type(self, sample_values):
        """Estime le type de données basé sur un échantillon de valeurs"""
        if not sample_values:
            return "vide"
        
        # Nettoyer les valeurs
        clean_values = [v.strip() for v in sample_values if v and str(v).strip()]
        
        if not clean_values:
            return "vide"
        
        # Vérifier si c'est numérique
        numeric_count = 0
        date_count = 0
        
        for value in clean_values[:5]:  # Analyser seulement les 5 premières
            try:
                float(value.replace(',', ''))
                numeric_count += 1
            except (ValueError, TypeError):
                pass
            
            # Recherche de motifs de date
            if any(char in str(value) for char in ['-', '/', '.']) and len(str(value)) >= 8:
                date_count += 1
        
        if numeric_count >= len(clean_values[:5]) * 0.8:
            return "numérique"
        elif date_count >= len(clean_values[:5]) * 0.6:
            return "date"
        else:
            return "texte"
    
    def on_closing(self):
        """Gestion de la fermeture de la fenêtre"""
        print("🪟 Fermeture de la fenêtre...")
        self.close_window()
    
    def on_mode_change(self, event=None):
        """Gère le changement de mode d'affichage"""
        try:
            mode = self.display_mode_var.get()
            if mode == "Plage personnalisée":
                self.range_frame.grid()
            else:
                self.range_frame.grid_remove()
            self.update_display()
        except Exception as e:
            print(f"Erreur changement de mode: {e}")
    
    def on_search_change(self, event=None):
        """Gère le changement de terme de recherche"""
        try:
            self.search_term = self.search_var.get()
            self.update_display()
        except Exception as e:
            print(f"Erreur recherche: {e}")
    
    def on_columns_change(self, event=None):
        """Gère le changement de sélection des colonnes"""
        try:
            selected_option = self.columns_var.get()
            
            if selected_option == "Toutes":
                # Afficher toutes les colonnes
                if self.data:
                    self.visible_columns = list(self.data[0].keys())
                else:
                    self.visible_columns = []
                
            elif selected_option == "10 premières":
                # Afficher les 10 premières colonnes
                if self.data:
                    self.visible_columns = list(self.data[0].keys())[:10]
                else:
                    self.visible_columns = []
                
            elif selected_option == "Sélectionner...":
                # Ouvrir la fenêtre de sélection personnalisée
                self.open_column_selection_window()
                return  # Ne pas mettre à jour l'affichage ici
            
            # Auto-update de l'affichage après sélection
            self.update_display()
            
        except Exception as e:
            print(f"Erreur changement de colonnes: {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la sélection des colonnes: {str(e)}")
    
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
                    f"{self.api_base_url}/api/v1/preview/preview-data/{self.data_source_id}?limit=1000",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.data = result.get('rows', [])
                    self.total_rows = result.get('total_rows', len(self.data))
                    
                    # Informations de la source
                    self.data_source = {
                        'name': result.get('data_source_name', 'Source inconnue'),
                        'type': result.get('data_source_type', 'inconnu')
                    }
                    
                    # Initialiser les colonnes visibles
                    if self.data:
                        self.visible_columns = list(self.data[0].keys())[:10]
                    
                    self.root.after(0, self.update_display)
                    self.root.after(0, lambda: self.update_status(f"Données chargées: {len(self.data)} lignes"))
                    
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
                display_data = self.get_filtered_data()
                df = pd.DataFrame(display_data)
                df.to_csv(filename, index=False, encoding='utf-8')
                messagebox.showinfo("Succès", f"Données exportées vers: {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def close_window(self):
        """Ferme la fenêtre"""
        print("🪟 Fermeture de la fenêtre via bouton...")
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Erreur lors de la fermeture: {e}")
    
    def update_status(self, message):
        """Met à jour le label de statut"""
        try:
            self.status_label.config(text=message)
        except Exception as e:
            print(f"Erreur mise à jour statut: {e}")
    
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
        try:
            # Vider le treeview existant
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not self.data:
                self.tree['columns'] = ('Message',)
                self.tree.heading('Message', text='Message')
                self.tree.insert('', tk.END, values=('Aucune donnée à afficher',))
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
            
            # Insérer les données avec couleurs
            for i, row in enumerate(display_data):
                values = [str(row.get(col, '')) for col in columns]
                item_id = self.tree.insert('', tk.END, text=str(i + 1), values=values)
                
                # Déterminer les tags à appliquer
                has_missing = self.has_missing_values(row)
                
                if has_missing:
                    self.tree.item(item_id, tags=('missing_values',))
                else:
                    if i % 2 == 0:
                        self.tree.item(item_id, tags=('even_row',))
                    else:
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
            
        except Exception as e:
            print(f"Erreur mise à jour affichage: {e}")
            self.log(f"Erreur update_display: {e}")
    
    def run(self):
        """Lance l'interface avec gestion d'erreurs améliorée"""
        if not self.window_created:
            print("❌ Impossible de lancer l'interface - fenêtre non créée")
            return False
        
        print("🚀 Lancement de l'interface tkinter corrigée...")
        print(f"📊 Data source ID: {self.data_source_id}")
        print(f"🌐 API URL: {self.api_base_url}")
        print("🎯 Démarrage de la boucle principale...")
        
        try:
            # Forcer la mise à jour de la fenêtre
            self.root.update()
            self.root.update_idletasks()
            
            # Mettre la fenêtre au premier plan
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)  # Retirer du premier plan
            
            # Message de confirmation
            self.root.after(1000, lambda: print("✅ Interface initialisée et stable"))
            
            print("🔄 Entrée dans mainloop...")
            print("✅ Interface lancée - rester ouverte indéfiniment")
            
            # Démarrer la boucle principale
            self.root.mainloop()
            
            print("✅ Interface fermée proprement")
            return True
            
        except Exception as e:
            print(f"❌ Erreur dans mainloop: {e}")
            traceback.print_exc()
            return False


def main():
    """Fonction principale pour test"""
    import sys
    
    print("🔄 Démarrage de data_preview_tkinter_fixed.py")
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
    print("🛠️ Création de l'interface DataPreviewTkinterFixed...")
    app = DataPreviewTkinterFixed(
        data_source_id=data_source_id,
        api_base_url=api_base_url,
        auth_token=auth_token
    )
    
    print("▶️ Lancement de l'interface...")
    success = app.run()
    
    if success:
        print("🎉 Interface fermée normalement")
    else:
        print("❌ Erreur lors de l'exécution de l'interface")


if __name__ == "__main__":
    main()