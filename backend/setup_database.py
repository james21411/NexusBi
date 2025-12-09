#!/usr/bin/env python3
"""
Setup automatique de la base de données SQLite NexusBi
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.db.base import Base
    from app.models.user import User
    from app.models.project import Project
    from app.models.project import DataSource
    from app.core.security import get_password_hash
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que les dépendances sont installées")
    sys.exit(1)

def setup_database():
    """Configure la base de données"""
    
    print(f"📁 Base de données: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Créer le moteur de base de données
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    
    # Créer toutes les tables
    print("🏗️  Création des tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier si des utilisateurs existent
        user_count = db.query(User).count()
        project_count = db.query(Project).count()
        data_source_count = db.query(DataSource).count()
        
        print(f"👥 Utilisateurs: {user_count}")
        print(f"🏗️  Projets: {project_count}")
        print(f"📊 Sources de données: {data_source_count}")
        
        # Créer l'utilisateur par défaut si nécessaire
        if user_count == 0:
            print("👤 Création de l'utilisateur par défaut...")
            
            default_user = User(
                email="admin@nexusbi.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrateur NexusBi",
                is_active=True,
                is_superuser=True
            )
            db.add(default_user)
            db.flush()  # Pour obtenir l'ID
            
            # Créer le projet par défaut
            default_project = Project(
                name="Projet Principal",
                description="Projet principal pour les tests et développement",
                owner_id=default_user.id,
                is_active=True
            )
            db.add(default_project)
            db.commit()
            
            print("✅ Utilisateur et projet par défaut créés")
            print("   📧 Email: admin@nexusbi.com")
            print("   🔑 Mot de passe: admin123")
            print(f"   🏗️  Projet ID: {default_project.id}")
        
        # Ajouter des sources de données de démonstration si aucune n'existe
        if data_source_count == 0 and project_count > 0:
            print("📊 Ajout de sources de données de démonstration...")
            
            project = db.query(Project).first()
            
            demo_sources = [
                DataSource(
                    name="Base Production MySQL",
                    type="MySQL",
                    project_id=project.id,
                    is_active=True
                ),
                DataSource(
                    name="Azure Cloud Storage",
                    type="Cloud",
                    project_id=project.id,
                    is_active=True
                ),
                DataSource(
                    name="PostgreSQL Analytics",
                    type="PostgreSQL",
                    project_id=project.id,
                    is_active=True
                ),
                DataSource(
                    name="Local Data Warehouse",
                    type="SQL Server",
                    project_id=project.id,
                    is_active=True
                )
            ]
            
            for source in demo_sources:
                db.add(source)
            
            db.commit()
            print("✅ Sources de données de démonstration ajoutées")
        
        print("✨ Base de données configurée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def check_database():
    """Vérifie l'état de la base de données"""
    
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            # Vérifier les tables
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """))
            tables = [row[0] for row in result]
            
            print("📋 Tables dans la base de données:")
            for table in tables:
                print(f"   - {table}")
            
            # Compter les enregistrements
            for table in ['users', 'projects', 'data_sources']:
                if table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"   {table}: {count} enregistrements")
                    
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    print("🚀 Configuration de la base de données NexusBi...")
    print("=" * 50)
    
    success = setup_database()
    
    print("\n" + "=" * 50)
    print("📊 État de la base de données:")
    check_database()
    
    if success:
        print("\n✅ Configuration terminée avec succès!")
        print("🎯 Vous pouvez maintenant utiliser l'application")
    else:
        print("\n❌ Échec de la configuration")
        sys.exit(1)