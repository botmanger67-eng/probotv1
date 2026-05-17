from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config import settings

# Construct database URL. Ensure it uses async dialect (asyncpg).
# Expects DATABASE_URL like: postgresql+asyncpg://user:pass@host/db
DATABASE_URL: str = settings.DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling and timeout settings.
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set to True for debugging SQL
)

# Session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.

    Yields a session and ensures proper cleanup (commit/rollback).
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables defined by models that inherit from Base.

    Should be called once during application startup.
    """
    async with engine.begin() as conn:
        # Import models so they are registered on Base.metadata
        import src.models.user  # noqa: F401
        import src.models.project  # noqa: F401
        import src.models.subscription  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine (used during shutdown)."""
    await engine.dispose()