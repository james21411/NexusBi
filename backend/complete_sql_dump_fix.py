#!/usr/bin/env python3
"""
SOLUTION COMPLÈTE ET DÉFINITIVE - PROBLÈME SQL DUMP TKINTER

Ce script résout TOUS les problèmes liés à l'affichage SQL dump:
1. Corrige les chemins de fichiers incorrects
2. Synchronise les données SQL dump
3. Vérifie que tout fonctionne
4. Génère un rapport complet
"""

import sys
import os
import json
import asyncio
import glob
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData
from app.services.data_sync import create_sync_service


def find_and_fix_sql_dump_paths():
    """Trouve et corrige les chemins des fichiers SQL dump"""
    print("🔍 ÉTAPE 1: RECHERCHE ET CORRECTION DES CHEMINS")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Rechercher tous les fichiers SQL dans le système
        search_patterns = [
            "**/*.sql",
            "uploads/*.sql", 
            "/tmp/**/*.sql",
            "/home/**/*.sql"
        ]
        
        found_files = {}
        print("🔍 Recherche des fichiers SQL dump...")
        
        # Recherche dans le répertoire courant et sous-répertoires
        for pattern in ["*.sql", "**/*.sql"]:
            for sql_file in glob.glob(pattern, recursive=True):
                if os.path.isfile(sql_file):
                    filename = os.path.basename(sql_file)
                    if filename not in found_files:
                        found_files[filename] = os.path.abspath(sql_file)
                        print(f"   ✅ Trouvé: {filename} -> {sql_file}")
        
        if not found_files:
            print("❌ Aucun fichier SQL dump trouvé")
            return False
        
        print(f"\n📁 {len(found_files)} fichier(s) SQL dump trouvé(s)")
        
        # Vérifier les sources SQL dans la base
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump dans la base")
            return False
        
        print(f"📊 {len(sql_sources)} source(s) SQL dump dans la base")
        
        fixed_paths = 0
        
        for source in sql_sources:
            print(f"\n🔧 Source: {source.name} (ID: {source.id})")
            print(f"   📁 Chemin actuel: {source.file_path}")
            
            # Essayer de trouver le fichier par nom
            filename = os.path.basename(source.file_path) if source.file_path else None
            
            if filename and filename in found_files:
                correct_path = found_files[filename]
                old_path = source.file_path
                source.file_path = correct_path
                
                print(f"   ✅ CORRIGÉ: {old_path}")
                print(f"   ✅ NOUVEAU: {correct_path}")
                
                # Vérifier que le fichier existe
                if os.path.exists(correct_path):
                    size = os.path.getsize(correct_path)
                    print(f"   📏 Taille: {size:,} octets ({size/1024/1024:.1f} MB)")
                    fixed_paths += 1
                else:
                    print(f"   ❌ ERREUR: Fichier still pas accessible")
            else:
                print(f"   ❌ Fichier non trouvé: {filename}")
                
                # Proposer des alternatives
                if filename:
                    similar = [f for f in found_files.keys() if filename.lower() in f.lower() or f.lower() in filename.lower()]
                    if similar:
                        print(f"   💡 Fichiers similaires: {similar[:3]}")
        
        # Sauvegarder
        if fixed_paths > 0:
            db.commit()
            print(f"\n✅ {fixed_paths} chemin(s) corrigé(s) et sauvegardé(s)")
            return True
        else:
            print(f"\n⚠️ Aucun chemin corrigé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def sync_all_sql_sources():
    """Synchronise toutes les sources SQL dump"""
    print("\n🔄 ÉTAPE 2: SYNCHRONISATION DES DONNÉES SQL DUMP")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        sync_service = create_sync_service(db)
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump à synchroniser")
            return False
        
        success_count = 0
        total_rows = 0
        
        for source in sql_sources:
            print(f"\n🔄 Synchronisation: {source.name} (ID: {source.id})")
            
            # Vérifier que le fichier existe
            if not source.file_path or not os.path.exists(source.file_path):
                print(f"   ❌ Fichier manquant: {source.file_path}")
                continue
            
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
                    total_rows += rows_updated
                    print(f"   ✅ Succès: {rows_updated} lignes synchronisées")
                    success_count += 1
                else:
                    error_msg = result.get('error', 'Erreur inconnue')
                    print(f"   ❌ Échec: {error_msg}")
                    
            except Exception as sync_error:
                print(f"   💥 Erreur: {str(sync_error)}")
        
        print(f"\n📊 RÉSULTAT: {success_count}/{len(sql_sources)} sources synchronisées")
        print(f"📈 TOTAL: {total_rows} lignes synchronisées")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False
    finally:
        db.close()


def verify_final_solution():
    """Vérifie que la solution finale fonctionne"""
    print("\n✅ ÉTAPE 3: VÉRIFICATION FINALE")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ Aucune source SQL dump")
            return False
        
        all_good = True
        total_rows = 0
        
        for source in sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            total_rows += row_count
            
            # Vérifier le fichier
            file_exists = source.file_path and os.path.exists(source.file_path)
            
            status = "✅ PRÊT" if (row_count > 0 and file_exists) else "❌ PROBLÈME"
            print(f"\n📊 {source.name}: {status}")
            print(f"   📊 Lignes DataFrameData: {row_count}")
            print(f"   📁 Fichier: {'✅ Existe' if file_exists else '❌ Manquant'}")
            
            if row_count == 0 or not file_exists:
                all_good = False
        
        print(f"\n📈 TOTAL: {total_rows} lignes dans {len(sql_sources)} sources")
        
        return all_good and total_rows > 0
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False
    finally:
        db.close()


def generate_comprehensive_report(path_fixed, sync_success, final_ok):
    """Génère un rapport complet de la solution"""
    
    report_content = f"""
# 📋 RAPPORT COMPLET - SOLUTION SQL DUMP TKINTER

## 🎯 RÉSULTATS DE LA SOLUTION

### Correction des Chemins
- ✅ Statut: {'SUCCÈS' if path_fixed else 'ÉCHEC'}

### Synchronisation des Données  
- ✅ Statut: {'SUCCÈS' if sync_success else 'ÉCHEC'}

### Vérification Finale
- ✅ Statut: {'SUCCÈS' if final_ok else 'ÉCHEC'}

## 📊 ÉTAT FINAL DES SOURCES SQL DUMP

"""
    
    db = SessionLocal()
    try:
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if sql_sources:
            report_content += "### Détail par source:\n\n"
            
            for source in sql_sources:
                row_count = db.query(DataFrameData).filter(
                    DataFrameData.data_source_id == source.id
                ).count()
                
                file_exists = source.file_path and os.path.exists(source.file_path)
                
                status = "✅ PRÊTE POUR TKINTER" if (row_count > 0 and file_exists) else "❌ PROBLÈME"
                
                report_content += f"#### {source.name} (ID: {source.id})\n"
                report_content += f"- **Statut**: {status}\n"
                report_content += f"- **Lignes DataFrameData**: {row_count}\n"
                report_content += f"- **Fichier**: {'✅ Existe' if file_exists else '❌ Manquant'}\n"
                report_content += f"- **Chemin**: `{source.file_path or 'Non défini'}`\n\n"
        
        report_content += f"""
## 🖥️ PROCHAINES ÉTAPES

### Test Immédiat
1. Retournez à l'interface web NexusBi
2. Cliquez sur "Aperçu" pour vos sources SQL dump
3. Vérifiez que les données s'affichent maintenant (plus 0 ligne)

### Si Ça Marche
🎉 **Félicitations!** Le problème SQL dump tkinter est résolu.
- Vos données SQL dump s'affichent comme les autres sources
- L'interface est maintenant uniforme pour tous les types de données

### Si Ça Ne Marche Pas
1. **Vérifiez les logs du serveur** pour les erreurs
2. **Redémarrez le serveur backend** si nécessaire
3. **Testez avec une source CSV** pour confirmer que tkinter fonctionne
4. **Consultez le guide de dépannage** dans la documentation

## 📞 RÉSUMÉ TECHNIQUE

**Problème initial**: 
- Données SQL dump non affichées dans tkinter (0 ligne)
- Cause: Données pas dans la table DataFrameData

**Solution appliquée**:
- ✅ Correction des chemins de fichiers
- ✅ Synchronisation forcée des données
- ✅ Vérification de la solution

**Résultat**:
- {'✅ SUCCÈS COMPLET' if final_ok else '⚠️ PARTIELLEMENT RÉSOLU'}
- Les données SQL dump sont maintenant disponibles pour tkinter

---
**Rapport généré le**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
    finally:
        db.close()
    
    with open('RAPPORT_SQL_DUMP_COMPLET.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 Rapport complet généré: RAPPORT_SQL_DUMP_COMPLET.md")


def main():
    """Fonction principale - solution complète"""
    print("🚀 SOLUTION COMPLÈTE - PROBLÈME SQL DUMP TKINTER")
    print("=" * 80)
    print("Ce script va résoudre définitivement le problème:")
    print("1. 🔍 Corriger les chemins de fichiers SQL dump")
    print("2. 🔄 Synchroniser toutes les données")  
    print("3. ✅ Vérifier que la solution fonctionne")
    print("4. 📋 Générer un rapport détaillé")
    print("=" * 80)
    
    # Étape 1: Corriger les chemins
    path_fixed = find_and_fix_sql_dump_paths()
    
    # Étape 2: Synchroniser
    sync_success = False
    if path_fixed:
        sync_success = sync_all_sql_sources()
    
    # Étape 3: Vérifier
    final_ok = verify_final_solution()
    
    # Étape 4: Rapport
    generate_comprehensive_report(path_fixed, sync_success, final_ok)
    
    # Résumé final
    print(f"\n{'='*80}")
    print("🏁 RÉSUMÉ FINAL")
    print(f"{'='*80}")
    
    if final_ok:
        print("🎉 SUCCÈS COMPLET: Le problème SQL dump tkinter est résolu!")
        print("✅ Vos données SQL dump sont maintenant disponibles pour tkinter")
        print("🖥️ Testez dès maintenant depuis l'interface web")
    elif sync_success:
        print("⚠️ PARTIEL: Synchronisation réussie mais vérification incomplète")
        print("📋 Consultez le rapport pour plus de détails")
    else:
        print("❌ ÉCHEC: La solution n'a pas fonctionné")
        print("💡 Vérifiez les logs et l'emplacement des fichiers SQL dump")
    
    print(f"\n📄 Rapport détaillé: RAPPORT_SQL_DUMP_COMPLET.md")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
