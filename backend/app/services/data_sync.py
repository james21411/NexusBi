#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de synchronisation pour les sources de données
Implémente la vraie synchronisation selon le type de source
"""

import json
import os
import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.project import DataSource, DataFrameData
from app.services.data_sources.factory import DataSourceFactory


class DataSyncService:
    """Service de synchronisation des sources de données"""
    
    def __init__(self, db: Session):
        self.db = db
        self.factory = DataSourceFactory()
    
    async def sync_data_source(self, data_source_id: int) -> Dict[str, Any]:
        """
        Synchronise une source de données avec sa source externe
        
        Args:
            data_source_id: ID de la source de données à synchroniser
            
        Returns:
            Dict avec les informations de synchronisation
        """
        print(f"🔄 Début de la synchronisation pour la source ID: {data_source_id}")
        
        # Récupérer la source de données
        data_source = self.db.query(DataSource).filter(DataSource.id == data_source_id).first()
        if not data_source:
            raise ValueError(f"Source de données {data_source_id} non trouvée")
        
        if not data_source.is_active:
            raise ValueError("La source de données est inactive")
        
        try:
            # Exécuter la synchronisation selon le type
            sync_result = await self._sync_by_type(data_source)
            
            # Mettre à jour les métadonnées
            data_source.updated_at = datetime.utcnow()
            data_source.schema_info = json.dumps(sync_result['schema_info'])
            self.db.commit()
            
            print(f"✅ Synchronisation réussie pour {data_source.name}")
            return {
                "success": True,
                "message": f"Source '{data_source.name}' synchronisée avec succès",
                "last_sync": data_source.updated_at.isoformat(),
                "rows_updated": sync_result['rows_updated'],
                "schema_info": sync_result['schema_info'],
                "data_source_type": data_source.type
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la synchronisation: {str(e)}")
            # Marquer l'erreur dans la source
            data_source.updated_at = datetime.utcnow()
            self.db.commit()
            
            return {
                "success": False,
                "message": f"Erreur lors de la synchronisation: {str(e)}",
                "error": str(e),
                "last_sync": data_source.updated_at.isoformat() if data_source.updated_at else None
            }
    
    async def _sync_by_type(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise selon le type de source de données"""
        
        if data_source.type == 'csv':
            return await self._sync_csv_file(data_source)
        elif data_source.type in ['xlsx', 'xls']:
            return await self._sync_excel_file(data_source)
        elif data_source.type == 'json':
            return await self._sync_json_file(data_source)
        elif data_source.type == 'sql':
            return await self._sync_sql_dump_file(data_source)
        elif data_source.type == 'mysql':
            return await self._sync_mysql_db(data_source)
        elif data_source.type == 'postgresql':
            return await self._sync_postgresql_db(data_source)
        elif data_source.type == 'sql_server':
            return await self._sync_sqlserver_db(data_source)
        elif data_source.type == 'mongodb':
            return await self._sync_mongodb_db(data_source)
        else:
            # Pour les types non supportés, simuler une synchronisation
            return await self._sync_generic(data_source)
    
    async def _sync_csv_file(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise un fichier CSV"""
        if not data_source.file_path:
            raise ValueError("Chemin de fichier non défini pour la source CSV")
        
        print(f"📄 Synchronisation du fichier CSV: {data_source.file_path}")
        
        # Construire le chemin complet du fichier
        from app.core.config import settings
        upload_dir = settings.UPLOAD_DIR
        file_path = data_source.file_path
        
        # Si le chemin n'est pas absolu, le chercher dans le répertoire d'upload
        if not os.path.isabs(file_path):
            full_file_path = os.path.join(upload_dir, file_path)
        else:
            full_file_path = file_path
        
        print(f"🔍 Recherche du fichier à: {full_file_path}")
        
        # Vérifier si le fichier existe
        if not os.path.exists(full_file_path):
            raise ValueError(f"Fichier CSV non trouvé: {full_file_path}")
        
        # Lire le fichier avec les paramètres sauvegardés
        schema_info = json.loads(data_source.schema_info) if data_source.schema_info else {}
        processing_info = schema_info.get('processing_info', {})
        
        encoding = processing_info.get('detected_encoding', 'utf-8')
        delimiter = processing_info.get('detected_delimiter', ',')
        
        try:
            df = pd.read_csv(full_file_path, encoding=encoding, sep=delimiter)
            print(f"📊 CSV lu: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Mettre à jour les données en base
            await self._update_dataframe_data(data_source.id, df)
            
            # Préparer le schéma mis à jour
            new_schema_info = {
                "columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                "row_count": len(df),
                "column_count": len(df.columns),
                "processing_info": processing_info,
                "file_modified": datetime.fromtimestamp(os.path.getmtime(full_file_path)).isoformat()
            }
            
            return {
                "rows_updated": len(df),
                "schema_info": new_schema_info
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du CSV: {str(e)}")
    
    async def _sync_excel_file(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise un fichier Excel"""
        if not data_source.file_path:
            raise ValueError("Chemin de fichier non défini pour la source Excel")
        
        print(f"📊 Synchronisation du fichier Excel: {data_source.file_path}")
        
        # Construire le chemin complet du fichier
        from app.core.config import settings
        upload_dir = settings.UPLOAD_DIR
        file_path = data_source.file_path
        
        # Si le chemin n'est pas absolu, le chercher dans le répertoire d'upload
        if not os.path.isabs(file_path):
            full_file_path = os.path.join(upload_dir, file_path)
        else:
            full_file_path = file_path
        
        print(f"🔍 Recherche du fichier à: {full_file_path}")
        
        if not os.path.exists(full_file_path):
            raise ValueError(f"Fichier Excel non trouvé: {full_file_path}")
        
        try:
            # Lire le fichier Excel (première feuille par défaut)
            df = pd.read_excel(full_file_path)
            print(f"📊 Excel lu: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Mettre à jour les données en base
            await self._update_dataframe_data(data_source.id, df)
            
            # Préparer le schéma mis à jour
            new_schema_info = {
                "columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                "row_count": len(df),
                "column_count": len(df.columns),
                "processing_info": {"processing_method": "pandas_excel"},
                "file_modified": datetime.fromtimestamp(os.path.getmtime(full_file_path)).isoformat()
            }
            
            return {
                "rows_updated": len(df),
                "schema_info": new_schema_info
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier Excel: {str(e)}")
    
    async def _sync_json_file(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise un fichier JSON"""
        if not data_source.file_path:
            raise ValueError("Chemin de fichier non défini pour la source JSON")
        
        print(f"🔗 Synchronisation du fichier JSON: {data_source.file_path}")
        
        # Construire le chemin complet du fichier
        from app.core.config import settings
        upload_dir = settings.UPLOAD_DIR
        file_path = data_source.file_path
        
        # Si le chemin n'est pas absolu, le chercher dans le répertoire d'upload
        if not os.path.isabs(file_path):
            full_file_path = os.path.join(upload_dir, file_path)
        else:
            full_file_path = file_path
        
        print(f"🔍 Recherche du fichier à: {full_file_path}")
        
        if not os.path.exists(full_file_path):
            raise ValueError(f"Fichier JSON non trouvé: {full_file_path}")
        
        try:
            df = pd.read_json(full_file_path)
            print(f"📊 JSON lu: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Mettre à jour les données en base
            await self._update_dataframe_data(data_source.id, df)
            
            # Préparer le schéma mis à jour
            new_schema_info = {
                "columns": [{"name": col, "type": str(df[col].dtype)} for col in df.columns],
                "row_count": len(df),
                "column_count": len(df.columns),
                "processing_info": {"processing_method": "pandas_json"},
                "file_modified": datetime.fromtimestamp(os.path.getmtime(full_file_path)).isoformat()
            }
            
            return {
                "rows_updated": len(df),
                "schema_info": new_schema_info
            }
            
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier JSON: {str(e)}")
    
    async def _sync_sql_dump_file(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise un fichier SQL dump"""
        if not data_source.file_path:
            raise ValueError("Chemin de fichier non défini pour la source SQL dump")
        
        print(f"🗄️ Synchronisation du fichier SQL dump: {data_source.file_path}")
        
        # Construire le chemin complet du fichier
        from app.core.config import settings
        upload_dir = settings.UPLOAD_DIR
        file_path = data_source.file_path
        
        # Si le chemin n'est pas absolu, le chercher dans le répertoire d'upload
        if not os.path.isabs(file_path):
            full_file_path = os.path.join(upload_dir, file_path)
        else:
            full_file_path = file_path
        
        print(f"🔍 Recherche du fichier à: {full_file_path}")
        
        if not os.path.exists(full_file_path):
            raise ValueError(f"Fichier SQL dump non trouvé: {full_file_path}")
        
        try:
            # Lire les paramètres de traitement
            schema_info = json.loads(data_source.schema_info) if data_source.schema_info else {}
            processing_info = schema_info.get('processing_info', {})
            
            encoding = processing_info.get('detected_encoding', 'utf-8')
            
            # Utiliser la factory pour créer la stratégie SQL dump
            strategy = self.factory.get_source('sql_dump', {
                'file_path': full_file_path,
                'encoding': encoding
            })
            
            strategy.connect()
            
            try:
                # Obtenir le schéma complet
                schema = strategy.get_schema()
                
                # Obtenir TOUTES les données de toutes les tables
                all_table_data = strategy.get_all_table_data()
                
                # Combiner toutes les tables en une seule DataFrame
                if all_table_data:
                    all_dataframes = []
                    for table_name, table_df in all_table_data.items():
                        # Add table name column to identify source
                        table_df_with_source = table_df.copy()
                        table_df_with_source.insert(0, '_source_table', table_name)
                        all_dataframes.append(table_df_with_source)
                    
                    combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
                else:
                    combined_df = pd.DataFrame()
                
                print(f"📊 SQL dump analysé: {len(schema.get('tables', []))} tables, {len(combined_df)} lignes au total")
                
                # Mettre à jour les données en base
                await self._update_dataframe_data(data_source.id, combined_df)
                
                # Préparer le schéma mis à jour
                new_schema_info = {
                    "tables": schema.get('tables', []),
                    "total_tables": len(schema.get('tables', [])),
                    "total_rows": sum(table.get('row_count', 0) for table in schema.get('tables', [])),
                    "processing_info": {
                        "processing_method": "sql_dump_parser",
                        "encoding": encoding,
                        "extracted_rows": len(combined_df),
                        "tables_processed": list(all_table_data.keys()) if all_table_data else []
                    },
                    "file_modified": datetime.fromtimestamp(os.path.getmtime(full_file_path)).isoformat()
                }
                
                return {
                    "rows_updated": len(combined_df),
                    "schema_info": new_schema_info
                }
                
            finally:
                strategy.disconnect()
                
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier SQL dump: {str(e)}")
    
    async def _sync_mysql_db(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise une base MySQL"""
        return await self._sync_database_generic(data_source, "mysql")
    
    async def _sync_postgresql_db(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise une base PostgreSQL"""
        return await self._sync_database_generic(data_source, "postgresql")
    
    async def _sync_sqlserver_db(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise une base SQL Server"""
        return await self._sync_database_generic(data_source, "sql_server")
    
    async def _sync_mongodb_db(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronise une base MongoDB"""
        return await self._sync_database_generic(data_source, "mongodb")
    
    async def _sync_database_generic(self, data_source: DataSource, db_type: str) -> Dict[str, Any]:
        """Synchronise une base de données générique"""
        if not data_source.connection_string:
            raise ValueError("Chaîne de connexion non définie pour la source de base de données")
        
        print(f"🗄️ Synchronisation de la base {db_type}: {data_source.name}")
        
        try:
            # Utiliser la factory pour créer la stratégie
            strategy = self.factory.get_source(db_type, {"connection_string": data_source.connection_string})
            strategy.connect()
            
            try:
                # Obtenir le schéma et les données
                schema = strategy.get_schema()
                df = strategy.get_data(limit=1000)  # Limiter à 1000 lignes pour la prévisualisation
                
                print(f"📊 Base de données lue: {len(df)} lignes, {len(df.columns)} colonnes")
                
                # Mettre à jour les données en base
                await self._update_dataframe_data(data_source.id, df)
                
                # Préparer le schéma mis à jour
                new_schema_info = {
                    "columns": schema.get("columns", []),
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "processing_info": {
                        "processing_method": f"database_{db_type}",
                        "connection_string": "***",  # Masquer pour la sécurité
                        "query_limit": 1000
                    },
                    "last_sync": datetime.utcnow().isoformat()
                }
                
                return {
                    "rows_updated": len(df),
                    "schema_info": new_schema_info
                }
                
            finally:
                strategy.disconnect()
                
        except Exception as e:
            raise ValueError(f"Erreur lors de la synchronisation de la base {db_type}: {str(e)}")
    
    async def _sync_generic(self, data_source: DataSource) -> Dict[str, Any]:
        """Synchronisation générique pour types non supportés"""
        print(f"🔄 Synchronisation générique pour: {data_source.type}")
        
        # Simuler une synchronisation en mettant à jour seulement le timestamp
        return {
            "rows_updated": 0,
            "schema_info": json.loads(data_source.schema_info) if data_source.schema_info else {}
        }
    
    def _detect_large_data_columns(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Détecte les colonnes avec des données volumineuses (images base64, etc.)"""
        large_columns = {}
        
        # Seuil pour considérer une donnée comme "volumineuse" (10KB)
        LARGE_DATA_THRESHOLD = 10 * 1024
        
        for col in df.columns:
            # Vérifier si la colonne contient des données volumineuses
            large_values = 0
            total_values = 0
            
            for val in df[col].dropna():
                total_values += 1
                val_str = str(val)
                # Détecter base64 (commence par常见的base64 patterns)
                if (len(val_str) > LARGE_DATA_THRESHOLD or
                    val_str.startswith('data:image/') or
                    val_str.startswith('iVBOR') or  # PNG base64
                    val_str.startswith('/9j/') or   # JPEG base64
                    (len(val_str) > 100 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in val_str[:100]))):
                    large_values += 1
                
                # Vérifier seulement les premières valeurs pour la performance
                if total_values >= 10:
                    break
            
            # Si plus de 50% des valeurs échantillonnées sont volumineuses, marquer la colonne
            if total_values > 0 and large_values / total_values > 0.5:
                large_columns[col] = True
        
        return large_columns
    
    def _sanitize_large_data(self, value: str, is_large_column: bool) -> str:
        """Remplace les données volumineuses par des labels"""
        if is_large_column:
            if not value or value == 'nan' or value == 'None':
                return "[Données vides]"
            else:
                return f"[Données volumineuses - {len(value)} caractères]"
        return value
    
    async def _update_dataframe_data(self, data_source_id: int, df: pd.DataFrame) -> None:
        """Met à jour les données DataFrame en base"""
        print(f"💾 Mise à jour des données en base pour la source {data_source_id}")
        
        # Détecter les colonnes avec des données volumineuses
        large_columns = self._detect_large_data_columns(df)
        if large_columns:
            print(f"🔍 Détecté colonnes avec données volumineuses: {list(large_columns.keys())}")
        
        # Supprimer les anciennes données
        self.db.query(DataFrameData).filter(DataFrameData.data_source_id == data_source_id).delete()
        
        # Insérer les nouvelles données
        for idx, row in df.iterrows():
            row_dict = {}
            for col, val in row.items():
                val_str = str(val) if val is not None else ""
                # Sanitize si c'est une colonne avec des données volumineuses
                sanitized_val = self._sanitize_large_data(val_str, large_columns.get(col, False))
                row_dict[col] = sanitized_val
            
            db_row = DataFrameData(
                data_source_id=data_source_id,
                row_data=json.dumps(row_dict),
                row_index=idx
            )
            self.db.add(db_row)
        
        self.db.commit()
        print(f"✅ {len(df)} lignes mises à jour en base")
        if large_columns:
            print(f"📊 {len(large_columns)} colonnes avec données volumineuses处理ées")


def create_sync_service(db: Session) -> DataSyncService:
    """Factory pour créer un service de synchronisation"""
    return DataSyncService(db)