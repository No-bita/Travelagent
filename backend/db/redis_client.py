import json
import redis
from datetime import timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Redis client configuration with connection pooling
redis_client: Optional[redis.Redis] = None
redis_pool: Optional[redis.ConnectionPool] = None
SESSION_TTL = timedelta(hours=24)

def get_redis_client() -> redis.Redis:
    """Get or create Redis client with connection pooling"""
    global redis_client, redis_pool
    if redis_client is None:
        from config import settings
        
        # Parse Redis URL
        url_parts = settings.redis_url.split('://')[1].split(':')
        host = url_parts[0]
        port = int(url_parts[1].split('/')[0])
        db = int(url_parts[1].split('/')[1])
        
        # Create connection pool for better performance
        redis_pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30
        )
        
        redis_client = redis.Redis(
            connection_pool=redis_pool,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        try:
            redis_client.ping()
            logger.info("Redis connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    return redis_client

def save_session(session_id: str, state: Dict[str, Any]) -> bool:
    """Save session state to Redis with TTL"""
    try:
        client = get_redis_client()
        key = f"session:{session_id}"
        client.setex(key, SESSION_TTL, json.dumps(state))
        logger.info(f"Saved session {session_id} to Redis")
        return True
    except Exception as e:
        logger.error(f"Failed to save session {session_id}: {e}")
        return False

def get_session(session_id: str) -> Dict[str, Any]:
    """Get session state from Redis"""
    try:
        client = get_redis_client()
        key = f"session:{session_id}"
        data = client.get(key)
        if data:
            return json.loads(data)
        return {}
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        return {}

def update_session(session_id: str, updates: Dict[str, Any]) -> bool:
    """Update session state in Redis"""
    try:
        state = get_session(session_id)
        state.update(updates)
        return save_session(session_id, state)
    except Exception as e:
        logger.error(f"Failed to update session {session_id}: {e}")
        return False

def delete_session(session_id: str) -> bool:
    """Delete session from Redis"""
    try:
        client = get_redis_client()
        key = f"session:{session_id}"
        client.delete(key)
        logger.info(f"Deleted session {session_id} from Redis")
        return True
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        return False

def extend_session_ttl(session_id: str) -> bool:
    """Extend session TTL on activity"""
    try:
        client = get_redis_client()
        key = f"session:{session_id}"
        client.expire(key, SESSION_TTL)
        return True
    except Exception as e:
        logger.error(f"Failed to extend TTL for session {session_id}: {e}")
        return False


