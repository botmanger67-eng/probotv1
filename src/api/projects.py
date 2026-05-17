from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from datetime import datetime

from src.config import settings
from src.database import get_db
from src.models.project import Project, ProjectStatus
from src.models.user import User
from src.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from src.middleware.auth import get_current_active_user
from src.services.ai_orchestrator import AIOrchestrator
from src.services.rate_limiter import RateLimiter

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    rate_limiter: RateLimiter = Depends(RateLimiter),
) -> ProjectResponse:
    """
    Create a new project for the authenticated user.

    Args:
        project_data: Project creation payload.
        db: Database session.
        current_user: Authenticated user.
        rate_limiter: Rate limiter instance.

    Returns:
        ProjectResponse: Created project details.

    Raises:
        HTTPException: If project creation fails or rate limit exceeded.
    """
    # Check rate limit per user
    if not await rate_limiter.check_limit(current_user.id, "project_creation"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Project creation rate limit exceeded. Please try again later.",
        )

    # Validate project name uniqueness per user
    existing = await db.execute(
        select(Project).where(
            Project.owner_id == current_user.id,
            Project.name == project_data.name,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_data.name}' already exists.",
        )

    # Create new project
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
        status=ProjectStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectResponse(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        owner_id=new_project.owner_id,
        status=new_project.status,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
    )