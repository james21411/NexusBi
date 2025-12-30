#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface tkinter pour les statistiques avancées de NexusBi
Équivalent tkinter de l'interface de visualisation de données
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import threading
import os
import time
from datetime import datetime
import traceback
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns


class StatisticsTkinter:
    def __init__(self, data_source_id: int = None, api_base_url: str = "http://localhost:8000", auth_token: str = None, stats_file: str = None):
        self.data_source_id = data_source_id
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.stats_data = {}
        self.data_source = None
        self.window_created = False
        self.initialization_error = None
        self.stats_file = stats_file

        # Configuration
        self.current_tab = "overview"

        # Tentative de création de l'interface
        try:
            self.setup_ui()
            if not self.window_created:
                raise Exception("La fenêtre n'a pas pu être créée")
        except Exception as e:
            self.initialization_error = str(e)
            print(f"❌ Erreur lors de l'initialisation: {e}")
            self.create_fallback_interface()

    def setup_ui(self):
        """Configure l'interface utilisateur tkinter pour les statistiques"""
        print("🔧 Création de la fenêtre tkinter des statistiques...")

        try:
            self.root = tk.Tk()
            self.root.title("Statistiques Avancées - NexusBi")
            self.root.geometry("1400x900")
            self.root.minsize(1200, 700)

            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
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

            print("✅ Style configuré")

        except Exception as e:
            print(f"⚠️ Erreur configuration style: {e}")

        try:
            # Frame principal
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)

            print("✅ Grille principale configurée")

        except Exception as e:
            print(f"❌ Erreur création frame principal: {e}")
            raise e

        try:
            # Frame de titre et boutons
            title_frame = ttk.Frame(main_frame)
            title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            title_frame.columnconfigure(1, weight=1)

            # Titre
            self.title_label = ttk.Label(
                title_frame,
                text="Statistiques Avancées - NexusBi",
                style='Title.TLabel'
            )
            self.title_label.grid(row=0, column=0, sticky=tk.W)

            # Boutons
            button_frame = ttk.Frame(title_frame)
            button_frame.grid(row=0, column=1, sticky=tk.E)

            ttk.Button(button_frame, text="Actualiser", command=self.refresh_stats, style='Accent.TButton').grid(row=0, column=0, padx=(0, 5))
            ttk.Button(button_frame, text="Exporter", command=self.export_stats, style='Accent.TButton').grid(row=0, column=1, padx=(0, 5))
            ttk.Button(button_frame, text="Fermer", command=self.close_window).grid(row=0, column=2)

            print("✅ Titre et boutons créés")

        except Exception as e:
            print(f"❌ Erreur création titre/boutons: {e}")
            raise e

        try:
            # Notebook pour les onglets
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Créer les onglets
            self.overview_frame = ttk.Frame(self.notebook, padding="10")
            self.descriptive_frame = ttk.Frame(self.notebook, padding="10")
            self.quality_frame = ttk.Frame(self.notebook, padding="10")
            self.distributions_frame = ttk.Frame(self.notebook, padding="10")
            self.correlations_frame = ttk.Frame(self.notebook, padding="10")

            self.notebook.add(self.overview_frame, text="Vue d'ensemble")
            self.notebook.add(self.descriptive_frame, text="Statistiques Descriptives")
            self.notebook.add(self.quality_frame, text="Qualité des Données")
            self.notebook.add(self.distributions_frame, text="Distributions")
            self.notebook.add(self.correlations_frame, text="Corrélations")

            self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

            print("✅ Onglets créés")

        except Exception as e:
            print(f"❌ Erreur création onglets: {e}")
            raise e

        try:
            # Frame de statut
            status_frame = ttk.Frame(main_frame)
            status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            status_frame.columnconfigure(0, weight=1)

            self.status_label = ttk.Label(status_frame, text="Prêt - Interface Statistiques Initialisée", relief=tk.SUNKEN)
            self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

            print("✅ Statut créé")

        except Exception as e:
            print(f"❌ Erreur création statut: {e}")
            raise e

        try:
            # Initialiser les onglets
            self.setup_overview_tab()
            self.setup_descriptive_tab()
            self.setup_quality_tab()
            self.setup_distributions_tab()
            self.setup_correlations_tab()

            print("✅ Interface statistiques créée avec succès")

            # Charger les données selon le mode d'initialisation
            if self.stats_file:
                self.load_statistics_from_file()
            elif self.data_source_id:
                self.load_statistics()
            else:
                self.show_welcome_message()

            self.window_created = True

        except Exception as e:
            print(f"❌ Erreur finalisation interface: {e}")
            raise e

    def setup_overview_tab(self):
        """Configure l'onglet Vue d'ensemble"""
        # Statistiques clés
        stats_frame = ttk.LabelFrame(self.overview_frame, text="Métriques Principales", padding="10")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        stats_frame.columnconfigure(0, weight=1)

        # Grille pour les métriques
        metrics_frame = ttk.Frame(stats_frame)
        metrics_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Métriques (seront remplies avec les vraies données)
        self.metrics_labels = {}
        metrics = [
            ("Variables Numériques", "numeric_cols"),
            ("Variables Catégorielles", "categorical_cols"),
            ("Données Manquantes", "missing_values"),
            ("Total Lignes", "total_rows")
        ]

        for i, (label, key) in enumerate(metrics):
            row = i // 2
            col = i % 2

            frame = ttk.Frame(metrics_frame, relief="ridge", borderwidth=2)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))

            ttk.Label(frame, text=label, font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2)
            self.metrics_labels[key] = ttk.Label(frame, text="0", font=('Segoe UI', 14, 'bold'), foreground='#0056D2')
            self.metrics_labels[key].grid(row=1, column=0, padx=5, pady=2)

        # Aperçu des statistiques descriptives
        preview_frame = ttk.LabelFrame(self.overview_frame, text="Aperçu des Statistiques Descriptives", padding="10")
        preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, font=('Courier', 9))
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_descriptive_tab(self):
        """Configure l'onglet Statistiques Descriptives"""
        # Table des statistiques descriptives
        table_frame = ttk.LabelFrame(self.descriptive_frame, text="Statistiques Descriptives (Équivalent R summary())", padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview pour les statistiques
        self.descriptive_tree = ttk.Treeview(table_frame)
        self.descriptive_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.descriptive_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.descriptive_tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.descriptive_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.descriptive_tree.configure(xscrollcommand=h_scrollbar.set)

        # Note explicative
        note_frame = ttk.Frame(self.descriptive_frame)
        note_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(note_frame, text="* Cette table correspond à la fonction summary() de R et describe() de pandas",
                 font=('Segoe UI', 8), foreground='#666666').grid(row=0, column=0, sticky=tk.W)

    def setup_quality_tab(self):
        """Configure l'onglet Qualité des Données"""
        # Frame principal avec deux colonnes
        main_frame = ttk.Frame(self.quality_frame)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Valeurs manquantes
        missing_frame = ttk.LabelFrame(main_frame, text="Valeurs Manquantes", padding="10")
        missing_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        missing_frame.columnconfigure(0, weight=1)
        missing_frame.rowconfigure(0, weight=1)

        self.missing_tree = ttk.Treeview(missing_frame, columns=('Colonne', 'Count', 'Pourcentage'), show='headings', height=8)
        self.missing_tree.heading('Colonne', text='Colonne')
        self.missing_tree.heading('Count', text='Nombre')
        self.missing_tree.heading('Pourcentage', text='Pourcentage')
        self.missing_tree.column('Colonne', width=150)
        self.missing_tree.column('Count', width=80)
        self.missing_tree.column('Pourcentage', width=100)
        self.missing_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Outliers
        outliers_frame = ttk.LabelFrame(main_frame, text="Valeurs Aberrantes (Outliers)", padding="10")
        outliers_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        outliers_frame.columnconfigure(0, weight=1)
        outliers_frame.rowconfigure(0, weight=1)

        self.outliers_tree = ttk.Treeview(outliers_frame, columns=('Colonne', 'Count', 'Pourcentage', 'Bounds'), show='headings', height=8)
        self.outliers_tree.heading('Colonne', text='Colonne')
        self.outliers_tree.heading('Count', text='Nombre')
        self.outliers_tree.heading('Pourcentage', text='Pourcentage')
        self.outliers_tree.heading('Bounds', text='Limites')
        self.outliers_tree.column('Colonne', width=150)
        self.outliers_tree.column('Count', width=80)
        self.outliers_tree.column('Pourcentage', width=100)
        self.outliers_tree.column('Bounds', width=120)
        self.outliers_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_distributions_tab(self):
        """Configure l'onglet Distributions"""
        # Frame principal
        main_frame = ttk.Frame(self.distributions_frame)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Contrôles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(control_frame, text="Variable:", style='Control.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.dist_var = tk.StringVar()
        self.dist_combo = ttk.Combobox(control_frame, textvariable=self.dist_var, state="readonly", width=30)
        self.dist_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        self.dist_combo.bind('<<ComboboxSelected>>', self.on_distribution_change)

        ttk.Button(control_frame, text="Générer Graphique", command=self.generate_distribution_plot, style='Accent.TButton').grid(row=0, column=2)

        # Frame pour le graphique
        plot_frame = ttk.LabelFrame(main_frame, text="Distribution", padding="10")
        plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        self.plot_frame = ttk.Frame(plot_frame)
        self.plot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def setup_correlations_tab(self):
        """Configure l'onglet Corrélations"""
        # Frame principal
        main_frame = ttk.Frame(self.correlations_frame)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Matrice de corrélation
        matrix_frame = ttk.LabelFrame(main_frame, text="Matrice de Corrélation", padding="10")
        matrix_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        matrix_frame.columnconfigure(0, weight=1)
        matrix_frame.rowconfigure(0, weight=1)

        self.corr_tree = ttk.Treeview(matrix_frame)
        self.corr_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(matrix_frame, orient=tk.VERTICAL, command=self.corr_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.corr_tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(matrix_frame, orient=tk.HORIZONTAL, command=self.corr_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.corr_tree.configure(xscrollcommand=h_scrollbar.set)

        # Graphiques de dispersion
        scatter_frame = ttk.LabelFrame(main_frame, text="Graphiques de Dispersion (Corrélations Fortes)", padding="10")
        scatter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scatter_frame.columnconfigure(0, weight=1)
        scatter_frame.rowconfigure(0, weight=1)

        self.scatter_frame = ttk.Frame(scatter_frame)
        self.scatter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_fallback_interface(self):
        """Crée une interface de fallback en cas d'erreur"""
        print("🔧 Création d'une interface de fallback pour les statistiques...")

        try:
            self.root = tk.Tk()
            self.root.title("Interface Statistiques - Mode Dépannage")
            self.root.geometry("800x600")

            main_frame = ttk.Frame(self.root, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            error_text = f"""
Erreur lors de l'initialisation de l'interface statistiques:

{self.initialization_error}

Interface de dépannage activée.

Configuration système:
- DISPLAY: {os.getenv('DISPLAY', 'Non définie')}
- Utilisateur: {os.getenv('USER', 'inconnu')}
- Time: {datetime.now().strftime('%H:%M:%S')}
            """

            error_label = ttk.Label(main_frame, text=error_text, justify=tk.LEFT, font=("Courier", 9))
            error_label.pack(pady=10)

            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)

            ttk.Button(button_frame, text="Test Statistiques", command=self.test_statistics).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Fermer", command=self.close_window, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

            self.window_created = True

        except Exception as e:
            print(f"❌ Erreur création fallback: {e}")

    def test_statistics(self):
        """Test des fonctionnalités statistiques"""
        messagebox.showinfo("Test Statistiques",
                          "Interface tkinter pour les statistiques opérationnelle!\n\n"
                          "Fonctionnalités disponibles:\n"
                          "• Statistiques descriptives (comme R summary())\n"
                          "• Analyse de la qualité des données\n"
                          "• Visualisations des distributions\n"
                          "• Matrices de corrélation\n"
                          "• Graphiques de dispersion")

    def load_statistics(self):
        """Charge les statistiques depuis l'API"""
        try:
            self.status_label.config(text="Chargement des statistiques...")

            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'

            # Charger les statistiques
            response = requests.get(f"{self.api_base_url}/data-sources/{self.data_source_id}/statistics",
                                  headers=headers, timeout=30)

            if response.status_code == 200:
                self.stats_data = response.json()
                self.update_ui_with_data()
                self.status_label.config(text="Statistiques chargées avec succès")
            else:
                raise Exception(f"Erreur API: {response.status_code}")

        except Exception as e:
            self.status_label.config(text=f"Erreur de chargement: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de charger les statistiques:\n{str(e)}")

    def load_statistics_from_file(self):
        """Charge les statistiques depuis un fichier JSON"""
        try:
            self.status_label.config(text="Chargement des statistiques depuis le fichier...")

            if not self.stats_file or not os.path.exists(self.stats_file):
                raise Exception(f"Fichier de statistiques non trouvé: {self.stats_file}")

            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats_data = json.load(f)

            self.update_ui_with_data()
            self.status_label.config(text="Statistiques chargées depuis le fichier avec succès")
            
            # Nettoyer le fichier temporaire après chargement
            try:
                os.unlink(self.stats_file)
            except:
                pass

        except Exception as e:
            self.status_label.config(text=f"Erreur de chargement du fichier: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible de charger les statistiques depuis le fichier:\n{str(e)}")

    def update_ui_with_data(self):
        """Met à jour l'interface avec les données chargées"""
        try:
            # Mettre à jour les métriques principales
            numeric_cols = 0
            categorical_cols = 0
            
            if 'columns' in self.stats_data:
                columns = self.stats_data['columns']
                if isinstance(columns, list):
                    for col in columns:
                        if isinstance(col, dict) and 'type' in col:
                            col_type = str(col['type']).lower()
                            # Types numériques
                            if any(num_type in col_type for num_type in ['int64', 'float64', 'int32', 'float32', 'int', 'float', 'double', 'number']):
                                numeric_cols += 1
                            # Types catégoriels
                            elif any(cat_type in col_type for cat_type in ['object', 'string', 'varchar', 'text', 'char']):
                                categorical_cols += 1
            
            # Compter les lignes si total_rows est disponible
            total_rows = self.stats_data.get('total_rows', 0)
            if not total_rows and 'summary' in self.stats_data:
                summary = self.stats_data['summary']
                if isinstance(summary, dict) and 'total_rows' in summary:
                    total_rows = summary['total_rows']
            
            # Compter les valeurs manquantes
            missing_count = 0
            if 'descriptive_stats' in self.stats_data:
                desc_stats = self.stats_data['descriptive_stats']
                if isinstance(desc_stats, dict):
                    for var, stats in desc_stats.items():
                        if isinstance(stats, dict) and 'count' in stats:
                            # Le count représente le nombre d'observations non manquantes
                            var_total = self.stats_data.get('summary', {}).get('total_rows', 0)
                            if var_total > 0:
                                missing_count += (var_total - stats.get('count', 0))

            self.metrics_labels['numeric_cols'].config(text=str(numeric_cols))
            self.metrics_labels['categorical_cols'].config(text=str(categorical_cols))
            self.metrics_labels['total_rows'].config(text=str(total_rows))
            self.metrics_labels['missing_values'].config(text=str(missing_count))

            if 'total_rows' in self.stats_data:
                self.metrics_labels['total_rows'].config(text=str(self.stats_data['total_rows']))

            if 'missing_values' in self.stats_data:
                self.metrics_labels['missing_values'].config(text=str(self.stats_data['missing_values']))

            # Mettre à jour l'aperçu des statistiques descriptives
            self.update_descriptive_preview()

            # Mettre à jour les onglets
            self.update_descriptive_tab()
            self.update_quality_tab()
            self.update_distributions_tab()
            self.update_correlations_tab()

        except Exception as e:
            print(f"Erreur mise à jour UI: {e}")

    def update_descriptive_preview(self):
        """Met à jour l'aperçu des statistiques descriptives"""
        try:
            self.preview_text.delete(1.0, tk.END)

            if 'descriptiveStats' in self.stats_data:
                stats = self.stats_data['descriptiveStats']
                if isinstance(stats, dict) and len(stats) > 0:
                    # Prendre les 3 premières variables
                    variables = list(stats.keys())[:3]

                    for var in variables:
                        if var in stats:
                            stat = stats[var]
                            self.preview_text.insert(tk.END, f"{var}:\n")
                            self.preview_text.insert(tk.END, f"  Moyenne: {stat.get('mean', 'N/A')}\n")
                            self.preview_text.insert(tk.END, f"  Médiane: {stat.get('median', 'N/A')}\n")
                            self.preview_text.insert(tk.END, f"  Écart-type: {stat.get('std', 'N/A')}\n")
                            self.preview_text.insert(tk.END, f"  Min: {stat.get('min', 'N/A')}\n")
                            self.preview_text.insert(tk.END, f"  Max: {stat.get('max', 'N/A')}\n\n")
                else:
                    self.preview_text.insert(tk.END, "Aucune statistique descriptive disponible")
            else:
                self.preview_text.insert(tk.END, "Données de statistiques descriptives non disponibles")

        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Erreur affichage aperçu: {str(e)}")

    def update_descriptive_tab(self):
        """Met à jour l'onglet des statistiques descriptives"""
        try:
            # Configurer les colonnes du treeview
            columns = ['Variable', 'Count', 'Mean', 'Std', 'Min', 'Q1', 'Median', 'Q3', 'Max']
            self.descriptive_tree['columns'] = columns
            self.descriptive_tree['show'] = 'headings'

            for col in columns:
                self.descriptive_tree.heading(col, text=col)
                self.descriptive_tree.column(col, width=80)

            # Vider le treeview
            for item in self.descriptive_tree.get_children():
                self.descriptive_tree.delete(item)

            # Ajouter les données
            if 'descriptiveStats' in self.stats_data:
                stats = self.stats_data['descriptiveStats']
                if isinstance(stats, dict):
                    for var, stat in stats.items():
                        values = [
                            var,
                            stat.get('count', ''),
                            f"{stat.get('mean', ''):.2f}" if stat.get('mean') != '' else '',
                            f"{stat.get('std', ''):.2f}" if stat.get('std') != '' else '',
                            stat.get('min', ''),
                            stat.get('q1', ''),
                            stat.get('median', ''),
                            stat.get('q3', ''),
                            stat.get('max', '')
                        ]
                        self.descriptive_tree.insert('', tk.END, values=values)

        except Exception as e:
            print(f"Erreur mise à jour onglet descriptif: {e}")

    def update_quality_tab(self):
        """Met à jour l'onglet qualité des données"""
        try:
            # Valeurs manquantes
            for item in self.missing_tree.get_children():
                self.missing_tree.delete(item)

            if 'missingValues' in self.stats_data:
                missing = self.stats_data['missingValues']
                if isinstance(missing, dict):
                    for col, info in missing.items():
                        if isinstance(info, dict):
                            self.missing_tree.insert('', tk.END, values=[
                                col,
                                info.get('count', 0),
                                f"{info.get('percentage', 0):.1f}%"
                            ])

            # Outliers
            for item in self.outliers_tree.get_children():
                self.outliers_tree.delete(item)

            if 'outliers' in self.stats_data:
                outliers = self.stats_data['outliers']
                if isinstance(outliers, dict):
                    for col, info in outliers.items():
                        if isinstance(info, dict):
                            bounds = info.get('bounds', {})
                            bounds_str = f"[{bounds.get('lower', ''):.1f}, {bounds.get('upper', ''):.1f}]" if bounds else ""
                            self.outliers_tree.insert('', tk.END, values=[
                                col,
                                info.get('count', 0),
                                f"{info.get('percentage', 0):.1f}%",
                                bounds_str
                            ])

        except Exception as e:
            print(f"Erreur mise à jour onglet qualité: {e}")

    def update_distributions_tab(self):
        """Met à jour l'onglet distributions"""
        try:
            # Mettre à jour la liste des variables
            if 'numericData' in self.stats_data:
                variables = list(self.stats_data['numericData'].keys())
                self.dist_combo['values'] = variables
                if variables:
                    self.dist_var.set(variables[0])

        except Exception as e:
            print(f"Erreur mise à jour onglet distributions: {e}")

    def update_correlations_tab(self):
        """Met à jour l'onglet corrélations"""
        try:
            # Configurer la matrice de corrélation
            if 'correlations' in self.stats_data:
                corr = self.stats_data['correlations']
                if isinstance(corr, dict) and len(corr) > 0:
                    variables = list(corr.keys())
                    self.corr_tree['columns'] = ['Variable'] + variables
                    self.corr_tree['show'] = 'headings'

                    for var in ['Variable'] + variables:
                        self.corr_tree.heading(var, text=var)
                        self.corr_tree.column(var, width=80)

                    # Vider le treeview
                    for item in self.corr_tree.get_children():
                        self.corr_tree.delete(item)

                    # Ajouter les données
                    for var1 in variables:
                        row_values = [var1]
                        for var2 in variables:
                            value = corr.get(var1, {}).get(var2, corr.get(var2, {}).get(var1, 0))
                            row_values.append(f"{value:.3f}")
                        self.corr_tree.insert('', tk.END, values=row_values)

        except Exception as e:
            print(f"Erreur mise à jour onglet corrélations: {e}")

    def on_tab_change(self, event):
        """Gère le changement d'onglet"""
        tab_id = self.notebook.index(self.notebook.select())
        tab_names = ['overview', 'descriptive', 'quality', 'distributions', 'correlations']
        self.current_tab = tab_names[tab_id] if tab_id < len(tab_names) else 'overview'

    def on_distribution_change(self, event):
        """Gère le changement de variable pour les distributions"""
        pass

    def generate_distribution_plot(self):
        """Génère un graphique de distribution"""
        try:
            variable = self.dist_var.get()
            if not variable or 'numericData' not in self.stats_data:
                return

            data = self.stats_data['numericData'].get(variable, [])
            if not data:
                return

            # Créer le graphique matplotlib
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.histplot(data, kde=True, ax=ax)
            ax.set_title(f'Distribution de {variable}')
            ax.set_xlabel(variable)
            ax.set_ylabel('Fréquence')

            # Afficher dans tkinter
            for widget in self.plot_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le graphique:\n{str(e)}")

    def refresh_stats(self):
        """Actualise les statistiques"""
        if self.data_source_id:
            self.load_statistics()

    def export_stats(self):
        """Exporte les statistiques"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.stats_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Succès", "Statistiques exportées avec succès!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exporter les statistiques:\n{str(e)}")

    def show_welcome_message(self):
        """Affiche un message d'accueil"""
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "Bienvenue dans l'interface de statistiques avancées!\n\n")
        self.preview_text.insert(tk.END, "Sélectionnez une source de données pour voir ses statistiques.\n\n")
        self.preview_text.insert(tk.END, "Fonctionnalités disponibles:\n")
        self.preview_text.insert(tk.END, "• Statistiques descriptives (équivalent R summary())\n")
        self.preview_text.insert(tk.END, "• Analyse de la qualité des données\n")
        self.preview_text.insert(tk.END, "• Visualisations des distributions\n")
        self.preview_text.insert(tk.END, "• Matrices de corrélation\n")
        self.preview_text.insert(tk.END, "• Graphiques de dispersion")

    def on_closing(self):
        """Gère la fermeture de la fenêtre"""
        if messagebox.askokcancel("Fermer", "Voulez-vous vraiment fermer l'interface statistiques?"):
            self.close_window()

    def close_window(self):
        """Ferme la fenêtre"""
        try:
            if hasattr(self, 'root'):
                self.root.quit()
                self.root.destroy()
        except:
            pass

    def run(self):
        """Lance la boucle principale tkinter"""
        if self.window_created:
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self.close_window()
        else:
            print("❌ Interface non créée - impossible de lancer")


def launch_statistics_interface(data_source_id: int = None, api_base_url: str = "http://localhost:8000", auth_token: str = None, stats_file: str = None):
    """Lance l'interface tkinter des statistiques"""
    try:
        if stats_file:
            print(f"🚀 Lancement de l'interface statistiques depuis le fichier: {stats_file}")
        else:
            print(f"🚀 Lancement de l'interface statistiques pour la source {data_source_id}")

        app = StatisticsTkinter(data_source_id, api_base_url, auth_token, stats_file)
        app.run()

        print("✅ Interface statistiques fermée")
        return True

    except Exception as e:
        print(f"❌ Erreur lancement interface statistiques: {e}")
        return False


if __name__ == "__main__":
    # Test de l'interface
    import sys

    # Premier argument peut être un data_source_id ou un fichier de statistiques
    arg1 = sys.argv[1] if len(sys.argv) > 1 else None
    
    if arg1 and os.path.exists(arg1) and arg1.endswith('.json'):
        # Si le premier argument est un fichier JSON, on l'utilise comme fichier de statistiques
        stats_file = arg1
        data_source_id = None
    elif arg1 and arg1.isdigit():
        # Si le premier argument est un nombre, c'est un data_source_id
        data_source_id = int(arg1)
        stats_file = None
    else:
        data_source_id = None
        stats_file = None
    
    api_base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    auth_token = sys.argv[3] if len(sys.argv) > 3 else None

    launch_statistics_interface(data_source_id, api_base_url, auth_token, stats_file)