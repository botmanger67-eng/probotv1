import logging
from typing import Optional, Dict, Any
from datetime import datetime

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.config import settings
from src.database import get_db
from src.models.project import Project
from src.models.user import User
from src.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class DeploymentError(Exception):
    """Custom exception for deployment failures."""
    pass

class DeploymentService:
    """Handles one-click deployment to external platforms (Vercel, etc.)."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rate_limiter = RateLimiter("deployment", max_requests=5, window=60)
        self.client = httpx.AsyncClient(
            base_url="https://api.vercel.com",
            headers={
                "Authorization": f"Bearer {settings.VERCEL_API_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def deploy_project(self, project_id: int, user_id: int) -> Dict[str, Any]:
        """
        Deploy a project to Vercel.
        
        Args:
            project_id: ID of the project to deploy
            user_id: ID of the user requesting deployment
            
        Returns:
            Deployment details including URL and status
            
        Raises:
            DeploymentError: If deployment fails or validation errors occur
        """
        try:
            # Validate rate limit
            if not await self.rate_limiter.check(user_id):
                raise DeploymentError("Rate limit exceeded. Please wait before deploying again.")

            # Fetch project and validate ownership
            project = await self._get_project(project_id, user_id)
            if not project:
                raise DeploymentError("Project not found or access denied.")

            if project.deployment_status == "deploying":
                raise DeploymentError("Project is already being deployed.")

            # TODO: Call Vercel deployment API and handle response
            # Example return – replace with actual deployment logic
            return {
                "status": "deployment_triggered",
                "project_id": project.id,
                "message": "Deployment initiated"
            }

        except DeploymentError:
            raise
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise DeploymentError("An unexpected error occurred during deployment.") from e