FIXED

```python
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config import settings
from src.database import Base


class ProjectStatus(str, PyEnum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(Base):
    """
    SQLAlchemy model representing a user project.

    Attributes:
        id: Unique UUID primary key.
        user_id: Foreign key to the user who owns the project.
        title: Project title (required, max 255 chars).
        description: Detailed project description (optional).
        status: Current lifecycle status (see ProjectStatus enum).
        created_at: Timestamp when the project was created.
        updated_at: Timestamp of the last modification.
    """

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(
        String(255),
        nullable=False,
        index=True,
    )
    description = Column(
        Text,
        nullable=True,
        default=None,
    )
    status = Column(
        Enum(ProjectStatus, name="project_status_enum"),
        nullable=False,
        default=ProjectStatus.DRAFT,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
```