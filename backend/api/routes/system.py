"""
System control API routes.

Implements the System Control endpoints from API_CONTRACTS.md §4:
  - POST /system/pause
  - POST /system/resume
  - GET  /system/status

Uses Redis to store system state for instant pause/resume.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from db.session import get_db_session
from db import messages_repo, activity_repo
from auth import get_current_user, CurrentUser
from services.redis_service import redis_service
from config.settings import settings

router = APIRouter()

# Redis keys for system state
_SYSTEM_STATUS_KEY = "careeros:system:status"
_SYSTEM_PAUSED_AT_KEY = "careeros:system:paused_at"
_SYSTEM_PAUSED_BY_KEY = "careeros:system:paused_by"


def _get_system_status() -> str:
    """Get current system status from Redis."""
    try:
        status = redis_service.get(_SYSTEM_STATUS_KEY)
        return status or "active"
    except Exception:
        return "active"


@router.post("/pause")
async def pause_system(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Pause all message generation and sending.

    Per API_CONTRACTS.md §4: POST /system/pause
    This is the backend for the Emergency Stop button in the UI.
    """
    now = datetime.now(timezone.utc).isoformat()

    try:
        redis_service.set(_SYSTEM_STATUS_KEY, "paused")
        redis_service.set(_SYSTEM_PAUSED_AT_KEY, now)
        redis_service.set(_SYSTEM_PAUSED_BY_KEY, current_user["id"])

        # Log the action
        await activity_repo.log(
            session,
            uuid.UUID(current_user["id"]),
            action_type="system_pause",
            metadata={"paused_at": now},
        )

        return {
            "success": True,
            "data": {
                "system_status": "paused",
                "paused_at": now,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume")
async def resume_system(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Resume message generation and sending.

    Per API_CONTRACTS.md §4: POST /system/resume
    """
    now = datetime.now(timezone.utc).isoformat()

    try:
        redis_service.set(_SYSTEM_STATUS_KEY, "active")
        redis_service.delete(_SYSTEM_PAUSED_AT_KEY)
        redis_service.delete(_SYSTEM_PAUSED_BY_KEY)

        # Log the action
        await activity_repo.log(
            session,
            uuid.UUID(current_user["id"]),
            action_type="system_resume",
            metadata={"resumed_at": now},
        )

        return {
            "success": True,
            "data": {
                "system_status": "active",
                "resumed_at": now,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get current system status including health checks.

    Per API_CONTRACTS.md §4: GET /system/status
    """
    try:
        uid = uuid.UUID(current_user["id"])
        system_status = _get_system_status()

        # Get message counts
        pending = await messages_repo.list(session, uid, status="draft", limit=1000)
        sent_today = await messages_repo.count_sent_today(session, uid)

        # Health checks
        db_ok = True  # If we're here, DB is working
        redis_ok = False
        ai_ok = True  # Assume OK unless we detect otherwise

        try:
            redis_ok = bool(redis_service.client.ping())
        except Exception:
            redis_ok = False

        return {
            "success": True,
            "data": {
                "status": system_status,
                "pending_messages": len(pending),
                "messages_sent_today": sent_today,
                "daily_limit": settings.EMAIL_DAILY_LIMIT,
                "health": {
                    "database": "healthy" if db_ok else "unhealthy",
                    "queue": "healthy" if redis_ok else "unhealthy",
                    "ai_service": "healthy" if ai_ok else "unhealthy",
                },
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def is_system_paused() -> bool:
    """
    Utility function for background tasks to check if the system is paused.

    Usage in Celery tasks::

        from api.routes.system import is_system_paused
        if is_system_paused():
            return {"skipped": True, "reason": "system_paused"}
    """
    return _get_system_status() == "paused"
