from pydantic import BaseModel, UUID4, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ContactType(str, Enum):
    """Type of contact"""
    CAREER = "career"
    RESEARCHER = "researcher"
    BETA_USER = "beta_user"
    PARTNERSHIP = "partnership"
    VALIDATION = "validation"


class ContactStatus(str, Enum):
    """Contact status in pipeline"""
    DISCOVERED = "discovered"
    TO_CONTACT = "to_contact"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    IN_CONVERSATION = "in_conversation"
    CONVERTED = "converted"
    INACTIVE = "inactive"


class Contact(BaseModel):
    """Contact model"""
    id: Optional[UUID4] = None
    user_id: UUID4
    name: str
    email: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = None
    github_username: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    lab_url: Optional[HttpUrl] = None  # For researchers: lab website
    research_areas: List[str] = []  # For researchers: research interests
    publications: List[Dict] = []  # For researchers: recent publications
    tags: List[str] = []
    source: Optional[str] = None  # "linkedin_search", "github_contributor", etc.
    contact_type: ContactType = ContactType.CAREER
    status: ContactStatus = ContactStatus.DISCOVERED
    quality_score: int = 5  # 1-10
    metadata: Dict = {}  # Flexible additional data
    created_at: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContactCreate(BaseModel):
    """Contact creation schema"""
    name: str
    email: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = None
    github_username: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    lab_url: Optional[HttpUrl] = None
    research_areas: List[str] = []
    publications: List[Dict] = []
    tags: List[str] = []
    source: Optional[str] = None
    contact_type: ContactType = ContactType.CAREER
    quality_score: int = 5
    metadata: Dict = {}


class ContactUpdate(BaseModel):
    """Contact update schema"""
    name: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    company: Optional[str] = None
    title: Optional[str] = None
    lab_url: Optional[HttpUrl] = None
    research_areas: Optional[List[str]] = None
    publications: Optional[List[Dict]] = None
    tags: Optional[List[str]] = None
    status: Optional[ContactStatus] = None
    quality_score: Optional[int] = None
    metadata: Optional[Dict] = None


class ContactFilter(BaseModel):
    """Filter criteria for contacts"""
    status: Optional[ContactStatus] = None
    contact_type: Optional[ContactType] = None
    tags: Optional[List[str]] = None
    min_quality_score: Optional[int] = None
    company: Optional[str] = None
