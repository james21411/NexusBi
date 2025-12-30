"""
Endpoints pour la prévisualisation des données et lancement des interfaces tkinter.
Version simplifiée pour éviter les erreurs d'authentification.
"""

import subprocess
import os
import sys
import logging
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.user import User

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Dictionnaire pour stocker les processus en cours
launched_processes: Dict[str, Dict[str, Any]] = {}

@router.post("/launch-preview/{data_source_id}")
async def launch_preview_interface(
    data_source_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Lance l'interface tkinter de prévisualisation des données pour une source de données spécifique.
    Version simplifiée sans authentification stricte.
    """
    try:
        logger.info(f"Demande de lancement de l'interface de prévisualisation pour la source {data_source_id}")

        # Vérifier si X11 est configuré
        display = os.environ.get('DISPLAY')
        if not display:
            raise HTTPException(status_code=500, detail="Variable DISPLAY non configurée - X11 requis pour tkinter")

        # Créer des données de démonstration
        demo_data = [
            {"id": 1, "nom": "Jean Dupont", "âge": 25, "ville": "Paris", "salaire": 45000},
            {"id": 2, "nom": "Marie Martin", "âge": 30, "ville": "Lyon", "salaire": 52000},
            {"id": 3, "nom": "Pierre Durand", "âge": 35, "ville": "Marseille", "salaire": 48000},
            {"id": 4, "nom": "Sophie Bernard", "âge": 28, "ville": "Toulouse", "salaire": 51000},
            {"id": 5, "nom": "Lucas Petit", "âge": 32, "ville": "Nice", "salaire": 55000}
        ]

        # Créer un fichier temporaire avec les données de démonstration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(demo_data, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name

        # Construire le chemin vers le script tkinter
        # Le script est dans le répertoire parent du backend
        script_path = Path.cwd().parent / "data_preview_tkinter_complete.py"

        if not script_path.exists():
            raise HTTPException(status_code=500, detail=f"Script tkinter non trouvé: {script_path}")

        # Préparer la commande
        command = [
            sys.executable, str(script_path), temp_file_path
        ]

        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent)
        )

        # Stocker les informations du processus
        process_id = f"preview_{data_source_id}_{process.pid}"
        launched_processes[process_id] = {
            "process": process,
            "data_source_id": data_source_id,
            "user_id": None,
            "temp_file": temp_file_path,
            "script_path": str(script_path),
            "command": command,
            "started_at": process.create_time(),
            "demo_mode": True
        }

        logger.info(f"Processus lancé avec succès: PID {process.pid}")

        return {
            "success": True,
            "message": f"Interface de prévisualisation lancée avec succès",
            "process_id": process_id,
            "pid": process.pid,
            "data_source_name": f"Démonstration (source {data_source_id})"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface de prévisualisation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement: {str(e)}")

@router.post("/test-launch/{data_source_id}")
async def test_launch_preview_interface(
    data_source_id: int,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Test de lancement de l'interface tkinter de prévisualisation (sans authentification).
    Utilisé pour les tests et démonstrations.
    """
    try:
        logger.info(f"Test de lancement de l'interface de prévisualisation pour la source {data_source_id}")

        # Vérifier si X11 est configuré
        display = os.environ.get('DISPLAY')
        if not display:
            raise HTTPException(status_code=500, detail="Variable DISPLAY non configurée - X11 requis pour tkinter")

        # Créer des données de démonstration
        demo_data = [
            {"id": 1, "nom": "Jean Dupont", "âge": 25, "ville": "Paris", "salaire": 45000},
            {"id": 2, "nom": "Marie Martin", "âge": 30, "ville": "Lyon", "salaire": 52000},
            {"id": 3, "nom": "Pierre Durand", "âge": 35, "ville": "Marseille", "salaire": 48000},
            {"id": 4, "nom": "Sophie Bernard", "âge": 28, "ville": "Toulouse", "salaire": 51000},
            {"id": 5, "nom": "Lucas Petit", "âge": 32, "ville": "Nice", "salaire": 55000}
        ]

        # Créer un fichier temporaire avec les données de démonstration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(demo_data, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name

        # Construire le chemin vers le script tkinter
        # Le script est dans le répertoire parent du backend
        script_path = Path.cwd().parent / "data_preview_tkinter_complete.py"

        if not script_path.exists():
            raise HTTPException(status_code=500, detail=f"Script tkinter non trouvé: {script_path}")

        # Préparer la commande
        command = [
            sys.executable, str(script_path), temp_file_path
        ]

        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent)
        )

        # Stocker les informations du processus
        process_id = f"test_preview_{data_source_id}_{process.pid}"
        launched_processes[process_id] = {
            "process": process,
            "data_source_id": data_source_id,
            "user_id": None,
            "temp_file": temp_file_path,
            "script_path": str(script_path),
            "command": command,
            "started_at": process.create_time(),
            "demo_mode": True
        }

        logger.info(f"Test de processus lancé avec succès: PID {process.pid}")

        return {
            "success": True,
            "message": f"Interface de test de prévisualisation lancée avec succès",
            "process_id": process_id,
            "pid": process.pid,
            "data_source_name": f"Démonstration (source {data_source_id})"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du test de lancement de l'interface de prévisualisation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du test de lancement: {str(e)}")

@router.post("/launch-statistics/{data_source_id}")
async def launch_statistics_interface(
    data_source_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Lance l'interface tkinter de statistiques pour une source de données spécifique.
    Version simplifiée sans authentification stricte.
    """
    try:
        logger.info(f"Demande de lancement de l'interface de statistiques pour la source {data_source_id}")

        # Vérifier si X11 est configuré
        display = os.environ.get('DISPLAY')
        if not display:
            raise HTTPException(status_code=500, detail="Variable DISPLAY non configurée - X11 requis pour tkinter")

        # Créer des statistiques de démonstration
        demo_stats = {
            "source_id": data_source_id,
            "source_name": f"Démonstration (source {data_source_id})",
            "summary": {
                "total_rows": 5,
                "total_columns": 4,
                "memory_usage": "1.2 KB",
                "data_types": {"int64": 2, "object": 2}
            },
            "descriptive_stats": {
                "nom": {
                    "count": 5,
                    "unique": 5,
                    "top": "Jean Dupont",
                    "freq": 1
                },
                "âge": {
                    "count": 5,
                    "mean": 30.0,
                    "std": 3.16,
                    "min": 25,
                    "25%": 28,
                    "50%": 30,
                    "75%": 32,
                    "max": 35
                },
                "ville": {
                    "count": 5,
                    "unique": 5,
                    "top": "Paris",
                    "freq": 1
                },
                "salaire": {
                    "count": 5,
                    "mean": 51000.0,
                    "std": 3897.11,
                    "min": 45000,
                    "25%": 48000,
                    "50%": 51000,
                    "75%": 52000,
                    "max": 55000
                }
            },
            "data_quality": {
                "missing_values": 0,
                "duplicate_rows": 0,
                "completeness": 100.0
            },
            "correlations": {
                "âge_salaire": 0.75,
                "âge_ville": 0.12
            }
        }

        # Créer un fichier temporaire avec les statistiques de démonstration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(demo_stats, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name

        # Construire le chemin vers le script tkinter des statistiques
        # Le script est dans le répertoire parent du backend
        script_path = Path.cwd().parent / "statistics_tkinter.py"

        if not script_path.exists():
            raise HTTPException(status_code=500, detail=f"Script tkinter des statistiques non trouvé: {script_path}")

        # Préparer la commande
        command = [
            sys.executable, str(script_path), temp_file_path
        ]

        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent)
        )

        # Stocker les informations du processus
        process_id = f"stats_{data_source_id}_{process.pid}"
        launched_processes[process_id] = {
            "process": process,
            "data_source_id": data_source_id,
            "user_id": None,
            "temp_file": temp_file_path,
            "script_path": str(script_path),
            "command": command,
            "started_at": process.create_time(),
            "demo_mode": True
        }

        logger.info(f"Processus de statistiques lancé avec succès: PID {process.pid}")

        return {
            "success": True,
            "message": f"Interface de statistiques lancée avec succès",
            "process_id": process_id,
            "pid": process.pid,
            "data_source_name": f"Démonstration (source {data_source_id})"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'interface de statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement: {str(e)}")

@router.post("/test-launch-statistics/{data_source_id}")
async def test_launch_statistics_interface(
    data_source_id: int,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Test de lancement de l'interface tkinter de statistiques (sans authentification).
    Utilisé pour les tests et démonstrations.
    """
    try:
        logger.info(f"Test de lancement de l'interface de statistiques pour la source {data_source_id}")

        # Vérifier si X11 est configuré
        display = os.environ.get('DISPLAY')
        if not display:
            raise HTTPException(status_code=500, detail="Variable DISPLAY non configurée - X11 requis pour tkinter")

        # Créer des statistiques de démonstration
        demo_stats = {
            "source_id": data_source_id,
            "source_name": f"Démonstration (source {data_source_id})",
            "summary": {
                "total_rows": 5,
                "total_columns": 4,
                "memory_usage": "1.2 KB",
                "data_types": {"int64": 2, "object": 2}
            },
            "descriptive_stats": {
                "nom": {
                    "count": 5,
                    "unique": 5,
                    "top": "Jean Dupont",
                    "freq": 1
                },
                "âge": {
                    "count": 5,
                    "mean": 30.0,
                    "std": 3.16,
                    "min": 25,
                    "25%": 28,
                    "50%": 30,
                    "75%": 32,
                    "max": 35
                },
                "ville": {
                    "count": 5,
                    "unique": 5,
                    "top": "Paris",
                    "freq": 1
                },
                "salaire": {
                    "count": 5,
                    "mean": 51000.0,
                    "std": 3897.11,
                    "min": 45000,
                    "25%": 48000,
                    "50%": 51000,
                    "75%": 52000,
                    "max": 55000
                }
            },
            "data_quality": {
                "missing_values": 0,
                "duplicate_rows": 0,
                "completeness": 100.0
            },
            "correlations": {
                "âge_salaire": 0.75,
                "âge_ville": 0.12
            }
        }

        # Créer un fichier temporaire avec les statistiques de démonstration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(demo_stats, temp_file, ensure_ascii=False, indent=2)
            temp_file_path = temp_file.name

        # Construire le chemin vers le script tkinter des statistiques
        # Le script est dans le répertoire parent du backend
        script_path = Path.cwd().parent / "statistics_tkinter.py"

        if not script_path.exists():
            raise HTTPException(status_code=500, detail=f"Script tkinter des statistiques non trouvé: {script_path}")

        # Préparer la commande
        command = [
            sys.executable, str(script_path), temp_file_path
        ]

        # Lancer le processus en arrière-plan
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(script_path.parent)
        )

        # Stocker les informations du processus
        process_id = f"test_stats_{data_source_id}_{process.pid}"
        launched_processes[process_id] = {
            "process": process,
            "data_source_id": data_source_id,
            "user_id": None,
            "temp_file": temp_file_path,
            "script_path": str(script_path),
            "command": command,
            "started_at": process.create_time(),
            "demo_mode": True
        }

        logger.info(f"Test de processus de statistiques lancé avec succès: PID {process.pid}")

        return {
            "success": True,
            "message": f"Interface de test de statistiques lancée avec succès",
            "process_id": process_id,
            "pid": process.pid,
            "data_source_name": f"Démonstration (source {data_source_id})"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du test de lancement de l'interface de statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du test de lancement: {str(e)}")

@router.post("/demo-launch-statistics")
async def demo_launch_statistics(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Retourne des statistiques de démonstration.
    """
    try:
        logger.info("Demande de démonstration des statistiques")

        # Créer des statistiques de démonstration
        demo_stats = {
            "source_id": "demo",
            "source_name": "Démonstration Statistiques",
            "summary": {
                "total_rows": 1000,
                "total_columns": 5,
                "memory_usage": "50 KB",
                "data_types": {"int64": 2, "float64": 1, "object": 2}
            },
            "descriptive_stats": {
                "age": {
                    "count": 1000,
                    "mean": 35.5,
                    "std": 12.3,
                    "min": 18,
                    "25%": 25,
                    "50%": 35,
                    "75%": 45,
                    "max": 70
                },
                "salary": {
                    "count": 1000,
                    "mean": 55000.0,
                    "std": 15000.0,
                    "min": 25000,
                    "25%": 40000,
                    "50%": 55000,
                    "75%": 70000,
                    "max": 120000
                },
                "department": {
                    "count": 1000,
                    "unique": 5,
                    "top": "IT",
                    "freq": 300
                },
                "experience": {
                    "count": 1000,
                    "mean": 8.5,
                    "std": 5.2,
                    "min": 0,
                    "25%": 3,
                    "50%": 8,
                    "75%": 12,
                    "max": 25
                }
            },
            "data_quality": {
                "missing_values": 50,
                "duplicate_rows": 0,
                "completeness": 95.0
            },
            "correlations": {
                "age_experience": 0.85,
                "age_salary": 0.65,
                "experience_salary": 0.75
            }
        }

        logger.info("Statistiques de démonstration générées")

        return {
            "success": True,
            "message": "Démonstration des statistiques récupérée avec succès",
            "data": demo_stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la démonstration des statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la démonstration: {str(e)}")

# Endpoint supplémentaire pour compatibilité avec l'interface de visualisation
@router.post("/demo-launch")
async def demo_launch_compatibility(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Endpoint de compatibilité pour les démonstrations - retourne des données de démonstration.
    """
    try:
        logger.info("Demande de démonstration (compatibilité)")

        # Créer des données de démonstration
        demo_data = [
            {"id": 1, "nom": "Jean Dupont", "âge": 25, "ville": "Paris", "salaire": 45000},
            {"id": 2, "nom": "Marie Martin", "âge": 30, "ville": "Lyon", "salaire": 52000},
            {"id": 3, "nom": "Pierre Durand", "âge": 35, "ville": "Marseille", "salaire": 48000},
            {"id": 4, "nom": "Sophie Bernard", "âge": 28, "ville": "Toulouse", "salaire": 51000},
            {"id": 5, "nom": "Lucas Petit", "âge": 32, "ville": "Nice", "salaire": 55000}
        ]

        logger.info("Données de démonstration générées")

        return {
            "success": True,
            "message": "Démonstration lancée avec succès",
            "data": demo_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la démonstration de compatibilité: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du lancement: {str(e)}")

@router.get("/launched-processes")
async def get_launched_processes():
    """
    Récupère la liste des processus lancés.
    """
    try:
        # Filtrer les processus actifs
        active_processes = {}
        for process_id, info in launched_processes.items():
            process = info.get('process')
            if process and process.poll() is None:  # Processus encore en cours
                active_processes[process_id] = {
                    "process_id": process_id,
                    "pid": process.pid,
                    "data_source_id": info.get('data_source_id'),
                    "started_at": info.get('started_at'),
                    "script_path": info.get('script_path'),
                    "is_alive": True
                }
            else:
                # Nettoyer les processus terminés
                if process:
                    try:
                        process.kill()
                    except:
                        pass
                try:
                    os.unlink(info.get('temp_file', ''))
                except:
                    pass
                del launched_processes[process_id]
        
        return {
            "success": True,
            "processes": list(active_processes.values())
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des processus: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.delete("/terminate-process/{process_id}")
async def terminate_process(process_id: str):
    """
    Termine un processus lancé.
    """
    try:
        if process_id not in launched_processes:
            raise HTTPException(status_code=404, detail="Processus non trouvé")
        
        info = launched_processes[process_id]
        process = info.get('process')
        if process:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.warning(f"Erreur lors de la terminaison du processus {process.pid}: {e}")
        
        # Nettoyer les fichiers temporaires
        try:
            os.unlink(info.get('temp_file', ''))
        except:
            pass
        
        # Supprimer de la liste
        del launched_processes[process_id]
        
        return {
            "success": True,
            "message": "Processus terminé avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la terminaison du processus: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")