"""
Database session management using async SQLAlchemy.

Provides:
- Async engine and session factory from DATABASE_URL
- FastAPI dependency `get_db_session` for route handlers
- `get_sessionmaker` for Celery tasks and scripts
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from config.settings import settings
from typing import AsyncGenerator

# ---------------------------------------------------------------------------
# Engine construction
# ---------------------------------------------------------------------------
# The canonical DATABASE_URL may use the plain `postgresql://` scheme.
# SQLAlchemy's async support requires the `asyncpg` driver.
_raw_url: str = settings.DATABASE_URL or ""

if _raw_url.startswith("postgresql://"):
    _async_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgres://"):
    _async_url = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql+asyncpg://"):
    _async_url = _raw_url
else:
    # Fallback — unit tests or CI may have no DB at all.
    _async_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/careeros"

engine = create_async_engine(
    _async_url,
    echo=settings.ENVIRONMENT.lower() == "development",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Session factory for dependency injection
_async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for FastAPI route handlers.

    Usage::

        @router.get("/items")
        async def list_items(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# For Celery / scripts (non-FastAPI contexts)
# ---------------------------------------------------------------------------
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return the session factory for use outside of FastAPI."""
    return _async_session_factory
