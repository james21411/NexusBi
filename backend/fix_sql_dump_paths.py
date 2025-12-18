#!/usr/bin/env python3
"""
Correction des chemins de fichiers SQL dump
Résout le problème de fichiers non trouvés lors de la synchronisation
"""

import sys
import os
import glob
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource


def find_sql_dump_files():
    """Trouve tous les fichiers SQL dump dans le système"""
    print("🔍 RECHERCHE DES FICHIERS SQL DUMP")
    print("=" * 60)
    
    # Rechercher dans différents répertoires possibles
    search_paths = [
        "/tmp/nexusbi/uploads/",
        "/tmp/nexusbi/",
        "/home/james/Bureau/BUREAU/CODE 17/PROJETS/NexusBi/backend/uploads/",
        "/home/james/Bureau/BUREAU/CODE 17/PROJETS/NexusBi/uploads/",
        "/tmp/uploads/",
        "/tmp/",
        ".",
        ".."
    ]
    
    found_files = {}
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            print(f"🔍 Recherche dans: {search_path}")
            
            # Chercher tous les fichiers .sql
            sql_files = glob.glob(os.path.join(search_path, "*.sql"))
            
            for sql_file in sql_files:
                filename = os.path.basename(sql_file)
                if filename not in found_files:
                    found_files[filename] = sql_file
                    print(f"   ✅ Trouvé: {filename} -> {sql_file}")
    
    return found_files


def fix_sql_dump_paths():
    """Corrige les chemins des fichiers SQL dump dans la base"""
    print("🔧 CORRECTION DES CHEMINS SQL DUMP")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Trouver tous les fichiers SQL disponibles
        available_files = find_sql_dump_files()
        
        if not available_files:
            print("❌ Aucun fichier SQL dump trouvé sur le système")
            return
        
        print(f"\n📁 {len(available_files)} fichier(s) SQL dump trouvé(s)")
        
        # Trouver les sources SQL dans la base
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump dans la base")
            return
        
        print(f"📊 {len(sql_sources)} source(s) SQL dump dans la base")
        
        fixed_count = 0
        
        for source in sql_sources:
            print(f"\n🔧 Traitement: {source.name} (ID: {source.id})")
            print(f"   📁 Chemin actuel: {source.file_path}")
            
            # Essayer de trouver le fichier par nom
            filename = os.path.basename(source.file_path) if source.file_path else None
            
            if filename and filename in available_files:
                correct_path = available_files[filename]
                old_path = source.file_path
                source.file_path = correct_path
                
                print(f"   ✅ CORRIGÉ: {old_path}")
                print(f"   ✅ NOUVEAU: {correct_path}")
                
                fixed_count += 1
            else:
                print(f"   ❌ Fichier non trouvé: {filename}")
                
                # Proposer des alternatives
                if filename:
                    similar_files = [f for f in available_files.keys() if filename.lower() in f.lower() or f.lower() in filename.lower()]
                    if similar_files:
                        print(f"   💡 Fichiers similaires: {similar_files}")
        
        # Sauvegarder les changements
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ {fixed_count} chemin(s) corrigé(s) et sauvegardé(s)")
        else:
            print(f"\n⚠️ Aucun chemin corrigé")
            
        return fixed_count
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()


def verify_file_existence():
    """Vérifie que les fichiers existent après correction"""
    print("\n✅ VÉRIFICATION DES FICHIERS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        for source in sql_sources:
            if source.file_path:
                exists = os.path.exists(source.file_path)
                status = "✅ EXISTE" if exists else "❌ MANQUANT"
                print(f"📁 {source.name}: {status}")
                print(f"   📍 {source.file_path}")
                
                if exists:
                    size = os.path.getsize(source.file_path)
                    print(f"   📏 Taille: {size:,} octets ({size/1024/1024:.1f} MB)")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    finally:
        db.close()


def main():
    """Fonction principale"""
    print("🔧 CORRECTION AUTOMATIQUE DES CHEMINS SQL DUMP")
    print("=" * 80)
    print("Ce script va:")
    print("1. 🔍 Rechercher tous les fichiers SQL dump sur le système")
    print("2. 🔧 Corriger les chemins dans la base de données")
    print("3. ✅ Vérifier que les fichiers existent")
    print("=" * 80)
    
    # Corriger les chemins
    fixed_count = fix_sql_dump_paths()
    
    # Vérifier l'existence
    verify_file_existence()
    
    # Résumé
    print(f"\n{'='*80}")
    print("🏁 RÉSUMÉ")
    print(f"{'='*80}")
    
    if fixed_count > 0:
        print(f"✅ {fixed_count} chemin(s) corrigé(s)")
        print("🔄 Vous pouvez maintenant relancer la synchronisation:")
        print("   python force_sql_dump_sync.py")
    else:
        print("⚠️ Aucun chemin corrigé")
        print("💡 Vérifiez manuellement l'emplacement de vos fichiers SQL dump")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
