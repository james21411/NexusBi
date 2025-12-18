from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import subprocess
import sys
import os
import json
from pathlib import Path

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import DataSource, DataFrameData

router = APIRouter()


@router.post("/launch-preview/{data_source_id}")
async def launch_data_preview(
    data_source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lance l'interface tkinter de prévisualisation des données
    """
    try:
        print(f"Tentative de lancement pour la source de données ID: {data_source_id}")
        
        # Vérifier que la source de données existe
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        
        if not data_source:
            print(f"Source de données {data_source_id} non trouvée")
            raise HTTPException(status_code=404, detail="Source de données non trouvée")
        
        print(f"Source de données trouvée: {data_source.name}")
        
        # Obtenir le token de l'utilisateur pour l'authentification
        from app.core.security import create_access_token
        token = create_access_token(subject=str(current_user.id))
        print(f"Token généré pour l'utilisateur: {current_user.email}")
        
        # Obtenir l'URL de base de l'API
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        print(f"URL API: {api_base_url}")
        
        # Préparer les arguments pour le launcher
        # Remonter au répertoire racine du projet (où se trouve le script tkinter fixe)
        # From backend/app/api/v1/endpoints/ we need to go up 6 levels to reach NexusBi root
        current_dir = Path(__file__).parent.parent.parent.parent.parent.parent
        launcher_script = current_dir / "data_preview_tkinter_fixed.py"

        if not launcher_script.exists():
            print(f"Script de lancement non trouvé: {launcher_script}")
            raise HTTPException(status_code=500, detail="Script de lancement non trouvé")
        
        print(f"Script de lancement trouvé: {launcher_script}")
        
        # Construire la commande
        cmd = [
            sys.executable,
            str(launcher_script),
            "--data-source-id", str(data_source_id),
            "--api-base-url", api_base_url,
            "--auth-token", token
        ]
        
        print(f"Commande à exécuter: {' '.join(cmd)}")
        
        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(current_dir)
        )
        
        print(f"Processus lancé avec PID: {process.pid}")
        
        return {
            "success": True,
            "message": "Interface de prévisualisation lancée avec succès",
            "data_source_id": data_source_id,
            "data_source_name": data_source.name,
            "process_id": process.pid,
            "user_email": current_user.email
        }
        
    except HTTPException:
        print(f"Erreur HTTP: {str(e)}")
        raise
    except Exception as e:
        print(f"Erreur lors du lancement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement: {str(e)}")


@router.get("/preview-status/{data_source_id}")
async def get_preview_status(
    data_source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vérifie le statut de l'interface de prévisualisation
    """
    try:
        # Vérifier que la source de données existe
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        
        if not data_source:
            raise HTTPException(status_code=404, detail="Source de données non trouvée")
        
        return {
            "data_source_id": data_source_id,
            "data_source_name": data_source.name,
            "status": "available",
            "can_launch": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/test-launch/{data_source_id}")
async def test_launch_preview(
    data_source_id: int
):
    """
    Endpoint de test pour lancer tkinter sans authentification
    """
    try:
        print(f"Test de lancement pour la source de données ID: {data_source_id}")
        
        # Obtenir l'URL de base de l'API
        api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        print(f"URL API: {api_base_url}")
        
        # Préparer les arguments pour le launcher
        # Remonter au répertoire racine du projet (où se trouve le script tkinter fixe)
        # From backend/app/api/v1/endpoints/ we need to go up 6 levels to reach NexusBi root
        current_dir = Path(__file__).parent.parent.parent.parent.parent.parent
        launcher_script = current_dir / "data_preview_tkinter_fixed.py"
        
        if not launcher_script.exists():
            print(f"Script de lancement non trouvé: {launcher_script}")
            raise HTTPException(status_code=500, detail="Script de lancement non trouvé")
        
        print(f"Script de lancement trouvé: {launcher_script}")
        
        # Construire la commande SANS token d'authentification
        cmd = [
            sys.executable,
            str(launcher_script),
            "--data-source-id", str(data_source_id),
            "--api-base-url", api_base_url
            # Pas de --auth-token pour le test
        ]
        
        print(f"Commande de test à exécuter: {' '.join(cmd)}")
        
        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(current_dir)
        )
        
        print(f"Processus de test lancé avec PID: {process.pid}")
        
        return {
            "success": True,
            "message": "Test de lancement tkinter réussi",
            "data_source_id": data_source_id,
            "process_id": process.pid,
            "note": "Test sans authentification - utilise des données fictives"
        }
        
    except Exception as e:
        print(f"Erreur lors du test de lancement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du test: {str(e)}")


@router.get("/preview-data/{data_source_id}")
async def get_preview_data_public(
    data_source_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Endpoint public pour récupérer les données d'aperçu sans authentification
    """
    try:
        print(f"📊 Récupération des données d'aperçu pour la source ID: {data_source_id}")
        
        # Vérifier que la source de données existe
        data_source = db.query(DataSource).filter(DataSource.id == data_source_id).first()
        
        if not data_source:
            raise HTTPException(status_code=404, detail="Source de données non trouvée")
        
        # Get total count of rows for this data source
        total_count = db.query(DataFrameData).filter(DataFrameData.data_source_id == data_source_id).count()

        # Get data rows
        data_rows = (
            db.query(DataFrameData)
            .filter(DataFrameData.data_source_id == data_source_id)
            .order_by(DataFrameData.row_index)
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Parse row data
        rows = []
        for row in data_rows:
            rows.append(json.loads(row.row_data))

        print(f"✅ Données récupérées: {len(rows)} lignes (total: {total_count})")
        
        return {
            "data_source_id": data_source_id,
            "rows": rows,
            "total_rows": total_count,
            "skip": skip,
            "limit": limit,
            "data_source_name": data_source.name,
            "data_source_type": data_source.type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


@router.post("/close-preview/{data_source_id}")
async def close_data_preview(
    data_source_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ferme l'interface de prévisualisation (si elle est encore ouverte)
    """
    try:
        # Cette fonction pourrait être étendue pour tuer le processus tkinter
        # Pour l'instant, on retourne juste un message de succès
        
        return {
            "success": True,
            "message": "Demande de fermeture envoyée",
            "data_source_id": data_source_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")