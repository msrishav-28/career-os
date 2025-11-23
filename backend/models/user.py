from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, Dict, List
from datetime import datetime


class UserProfile(BaseModel):
    """User profile data structure"""
    skills: List[str]
    projects: List[Dict[str, str]]  # {name, description, tech_stack, url}
    experiences: List[Dict[str, str]]  # {title, company, duration, description}
    education: List[Dict[str, str]]  # {institution, degree, year, achievements}
    goals: List[Dict[str, str]]  # {goal, priority, deadline}
    interests: List[str]
    achievements: List[str]


class UserSettings(BaseModel):
    """User-specific settings"""
    linkedin_daily_limit: int = 15
    email_daily_limit: int = 50
    auto_approve_score_threshold: int = 85
    notification_email: Optional[str] = None
    notification_preferences: Dict[str, bool] = {
        "email_digest": True,
        "slack_notifications": False,
        "response_alerts": True
    }
    active_campaigns: List[str] = []


class User(BaseModel):
    """User model"""
    id: Optional[UUID4] = None
    email: EmailStr
    created_at: Optional[datetime] = None
    profile_data: Optional[UserProfile] = None
    settings: Optional[UserSettings] = UserSettings()
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    profile_data: Optional[UserProfile] = None
    settings: Optional[UserSettings] = None


class UserInDB(User):
    """User in database with hashed password"""
    hashed_password: str
