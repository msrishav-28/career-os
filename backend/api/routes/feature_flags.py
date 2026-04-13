"""
Feature flags API route.

Per MIGRATION_ROLLOUT_PLAN.md §Feature Flags — provides a frontend-facing
endpoint for SWR/React to check flag status.
"""
from fastapi import APIRouter, Depends
from auth import get_current_user, CurrentUser
from services.feature_flags import feature_flags

router = APIRouter()


@router.get("/{flag_name}")
async def get_flag(
    flag_name: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Check if a feature flag is enabled for the current user.

    Used by frontend:
        const { data } = useSWR('/api/feature-flags/quantum_ui', fetcher);
    """
    enabled = feature_flags.is_enabled(flag_name, current_user["id"])
    return {"flag": flag_name, "enabled": enabled}


@router.get("/")
async def get_all_flags(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get all feature flag statuses for the current user."""
    all_flags = feature_flags.get_all_flags()
    result = {}
    for flag_name in all_flags:
        result[flag_name] = feature_flags.is_enabled(flag_name, current_user["id"])
    return {"flags": result}
