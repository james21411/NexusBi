#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration pour l'interface tkinter des statistiques NexusBi
Génère des données de démonstration et lance l'interface tkinter
"""

import json
import tempfile
import os
import sys
from statistics_tkinter import launch_statistics_interface


def generate_demo_statistics():
    """Génère des statistiques de démonstration"""
    
    demo_stats = {
        "source_id": 1,
        "source_name": "Démonstration - Dataset Employés",
        "summary": {
            "total_rows": 150,
            "total_columns": 8,
            "memory_usage": "12.5 KB",
            "data_types": {
                "int64": 3,
                "float64": 2, 
                "object": 3
            }
        },
        "descriptive_stats": {
            "age": {
                "count": 150,
                "mean": 35.7,
                "std": 8.9,
                "min": 22,
                "25%": 28.0,
                "50%": 35.0,
                "75%": 42.0,
                "max": 58
            },
            "salary": {
                "count": 150,
                "mean": 52000.0,
                "std": 12500.0,
                "min": 35000,
                "25%": 42000.0,
                "50%": 51000.0,
                "75%": 61000.0,
                "max": 85000
            },
            "experience_years": {
                "count": 150,
                "mean": 8.2,
                "std": 4.5,
                "min": 0,
                "25%": 4.0,
                "50%": 7.0,
                "75%": 12.0,
                "max": 20
            },
            "performance_score": {
                "count": 150,
                "mean": 7.8,
                "std": 1.2,
                "min": 5.0,
                "25%": 7.0,
                "50%": 8.0,
                "75%": 9.0,
                "max": 10.0
            },
            "department": {
                "count": 150,
                "unique": 5,
                "top": "IT",
                "freq": 45
            },
            "education_level": {
                "count": 150,
                "unique": 4,
                "top": "Bachelor",
                "freq": 65
            },
            "gender": {
                "count": 150,
                "unique": 2,
                "top": "Female",
                "freq": 78
            },
            "location": {
                "count": 150,
                "unique": 3,
                "top": "Paris",
                "freq": 70
            }
        },
        "numeric_data": {
            "age": [22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58] * 10,
            "salary": [35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 85000] * 14,
            "experience_years": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] * 7,
            "performance_score": [5.0, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0] * 15
        },
        "missing_values": {
            "age": {"count": 2, "percentage": 1.3},
            "salary": {"count": 3, "percentage": 2.0},
            "experience_years": {"count": 1, "percentage": 0.7},
            "performance_score": {"count": 0, "percentage": 0.0},
            "department": {"count": 5, "percentage": 3.3},
            "education_level": {"count": 2, "percentage": 1.3},
            "gender": {"count": 0, "percentage": 0.0},
            "location": {"count": 1, "percentage": 0.7}
        },
        "outliers": {
            "age": {
                "count": 3,
                "percentage": 2.0,
                "bounds": {"lower": 17.5, "upper": 52.5}
            },
            "salary": {
                "count": 4,
                "percentage": 2.7,
                "bounds": {"lower": 22750.0, "upper": 80250.0}
            },
            "experience_years": {
                "count": 2,
                "percentage": 1.3,
                "bounds": {"lower": -8.0, "upper": 20.0}
            },
            "performance_score": {
                "count": 1,
                "percentage": 0.7,
                "bounds": {"lower": 4.5, "upper": 10.5}
            }
        },
        "correlations": {
            "age": {
                "age": 1.000,
                "salary": 0.78,
                "experience_years": 0.85,
                "performance_score": 0.45
            },
            "salary": {
                "age": 0.78,
                "salary": 1.000,
                "experience_years": 0.82,
                "performance_score": 0.52
            },
            "experience_years": {
                "age": 0.85,
                "salary": 0.82,
                "experience_years": 1.000,
                "performance_score": 0.38
            },
            "performance_score": {
                "age": 0.45,
                "salary": 0.52,
                "experience_years": 0.38,
                "performance_score": 1.000
            }
        },
        "data_quality": {
            "completeness": 97.3,
            "accuracy": 94.2,
            "consistency": 96.8,
            "validity": 98.1
        }
    }
    
    return demo_stats


def main():
    """Fonction principale"""
    print("🎭 Génération des données de démonstration pour les statistiques...")
    
    try:
        # Générer les données de démonstration
        demo_stats = generate_demo_statistics()
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(demo_stats, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name
        
        print(f"📊 Données de démonstration générées: {len(demo_stats)} métriques")
        print(f"📁 Fichier temporaire créé: {temp_file_path}")
        
        # Vérifier la variable DISPLAY
        display = os.getenv('DISPLAY')
        if not display:
            print("⚠️  Variable DISPLAY non définie - tentative de lancement anyway...")
        
        # Lancer l'interface tkinter
        print("🚀 Lancement de l'interface tkinter des statistiques...")
        
        success = launch_statistics_interface(
            data_source_id=None,
            api_base_url="http://localhost:8000",
            auth_token=None,
            stats_file=temp_file_path
        )
        
        if success:
            print("✅ Démonstration terminée avec succès")
        else:
            print("❌ Erreur lors de la démonstration")
        
        # Nettoyer le fichier temporaire
        try:
            os.unlink(temp_file_path)
            print("🧹 Fichier temporaire supprimé")
        except:
            print("⚠️  Impossible de supprimer le fichier temporaire")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
