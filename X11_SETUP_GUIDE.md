# Guide de Configuration X11 pour Tkinter

Ce guide vous aidera à configurer X11 forwarding pour permettre à l'interface Tkinter de s'afficher correctement, en particulier dans un environnement Docker.

## Problème

L'interface Tkinter ne s'affiche pas lorsque vous cliquez sur le bouton "Voir" pour visualiser vos données. Cela est généralement dû à l'absence de la variable d'environnement `DISPLAY` ou à une configuration incorrecte de X11, en particulier dans les environnements Docker.

## Solution

### 1. Configuration de X11 sur votre machine locale

#### Sur Linux:

1. **Installez X11** si ce n'est pas déjà fait:
   ```bash
   sudo apt-get update
   sudo apt-get install xorg openbox
   ```

2. **Autorisez les connexions X11** depuis votre machine locale:
   ```bash
   xhost +local:
   ```

#### Sur macOS:

1. **Installez XQuartz** (si ce n'est pas déjà fait):
   - Téléchargez et installez XQuartz depuis [https://www.xquartz.org/](https://www.xquartz.org/)

2. **Ouvrez XQuartz** et allez dans les préférences:
   - Allez dans l'onglet "Sécurité"
   - Cochez "Autoriser les connexions depuis les clients réseau"

3. **Redémarrez XQuartz** pour appliquer les changements.

#### Sur Windows:

1. **Installez un serveur X11** comme VcXsrv ou Xming.
2. **Lancez le serveur X11** et assurez-vous qu'il est en cours d'exécution.

### 2. Configuration de Docker pour X11 Forwarding

#### Pour Docker sur Linux/macOS:

1. **Ajoutez les options suivantes** à votre commande `docker run`:
   ```bash
   docker run -it \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix \
     --name votre_conteneur \
     votre_image
   ```

2. **Si vous utilisez Docker Compose**, ajoutez les options suivantes à votre service:
   ```yaml
   services:
     votre_service:
       environment:
         - DISPLAY=${DISPLAY}
       volumes:
         - /tmp/.X11-unix:/tmp/.X11-unix
   ```

#### Pour Docker sur Windows:

1. **Déterminez l'adresse IP** de votre machine hôte (ex: `192.168.1.100`).
2. **Ajoutez les options suivantes** à votre commande `docker run`:
   ```bash
   docker run -it \
     -e DISPLAY=192.168.1.100:0.0 \
     --name votre_conteneur \
     votre_image
   ```

### 3. Vérification de la Configuration

1. **Vérifiez que la variable `DISPLAY` est définie** dans votre conteneur:
   ```bash
   echo $DISPLAY
   ```
   Cela devrait afficher quelque chose comme `:0` ou `localhost:10.0`.

2. **Testez X11** en exécutant une commande simple comme `xclock`:
   ```bash
   xclock
   ```
   Si une horloge s'affiche, X11 est correctement configuré.

### 4. Redémarrage des Services

1. **Redémarrez votre conteneur Docker** pour appliquer les changements:
   ```bash
   docker restart votre_conteneur
   ```

2. **Redémarrez votre application** et essayez à nouveau de visualiser les données.

## Dépannage

### Problème: `Error: Can't open display`

**Solution:**
- Assurez-vous que X11 est en cours d'exécution sur votre machine hôte.
- Vérifiez que la variable `DISPLAY` est correctement définie dans le conteneur.
- Assurez-vous que le volume `/tmp/.X11-unix` est correctement monté.

### Problème: `xhost: unable to open display`

**Solution:**
- Assurez-vous que X11 est installé et en cours d'exécution.
- Essayez de redémarrer le serveur X11.

### Problème: L'interface Tkinter ne s'affiche toujours pas

**Solution:**
- Vérifiez les logs de votre application pour voir si des erreurs spécifiques sont rapportées.
- Assurez-vous que le conteneur Docker a accès au serveur X11 de l'hôte.
- Essayez de lancer une application X11 simple comme `xclock` pour vérifier la configuration.

## Conclusion

En suivant ces étapes, vous devriez être en mesure de configurer X11 forwarding pour Docker et permettre à l'interface Tkinter de s'afficher correctement. Si vous rencontrez toujours des problèmes, consultez les logs de votre application pour obtenir des informations supplémentaires sur l'erreur.
