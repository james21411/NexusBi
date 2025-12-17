#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement pour l'interface tkinter de prévisualisation des données
Version corrigée pour permettre à la GUI de rester ouverte
"""

import subprocess
import sys
import os
import json
import argparse
import time
from pathlib import Path


def launch_data_preview(data_source_id: int, api_base_url: str = "http://localhost:8000", auth_token: str = None):
    """
    Lance l'interface tkinter de prévisualisation des données
    
    Args:
        data_source_id: ID de la source de données à afficher
        api_base_url: URL de base de l'API backend
        auth_token: Token d'authentification (optionnel)
    """
    print("🚀 Lancement de launch_data_preview")
    print(f"📋 Paramètres reçus:")
    print(f"   - data_source_id: {data_source_id}")
    print(f"   - api_base_url: {api_base_url}")
    print(f"   - auth_token: {'***' if auth_token else None}")
    
    try:
        # Obtenir le chemin vers le script tkinter
        current_dir = Path(__file__).parent
        tkinter_script = current_dir / "data_preview_tkinter.py"
        print(f"🔍 Recherche du script: {tkinter_script}")
        print(f"📁 Répertoire courant: {current_dir}")
        
        if not tkinter_script.exists():
            print(f"❌ Erreur: Script tkinter non trouvé: {tkinter_script}")
            print(f"📂 Contenu du répertoire:")
            for file in current_dir.iterdir():
                print(f"   - {file.name}")
            return False
        
        print(f"✅ Script tkinter trouvé: {tkinter_script}")
        
        # Préparer les arguments
        args = [sys.executable, str(tkinter_script)]
        if data_source_id:
            args.extend(["--data-source-id", str(data_source_id)])
        if api_base_url:
            # Ensure the API base URL includes the /api/v1/ prefix
            if not api_base_url.endswith('/api/v1'):
                api_base_url = api_base_url.rstrip('/') + '/api/v1'
            args.extend(["--api-base-url", api_base_url])
        if auth_token:
            args.extend(["--auth-token", auth_token])
        
        print(f"⚙️ Arguments de commande: {args}")
        
        # Lancer le processus tkinter avec environnement graphique
        print(f"🖥️ Lancement de l'interface tkinter pour la source {data_source_id}")
        
        # Créer un nouvel environnement pour le processus
        env = os.environ.copy()
        env['DISPLAY'] = env.get('DISPLAY', ':0')  # Assurer que DISPLAY est défini
        print(f"🖥️ Configuration DISPLAY: {env.get('DISPLAY')}")
        
        print("🔧 Lancement du processus...")
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid  # Créer un nouveau groupe de processus
        )
        
        print(f"✅ Processus lancé avec PID: {process.pid}")
        
        # Attendre un peu pour voir si le processus démarre correctement
        time.sleep(2)
        
        # Vérifier si le processus est toujours en cours d'exécution
        if process.poll() is None:
            print("✅ Interface de prévisualisation lancée avec succès. PID:", process.pid)
            print(f"🔍 PID du processus: {process.pid}")
            print("🎯 Le processus continue en arrière-plan (normal pour une GUI)")
            
            # Ne pas terminer le processus - laisser la GUI ouverte
            print("🚀 Lancement réussi - Interface disponible")
            return True
        else:
            # Le processus s'est arrêté - récupérer les erreurs
            stdout, stderr = process.communicate()
            if stdout:
                print(f"📤 STDOUT:\n{stdout.decode()}")
            if stderr:
                print(f"❌ STDERR:\n{stderr.decode()}")
            print(f"❌ Erreur lors du lancement - Code de retour: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'interface tkinter: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Fonction principale pour utilisation en ligne de commande"""
    parser = argparse.ArgumentParser(description="Lance l'interface tkinter de prévisualisation des données")
    parser.add_argument("--data-source-id", type=int, required=True, help="ID de la source de données")
    parser.add_argument("--api-base-url", default="http://localhost:8000", help="URL de base de l'API")
    parser.add_argument("--auth-token", help="Token d'authentification")
    
    args = parser.parse_args()
    
    success = launch_data_preview(
        data_source_id=args.data_source_id,
        api_base_url=args.api_base_url,
        auth_token=args.auth_token
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()