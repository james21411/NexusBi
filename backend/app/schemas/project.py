from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    name: str


class ProjectUpdate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    owner_id: int
    is_active: bool

    class Config:
        from_attributes = True


class DataSourceBase(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    connection_string: Optional[str] = None
    file_path: Optional[str] = None


class DataSourceCreate(DataSourceBase):
    name: str
    type: str
    project_id: int


class DataSourceUpdate(DataSourceBase):
    pass


class DataSource(DataSourceBase):
    id: int
    project_id: int
    schema_info: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True