from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    data_sources = relationship("DataSource", back_populates="project")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # csv, excel, mysql, postgresql, sql_dump
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    connection_string = Column(Text)  # For database connections
    file_path = Column(String)  # For file-based sources
    schema_info = Column(Text)  # JSON string with column info
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="data_sources")
    data_rows = relationship("DataFrameData", back_populates="data_source")


class DataFrameData(Base):
    __tablename__ = "dataframe_data"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    row_data = Column(Text, nullable=False)  # JSON string of the row data
    row_index = Column(Integer, nullable=False)  # Row index in the DataFrame

    # Relationships
    data_source = relationship("DataSource", back_populates="data_rows")