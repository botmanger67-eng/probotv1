import os
import tempfile
import logging
from typing import Optional, BinaryIO
from pathlib import Path

import whisper
from fastapi import UploadFile

from src.config import settings
from src.services.ai_orchestrator import AIOrchestrator
from src.services.rate_limiter import RateLimiter
from src.services.notifications import NotificationService

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """
    Handles voice message processing using OpenAI Whisper for speech-to-text
    and integrates with AI orchestrator for further processing.
    """

    def __init__(self):
        self.model: Optional[whisper.Whisper] = None
        self._load_model()
        self.orchestrator = AIOrchestrator()
        self.rate_limiter = RateLimiter()
        self.notification_service = NotificationService()

    def _load_model(self) -> None:
        """Load Whisper model based on configuration."""
        try:
            model_size = settings.WHISPER_MODEL_SIZE or "base"
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError("Voice processing is unavailable due to model loading failure")

    async def transcribe_audio(self, audio_file: BinaryIO) -> str:
        """
        Transcribe audio file to text using Whisper.

        Args:
            audio_file: Binary file-like object of audio data

        Returns:
            Transcribed text string

        Raises:
            ValueError: If audio file is invalid or too large
            RuntimeError: If transcription fails
        """
        if not self.model:
            raise RuntimeError("Whisper model not loaded")

        # Validate file size (max 25 MB)
        audio_file.seek(0, os.SEEK_END)
        file_size = audio_file.tell()
        audio_file.seek(0)  # rewind

        max_size = 25 * 1024 * 1024  # 25 MB
        if file_size > max_size:
            raise ValueError(f"Audio file too large: {file_size} bytes (max {max_size} bytes)")

        # Write audio to temporary file for Whisper
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            # Transcribe using Whisper (synchronous, but we run in executor to avoid blocking)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.model.transcribe, tmp_path)
            text = result.get("text", "").strip()
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError("Transcription failed due to an internal error") from e
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)