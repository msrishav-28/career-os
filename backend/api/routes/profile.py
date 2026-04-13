from fastapi import APIRouter, HTTPException, Depends
from models import UserProfile, UserSettings
from services import vector_service
from db import users_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
import uuid
from auth import get_current_user, CurrentUser

router = APIRouter()


@router.post("/store")
async def store_profile(
    profile: UserProfile,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Store user profile in vector database"""
    try:
        vector_service.store_user_profile(current_user["id"], profile.dict())
        
        await users_repo.update(session, uuid.UUID(current_user["id"]), {"profile_data": profile.dict()})
        
        return {"message": "Profile stored successfully", "user_id": current_user["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
async def query_profile(
    query: str,
    n_results: int = 5,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Query user profile memory"""
    try:
        results = vector_service.query_user_profile(current_user["id"], query, n_results)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_profile(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get user profile"""
    try:
        user = await users_repo.get_by_id(session, uuid.UUID(current_user["id"]))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_settings(
    settings: UserSettings,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Update user settings"""
    try:
        await users_repo.update(session, uuid.UUID(current_user["id"]), {"settings": settings.dict()})
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
