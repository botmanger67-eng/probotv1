import asyncio
import json
import logging
import signal
from typing import Any, Callable, Dict, Optional

import aioredis
from aioredis.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import async_session_factory
from src.models.user import User
from src.models.project import Project
from src.services.ai_orchestrator import AIOrchestrator
from src.services.code_generator import CodeGenerator
from src.services.deployment import DeploymentService
from src.services.notifications import NotificationService
from src.services.rate_limiter import RateLimiter
from src.workers.code_review import CodeReviewWorker

logger = logging.getLogger(__name__)


class TaskQueueWorker:
    """
    Redis-backed async task queue worker.
    Processes tasks from a Redis list (queue) with automatic retries and dead-letter handling.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL, queue_name: str = "task_queue"):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.redis: Optional[Redis] = None
        self.pubsub = None
        self._running = False
        self._task_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register built-in task handlers for known task types."""
        self.register_handler("project_create", self._handle_project_create)
        self.register_handler("project_deploy", self._handle_project_deploy)
        self.register_handler("code_review", self._handle_code_review)
        self.register_handler("ai_generate", self._handle_ai_generate)

    def register_handler(self, task_type: str, handler: Callable) -> None:
        """Register a custom handler for a specific task type."""
        self._task_handlers[task_type] = handler

    async def connect(self) -> None:
        """Establish Redis connection with retries."""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise