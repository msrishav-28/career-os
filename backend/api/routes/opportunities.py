from fastapi import APIRouter, HTTPException, BackgroundTasks
from models import OpportunityCreate, OpportunityUpdate, OpportunityStatus, OpportunityType
from services import supabase_service
from crews import DiscoveryCrew
from typing import Optional

router = APIRouter()


@router.post("/discover")
async def discover_opportunities(
    user_id: str,
    keywords: str = "AI ML internship",
    location: str = "India",
    opportunity_type: str = "internship"
):
    """Discover new opportunities using AI agents"""
    try:
        crew = DiscoveryCrew(user_id)
        search_params = {
            "keywords": keywords,
            "location": location,
            "type": opportunity_type
        }
        
        result = crew.discover_opportunities(search_params)
        
        return {"opportunities": result, "search_params": search_params}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_opportunity(user_id: str, opportunity: OpportunityCreate):
    """Manually create an opportunity"""
    try:
        result = await supabase_service.create_opportunity(user_id, opportunity.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_opportunities(
    user_id: str,
    status: Optional[OpportunityStatus] = None,
    opportunity_type: Optional[OpportunityType] = None,
    min_match_score: Optional[int] = None,
    limit: int = 100
):
    """Get opportunities with filters"""
    try:
        opportunities = await supabase_service.get_opportunities(
            user_id,
            status=status.value if status else None,
            opportunity_type=opportunity_type.value if opportunity_type else None,
            min_match_score=min_match_score,
            limit=limit
        )
        return {"opportunities": opportunities, "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{opportunity_id}")
async def update_opportunity(opportunity_id: str, update: OpportunityUpdate):
    """Update an opportunity"""
    try:
        result = await supabase_service.update_opportunity(
            opportunity_id,
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top")
async def get_top_opportunities(user_id: str, limit: int = 10):
    """Get top opportunities by match score"""
    try:
        opportunities = await supabase_service.get_opportunities(
            user_id,
            min_match_score=7,
            limit=limit
        )
        # Sort by match score
        sorted_opps = sorted(opportunities, key=lambda x: x.get('match_score', 0), reverse=True)
        return {"opportunities": sorted_opps[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
