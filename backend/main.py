from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker  # Not used anymore
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
# Imports pour modèles (maintenus pour compatibilité future)
# from app.models.user import User
# from app.models.project import Project, DataSource
# from app.core.security import get_password_hash

# Créer le moteur de base de données
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Créer les tables si elles n'existent pas
print("🏗️  Vérification des tables de la base de données...")
Base.metadata.create_all(bind=engine)
print("✅ Tables vérifiées/créées")

# Base de données initialisée sans données de démonstration
print("✅ Base de données initialisée (sans données de démonstration)")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS - always enable for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "healthy"}