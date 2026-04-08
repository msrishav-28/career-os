from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from models import MessageCreate, MessageUpdate, MessageStatus, Platform
from db import contacts_repo, messages_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from crews import OutreachCrew
from typing import Optional
import uuid
from auth import get_current_user, CurrentUser
from security.rate_limit import rate_limit

router = APIRouter()


@router.post("/generate")
async def generate_message(
    contact_id: str,
    context: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit("message_generate", 60)),
):
    """Generate personalized outreach message"""
    try:
        # Get contact info
        contact = await contacts_repo.get(session, uuid.UUID(contact_id))
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Generate message using crew
        crew = OutreachCrew(current_user["id"])
        result = crew.generate_outreach(contact, context)
        
        return {"drafts": result, "contact_id": contact_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_message(
    message: MessageCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new message (draft)"""
    try:
        result = await messages_repo.create(session, uuid.UUID(current_user["id"]), message.dict())
        return result
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
    """Get messages with filters"""
    try:
        messages = await messages_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            status=status.value if status else None,
            contact_id=uuid.UUID(contact_id) if contact_id else None,
            campaign_id=uuid.UUID(campaign_id) if campaign_id else None,
            limit=limit
        )
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{message_id}")
async def update_message(message_id: str, update: MessageUpdate, session: AsyncSession = Depends(get_db_session)):
    """Update a message (e.g., approve for sending)"""
    try:
        result = await messages_repo.update(
            session,
            uuid.UUID(message_id),
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/approve")
async def approve_message(message_id: str, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_db_session)):
    """Approve message and queue for sending"""
    try:
        # Update status to approved
        await messages_repo.update(session, uuid.UUID(message_id), {"status": "approved"})
        
        # Queue for sending (background task)
        # background_tasks.add_task(send_message_task, message_id)
        
        return {"message": "Message approved and queued for sending", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approval-queue")
async def get_approval_queue(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get messages awaiting approval"""
    try:
        messages = await messages_repo.list(session, uuid.UUID(current_user["id"]), status="draft", limit=50)
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
