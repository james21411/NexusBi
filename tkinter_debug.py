#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic et de débogage pour l'interface tkinter
Ce script teste toutes les configurations possibles pour résoudre le problème d'affichage
"""

import subprocess
import sys
import os
import time
import platform
from pathlib import Path


def check_system_info():
    """Vérifie les informations système pour le débogage"""
    print("🔍 === DIAGNOSTIC SYSTÈME ===")
    print(f"💻 OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"👤 Utilisateur: {os.getenv('USER', 'inconnu')}")
    print(f"🏠 HOME: {os.getenv('HOME', 'inconnu')}")
    print(f"📁 Répertoire courant: {os.getcwd()}")
    
    # Vérifier la variable DISPLAY
    display = os.getenv('DISPLAY')
    print(f"🖥️ DISPLAY: {display if display else 'Non définie'}")
    
    # Vérifier les variables X11
    print(f"🔗 XAUTHORITY: {os.getenv('XAUTHORITY', 'Non définie')}")
    
    # Vérifier si X11 est installé
    try:
        result = subprocess.run(['which', 'xhost'], capture_output=True)
        print(f"🔧 X11 disponible: {'Oui' if result.returncode == 0 else 'Non'}")
    except:
        print("🔧 X11 disponible: Impossible de vérifier")
    
    print("=" * 50)


def test_x11_connection():
    """Test de connexion X11"""
    print("\n🧪 === TEST X11 ===")
    
    # Test 1: Vérifier DISPLAY
    display = os.getenv('DISPLAY')
    if not display:
        print("❌ Variable DISPLAY non définie")
        return False
    
    print(f"✅ Variable DISPLAY définie: {display}")
    
    # Test 2: Vérifier xset
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Serveur X11 accessible")
            return True
        else:
            print(f"❌ Erreur xset: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Commande xset non trouvée")
        return False
    except Exception as e:
        print(f"❌ Erreur test X11: {e}")
        return False


def test_tkinter_basic():
    """Test basique de tkinter"""
    print("\n🧪 === TEST TKINTER ===")
    
    try:
        import tkinter as tk
        print("✅ Module tkinter importé")
        
        # Test création fenêtre
        root = tk.Tk()
        root.title("Test tkinter")
        root.geometry("300x200")
        
        # Ajouter un label
        label = tk.Label(root, text="Test de fonctionnement tkinter", font=("Arial", 12))
        label.pack(pady=20)
        
        # Ajouter un bouton de fermeture
        def close():
            root.quit()
            root.destroy()
        
        button = tk.Button(root, text="Fermer", command=close, bg="red", fg="white")
        button.pack(pady=10)
        
        print("✅ Fenêtre tkinter créée")
        print("🖼️ Si vous voyez cette fenêtre, tkinter fonctionne !")
        print("⏰ Fermeture automatique dans 3 secondes...")
        
        # Fermeture automatique après 3 secondes
        root.after(3000, close)
        root.mainloop()
        
        print("✅ Test tkinter réussi")
        return True
        
    except Exception as e:
        print(f"❌ Erreur tkinter: {e}")
        return False


def test_display_configurations():
    """Test différentes configurations d'affichage"""
    print("\n🧪 === TEST CONFIGURATIONS DISPLAY ===")
    
    configurations = [
        {"DISPLAY": ":0", "description": "Display local standard"},
        {"DISPLAY": ":1", "description": "Display virtuel 1"},
        {"DISPLAY": os.getenv('DISPLAY', ''), "description": "Display actuel"},
    ]
    
    for config in configurations:
        if not config["DISPLAY"]:
            continue
            
        print(f"\n🔧 Test configuration: {config['description']} ({config['DISPLAY']})")
        
        env = os.environ.copy()
        env.update(config)
        
        try:
            # Test simple avec xset
            result = subprocess.run(['xset', 'q'], capture_output=True, text=True, env=env)
            if result.returncode == 0:
                print(f"✅ Configuration {config['DISPLAY']} fonctionne")
            else:
                print(f"❌ Configuration {config['DISPLAY']} échoue: {result.stderr}")
        except Exception as e:
            print(f"❌ Erreur test {config['DISPLAY']}: {e}")


def fix_display_issues():
    """Propose des solutions pour les problèmes d'affichage"""
    print("\n🔧 === SOLUTIONS PROPOSÉES ===")
    
    display = os.getenv('DISPLAY')
    
    if not display:
        print("💡 Solution 1: Définir la variable DISPLAY")
        print("   Exécutez: export DISPLAY=:0")
        print("   Ou: export DISPLAY=:1")
        
        # Proposer de la définir automatiquement
        print("\n🔄 Tentative de définition automatique...")
        os.environ['DISPLAY'] = ':0'
        print("✅ DISPLAY défini à :0")
    
    print("\n💡 Solution 2: Autoriser les connexions X11")
    print("   Exécutez: xhost +local:")
    
    # Proposer de l'exécuter automatiquement
    try:
        result = subprocess.run(['xhost', '+local:'], capture_output=True)
        if result.returncode == 0:
            print("✅ Autorisations X11 accordées")
        else:
            print(f"⚠️ Impossible d'accorder les autorisations X11: {result.stderr}")
    except FileNotFoundError:
        print("⚠️ Commande xhost non trouvée")
    
    print("\n💡 Solution 3: Vérifier que le serveur X11 est démarré")
    print("   Sur Ubuntu/Debian: sudo systemctl start gdm3")
    print("   Sur CentOS/RHEL: sudo systemctl start gdm")
    print("   Ou: sudo systemctl start lightdm")


