"""
Performance Metrics and Monitoring Endpoints
Provides system health, performance metrics, and optimization insights
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import psutil
import time
from datetime import datetime, timedelta
from services.flight_service_async import AsyncFlightService
from config import settings
import redis
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {}
    }
    
    # Check Redis connection
    try:
        from db.redis_client import get_redis_client
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["components"]["redis"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check database connection
    try:
        from db.database import get_database_engine
        engine = get_database_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["components"]["system"] = {
            "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
        
        if cpu_percent > 90 or memory.percent > 90:
            health_status["status"] = "degraded"
            
    except Exception as e:
        health_status["components"]["system"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get detailed performance metrics"""
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {},
        "api": {},
        "cache": {},
        "database": {}
    }
    
    # System metrics
    try:
        metrics["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                "percent": psutil.disk_usage('/').percent
            },
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    except Exception as e:
        metrics["system"]["error"] = str(e)
    
    # API metrics
    try:
        async_flight_service = AsyncFlightService({
            'amadeus_api_key': settings.amadeus_api_key,
            'amadeus_api_secret': settings.amadeus_api_secret,
            'skyscanner_api_key': settings.skyscanner_api_key
        })
        metrics["api"] = await async_flight_service.get_metrics()
    except Exception as e:
        metrics["api"]["error"] = str(e)
    
    # Cache metrics
    try:
        from db.redis_client import get_redis_client
        redis_client = get_redis_client()
        
        # Get Redis info
        info = redis_client.info()
        metrics["cache"] = {
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 2
            )
        }
    except Exception as e:
        metrics["cache"]["error"] = str(e)
    
    # Database metrics
    try:
        from db.database import get_database_engine
        engine = get_database_engine()
        
        with engine.connect() as conn:
            # Get connection pool stats
            pool = engine.pool
            metrics["database"] = {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid()
            }
    except Exception as e:
        metrics["database"]["error"] = str(e)
    
    return metrics

@router.get("/performance")
async def get_performance_insights() -> Dict[str, Any]:
    """Get performance insights and optimization recommendations"""
    insights = {
        "timestamp": datetime.utcnow().isoformat(),
        "recommendations": [],
        "alerts": [],
        "optimization_score": 0
    }
    
    try:
        # Get current metrics
        metrics_response = await get_metrics()
        metrics = metrics_response
        
        score = 100
        recommendations = []
        alerts = []
        
        # Analyze system performance
        if "system" in metrics and "error" not in metrics["system"]:
            cpu = metrics["system"].get("cpu_percent", 0)
            memory = metrics["system"].get("memory", {}).get("percent", 0)
            
            if cpu > 80:
                alerts.append(f"High CPU usage: {cpu}%")
                recommendations.append("Consider scaling horizontally or optimizing CPU-intensive operations")
                score -= 20
            
            if memory > 80:
                alerts.append(f"High memory usage: {memory}%")
                recommendations.append("Consider increasing memory or optimizing memory usage")
                score -= 20
        
        # Analyze API performance
        if "api" in metrics and "error" not in metrics["api"]:
            api_metrics = metrics["api"]
            cache_hit_rate = float(api_metrics.get("cache_hit_rate", "0%").replace("%", ""))
            
            if cache_hit_rate < 50:
                recommendations.append("Low cache hit rate - consider increasing cache TTL or improving cache keys")
                score -= 15
            
            if api_metrics.get("failures", 0) > 10:
                alerts.append(f"High API failure rate: {api_metrics.get('failures', 0)} failures")
                recommendations.append("Check API health and implement better error handling")
                score -= 25
        
        # Analyze database performance
        if "database" in metrics and "error" not in metrics["database"]:
            db_metrics = metrics["database"]
            pool_utilization = (db_metrics.get("checked_out", 0) / max(db_metrics.get("pool_size", 1), 1)) * 100
            
            if pool_utilization > 80:
                recommendations.append("High database connection pool utilization - consider increasing pool size")
                score -= 10
        
        # Analyze cache performance
        if "cache" in metrics and "error" not in metrics["cache"]:
            cache_metrics = metrics["cache"]
            hit_rate = cache_metrics.get("hit_rate", 0)
            
            if hit_rate < 70:
                recommendations.append("Low Redis hit rate - consider optimizing cache strategy")
                score -= 15
        
        insights["recommendations"] = recommendations
        insights["alerts"] = alerts
        insights["optimization_score"] = max(score, 0)
        
    except Exception as e:
        insights["error"] = str(e)
        insights["optimization_score"] = 0
    
    return insights

@router.get("/optimize")
async def get_optimization_suggestions() -> Dict[str, Any]:
    """Get specific optimization suggestions based on current system state"""
    suggestions = {
        "timestamp": datetime.utcnow().isoformat(),
        "immediate_actions": [],
        "medium_term_actions": [],
        "long_term_actions": []
    }
    
    try:
        # Get current performance data
        metrics_response = await get_metrics()
        
        # Immediate actions (can be implemented quickly)
        suggestions["immediate_actions"] = [
            "Enable Redis connection pooling (already implemented)",
            "Add database indexes for common queries (already implemented)",
            "Implement request-level caching for NLP results",
            "Add circuit breakers for external API calls (already implemented)"
        ]
        
        # Medium term actions (require some development)
        suggestions["medium_term_actions"] = [
            "Implement async processing for all I/O operations",
            "Add request batching for multiple API calls",
            "Implement intelligent cache warming",
            "Add performance monitoring and alerting",
            "Optimize database queries with query analysis"
        ]
        
        # Long term actions (architectural changes)
        suggestions["long_term_actions"] = [
            "Migrate to microservices architecture",
            "Implement event-driven architecture with message queues",
            "Add machine learning for intelligent caching",
            "Implement auto-scaling based on load",
            "Add distributed tracing for performance analysis"
        ]
        
    except Exception as e:
        suggestions["error"] = str(e)
    
    return suggestions
