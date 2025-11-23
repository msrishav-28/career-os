from supabase import create_client, Client
from typing import List, Dict, Optional
from config.settings import settings
from datetime import datetime
import uuid


class SupabaseService:
    """Service for managing Supabase database operations"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    # Contacts Operations
    async def create_contact(self, user_id: str, contact_data: Dict) -> Dict:
        """Create a new contact"""
        contact_data['user_id'] = user_id
        contact_data['id'] = str(uuid.uuid4())
        contact_data['created_at'] = datetime.utcnow().isoformat()
        
        result = self.client.table('contacts').insert(contact_data).execute()
        return result.data[0] if result.data else None
    
    async def get_contacts(
        self,
        user_id: str,
        status: Optional[str] = None,
        contact_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get contacts with filters"""
        query = self.client.table('contacts').select('*').eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        if contact_type:
            query = query.eq('contact_type', contact_type)
        
        result = query.limit(limit).order('created_at', desc=True).execute()
        return result.data
    
    async def update_contact(self, contact_id: str, update_data: Dict) -> Dict:
        """Update a contact"""
        result = self.client.table('contacts').update(update_data).eq('id', contact_id).execute()
        return result.data[0] if result.data else None
    
    async def get_contact_by_id(self, contact_id: str) -> Optional[Dict]:
        """Get a single contact by ID"""
        result = self.client.table('contacts').select('*').eq('id', contact_id).execute()
        return result.data[0] if result.data else None
    
    # Messages Operations
    async def create_message(self, user_id: str, message_data: Dict) -> Dict:
        """Create a new message"""
        message_data['user_id'] = user_id
        message_data['id'] = str(uuid.uuid4())
        message_data['created_at'] = datetime.utcnow().isoformat()
        
        result = self.client.table('messages').insert(message_data).execute()
        return result.data[0] if result.data else None
    
    async def get_messages(
        self,
        user_id: str,
        status: Optional[str] = None,
        contact_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get messages with filters"""
        query = self.client.table('messages').select('*').eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        if contact_id:
            query = query.eq('contact_id', contact_id)
        if campaign_id:
            query = query.eq('campaign_id', campaign_id)
        
        result = query.limit(limit).order('created_at', desc=True).execute()
        return result.data
    
    async def update_message(self, message_id: str, update_data: Dict) -> Dict:
        """Update a message"""
        result = self.client.table('messages').update(update_data).eq('id', message_id).execute()
        return result.data[0] if result.data else None
    
    # Opportunities Operations
    async def create_opportunity(self, user_id: str, opportunity_data: Dict) -> Dict:
        """Create a new opportunity"""
        opportunity_data['user_id'] = user_id
        opportunity_data['id'] = str(uuid.uuid4())
        opportunity_data['discovered_at'] = datetime.utcnow().isoformat()
        
        result = self.client.table('opportunities').insert(opportunity_data).execute()
        return result.data[0] if result.data else None
    
    async def get_opportunities(
        self,
        user_id: str,
        status: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        min_match_score: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get opportunities with filters"""
        query = self.client.table('opportunities').select('*').eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        if opportunity_type:
            query = query.eq('opportunity_type', opportunity_type)
        if min_match_score:
            query = query.gte('match_score', min_match_score)
        
        result = query.limit(limit).order('discovered_at', desc=True).execute()
        return result.data
    
    async def update_opportunity(self, opportunity_id: str, update_data: Dict) -> Dict:
        """Update an opportunity"""
        result = self.client.table('opportunities').update(update_data).eq('id', opportunity_id).execute()
        return result.data[0] if result.data else None
    
    # Campaigns Operations
    async def create_campaign(self, user_id: str, campaign_data: Dict) -> Dict:
        """Create a new campaign"""
        campaign_data['user_id'] = user_id
        campaign_data['id'] = str(uuid.uuid4())
        campaign_data['created_at'] = datetime.utcnow().isoformat()
        
        result = self.client.table('campaigns').insert(campaign_data).execute()
        return result.data[0] if result.data else None
    
    async def get_campaigns(self, user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get campaigns"""
        query = self.client.table('campaigns').select('*').eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        
        result = query.order('created_at', desc=True).execute()
        return result.data
    
    async def update_campaign(self, campaign_id: str, update_data: Dict) -> Dict:
        """Update a campaign"""
        result = self.client.table('campaigns').update(update_data).eq('id', campaign_id).execute()
        return result.data[0] if result.data else None
    
    # Activity Log
    async def log_activity(self, user_id: str, action_type: str, platform: str, success: bool, metadata: Dict = None):
        """Log an activity"""
        activity_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'action_type': action_type,
            'platform': platform,
            'success': success,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.client.table('activity_log').insert(activity_data).execute()
    
    async def get_activity_stats(self, user_id: str, days: int = 7) -> Dict:
        """Get activity statistics"""
        # This would use SQL aggregations in a real implementation
        from datetime import timedelta
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        result = self.client.table('activity_log')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', since)\
            .execute()
        
        activities = result.data
        
        return {
            'total_activities': len(activities),
            'successful': len([a for a in activities if a['success']]),
            'failed': len([a for a in activities if not a['success']]),
            'by_platform': self._group_by(activities, 'platform'),
            'by_action': self._group_by(activities, 'action_type')
        }
    
    def _group_by(self, items: List[Dict], key: str) -> Dict:
        """Group items by a key"""
        result = {}
        for item in items:
            value = item.get(key, 'unknown')
            result[value] = result.get(value, 0) + 1
        return result
    
    # User Operations
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        user_data['id'] = str(uuid.uuid4())
        user_data['created_at'] = datetime.utcnow().isoformat()
        
        result = self.client.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self.client.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    
    async def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Update a user"""
        result = self.client.table('users').update(update_data).eq('id', user_id).execute()
        return result.data[0] if result.data else None


# Singleton instance
supabase_service = SupabaseService()
