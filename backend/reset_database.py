#!/usr/bin/env python3
"""
Script pour recréer complètement la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base

def reset_database():
    """Recréer complètement la base de données"""
    print("🔄 Recréation de la base de données...")

    # Créer le moteur de base de données
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    try:
        # Supprimer toutes les tables
        print("🗑️  Suppression des tables existantes...")
        Base.metadata.drop_all(bind=engine)

        # Recréer toutes les tables
        print("🏗️  Création des nouvelles tables...")
        Base.metadata.create_all(bind=engine)

        print("✅ Base de données recréée avec succès!")

    except Exception as e:
        print(f"❌ Erreur lors de la recréation: {e}")

if __name__ == "__main__":
    reset_database()