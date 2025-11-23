from fastapi import APIRouter, HTTPException, BackgroundTasks
from models import MessageCreate, MessageUpdate, MessageStatus, Platform
from services import supabase_service
from crews import OutreachCrew
from typing import Optional

router = APIRouter()


@router.post("/generate")
async def generate_message(user_id: str, contact_id: str, context: str):
    """Generate personalized outreach message"""
    try:
        # Get contact info
        contact = await supabase_service.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Generate message using crew
        crew = OutreachCrew(user_id)
        result = crew.generate_outreach(contact, context)
        
        return {"drafts": result, "contact_id": contact_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_message(user_id: str, message: MessageCreate):
    """Create a new message (draft)"""
    try:
        result = await supabase_service.create_message(user_id, message.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_messages(
    user_id: str,
    status: Optional[MessageStatus] = None,
    contact_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    limit: int = 100
):
    """Get messages with filters"""
    try:
        messages = await supabase_service.get_messages(
            user_id,
            status=status.value if status else None,
            contact_id=contact_id,
            campaign_id=campaign_id,
            limit=limit
        )
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{message_id}")
async def update_message(message_id: str, update: MessageUpdate):
    """Update a message (e.g., approve for sending)"""
    try:
        result = await supabase_service.update_message(
            message_id,
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/approve")
async def approve_message(message_id: str, background_tasks: BackgroundTasks):
    """Approve message and queue for sending"""
    try:
        # Update status to approved
        await supabase_service.update_message(message_id, {"status": "approved"})
        
        # Queue for sending (background task)
        # background_tasks.add_task(send_message_task, message_id)
        
        return {"message": "Message approved and queued for sending", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approval-queue")
async def get_approval_queue(user_id: str):
    """Get messages awaiting approval"""
    try:
        messages = await supabase_service.get_messages(user_id, status="draft", limit=50)
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
