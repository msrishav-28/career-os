from fastapi import APIRouter, HTTPException, Query, Depends
from models import ContactCreate, ContactUpdate, ContactStatus, ContactType
from db import contacts_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from auth import get_current_user, CurrentUser

router = APIRouter()


@router.post("/")
async def create_contact(
    contact: ContactCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new contact"""
    try:
        result = await contacts_repo.create(session, uuid.UUID(current_user["id"]), contact.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_contacts(
    status: Optional[ContactStatus] = None,
    contact_type: Optional[ContactType] = None,
    limit: int = Query(100, le=500),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get contacts with optional filters"""
    try:
        contacts = await contacts_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            status=status.value if status else None,
            contact_type=contact_type.value if contact_type else None,
            limit=limit
        )
        return {"contacts": contacts, "count": len(contacts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}")
async def get_contact(contact_id: str, session: AsyncSession = Depends(get_db_session)):
    """Get a single contact by ID"""
    try:
        contact = await contacts_repo.get(session, uuid.UUID(contact_id))
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}")
async def update_contact(contact_id: str, update: ContactUpdate, session: AsyncSession = Depends(get_db_session)):
    """Update a contact"""
    try:
        result = await contacts_repo.update(
            session,
            uuid.UUID(contact_id),
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/summary")
async def get_pipeline_summary(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get contact pipeline summary (count by status)"""
    try:
        all_contacts = await contacts_repo.list(session, uuid.UUID(current_user["id"]), limit=1000)
        
        summary = {}
        for status in ContactStatus:
            summary[status.value] = len([c for c in all_contacts if c.get('status') == status.value])
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
