#!/usr/bin/env python3
"""
Script simple pour créer la base de données SQLite et les tables
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.core.security import get_password_hash

def create_database():
    """Crée la base de données et les tables"""
    
    print(f"📁 Base de données: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Créer le moteur
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    # Créer toutes les tables
    print("🏗️  Création des tables...")
    Base.metadata.create_all(bind=engine)
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(User).first()
        if not user:
            print("👤 Création de l'utilisateur par défaut...")
            
            # Créer l'utilisateur
            default_user = User(
                email="admin@nexusbi.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrateur",
                is_active=True,
                is_superuser=True
            )
            db.add(default_user)
            db.flush()  # Pour obtenir l'ID
            
            # Créer le projet par défaut
            project = Project(
                name="Projet Principal",
                description="Projet principal pour les tests",
                owner_id=default_user.id,
                is_active=True
            )
            db.add(project)
            db.commit()
            
            print("✅ Utilisateur et projet créés!")
            print(f"   📧 Email: admin@nexusbi.com")
            print(f"   🔑 Mot de passe: admin123")
            print(f"   🏗️  Projet ID: {project.id}")
        else:
            print("✅ Base de données déjà initialisée")
            
        print("✨ Base de données prête!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données NexusBi...")
    create_database()