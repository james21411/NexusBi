#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration pour l'interface tkinter de prévisualisation des données
Ce script crée des données de test et lance l'interface tkinter
"""

import json
import random
import string
from datetime import datetime, timedelta
from data_preview_tkinter import DataPreviewTkinter


def generate_sample_data(num_rows=1000):
    """Génère des données d'exemple pour la démonstration"""
    
    # Noms de personnes
    first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Michel', 'Anne', 'Luc', 'Catherine', 'Paul', 'Isabelle',
                   'David', 'Nathalie', 'Thomas', 'Sandrine', 'Nicolas', 'Sylvie', 'Christophe', 'Valérie', 'Sébastien', 'Véronique']
    last_names = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau',
                  'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'David', 'Bertrand', 'Roux', 'Vincent', 'Fournier']
    
    # Villes françaises
    cities = ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille',
              'Rennes', 'Reims', 'Le Havre', 'Saint-Étienne', 'Toulon', 'Grenoble', 'Dijon', 'Angers', 'Nîmes', 'Villeurbanne']
    
    # Départements
    departments = ['75', '69', '13', '31', '06', '44', '67', '34', '33', '59',
                   '35', '51', '76', '42', '83', '38', '21', '49', '30', '69']
    
    # Produits
    products = ['Ordinateur portable', 'Smartphone', 'Tablette', 'Écouteurs', 'Montre connectée',
                'Appareil photo', 'Console de jeu', 'Téléviseur', 'Réfrigérateur', 'Machine à laver',
                'Aspirateur', 'Four micro-ondes', 'Cafetière', 'Grille-pain', 'Mixeur']
    
    # Couleurs
    colors = ['Rouge', 'Bleu', 'Vert', 'Jaune', 'Noir', 'Blanc', 'Gris', 'Orange', 'Violet', 'Rose']
    
    data = []
    
    for i in range(num_rows):
        # Date aléatoire dans les 2 dernières années
        days_ago = random.randint(0, 730)
        random_date = datetime.now() - timedelta(days=days_ago)
        
        row = {
            'id': i + 1,
            'nom': random.choice(first_names),
            'prenom': random.choice(last_names),
            'age': random.randint(18, 80),
            'ville': random.choice(cities),
            'departement': random.choice(departments),
            'salaire': random.randint(20000, 100000),
            'date_embauche': random_date.strftime('%Y-%m-%d'),
            'produit_achete': random.choice(products),
            'couleur_preferee': random.choice(colors),
            'note_satisfaction': random.randint(1, 10),
            'est_actif': random.choice([True, False]),
            'nombre_commandes': random.randint(0, 50),
            'montant_total': round(random.uniform(0, 5000), 2),
            'commentaire': ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=random.randint(10, 100)))
        }
        
        data.append(row)
    
    return data


def create_demo_data_source():
    """Crée une structure de source de données de démonstration"""
    return {
        'id': 999,
        'name': 'Démonstration - Données Clients',
        'type': 'csv',
        'description': 'Données de démonstration pour tester l\'interface tkinter',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'is_active': True,
        'schema_info': json.dumps({
            'column_count': 15,
            'processing_info': {
                'detected_encoding': 'utf-8',
                'detected_delimiter': ','
            },
            'columns': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'nom', 'type': 'string'},
                {'name': 'prenom', 'type': 'string'},
                {'name': 'age', 'type': 'integer'},
                {'name': 'ville', 'type': 'string'},
                {'name': 'departement', 'type': 'string'},
                {'name': 'salaire', 'type': 'integer'},
                {'name': 'date_embauche', 'type': 'date'},
                {'name': 'produit_achete', 'type': 'string'},
                {'name': 'couleur_preferee', 'type': 'string'},
                {'name': 'note_satisfaction', 'type': 'integer'},
                {'name': 'est_actif', 'type': 'boolean'},
                {'name': 'nombre_commandes', 'type': 'integer'},
                {'name': 'montant_total', 'type': 'float'},
                {'name': 'commentaire', 'type': 'text'}
            ]
        })
    }


class DemoDataPreviewTkinter(DataPreviewTkinter):
    """Version de démonstration de l'interface tkinter avec données locales"""
    
    def __init__(self):
        # Créer des données de démonstration
        self.demo_data = generate_sample_data(1000)
        self.demo_data_source = create_demo_data_source()
        self.total_rows = len(self.demo_data)
        
        # Initialiser sans se connecter à l'API
        super().__init__(data_source_id=None, api_base_url="", auth_token=None)
        
        # Remplacer les méthodes de chargement de données
        self.data = self.demo_data
        self.data_source = self.demo_data_source
        self.schema = json.loads(self.demo_data_source['schema_info'])
        self.visible_columns = list(self.data[0].keys())[:10]  # 10 premières colonnes
        
        # Mettre à jour l'affichage
        self.update_display()
        self.update_status(f"Données de démonstration chargées: {len(self.data)} lignes")
    
    def load_data(self):
        """Remplacer le chargement par des données locales"""
        # Les données sont déjà chargées dans __init__
        pass
    
    def refresh_data(self):
        """Actualiser avec de nouvelles données aléatoires"""
        self.demo_data = generate_sample_data(1000)
        self.data = self.demo_data
        self.total_rows = len(self.demo_data)
        self.update_display()
        self.update_status(f"Données actualisées: {len(self.demo_data)} lignes")


def main():
    """Fonction principale pour lancer la démonstration"""
    print("=== Démonstration de l'Interface tkinter ===")
    print()
    print("Cette démonstration lance une interface tkinter avec des données fictives.")
    print("Vous pouvez tester toutes les fonctionnalités sans avoir besoin du backend.")
    print()
    print("Fonctionnalités disponibles :")
    print("- Affichage de 1000 lignes de données clients")
    print("- Filtres par mode d'affichage (premières/dernières/plage)")
    print("- Recherche dans toutes les colonnes")
    print("- Sélection des colonnes à afficher")
    print("- Export des données filtrées en CSV")
    print("- Actualisation avec de nouvelles données")
    print()
    
    try:
        # Try to get user input, but continue automatically if not available
        try:
            input("Appuyez sur Entrée pour lancer la démonstration...")
        except EOFError:
            print("\nAucune entrée détectée - lancement automatique...")
         
        print("\nLancement de l'interface tkinter...")
        
        # Créer et lancer l'interface de démonstration
        demo_app = DemoDataPreviewTkinter()
        demo_app.run()
        
        print("\nDémonstration terminée. Merci d'avoir testé l'interface tkinter!")
        
    except KeyboardInterrupt:
        print("\n\nDémonstration interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\nErreur lors de la démonstration: {e}")
        print("Vérifiez que tkinter est installé et disponible.")


if __name__ == "__main__":
    main()