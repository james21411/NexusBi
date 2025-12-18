#!/usr/bin/env python3
"""
SOLUTION AUTOMATIQUE COMPLÈTE - PROBLÈME SQL DUMP TKINTER

Ce script résout automatiquement le problème d'affichage des données SQL dump:
1. Diagnostique le problème
2. Force la synchronisation des données SQL dump
3. Vérifie que la solution a fonctionné
4. Génère un rapport final
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData
from app.services.data_sync import create_sync_service


def run_diagnostic():
    """Exécute le diagnostic complet"""
    print("🔍 ÉTAPE 1: DIAGNOSTIC DU PROBLÈME")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump trouvée")
            return False, "Aucune source SQL dump dans la base"
        
        print(f"✅ {len(sql_sources)} source(s) SQL dump trouvée(s)")
        
        sources_without_data = []
        
        for source in sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            print(f"📊 {source.name}: {row_count} lignes dans DataFrameData")
            
            if row_count == 0:
                sources_without_data.append(source)
        
        if sources_without_data:
            print(f"⚠️ {len(sources_without_data)} source(s) sans données - PROBLÈME CONFIRMÉ")
            return True, f"{len(sources_without_data)} sources à synchroniser"
        else:
            print("✅ Toutes les sources SQL ont des données - PROBLÈME RÉSOLU")
            return False, "Toutes les sources ont des données"
            
    except Exception as e:
        return False, f"Erreur diagnostic: {str(e)}"
    finally:
        db.close()


def force_sync_all_sql_sources():
    """Force la synchronisation de toutes les sources SQL dump"""
    print("\n🔧 ÉTAPE 2: SYNCHRONISATION FORCÉE")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        sync_service = create_sync_service(db)
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump à synchroniser")
            return False, "Aucune source trouvée"
        
        success_count = 0
        error_count = 0
        
        for source in sql_sources:
            print(f"\n🔄 Synchronisation: {source.name} (ID: {source.id})")
            
            try:
                # Créer un event loop pour l'async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Synchroniser
                result = loop.run_until_complete(
                    sync_service.sync_data_source(source.id)
                )
                
                loop.close()
                
                if result['success']:
                    rows_updated = result.get('rows_updated', 0)
                    print(f"   ✅ Succès: {rows_updated} lignes synchronisées")
                    success_count += 1
                else:
                    error_msg = result.get('error', 'Erreur inconnue')
                    print(f"   ❌ Échec: {error_msg}")
                    error_count += 1
                    
            except Exception as sync_error:
                print(f"   💥 Erreur: {str(sync_error)}")
                error_count += 1
        
        print(f"\n📊 RÉSULTAT: {success_count} succès, {error_count} erreurs")
        return error_count == 0, f"{success_count} sources synchronisées"
        
    except Exception as e:
        return False, f"Erreur générale: {str(e)}"
    finally:
        db.close()


def verify_solution():
    """Vérifie que la solution a fonctionné"""
    print("\n✅ ÉTAPE 3: VÉRIFICATION DE LA SOLUTION")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            return False, "Aucune source SQL dump"
        
        total_rows = 0
        sources_with_data = 0
        
        for source in sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            total_rows += row_count
            
            if row_count > 0:
                sources_with_data += 1
                print(f"✅ {source.name}: {row_count} lignes")
            else:
                print(f"❌ {source.name}: 0 ligne")
        
        print(f"\n📊 TOTAL: {total_rows} lignes dans {sources_with_data}/{len(sql_sources)} sources")
        
        if total_rows > 0 and sources_with_data == len(sql_sources):
            return True, f"Solution réussie: {total_rows} lignes disponibles"
        else:
            return False, f"Solution incomplète: {sources_with_data}/{len(sql_sources)} sources avec données"
            
    except Exception as e:
        return False, f"Erreur vérification: {str(e)}"
    finally:
        db.close()


def generate_final_report(diagnostic_ok, sync_ok, verify_ok, details):
    """Génère un rapport final"""
    
    report_content = f"""
