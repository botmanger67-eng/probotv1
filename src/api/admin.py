from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.config import settings
from src.database import get_db
from src.models.user import User, UserRole
from src.models.project import Project, ProjectStatus
from src.schemas.user import UserOut, UserAdminUpdate
from src.schemas.project import ProjectOut
from src.middleware.auth import get_current_user
from src.middleware.security import admin_required

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(admin_required)]
)

def get_admin_dependency():
    """Return dependency that checks if current user is admin."""
    async def admin_only(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    return admin_only

admin_dependency = get_admin_dependency()

@router.get("/dashboard", summary="Get admin dashboard statistics")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_dependency)
):
    """
    Return aggregated statistics for the admin dashboard.
    
    - Total users
    - Active projects
    - Total projects
    - New users in last 7 days
    """
    try:
        # Total users
        total_users_query = select(func.count(User.id))
        total_users_result = await db.execute(total_users_query)
        total_users = total_users_result.scalar()

        # Active projects (assuming status is active/running)
        active_projects_query = select(func.count(Project.id)).where(
            Project.status == ProjectStatus.ACTIVE
        )
        active_projects_result = await db.execute(active_projects_query)
        active_projects = active_projects_result.scalar()  # FIX: corrected variable name