"""
Redis State Management for Conversation Context
PATTERN: Cache-aside pattern with TTL
WHY: Fast context retrieval without database overhead
"""
import json
import redis.asyncio as redis
from typing import List, Dict, Optional
from datetime import datetime
from app.config import settings

class StateManager:
    def __init__(self):
        self.redis_client = None
        self.ttl = settings.redis_ttl
        
    async def initialize(self):
        """
        CONCEPT: Connection pooling for Redis
        WHY: Reuse connections for better performance
        """
        self.redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
    
    async def get_conversation_context(
        self, 
        session_id: str
    ) -> List[Dict]:
        """
        PATTERN: Sliding window of conversation history
        WHY: Claude needs context for coherent responses
        """
        key = f"session:{session_id}:context"
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return []
    
    async def update_conversation_context(
        self,
        session_id: str,
        user_text: str,
        agent_text: str
    ):
        """
        CONCEPT: FIFO queue with fixed size
        WHY: Maintain only relevant recent context
        """
        key = f"session:{session_id}:context"
        
        # Get existing context
        context = await self.get_conversation_context(session_id)
        
        # Add new exchange
        context.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_text,
            "agent": agent_text
        })
        
        # Keep only last N exchanges
        if len(context) > settings.max_context_exchanges:
            context = context[-settings.max_context_exchanges:]
        
        # Save with TTL
        await self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(context)
        )
    
    async def get_session_metadata(
        self, 
        session_id: str
    ) -> Optional[Dict]:
        """Get session metadata like start time, exchange count"""
        key = f"session:{session_id}:metadata"
        data = await self.redis_client.get(key)
        return json.loads(data) if data else None
    
    async def update_session_metadata(
        self,
        session_id: str,
        metadata: Dict
    ):
        """Update session metadata with activity tracking"""
        key = f"session:{session_id}:metadata"
        
        # Update last activity
        metadata["last_activity"] = datetime.utcnow().isoformat()
        
        await self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(metadata)
        )
    
    async def is_session_active(
        self, 
        session_id: str
    ) -> bool:
        """
        PATTERN: Activity-based session validation
        WHY: Auto-end sessions after inactivity
        """
        metadata = await self.get_session_metadata(session_id)
        
        if not metadata:
            return False
        
        last_activity = datetime.fromisoformat(metadata["last_activity"])
        inactive_seconds = (datetime.utcnow() - last_activity).total_seconds()
        
        return inactive_seconds < settings.session_timeout
    
    async def end_session(self, session_id: str):
        """Clean up session data"""
        keys = [
            f"session:{session_id}:context",
            f"session:{session_id}:metadata"
        ]
        
        for key in keys:
            await self.redis_client.delete(key)
    
    async def get_active_sessions(self) -> List[str]:
        """Get all active session IDs for monitoring"""
        pattern = "session:*:metadata"
        keys = []
        
        async for key in self.redis_client.scan_iter(match=pattern):
            session_id = key.split(":")[1]
            if await self.is_session_active(session_id):
                keys.append(session_id)
        
        return keys
    
    async def close(self):
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

# Global state manager instance
state_manager = StateManager()