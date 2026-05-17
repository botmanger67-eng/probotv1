"""
Telegram bot message handlers for project creation and management.
Integrates with database models, AI orchestration, and rate limiting.
"""

from typing import Optional
from uuid import UUID

from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from src.config import settings
from src.database import get_db_session
from src.models.user import User, UserRole
from src.models.project import Project, ProjectStatus
from src.models.subscription import Subscription, SubscriptionTier
from src.bot.keyboards import (
    main_menu_keyboard,
    project_type_keyboard,
    confirm_keyboard,
    subscription_keyboard,
)
from src.services.ai_orchestrator import ai_orchestrator
from src.services.code_generator import code_generator
from src.services.rate_limiter import rate_limiter
from src.services.voice_processor import voice_processor
from src.services.memory import conversation_memory
from src.services.notifications import NotificationService
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Conversation states
SELECTING_ACTION, ADDING_PROJECT_NAME, ADDING_DESCRIPTION, SELECTING_TECH_STACK, CONFIRMING_PROJECT = range(5)

# Callback data patterns
CALLBACK_PROJECT_TYPE = "project_type:{}"
CALLBACK_CONFIRM = "confirm:{}"
CALLBACK_CANCEL = "cancel:{}"

# Maximum number of concurrent projects per user (from settings or config)
MAX_CONCURRENT_PROJECTS = settings.MAX_CONCURRENT_PROJECTS or 5

# Rate limit configuration
RATE_LIMIT_COMMANDS = 10  # commands per minute
RATE_LIMIT_MESSAGES = 30  # messages per minute


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command. Initialize user in database and show main menu.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Log the incoming command
    logger.info(f"User {user_id} (@{username}) started the bot.")

    # Initialize user in database if new
    db_session = get_db_session()
    try:
        user = db_session.query(User).filter(User.telegram_id == user_id).first()
        if user is None:
            user = User(
                telegram_id=user_id,
                username=username,
                role=UserRole.USER,
            )
            db_session.add(user)
            db_session.commit()
            logger.info(f"New user created: {user_id}")
        else:
            logger.debug(f"Existing user: {user_id}")
    except Exception as e:
        logger.error(f"Database error while handling /start for user {user_id}: {e}")
        await update.message.reply_text("⚠️ An error occurred while setting up your account. Please try again later.")
        return ConversationHandler.END
    finally:
        db_session.close()

    # Send welcome message with main menu
    welcome_text = (
        f"👋 Hello, {username}! Welcome to BotAI.\n\n"
        "I can help you create and manage projects. Use the menu below to get started."
    )
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=main_menu_keyboard(),
    )

    return SELECTING_ACTION