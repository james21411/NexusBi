#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour inspecter les données SQL dump stockées en base
Affiche le contenu exact des tables DataFrameData pour diagnostiquer le problème
"""

import json
import sys
import os
from pathlib import Path

def inspect_sql_dump_data():
    """Inspecte les données SQL dump en base"""
    print("🔍 === INSPECTION DONNÉES SQL DUMP ===")
    
    # Ajouter le répertoire backend au PYTHONPATH
    backend_dir = Path("backend")
    if backend_dir.exists():
        sys.path.insert(0, str(backend_dir))
    
    try:
        # Import des modules backend
        from app.db.session import SessionLocal
        from app.models.project import DataSource, DataFrameData
        
        # Connexion à la base
        db = SessionLocal()
        
        try:
            # Chercher les sources SQL dump
            sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
            
            if not sql_sources:
                print("❌ Aucune source de données SQL dump trouvée en base")
                return
            
            print(f"📄 {len(sql_sources)} source(s) SQL dump trouvée(s):")
            
            for source in sql_sources:
                print(f"\n{'='*60}")
                print(f"📊 SOURCE: {source.name} (ID: {source.id})")
                print(f"   - Fichier: {source.file_path}")
                print(f"   - Type: {source.type}")
                print(f"   - Actif: {source.is_active}")
                print(f"   - Créé: {source.created_at}")
                print(f"   - Mis à jour: {source.updated_at}")
                
                # Vérifier le schéma
                if source.schema_info:
                    try:
                        schema = json.loads(source.schema_info)
                        print(f"\n📋 SCHÉMA:")
                        print(json.dumps(schema, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        print(f"❌ Schéma invalide: {source.schema_info}")
                else:
                    print(f"❌ Aucun schéma enregistré")
                
                # Compter les données
                data_count = db.query(DataFrameData).filter(DataFrameData.data_source_id == source.id).count()
                print(f"\n📊 DONNÉES EN BASE: {data_count} lignes")
                
                if data_count == 0:
                    print(f"❌ Aucune donnée stockée pour cette source!")
                    continue
                
                # Récupérer toutes les données pour inspection
                all_data = db.query(DataFrameData).filter(
                    DataFrameData.data_source_id == source.id
                ).order_by(DataFrameData.row_index).all()
                
                print(f"\n📋 CONTENU COMPLET DES DONNÉES:")
                print(f"{'='*60}")
                
                for i, row in enumerate(all_data):
                    try:
                        data = json.loads(row.row_data)
                        print(f"\nLigne {row.row_index}:")
                        for key, value in data.items():
                            print(f"  {key}: {value}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Erreur parsing ligne {row.row_index}: {e}")
                        print(f"  raw_data: {row.row_data}")
                
                # Vérifier la cohérence des données
                print(f"\n🔍 ANALYSE DE COHÉRENCE:")
                print(f"   - Nombre de lignes en base: {data_count}")
                print(f"   - Index min: {min(r.row_index for r in all_data) if all_data else 'N/A'}")
                print(f"   - Index max: {max(r.row_index for r in all_data) if all_data else 'N/A'}")
                
                # Analyser les colonnes
                if all_data:
                    first_row = json.loads(all_data[0].row_data)
                    columns = list(first_row.keys())
                    print(f"   - Colonnes trouvées: {columns}")
                    
                    # Vérifier s'il y a des données vides
                    non_empty_rows = 0
                    for row in all_data:
                        data = json.loads(row.row_data)
                        if any(str(v).strip() for v in data.values() if v is not None):
                            non_empty_rows += 1
                    
                    print(f"   - Lignes avec données: {non_empty_rows}")
                    print(f"   - Lignes vides: {data_count - non_empty_rows}")
                
                # Sauvegarder les données pour inspection
                output_file = f"sql_dump_data_source_{source.id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    export_data = {
                        'source_info': {
                            'id': source.id,
                            'name': source.name,
                            'file_path': source.file_path,
                            'type': source.type,
                            'created_at': source.created_at.isoformat() if source.created_at else None,
                            'updated_at': source.updated_at.isoformat() if source.updated_at else None
                        },
                        'schema_info': json.loads(source.schema_info) if source.schema_info else None,
                        'data_count': data_count,
                        'rows': []
                    }
                    
                    for row in all_data:
                        try:
                            data = json.loads(row.row_data)
                            export_data['rows'].append({
                                'row_index': row.row_index,
                                'data': data
                            })
                        except json.JSONDecodeError:
                            export_data['rows'].append({
                                'row_index': row.row_index,
                                'data': None,
                                'raw_data': row.row_data
                            })
                    
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Données exportées dans: {output_file}")
        
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erreur lors de l'inspection: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoint():
    """Test l'endpoint API pour voir ce qu'il retourne"""
    print(f"\n🔗 === TEST ENDPOINT API ===")
    
    try:
        import requests
        
        # Test avec l'endpoint public pour la source ID 1
        response = requests.get("http://localhost:8000/api/v1/preview/preview-data/1", timeout=10)
        
        print(f"📡 Réponse API pour source ID 1: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Données récupérées:")
            print(f"   - Lignes retournées: {len(data.get('rows', []))}")
            print(f"   - Total lignes: {data.get('total_rows', 'N/A')}")
            print(f"   - Source name: {data.get('data_source_name', 'N/A')}")
            
            if data.get('rows'):
                print(f"\n📋 PREMIÈRES LIGNES RETOURNÉES:")
                for i, row in enumerate(data['rows'][:5]):  # 5 premières lignes
                    print(f"   Ligne {i+1}: {row}")
            else:
                print(f"❌ Aucune ligne retournée par l'API!")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")

def check_backend_processing():
    """Vérifie le traitement backend des fichiers SQL"""
    print(f"\n🔄 === VÉRIFICATION TRAITEMENT BACKEND ===")
    
    # Chercher les fichiers SQL dans le répertoire uploads
    upload_dir = Path("backend/uploads")
    if upload_dir.exists():
        sql_files = list(upload_dir.glob("*.sql")) + list(upload_dir.glob("*.dump"))
        if sql_files:
            print(f"📁 Fichiers SQL trouvés dans backend/uploads/:")
            for sql_file in sql_files:
                size = sql_file.stat().st_size
                print(f"   - {sql_file.name} ({size} bytes)")
        else:
            print(f"❌ Aucun fichier SQL trouvé dans backend/uploads/")
    else:
        print(f"❌ Répertoire backend/uploads/ non trouvé")

def main():
    """Fonction principale"""
    print("🔍 INSPECTION COMPLÈTE DES DONNÉES SQL DUMP")
    print("Ce script examine en détail les données SQL dump stockées")
    print("=" * 70)
    
    # 1. Inspection base de données
    inspect_sql_dump_data()
    
    # 2. Test API
    test_api_endpoint()
    
    # 3. Vérification fichiers
    check_backend_processing()
    
    print(f"\n" + "=" * 70)
    print("🏁 INSPECTION TERMINÉE")
    print(f"\n💡 Analyse des résultats:")
    print(f"   1. Si données en base = 0 → Problème de synchronisation")
    print(f"   2. Si données en base > 0 mais API retourne 0 → Problème endpoint")
    print(f"   3. Si API retourne des données mais tkinter n'affiche rien → Problème interface")
    print(f"   4. Si données sont vides → Problème de parsing SQL")

if __name__ == "__main__":
    main()