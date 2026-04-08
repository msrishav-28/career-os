from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from models import OpportunityCreate, OpportunityUpdate, OpportunityStatus, OpportunityType
from db import opportunities_repo
from db.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from crews import DiscoveryCrew
from typing import Optional
import uuid
from auth import get_current_user, CurrentUser
from security.rate_limit import rate_limit

router = APIRouter()


@router.post("/discover")
async def discover_opportunities(
    keywords: str = "AI ML internship",
    location: str = "India",
    opportunity_type: str = "internship",
    current_user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit("opportunity_discover", 30)),
):
    """Discover new opportunities using AI agents"""
    try:
        crew = DiscoveryCrew(current_user["id"])
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
async def create_opportunity(
    opportunity: OpportunityCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Manually create an opportunity"""
    try:
        result = await opportunities_repo.create(session, uuid.UUID(current_user["id"]), opportunity.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_opportunities(
    status: Optional[OpportunityStatus] = None,
    opportunity_type: Optional[OpportunityType] = None,
    min_match_score: Optional[int] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get opportunities with filters"""
    try:
        opportunities = await opportunities_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            status=status.value if status else None,
            opportunity_type=opportunity_type.value if opportunity_type else None,
            min_match_score=min_match_score,
            limit=limit
        )
        return {"opportunities": opportunities, "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{opportunity_id}")
async def update_opportunity(opportunity_id: str, update: OpportunityUpdate, session: AsyncSession = Depends(get_db_session)):
    """Update an opportunity"""
    try:
        result = await opportunities_repo.update(
            session,
            uuid.UUID(opportunity_id),
            {k: v for k, v in update.dict().items() if v is not None}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top")
async def get_top_opportunities(
    limit: int = 10,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get top opportunities by match score"""
    try:
        opportunities = await opportunities_repo.list(
            session,
            uuid.UUID(current_user["id"]),
            min_match_score=7,
            limit=limit
        )
        # Sort by match score
        sorted_opps = sorted(opportunities, key=lambda x: x.get('match_score', 0), reverse=True)
        return {"opportunities": sorted_opps[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
