#!/usr/bin/env python3
"""
Script pour créer uniquement la table dataframe_data manquante
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey
from app.core.config import settings

def create_dataframe_table():
    """Créer uniquement la table dataframe_data"""
    print("🏗️  Création de la table dataframe_data...")

    # Créer le moteur de base de données
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

    # Définir la table dataframe_data
    metadata = MetaData()

    dataframe_data_table = Table(
        'dataframe_data',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('data_source_id', Integer, ForeignKey('data_sources.id'), nullable=False),
        Column('row_data', Text, nullable=False),
        Column('row_index', Integer, nullable=False),
    )

    try:
        # Créer la table si elle n'existe pas
        dataframe_data_table.create(engine, checkfirst=True)
        print("✅ Table dataframe_data créée avec succès!")

    except Exception as e:
        print(f"❌ Erreur lors de la création de la table: {e}")

if __name__ == "__main__":
    create_dataframe_table()