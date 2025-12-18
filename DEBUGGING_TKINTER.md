# Guide de Débogage pour l'Interface Tkinter

Ce guide vous aidera à déboguer et résoudre les problèmes liés à l'affichage de l'interface Tkinter lorsque vous cliquez sur le bouton "Voir" pour visualiser vos données.

## Contexte

L'interface Tkinter fonctionne correctement lorsque vous la lancez directement depuis le terminal, mais elle ne s'affiche pas lorsque vous la lancez depuis le backend. Cela suggère que le problème est lié à la manière dont le processus Tkinter est lancé depuis le backend, et non à un problème de configuration X11.

## Étapes de Débogage

### 1. Vérifiez les Logs du Backend

Lorsque vous cliquez sur le bouton "Voir", vérifiez les logs du backend pour voir si des erreurs spécifiques sont rapportées. Les logs devraient afficher des informations sur le lancement du processus Tkinter, y compris le PID du processus.

### 2. Vérifiez que le Processus est en Cours d'Exécution

Si le processus Tkinter est lancé avec succès, vous devriez pouvoir le voir dans la liste des processus en cours d'exécution. Utilisez la commande suivante pour vérifier:

```bash
ps aux | grep python
```

Recherchez un processus qui correspond au script `data_preview_tkinter.py`. Si le processus est en cours d'exécution mais que l'interface ne s'affiche pas, cela peut indiquer un problème avec l'environnement d'affichage.

### 3. Vérifiez les Variables d'Environnement

Assurez-vous que les variables d'environnement nécessaires sont correctement définies. Vous pouvez vérifier les variables d'environnement du processus backend en utilisant la commande suivante:

```bash
# Si vous utilisez Docker, exécutez la commande suivante pour entrer dans le conteneur
docker exec -it <nom_du_conteneur_backend> bash

# Une fois dans le conteneur, vérifiez les variables d'environnement
echo $DISPLAY
printenv
```

Assurez-vous que la variable `DISPLAY` est définie et qu'elle pointe vers le bon serveur X11.

### 4. Testez le Lancement Direct du Script

Essayez de lancer le script `data_preview_tkinter.py` directement depuis le terminal pour vérifier qu'il fonctionne correctement:

```bash
python data_preview_tkinter.py --data-source-id <ID> --api-base-url http://localhost:8000
```

Si le script fonctionne correctement lorsqu'il est lancé directement, cela confirme que le problème est lié à la manière dont le processus est lancé depuis le backend.

### 5. Vérifiez les Autorisations X11

Assurez-vous que les autorisations X11 sont correctement configurées pour permettre aux processus locaux de se connecter au serveur X11. Vous pouvez vérifier les autorisations en utilisant la commande suivante:

```bash
xhost
```

Si les autorisations ne sont pas configurées correctement, vous pouvez les autoriser en utilisant la commande suivante:

```bash
xhost +local:
```

### 6. Vérifiez les Logs du Processus Tkinter

Si le processus Tkinter est lancé mais que l'interface ne s'affiche pas, vous pouvez vérifier les logs du processus pour voir si des erreurs spécifiques sont rapportées. Vous pouvez rediriger les logs vers un fichier en modifiant le script `launch_data_preview.py` pour capturer la sortie standard et la sortie d'erreur.

### 7. Testez avec des Données de Test

Essayez de lancer l'interface Tkinter avec des données de test pour vérifier qu'elle fonctionne correctement. Vous pouvez utiliser le script `test_tkinter_direct.py` pour tester l'interface avec des données de test:

```bash
python test_tkinter_direct.py
```

Si l'interface s'affiche correctement avec des données de test, cela confirme que le problème est lié à la manière dont le processus est lancé depuis le backend.

## Solutions Possibles

### 1. Modifiez le Script de Lancement

Si le problème est lié à la manière dont le processus Tkinter est lancé depuis le backend, vous pouvez modifier le script `launch_data_preview.py` pour utiliser une approche différente. Par exemple, vous pouvez essayer de lancer le processus avec des options supplémentaires pour capturer les erreurs et les logs.

### 2. Utilisez un Autre Méthode de Lancement

Si le problème persiste, vous pouvez essayer d'utiliser une autre méthode pour lancer l'interface Tkinter. Par exemple, vous pouvez essayer de lancer le processus en utilisant un script shell ou un autre outil de gestion de processus.

### 3. Vérifiez les Dépendances

Assurez-vous que toutes les dépendances nécessaires sont installées et disponibles dans l'environnement où le processus Tkinter est lancé. Vous pouvez vérifier les dépendances en utilisant la commande suivante:

```bash
pip list
```

Assurez-vous que les packages nécessaires, tels que `tkinter`, `pandas`, et `requests`, sont installés et disponibles.

### 4. Testez avec un Autre Environnement

Si le problème persiste, vous pouvez essayer de tester l'interface Tkinter dans un autre environnement pour voir si le problème est spécifique à l'environnement actuel. Par exemple, vous pouvez essayer de lancer l'interface dans un environnement virtuel ou un conteneur Docker différent.

## Conclusion

En suivant ces étapes de débogage, vous devriez être en mesure d'identifier et de résoudre le problème lié à l'affichage de l'interface Tkinter lorsque vous la lancez depuis le backend. Si vous rencontrez toujours des problèmes, consultez les logs et les messages d'erreur pour obtenir des informations supplémentaires sur l'erreur.

Pour plus de détails, consultez le guide complet [X11_SETUP_GUIDE.md](X11_SETUP_GUIDE.md) et le guide de dépannage [TROUBLESHOOTING_TKINTER.md](TROUBLESHOOTING_TKINTER.md).
