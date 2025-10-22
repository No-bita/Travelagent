"""
City Recognition API Endpoints
Provides city matching, validation, and suggestions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from services.city_service import get_city_service

logger = logging.getLogger(__name__)

router = APIRouter()

class CityMatchRequest(BaseModel):
    input: str

class CityMatchResponse(BaseModel):
    city: Optional[Dict[str, Any]] = None
    found: bool = False
    suggestions: List[Dict[str, Any]] = []

class CityValidationRequest(BaseModel):
    from_city: str
    to_city: str

class CityValidationResponse(BaseModel):
    from_city: Dict[str, Any]
    to_city: Dict[str, Any]
    overall_valid: bool

@router.post("/cities/match", response_model=CityMatchResponse)
async def match_city(request: CityMatchRequest):
    """Find city match with fuzzy search"""
    try:
        city_service = await get_city_service()
        
        # Find city match
        city_match = await city_service.find_city_match(request.input)
        
        if city_match:
            return CityMatchResponse(
                city=city_match,
                found=True,
                suggestions=[]
            )
        else:
            # Get suggestions for unrecognized input
            suggestions = await city_service.get_suggestions(request.input)
            return CityMatchResponse(
                city=None,
                found=False,
                suggestions=suggestions
            )
    
    except Exception as e:
        logger.error(f"City matching error: {e}")
        raise HTTPException(status_code=500, detail="City matching failed")

@router.post("/cities/validate", response_model=CityValidationResponse)
async def validate_cities(request: CityValidationRequest):
    """Validate both origin and destination cities"""
    try:
        city_service = await get_city_service()
        
        # Validate both cities
        validation_result = await city_service.validate_cities(
            request.from_city, 
            request.to_city
        )
        
        return CityValidationResponse(
            from_city=validation_result['from'],
            to_city=validation_result['to'],
            overall_valid=validation_result['overall_valid']
        )
    
    except Exception as e:
        logger.error(f"City validation error: {e}")
        raise HTTPException(status_code=500, detail="City validation failed")

@router.get("/cities/suggestions")
async def get_city_suggestions(input: str, limit: int = 5):
    """Get city suggestions for partial input"""
    try:
        city_service = await get_city_service()
        
        suggestions = await city_service.get_suggestions(input, limit)
        
        return {
            "input": input,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    
    except Exception as e:
        logger.error(f"City suggestions error: {e}")
        raise HTTPException(status_code=500, detail="City suggestions failed")

@router.get("/cities/health")
async def cities_health():
    """Health check for city service"""
    try:
        city_service = await get_city_service()
        
        return {
            "status": "healthy",
            "total_cities": len(city_service.all_cities),
            "total_variations": len(city_service.all_variations)
        }
    
    except Exception as e:
        logger.error(f"City service health check failed: {e}")
        raise HTTPException(status_code=500, detail="City service unhealthy")
