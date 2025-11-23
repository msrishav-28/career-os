import redis
from typing import Optional
from datetime import timedelta
from config.settings import settings
import json


class RedisService:
    """Service for Redis operations (caching and rate limiting)"""
    
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def set(self, key: str, value: str, expiry: Optional[int] = None):
        """Set a value in Redis"""
        if expiry:
            self.client.setex(key, expiry, value)
        else:
            self.client.set(key, value)
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis"""
        return self.client.get(key)
    
    def delete(self, key: str):
        """Delete a key from Redis"""
        self.client.delete(key)
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter"""
        return self.client.incrby(key, amount)
    
    def set_json(self, key: str, value: dict, expiry: Optional[int] = None):
        """Set a JSON value"""
        self.set(key, json.dumps(value), expiry)
    
    def get_json(self, key: str) -> Optional[dict]:
        """Get a JSON value"""
        value = self.get(key)
        return json.loads(value) if value else None
    
    # Rate Limiting
    def check_rate_limit(
        self,
        user_id: str,
        action_type: str,
        limit: int,
        window_seconds: int = 86400  # 24 hours default
    ) -> tuple[bool, int]:
        """
        Check if action is within rate limit
        Returns: (allowed: bool, current_count: int)
        """
        key = f"rate_limit:{user_id}:{action_type}"
        current = self.client.get(key)
        
        if current is None:
            # First action, set counter
            self.client.setex(key, window_seconds, 1)
            return True, 1
        
        current_count = int(current)
        
        if current_count >= limit:
            return False, current_count
        
        # Increment counter
        new_count = self.client.incr(key)
        return True, new_count
    
    def get_rate_limit_status(self, user_id: str, action_type: str) -> dict:
        """Get rate limit status for an action"""
        key = f"rate_limit:{user_id}:{action_type}"
        current = self.client.get(key)
        ttl = self.client.ttl(key)
        
        return {
            'current_count': int(current) if current else 0,
            'ttl_seconds': ttl if ttl > 0 else 0
        }
    
    def reset_rate_limit(self, user_id: str, action_type: str):
        """Reset rate limit for an action"""
        key = f"rate_limit:{user_id}:{action_type}"
        self.client.delete(key)
    
    # Caching
    def cache_set(self, key: str, value: any, ttl: int = 3600):
        """Cache a value"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.set(key, value, ttl)
    
    def cache_get(self, key: str) -> Optional[any]:
        """Get cached value"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def cache_delete(self, key: str):
        """Delete cached value"""
        self.delete(key)
    
    # Session Management
    def store_session(self, session_id: str, data: dict, ttl: int = 3600):
        """Store session data"""
        key = f"session:{session_id}"
        self.set_json(key, data, ttl)
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        key = f"session:{session_id}"
        return self.get_json(key)
    
    def delete_session(self, session_id: str):
        """Delete session"""
        key = f"session:{session_id}"
        self.delete(key)


# Singleton instance
redis_service = RedisService()
