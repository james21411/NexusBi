from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core.deps import get_current_active_user, get_db
from app.core.security import get_random_string

router = APIRouter()

class UserAPIKeyCreate(BaseModel):
    key_name: str
    key_type: str = "gemini"
    api_key_value: str

class UserAPIKeyResponse(BaseModel):
    id: int
    key_name: str
    key_type: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    usage_count: int

class ChatbotConfig(BaseModel):
    selected_model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1024
    language: str = "fr"

class ChatbotResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int
    suggestions: List[str]

@router.post("/api-keys/create", response_model=UserAPIKeyResponse)
def create_user_api_key(
    *,
    db: Session = Depends(get_db),
    key_data: UserAPIKeyCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Créer une nouvelle clé API pour l'utilisateur.
    """
    try:
        # Créer la clé API
        db_api_key = models.APIKey(
            user_id=current_user.id,
            key_name=key_data.key_name,
            key_value=key_data.api_key_value,
            key_type=key_data.key_type,
            is_active=True,
            usage_count=0
        )

        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)

        return {
            "id": db_api_key.id,
            "key_name": db_api_key.key_name,
            "key_type": db_api_key.key_type,
            "is_active": db_api_key.is_active,
            "created_at": db_api_key.created_at,
            "last_used_at": db_api_key.last_used_at,
            "usage_count": db_api_key.usage_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la clé API: {str(e)}"
        )

@router.get("/api-keys/list", response_model=List[UserAPIKeyResponse])
def list_user_api_keys(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Lister toutes les clés API de l'utilisateur.
    """
    try:
        api_keys = db.query(models.APIKey).filter(
            models.APIKey.user_id == current_user.id
        ).all()

        return [{
            "id": key.id,
            "key_name": key.key_name,
            "key_type": key.key_type,
            "is_active": key.is_active,
            "created_at": key.created_at,
            "last_used_at": key.last_used_at,
            "usage_count": key.usage_count
        } for key in api_keys]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la liste des clés API: {str(e)}"
        )

@router.post("/chatbot/config", response_model=dict)
def update_chatbot_config(
    *,
    db: Session = Depends(get_db),
    config: ChatbotConfig,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Mettre à jour la configuration du chatbot.
    """
    try:
        # Mettre à jour les paramètres utilisateur
        user_settings = db.query(models.UserSettings).filter(
            models.UserSettings.user_id == current_user.id
        ).first()

        if not user_settings:
            user_settings = models.UserSettings(
                user_id=current_user.id,
                preferred_ai_model=config.selected_model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                theme="dark",
                language=config.language,
                notifications_enabled=True
            )
            db.add(user_settings)
        else:
            user_settings.preferred_ai_model = config.selected_model
            user_settings.temperature = config.temperature
            user_settings.max_tokens = config.max_tokens
            user_settings.language = config.language

        db.commit()
        db.refresh(user_settings)

        return {
            "status": "success",
            "message": "Configuration du chatbot mise à jour avec succès",
            "config": {
                "selected_model": user_settings.preferred_ai_model,
                "temperature": user_settings.temperature,
                "max_tokens": user_settings.max_tokens,
                "language": user_settings.language
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour de la configuration: {str(e)}"
        )

@router.post("/chatbot/query", response_model=ChatbotResponse)
def chatbot_query(
    *,
    db: Session = Depends(get_db),
    query: str,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Interroger le chatbot avec la configuration utilisateur.
    """
    try:
        # Récupérer la configuration utilisateur
        user_settings = db.query(models.UserSettings).filter(
            models.UserSettings.user_id == current_user.id
        ).first()

        model = user_settings.preferred_ai_model if user_settings else "gemini-pro"
        temperature = user_settings.temperature if user_settings else 0.7
        max_tokens = user_settings.max_tokens if user_settings else 1024
        language = user_settings.language if user_settings else "fr"

        # Générer une réponse en français
        import random
        import time
        time.sleep(0.3)  # Simuler le temps de traitement

        # Réponses en français basées sur le type de requête
        if "analyse de données" in query.lower():
            response = f"Basé sur votre demande d'analyse de données: '{query}', j'ai analysé les motifs et identifié des tendances clés. Les données montrent des corrélations significatives entre les variables X et Y, suggérant des opportunités commerciales potentielles."
        elif "prédiction" in query.lower():
            response = f"Pour votre demande de prédiction: '{query}', le modèle prévoit une augmentation de {random.uniform(5, 20):.1f}% de la métrique cible au cours du prochain trimestre, avec une confiance de {random.uniform(70, 95):.0f}%."
        elif "recommandation" in query.lower():
            response = f"Concernant votre demande de recommandation: '{query}', je suggère de mettre en œuvre la stratégie A pour des gains à court terme et la stratégie B pour une croissance à long terme. Cela est basé sur l'analyse des performances historiques."
        else:
            response = f"J'ai traité votre requête: '{query}'. Voici une analyse complète avec des informations exploitables et des recommandations basées sur les données, adaptées à votre contexte commercial."

        return {
            "response": response,
            "model_used": model,
            "tokens_used": random.randint(50, max_tokens),
            "suggestions": [
                "Envisagez d'exécuter des tests A/B supplémentaires",
                "Examinez les motifs saisonniers identifiés",
                "Validez les résultats avec des experts du domaine",
                "Optimisez les paramètres du modèle pour de meilleurs résultats"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de la requête du chatbot: {str(e)}"
        )

@router.get("/chatbot/models")
def get_chatbot_models() -> List[dict]:
    """
    Obtenir la liste des modèles de chatbot disponibles.
    """
    return [
        {
            "name": "gemini-pro",
            "display_name": "Gemini Pro",
            "description": "Modèle polyvalent pour la plupart des tâches",
            "max_tokens": 8192,
            "supported_languages": ["fr", "en", "es", "de"]
        },
        {
            "name": "gemini-pro-vision",
            "display_name": "Gemini Pro Vision",
            "description": "Modèle avec capacités de vision par ordinateur",
            "max_tokens": 4096,
            "supported_languages": ["fr", "en"]
        },
        {
            "name": "gemini-ultra",
            "display_name": "Gemini Ultra",
            "description": "Modèle le plus puissant pour les tâches complexes",
            "max_tokens": 16384,
            "supported_languages": ["fr", "en", "es", "de", "it"]
        }
    ]

@router.get("/chatbot/config")
def get_chatbot_config(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Obtenir la configuration actuelle du chatbot.
    """
    try:
        user_settings = db.query(models.UserSettings).filter(
            models.UserSettings.user_id == current_user.id
        ).first()

        if not user_settings:
            return {
                "selected_model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 1024,
                "language": "fr",
                "available_models": get_chatbot_models()
            }

        return {
            "selected_model": user_settings.preferred_ai_model,
            "temperature": user_settings.temperature,
            "max_tokens": user_settings.max_tokens,
            "language": user_settings.language,
            "available_models": get_chatbot_models()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la configuration: {str(e)}"
        )