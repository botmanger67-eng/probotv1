import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.config import settings
from src.database import Base, get_db
from src.models.user import User
from src.models.project import Project
from src.models.subscription import Subscription
from src.schemas.user import UserCreate, UserResponse
from src.schemas.project import ProjectCreate, ProjectResponse
from src.middleware.auth import get_current_user
from src.services.ai_orchestrator import AIOrchestrator
from src.services.rate_limiter import RateLimiter
from src.services.notifications import NotificationService
from unittest.mock import AsyncMock, MagicMock, patch

# Use in-memory SQLite for tests to avoid file pollution and concurrency issues
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a clean test database for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden dependencies."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # session lifecycle managed by the db_session fixture

    def override_get_current_user():
        # Return a mock user object; consider adding to DB if endpoints query it
        return User(id=1, email="test@example.com", name="Test User", role="user")

    def override_rate_limiter():
        return MagicMock(spec=RateLimiter)

    def override_ai_orchestrator():
        return MagicMock(spec=AIOrchestrator)

    def override_notification_service():
        return MagicMock(spec=NotificationService)

    # Apply all overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[RateLimiter] = override_rate_limiter
    app.dependency_overrides[AIOrchestrator] = override_ai_orchestrator
    app.dependency_overrides[NotificationService] = override_notification_service

    with TestClient(app) as client:
        yield client

    # Clean up overrides after test
    app.dependency_overrides.clear()