# 📋 RAPPORT FINAL - SOLUTION SQL DUMP TKINTER

## 🎯 RÉSULTAT DE LA SOLUTION

### Diagnostic Initial
- ✅ Problème identifié: {details.get('diagnostic', 'N/A')}

### Synchronisation
- ✅ Statut: {details.get('sync', 'N/A')}

### Vérification Finale  
- ✅ Statut: {details.get('verify', 'N/A')}

## 📊 ÉTAT FINAL

"""
    
    db = SessionLocal()
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if sql_sources:
            report_content += "### Sources SQL Dump:\n"
            
            for source in sql_sources:
                row_count = db.query(DataFrameData).filter(
                    DataFrameData.data_source_id == source.id
                ).count()
                
                status = "✅ PRÊTE POUR TKINTER" if row_count > 0 else "❌ SANS DONNÉES"
                report_content += f"- {source.name} (ID: {source.id}): {row_count} lignes - {status}\n"
        
        report_content += f"""
## 🖥️ PROCHAINES ÉTAPES

1. **Test tkinter**: Retournez à l'interface web et cliquez sur "Aperçu" pour vos sources SQL
2. **Vérification**: Confirmez que les données s'affichent maintenant (plus 0 ligne)
3. **Si problème persiste**: Consultez les logs du serveur pour plus de détails

## 📞 SUPPORT

Si le problème persiste après cette solution:
1. Vérifiez que le serveur backend est démarré
2. Consultez les logs pour les erreurs de synchronisation  
3. Testez avec un fichier SQL dump plus petit
4. Vérifiez les permissions de lecture du fichier SQL

---
Généré automatiquement le: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
    finally:
        db.close()
    
    with open('RAPPORT_SQL_DUMP_SOLUTION.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 Rapport généré: RAPPORT_SQL_DUMP_SOLUTION.md")


def main():
    """Fonction principale - solution automatique complète"""
    print("🚀 SOLUTION AUTOMATIQUE - PROBLÈME SQL DUMP TKINTER")
    print("=" * 80)
    print("Ce script va automatiquement:")
    print("1. 🔍 Diagnostiquer le problème")
    print("2. 🔧 Synchroniser les données SQL dump")  
    print("3. ✅ Vérifier que la solution fonctionne")
    print("4. 📋 Générer un rapport final")
    print("=" * 80)
    
    details = {}
    
    # Étape 1: Diagnostic
    diagnostic_ok, diagnostic_msg = run_diagnostic()
    details['diagnostic'] = diagnostic_msg
    
    if not diagnostic_ok and "aucune source" in diagnostic_msg.lower():
        print("\n❌ ARRÊT: Aucune source SQL dump trouvée")
        return
    
    # Étape 2: Synchronisation
    sync_ok, sync_msg = force_sync_all_sql_sources()
    details['sync'] = sync_msg
    
    # Étape 3: Vérification
    verify_ok, verify_msg = verify_solution()
    details['verify'] = verify_msg
    
    # Étape 4: Rapport final
    generate_final_report(diagnostic_ok, sync_ok, verify_ok, details)
    
    # Résumé final
    print(f"\n{'='*80}")
    print("🏁 RÉSUMÉ FINAL")
    print(f"{'='*80}")
    
    if verify_ok:
        print("🎉 SUCCÈS: Le problème SQL dump tkinter a été résolu!")
        print("✅ Vos données SQL dump sont maintenant disponibles pour tkinter")
        print("🖥️ Vous pouvez maintenant tester l'affichage depuis l'interface web")
    else:
        print("⚠️ PARTIEL: La solution a été appliquée mais nécessite une vérification")
        print("📋 Consultez le rapport pour plus de détails")
    
    print(f"\n📄 Rapport détaillé: RAPPORT_SQL_DUMP_SOLUTION.md")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
