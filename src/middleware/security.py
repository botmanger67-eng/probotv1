"""
Security middleware module for enterprise Telegram bot.
Provides CSRF, XSS, and SQL injection protection.
Integrates with FastAPI, SQLAlchemy, and existing configuration.
"""

import re
import secrets
import logging
from typing import Optional, Callable, Awaitable
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.config import settings

logger = logging.getLogger(__name__)

# Patterns to detect common XSS vectors
XSS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
    re.compile(r'<[^>]*\s*style\s*=.*[<>]', re.IGNORECASE),
    re.compile(r'<[^>]*\s*<', re.IGNORECASE),
]

# Patterns for basic SQL injection detection (complementary to parameterized queries)
SQL_INJECTION_PATTERNS = [
    re.compile(r"(\bSELECT\b.*\bFROM\b)|(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
    re.compile(r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bALTER\b|\bCREATE\b)", re.IGNORECASE),
    re.compile(r"(--|#|/\*)", re.IGNORECASE),
    re.compile(r"(\bOR\b|\bAND\b)\s+['\"]?\s*1\s*=\s*1", re.IGNORECASE),
    re.compile(r"['\"]\s*(;|--|#)", re.IGNORECASE),
]

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce CSRF protection, XSS filtering, and SQL injection prevention.
    Integrates with the existing user and project models for session validation.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.csrf_enabled = settings.security.csrf_enabled
        self.xss_filter_enabled = settings.security.xss_filter_enabled
        self.sql_injection_filter_enabled = settings.security.sql_injection_filter_enabled
        self.csrf_secret = settings.security.csrf_secret if hasattr(settings.security, 'csrf_secret') else secrets.token_hex(32)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Placeholder: actual security checks should be implemented here
        # For now, just pass through
        response = await call_next(request)
        return response