from fastapi import APIRouter, HTTPException
from utils.analytics import analytics_engine
from typing import Optional

router = APIRouter()


@router.get("/outreach")
async def get_outreach_analytics(user_id: str, days: int = 30):
    """Get outreach performance analytics"""
    try:
        metrics = await analytics_engine.get_outreach_metrics(user_id, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline")
async def get_pipeline_analytics(user_id: str):
    """Get CRM pipeline analytics"""
    try:
        metrics = await analytics_engine.get_pipeline_metrics(user_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns")
async def get_campaign_analytics(user_id: str):
    """Get campaign performance analytics"""
    try:
        performance = await analytics_engine.get_campaign_performance(user_id)
        return {"campaigns": performance, "count": len(performance)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skill-gaps")
async def get_skill_gaps(user_id: str):
    """Identify skill gaps based on opportunities"""
    try:
        gaps = await analytics_engine.identify_skill_gaps(user_id)
        return gaps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network-health")
async def get_network_health(user_id: str):
    """Analyze network composition and health"""
    try:
        health = await analytics_engine.analyze_network_health(user_id)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goal-progress")
async def get_goal_progress(user_id: str):
    """Track progress toward goals"""
    try:
        progress = await analytics_engine.get_goal_progress(user_id)
        return {"goals": progress, "count": len(progress)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_summary(user_id: str, days: int = 7):
    """Get comprehensive dashboard summary"""
    try:
        # Get all key metrics
        outreach = await analytics_engine.get_outreach_metrics(user_id, days)
        pipeline = await analytics_engine.get_pipeline_metrics(user_id)
        network = await analytics_engine.analyze_network_health(user_id)
        skill_gaps = await analytics_engine.identify_skill_gaps(user_id)
        
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
async def generate_weekly_report_manual(user_id: str):
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
async def get_insights(user_id: str, limit: int = 10):
    """Get AI-generated insights"""
    try:
        from services import supabase_service
        
        # Get recent insights
        insights = await supabase_service.client.table('agent_insights')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {"insights": insights.data, "count": len(insights.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
