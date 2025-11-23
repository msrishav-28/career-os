from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    """Message platform"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class MessageStatus(str, Enum):
    """Message status"""
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    REJECTED = "rejected"


class Sentiment(str, Enum):
    """Reply sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Message(BaseModel):
    """Message model"""
    id: Optional[UUID4] = None
    user_id: UUID4
    contact_id: UUID4
    campaign_id: Optional[UUID4] = None
    platform: Platform
    subject: Optional[str] = None
    body: str
    personalization_score: int = 0  # 0-100
    status: MessageStatus = MessageStatus.DRAFT
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    reply_content: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    metadata: Dict = {}
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Message creation schema"""
    contact_id: UUID4
    campaign_id: Optional[UUID4] = None
    platform: Platform
    subject: Optional[str] = None
    body: str
    personalization_score: int = 0


class MessageUpdate(BaseModel):
    """Message update schema"""
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[MessageStatus] = None
    personalization_score: Optional[int] = None


class MessageDraft(BaseModel):
    """Message draft with multiple versions"""
    contact_name: str
    contact_info: Dict
    drafts: List[Dict[str, any]]  # Multiple versions with scores
    recommended_draft_index: int
    reasoning: str
