import os
import sys
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock, Mock
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Test configuration
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test:bot-token")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ENVIRONMENT", "test")

from src.config import settings, Settings
from src.database import get_db, Base, engine, async_session
from src.models.user import User, UserRole
from src.models.project import Project, ProjectStatus, ProjectType
from src.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from src.services.ai_orchestrator import AIOrchestrator
from src.services.memory import MemoryService
from src.services.code_generator import CodeGenerator
from src.services.voice_processor import VoiceProcessor
from src.services.deployment import DeploymentService
from src.services.rate_limiter import RateLimiter, RateLimit
from src.services.notifications import NotificationService, NotificationType
from src.services.task_queue import TaskQueue
from src.services.code_review import CodeReviewService

# ---- Fixtures ----

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)