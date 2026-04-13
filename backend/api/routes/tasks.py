from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from tasks import agent_tasks, scheduled_tasks
from typing import Optional, Dict
from auth import get_current_user, CurrentUser
from auth.admin import require_admin

router = APIRouter()


@router.post("/outreach/generate-async")
async def generate_outreach_async(
    contact_id: str,
    context: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Generate outreach message asynchronously"""
    try:
        result = agent_tasks.generate_outreach_async.delay(current_user["id"], contact_id, context)
        return {
            "message": "Outreach generation started",
            "task_id": result.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outreach/batch-generate")
async def batch_generate_outreach(
    contact_ids: list,
    context: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Generate outreach for multiple contacts"""
    try:
        result = agent_tasks.batch_generate_outreach.delay(current_user["id"], contact_ids, context)
        return {
            "message": f"Batch generation started for {len(contact_ids)} contacts",
            "task_id": result.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/opportunities/discover-async")
async def discover_opportunities_async(search_params: Dict, current_user: CurrentUser = Depends(get_current_user)):
    """Discover opportunities asynchronously"""
    try:
        result = agent_tasks.discover_opportunities_async.delay(current_user["id"], search_params)
        return {
            "message": "Opportunity discovery started",
            "task_id": result.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/followup/auto-generate")
async def auto_generate_followup(message_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Auto-generate follow-up message"""
    try:
        result = agent_tasks.auto_followup_generation.delay(current_user["id"], message_id)
        return {
            "message": "Follow-up generation started",
            "task_id": result.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a background task"""
    try:
        from tasks.celery_app import celery_app
        
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "info": result.info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduled/trigger/{task_name}")
async def trigger_scheduled_task(task_name: str, admin_user: CurrentUser = Depends(require_admin)):
    """Manually trigger a scheduled task"""
    try:
        task_map = {
            "discover_opportunities": scheduled_tasks.discover_opportunities_task,
            "check_followups": scheduled_tasks.check_followups_task,
            "send_approved_messages": scheduled_tasks.send_approved_messages_task,
            "curate_content": scheduled_tasks.curate_content_task,
            "weekly_report": scheduled_tasks.generate_weekly_report_task,
            "analyze_responses": scheduled_tasks.analyze_responses_task
        }
        
        task = task_map.get(task_name)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        result = task.delay()
        
        return {
            "message": f"Task '{task_name}' triggered",
            "task_id": result.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled/status")
async def get_scheduled_tasks_status():
    """Get status of all scheduled tasks"""
    try:
        from tasks.celery_app import celery_app
        
        # Get celery beat schedule
        schedule = celery_app.conf.beat_schedule
        
        task_status = []
        for name, config in schedule.items():
            task_status.append({
                "name": name,
                "task": config['task'],
                "schedule": str(config['schedule']),
                "enabled": True
            })
        
        return {"scheduled_tasks": task_status, "count": len(task_status)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
