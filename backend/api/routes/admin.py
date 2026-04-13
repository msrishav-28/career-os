"""
Admin API routes.

Per OPERATIONAL_RUNBOOK.md — feature flag management via admin endpoints:
  - POST /admin/feature-flags/enable
  - POST /admin/feature-flags/disable
  - GET  /admin/feature-flags
  - POST /admin/sync-chromadb  — trigger data sync
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user, CurrentUser
from auth.admin import require_admin
from services.feature_flags import feature_flags

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class FlagToggleRequest(BaseModel):
    flag: str
    percentage: Optional[int] = 100


class FlagOverrideRequest(BaseModel):
    flag: str
    user_id: str
    enabled: bool


# ---------------------------------------------------------------------------
# Feature flag management
# ---------------------------------------------------------------------------
@router.get("/feature-flags")
async def list_flags(
    _admin: CurrentUser = Depends(require_admin),
):
    """List all feature flags and their configurations."""
    return {"success": True, "data": feature_flags.get_all_flags()}


@router.post("/feature-flags/enable")
async def enable_flag(
    body: FlagToggleRequest,
    _admin: CurrentUser = Depends(require_admin),
):
    """Enable a feature flag at a given rollout percentage."""
    feature_flags.enable(body.flag, body.percentage or 100)
    return {"success": True, "data": {"flag": body.flag, "enabled": True, "percentage": body.percentage}}


@router.post("/feature-flags/disable")
async def disable_flag(
    body: FlagToggleRequest,
    _admin: CurrentUser = Depends(require_admin),
):
    """Disable a feature flag immediately."""
    feature_flags.disable(body.flag)
    return {"success": True, "data": {"flag": body.flag, "enabled": False}}


@router.post("/feature-flags/override")
async def set_flag_override(
    body: FlagOverrideRequest,
    _admin: CurrentUser = Depends(require_admin),
):
    """Set a per-user override for a feature flag."""
    feature_flags.set_override(body.flag, body.user_id, body.enabled)
    return {"success": True, "data": {"flag": body.flag, "user_id": body.user_id, "enabled": body.enabled}}


# ---------------------------------------------------------------------------
# Operational tools
# ---------------------------------------------------------------------------
@router.post("/sync-chromadb")
async def trigger_sync(
    _admin: CurrentUser = Depends(require_admin),
):
    """
    Trigger a ChromaDB sync job.
    Per OPERATIONAL_RUNBOOK.md §5 — ChromaDB Out of Sync.
    """
    try:
        from tasks.scheduled_tasks import sync_chromadb_task
        result = sync_chromadb_task.delay()
        return {"success": True, "data": {"task_id": str(result.id), "status": "queued"}}
    except Exception as e:
        return {"success": False, "error": {"code": "SYNC_FAILED", "message": str(e)}}
