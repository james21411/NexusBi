# Guide d'Installation - NexusBi

## 🎯 Vue d'ensemble

Ce guide explique comment installer et configurer NexusBi sur votre machine pour le développement.

## 📋 Prérequis Système

### Logiciels Requis
- **Python 3.11 ou 3.12** (⚠️ Python 3.13 peut causer des problèmes de compatibilité)
- **Node.js 18+**
- **Docker & Docker Compose** (recommandé)
- **Git**

### Vérification des Versions
```bash
# Vérifier Python
python --version  # Doit être 3.11.x ou 3.12.x

# Vérifier Node.js
node --version   # Doit être ≥ 18.0.0

# Vérifier Docker
docker --version
docker-compose --version
```

## 🚀 Installation Rapide (Docker - Recommandé)

### 1. Cloner le Projet
```bash
git clone <repository-url>
cd nexusbi
```

### 2. Configuration des Variables d'Environnement
```bash
# Copier le fichier d'exemple
cp backend/.env.example backend/.env

# Éditer les variables si nécessaire
nano backend/.env  # ou code backend/.env
```

### 3. Lancer avec Docker
```bash
cd docker
docker-compose up --build
```

### 4. Accéder à l'Application
- **Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 🐍 Installation Manuelle (Backend)

### 1. Préparer l'Environnement Python
```bash
cd backend

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 2. Installer les Dépendances
```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de la Base de Données
```bash
# Créer un fichier .env
cp .env.example .env

# Modifier les variables selon votre configuration
# Par défaut, utilise PostgreSQL en Docker
```

### 4. Initialiser la Base de Données
```bash
# Créer les tables (avec Alembic si configuré)
# Ou utiliser directement SQLAlchemy
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 5. Lancer le Serveur Backend
```bash
# Avec rechargement automatique (développement)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou en production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## ⚛️ Installation Frontend

### 1. Installer les Dépendances Node.js
```bash
cd frontend

# Installer les dépendances
npm install
```

### 2. Configuration
```bash
# Créer un fichier .env.local si nécessaire
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
```

### 3. Lancer le Serveur de Développement
```bash
npm run dev
```

## 🔧 Dépannage

### Problème : Erreur avec pandas/numpy
```
Solution : Utiliser Python 3.11 ou 3.12 au lieu de 3.13
```

### Problème : Port déjà utilisé
```bash
# Trouver le processus
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Tuer le processus
kill -9 <PID>
```

### Problème : Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est lancé
docker ps | grep postgres

# Ou utiliser SQLite pour les tests
# Modifier .env : SQLALCHEMY_DATABASE_URI=sqlite:///./nexusbi.db
```

### Problème : Dépendances manquantes
```bash
# Recréer l'environnement virtuel
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🧪 Tests

### Tests Backend
```bash
cd backend
pytest
```

### Tests Frontend
```bash
cd frontend
npm test
```

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez que tous les prérequis sont installés
2. Utilisez Docker (plus simple)
3. Consultez les logs : `docker-compose logs`
4. Vérifiez la documentation API : http://localhost:8000/docs

## 🎉 Vérification Finale

Testez que tout fonctionne :

```bash
# Backend
curl http://localhost:8000/health

# Frontend (dans le navigateur)
open http://localhost:3000
```

**Bonne installation ! 🚀**