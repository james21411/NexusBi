#!/usr/bin/env python3
"""
Synchronisation forcée d'une source spécifique
Test la synchronisation de la source SQL dump bb.sql
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.data_sync import create_sync_service


def force_sync_specific_source():
    """Synchronise spécifiquement la source SQL dump bb.sql"""
    print("🎯 SYNCHRONISATION FORCÉE - SOURCE bb.sql")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Trouver la source bb.sql (ID: 5)
        from app.models.project import DataSource
        source = db.query(DataSource).filter(DataSource.id == 5).first()
        
        if not source:
            print("❌ Source bb.sql (ID: 5) non trouvée")
            return False
        
        print(f"📁 Source trouvée: {source.name}")
        print(f"   📍 Chemin: {source.file_path}")
        print(f"   📄 Type: {source.type}")
        
        # Vérifier le fichier
        if not source.file_path or not os.path.exists(source.file_path):
            print("❌ Fichier bb.sql non accessible")
            return False
        
        file_size = os.path.getsize(source.file_path)
        print(f"   📏 Taille: {file_size:,} octets ({file_size/1024/1024:.1f} MB)")
        
        # Créer le service de synchronisation
        sync_service = create_sync_service(db)
        print("   🔧 Service de synchronisation créé")
        
        # Synchroniser
        print("   🔄 Lancement de la synchronisation...")
        
        # Créer un event loop pour l'async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                sync_service.sync_data_source(source.id)
            )
            
            print(f"\n📊 RÉSULTAT DE LA SYNCHRONISATION:")
            print(f"   ✅ Succès: {result['success']}")
            print(f"   💾 Message: {result.get('message', 'N/A')}")
            
            if result['success']:
                rows_updated = result.get('rows_updated', 0)
                print(f"   📈 Lignes mises à jour: {rows_updated}")
                
                schema_info = result.get('schema_info', {})
                print(f"   📋 Schema info: {schema_info}")
                
                # Vérifier les données en base
                from app.models.project import DataFrameData
                actual_rows = db.query(DataFrameData).filter(
                    DataFrameData.data_source_id == source.id
                ).count()
                
                print(f"   💾 Lignes dans DataFrameData: {actual_rows}")
                
                if actual_rows > 0:
                    print("   🎉 SUCCÈS: Les données sont maintenant disponibles!")
                    return True
                else:
                    print("   ⚠️ PROBLÈME: Synchronisation réussie mais pas de données en base")
                    return False
            else:
                error_msg = result.get('error', 'Erreur inconnue')
                print(f"   ❌ Erreur: {error_msg}")
                return False
                
        except Exception as sync_error:
            print(f"   💥 Erreur lors de la synchronisation: {str(sync_error)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            loop.close()
    
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = force_sync_specific_source()
    
    if success:
        print("\n🎉 SUCCÈS! Vous pouvez maintenant tester l'affichage tkinter")
    else:
        print("\n❌ ÉCHEC. Consultez les logs pour plus de détails")
