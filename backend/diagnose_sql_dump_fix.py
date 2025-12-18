#!/usr/bin/env python3
"""
DIAGNOSTIC ET SOLUTION COMPLÈTE - PROBLÈME D'AFFICHAGE SQL DUMP DANS TKINTER

Problème identifié:
- Les données SQL dump sont importées mais PAS synchronisées
- Elles ne sont donc PAS converties en DataFrame et stockées dans DataFrameData
- tkinter ne peut afficher que les données de la table DataFrameData
- Résultat: 0 ligne affichée malgré 500K lignes dans le SQL dump

Solution:
1. Diagnostiquer le problème
2. Forcer la synchronisation SQL dump
3. Vérifier que les données sont maintenant disponibles
4. Tester l'affichage tkinter
"""

import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData


def diagnose_sql_dump_issue():
    """Diagnostique le problème d'affichage SQL dump"""
    
    print("🔍 DIAGNOSTIC DU PROBLÈME D'AFFICHAGE SQL DUMP")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # 1. Vérifier les sources SQL dump
        sql_sources = db.query(DataSource).filter(DataSource.type == 'sql').all()
        
        if not sql_sources:
            print("❌ AUCUNE SOURCE SQL DUMP TROUVÉE")
            print("💡 Aucune source SQL n'a été importée dans la base")
            return
        
        print(f"✅ {len(sql_sources)} source(s) SQL dump trouvée(s)")
        
        for source in sql_sources:
            print(f"\n{'='*60}")
            print(f"📁 SOURCE: {source.name} (ID: {source.id})")
            print(f"{'='*60}")
            
            # 2. Vérifier le chemin du fichier
            file_path = source.file_path
            print(f"📁 Chemin fichier: {file_path}")
            
            if file_path:
                from app.core.config import settings
                upload_dir = settings.UPLOAD_DIR
                
                if not os.path.isabs(file_path):
                    full_path = os.path.join(upload_dir, file_path)
                else:
                    full_path = file_path
                
                file_exists = os.path.exists(full_path)
                print(f"🔍 Fichier existe: {'✅ OUI' if file_exists else '❌ NON'}")
                print(f"📍 Chemin complet: {full_path}")
                
                if file_exists:
                    file_size = os.path.getsize(full_path)
                    print(f"📏 Taille fichier: {file_size:,} octets ({file_size/1024/1024:.1f} MB)")
            
            # 3. Vérifier les données dans DataFrameData
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            print(f"📊 Lignes dans DataFrameData: {row_count}")
            
            # 4. Analyser le schema_info
            if source.schema_info:
                try:
                    schema = json.loads(source.schema_info)
                    print(f"📋 Schema info:")
                    
                    if 'total_tables' in schema:
                        print(f"   🗄️ Tables: {schema['total_tables']}")
                    if 'total_rows' in schema:
                        print(f"   📊 Total rows (schema): {schema['total_rows']}")
                    if 'row_count' in schema:
                        print(f"   📈 Row count: {schema['row_count']}")
                    if 'processing_info' in schema:
                        print(f"   ⚙️ Processing info: {schema['processing_info']}")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️ Schema info invalide")
            
            # 5. DIAGNOSTIC FINAL
            print(f"\n🔧 DIAGNOSTIC POUR {source.name}:")
            
            if row_count == 0:
                print("   ❌ PROBLÈME CONFIRMÉ: Aucune donnée dans DataFrameData")
                print("   💡 Les données SQL dump n'ont PAS été synchronisées")
                print("   🎯 ACTION REQUISE: Forcer la synchronisation")
                
                if file_path and file_exists:
                    print("   ✅ Le fichier SQL existe, la synchronisation devrait fonctionner")
                else:
                    print("   ❌ Le fichier SQL n'existe pas - vérifiez le chemin")
                    
            else:
                print("   ✅ Données présentes dans DataFrameData")
                print("   🎉 Cette source devrait s'afficher dans tkinter")
        
        # 6. Résumé global
        print(f"\n{'='*80}")
        print("📊 RÉSUMÉ GLOBAL")
        print(f"{'='*80}")
        
        sql_with_data = 0
        sql_without_data = 0
        
        for source in sql_sources:
            row_count = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).count()
            
            if row_count > 0:
                sql_with_data += 1
            else:
                sql_without_data += 1
        
        print(f"📊 Sources SQL avec données: {sql_with_data}")
        print(f"📊 Sources SQL sans données: {sql_without_data}")
        
        if sql_without_data > 0:
            print(f"\n⚠️ PROBLÈME IDENTIFIÉ:")
            print(f"   {sql_without_data} source(s) SQL dump n'ont pas été synchronisées")
            print(f"   Elles ne peuvent donc PAS s'afficher dans tkinter")
            print(f"\n🛠️ SOLUTION:")
            print(f"   Exécutez le script: python force_sql_dump_sync.py")
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def create_solution_guide():
    """Crée un guide de solution étape par étape"""
    
    guide_content = """
# 🔧 GUIDE DE SOLUTION - PROBLÈME SQL DUMP TKINTER

## 🎯 PROBLÈME IDENTIFIÉ

Les données SQL dump ne s'affichent pas dans tkinter (0 ligne) malgré:
- ✅ Fichier SQL dump importé avec succès
- ✅ Source créée dans la base avec ~500K lignes dans les métadonnées
- ❌ Données NON synchronisées dans la table DataFrameData

## 🔍 EXPLICATION TECHNIQUE

### Comment fonctionne l'affichage tkinter:
1. tkinter récupère les données depuis l'endpoint `/api/v1/data-preview/preview-data/{id}`
2. Cet endpoint lit UNIQUEMENT la table `DataFrameData`
3. Si `DataFrameData` est vide → 0 ligne affichée

### Le problème SQL dump:
1. Import SQL dump → Crée une entrée dans `DataSource`
2. Parse le fichier → Stocke les métadonnées dans `schema_info`
3. **MANQUE**: Synchronisation → Conversion en DataFrame + stockage dans `DataFrameData`
4. Résultat: Métadonnées OK, mais `DataFrameData` vide

## 🛠️ SOLUTION ÉTAPE PAR ÉTAPE

### Étape 1: Diagnostic
```bash
cd backend
python verify_sql_dump_data.py
```

### Étape 2: Synchronisation forcée
```bash
cd backend  
python force_sql_dump_sync.py
```

### Étape 3: Vérification
```bash
cd backend
python verify_sql_dump_data.py
```
→ Vérifiez que les sources SQL affichent maintenant des lignes dans DataFrameData

### Étape 4: Test tkinter
1. Retournez à l'interface web
2. Cliquez sur "Aperçu" pour la source SQL dump
3. Vérifiez que les données s'affichent maintenant

## ⚡ SOLUTION AUTOMATIQUE (RECOMMANDÉE)

Exécutez ce script pour tout faire en une fois:
```bash
cd backend
python auto_fix_sql_dump.py
```

## 🔍 CAUSES POSSIBLES

1. **Synchronisation non déclenchée**: Après import SQL, la sync n'est pas automatique
2. **Erreur lors du parsing**: Le fichier SQL dump contient des syntaxes non supportées  
3. **Chemin de fichier incorrect**: Le fichier a été déplacé/supprimé
4. **Problème de permissions**: Impossible de lire le fichier SQL
5. **Timeout**: Le fichier est trop volumineux pour être traité en une fois

## 📋 VALIDATION

Après la solution, vous devriez voir:
- ✅ Source SQL avec > 0 lignes dans DataFrameData
- ✅ tkinter affiche les données (plus 0 ligne)
- ✅ Métadonnées cohérentes entre schema_info et DataFrameData

## 🚨 SI LE PROBLÈME PERSISTE

1. Vérifiez les logs du serveur pour les erreurs
2. Testez avec un petit fichier SQL dump d'abord
3. Vérifiez que tous les modules requis sont installés
4. Consultez la documentation technique dans `docs/`
"""
    
    with open('GUIDE_SQL_DUMP_SOLUTION.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📄 Guide de solution créé: GUIDE_SQL_DUMP_SOLUTION.md")


def main():
    """Fonction principale"""
    print("🚀 DIAGNOSTIC ET SOLUTION SQL DUMP TKINTER")
    print("=" * 80)
    
    # Diagnostiquer le problème
    diagnose_sql_dump_issue()
    
    # Créer le guide de solution
    create_solution_guide()
    
    print(f"\n{'='*80}")
    print("🎯 ACTIONS RECOMMANDÉES")
    print(f"{'='*80}")
    print("1. 📋 Lisez le guide: GUIDE_SQL_DUMP_SOLUTION.md")
    print("2. 🔧 Exécutez: python force_sql_dump_sync.py")
    print("3. ✅ Vérifiez: python verify_sql_dump_data.py") 
    print("4. 🖥️ Testez tkinter depuis l'interface web")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
