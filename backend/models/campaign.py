from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class CampaignType(str, Enum):
    """Type of campaign"""
    CAREER = "career"
    BETA_ACQUISITION = "beta_acquisition"
    VALIDATION = "validation"
    PARTNERSHIP = "partnership"


class CampaignStatus(str, Enum):
    """Campaign status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(BaseModel):
    """Campaign model"""
    id: Optional[UUID4] = None
    user_id: UUID4
    name: str
    campaign_type: CampaignType
    target_persona: Optional[str] = None  # "ML hiring managers", "students", etc.
    status: CampaignStatus = CampaignStatus.ACTIVE
    metadata: Dict = {}
    created_at: Optional[datetime] = None
    
    # Campaign settings
    daily_outreach_limit: int = 10
    min_personalization_score: int = 70
    
    # Metrics
    total_sent: int = 0
    total_responses: int = 0
    total_conversions: int = 0
    
    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    """Campaign creation schema"""
    name: str
    campaign_type: CampaignType
    target_persona: Optional[str] = None
    metadata: Dict = {}
    daily_outreach_limit: int = 10
    min_personalization_score: int = 70


class CampaignUpdate(BaseModel):
    """Campaign update schema"""
    name: Optional[str] = None
    status: Optional[CampaignStatus] = None
    target_persona: Optional[str] = None
    metadata: Optional[Dict] = None
    daily_outreach_limit: Optional[int] = None


class CampaignMetrics(BaseModel):
    """Campaign metrics"""
    campaign_id: UUID4
    campaign_name: str
    total_sent: int
    total_responses: int
    total_conversions: int
    response_rate: float
    conversion_rate: float
    avg_personalization_score: float
