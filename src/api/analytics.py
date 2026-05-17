FIXED

```python
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from src.config import get_settings
from src.database import get_db
from src.models.user import User
from src.models.project import Project
from src.models.subscription import Subscription
from src.middleware.auth import get_current_admin_user
from src.services.rate_limiter import rate_limit

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}}
)

@router.get("/overview", response_model=Dict[str, Any])
async def get_analytics_overview(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
    rate: Any = Depends(rate_limit(limit="admin"))
) -> Dict[str, Any]:
    """
    Get an overview of platform analytics: total users, total projects,
    active subscriptions, recent activity counts.
    """
    try:
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Total users
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0

        # Users created in last 24h and 7d
        new_users_24h_result = await db.execute(
            select(func.count(User.id)).where(User.created_at >= last_24h)
        )
        new_users_24h = new_users_24h_result.scalar() or 0

        new_users_7d_result = await db.execute(
            select(func.count(User.id)).where(User.created_at >= last_7d)
        )
        new_users_7d = new_users_7d_result.scalar() or 0

        # Total projects
        total_projects_result = await db.execute(select(func.count(Project.id)))
        total_projects = total_projects_result.scalar() or 0

        # Projects created in last 24h and 7d
        new_projects_24h_result = await db.execute(
            select(func.count(Project.id)).where(Project.created_at >= last_24h)
        )
        new_projects_24h = new_projects_24h_result.scalar() or 0

        new_projects_7d_result = await db.execute(
            select(func.count(Project.id)).where(Project.created_at >= last_7d)
        )
        new_projects_7d = new_projects_7d_result.scalar() or 0

        # Active subscriptions (assuming 'active' status)
        active_subscriptions_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.status == 'active')
        )
        active_subscriptions = active_subscriptions_result.scalar() or 0

        # Subscriptions created in last 24h and 7d
        new_subscriptions_24h_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.created_at >= last_24h)
        )
        new_subscriptions_24h = new_subscriptions_24h_result.scalar() or 0

        new_subscriptions_7d_result = await db.execute(
            select(func.count(Subscription.id)).where(Subscription.created_at >= last_7d)
        )
        new_subscriptions_7d = new_subscriptions_7d_result.scalar() or 0

        return {
            "total_users": total_users,
            "new_users_24h": new_users_24h,
            "new_users_7d": new_users_7d,
            "total_projects": total_projects,
            "new_projects_24h": new_projects_24h,
            "new_projects_7d": new_projects_7d,
            "active_subscriptions": active_subscriptions,
            "new_subscriptions_24h": new_subscriptions_24h,
            "new_subscriptions_7d": new_subscriptions_7d,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics retrieval failed: {str(e)}"
        )
```