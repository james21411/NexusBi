#!/usr/bin/env python3
"""
Script de vérification des données SQL dump dans la base de données
Vérifie si les données ont été correctement converties en DataFrame et stockées
"""

import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData


def verify_sql_dump_data():
    """Vérifie les données SQL dump dans la base de données"""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("🔍 VÉRIFICATION DES DONNÉES SQL DUMP DANS LA BASE DE DONNÉES")
        print("=" * 70)
        
        # 1. Lister toutes les sources de données
        print("\n📋 === TOUTES LES SOURCES DE DONNÉES ===")
        all_sources = db.query(DataSource).all()
        
        if not all_sources:
            print("❌ Aucune source de données trouvée dans la base!")
            return
        
        for source in all_sources:
            print(f"\n📁 Source ID: {source.id}")
            print(f"   Nom: {source.name}")
            print(f"   Type: {source.type}")
            print(f"   Fichier: {source.file_path}")
            print(f"   Active: {source.is_active}")
            print(f"   Créée: {source.created_at}")
            print(f"   Mise à jour: {source.updated_at}")
            
            # Compter les lignes de données pour cette source
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            print(f"   📊 Lignes dans DataFrameData: {row_count}")
            
            # Afficher le schema_info
            if source.schema_info:
                try:
                    schema = json.loads(source.schema_info)
                    print(f"   📋 Schema info:")
                    if 'total_tables' in schema:
                        print(f"      - Tables: {schema.get('total_tables', 'N/A')}")
                    if 'total_rows' in schema:
                        print(f"      - Total rows (schema): {schema.get('total_rows', 'N/A')}")
                    if 'row_count' in schema:
                        print(f"      - Row count: {schema.get('row_count', 'N/A')}")
                    if 'processing_info' in schema:
                        proc_info = schema['processing_info']
                        print(f"      - Processing info: {proc_info}")
                except json.JSONDecodeError:
                    print(f"   ⚠️ Schema info invalide: {source.schema_info[:100]}...")
        
        # 2. Chercher spécifiquement les sources SQL
        print("\n" + "=" * 70)
        print("🗄️ === SOURCES SQL DUMP SPÉCIFIQUEMENT ===")
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump trouvée!")
            print("   Vérifiez que le type est bien 'sql' lors de l'import")
        else:
            for source in sql_sources:
                print(f"\n🗄️ Source SQL: {source.name} (ID: {source.id})")
                
                # Vérifier les données
                data_rows = db.query(DataFrameData).filter(
                    DataFrameData.data_source_id == source.id
                ).order_by(DataFrameData.row_index).limit(5).all()
                
                if data_rows:
                    print(f"   ✅ {len(data_rows)} premières lignes trouvées:")
                    for i, row in enumerate(data_rows):
                        try:
                            row_data = json.loads(row.row_data)
                            print(f"      Ligne {row.row_index}: {list(row_data.keys())[:5]}...")
                        except:
                            print(f"      Ligne {row.row_index}: [Erreur de parsing]")
                else:
                    print("   ❌ AUCUNE DONNÉE TROUVÉE DANS DataFrameData!")
                    print("   💡 Le problème est que les données n'ont pas été synchronisées")
                    print("   💡 Vérifiez que la synchronisation a été effectuée après l'import")
        
        # 3. Vérifier la table DataFrameData globalement
        print("\n" + "=" * 70)
        print("📊 === STATISTIQUES GLOBALES DataFrameData ===")
        
        total_rows = db.query(DataFrameData).count()
        print(f"Total de lignes dans DataFrameData: {total_rows}")
        
        # Grouper par source
        from sqlalchemy import func
        stats = db.query(
            DataFrameData.data_source_id,
            func.count(DataFrameData.id).label('count')
        ).group_by(DataFrameData.data_source_id).all()
        
        print("\nRépartition par source:")
        for stat in stats:
            source = db.query(DataSource).filter(DataSource.id == stat.data_source_id).first()
            source_name = source.name if source else "Inconnue"
            source_type = source.type if source else "?"
            print(f"   Source {stat.data_source_id} ({source_type}): {stat.count} lignes - {source_name}")
        
        # 4. Diagnostic du problème
        print("\n" + "=" * 70)
        print("🔧 === DIAGNOSTIC ===")
        
        sql_sources_with_no_data = []
        for source in sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            if row_count == 0:
                sql_sources_with_no_data.append(source)
        
        if sql_sources_with_no_data:
            print("\n⚠️ PROBLÈME DÉTECTÉ: Sources SQL sans données!")
            for source in sql_sources_with_no_data:
                print(f"   - {source.name} (ID: {source.id})")
            
            print("\n💡 SOLUTIONS POSSIBLES:")
            print("   1. La synchronisation n'a pas été effectuée après l'import")
            print("   2. Le fichier SQL dump n'a pas été trouvé lors de la sync")
            print("   3. Le parsing du fichier SQL a échoué")
            print("   4. Le fichier SQL ne contient pas d'INSERT statements")
            
            print("\n🔧 ACTIONS RECOMMANDÉES:")
            print("   1. Vérifier que le fichier SQL existe au chemin indiqué")
            print("   2. Lancer manuellement la synchronisation via l'API")
            print("   3. Vérifier les logs du serveur pour les erreurs")
        else:
            print("✅ Toutes les sources SQL ont des données!")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    verify_sql_dump_data()
