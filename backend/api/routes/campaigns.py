from fastapi import APIRouter, HTTPException
from models import CampaignCreate, CampaignUpdate, CampaignStatus
from services import supabase_service
from typing import Optional

router = APIRouter()


@router.post("/")
async def create_campaign(user_id: str, campaign: CampaignCreate):
    """Create a new campaign"""
    try:
        result = await supabase_service.create_campaign(user_id, campaign.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_campaigns(user_id: str, status: Optional[CampaignStatus] = None):
    """Get campaigns"""
    try:
        campaigns = await supabase_service.get_campaigns(
            user_id,
            status=status.value if status else None
        )
        return {"campaigns": campaigns, "count": len(campaigns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, update: CampaignUpdate):
    """Update a campaign"""
    try:
        result = await supabase_service.update_campaign(
            campaign_id,
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/metrics")
async def get_campaign_metrics(campaign_id: str, user_id: str):
    """Get campaign performance metrics"""
    try:
        # Get all messages for campaign
        messages = await supabase_service.get_messages(
            user_id,
            campaign_id=campaign_id,
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
