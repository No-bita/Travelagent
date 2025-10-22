from fastapi import APIRouter
from services.flight_service_async import get_flight_metrics_async
from core.state_manager_async import get_async_state_manager
from core.nlp_engine_async import get_async_nlp_engine
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "async": True}


@router.get("/health/detailed")
async def detailed_health() -> dict:
    """Detailed async health check including all services"""
    try:
        # Get async flight service metrics
        flight_metrics = await get_flight_metrics_async()
        
        # Get async state manager stats
        async with get_async_state_manager() as state_manager:
            state_stats = await state_manager.get_session_stats_async()
        
        # Get async NLP engine stats
        async with get_async_nlp_engine() as nlp_engine:
            nlp_stats = {
                "cache_size": len(nlp_engine.entity_cache),
                "redis_connected": nlp_engine.redis_pool is not None,
                "thread_pool_active": nlp_engine.executor._threads
            }
        
        return {
            "status": "ok",
            "async": True,
            "flight_service": flight_metrics,
            "state_manager": state_stats,
            "nlp_engine": nlp_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Async health check failed: {e}")
        return {
            "status": "error",
            "async": True,
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/async")
async def async_health() -> dict:
    """Async-specific health check"""
    try:
        # Test async flight service
        from services.flight_service_async import AsyncFlightService
        async with AsyncFlightService() as flight_service:
            flight_healthy = True
        
        # Test async state manager
        async with get_async_state_manager() as state_manager:
            state_healthy = True
        
        # Test async NLP engine
        async with get_async_nlp_engine() as nlp_engine:
            nlp_healthy = True
        
        return {
            "status": "healthy",
            "async_services": {
                "flight_service": flight_healthy,
                "state_manager": state_healthy,
                "nlp_engine": nlp_healthy
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Async health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


