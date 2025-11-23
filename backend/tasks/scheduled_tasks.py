from tasks.celery_app import celery_app
from services import supabase_service, redis_service, chroma_service
from crews import DiscoveryCrew, OutreachCrew
from agents.crm_agent import analyze_response_sentiment, calculate_contact_priority
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta
import json


@celery_app.task(name='tasks.scheduled_tasks.discover_opportunities_task')
def discover_opportunities_task():
    """Daily task to discover new opportunities for all active users"""
    try:
        # Get all active users
        # In production, query from database
        user_ids = ["demo-user"]  # Placeholder
        
        results = []
        for user_id in user_ids:
            try:
                # Run discovery crew
                crew = DiscoveryCrew(user_id)
                search_params = {
                    "keywords": "AI ML internship",
                    "location": "India",
                    "type": "internship"
                }
                
                opportunities = crew.discover_opportunities(search_params)
                results.append({
                    "user_id": user_id,
                    "opportunities_found": len(opportunities) if opportunities else 0,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "user_id": user_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {"task": "discover_opportunities", "results": results}
    
    except Exception as e:
        return {"task": "discover_opportunities", "error": str(e), "status": "failed"}


@celery_app.task(name='tasks.scheduled_tasks.check_followups_task')
def check_followups_task():
    """Check messages that need follow-ups"""
    try:
        async def run_check():
            results = []
            user_ids = ["demo-user"]
            
            for user_id in user_ids:
                # Get messages sent 7+ days ago with no response
                cutoff_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
                
                messages = await supabase_service.get_messages(
                    user_id,
                    status="sent",
                    limit=100
                )
                
                followup_needed = []
                for msg in messages:
                    sent_at = datetime.fromisoformat(msg.get('sent_at', ''))
                    days_since = (datetime.utcnow() - sent_at).days
                    
                    if days_since >= 7 and not msg.get('replied_at'):
                        # Check if already followed up
                        contact_id = msg.get('contact_id')
                        campaign_id = msg.get('campaign_id')
                        
                        # Count previous follow-ups
                        all_messages = await supabase_service.get_messages(
                            user_id,
                            contact_id=contact_id,
                            campaign_id=campaign_id
                        )
                        
                        followup_count = len([m for m in all_messages if 'follow' in m.get('subject', '').lower()])
                        
                        if followup_count < 2:  # Max 2 follow-ups
                            followup_needed.append({
                                "message_id": msg['id'],
                                "contact_id": contact_id,
                                "days_since": days_since,
                                "followup_count": followup_count
                            })
                
                results.append({
                    "user_id": user_id,
                    "followups_needed": len(followup_needed),
                    "details": followup_needed[:5]  # First 5
                })
            
            return results
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(run_check())
        
        return {"task": "check_followups", "results": results}
    
    except Exception as e:
        return {"task": "check_followups", "error": str(e), "status": "failed"}


@celery_app.task(name='tasks.scheduled_tasks.send_approved_messages_task')
def send_approved_messages_task():
    """Send messages that have been approved, with human-like timing"""
    try:
        async def run_send():
            results = []
            user_ids = ["demo-user"]
            
            for user_id in user_ids:
                # Get approved messages
                messages = await supabase_service.get_messages(
                    user_id,
                    status="approved",
                    limit=50
                )
                
                sent_count = 0
                for msg in messages:
                    # Check rate limits
                    platform = msg.get('platform')
                    action_type = f"{platform}_sent"
                    
                    if platform == 'linkedin':
                        limit = 15
                    elif platform == 'email':
                        limit = 50
                    else:
                        limit = 20
                    
                    allowed, count = redis_service.check_rate_limit(
                        user_id,
                        action_type,
                        limit
                    )
                    
                    if not allowed:
                        continue
                    
                    # Update message status to sent
                    await supabase_service.update_message(
                        msg['id'],
                        {
                            "status": "sent",
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Log activity
                    await supabase_service.log_activity(
                        user_id,
                        action_type,
                        platform,
                        True,
                        {"message_id": msg['id']}
                    )
                    
                    sent_count += 1
                
                results.append({
                    "user_id": user_id,
                    "messages_sent": sent_count
                })
            
            return results
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(run_send())
        
        return {"task": "send_approved_messages", "results": results}
    
    except Exception as e:
        return {"task": "send_approved_messages", "error": str(e), "status": "failed"}


@celery_app.task(name='tasks.scheduled_tasks.curate_content_task')
def curate_content_task():
    """Daily content curation from social feeds"""
    try:
        results = []
        user_ids = ["demo-user"]
        
        for user_id in user_ids:
            # This would integrate with Twitter/LinkedIn APIs
            # For now, create placeholder insight
            
            curated_items = [
                {
                    "title": "New AI research paper on LLMs",
                    "source": "twitter",
                    "relevance_score": 9,
                    "url": "https://example.com/paper",
                    "summary": "Important breakthrough in language models"
                }
            ]
            
            results.append({
                "user_id": user_id,
                "items_curated": len(curated_items)
            })
        
        return {"task": "curate_content", "results": results}
    
    except Exception as e:
        return {"task": "curate_content", "error": str(e), "status": "failed"}


@celery_app.task(name='tasks.scheduled_tasks.generate_weekly_report_task')
def generate_weekly_report_task():
    """Generate weekly performance report"""
    try:
        async def run_report():
            results = []
            user_ids = ["demo-user"]
            
            for user_id in user_ids:
                # Get activity stats for past week
                stats = await supabase_service.get_activity_stats(user_id, days=7)
                
                # Get messages sent this week
                week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
                messages = await supabase_service.get_messages(user_id, limit=1000)
                
                week_messages = [m for m in messages if m.get('sent_at', '') >= week_ago]
                
                # Calculate metrics
                total_sent = len([m for m in week_messages if m.get('status') in ['sent', 'opened', 'replied']])
                total_replied = len([m for m in week_messages if m.get('status') == 'replied'])
                
                response_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
                
                # Get contacts added
                contacts = await supabase_service.get_contacts(user_id, limit=1000)
                week_contacts = [c for c in contacts if c.get('created_at', '') >= week_ago]
                
                report = {
                    "week_ending": datetime.utcnow().strftime("%Y-%m-%d"),
                    "messages_sent": total_sent,
                    "responses_received": total_replied,
                    "response_rate": round(response_rate, 1),
                    "new_contacts": len(week_contacts),
                    "activities": stats
                }
                
                # Store report
                await supabase_service.client.table('agent_insights').insert({
                    "user_id": user_id,
                    "insight_type": "weekly_report",
                    "title": f"Weekly Report - {report['week_ending']}",
                    "description": json.dumps(report),
                    "priority": "medium",
                    "status": "new"
                }).execute()
                
                results.append({
                    "user_id": user_id,
                    "report": report
                })
            
            return results
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(run_report())
        
        return {"task": "generate_weekly_report", "results": results}
    
    except Exception as e:
        return {"task": "generate_weekly_report", "error": str(e), "status": "failed"}


@celery_app.task(name='tasks.scheduled_tasks.analyze_responses_task')
def analyze_responses_task():
    """Analyze responses and update contact priorities"""
    try:
        async def run_analysis():
            results = []
            user_ids = ["demo-user"]
            
            for user_id in user_ids:
                # Get messages with recent replies
                messages = await supabase_service.get_messages(
                    user_id,
                    status="replied",
                    limit=100
                )
                
                analyzed_count = 0
                for msg in messages:
                    if msg.get('reply_content') and not msg.get('sentiment'):
                        # Analyze sentiment
                        sentiment_data = analyze_response_sentiment(msg['reply_content'])
                        
                        # Update message
                        await supabase_service.update_message(
                            msg['id'],
                            {
                                "sentiment": sentiment_data['sentiment'],
                                "metadata": sentiment_data
                            }
                        )
                        
                        # Update contact priority
                        contact = await supabase_service.get_contact_by_id(msg['contact_id'])
                        if contact:
                            priority = calculate_contact_priority(contact, [msg])
                            await supabase_service.update_contact(
                                msg['contact_id'],
                                {"quality_score": priority}
                            )
                        
                        analyzed_count += 1
                
                results.append({
                    "user_id": user_id,
                    "responses_analyzed": analyzed_count
                })
            
            return results
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(run_analysis())
        
        return {"task": "analyze_responses", "results": results}
    
    except Exception as e:
        return {"task": "analyze_responses", "error": str(e), "status": "failed"}
