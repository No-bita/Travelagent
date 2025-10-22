"""
Async State Manager
Replaces sync state manager with async Redis operations and connection pooling
"""

import redis.asyncio as redis
import json
import logging
from typing import Dict, Any, Optional
from config import settings
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AsyncStateManager:
    """Async state manager with Redis connection pooling"""
    
    def __init__(self):
        self.redis_pool = None
        self._fallback_storage = {}  # In-memory fallback for development
    
    async def __aenter__(self):
        """Async context manager for Redis connection pooling"""
        try:
            self.redis_pool = redis.from_url(
                settings.redis_url,
                encoding=settings.redis_encoding,
                decode_responses=settings.redis_decode_responses,
                max_connections=settings.redis_max_connections,
                retry_on_timeout=settings.redis_retry_on_timeout
            )
            # Test connection
            await self.redis_pool.ping()
            logger.info("Async Redis connection created successfully")
        except Exception as e:
            logger.warning(f"Failed to create Redis connection: {e}. Using in-memory fallback.")
            self.redis_pool = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up Redis connection pool"""
        if self.redis_pool:
            await self.redis_pool.aclose()
            logger.info("Async Redis connection closed")
    
    async def _get_session_async(self, session_id: str) -> Dict[str, Any]:
        """Get session data asynchronously"""
        if self.redis_pool:
            try:
                data = await self.redis_pool.get(f"session:{session_id}")
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}. Using fallback.")
        
        # Fallback to in-memory storage
        return self._fallback_storage.get(session_id, {})
    
    async def _set_session_async(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Set session data asynchronously"""
        if self.redis_pool:
            try:
                # Set with configurable expiration
                await self.redis_pool.setex(
                    f"session:{session_id}",
                    settings.session_expiry,
                    json.dumps(data)
                )
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}. Using fallback.")
        
        # Fallback to in-memory storage
        self._fallback_storage[session_id] = data
        return True
    
    async def _delete_session_async(self, session_id: str) -> bool:
        """Delete session data asynchronously"""
        if self.redis_pool:
            try:
                await self.redis_pool.delete(f"session:{session_id}")
                return True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}. Using fallback.")
        
        # Fallback to in-memory storage
        if session_id in self._fallback_storage:
            del self._fallback_storage[session_id]
        return True
    
    async def merge_into_session_async(self, session_id: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge NLP result into session state asynchronously
        """
        try:
            # Get existing session data
            session_data = await self._get_session_async(session_id)
            
            # Merge NLP result into session
            if 'intent' in nlp_result:
                session_data['intent'] = nlp_result['intent']
            
            if 'from' in nlp_result and nlp_result['from']:
                session_data['from'] = nlp_result['from']
            
            if 'to' in nlp_result and nlp_result['to']:
                session_data['to'] = nlp_result['to']
            
            if 'date' in nlp_result and nlp_result['date']:
                session_data['date'] = nlp_result['date']
            
            if 'preference' in nlp_result and nlp_result['preference']:
                session_data['preference'] = nlp_result['preference']
            
            # Add timestamp
            session_data['last_updated'] = datetime.now().isoformat()
            
            # Save updated session
            await self._set_session_async(session_id, session_data)
            
            logger.info(f"Async session updated for {session_id}: {list(session_data.keys())}")
            return session_data
            
        except Exception as e:
            logger.error(f"Async session merge failed: {e}")
            # Return minimal session data
            return {
                'intent': nlp_result.get('intent', ''),
                'from': nlp_result.get('from', ''),
                'to': nlp_result.get('to', ''),
                'date': nlp_result.get('date', ''),
                'preference': nlp_result.get('preference', ''),
                'last_updated': datetime.now().isoformat()
            }
    
    async def get_session_async(self, session_id: str) -> Dict[str, Any]:
        """Get session data asynchronously"""
        try:
            return await self._get_session_async(session_id)
        except Exception as e:
            logger.error(f"Async session get failed: {e}")
            return {}
    
    async def clear_session_async(self, session_id: str) -> bool:
        """Clear session data asynchronously"""
        try:
            return await self._delete_session_async(session_id)
        except Exception as e:
            logger.error(f"Async session clear failed: {e}")
            return False
    
    async def get_session_stats_async(self) -> Dict[str, Any]:
        """Get session statistics asynchronously"""
        try:
            if self.redis_pool:
                # Get Redis info
                info = await self.redis_pool.info()
                return {
                    "storage_type": "redis",
                    "connected_clients": info.get('connected_clients', 0),
                    "used_memory": info.get('used_memory_human', '0B'),
                    "total_commands_processed": info.get('total_commands_processed', 0)
                }
            else:
                # Fallback storage stats
                return {
                    "storage_type": "in_memory",
                    "total_sessions": len(self._fallback_storage),
                    "fallback_mode": True
                }
        except Exception as e:
            logger.error(f"Async session stats failed: {e}")
            return {"error": str(e)}

# Global async state manager instance
_async_state_manager = None

async def get_async_state_manager() -> AsyncStateManager:
    """Get or create async state manager instance"""
    global _async_state_manager
    if _async_state_manager is None:
        _async_state_manager = AsyncStateManager()
    return _async_state_manager

# Async wrapper functions for backward compatibility
async def merge_into_session_async(session_id: str, nlp_result: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for session merge"""
    async with AsyncStateManager() as manager:
        return await manager.merge_into_session_async(session_id, nlp_result)

async def get_session_async(session_id: str) -> Dict[str, Any]:
    """Async wrapper for session get"""
    async with AsyncStateManager() as manager:
        return await manager.get_session_async(session_id)

async def clear_session_async(session_id: str) -> bool:
    """Async wrapper for session clear"""
    async with AsyncStateManager() as manager:
        return await manager.clear_session_async(session_id)
