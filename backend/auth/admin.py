"""
Admin authentication guard.

Used by ``tasks.py`` router for administrative endpoints like
triggering scheduled tasks.
"""
from fastapi import Depends, HTTPException, status
from auth.dependencies import get_current_user, CurrentUser
from config.settings import settings


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Dependency that ensures the current user is an admin.

    Admin emails are configured via the ADMIN_EMAILS environment variable
    (comma-separated list).

    Raises:
        HTTPException 403 if user is not an admin.
    """
    admin_emails = {
        email.strip().lower()
        for email in (settings.ADMIN_EMAILS or "").split(",")
        if email.strip()
    }

    user_email = (current_user.get("email") or "").lower()

    if not admin_emails or user_email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user
