from fastapi import APIRouter, HTTPException, Query
from models import ContactCreate, ContactUpdate, ContactStatus, ContactType
from services import supabase_service
from typing import List, Optional

router = APIRouter()


@router.post("/")
async def create_contact(user_id: str, contact: ContactCreate):
    """Create a new contact"""
    try:
        result = await supabase_service.create_contact(user_id, contact.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_contacts(
    user_id: str,
    status: Optional[ContactStatus] = None,
    contact_type: Optional[ContactType] = None,
    limit: int = Query(100, le=500)
):
    """Get contacts with optional filters"""
    try:
        contacts = await supabase_service.get_contacts(
            user_id,
            status=status.value if status else None,
            contact_type=contact_type.value if contact_type else None,
            limit=limit
        )
        return {"contacts": contacts, "count": len(contacts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}")
async def get_contact(contact_id: str):
    """Get a single contact by ID"""
    try:
        contact = await supabase_service.get_contact_by_id(contact_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}")
async def update_contact(contact_id: str, update: ContactUpdate):
    """Update a contact"""
    try:
        result = await supabase_service.update_contact(
            contact_id,
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/summary")
async def get_pipeline_summary(user_id: str):
    """Get contact pipeline summary (count by status)"""
    try:
        all_contacts = await supabase_service.get_contacts(user_id, limit=1000)
        
        summary = {}
        for status in ContactStatus:
            summary[status.value] = len([c for c in all_contacts if c.get('status') == status.value])
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
