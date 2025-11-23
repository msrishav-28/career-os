from tasks.celery_app import celery_app
from crews import OutreachCrew, DiscoveryCrew
from services import supabase_service
import asyncio


@celery_app.task(name='tasks.agent_tasks.generate_outreach_async')
def generate_outreach_async(user_id: str, contact_id: str, context: str):
    """Async task to generate outreach message"""
    try:
        async def run_generation():
            # Get contact
            contact = await supabase_service.get_contact_by_id(contact_id)
            if not contact:
                return {"error": "Contact not found"}
            
            # Generate message
            crew = OutreachCrew(user_id)
            result = crew.generate_outreach(contact, context)
            
            return {"result": result, "contact_id": contact_id}
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_generation())
        
        return result
    
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@celery_app.task(name='tasks.agent_tasks.discover_opportunities_async')
def discover_opportunities_async(user_id: str, search_params: dict):
    """Async task to discover opportunities"""
    try:
        crew = DiscoveryCrew(user_id)
        result = crew.discover_opportunities(search_params)
        
        return {"result": result, "user_id": user_id}
    
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@celery_app.task(name='tasks.agent_tasks.batch_generate_outreach')
def batch_generate_outreach(user_id: str, contact_ids: list, context: str):
    """Generate outreach for multiple contacts"""
    try:
        results = []
        
        for contact_id in contact_ids:
            result = generate_outreach_async.delay(user_id, contact_id, context)
            results.append({
                "contact_id": contact_id,
                "task_id": result.id
            })
        
        return {"batch_results": results}
    
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@celery_app.task(name='tasks.agent_tasks.auto_followup_generation')
def auto_followup_generation(user_id: str, message_id: str):
    """Generate follow-up message automatically"""
    try:
        async def run_followup():
            # Get original message
            messages = await supabase_service.get_messages(user_id, limit=1000)
            original_msg = next((m for m in messages if m['id'] == message_id), None)
            
            if not original_msg:
                return {"error": "Message not found"}
            
            # Get contact
            contact = await supabase_service.get_contact_by_id(original_msg['contact_id'])
            
            # Generate follow-up with new angle
            crew = OutreachCrew(user_id)
            context = f"Follow-up to previous message about {original_msg.get('subject', 'our conversation')}"
            
            result = crew.generate_outreach(contact, context)
            
            # Create draft message
            if result:
                await supabase_service.create_message(
                    user_id,
                    {
                        "contact_id": contact['id'],
                        "campaign_id": original_msg.get('campaign_id'),
                        "platform": original_msg.get('platform'),
                        "subject": f"Re: {original_msg.get('subject', '')}",
                        "body": str(result),
                        "personalization_score": 75,
                        "status": "draft"
                    }
                )
            
            return {"followup_generated": True}
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_followup())
        
        return result
    
    except Exception as e:
        return {"error": str(e), "status": "failed"}
