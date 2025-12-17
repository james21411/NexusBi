from fastapi import APIRouter

from app.api.v1.endpoints import auth, data_sources, projects, ai_assistant, settings, api_keys, user_api, data_preview

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["ai-assistant"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(user_api.router, prefix="/user", tags=["user-api"])
api_router.include_router(data_preview.router, prefix="/preview", tags=["data-preview"])