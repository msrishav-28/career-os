"""
Webhook API routes.

Implements webhook management from API_CONTRACTS.md §5:
  - POST /webhooks           — Register a webhook endpoint
  - GET  /webhooks           — List registered webhooks
  - DELETE /webhooks/{id}    — Remove a webhook
  - POST /webhooks/{id}/test — Test a webhook with sample payload
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import uuid
import json
import hashlib
import hmac
import aiohttp
from datetime import datetime, timezone

from db.session import get_db_session
from sqlalchemy import text
from auth import get_current_user, CurrentUser

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class WebhookCreate(BaseModel):
    url: HttpUrl
    event_types: List[str] = ["message.approved", "message.sent", "contact.created"]
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    event_types: List[str]
    is_active: bool
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/")
async def register_webhook(
    webhook: WebhookCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Register a new webhook endpoint."""
    # Generate a signing secret if not provided
    secret = webhook.secret or hashlib.sha256(
        f"{current_user['id']}:{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:32]

    query = text(
        "INSERT INTO webhook_endpoints (user_id, url, event_types, secret) "
        "VALUES (:user_id, :url, :event_types, :secret) RETURNING *"
    )
    result = await session.execute(query, {
        "user_id": current_user["id"],
        "url": str(webhook.url),
        "event_types": webhook.event_types,
        "secret": secret,
    })
    row = result.mappings().first()

    return {
        "success": True,
        "data": {
            "id": str(row["id"]),
            "url": row["url"],
            "event_types": row["event_types"],
            "secret": secret,
            "is_active": row["is_active"],
        },
    }


@router.get("/")
async def list_webhooks(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """List all registered webhooks for the current user."""
    query = text(
        "SELECT * FROM webhook_endpoints WHERE user_id = :user_id "
        "ORDER BY created_at DESC"
    )
    result = await session.execute(query, {"user_id": current_user["id"]})
    rows = result.mappings().all()

    return {
        "success": True,
        "data": [
            {
                "id": str(row["id"]),
                "url": row["url"],
                "event_types": row["event_types"],
                "is_active": row["is_active"],
                "created_at": str(row["created_at"]) if row.get("created_at") else None,
            }
            for row in rows
        ],
    }


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Delete a webhook endpoint."""
    query = text(
        "DELETE FROM webhook_endpoints WHERE id = :id AND user_id = :user_id"
    )
    result = await session.execute(query, {
        "id": webhook_id,
        "user_id": current_user["id"],
    })

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return {"success": True, "data": {"deleted": True}}


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Test a webhook with a sample payload."""
    query = text(
        "SELECT * FROM webhook_endpoints WHERE id = :id AND user_id = :user_id"
    )
    result = await session.execute(query, {
        "id": webhook_id,
        "user_id": current_user["id"],
    })
    row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Build test payload
    test_payload = {
        "event": "webhook.test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "message": "This is a test webhook payload from CareerOS",
            "webhook_id": str(row["id"]),
        },
    }

    # Sign the payload
    payload_bytes = json.dumps(test_payload).encode()
    signature = hmac.new(
        (row["secret"] or "").encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    # Send test request
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                row["url"],
                json=test_payload,
                headers={
                    "X-CareerOS-Signature": signature,
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                return {
                    "success": True,
                    "data": {
                        "status_code": response.status,
                        "response_body": await response.text(),
                    },
                }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "WEBHOOK_DELIVERY_FAILED",
                "message": str(e),
            },
        }


# ---------------------------------------------------------------------------
# Internal helper for dispatching webhooks
# ---------------------------------------------------------------------------
async def dispatch_webhook_event(
    session: AsyncSession,
    user_id: str,
    event_type: str,
    payload: dict,
):
    """
    Dispatch an event to all active webhooks registered for that event type.

    Called internally by route handlers and background tasks.
    """
    query = text(
        "SELECT * FROM webhook_endpoints "
        "WHERE user_id = :user_id AND is_active = true "
        "AND :event_type = ANY(event_types)"
    )
    result = await session.execute(query, {
        "user_id": user_id,
        "event_type": event_type,
    })
    webhooks = result.mappings().all()

    for webhook in webhooks:
        full_payload = {
            "event": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }
        payload_bytes = json.dumps(full_payload).encode()
        signature = hmac.new(
            (webhook["secret"] or "").encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        try:
            async with aiohttp.ClientSession() as http_session:
                async with http_session.post(
                    webhook["url"],
                    json=full_payload,
                    headers={
                        "X-CareerOS-Signature": signature,
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    # Update last_triggered_at
                    await session.execute(
                        text("UPDATE webhook_endpoints SET last_triggered_at = :now WHERE id = :id"),
                        {"now": datetime.now(timezone.utc).isoformat(), "id": str(webhook["id"])},
                    )
        except Exception:
            # Webhook delivery failure — log but don't block
            pass