def launch_improved_tkinter():
    """Lance une version améliorée de tkinter avec plus de diagnostics"""
    print("\n🚀 === LANCEMENT TKINTER AMÉLIORÉ ===")
    
    # Créer un script tkinter temporaire avec diagnostics
    script_content = '''#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import os
import sys

def main():
    print("🚀 Interface tkinter améliorée")
    print(f"🖥️ DISPLAY: {os.getenv('DISPLAY', 'Non définie')}")
    print(f"👤 Utilisateur: {os.getenv('USER', 'inconnu')}")
    
    try:
        root = tk.Tk()
        root.title("Interface tkinter - Mode diagnostic")
        root.geometry("500x400")
        
        # Message d'information
        info_text = f"""
Interface tkinter fonctionnelle !

Configuration:
- DISPLAY: {os.getenv('DISPLAY', 'Non définie')}
- Utilisateur: {os.getenv('USER', 'inconnu')}
- Répertoire: {os.getcwd()}

Si vous voyez cette fenêtre, le problème n'est pas dans tkinter.
Le problème vient probablement du processus parent.
        """
        
        label = tk.Label(root, text=info_text, justify=tk.LEFT, font=("Courier", 10))
        label.pack(pady=10, padx=10)
        
        # Bouton de test
        def test_click():
            messagebox.showinfo("Test", "Le clic fonctionne !")
        
        button = tk.Button(root, text="Test de clic", command=test_click, bg="green", fg="white")
        button.pack(pady=10)
        
        # Bouton de fermeture
        def close():
            print("🪟 Fermeture de l'interface")
            root.quit()
            root.destroy()
        
        button_close = tk.Button(root, text="Fermer", command=close, bg="red", fg="white")
        button_close.pack(pady=10)
        
        print("✅ Interface créée, prêt pour interaction")
        
        # Garder la fenêtre ouverte
        root.mainloop()
        print("✅ Interface fermée proprement")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    # Écrire le script temporaire
    temp_script = Path("temp_tkinter_test.py")
    temp_script.write_text(script_content)
    
    try:
        print("📝 Script temporaire créé")
        
        # Lancer le script
        env = os.environ.copy()
        process = subprocess.Popen(
            [sys.executable, str(temp_script)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"🔄 Processus lancé avec PID: {process.pid}")
        
        # Attendre un peu
        time.sleep(2)
        
        # Vérifier si le processus est encore en cours
        if process.poll() is None:
            print("✅ Processus en cours d'exécution")
            print("🎯 Regardez si une fenêtre tkinter est apparue !")
            print("⏰ Attente de la fermeture du processus...")
            
            # Attendre la fin du processus
            stdout, stderr = process.communicate(timeout=10)
            
            print("📤 STDOUT:")
            print(stdout)
            if stderr:
                print("❌ STDERR:")
                print(stderr)
        else:
            stdout, stderr = process.communicate()
            print("❌ Le processus s'est arrêté immédiatement")
            print("📤 STDOUT:")
            print(stdout)
            if stderr:
                print("❌ STDERR:")
                print(stderr)
    
    finally:
        # Nettoyer le fichier temporaire
        if temp_script.exists():
            temp_script.unlink()
            print("🧹 Fichier temporaire supprimé")


def main():
    """Fonction principale de diagnostic"""
    print("🔍 === DIAGNOSTIC TKINTER ===")
    print("Ce script va diagnostiquer et tenter de résoudre les problèmes d'affichage tkinter")
    
    # 1. Informations système
    check_system_info()
    
    # 2. Test X11
    x11_working = test_x11_connection()
    
    # 3. Test tkinter basique
    tkinter_working = test_tkinter_basic()
    
    # 4. Test configurations display
    test_display_configurations()
    
    # 5. Proposer des solutions
    fix_display_issues()
    
    # 6. Lancer une interface améliorée
    launch_improved_tkinter()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSTIC TERMINÉ")
    print("\n💡 CONSEILS:")
    print("1. Si vous avez vu une fenêtre tkinter, le problème vient du processus parent")
    print("2. Si aucune fenêtre n'apparaît, il y a un problème X11/DISPLAY")
    print("3. Exécutez 'python test_tkinter_demo.py' pour tester l'interface complète")
    print("4. Vérifiez que le backend est bien configuré pour lancer tkinter")


if __name__ == "__main__":
    main()