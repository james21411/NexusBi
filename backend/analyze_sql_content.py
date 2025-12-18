#!/usr/bin/env python3
"""
Analyse du contenu SQL dump
Vérifie si le fichier contient des INSERT statements ou seulement le schéma
"""

import sys
import os
import re
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource


def analyze_sql_content():
    """Analyse le contenu du fichier SQL dump bb.sql"""
    print("🔍 ANALYSE DU CONTENU SQL DUMP")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Trouver la source bb.sql
        source = db.query(DataSource).filter(DataSource.id == 5).first()
        
        if not source:
            print("❌ Source bb.sql (ID: 5) non trouvée")
            return
        
        file_path = source.file_path
        print(f"📁 Analyse du fichier: {file_path}")
        
        if not os.path.exists(file_path):
            print("❌ Fichier non accessible")
            return
        
        # Lire le contenu complet
        print("📖 Lecture du contenu complet...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📏 Taille du contenu: {len(content):,} caractères")
        
        # Analyser les sections
        print("\n🔍 ANALYSE DES SECTIONS:")
        
        # 1. Vérifier les CREATE TABLE
        create_table_matches = re.findall(r'CREATE TABLE\s+`?(\w+)`?\s*\(', content, re.IGNORECASE)
        print(f"   📋 CREATE TABLE: {len(create_table_matches)} tables")
        if create_table_matches:
            print(f"      Tables: {create_table_matches[:5]}{'...' if len(create_table_matches) > 5 else ''}")
        
        # 2. Vérifier les INSERT INTO
        insert_matches = re.findall(r'INSERT INTO\s+`?(\w+)`?\s*\(', content, re.IGNORECASE)
        print(f"   📝 INSERT INTO: {len(insert_matches)} statements")
        
        if insert_matches:
            # Grouper par table
            from collections import Counter
            insert_counts = Counter(insert_matches)
            print(f"      Répartition par table:")
            for table, count in insert_counts.most_common(10):
                print(f"         {table}: {count} INSERT statements")
        else:
            print("      ❌ AUCUN INSERT STATEMENT TROUVÉ")
        
        # 3. Analyser la structure du fichier
        lines = content.split('\n')
        print(f"\n📊 STRUCTURE DU FICHIER:")
        print(f"   📏 Total lignes: {len(lines)}")
        
        # Compter les lignes de commentaires, CREATE, INSERT, etc.
        comment_lines = 0
        create_lines = 0
        insert_lines = 0
        empty_lines = 0
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                empty_lines += 1
            elif line_stripped.startswith('--') or line_stripped.startswith('/*'):
                comment_lines += 1
            elif 'CREATE TABLE' in line_stripped.upper():
                create_lines += 1
            elif 'INSERT INTO' in line_stripped.upper():
                insert_lines += 1
        
        print(f"   💬 Lignes de commentaires: {comment_lines}")
        print(f"   📋 Lignes CREATE TABLE: {create_lines}")
        print(f"   📝 Lignes INSERT INTO: {insert_lines}")
        print(f"   ⚪ Lignes vides: {empty_lines}")
        
        # 4. Vérifier les premières et dernières lignes
        print(f"\n📄 DÉBUT DU FICHIER:")
        for i, line in enumerate(lines[:10]):
            print(f"   {i+1:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        print(f"\n📄 FIN DU FICHIER:")
        for i, line in enumerate(lines[-10:], len(lines)-9):
            print(f"   {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
        
        # 5. DIAGNOSTIC FINAL
        print(f"\n{'='*80}")
        print("🎯 DIAGNOSTIC FINAL")
        print(f"{'='*80}")
        
        if insert_lines == 0:
            print("❌ PROBLÈME CONFIRMÉ:")
            print("   📄 Le fichier SQL dump ne contient QUE le SCHÉMA")
            print("   📋 CREATE TABLE statements présents")
            print("   ❌ AUCUN INSERT INTO statement")
            print("   💡 C'est un 'dump de structure' sans données")
            print("\n🔧 SOLUTIONS POSSIBLES:")
            print("   1. Obtenir un dump complet avec données (CREATE + INSERT)")
            print("   2. Utiliser les métadonnées du schéma pour l'interface")
            print("   3. Importer les données depuis une autre source")
            
        else:
            print("✅ DONNÉES PRÉSENTES:")
            print(f"   📝 {insert_lines} INSERT statements trouvés")
            print("   💡 Problème dans le parsing des INSERT statements")
            print("   🔧 Corriger la stratégie SQL dump")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    analyze_sql_content()
