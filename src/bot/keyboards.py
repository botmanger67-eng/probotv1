"""
Bot inline keyboards for Telegram bot.
Provides keyboard markup functions for various bot interactions.
"""

from typing import Optional, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.config import (
    ADMIN_IDS,
    PROJECT_STATUSES,
    SUBSCRIPTION_PLANS,
    BOT_USERNAME,
)


def main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Generate the main menu inline keyboard.

    Args:
        is_admin: Whether the user is an admin.

    Returns:
        InlineKeyboardMarkup with main menu buttons.
    """
    try:
        buttons: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton("📋 My Projects", callback_data="my_projects")],
            [InlineKeyboardButton("➕ Create Project", callback_data="create_project")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]

        if is_admin:
            buttons.append([InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_panel")])

        return InlineKeyboardMarkup(buttons)
    except Exception as e:
        # Fallback to a minimal keyboard in case of error
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Error", callback_data="error")]]
        )


def project_actions_keyboard(
    project_id: int,
    is_owner: bool = False,
    status: Optional[str] = None,
) -> InlineKeyboardMarkup:
    """
    Generate keyboard for project-specific actions.

    Args:
        project_id: The project ID.
        is_owner: Whether the user owns the project.
        status: Current project status (if available).

    Returns:
        InlineKeyboardMarkup with action buttons.
    """
    try:
        buttons: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton("📄 View Details", callback_data=f"view_project:{project_id}")],
        ]

        if is_owner:
            buttons.append([InlineKeyboardButton("✏️ Edit Project", callback_data=f"edit_project:{project_id}")])
            buttons.append([InlineKeyboardButton("🗑️ Delete Project", callback_data=f"delete_project:{project_id}")])

        # Add status-specific action if status is known
        if status and status in PROJECT_STATUSES:
            allowed_transitions = {
                "draft": ["submit"],
                "pending": ["approve", "reject"],
                "approved": ["complete"],
                "rejected": ["reopen"],
                "completed": [],
            }
            if status in allowed_transitions:
                for next_status in allowed_transitions[status]:
                    buttons.append([
                        InlineKeyboardButton(
                            f"➡️ Move to {next_status.capitalize()}",
                            callback_data=f"change_status:{project_id}:{next_status}"
                        )
                    ])

        return InlineKeyboardMarkup(buttons)
    except Exception as e:
        # Fallback to a minimal keyboard in case of error
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Error", callback_data="error")]]
        )