from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.core.deps import get_current_active_user, get_db

router = APIRouter()


@router.post("/query")
def process_ai_query(
    *,
    db: Session = Depends(get_db),
    query: str,
    project_id: int = None,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Process AI query for data analysis.
    """
    # TODO: Implement AI query processing with OpenAI
    raise HTTPException(status_code=501, detail="AI assistant not implemented yet")


@router.get("/suggestions")
def get_ai_suggestions(
    *,
    db: Session = Depends(get_db),
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Get AI suggestions for data operations.
    """
    # TODO: Implement AI suggestions
    return {"suggestions": []}