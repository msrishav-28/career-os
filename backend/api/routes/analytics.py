from fastapi import APIRouter, HTTPException, Depends
from utils.analytics import analytics_engine
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db_session
from db import insights_repo
import uuid
from auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/outreach")
async def get_outreach_analytics(
    days: int = 30,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get outreach performance analytics"""
    try:
        metrics = await analytics_engine.get_outreach_metrics(uuid.UUID(current_user["id"]), days, session=session)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline")
async def get_pipeline_analytics(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get CRM pipeline analytics"""
    try:
        metrics = await analytics_engine.get_pipeline_metrics(uuid.UUID(current_user["id"]), session=session)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns")
async def get_campaign_analytics(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get campaign performance analytics"""
    try:
        performance = await analytics_engine.get_campaign_performance(uuid.UUID(current_user["id"]), session=session)
        return {"campaigns": performance, "count": len(performance)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skill-gaps")
async def get_skill_gaps(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Identify skill gaps based on opportunities"""
    try:
        gaps = await analytics_engine.identify_skill_gaps(uuid.UUID(current_user["id"]), session=session)
        return gaps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-health")
async def get_network_health(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Analyze network composition and health"""
    try:
        health = await analytics_engine.analyze_network_health(uuid.UUID(current_user["id"]), session=session)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goal-progress")
async def get_goal_progress(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Track progress toward goals"""
    try:
        progress = await analytics_engine.get_goal_progress(uuid.UUID(current_user["id"]), session=session)
        return {"goals": progress, "count": len(progress)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_summary(
    days: int = 7,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get comprehensive dashboard summary"""
    try:
        # Get all key metrics
        uid = uuid.UUID(current_user["id"])
        outreach = await analytics_engine.get_outreach_metrics(uid, days, session=session)
        pipeline = await analytics_engine.get_pipeline_metrics(uid, session=session)
        network = await analytics_engine.analyze_network_health(uid, session=session)
        skill_gaps = await analytics_engine.identify_skill_gaps(uid, session=session)
        
        return {
            'period_days': days,
            'outreach': {
                'messages_sent': outreach['total_sent'],
                'response_rate': outreach['response_rate'],
                'avg_personalization': outreach['avg_personalization_score']
            },
            'pipeline': {
                'total_contacts': pipeline['total_contacts'],
                'conversion_rate': pipeline['conversion_rates']['contact_to_response'],
                'by_status': pipeline['by_status']
            },
            'network': {
                'health_score': network['network_health_score'],
                'total_contacts': network['total_contacts']
            },
            'skill_gaps': {
                'gaps_identified': skill_gaps['skill_gaps_identified'],
                'top_gap': skill_gaps['top_gaps'][0] if skill_gaps['top_gaps'] else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly-report/generate")
async def generate_weekly_report_manual(current_user: CurrentUser = Depends(get_current_user)):
    """Manually trigger weekly report generation"""
    try:
        from tasks.scheduled_tasks import generate_weekly_report_task
        
        # Trigger async task
        result = generate_weekly_report_task.delay()
        
        return {
            "message": "Weekly report generation started",
            "task_id": result.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights(
    limit: int = 10,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Get AI-generated insights"""
    try:
        insights = await insights_repo.list(session, uuid.UUID(current_user["id"]), limit=limit)
        return {"insights": insights, "count": len(insights)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
