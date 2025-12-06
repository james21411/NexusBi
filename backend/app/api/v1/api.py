from fastapi import APIRouter

from app.api.v1.endpoints import auth, data_sources, projects, ai_assistant

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["ai-assistant"])