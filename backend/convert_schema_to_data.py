#!/usr/bin/env python3
"""
Conversion du schéma SQL en données informatives
Crée des données de démonstration basées sur le schéma pour l'interface
"""

import sys
import os
import json
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.project import DataSource, DataFrameData
from app.services.data_sources.factory import DataSourceFactory


def convert_schema_to_demo_data():
    """Convertit le schéma SQL en données de démonstration"""
    print("🔄 CONVERSION SCHÉMA → DONNÉES DE DÉMONSTRATION")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Trouver la source bb.sql
        source = db.query(DataSource).filter(DataSource.id == 5).first()
        
        if not source:
            print("❌ Source bb.sql (ID: 5) non trouvée")
            return False
        
        print(f"📁 Traitement: {source.name}")
        
        # Utiliser la stratégie SQL dump pour obtenir le schéma
        factory = DataSourceFactory()
        strategy = factory.get_source('sql_dump', {
            'file_path': source.file_path,
            'encoding': 'utf-8'
        })
        
        strategy.connect()
        
        try:
            # Obtenir le schéma complet
            schema = strategy.get_schema()
            tables = schema.get('tables', [])
            
            print(f"📋 {len(tables)} tables trouvées dans le schéma")
            
            if not tables:
                print("❌ Aucune table dans le schéma")
                return False
            
            # Créer des données de démonstration basées sur le schéma
            demo_rows = []
            
            # 1. Ajouter une ligne récapitulative
            summary_row = {
                "_source_table": "SCHEMA_SUMMARY",
                "table_name": "RÉCAPITULATIF_SCHEMA",
                "total_tables": len(tables),
                "schema_info": "Fichier SQL dump de structure uniquement",
                "data_status": "SCHÉMA_SEUL",
                "recommendation": "Importer les données séparément ou obtenir un dump complet"
            }
            demo_rows.append(summary_row)
            
            # 2. Ajouter une ligne pour chaque table
            for table in tables:
                table_row = {
                    "_source_table": "SCHEMA_DETAIL",
                    "table_name": table['name'],
                    "columns_count": len(table.get('columns', [])),
                    "row_count_estimate": table.get('row_count', 0),
                    "has_data": "OUI" if table.get('row_count', 0) > 0 else "NON",
                    "table_type": "STRUCTURE_SEULE",
                    "columns": ", ".join([col['name'] for col in table.get('columns', [])[:5]]) + ("..." if len(table.get('columns', [])) > 5 else "")
                }
                demo_rows.append(table_row)
            
            # 3. Ajouter des recommandations
            recommendations = [
                {
                    "_source_table": "RECOMMENDATIONS",
                    "table_name": "SOLUTIONS",
                    "solution_1": "Obtenir un dump MySQL complet avec: mysqldump --complete-insert",
                    "solution_2": "Exporter les données en CSV depuis phpMyAdmin",
                    "solution_3": "Utiliser l'interface pour importer CSV/Excel",
                    "current_status": "STRUCTURE_UNiquement",
                    "next_steps": "Sélectionner une solution ci-dessus"
                }
            ]
            demo_rows.extend(recommendations)
            
            print(f"📊 {len(demo_rows)} lignes de démonstration créées")
            
            # Supprimer les anciennes données
            db.query(DataFrameData).filter(DataFrameData.data_source_id == source.id).delete()
            
            # Insérer les nouvelles données
            for idx, row in enumerate(demo_rows):
                db_row = DataFrameData(
                    data_source_id=source.id,
                    row_data=json.dumps(row, ensure_ascii=False),
                    row_index=idx
                )
                db.add(db_row)
            
            db.commit()
            print("✅ Données de démonstration sauvegardées")
            
            # Mettre à jour le schema_info pour refléter le contenu réel
            new_schema_info = {
                "tables": tables,
                "total_tables": len(tables),
                "total_rows": len(demo_rows),  # Lignes de démonstration
                "row_count": len(demo_rows),
                "data_type": "schema_demonstration",
                "note": "Données basées sur le schéma SQL dump - fichier ne contenait que la structure",
                "processing_info": {
                    "original_file_size": os.path.getsize(source.file_path),
                    "encoding": "utf-8",
                    "tables_found": len(tables),
                    "demo_rows_created": len(demo_rows)
                }
            }
            
            source.schema_info = json.dumps(new_schema_info)
            db.commit()
            
            print("✅ Schema_info mis à jour")
            
            return True
            
        finally:
            strategy.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def verify_demo_data():
    """Vérifie que les données de démonstration sont bien présentes"""
    print("\n✅ VÉRIFICATION DES DONNÉES DE DÉMONSTRATION")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        from app.models.project import DataFrameData
        
        # Vérifier la source bb.sql
        source = db.query(DataSource).filter(DataSource.id == 5).first()
        if not source:
            print("❌ Source bb.sql non trouvée")
            return False
        
        # Compter les lignes
        row_count = db.query(DataFrameData).filter(
            DataFrameData.data_source_id == source.id
        ).count()
        
        print(f"📊 {row_count} lignes dans DataFrameData pour bb.sql")
        
        if row_count > 0:
            print("✅ Données de démonstration présentes")
            
            # Afficher un échantillon
            sample_rows = db.query(DataFrameData).filter(
                DataFrameData.data_source_id == source.id
            ).order_by(DataFrameData.row_index).limit(3).all()
            
            print("\n📋 Échantillon des données:")
            for i, row in enumerate(sample_rows):
                row_data = json.loads(row.row_data)
                print(f"   Ligne {row.row_index}: {list(row_data.keys())[:3]}...")
            
            return True
        else:
            print("❌ Aucune donnée trouvée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """Fonction principale"""
    print("🚀 CONVERSION SCHÉMA SQL → DONNÉES INTERFACE")
    print("=" * 80)
    print("Ce script va:")
    print("1. 🔍 Analyser le schéma SQL dump")
    print("2. 🔄 Créer des données de démonstration informatives")
    print("3. 💾 Sauvegarder dans DataFrameData")
    print("4. ✅ Vérifier le résultat")
    print("=" * 80)
    
    # Convertir le schéma en données
    success = convert_schema_to_demo_data()
    
    if success:
        # Vérifier le résultat
        verify_demo_data()
        
        print(f"\n{'='*80}")
        print("🎉 SUCCÈS!")
        print(f"{'='*80}")
        print("✅ Le schéma SQL a été converti en données informatives")
        print("🖥️ L'interface tkinter affichera maintenant des informations utiles")
        print("📋 Au lieu de 0 ligne, vous verrez:")
        print("   - Récapitulatif du schéma")
        print("   - Détails de chaque table")
        print("   - Recommandations pour obtenir les données")
        print("\n🔧 PROCHAINES ÉTAPES:")
        print("1. Testez l'affichage tkinter depuis l'interface web")
        print("2. Pour de vraies données, importez un dump MySQL complet")
        print("   ou utilisez CSV/Excel avec les mêmes tables")
        
    else:
        print(f"\n❌ ÉCHEC de la conversion")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
