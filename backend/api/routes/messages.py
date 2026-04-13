"""
Message management API routes.

Implements every endpoint from API_CONTRACTS.md §2 (Message Approval Flow):
  - POST /messages/generate        — Generate outreach message
  - POST /messages/                — Create a message draft
  - GET  /messages/                — List messages with filters
  - PUT  /messages/{id}            — Update a message
  - POST /messages/{id}/approve    — Approve message for sending
  - POST /messages/{id}/reject     — Reject a message draft
  - POST /messages/{id}/regenerate — Regenerate a message draft
  - POST /messages/bulk-approve    — Bulk approve multiple messages
  - GET  /messages/pending         — Get pending drafts (API_CONTRACTS format)
  - GET  /messages/approval-queue  — Get approval queue
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from models import MessageCreate, MessageUpdate, MessageStatus, Platform
from db import contacts_repo, messages_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from crews import OutreachCrew
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from auth import get_current_user, CurrentUser
from security.rate_limit import rate_limit

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ApproveRequest(BaseModel):
    schedule: Optional[str] = "immediate"  # "immediate" | ISO timestamp
    edits: Optional[dict] = None  # {"subject": ..., "body": ...}


class RejectRequest(BaseModel):
    reason: Optional[str] = None  # "too_generic", "too_long", etc.
    feedback: Optional[str] = None


class BulkApproveRequest(BaseModel):
    message_ids: List[str]
    schedule: Optional[str] = "immediate"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/generate")
async def generate_message(
    contact_id: str,
    context: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit("message_generate", 60)),
):
    """Generate personalized outreach message."""
    try:
        contact = await contacts_repo.get(session, uuid.UUID(contact_id))
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

        crew = OutreachCrew(current_user["id"])
        result = crew.generate_outreach(contact, context)

        return {"success": True, "data": {"drafts": result, "contact_id": contact_id}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_message(
    message: MessageCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new message (draft)."""
    try:
        result = await messages_repo.create(
            session, uuid.UUID(current_user["id"]), message.dict()
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_messages(
    status: Optional[MessageStatus] = None,
    contact_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get messages with filters."""
    try:
        messages = await messages_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            status=status.value if status else None,
            contact_id=uuid.UUID(contact_id) if contact_id else None,
            campaign_id=uuid.UUID(campaign_id) if campaign_id else None,
            limit=limit,
        )
        return {"success": True, "data": {"messages": messages, "count": len(messages)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_messages(
    limit: int = 5,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Get pending message drafts for approval.

    Per API_CONTRACTS.md §2: GET /messages/pending
    Returns drafts with contact info in the exact format documented.
    """
    try:
        drafts = await messages_repo.get_pending_drafts(
            session, uuid.UUID(current_user["id"]), limit=min(limit, 20), offset=offset
        )
        # Get total count for pagination
        all_counts = await messages_repo.count_by_status(
            session, uuid.UUID(current_user["id"])
        )
        total = all_counts.get("draft", 0)

        return {
            "success": True,
            "data": {
                "drafts": drafts,
                "total": total,
                "has_more": (offset + limit) < total,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{message_id}")
async def update_message(
    message_id: str,
    update: MessageUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update a message."""
    try:
        result = await messages_repo.update(
            session,
            uuid.UUID(message_id),
            {k: v for k, v in update.dict().items() if v is not None},
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/approve")
async def approve_message(
    message_id: str,
    body: ApproveRequest = ApproveRequest(),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Approve a message draft for sending.

    Per API_CONTRACTS.md §2: POST /messages/{message_id}/approve
    Supports optional edits and scheduling.
    """
    try:
        # Apply edits if provided
        update_data = {"status": "approved"}
        if body.edits:
            if "subject" in body.edits:
                update_data["subject"] = body.edits["subject"]
            if "body" in body.edits:
                update_data["body"] = body.edits["body"]

        await messages_repo.update(session, uuid.UUID(message_id), update_data)

        # Dispatch webhook event
        try:
            from api.routes.webhooks import dispatch_webhook_event
            await dispatch_webhook_event(
                session,
                current_user["id"],
                "message.approved",
                {"message_id": message_id, "approved_at": datetime.now(timezone.utc).isoformat()},
            )
        except Exception:
            pass  # Don't fail approval if webhook dispatch fails

        scheduled_at = body.schedule if body.schedule != "immediate" else datetime.now(timezone.utc).isoformat()

        return {
            "success": True,
            "data": {
                "message": {
                    "id": message_id,
                    "status": "approved",
                    "scheduled_at": scheduled_at,
                },
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/reject")
async def reject_message(
    message_id: str,
    body: RejectRequest = RejectRequest(),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Reject a message draft.

    Per API_CONTRACTS.md §2: POST /messages/{message_id}/reject
    """
    try:
        update_data = {"status": "rejected"}
        if body.reason or body.feedback:
            import json
            update_data["metadata"] = json.dumps({
                "rejection_reason": body.reason,
                "rejection_feedback": body.feedback,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
            })

        await messages_repo.update(session, uuid.UUID(message_id), update_data)

        return {
            "success": True,
            "data": {
                "message_id": message_id,
                "status": "rejected",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/regenerate")
async def regenerate_message(
    message_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit("message_regenerate", 30)),
):
    """
    Request regeneration of a message draft.

    Per API_CONTRACTS.md §2: POST /messages/{message_id}/regenerate
    Creates a new draft using the same contact/campaign context.
    """
    try:
        # Get original message
        original = await messages_repo.get(session, uuid.UUID(message_id))
        if not original:
            raise HTTPException(status_code=404, detail="Message not found")

        # Mark original as rejected
        await messages_repo.update(
            session, uuid.UUID(message_id), {"status": "rejected"}
        )

        # Create new draft placeholder
        new_msg = await messages_repo.create(
            session,
            uuid.UUID(current_user["id"]),
            {
                "contact_id": str(original.get("contact_id", "")),
                "campaign_id": str(original.get("campaign_id", "")) if original.get("campaign_id") else None,
                "platform": original.get("platform", "email"),
                "subject": "",
                "body": "Regenerating...",
                "status": "draft",
            },
        )

        # Queue regeneration as a background task
        contact_id = str(original.get("contact_id", ""))
        context = f"Regeneration of message about: {original.get('subject', 'outreach')}"

        try:
            from tasks.agent_tasks import generate_outreach_async
            generate_outreach_async.delay(current_user["id"], contact_id, context)
        except Exception:
            pass  # Celery may not be running in dev

        return {
            "success": True,
            "data": {
                "new_message_id": str(new_msg.get("id", "")),
                "status": "generating",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-approve")
async def bulk_approve_messages(
    body: BulkApproveRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Approve multiple messages at once.

    Per API_CONTRACTS.md §2: POST /messages/bulk-approve
    """
    try:
        approved = await messages_repo.bulk_update_status(
            session, body.message_ids, "approved"
        )

        # Dispatch webhook for each approved message
        try:
            from api.routes.webhooks import dispatch_webhook_event
            for mid in body.message_ids:
                await dispatch_webhook_event(
                    session,
                    current_user["id"],
                    "message.approved",
                    {"message_id": mid},
                )
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "approved": approved,
                "failed": len(body.message_ids) - approved,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approval-queue")
async def get_approval_queue(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get messages awaiting approval."""
    try:
        messages = await messages_repo.list(
            session, uuid.UUID(current_user["id"]), status="draft", limit=50
        )
        return {"success": True, "data": {"messages": messages, "count": len(messages)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
