"""
Authentication package.

Exports the core dependencies used by all protected routes.
"""
from auth.dependencies import get_current_user, CurrentUser
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
)

__all__ = [
    "get_current_user",
    "CurrentUser",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "hash_password",
    "verify_password",
]
