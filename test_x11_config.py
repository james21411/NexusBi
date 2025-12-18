#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la configuration X11 et la capacité à lancer Tkinter.
"""

import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox

def test_x11_configuration():
    """Teste la configuration X11 et affiche les résultats."""
    print("🔍 Test de la configuration X11...")
    
    # Vérifier la variable DISPLAY
    display = os.environ.get('DISPLAY')
    print(f"🖥️ Variable DISPLAY: {display}")
    
    if not display:
        print("❌ Erreur: La variable DISPLAY n'est pas définie.")
        print("   Solution: Exportez la variable DISPLAY (ex: export DISPLAY=:0)")
        return False
    
    # Tester la connexion au serveur X11
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connexion au serveur X11 réussie.")
        else:
            print(f"❌ Erreur de connexion au serveur X11: {result.stderr}")
            print("   Solution: Assurez-vous que X11 est en cours d'exécution et accessible.")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test X11: {e}")
        print("   Solution: Installez les outils X11 (ex: xorg) et assurez-vous que X11 est en cours d'exécution.")
        return False
    
    # Tester la création d'une fenêtre Tkinter
    try:
        print("🔧 Test de la création d'une fenêtre Tkinter...")
        root = tk.Tk()
        root.title("Test X11")
        root.geometry("300x200")
        
        label = tk.Label(root, text="Test X11 réussi !", font=('Arial', 14))
        label.pack(pady=50)
        
        button = tk.Button(root, text="Fermer", command=root.destroy)
        button.pack()
        
        print("✅ Fenêtre Tkinter créée avec succès.")
        print("🎯 Si vous voyez une fenêtre avec le message 'Test X11 réussi !', la configuration est correcte.")
        
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la fenêtre Tkinter: {e}")
        print("   Solution: Vérifiez que X11 est correctement configuré et que la variable DISPLAY est accessible.")
        return False

def main():
    """Fonction principale."""
    print("🚀 Démarrage du test de configuration X11...")
    print("=" * 50)
    
    success = test_x11_configuration()
    
    print("=" * 50)
    if success:
        print("✅ Tous les tests ont réussi !")
        print("🎯 Votre configuration X11 est prête pour l'utilisation de Tkinter.")
    else:
        print("❌ Certains tests ont échoué.")
        print("📋 Veuillez consulter les messages d'erreur ci-dessus pour résoudre les problèmes.")
        print("📖 Consultez le guide X11_SETUP_GUIDE.md pour des instructions détaillées.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
