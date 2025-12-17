# Interface tkinter pour la Prévisualisation des Données

## Vue d'ensemble

Cette solution remplace la fenêtre modale React par une interface tkinter native pour la prévisualisation des données. L'interface tkinter offre une expérience plus stable et des fonctionnalités étendues pour visualiser et manipuler les données.

## Architecture

### Composants Principaux

1. **`data_preview_tkinter.py`** - Interface tkinter principale
2. **`launch_data_preview.py`** - Script de lancement 
3. **`backend/app/api/v1/endpoints/data_preview.py`** - API endpoints backend
4. **`frontend/src/components/DataSourcesView.tsx`** - Frontend React modifié

### Flux de Données

1. L'utilisateur clique sur "Voir" dans l'interface React
2. Le frontend envoie une requête POST à `/preview/launch-preview/{data_source_id}`
3. Le backend lance l'interface tkinter en arrière-plan
4. L'interface tkinter se connecte à l'API pour récupérer et afficher les données

## Fonctionnalités de l'Interface tkinter

### Affichage des Données
- Tableau scrollable avec en-têtes fixes
- Support des grandes datasets
- Colonnes redimensionnables
- Numérotation des lignes

### Contrôles d'Affichage
- **Mode d'affichage** : Premières lignes, Dernières lignes, Plage personnalisée
- **Nombre de lignes** : Contrôle flexible (1-1000 lignes)
- **Plage personnalisée** : Sélection par index de début/fin
- **Recherche** : Filtrage en temps réel dans toutes les colonnes
- **Sélection des colonnes** : 
  - Toutes les colonnes
  - 10 premières colonnes
  - Sélection manuelle via dialogue

### Fonctionnalités Avancées
- **Export CSV** : Export des données filtrées
- **Actualisation** : Rechargement des données depuis l'API
- **Titre dynamique** : Nom de la source et nombre total de lignes
- **Barre de statut** : Informations sur l'affichage actuel
- **Interface responsive** : S'adapte à la taille de l'écran

### Gestion des Erreurs
- Messages d'erreur explicites
- Gestion des timeouts
- Validation des données
- Fallback en cas d'échec de connexion

## Installation et Configuration

### Prérequis
```bash
# Installer les dépendances Python
pip install pandas requests

# Le module tkinter est généralement inclus avec Python
```

### Configuration Backend
1. Vérifiez que le backend FastAPI est en cours d'exécution
2. Assurez-vous que l'utilisateur est authentifié
3. L'API doit être accessible sur `http://localhost:8000`

### Configuration Frontend
Le frontend React est déjà configuré pour utiliser l'interface tkinter. Les modifications ont été apportées à :
- `DataSourcesView.tsx` - Remplacement de la modal React par l'appel API tkinter

## Utilisation

### Démarrage de l'Application

1. **Démarrer le backend** :
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Démarrer le frontend** :
   ```bash
   cd frontend
   npm run dev
   ```

3. **Tester l'interface tkinter** :
   ```bash
   python data_preview_tkinter.py --data-source-id 1 --api-base-url http://localhost:8000
   ```

### Utilisation de l'Interface

1. **Accéder aux sources de données** dans l'interface React
2. **Cliquer sur le bouton "Voir"** pour une source de données
3. **Attendre le lancement** de la fenêtre tkinter
4. **Utiliser les contrôles** pour naviguer dans les données
5. **Fermer la fenêtre** tkinter quand vous avez terminé

## API Endpoints

### `POST /preview/launch-preview/{data_source_id}`
Lance l'interface tkinter pour une source de données spécifique.

**Paramètres** :
- `data_source_id` (path) : ID de la source de données

**Réponse** :
```json
{
  "success": true,
  "message": "Interface de prévisualisation lancée avec succès",
  "data_source_id": 123,
  "process_id": 4567
}
```

### `GET /preview/preview-status/{data_source_id}`
Vérifie le statut de l'interface de prévisualisation.

**Réponse** :
```json
{
  "data_source_id": 123,
  "data_source_name": "Ma Source",
  "status": "available",
  "can_launch": true
}
```

### `POST /preview/close-preview/{data_source_id}`
Ferme l'interface de prévisualisation (si elle est encore ouverte).

## Configuration Avancée

### Variables d'Environnement
- `API_BASE_URL` : URL de base de l'API backend (défaut: `http://localhost:8000`)

### Paramètres de Lancement
L'interface tkinter peut être lancée avec les paramètres suivants :
- `--data-source-id` : ID de la source de données (requis)
- `--api-base-url` : URL de base de l'API (défaut: `http://localhost:8000`)
- `--auth-token` : Token d'authentification (optionnel)

### Exemple de Lancement Manuel
```bash
python launch_data_preview.py --data-source-id 1 --api-base-url http://localhost:8000 --auth-token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Dépannage

### Problèmes Courants

1. **La fenêtre tkinter ne s'ouvre pas**
   - Vérifiez que le backend fonctionne
   - Vérifiez les logs du backend
   - Assurez-vous que l'utilisateur est authentifié

2. **Erreur de connexion à l'API**
   - Vérifiez l'URL de l'API dans la configuration
   - Vérifiez que le token d'authentification est valide
   - Vérifiez les permissions de l'utilisateur

3. **Pas de données affichées**
   - Vérifiez que la source de données existe
   - Vérifiez que la source de données contient des données
   - Consultez les logs de l'interface tkinter

4. **L'interface est lente**
   - Réduisez le nombre de lignes affichées
   - Utilisez les filtres pour limiter les données
   - Vérifiez les performances du backend

### Logs et Débogage

Les logs sont affichés dans :
- Console du backend pour les erreurs API
- Console tkinter pour les erreurs d'interface
- Console du navigateur pour les erreurs frontend

## Développement et Extensions

### Ajouter de Nouvelles Fonctionnalités

1. **Nouvelles colonnes d'affichage** : Modifiez `visible_columns` dans `DataPreviewTkinter`
2. **Nouveaux filtres** : Ajoutez des contrôles dans la section `control_frame`
3. **Nouveaux formats d'export** : Étendez la fonction `export_csv`

### Personnalisation de l'Interface

- **Couleurs** : Modifiez les classes CSS dans l'interface
- **Police** : Changez `font` dans les widgets tkinter
- **Layout** : Modifiez la structure des frames

## Sécurité

- L'interface tkinter nécessite une authentification
- Les tokens d'authentification sont transmis de manière sécurisée
- Les données ne sont pas stockées localement
- Les connexions API utilisent HTTPS en production

## Support

Pour toute question ou problème :
1. Consultez les logs pour identifier l'erreur
2. Vérifiez la configuration des endpoints API
3. Testez avec des données d'exemple
4. Consultez la documentation de l'API backend