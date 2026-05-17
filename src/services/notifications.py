FIXED code:

```python
from typing import Optional, List
import logging
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from src.config import settings
from src.database import get_db
from src.models.user import User
from src.models.project import Project

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Handles sending email notifications via SendGrid.
    All methods are synchronous; for use in async contexts, call via
    BackgroundTasks or asyncio.to_thread.
    """

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        self.api_key = api_key or settings.SENDGRID_API_KEY
        self.from_email = from_email or settings.FROM_EMAIL
        if not self.api_key:
            raise ValueError("SendGrid API key is not configured")
        if not self.from_email:
            raise ValueError("Sender email address is not configured")
        self.client = SendGridAPIClient(self.api_key)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: Optional[str] = None,
    ) -> bool:
        """
        Send an email using SendGrid.

        Args:
            to_email: Recipient email address.
            subject: Email subject line.
            html_content: HTML body of the email.
            to_name: Optional recipient name.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        if not to_email or not subject or not html_content:
            logger.error("Missing required email parameters")
            return False

        message = Mail(
            from_email=Email(self.from_email, "Project Creator"),
            to_emails=To(to_email, to_name) if to_name else To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content),
        )

        try:
            response = self.client.send(message)
            if response.status_code in (200, 201, 202):
                logger.info(f"Email sent to {to_email}")
                return True
            else:
                logger.error(
                    f"Failed to send email to {to_email}: status {response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
```