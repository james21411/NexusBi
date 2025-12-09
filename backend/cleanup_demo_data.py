#!/usr/bin/env python3
"""
Script pour supprimer toutes les données de démonstration de la base de données
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.project import Project, DataSource

def cleanup_demo_data():
    """Supprime toutes les données de démonstration"""
    print("🧹 Nettoyage des données de démonstration...")

    # Créer le moteur de base de données
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Supprimer dans l'ordre pour respecter les contraintes de clés étrangères
        demo_sources_count = db.query(DataSource).count()
        demo_projects_count = db.query(Project).count()
        demo_users_count = db.query(User).count()

        print(f"📊 Trouvé {demo_sources_count} sources, {demo_projects_count} projets, {demo_users_count} utilisateurs")

        # Supprimer toutes les sources de données
        db.query(DataSource).delete()
        print("✅ Sources de données supprimées")

        # Supprimer tous les projets
        db.query(Project).delete()
        print("✅ Projets supprimés")

        # Supprimer tous les utilisateurs
        db.query(User).delete()
        print("✅ Utilisateurs supprimés")

        # Commit les changements
        db.commit()
        print("🎉 Nettoyage terminé avec succès!")

    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_demo_data()