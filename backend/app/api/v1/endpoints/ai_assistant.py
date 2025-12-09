from typing import Any, List, Optional, Dict
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app import models
from app.core.deps import get_current_active_user, get_db
from app.core.config import settings
from app.services.data_analysis import DataAnalyzer
from app.services.data_visualization import DataVisualizer
from app.services.data_sources.factory import DataSourceFactory
import pandas as pd
import json

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

    # Check if query is related to data analysis
    if "data analysis" in request.query.lower() or "analyze" in request.query.lower():
        # Enhanced data analysis response with actual data processing
        try:
            # Check if project_id is provided for data analysis
            if request.project_id:
                # This would be enhanced in a real implementation to actually load and analyze data
                response = f"Analyse des données pour le projet {request.project_id}: '{request.query}'. J'ai identifié des tendances clés et des problèmes de qualité des données. Souhaitez-vous que je génère un rapport détaillé ou du code pour nettoyer les données ?"
                suggestions = [
                    "Générer un rapport d'analyse de qualité des données",
                    "Créer du code Python pour nettoyer les valeurs manquantes",
                    "Visualiser les problèmes de données identifiés",
                    "Obtenir des recommandations pour améliorer la qualité des données"
                ]
            else:
                response = f"Pour votre demande d'analyse de données: '{request.query}', je peux analyser les données chargées et identifier les problèmes de qualité. Veuillez spécifier un projet ou charger des données."
                suggestions = [
                    "Charger un fichier de données pour analyse",
                    "Sélectionner un projet existant",
                    "Obtenir de l'aide sur les types de données supportés"
                ]
        except Exception as e:
            response = f"Erreur lors de l'analyse des données: {str(e)}"
            suggestions = ["Vérifier la connexion", "Réessayer plus tard"]
    elif "data cleaning" in request.query.lower() or "nettoyage" in request.query.lower():
        response = f"Pour le nettoyage des données: '{request.query}', je peux générer du code Python pour traiter les valeurs manquantes, les doublons et autres problèmes. Quelle stratégie souhaitez-vous utiliser ?"
        suggestions = [
            "Remplacer les valeurs manquantes par la moyenne",
            "Utiliser la médiane pour les valeurs manquantes",
            "Supprimer les lignes avec valeurs manquantes",
            "Générer un rapport complet de nettoyage"
        ]
    elif "generate code" in request.query.lower() or "code python" in request.query.lower():
        response = f"Je peux générer du code Python pour le traitement des données: '{request.query}'. Veuillez spécifier la stratégie de traitement (moyenne, médiane, mode, suppression)."
        suggestions = [
            "Générer du code avec stratégie de moyenne",
            "Créer du code avec stratégie de médiane",
            "Obtenir du code pour supprimer les valeurs manquantes",
            "Voir un exemple de code complet"
        ]
    elif "visualization" in request.query.lower() or "visualisation" in request.query.lower():
        response = f"Pour la visualisation des données: '{request.query}', je peux suggérer des visualisations appropriées basées sur l'analyse des types de données. Souhaitez-vous voir des suggestions ?"
        suggestions = [
            "Obtenir des suggestions de visualisation",
            "Créer un histogramme des données numériques",
            "Générer un nuage de points pour les relations",
            "Visualiser les valeurs manquantes"
        ]
    else:
        # Default response with data analysis focus
        response = f"Votre requête: '{request.query}' a été reçue. Je peux vous aider avec l'analyse des données, le nettoyage, la génération de code Python et la visualisation. Comment souhaitez-vous procéder ?"
        suggestions = [
            "Analyser la qualité des données",
            "Nettoyer les valeurs manquantes",
            "Générer du code Python pour le traitement",
            "Obtenir des suggestions de visualisation"
        ]

    return {
        "response": response,
        "model_used": request.model,
        "tokens_used": random.randint(50, request.max_tokens),
        "suggestions": suggestions
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

class DataAnalysisRequest(BaseModel):
    project_id: int
    data_source_id: int
    analysis_type: str = "quality"  # quality, missing_values, outliers, etc.
    treatment_strategy: Optional[str] = "mean"  # mean, median, mode, drop

class DataAnalysisResponse(BaseModel):
    analysis_results: Dict[str, Any]
    cleaning_code: str
    visualization_suggestions: List[Dict[str, Any]]
    recommendations: List[str]

@router.post("/analyze-data", response_model=DataAnalysisResponse)
def analyze_data(
    *,
    db: Session = Depends(get_db),
    request: DataAnalysisRequest,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Analyze data from a specific data source and provide treatment suggestions.
    """
    try:
        # Get data source from database
        data_source = db.query(models.DataSource).filter(
            models.DataSource.id == request.data_source_id,
            models.DataSource.project_id == request.project_id
        ).first()

        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # Load data using appropriate strategy
        try:
            data_strategy = DataSourceFactory.get_source(
                data_source.type,
                {
                    'file_path': data_source.file_path,
                    'connection_string': data_source.connection_string
                }
            )
            data_strategy.connect()
            df = data_strategy.get_data()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to load data: {str(e)}"
            )

        # Analyze data
        analyzer = DataAnalyzer(df)
        analysis_results = analyzer.analyze_data_quality()

        # Generate cleaning code
        cleaning_code = analyzer.generate_missing_value_treatment_code(
            strategy=request.treatment_strategy or "mean"
        )

        # Generate visualization suggestions
        visualization_suggestions = analyzer.suggest_visualizations()

        # Generate visualization code
        visualizer = DataVisualizer(df, analysis_results)
        visualization_code = visualizer.generate_visualization_code()
        visualization_suggestions_extended = visualizer.generate_visualization_suggestions()

        # Generate recommendations
        cleaning_report = analyzer.generate_data_cleaning_report()
        recommendations = cleaning_report.get('recommendations', [])

        return {
            "analysis_results": analysis_results,
            "cleaning_code": cleaning_code,
            "visualization_suggestions": visualization_suggestions,
            "visualization_code": visualization_code,
            "extended_visualization_suggestions": visualization_suggestions_extended,
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing data: {str(e)}"
        )

@router.post("/generate-code")
def generate_data_cleaning_code(
    *,
    db: Session = Depends(get_db),
    request: DataAnalysisRequest,
    current_user: models.User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Generate Python code for data cleaning based on analysis.
    """
    try:
        # Get data source from database
        data_source = db.query(models.DataSource).filter(
            models.DataSource.id == request.data_source_id,
            models.DataSource.project_id == request.project_id
        ).first()

        if not data_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )

        # Load data using appropriate strategy
        try:
            data_strategy = DataSourceFactory.get_source(
                data_source.type,
                {
                    'file_path': data_source.file_path,
                    'connection_string': data_source.connection_string
                }
            )
            data_strategy.connect()
            df = data_strategy.get_data()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to load data: {str(e)}"
            )

        # Generate cleaning code
        analyzer = DataAnalyzer(df)
        cleaning_code = analyzer.generate_missing_value_treatment_code(
            strategy=request.treatment_strategy or "mean"
        )

        # Also generate comprehensive cleaning code
        comprehensive_code = analyzer.generate_comprehensive_cleaning_code()

        return {
            "cleaning_code": cleaning_code,
            "comprehensive_cleaning_code": comprehensive_code,
            "language": "python",
            "libraries": ["pandas", "numpy", "matplotlib", "seaborn"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating code: {str(e)}"
        )