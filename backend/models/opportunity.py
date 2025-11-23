from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class OpportunityType(str, Enum):
    """Type of opportunity"""
    INTERNSHIP = "internship"
    JOB = "job"
    PARTNERSHIP = "partnership"
    SPEAKING = "speaking"
    HACKATHON = "hackathon"
    RESEARCH = "research"


class OpportunityStatus(str, Enum):
    """Opportunity status"""
    DISCOVERED = "discovered"
    RESEARCHING = "researching"
    READY_TO_APPLY = "ready_to_apply"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Opportunity(BaseModel):
    """Opportunity model"""
    id: Optional[UUID4] = None
    user_id: UUID4
    title: str
    company: Optional[str] = None
    url: Optional[HttpUrl] = None
    opportunity_type: OpportunityType
    description: Optional[str] = None
    requirements: List[str] = []
    match_score: int = 0  # 1-10 based on profile fit
    status: OpportunityStatus = OpportunityStatus.DISCOVERED
    source: Optional[str] = None  # "linkedin_scrape", "manual_add", etc.
    discovered_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    metadata: Dict = {}
    hiring_manager: Optional[Dict] = None  # {name, linkedin, email}
    
    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    """Opportunity creation schema"""
    title: str
    company: Optional[str] = None
    url: Optional[HttpUrl] = None
    opportunity_type: OpportunityType
    description: Optional[str] = None
    requirements: List[str] = []
    source: Optional[str] = None
    deadline: Optional[datetime] = None
    metadata: Dict = {}


class OpportunityUpdate(BaseModel):
    """Opportunity update schema"""
    status: Optional[OpportunityStatus] = None
    match_score: Optional[int] = None
    metadata: Optional[Dict] = None
    hiring_manager: Optional[Dict] = None


class OpportunityFilter(BaseModel):
    """Filter criteria for opportunities"""
    status: Optional[OpportunityStatus] = None
    opportunity_type: Optional[OpportunityType] = None
    min_match_score: Optional[int] = None
    company: Optional[str] = None
