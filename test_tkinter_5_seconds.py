#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour vérifier que tkinter peut rester ouvert pendant 5 secondes
"""

import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime

def main():
    print("🧪 Test tkinter - Interface qui reste ouverte 5 secondes")
    print(f"⏰ Démarré à: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Créer la fenêtre
        root = tk.Tk()
        root.title("Test 5 secondes - tkinter")
        root.geometry("400x300")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Test tkinter", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Message
        message_label = ttk.Label(main_frame, text="Cette fenêtre devrait rester ouverte pendant 5 secondes")
        message_label.pack(pady=(0, 20))
        
        # Compteur
        counter_label = ttk.Label(main_frame, text="", font=("Arial", 14))
        counter_label.pack(pady=10)
        
        # Statut
        status_label = ttk.Label(main_frame, text="En cours...", foreground="blue")
        status_label.pack(pady=10)
        
        # Compteur en temps réel
        start_time = time.time()
        
        def update_counter():
            elapsed = time.time() - start_time
            remaining = max(0, 5 - elapsed)
            
            if remaining > 0:
                counter_label.config(text=f"Temps restant: {remaining:.1f} secondes")
                root.after(100, update_counter)
            else:
                counter_label.config(text="✅ 5 secondes écoulées!")
                status_label.config(text="Test terminé avec succès!", foreground="green")
                # Fermer automatiquement après 显示
                root.after(2000, root.destroy)  # Attendre 2 secondes puis fermer
        
        # Démarrer le compteur
        update_counter()
        
        # Mettre la fenêtre au premier plan
        root.lift()
        root.attributes('-topmost', True)
        
        print("✅ Interface tkinter créée")
        print("⏰ Cette fenêtre se fermera automatiquement après 5 secondes")
        print("🎯 Si vous voyez cette fenêtre, tkinter fonctionne correctement!")
        
        # Lancer la boucle principale
        root.mainloop()
        
        print(f"✅ Interface fermée à: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()