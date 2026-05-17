import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

from src.config import settings
from src.models.user import User as UserModel
from src.models.project import Project as ProjectModel
from src.database import get_db, AsyncSession
from src.bot.handlers import (
    start,
    help_command,
    new_project,
    handle_message,
    error_handler,
)
from src.services.ai_orchestrator import AIOrchestrator
from src.services.rate_limiter import RateLimiter


@pytest.fixture
def mock_db_session():
    """Fixture for mocked database session."""
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_update():
    """Fixture for mocked Update object."""
    user = User(
        id=123456,
        first_name="Test",
        last_name="User",
        username="testuser",
        is_bot=False,
    )
    chat = Chat(id=123456, type="private")
    message = MagicMock(spec=Message)
    message.message_id = 1
    message.from_user = user
    message.chat = chat
    message.text = ""
    message.reply_text = AsyncMock()
    message.reply_html = AsyncMock()
    message.reply_markdown = AsyncMock()
    update = MagicMock(spec=Update)
    update.update_id = 1
    update.effective_user = user
    update.effective_chat = chat
    update.message = message
    update.effective_message = message
    return update


@pytest.fixture
def mock_context():
    """Fixture for mocked Context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_chat_action = AsyncMock()
    context.args = []
    context.user_data = {}
    context.chat_data = {}
    context.bot_data = {}
    return context