import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from telegram import Update
from telegram.ext import Application

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def set_webhook(bot: Application) -> bool:
    """
    Set the Telegram bot webhook to the configured URL.

    Args:
        bot: The initialized Telegram Application instance.

    Returns:
        True if webhook was set successfully, False otherwise.

    Raises:
        RuntimeError: If setting the webhook fails repeatedly.
    """
    try:
        await bot.bot.set_webhook(
            url=settings.WEBHOOK_URL,
            secret_token=settings.WEBHOOK_SECRET_TOKEN,
            allowed_updates=Update.ALL_TYPES,
        )
        logger.info("Webhook set successfully to %s", settings.WEBHOOK_URL)
        return True
    except Exception as e:
        logger.error("Failed to set webhook: %s", e)
        raise RuntimeError("Could not set Telegram webhook") from e


async def delete_webhook(bot: Application) -> bool:
    """
    Remove the current webhook for the bot.

    Args:
        bot: The Telegram Application instance.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    try:
        await bot.bot.delete_webhook()
        logger.info("Webhook deleted successfully")
        return True
    except Exception as e:
        logger.error("Failed to delete webhook: %s", e)
        return False


async def process_update(
    bot: Application,
    update_data: dict,
    secret_token: Optional[str] = None,
) -> int:
    """
    Validate and process an incoming Telegram update.

    Args:
        bot: The Telegram Application instance (must be initialized and started).
        update_data: The raw JSON payload from Telegram.
        secret_token: The expected secret token from the request header.
            If provided, it is compared against the configured secret token.
            If it does not match, the request is rejected with 403.

    Returns:
        HTTP status code (200 on success, 403 on invalid token, 400 on parse error).
    """
    # Validate secret token if provided
    if secret_token is not None and secret_token != settings.WEBHOOK_SECRET_TOKEN:
        logger.warning("Invalid secret token received")
        return 403

    try:
        # Parse the update using the bot instance
        update = Update.de_json(update_data, bot.bot)
    except Exception as e:
        logger.error("Failed to parse update data: %s", e)
        return 400

    # Process the update
    try:
        await bot.process_update(update)
    except Exception as e:
        logger.error("Failed to process update: %s", e)
        return 500

    return 200