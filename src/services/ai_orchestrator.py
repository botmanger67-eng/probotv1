import logging
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.database import get_async_session
from src.models.user import User
from src.models.project import Project, ProjectStatus

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Orchestrates multi-agent AI tasks using DeepSeek models.
    Coordinates calls to the DeepSeek API for project creation, code review,
    and other AI-driven features.
    """

    def __init__(self):
        self.api_key: str = settings.DEEPSEEK_API_KEY
        self.api_url: str = settings.DEEPSEEK_API_URL
        self.model: str = settings.DEEPSEEK_MODEL
        self.http_client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=httpx.Timeout(30.0, read=60.0)
        )

    async def __aenter__(self) -> "AIOrchestrator":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.http_client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_deepseek(self, prompt: str, system_prompt: str = "") -> str:
        """
        Make an API call to DeepSeek with retry logic.

        Args:
            prompt: User input prompt.
            system_prompt: System-level instructions.

        Returns:
            The generated text response from the model.

        Raises:
            RuntimeError: If API call fails after retries.
        """
        try:
            payload: Dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            response = await self.http_client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise RuntimeError(f"DeepSeek API call failed after retries: {e}")