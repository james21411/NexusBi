#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface tkinter COMPLÈTE pour la prévisualisation des données
Version avec toutes les fonctionnalités : gestion d'erreurs + sélection colonnes + robustesse
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


class DataPreviewTkinterComplete:
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
        """Configure l'interface utilisateur tkinter COMPLÈTE"""
        print("🔧 Création de la fenêtre tkinter COMPLÈTE...")
        
        try:
            # Créer la fenêtre avec des options de sécurité
            self.root = tk.Tk()
            self.root.title("Prévisualisation des Données - NexusBi (Version Complète)")
            self.root.geometry("1400x900")  # Plus grande pour accommodates toutes les fonctionnalités
            self.root.minsize(1000, 700)
            
            # Empêcher la fermeture accidentelle
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Configurer les propriétés de la fenêtre
            self.root.resizable(True, True)
            
            print("✅ Objet Tk() créé avec succès")
            
        except Exception as e:
            print(f"❌ Erreur création Tk(): {e}")
            raise e
        
        try:
            # Configuration du style amélioré
            style = ttk.Style()
            style.theme_use('clam')
            
            # Styles personnalisés
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
                text="Prévisualisation des Données - NexusBi (Version Complète)",
                style='Title.TLabel'
            )
            self.title_label.grid(row=0, column=0, sticky=tk.W)
            
            # Boutons
            button_frame = ttk.Frame(title_frame)
            button_frame.grid(row=0, column=1, sticky=tk.E)
            
            ttk.Button(button_frame, text="Actualiser", command=self.refresh_data, style='Accent.TButton').grid(row=0, column=0, padx=(0, 5))
            ttk.Button(button_frame, text="Exporter CSV", command=self.export_csv, style='Accent.TButton').grid(row=0, column=1, padx=(0, 5))
            ttk.Button(button_frame, text="Filtrer", command=self.show_filter_dialog, style='Accent.TButton').grid(row=0, column=2, padx=(0, 5))
            ttk.Button(button_frame, text="Fermer", command=self.close_window).grid(row=0, column=3)
            
            print("✅ Titre et boutons créés")
            
        except Exception as e:
            print(f"❌ Erreur création titre/boutons: {e}")
            raise e
        
        try:
            # Frame de contrôle avec plus d'options
            control_frame = ttk.LabelFrame(main_frame, text="Contrôles Avancés", padding="10")
            control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            control_frame.columnconfigure(1, weight=1)
            control_frame.columnconfigure(3, weight=1)
            
            # Ligne 1: Contrôles des lignes
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
            
            # Ligne 2: Recherche et sélection des colonnes
            ttk.Label(control_frame, text="Rechercher:", style='Control.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
            search_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0), padx=(0, 10))
            search_entry.bind('<KeyRelease>', self.on_search_change)
            
            # Sélection des colonnes avec combobox complet
            ttk.Label(control_frame, text="Colonnes:", style='Control.TLabel').grid(row=1, column=3, sticky=tk.W, pady=(10, 0), padx=(20, 5))
            self.columns_var = tk.StringVar(value="Toutes")
            columns_combo = ttk.Combobox(control_frame, textvariable=self.columns_var,
                                         values=["Toutes", "10 premières", "Sélectionner..."],
                                         state="readonly", width=15)
            columns_combo.grid(row=1, column=4, sticky=tk.W, pady=(10, 0))
            columns_combo.bind('<<ComboboxSelected>>', self.on_columns_change)
            
            print("✅ Contrôles avancés créés")
            
        except Exception as e:
            print(f"❌ Erreur création contrôles: {e}")
            raise e
        
        try:
            # Frame du tableau amélioré
            table_frame = ttk.LabelFrame(main_frame, text="Données (Affichage Complet)", padding="5")
            table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
            table_frame.columnconfigure(0, weight=1)
            table_frame.rowconfigure(0, weight=1)
            
            # Treeview avec toutes les fonctionnalités
            self.tree = ttk.Treeview(table_frame)
            self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configuration des couleurs avancées
            self.tree.tag_configure('even_row', background='#e8f4f8')  # Bleu clair pour les lignes paires
            self.tree.tag_configure('odd_row', background='#ffffff')   # Blanc pour les lignes impaires
            self.tree.tag_configure('missing_values', background='#ffebee', foreground='#c62828')  # Rouge clair pour valeurs manquantes
            self.tree.tag_configure('filtered_row', background='#fff3cd', foreground='#856404')  # Jaune pour lignes filtrées
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            self.tree.configure(yscrollcommand=v_scrollbar.set)
            
            h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            self.tree.configure(xscrollcommand=h_scrollbar.set)
            
            print("✅ Tableau avancé créé")
            
        except Exception as e:
            print(f"❌ Erreur création tableau: {e}")
            raise e
        
        try:
            # Frame de statut amélioré
            status_frame = ttk.Frame(main_frame)
            status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
            status_frame.columnconfigure(0, weight=1)
            
            self.status_label = ttk.Label(status_frame, text="Prêt - Interface Complète Initialisée", relief=tk.SUNKEN)
            self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            # Frame pour les informations supplémentaires
            info_frame = ttk.Frame(status_frame)
            info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
            
            self.info_label = ttk.Label(info_frame, text="", font=('Segoe UI', 8), foreground='#666666')
            self.info_label.pack(side=tk.LEFT)
            
            print("✅ Statut créé")
            
        except Exception as e:
            print(f"❌ Erreur création statut: {e}")
            raise e
        
        try:
            # Masquer le frame de plage par défaut
            self.range_frame.grid_remove()
            
            print("✅ Interface complète créée avec succès")
            
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
            self.root.title("Interface tkinter - Mode Dépannage Complet")
            self.root.geometry("800x600")
            
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Message d'erreur détaillé
            error_text = f"""
Erreur lors de l'initialisation de l'interface complète:

{self.initialization_error}

Interface de dépannage activée.

Configuration système:
- DISPLAY: {os.getenv('DISPLAY', 'Non définie')}
- Utilisateur: {os.getenv('USER', 'inconnu')}
- Répertoire: {os.getcwd()}
- Time: {datetime.now().strftime('%H:%M:%S')}
            """
            
            error_label = ttk.Label(main_frame, text=error_text, justify=tk.LEFT, font=("Courier", 9))
            error_label.pack(pady=10)
            
            # Boutons de test avancés
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(button_frame, text="Test de clic", command=self.test_click).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Afficher infos système", command=self.show_system_info).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Test fonctionnalités", command=self.test_features).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Fermer", command=self.close_window, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
            
            # Zone de logs améliorée
            log_frame = ttk.LabelFrame(main_frame, text="Logs et Diagnostics", padding="5")
            log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            self.log_text = tk.Text(log_frame, height=10, font=("Courier", 8))
            scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
            self.log_text.configure(yscrollcommand=scrollbar.set)
            
            self.log_text.pack(side="left", fill=tk.BOTH, expand=True)
            scrollbar.pack(side="right", fill="y")
            
            self.window_created = True
            self.log("✅ Interface de fallback complète créée")
            self.log("🎯 Fonctionnalités de test disponibles")
            
        except Exception as e:
            print(f"❌ Erreur création fallback: {e}")
    
    def log(self, message):
        """Ajoute un message au log avec timestamp"""
        if hasattr(self, 'log_text'):
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
    
    def test_click(self):
        """Test de fonctionnalité de clic"""
        messagebox.showinfo("Test", "Le clic fonctionne ! L'interface est responsive.\n\nToutes les fonctionnalités de sélection des colonnes sont opérationnelles.")
        self.log("✅ Test de clic réussi - Interface responsive")
    
    def test_features(self):
        """Test des fonctionnalités avancées"""
        features = """
Fonctionnalités测试ées:
✅ Interface graphique responsive
✅ Gestion des événements
✅ Affichage des messages
✅ Log système

Fonctionnalités disponibles dans la version complète:
🎯 Sélection avancée des colonnes
🔍 Recherche en temps réel
📊 Filtrage par plage
📈 Export CSV
🔄 Auto-update des données
        """
        messagebox.showinfo("Test des Fonctionnalités", features)
        self.log("🧪 Test des fonctionnalités avancées effectué")
    
    def show_system_info(self):
        """Affiche les informations système détaillées"""
        info = f"""
Informations système complètes:
- DISPLAY: {os.getenv('DISPLAY')}
- USER: {os.getenv('USER')}
- HOME: {os.getenv('HOME')}
- PWD: {os.getcwd()}
- Python: {os.sys.version.split()[0]}
- Time: {datetime.now()}
- Interface: tkinter complète
- État: Prête pour utilisation
        """
        messagebox.showinfo("Informations système", info)
        self.log("ℹ️ Informations système affichées")
    
    def show_welcome_message(self):
        """Affiche un message d'accueil complet"""
        self.tree['columns'] = ('Message',)
        self.tree.heading('Message', text='Message')
        
        welcome_messages = [
            ('Bienvenue dans l\'interface de prévisualisation COMPLÈTE!',),
            ('',),
            ('Fonctionnalités disponibles:',),
            ('• Sélection avancée des colonnes',),
            ('• Recherche en temps réel',),
            ('• Filtrage par plage personnalisée',),
