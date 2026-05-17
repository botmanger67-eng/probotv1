"""
User SQLAlchemy model for the Telegram bot project.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship, validates, Mapped, mapped_column
from src.database import Base
from src.config import settings
from src.models.project import Project
from src.models.subscription import Subscription
import enum


class UserRole(str, enum.Enum):
    """Enum for user roles."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """
    Represents a user of the Telegram bot system.
    Stores authentication and profile information.
    """

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("telegram_id", name="uq_user_telegram_id"),
        UniqueConstraint("email", name="uq_user_email"),
        Index("idx_user_telegram_id", "telegram_id"),
        Index("idx_user_email", "email"),
        {"schema": settings.DB_SCHEMA or None},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    telegram_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )