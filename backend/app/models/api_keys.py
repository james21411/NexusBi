from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String, nullable=False)
    key_value = Column(String, unique=True, nullable=False)
    key_type = Column(String, nullable=False)  # gemini, openai, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User")
    usage_history = relationship("APIKeyUsage", back_populates="api_key")

class APIKeyUsage(Base):
    __tablename__ = "api_key_usage"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    endpoint = Column(String, nullable=False)
    request_method = Column(String, nullable=False)
    response_status = Column(Integer, nullable=False)
    tokens_used = Column(Integer, default=0)
    request_data = Column(Text)
    response_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Float)

    # Relationships
    api_key = relationship("APIKey", back_populates="usage_history")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    preferred_ai_model = Column(String, default="gemini-pro")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1024)
    theme = Column(String, default="dark")
    language = Column(String, default="en")
    notifications_enabled = Column(Boolean, default=True)
    last_active_project_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")

class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # login, query, settings_change, etc.
    activity_details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")