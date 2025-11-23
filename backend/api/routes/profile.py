from fastapi import APIRouter, HTTPException
from models import UserProfile, UserSettings
from services import chroma_service, supabase_service
from typing import Dict

router = APIRouter()


@router.post("/store")
async def store_profile(user_id: str, profile: UserProfile):
    """Store user profile in vector database"""
    try:
        chroma_service.store_user_profile(user_id, profile.dict())
        
        # Also update in Supabase
        await supabase_service.update_user(user_id, {"profile_data": profile.dict()})
        
        return {"message": "Profile stored successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
async def query_profile(user_id: str, query: str, n_results: int = 5):
    """Query user profile memory"""
    try:
        results = chroma_service.query_user_profile(user_id, query, n_results)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_profile(user_id: str):
    """Get user profile"""
    try:
        user = await supabase_service.get_user_by_email(user_id)  # Simplified
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings")
async def update_settings(user_id: str, settings: UserSettings):
    """Update user settings"""
    try:
        await supabase_service.update_user(user_id, {"settings": settings.dict()})
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
