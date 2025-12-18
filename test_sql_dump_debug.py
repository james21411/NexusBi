#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour les fichiers SQL dump
Teste le processus complet : parsing → stockage → récupération
"""

import os
import json
import pandas as pd
from pathlib import Path

def test_sql_dump_parsing():
    """Test le parsing des fichiers SQL dump"""
    print("🔍 === DIAGNOSTIC SQL DUMP ===")
    
    # Chercher des fichiers SQL dump
    upload_dir = Path("backend/uploads")
    if not upload_dir.exists():
        print("❌ Répertoire backend/uploads non trouvé")
        return
    
    sql_files = list(upload_dir.glob("*.sql")) + list(upload_dir.glob("*.dump"))
    
    if not sql_files:
        print("❌ Aucun fichier SQL dump trouvé dans backend/uploads/")
        print("📁 Fichiers trouvés:")
        for file in upload_dir.iterdir():
            print(f"   - {file.name}")
        return
    
    print(f"📄 {len(sql_files)} fichier(s) SQL dump trouvé(s)")
    
    for sql_file in sql_files:
        print(f"\n🔍 Test du fichier: {sql_file.name}")
        test_single_sql_file(sql_file)

def test_single_sql_file(sql_file_path):
    """Test un fichier SQL dump spécifique"""
    try:
        # Importer la stratégie SQL dump
        import sys
        sys.path.append('.')
        from backend.app.services.data_sources.sql_dump_strategy import SQLDumpStrategy
        
        # Créer la stratégie
        strategy = SQLDumpStrategy({
            'file_path': str(sql_file_path),
            'encoding': 'utf-8'
        })
        
        print(f"📋 Connexion au fichier SQL...")
        strategy.connect()
        
        # Test 1: Schéma
        print(f"📊 Récupération du schéma...")
        schema = strategy.get_schema()
        print(f"✅ Schéma récupéré:")
        print(f"   - Tables: {len(schema.get('tables', []))}")
        for table in schema.get('tables', []):
            print(f"     * {table['name']}: {table.get('row_count', 0)} lignes")
        
        # Test 2: Données par table
        print(f"\n📊 Récupération des données par table...")
        all_table_data = strategy.get_all_table_data()
        
        if not all_table_data:
            print("❌ Aucune donnée extraite!")
            return
        
        print(f"✅ {len(all_table_data)} table(s) avec données:")
        for table_name, df in all_table_data.items():
            print(f"   * {table_name}: {len(df)} lignes, {len(df.columns)} colonnes")
            if len(df) > 0:
                print(f"     Colonnes: {list(df.columns)}")
                print(f"     Premières lignes:")
                print(df.head(3).to_string(index=False))
        
        # Test 3: Données combinées
        print(f"\n📊 Test des données combinées...")
        combined_df = strategy.get_data()
        print(f"✅ DataFrame combinée: {len(combined_df)} lignes, {len(combined_df.columns)} colonnes")
        
        if len(combined_df) > 0:
            print(f"Colonnes: {list(combined_df.columns)}")
            print("Premières lignes:")
            print(combined_df.head(3).to_string(index=False))
        
        # Test 4: Sauvegarde pour vérification
        output_file = f"debug_{sql_file_path.stem}_data.csv"
        if len(combined_df) > 0:
            combined_df.to_csv(output_file, index=False)
            print(f"💾 Données sauvegardées dans: {output_file}")
        
        strategy.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

def check_database_storage():
    """Vérifie le stockage en base de données"""
    print(f"\n🗄️ === VÉRIFICATION BASE DE DONNÉES ===")
    
    try:
        # Import des modules nécessaires
        from backend.app.db.session import SessionLocal
        from backend.app.models.project import DataSource, DataFrameData
        
        # Connexion à la base
        db = SessionLocal()
        
        try:
            # Chercher les sources SQL dump
            sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
            
            if not sql_sources:
                print("❌ Aucune source de données SQL dump en base")
                return
            
            print(f"📄 {len(sql_sources)} source(s) SQL dump en base:")
            
            for source in sql_sources:
                print(f"\n📊 Source: {source.name} (ID: {source.id})")
                print(f"   - Fichier: {source.file_path}")
                print(f"   - Actif: {source.is_active}")
                print(f"   - Mis à jour: {source.updated_at}")
                
                # Vérifier les données stockées
                data_count = db.query(DataFrameData).filter(DataFrameData.data_source_id == source.id).count()
                print(f"   - Lignes en base: {data_count}")
                
                if data_count > 0:
                    # Récupérer quelques lignes d'exemple
                    sample_data = db.query(DataFrameData).filter(DataFrameData.data_source_id == source.id).limit(3).all()
                    print(f"   - Échantillon de données:")
                    for i, row in enumerate(sample_data):
                        data = json.loads(row.row_data)
                        print(f"     Ligne {row.row_index}: {data}")
                
                # Vérifier le schéma
                if source.schema_info:
                    schema = json.loads(source.schema_info)
                    print(f"   - Schéma: {json.dumps(schema, indent=2, ensure_ascii=False)}")
        
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification base: {e}")
        import traceback
        traceback.print_exc()

def test_data_retrieval():
    """Test la récupération des données via l'API"""
    print(f"\n🔗 === TEST RÉCUPÉRATION API ===")
    
    try:
        import requests
        
        # Test avec l'endpoint public
        response = requests.get("http://localhost:8000/api/v1/preview/preview-data/1", timeout=10)
        
        print(f"📡 Réponse API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données récupérées:")
            print(f"   - Lignes: {len(data.get('rows', []))}")
            print(f"   - Total lignes: {data.get('total_rows', 'N/A')}")
            print(f"   - Source: {data.get('data_source_name', 'N/A')}")
            
            if data.get('rows'):
                print(f"   - Première ligne: {data['rows'][0]}")
        else:
            print(f"❌ Erreur API: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC SQL DUMP COMPLET")
    print("Ce script teste le processus complet des fichiers SQL dump")
    print("=" * 60)
    
    # 1. Test du parsing
    test_sql_dump_parsing()
    
    # 2. Vérification base de données
    check_database_storage()
    
    # 3. Test récupération API
    test_data_retrieval()
    
    print("\n" + "=" * 60)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("\n💡 Si vous voyez des erreurs, elles indiquent où est le problème:")
    print("   1. Erreur de parsing → Problème dans sql_dump_strategy.py")
    print("   2. Aucune donnée en base → Problème dans data_sync.py")
    print("   3. Erreur API → Problème dans les endpoints backend")
    print("   4. Données en base mais pas d'affichage → Problème dans tkinter")

if __name__ == "__main__":
    main()