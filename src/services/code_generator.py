from typing import Dict, List, Optional, Any
import logging
from enum import Enum
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.database import get_db, async_session
from src.models.project import Project, GeneratedFile
from src.models.user import User
from src.services.ai_orchestrator import AIService  # Assumed to have generate_text()
from src.services.rate_limiter import RateLimiter  # Optional per-user limits

logger = logging.getLogger(__name__)

class SupportedLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    KOTLIN = "kotlin"
    RUBY = "ruby"
    SWIFT = "swift"
    CPP = "cpp"

class CodeGenerationError(Exception):
    """Base exception for code generation failures."""
    pass

class UnsupportedLanguageError(CodeGenerationError):
    """Raised when requested language is not supported."""
    pass

class EmptyPromptError(CodeGenerationError):
    """Raised when prompt is empty."""
    pass

class AIServiceError(CodeGenerationError):
    """Raised when underlying AI service fails."""
    pass

class CodeGenerator:
    """
    Multi-language code generation service.
    Integrates with AI orchestrator and persists generated code to the project.
    """

    LANGUAGE_CONFIG: Dict[SupportedLanguage, Dict[str, Any]] = {
        SupportedLanguage.PYTHON: {
            "file_extension": ".py",
            "comment_prefix": "#",
            "block_comment_start": '"""',
            "block_comment_end": '"""',
        },
        SupportedLanguage.JAVASCRIPT: {
            "file_extension": ".js",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.TYPESCRIPT: {
            "file_extension": ".ts",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.GO: {
            "file_extension": ".go",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.RUST: {
            "file_extension": ".rs",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.JAVA: {
            "file_extension": ".java",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.KOTLIN: {
            "file_extension": ".kt",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.RUBY: {
            "file_extension": ".rb",
            "comment_prefix": "#",
            "block_comment_start": "=begin",
            "block_comment_end": "=end",
        },
        SupportedLanguage.SWIFT: {
            "file_extension": ".swift",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
        SupportedLanguage.CPP: {
            "file_extension": ".cpp",
            "comment_prefix": "//",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
        },
    }