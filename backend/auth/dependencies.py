"""
FastAPI authentication dependencies.

Provides ``get_current_user`` — the core dependency used by every protected route.
Supports both:
  - Authorization: Bearer <JWT> header
  - next-auth.session-token cookie (for frontend integration per API.md)
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Any, Dict, Optional
from auth.jwt import verify_token

# Type alias used across all routes
CurrentUser = Dict[str, Any]

# Optional bearer — allows cookie fallback
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> CurrentUser:
    """
    Extract and validate the current user from the request.

    Resolution order:
    1. Authorization: Bearer <token> header
    2. next-auth.session-token cookie
    3. __Secure-next-auth.session-token cookie (production)

    Returns a dict with at minimum {"id": ..., "email": ...}.

    Raises:
        HTTPException 401 if no valid token found.
    """
    token: Optional[str] = None

    # 1. Try Bearer header
    if credentials and credentials.credentials:
        token = credentials.credentials

    # 2. Try cookies (NextAuth integration per API.md)
    if not token:
        token = request.cookies.get("next-auth.session-token")
    if not token:
        token = request.cookies.get("__Secure-next-auth.session-token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier",
        )

    return {
        "id": user_id,
        "email": payload.get("email", ""),
        "token_payload": payload,
    }
