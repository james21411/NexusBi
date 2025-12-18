#!/usr/bin/env python3
"""
Debug spécifique de la synchronisation SQL dump
Identifie pourquoi la sync échoue malgré le fichier accessible
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData
from app.services.data_sources.factory import DataSourceFactory


def debug_sql_dump_sync():
    """Debug détaillé de la synchronisation SQL dump"""
    print("🔍 DEBUG SYNCHRONISATION SQL DUMP")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Trouver la source SQL dump
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump trouvée")
            return
        
        for source in sql_sources:
            print(f"\n🔍 DEBUG SOURCE: {source.name} (ID: {source.id})")
            print(f"   📁 Type: {source.type}")
            print(f"   📍 Chemin: {source.file_path}")
            
            # Vérifier l'existence du fichier
            if not source.file_path:
                print("   ❌ Aucun chemin défini")
                continue
            
            file_exists = os.path.exists(source.file_path)
            print(f"   📄 Fichier existe: {'✅ OUI' if file_exists else '❌ NON'}")
            
            if not file_exists:
                print("   💡 Fichier manquant - impossible de continuer")
                continue
            
            # Vérifier la taille du fichier
            file_size = os.path.getsize(source.file_path)
            print(f"   📏 Taille: {file_size:,} octets ({file_size/1024/1024:.1f} MB)")
            
            # Tester l'encodage
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            detected_encoding = None
            
            print("   🔍 Test des encodages...")
            
            for encoding in encodings_to_try:
                try:
                    with open(source.file_path, 'r', encoding=encoding) as f:
                        sample = f.read(1024)  # Lire 1KB
                    
                    if 'CREATE TABLE' in sample.upper() or 'INSERT INTO' in sample.upper():
                        detected_encoding = encoding
                        print(f"   ✅ Encodage détecté: {encoding}")
                        print(f"   📝 Contenu sample: {sample[:200]}...")
                        break
                        
                except UnicodeDecodeError:
                    print(f"   ❌ Échec encodage: {encoding}")
                except Exception as e:
                    print(f"   💥 Erreur avec {encoding}: {e}")
            
            if not detected_encoding:
                print("   ❌ Aucun encodage compatible trouvé")
                continue
            
            # Tester la stratégie SQL dump
            print(f"\n   🔧 Test de la stratégie SQL dump...")
            
            try:
                factory = DataSourceFactory()
                strategy = factory.get_source('sql_dump', {
                    'file_path': source.file_path,
                    'encoding': detected_encoding
                })
                
                print(f"   📋 Stratégie créée: {type(strategy).__name__}")
                
                # Connecter
                print("   🔗 Connexion...")
                strategy.connect()
                print("   ✅ Connexion réussie")
                
                # Obtenir le schéma
                print("   📊 Récupération du schéma...")
                schema = strategy.get_schema()
                print(f"   ✅ Schéma récupéré: {len(schema.get('tables', []))} tables")
                
                # Afficher les détails des tables
                for table in schema.get('tables', []):
                    print(f"      📋 Table: {table['name']} - {table['row_count']} lignes")
                
                # Obtenir toutes les données
                print("   📊 Récupération des données...")
                all_table_data = strategy.get_all_table_data()
                print(f"   ✅ Données récupérées: {len(all_table_data)} tables")
                
                total_rows = 0
                for table_name, table_df in all_table_data.items():
                    print(f"      📈 Table {table_name}: {len(table_df)} lignes")
                    total_rows += len(table_df)
                
                print(f"   📊 TOTAL DES LIGNES: {total_rows}")
                
                if total_rows == 0:
                    print("   ⚠️ ATTENTION: Aucune donnée extraite du SQL dump")
                    print("   💡 Le fichier SQL pourrait ne pas contenir d'INSERT statements")
                else:
                    print(f"   🎉 SUCCÈS: {total_rows} lignes prêtes pour la synchronisation")
                
                # Déconnecter
                strategy.disconnect()
                print("   ✅ Déconnexion réussie")
                
            except Exception as strategy_error:
                print(f"   💥 Erreur stratégie: {str(strategy_error)}")
                import traceback
                traceback.print_exc()
            
            # Vérifier les données actuelles dans DataFrameData
            current_rows = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            print(f"\n   💾 Données actuelles dans DataFrameData: {current_rows} lignes")
            
            if current_rows == 0:
                print("   ❌ PROBLÈME: Aucune donnée dans DataFrameData")
                print("   💡 La stratégie fonctionne mais les données ne sont pas sauvegardées")
                print("   🔧 Vérifiez la méthode _update_dataframe_data dans data_sync.py")
            else:
                print("   ✅ Données présentes dans DataFrameData")
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    debug_sql_dump_sync()
