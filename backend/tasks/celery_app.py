from celery import Celery
from celery.schedules import crontab
from config.settings import settings

# Initialize Celery
celery_app = Celery(
    'careeros',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'tasks.scheduled_tasks',
        'tasks.agent_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Daily opportunity discovery (6 AM)
    'discover-opportunities-daily': {
        'task': 'tasks.scheduled_tasks.discover_opportunities_task',
        'schedule': crontab(hour=6, minute=0),
    },
    
    # Check for follow-ups needed (every 6 hours)
    'check-followups': {
        'task': 'tasks.scheduled_tasks.check_followups_task',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    
    # Send approved messages (every hour during work hours)
    'send-approved-messages': {
        'task': 'tasks.scheduled_tasks.send_approved_messages_task',
        'schedule': crontab(minute=0, hour='9-18'),
    },
    
    # Daily content curation (8 AM)
    'curate-daily-content': {
        'task': 'tasks.scheduled_tasks.curate_content_task',
        'schedule': crontab(hour=8, minute=0),
    },
    
    # Weekly performance report (Sunday 7 PM)
    'weekly-report': {
        'task': 'tasks.scheduled_tasks.generate_weekly_report_task',
        'schedule': crontab(day_of_week=0, hour=19, minute=0),
    },
    
    # Analyze responses (every 2 hours)
    'analyze-responses': {
        'task': 'tasks.scheduled_tasks.analyze_responses_task',
        'schedule': crontab(minute=0, hour='*/2'),
    },
}

# Task routing
celery_app.conf.task_routes = {
    'tasks.scheduled_tasks.*': {'queue': 'scheduled'},
    'tasks.agent_tasks.*': {'queue': 'agents'},
}
