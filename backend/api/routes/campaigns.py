from fastapi import APIRouter, HTTPException, Depends
from models import CampaignCreate, CampaignUpdate, CampaignStatus
from db import campaigns_repo, messages_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from auth import get_current_user, CurrentUser

router = APIRouter()


@router.post("/")
async def create_campaign(
    campaign: CampaignCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Create a new campaign"""
    try:
        result = await campaigns_repo.create(session, uuid.UUID(current_user["id"]), campaign.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_campaigns(
    status: Optional[CampaignStatus] = None,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get campaigns"""
    try:
        campaigns = await campaigns_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            status=status.value if status else None
        )
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, update: CampaignUpdate, session: AsyncSession = Depends(get_db_session)):
    """Update a campaign"""
    try:
        result = await campaigns_repo.update(
            session,
            uuid.UUID(campaign_id),
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/metrics")
async def get_campaign_metrics(
    campaign_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get campaign performance metrics"""
    try:
        # Get all messages for campaign
        messages = await messages_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            campaign_id=uuid.UUID(campaign_id),
            limit=1000
        )
        
        total_sent = len([m for m in messages if m.get('status') in ['sent', 'opened', 'replied']])
        total_opened = len([m for m in messages if m.get('status') in ['opened', 'replied']])
        total_replied = len([m for m in messages if m.get('status') == 'replied'])
        
        avg_personalization = sum(m.get('personalization_score', 0) for m in messages) / len(messages) if messages else 0
        
        return {
            "campaign_id": campaign_id,
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_replied": total_replied,
            "open_rate": (total_opened / total_sent * 100) if total_sent > 0 else 0,
            "response_rate": (total_replied / total_sent * 100) if total_sent > 0 else 0,
            "avg_personalization_score": round(avg_personalization, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
