#!/usr/bin/env python3
"""
Correction des chemins de fichiers existants
Résout le problème des sources de données qui n'ont que le nom de fichier
"""

import sys
import os
import glob
import shutil
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource


def find_and_move_existing_files():
    """Trouve et déplace les fichiers existants vers UPLOAD_DIR"""
    print("🔍 RECHERCHE ET DÉPLACEMENT DES FICHIERS EXISTANTS")
    print("=" * 70)
    
    from app.core.config import settings
    
    # Créer le répertoire UPLOAD_DIR s'il n'existe pas
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"📁 UPLOAD_DIR: {settings.UPLOAD_DIR}")
    
    # Rechercher des fichiers dans différents emplacements possibles
    search_locations = [
        "/tmp/",
        "/tmp/nexusbi/",
        ".",
        "..",
        "/home/james/Bureau/BUREAU/CODE 17/PROJETS/NexusBi/",
    ]
    
    # Chercher tous les fichiers de données
    data_extensions = ['*.csv', '*.xlsx', '*.xls', '*.json', '*.txt', '*.sql']
    found_files = {}
    
    print("🔍 Recherche des fichiers de données...")
    
    for location in search_locations:
        if os.path.exists(location):
            print(f"   📂 Recherche dans: {location}")
            
            for ext in data_extensions:
                for file_path in glob.glob(os.path.join(location, ext)):
                    filename = os.path.basename(file_path)
                    if filename not in found_files and os.path.isfile(file_path):
                        found_files[filename] = file_path
                        print(f"      ✅ Trouvé: {filename}")
    
    print(f"\n📊 {len(found_files)} fichier(s) de données trouvé(s)")
    
    return found_files, settings.UPLOAD_DIR


def fix_existing_data_sources():
    """Corrige les sources de données existantes avec chemins incorrects"""
    print("\n🔧 CORRECTION DES SOURCES DE DONNÉES EXISTANTES")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Trouver tous les fichiers disponibles
        found_files, upload_dir = find_and_move_existing_files()
        
        if not found_files:
            print("❌ Aucun fichier de données trouvé")
            return False
        
        # Trouver toutes les sources de données
        all_sources = db.query(DataSource).all()
        
        if not all_sources:
            print("❌ Aucune source de données dans la base")
            return False
        
        print(f"📊 {len(all_sources)} source(s) de données dans la base")
        
        fixed_count = 0
        moved_files = 0
        
        for source in all_sources:
            print(f"\n🔧 Source: {source.name} (ID: {source.id})")
            print(f"   📁 Type: {source.type}")
            print(f"   📍 Chemin actuel: {source.file_path}")
            
            if not source.file_path:
                print(f"   ⚠️  Aucun chemin défini")
                continue
            
            filename = os.path.basename(source.file_path)
            
            # Vérifier si on a trouvé le fichier
            if filename in found_files:
                old_path = source.file_path
                source_path = found_files[filename]
                
                # Vérifier si le fichier est déjà au bon endroit
                if source_path == source.file_path:
                    print(f"   ✅ Déjà au bon endroit: {source_path}")
                    continue
                
                # Déplacer le fichier vers UPLOAD_DIR si nécessaire
                if not source_path.startswith(upload_dir):
                    import uuid
                    file_id = str(uuid.uuid4())
                    safe_filename = f"{file_id}_{filename}"
                    new_path = os.path.join(upload_dir, safe_filename)
                    
                    try:
                        shutil.move(source_path, new_path)
                        print(f"   📦 Déplacé: {source_path} -> {new_path}")
                        moved_files += 1
                        source.file_path = new_path
                    except Exception as e:
                        print(f"   ❌ Erreur déplacement: {e}")
                        # Si le déplacement échoue, utiliser le chemin existant
                        source.file_path = source_path
                else:
                    source.file_path = source_path
                
                print(f"   ✅ CORRIGÉ: {old_path}")
                print(f"   ✅ NOUVEAU: {source.file_path}")
                
                # Vérifier que le fichier existe
                if os.path.exists(source.file_path):
                    size = os.path.getsize(source.file_path)
                    print(f"   📏 Taille: {size:,} octets ({size/1024/1024:.1f} MB)")
                    fixed_count += 1
                else:
                    print(f"   ❌ Fichier still manquant: {source.file_path}")
            else:
                print(f"   ❌ Fichier non trouvé: {filename}")
                
                # Proposer des alternatives
                similar_files = [f for f in found_files.keys() if filename.lower() in f.lower() or f.lower() in filename.lower()]
                if similar_files:
                    print(f"   💡 Fichiers similaires: {similar_files[:3]}")
        
        # Sauvegarder les changements
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ {fixed_count} source(s) corrigée(s)")
            if moved_files > 0:
                print(f"📦 {moved_files} fichier(s) déplacé(s) vers UPLOAD_DIR")
            return True
        else:
            print(f"\n⚠️ Aucune source corrigée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_file_paths():
    """Vérifie que tous les fichiers sont accessibles"""
    print("\n✅ VÉRIFICATION DES CHEMINS DE FICHIERS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        all_sources = db.query(DataSource).all()
        
        accessible_count = 0
        inaccessible_count = 0
        
        for source in all_sources:
            if source.file_path:
                exists = os.path.exists(source.file_path)
                status = "✅ ACCESSIBLE" if exists else "❌ INACCESSIBLE"
                
                print(f"📁 {source.name} ({source.type}): {status}")
                print(f"   📍 {source.file_path}")
                
                if exists:
                    size = os.path.getsize(source.file_path)
                    print(f"   📏 Taille: {size:,} octets ({size/1024/1024:.1f} MB)")
                    accessible_count += 1
                else:
                    inaccessible_count += 1
        
        print(f"\n📊 RÉSUMÉ: {accessible_count} fichiers accessibles, {inaccessible_count} inaccessibles")
        
        return accessible_count > 0
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """Fonction principale"""
    print("🚀 CORRECTION DES CHEMINS DE FICHIERS EXISTANTS")
    print("=" * 80)
    print("Ce script va:")
    print("1. 🔍 Rechercher tous les fichiers de données sur le système")
    print("2. 📦 Déplacer les fichiers vers UPLOAD_DIR")
    print("3. 🔧 Corriger les chemins dans la base de données")
    print("4. ✅ Vérifier que tous les fichiers sont accessibles")
    print("=" * 80)
    
    # Corriger les sources existantes
    success = fix_existing_data_sources()
    
    # Vérifier les chemins
    verify_file_paths()
    
    # Résumé
    print(f"\n{'='*80}")
    print("🏁 RÉSUMÉ")
    print(f"{'='*80}")
    
    if success:
        print("✅ SUCCÈS: Les chemins de fichiers ont été corrigés")
        print("🔄 Vous pouvez maintenant tester la synchronisation:")
        print("   python backend/force_sql_dump_sync.py")
        print("   ou")
        print("   python backend/complete_sql_dump_fix.py")
    else:
        print("⚠️ ATTENTION: Certains fichiers n'ont pas pu être corrigés")
        print("💡 Vérifiez manuellement l'emplacement de vos fichiers")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
