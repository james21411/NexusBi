#!/usr/bin/env python3
"""
Script d'initialisation de la base de données SQLite
Crée toutes les tables et un utilisateur par défaut
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.core.security import get_password_hash


def init_database():
    """Initialise la base de données avec toutes les tables"""
    
    # Créer le moteur de base de données
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
    
    # Créer toutes les tables
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Créer un utilisateur par défaut si il n'existe pas
        from app.models.user import User
        from app.models.project import Project
        
        # Vérifier si un utilisateur existe déjà
        existing_user = db.query(User).first()
        if not existing_user:
            print("Création de l'utilisateur par défaut...")
            
            # Créer l'utilisateur par défaut
            default_user = User(
                email="admin@nexusbi.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrateur NexusBi",
                is_active=True,
                is_superuser=True
            )
            db.add(default_user)
            db.flush()  # Pour obtenir l'ID
            
            # Créer un projet par défaut
            default_project = Project(
                name="Projet Principal",
                description="Projet principal pour les tests",
                owner_id=default_user.id,
                is_active=True
            )
            db.add(default_project)
            db.commit()
            
            print("✅ Utilisateur et projet par défaut créés")
            print("   Email: admin@nexusbi.com")
            print("   Mot de passe: admin123")
            print(f"   Projet ID: {default_project.id}")
        else:
            print("✅ Utilisateur par défaut déjà existant")
            
        print("✅ Base de données initialisée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Initialisation de la base de données NexusBi...")
    init_database()
    print("✨ Terminé!")