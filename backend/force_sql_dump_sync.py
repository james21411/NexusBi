#!/usr/bin/env python3
"""
Script de synchronisation forcée des données SQL dump
Résout le problème d'affichage des données SQL dump dans tkinter
"""

import sys
import os
import asyncio
from pathlib import Path
import json

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData
from app.services.data_sync import create_sync_service


def force_sql_dump_sync():
    """Force la synchronisation de toutes les sources SQL dump"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("🔧 SYNCHRONISATION FORCÉE DES DONNÉES SQL DUMP")
        print("=" * 80)
        
        # Créer le service de synchronisation
        sync_service = create_sync_service(db)
        
        # Trouver toutes les sources SQL dump
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump trouvée dans la base de données!")
            print("💡 Assurez-vous qu'une source SQL a été importée")
            return
        
        print(f"📊 {len(sql_sources)} sources SQL dump trouvées")
        
        for source in sql_sources:
            print(f"\n{'='*50}")
            print(f"🗄️ TRAITEMENT DE LA SOURCE: {source.name} (ID: {source.id})")
            print(f"{'='*50}")
            
            # Vérifier le chemin du fichier
            file_path = source.file_path
            if not file_path:
                print(f"❌ ERREUR: Chemin de fichier non défini pour {source.name}")
                continue
            
            print(f"📁 Chemin du fichier: {file_path}")
            
            # Construire le chemin complet
            from app.core.config import settings
            upload_dir = settings.UPLOAD_DIR
            
            if not os.path.isabs(file_path):
                full_file_path = os.path.join(upload_dir, file_path)
            else:
                full_file_path = file_path
            
            print(f"🔍 Chemin complet: {full_file_path}")
            
            # Vérifier l'existence du fichier
            if not os.path.exists(full_file_path):
                print(f"❌ FICHIER NON TROUVÉ: {full_file_path}")
                print("💡 Vérifiez que le fichier SQL dump existe au bon endroit")
                continue
            
            # Vérifier les données actuelles
            current_rows = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            print(f"📊 Données actuelles dans DataFrameData: {current_rows} lignes")
            
            if current_rows > 0:
                print(f"⚠️ ATTENTION: Cette source a déjà {current_rows} lignes")
                print("🤔 Voulez-vous vraiment synchroniser à nouveau? (Oui/Non)")
                # Pour l'automatisation, on continue quand même
                print("➡️  Continuation automatique...")
            
            # Lancer la synchronisation
            print("\n🔄 LANCEMENT DE LA SYNCHRONISATION...")
            
            try:
                # Créer un event loop pour l'async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Synchroniser
                result = loop.run_until_complete(
                    sync_service.sync_data_source(source.id)
                )
                
                loop.close()
                
                # Afficher le résultat
                if result['success']:
                    print("✅ SYNCHRONISATION RÉUSSIE!")
                    print(f"   📊 Lignes mises à jour: {result.get('rows_updated', 'N/A')}")
                    print(f"   📋 Schema info: {result.get('schema_info', {})}")
                    print(f"   💾 Message: {result.get('message', 'N/A')}")
                    
                    # Vérifier les nouvelles données
                    new_rows = db.query(DataFrameData).filter(
                        DataFrameData.data_source_id == source.id
                    ).count()
                    
                    print(f"📊 NOUVELLES DONNÉES: {new_rows} lignes dans DataFrameData")
                    
                    if new_rows > 0:
                        print("🎉 SUCCÈS: Les données sont maintenant disponibles pour tkinter!")
                    else:
                        print("⚠️ ATTENTION: Aucune donnée n'a été stockée malgré le succès")
                        
                else:
                    print("❌ ÉCHEC DE LA SYNCHRONISATION!")
                    print(f"   💥 Erreur: {result.get('error', 'Erreur inconnue')}")
                    print(f"   💾 Message: {result.get('message', 'N/A')}")
                
            except Exception as sync_error:
                print(f"💥 ERREUR LORS DE LA SYNCHRONISATION: {str(sync_error)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("🏁 SYNCHRONISATION TERMINÉE")
        print("=" * 80)
        
        # Résumé final
        print("\n📊 RÉSUMÉ FINAL:")
        all_sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        for source in all_sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            status = "✅ PRÊT POUR TKINTER" if row_count > 0 else "❌ SANS DONNÉES"
            print(f"   {source.name} (ID: {source.id}): {row_count} lignes - {status}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    force_sql_dump_sync()
