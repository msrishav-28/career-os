"""
Rate limiting middleware for FastAPI.

Returns a FastAPI dependency factory that enforces per-user rate limits
using the RedisService already built in services/redis_service.py.
"""
from fastapi import HTTPException, Request, Depends, status
from typing import Optional
from auth.dependencies import get_current_user, CurrentUser


def rate_limit(
    action: str,
    max_per_minute: int = 60,
    window_seconds: int = 60,
):
    """
    FastAPI dependency factory for rate limiting.

    Usage::

        @router.post("/generate")
        async def generate(
            ...,
            _: None = Depends(rate_limit("message_generate", 10)),
        ):
            ...

    Args:
        action: Identifier for the rate-limited action.
        max_per_minute: Maximum requests allowed in the window.
        window_seconds: Window size in seconds (default: 60).
    """

    async def _check_rate(
        request: Request,
        current_user: CurrentUser = Depends(get_current_user),
    ) -> None:
        try:
            from services.redis_service import redis_service

            user_id = current_user["id"]
            allowed, current_count = redis_service.check_rate_limit(
                user_id=user_id,
                action_type=action,
                limit=max_per_minute,
                window_seconds=window_seconds,
            )

            # Set rate-limit headers on the response
            # (accessible via request.state for middleware)
            request.state.rate_limit_remaining = max(0, max_per_minute - current_count)
            request.state.rate_limit_limit = max_per_minute

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Too many requests. Limit: {max_per_minute} per {window_seconds}s.",
                            "retry_after": window_seconds,
                        },
                    },
                    headers={
                        "Retry-After": str(window_seconds),
                        "X-RateLimit-Limit": str(max_per_minute),
                        "X-RateLimit-Remaining": "0",
                    },
                )
        except HTTPException:
            raise
        except Exception:
            # If Redis is down, allow the request (fail-open)
            pass

    return _check_rate
