# NexusBi - Plateforme d'Analyse de Données Alimentée par IA

NexusBi est une plateforme web moderne qui comble le fossé entre les utilisateurs non-techniques et leurs données grâce au traitement du langage naturel et à l'analyse alimentée par l'IA.

## 🎯 Vision

Transformer l'analyse de données complexe en conversations simples. Au lieu de lutter avec les formules Excel ou les requêtes SQL, les utilisateurs peuvent simplement poser des questions comme :

> "Montre-moi la tendance des ventes du dernier trimestre"
> "Trouve les clients qui n'ont pas acheté depuis 6 mois"
> "Compare les revenus par région et catégorie de produit"

## 🏗️ Architecture

NexusBi suit une architecture micro-services avec :

- **Frontend** : React + TypeScript + TailwindCSS
- **API Gateway** : FastAPI (Python)
- **Workers** : Celery pour le traitement asynchrone
- **Base de données** : PostgreSQL
- **Cache/Broker** : Redis
- **IA** : Intégration OpenAI GPT

### Schéma d'Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Celery        │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Workers       │
│                 │    │                 │    │   (Pandas)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   OpenAI API    │
│   (App Data)    │    │   (Broker)      │    │   (LLM)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose
- Node.js 18+ (pour le développement frontend local)
- Python 3.11+ (pour le développement backend local)

### Installation des Dépendances

#### Méthode 1 : Docker (Recommandée)
```bash
# Cloner le dépôt
git clone <repository-url>
cd nexusbi

# Lancer tous les services avec Docker
cd docker
docker-compose up --build
```

#### Méthode 2 : Installation Locale

**Backend (Python) :**
```bash
cd backend

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou sur Windows :
# venv\Scripts\activate

# Installer les dépendances Python
pip install -r requirements.txt

# Vérifier l'installation
python -c "import numpy, matplotlib, plotly, seaborn, pandas, fastapi; print('✅ Toutes les dépendances sont installées !')"
```

**Frontend (Node.js) :**
```bash
cd frontend

# Installer les dépendances Node.js
npm install

# Lancer le serveur de développement
npm run dev
```

### Accès à l'Application

- **Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 📁 Structure du Projet

```
nexusbi/
├── frontend/           # Application React
├── backend/            # Application FastAPI
│   ├── app/
│   │   ├── api/        # Points de terminaison API
│   │   ├── core/       # Configuration & sécurité
│   │   ├── db/         # Modèles de base de données & session
│   │   ├── models/     # Modèles SQLAlchemy
│   │   ├── schemas/    # Schémas Pydantic
│   │   ├── services/   # Logique métier
│   │   └── utils/      # Utilitaires
│   ├── requirements.txt
│   └── Dockerfile
├── docker/             # Configuration Docker
├── docs/               # Documentation
└── README.md
```

## 🔑 Fonctionnalités Clés

### Intégration des Sources de Données
- Téléchargement de fichiers CSV/Excel
- Connexions aux bases de données (MySQL, PostgreSQL)
- Traitement des dumps SQL avec Docker-in-Docker
- Détection et analyse de schéma

### Analyse Alimentée par IA
- Traitement des requêtes en langage naturel
- Génération automatique de code (Pandas/SQL)
- Suggestions intelligentes de nettoyage de données
- Recommandations de visualisation intelligentes

### Sécurité & Performance
- Authentification basée sur JWT
- Isolation des données par utilisateur/projet
- Traitement asynchrone pour les gros volumes
- Connexions chiffrées aux bases de données

## 🛠️ Pile Technologique

### Backend
- **FastAPI** : Framework web asynchrone haute performance
- **SQLAlchemy** : ORM pour les opérations de base de données
- **Celery** : File d'attente de tâches distribuée
- **Pandas** : Manipulation et analyse de données
- **OpenAI** : Intégration IA/LLM

### Frontend
- **React 18** : Framework UI
- **TypeScript** : Sécurité des types
- **TailwindCSS** : Styling utility-first
- **Recharts** : Visualisation de données
- **React Hook Form** : Gestion des formulaires

### Infrastructure
- **PostgreSQL** : Base de données principale
- **Redis** : Cache et broker de messages
- **Docker** : Conteneurisation
- **Nginx** : Équilibrage de charge (futur)

## 👥 Organisation de l'Équipe

Ce projet est conçu pour une équipe de développement de 4 personnes :

1. **Lead & Architecte Backend** : API Gateway, Sécurité, Base de données
2. **Frontend & UI/UX** : Interface React, Expérience utilisateur
3. **Ingénieur Data & IA** : Logique Pandas, Intégration IA
4. **DevOps & Fullstack** : Docker, CI/CD, Tests

### Workflow de Développement
- **Git Flow** : Branches de fonctionnalités, revues PR
- **Scrum** : Sprints de 2 semaines, daily standups
- **Qualité du Code** : Type hints, tests, documentation

## 📈 Feuille de Route

### Phase 1 (Actuelle)
- [x] Configuration architecture de base
- [x] Système d'authentification
- [x] Pattern factory pour les sources de données
- [x] Configuration Docker
- [ ] Intégration frontend-backend

### Phase 2
- [ ] Implémentation de l'assistant IA
- [ ] Système de téléchargement de fichiers
- [ ] Visualisation de données
- [ ] Traitement des dumps SQL

### Phase 3
- [ ] Analyses avancées
- [ ] Architecture multi-tenant
- [ ] Optimisation des performances
- [ ] Déploiement en production

## 🔒 Sécurité

- Isolation des données utilisateur
- Identifiants de base de données chiffrés
- Authentification par token JWT
- Validation et assainissement des entrées
- Sécurité des conteneurs Docker

## 📚 Documentation

- [Documentation API](http://localhost:8000/docs) (lorsque lancée)
- [Guide Frontend](./frontend/README.md)
- [Architecture Backend](./docs/architecture.md)
- [Guide de Déploiement](./docs/deployment.md)

## 🤝 Contribution

1. Suivre le Git Flow établi
2. Écrire des tests pour les nouvelles fonctionnalités
3. Mettre à jour la documentation
4. Assurer les standards de qualité du code

## 📄 Licence

Ce projet est un logiciel propriétaire développé pour NexusBi.

---

**Développé avec ❤️ par l'équipe NexusBi**# NexusBi
# NexusBI
