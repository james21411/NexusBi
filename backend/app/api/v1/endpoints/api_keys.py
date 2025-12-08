from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core.deps import get_current_active_user, get_db
from app.core.security import get_random_string

router = APIRouter()

class APIKeyCreate(BaseModel):
    key_name: str
    key_type: str = "gemini"

class APIKeyResponse(BaseModel):
    id: int
    key_name: str
    key_type: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]
    usage_count: int

class APIKeyUsageResponse(BaseModel):
    id: int
    endpoint: str
    request_method: str
    response_status: int
    tokens_used: int
    created_at: datetime
    processing_time_ms: float

class UserSettingsResponse(BaseModel):
    preferred_ai_model: str
    temperature: float
    max_tokens: int
    theme: str
    language: str
    notifications_enabled: bool

@router.post("/create", response_model=APIKeyResponse)
def create_api_key(
    *,
    db: Session = Depends(get_db),
    key_data: APIKeyCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new API key for the current user.
    """
    try:
        # Generate a secure random API key
        api_key_value = f"sk-{get_random_string(32)}"

        # Create the API key record
        db_api_key = models.APIKey(
            user_id=current_user.id,
            key_name=key_data.key_name,
            key_value=api_key_value,
            key_type=key_data.key_type,
            is_active=True,
            usage_count=0
        )

        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)

        # Return the key response (without the actual key value for security)
        return {
            "id": db_api_key.id,
            "key_name": db_api_key.key_name,
            "key_type": db_api_key.key_type,
            "is_active": db_api_key.is_active,
            "created_at": db_api_key.created_at,
            "last_used_at": db_api_key.last_used_at,
            "usage_count": db_api_key.usage_count,
            "key_value": api_key_value  # In production, don't return this
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}"
        )

@router.get("/list", response_model=List[APIKeyResponse])
def list_api_keys(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    List all API keys for the current user.
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
            detail=f"Error listing API keys: {str(e)}"
        )

@router.get("/usage/{key_id}", response_model=List[APIKeyUsageResponse])
def get_api_key_usage(
    *,
    db: Session = Depends(get_db),
    key_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get usage history for a specific API key.
    """
    try:
        # Verify the key belongs to the current user
        api_key = db.query(models.APIKey).filter(
            models.APIKey.id == key_id,
            models.APIKey.user_id == current_user.id
        ).first()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        usage_history = db.query(models.APIKeyUsage).filter(
            models.APIKeyUsage.api_key_id == key_id
        ).order_by(models.APIKeyUsage.created_at.desc()).limit(50).all()

        return [{
            "id": usage.id,
            "endpoint": usage.endpoint,
            "request_method": usage.request_method,
            "response_status": usage.response_status,
            "tokens_used": usage.tokens_used,
            "created_at": usage.created_at,
            "processing_time_ms": usage.processing_time_ms
        } for usage in usage_history]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API key usage: {str(e)}"
        )

@router.post("/deactivate/{key_id}")
def deactivate_api_key(
    *,
    db: Session = Depends(get_db),
    key_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Deactivate an API key.
    """
    try:
        api_key = db.query(models.APIKey).filter(
            models.APIKey.id == key_id,
            models.APIKey.user_id == current_user.id
        ).first()

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )

        api_key.is_active = False
        db.commit()

        return {"status": "success", "message": "API key deactivated"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating API key: {str(e)}"
        )

@router.get("/settings", response_model=UserSettingsResponse)
def get_user_settings(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get user settings.
    """
    try:
        # Check if user has settings, if not create default settings
        user_settings = db.query(models.UserSettings).filter(
            models.UserSettings.user_id == current_user.id
        ).first()

        if not user_settings:
            # Create default settings
            user_settings = models.UserSettings(
                user_id=current_user.id,
                preferred_ai_model="gemini-pro",
                temperature=0.7,
                max_tokens=1024,
                theme="dark",
                language="en",
                notifications_enabled=True
            )
            db.add(user_settings)
            db.commit()
            db.refresh(user_settings)

        return {
            "preferred_ai_model": user_settings.preferred_ai_model,
            "temperature": user_settings.temperature,
            "max_tokens": user_settings.max_tokens,
            "theme": user_settings.theme,
            "language": user_settings.language,
            "notifications_enabled": user_settings.notifications_enabled
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user settings: {str(e)}"
        )

@router.post("/settings/update")
def update_user_settings(
    *,
    db: Session = Depends(get_db),
    settings_data: UserSettingsResponse,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Update user settings.
    """
    try:
        user_settings = db.query(models.UserSettings).filter(
            models.UserSettings.user_id == current_user.id
        ).first()

        if not user_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )

        # Update settings
        user_settings.preferred_ai_model = settings_data.preferred_ai_model
        user_settings.temperature = settings_data.temperature
        user_settings.max_tokens = settings_data.max_tokens
        user_settings.theme = settings_data.theme
        user_settings.language = settings_data.language
        user_settings.notifications_enabled = settings_data.notifications_enabled

        db.commit()

        return {
            "status": "success",
            "message": "User settings updated successfully",
            "updated_settings": settings_data.dict()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user settings: {str(e)}"
        )