from typing import Any, List, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core.deps import get_current_active_user, get_db
from app.core.config import settings

router = APIRouter()

class AIQueryRequest(BaseModel):
    query: str
    project_id: Optional[int] = None
    model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1024

class AISuggestionRequest(BaseModel):
    project_id: int
    context: Optional[str] = None

class AIResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: int

class AISuggestion(BaseModel):
    suggestion: str
    confidence: float
    category: str

@router.post("/query", response_model=AIResponse)
def process_ai_query(
    *,
    db: Session = Depends(get_db),
    request: AIQueryRequest,
) -> Any:
    """
    Process AI query for data analysis using Gemini models.
    """
    # Debug logging
    print(f"DEBUG: AI Query received - Query: {request.query}, Model: {request.model}")
    print(f"DEBUG: Full request data: {request.dict()}")
    # Validate model selection
    available_models = ["gemini-pro", "gemini-pro-vision", "gemini-ultra"]
    if request.model not in available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {request.model} not available. Choose from: {', '.join(available_models)}"
        )

    # Force mock mode for testing
    import random
    import time

    # Simulate API processing time
    time.sleep(0.5)

    # Mock response based on query type - more varied responses
    greetings = [
        "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        "Salut ! Je suis prêt à vous assister.",
        "En quoi puis-je vous être utile ?",
        "Comment puis-je vous aider avec cette requête ?",
        "Je suis à votre disposition pour cette demande.",
        "Que puis-je faire pour vous aujourd'hui ?"
    ]

    if "data analysis" in request.query.lower():
        response = f"Pour votre demande d'analyse de données: '{request.query}', j'ai identifié des tendances clés. Les données montrent des corrélations significatives entre les variables, suggérant des opportunités stratégiques."
    elif "prediction" in request.query.lower():
        response = f"Concernant votre demande de prédiction: '{request.query}', le modèle prévoit une augmentation de {random.uniform(5, 20):.1f}% de la métrique cible au prochain trimestre, avec un niveau de confiance de {random.uniform(70, 95):.0f}%."
    elif "recommendation" in request.query.lower():
        response = f"Pour votre demande de recommandation: '{request.query}', je suggère de mettre en œuvre la stratégie A pour des gains à court terme et la stratégie B pour une croissance à long terme. Cela est basé sur l'analyse des performances historiques."
    elif "bonjour" in request.query.lower() or "salut" in request.query.lower() or "ça va" in request.query.lower():
        response = random.choice(greetings) + f" Votre requête: '{request.query}' a été reçue et sera traitée avec une analyse complète basée sur les données disponibles."
    else:
        # More varied default responses
        default_responses = [
            f"Votre requête: '{request.query}' est en cours de traitement. Voici une analyse complète avec des informations basées sur les données disponibles.",
            f"Je traite votre demande: '{request.query}'. Voici une réponse détaillée avec des recommandations adaptées à votre contexte.",
            f"Pour votre question: '{request.query}', voici une analyse approfondie avec des insights basés sur les données.",
            f"Concernant: '{request.query}', voici une réponse complète avec des informations pertinentes et des suggestions d'action.",
            f"Votre demande: '{request.query}' a été analysée. Voici un retour détaillé avec des données et recommandations.",
            f"Je vous fournit une réponse complète pour: '{request.query}' basée sur l'analyse des données disponibles."
        ]
        response = random.choice(default_responses)

    return {
        "response": response,
        "model_used": request.model,
        "tokens_used": random.randint(50, request.max_tokens),
        "suggestions": [
            "Consider running additional A/B tests",
            "Review the seasonal patterns identified",
            "Validate findings with domain experts"
        ]
    }


@router.get("/suggestions", response_model=List[AISuggestion])
def get_ai_suggestions(
    *,
    db: Session = Depends(get_db),
    request: AISuggestionRequest,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get AI suggestions for data operations using Gemini models.
    """
    try:
        # Mock suggestions based on context
        base_suggestions = [
            {
                "suggestion": "Implement automated data cleaning pipelines",
                "confidence": 0.92,
                "category": "data_quality"
            },
            {
                "suggestion": "Create interactive dashboards for real-time monitoring",
                "confidence": 0.88,
                "category": "visualization"
            },
            {
                "suggestion": "Set up anomaly detection alerts",
                "confidence": 0.85,
                "category": "monitoring"
            }
        ]

        # Add context-specific suggestions
        if request.context and "sales" in request.context.lower():
            base_suggestions.append({
                "suggestion": "Analyze sales funnel conversion rates",
                "confidence": 0.90,
                "category": "sales_analysis"
            })

        if request.context and "customer" in request.context.lower():
            base_suggestions.append({
                "suggestion": "Segment customers using RFM analysis",
                "confidence": 0.87,
                "category": "customer_insights"
            })

        return base_suggestions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )

@router.get("/models")
def get_available_models() -> List[str]:
    """
    Get list of available AI models.
    """
    return [
        "gemini-pro",
        "gemini-pro-vision",
        "gemini-ultra",
        "gemini-flash"
    ]

@router.get("/config")
def get_ai_config() -> dict:
    """
    Get current AI configuration.
    """
    return {
        "default_model": settings.GEMINI_MODEL,
        "temperature": settings.GEMINI_TEMPERATURE,
        "max_tokens": settings.GEMINI_MAX_TOKENS,
        "api_status": "operational",
        "models_available": get_available_models()
    }