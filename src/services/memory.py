"""
Self-learning memory system for enterprise project creation bot.
Stores and retrieves contextual memories about users and projects,
enabling the AI orchestrator to learn from past interactions.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, and_
from sqlalchemy.dialects.postgresql import JSONB, UUID as UUIDType
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func

from src.config import settings
from src.database import Base, get_db_session
from src.models.project import Project
from src.models.user import User


class Memory(Base):
    """Persistent memory entry stored in PostgreSQL."""
    __tablename__ = "memories"

    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUIDType(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUIDType(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSONB, nullable=False, default=dict)
    weight = Column(Integer, nullable=False, default=1)  # Self-learning weight
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships (optional, for ORM convenience)
    user = relationship("User", backref="memories")
    project = relationship("Project", backref="memories")

    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, user={self.user_id}, key={self.key})>"


class MemoryService:
    """
    Self-learning memory service that persists and retrieves
    """