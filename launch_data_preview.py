#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement pour l'interface tkinter de prévisualisation des données
Version améliorée avec gestion des erreurs X11 et diagnostics
"""

import subprocess
import sys
import os
import json
import argparse
import time
from pathlib import Path


def check_x11_environment():
    """Vérifie et configure l'environnement X11"""
    print("🔍 Vérification de l'environnement X11...")
    
    # Vérifier si DISPLAY est définie
    display = os.getenv('DISPLAY')
    if not display:
        print("⚠️ Variable DISPLAY non définie - tentative de configuration...")
        os.environ['DISPLAY'] = ':0'
        print(f"✅ DISPLAY défini à: {os.getenv('DISPLAY')}")
    else:
        print(f"✅ DISPLAY définie: {display}")
    
    # Vérifier xhost
    try:
        result = subprocess.run(['xhost'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ xhost disponible")
        else:
            print("⚠️ xhost non disponible")
    except FileNotFoundError:
        print("⚠️ xhost non installé")
    
    # Autoriser les connexions locales
    try:
        result = subprocess.run(['xhost', '+local:'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Autorisations X11 accordées (xhost +local:)")
        else:
            print(f"⚠️ Impossible d'accorder les autorisations X11: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Erreur lors de l'accord des autorisations X11: {e}")
    
    # Test de connexion X11
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Serveur X11 accessible")
            return True
        else:
            print(f"❌ Serveur X11 inaccessible: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ xset non trouvé - X11 probablement non installé")
        return False
    except Exception as e:
        print(f"❌ Erreur test X11: {e}")
        return False


def create_diagnostic_script(data_source_id, api_base_url, auth_token):
    """Crée un script de diagnostic temporaire"""
    script_content = f'''#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import json
import requests
from datetime import datetime

def main():
    print("🚀 Interface tkinter de diagnostic")
    print(f"🕐 Démarré à: {{datetime.now()}}")
    print(f"🖥️ DISPLAY: {{os.getenv('DISPLAY', 'Non définie')}}")
    print(f"👤 Utilisateur: {{os.getenv('USER', 'inconnu')}}")
    print(f"📊 Data source ID: {data_source_id}")
    print(f"🌐 API URL: {api_base_url}")
    
    try:
        root = tk.Tk()
        root.title("Diagnostic tkinter - NexusBi")
        root.geometry("600x500")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informations système
        info_text = f"""
🖥️ CONFIGURATION SYSTÈME:
   - DISPLAY: {{os.getenv('DISPLAY', 'Non définie')}}
   - Utilisateur: {{os.getenv('USER', 'inconnu')}}
   - Répertoire: {{os.getcwd()}}
   - Python: {{sys.version.split()[0]}}

📊 CONFIGURATION APPLICATION:
   - Data Source ID: {data_source_id}
   - API Base URL: {api_base_url}
   - Auth Token: {{'***' if "{auth_token}" else 'Aucun'}}

🕐 Démarré: {{datetime.now().strftime("%H:%M:%S")}}
        """
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, font=("Courier", 9))
        info_label.pack(pady=10, anchor=tk.W)
        
        # Zone de statut
        status_frame = ttk.LabelFrame(main_frame, text="Statut", padding="5")
        status_frame.pack(fill=tk.X, pady=10)
        
        status_label = ttk.Label(status_frame, text="Interface initialisée", foreground="green")
        status_label.pack()
        
        # Zone de logs
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Text widget pour les logs
        log_text = tk.Text(log_frame, height=10, font=("Courier", 8))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def log(message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_text.insert(tk.END, f"[{{timestamp}}] {{message}}\\n")
            log_text.see(tk.END)
            print(f"[{{timestamp}}] {{message}}")
        
        # Test de connexion API
        def test_api_connection():
            try:
                log("🌐 Test de connexion API...")
                response = requests.get(f"{{api_base_url}}/api/v1/preview/preview-data/{data_source_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    log(f"✅ API accessible: {{len(result.get('rows', []))}} lignes chargées")
                    status_label.config(text="API accessible", foreground="green")
                else:
                    log(f"❌ Erreur API: {{response.status_code}}")
                    status_label.config(text=f"Erreur API: {{response.status_code}}", foreground="red")
            except Exception as e:
                log(f"❌ Erreur connexion API: {{e}}")
                status_label.config(text="Erreur connexion API", foreground="red")
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Tester API", command=test_api_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualiser", command=lambda: log("🔄 Actualisation manuelle")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Fermer", command=root.destroy, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Test automatique au démarrage
        root.after(1000, test_api_connection)
        
        log("✅ Interface tkinter créée avec succès")
        log("🎯 Cette interface devrait être visible maintenant")
        
        print("🖼️ Interface tkinter démarrée - Vérifiez qu'elle est visible")
        
        root.mainloop()
        log("🪟 Interface fermée proprement")
        
    except Exception as e:
        error_msg = f"❌ Erreur création interface: {{e}}"
        print(error_msg)
        log(error_msg)
        import traceback
        traceback.print_exc()
        log(traceback.format_exc())

if __name__ == "__main__":
    main()
'''
    
    temp_script = Path("temp_tkinter_diagnostic.py")
    temp_script.write_text(script_content)
    return temp_script


def launch_data_preview(data_source_id: int, api_base_url: str = "http://localhost:8000", auth_token: str = None):
    """
    Lance l'interface tkinter de prévisualisation des données avec diagnostics améliorés
    
    Args:
        data_source_id: ID de la source de données à afficher
        api_base_url: URL de base de l'API backend
        auth_token: Token d'authentification (optionnel)
    """
    print("🚀 Lancement de launch_data_preview (version améliorée)")
    print(f"📋 Paramètres reçus:")
    print(f"   - data_source_id: {data_source_id}")
    print(f"   - api_base_url: {api_base_url}")
    print(f"   - auth_token: {'***' if auth_token else None}")
    
    try:
        # Vérifier l'environnement X11
        x11_working = check_x11_environment()
        
        if not x11_working:
            print("⚠️ ATTENTION: X11 ne semble pas accessible")
            print("💡 L'interface peut ne pas s'afficher")
            print("🔧 Suggestions:")
            print("   1. Vérifiez que vous êtes dans un environnement graphique")
            print("   2. Exécutez: export DISPLAY=:0")
            print("   3. Exécutez: xhost +local:")
            print("   4. Sur serveur: utilisez un redirecteur X11 comme Xming ou VcXsrv")
        
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
            
            # Créer et lancer le script de diagnostic à la place
            print("🛠️ Création du script de diagnostic...")
            diagnostic_script = create_diagnostic_script(data_source_id, api_base_url, auth_token)
            script_to_run = diagnostic_script
        else:
            print(f"✅ Script tkinter trouvé: {tkinter_script}")
            script_to_run = tkinter_script
        
        # Préparer les arguments
        args = [sys.executable, str(script_to_run)]
        if data_source_id:
            args.extend(["--data-source-id", str(data_source_id)])
        if api_base_url:
            # Use the API base URL as-is, let tkinter handle the /api/v1/ prefix
            args.extend(["--api-base-url", api_base_url])
        if auth_token:
            args.extend(["--auth-token", auth_token])
        
        print(f"⚙️ Arguments de commande: {args}")
        
        # Créer un environnement amélioré
        env = os.environ.copy()
        
        # Variables de débogage
        env['TKINTER_DEBUG'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        
        # Assurer que DISPLAY est définie
        if 'DISPLAY' not in env:
            env['DISPLAY'] = ':0'
        
        print(f"🖥️ Configuration finale DISPLAY: {env.get('DISPLAY')}")
        
        # Afficher les informations de débogage
        print("🔍 Informations de débogage:")
        print(f"   - Répertoire de travail: {os.getcwd()}")
        print(f"   - Utilisateur: {os.getenv('USER', 'inconnu')}")
        print(f"   - HOME: {os.getenv('HOME', 'inconnu')}")
        print(f"   - PATH: {os.getenv('PATH', 'inconnu')}")
        
        # Définir le répertoire de travail sur le répertoire courant
        cwd = str(current_dir)
        print(f"📁 Répertoire de travail: {cwd}")
        
        print("🔧 Lancement du processus...")
        
        # Lancer le processus avec gestion améliorée des erreurs
        try:
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd,
                preexec_fn=os.setsid  # Créer un nouveau groupe de processus
            )
            
            print(f"✅ Processus lancé avec PID: {process.pid}")
            
            # Attendre un peu pour voir si le processus démarre correctement
            print("⏳ Attente du démarrage du processus...")
            time.sleep(3)
            
            # Vérifier si le processus est toujours en cours d'exécution
            if process.poll() is None:
                print("✅ Interface de prévisualisation lancée avec succès")
                print(f"🔍 PID du processus: {process.pid}")
                print("🎯 Le processus continue en arrière-plan")
                
                # Nettoyer le script temporaire s'il existe
                if script_to_run.name == "temp_tkinter_diagnostic.py" and script_to_run.exists():
                    print("🧹 Nettoyage du script de diagnostic...")
                    # On laisse le script vivre un peu plus longtemps pour les tests
                    # script_to_run.unlink()
                
                return True
            else:
                # Le processus s'est arrêté - récupérer les erreurs
                stdout, stderr = process.communicate()
                if stdout:
                    print(f"📤 STDOUT:\n{stdout.decode()}")
                if stderr:
                    print(f"❌ STDERR:\n{stderr.decode()}")
                print(f"❌ Erreur lors du lancement - Code de retour: {process.returncode}")
                
                print("🔧 Suggestions de dépannage:")
                print("   1. Vérifiez que X11 est installé et en cours d'exécution")
                print("   2. Exécutez 'python tkinter_debug.py' pour un diagnostic complet")
                print("   3. Essayez de lancer le script directement depuis le terminal")
                print("   4. Vérifiez les permissions des fichiers")
                
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du lancement du processus: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'interface tkinter: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Fonction principale pour utilisation en ligne de commande"""
    parser = argparse.ArgumentParser(description="Lance l'interface tkinter de prévisualisation des données (version améliorée)")
    parser.add_argument("--data-source-id", type=int, required=True, help="ID de la source de données")
    parser.add_argument("--api-base-url", default="http://localhost:8000", help="URL de base de l'API")
    parser.add_argument("--auth-token", help="Token d'authentification")
    
    args = parser.parse_args()
    
    success = launch_data_preview(
        data_source_id=args.data_source_id,
        api_base_url=args.api_base_url,
        auth_token=args.auth_token
    )
    
    if success:
        print("🎉 Lancement réussi !")
        print("💡 Si l'interface ne s'affiche pas, exécutez: python tkinter_debug.py")
    else:
        print("💥 Échec du lancement")
        print("💡 Exécutez: python tkinter_debug.py pour diagnostiquer le problème")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()