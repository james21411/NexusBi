from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.deps import get_current_active_user, get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.DataSource])
def read_data_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve data sources for user's projects.
    """
    # TODO: Implement data source listing
    return []


@router.post("/", response_model=schemas.DataSource)
def create_data_source(
    *,
    db: Session = Depends(get_db),
    data_source_in: schemas.DataSourceCreate,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Create new data source.
    """
    # TODO: Implement data source creation
    raise HTTPException(status_code=501, detail="Not implemented yet")