"""
Enhanced Error Handling for NLP Engine
Handles missing cities, unrecognized locations, and provides helpful suggestions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from difflib import get_close_matches
from config import settings

logger = logging.getLogger(__name__)

class AsyncErrorHandler:
    """Async error handler for NLP processing with intelligent suggestions"""
    
    def __init__(self):
        self.city_mappings = settings.city_mappings
        self.airport_codes = settings.airport_codes
        self.all_cities = list(self.city_mappings.keys())
        self.all_variations = []
        
        # Build comprehensive variation list
        for city, variations in self.city_mappings.items():
            self.all_variations.extend(variations)
            self.all_variations.append(city)
    
    async def validate_cities_async(self, from_city: str, to_city: str) -> Dict[str, Any]:
        """Validate and suggest corrections for cities"""
        validation_result = {
            'from': {'valid': False, 'suggestions': [], 'error': None},
            'to': {'valid': False, 'suggestions': [], 'error': None},
            'overall_valid': False
        }
        
        # Validate from city
        from_validation = await self._validate_single_city_async(from_city, 'from')
        validation_result['from'] = from_validation
        
        # Validate to city
        to_validation = await self._validate_single_city_async(to_city, 'to')
        validation_result['to'] = to_validation
        
        # Overall validation
        validation_result['overall_valid'] = from_validation['valid'] and to_validation['valid']
        
        return validation_result
    
    async def _validate_single_city_async(self, city: str, city_type: str) -> Dict[str, Any]:
        """Validate a single city and provide suggestions"""
        if not city or not city.strip():
            return {
                'valid': False,
                'suggestions': [],
                'error': f'No {city_type} city provided',
                'error_type': 'missing'
            }
        
        city_lower = city.lower().strip()
        
        # Check if city exists in mappings
        if city_lower in self.city_mappings:
            return {
                'valid': True,
                'suggestions': [],
                'error': None,
                'error_type': None,
                'canonical_name': city_lower
            }
        
        # Check if city exists in variations
        for canonical_city, variations in self.city_mappings.items():
            if city_lower in [v.lower() for v in variations]:
                return {
                    'valid': True,
                    'suggestions': [],
                    'error': None,
                    'error_type': None,
                    'canonical_name': canonical_city
                }
        
        # Find similar cities using fuzzy matching
        suggestions = await self._find_similar_cities_async(city_lower)
        
        return {
            'valid': False,
            'suggestions': suggestions,
            'error': f'City "{city}" not recognized',
            'error_type': 'unrecognized',
            'canonical_name': None
        }
    
    async def _find_similar_cities_async(self, city: str) -> List[Dict[str, Any]]:
        """Find similar cities using fuzzy matching"""
        # Run fuzzy matching in thread pool (CPU intensive)
        loop = asyncio.get_event_loop()
        suggestions = await loop.run_in_executor(
            None,
            self._find_similar_cities_sync,
            city
        )
        return suggestions
    
    def _find_similar_cities_sync(self, city: str) -> List[Dict[str, Any]]:
        """Synchronous fuzzy matching (runs in thread pool)"""
        suggestions = []
        
        # Find close matches in all variations
        close_matches = get_close_matches(
            city, 
            self.all_variations, 
            n=5, 
            cutoff=0.6
        )
        
        for match in close_matches:
            # Find the canonical city name
            canonical_city = None
            for canonical, variations in self.city_mappings.items():
                if match.lower() in [v.lower() for v in variations] or match.lower() == canonical:
                    canonical_city = canonical
                    break
            
            if canonical_city:
                airport_code = self.airport_codes.get(canonical_city, 'N/A')
                suggestions.append({
                    'city': canonical_city,
                    'airport_code': airport_code,
                    'match': match,
                    'confidence': 0.8  # High confidence for fuzzy matches
                })
        
        # If no fuzzy matches, suggest popular cities
        if not suggestions:
            popular_cities = [
                'mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad', 'kolkata',
                'dubai', 'singapore', 'london', 'new york', 'paris', 'tokyo'
            ]
            
            for popular_city in popular_cities[:3]:  # Top 3 popular cities
                airport_code = self.airport_codes.get(popular_city, 'N/A')
                suggestions.append({
                    'city': popular_city,
                    'airport_code': airport_code,
                    'match': popular_city,
                    'confidence': 0.5  # Medium confidence for popular suggestions
                })
        
        return suggestions
    
    async def generate_error_message_async(self, validation_result: Dict[str, Any]) -> str:
        """Generate user-friendly error messages"""
        from_city = validation_result['from']
        to_city = validation_result['to']
        
        error_parts = []
        
        # Handle from city errors
        if not from_city['valid']:
            if from_city['error_type'] == 'missing':
                error_parts.append("Please specify your departure city")
            elif from_city['error_type'] == 'unrecognized':
                if from_city['suggestions']:
                    suggestions = [s['city'].title() for s in from_city['suggestions'][:3]]
                    error_parts.append(f"Departure city not recognized. Did you mean: {', '.join(suggestions)}?")
                else:
                    error_parts.append("Departure city not recognized. Please try a different city.")
        
        # Handle to city errors
        if not to_city['valid']:
            if to_city['error_type'] == 'missing':
                error_parts.append("Please specify your destination city")
            elif to_city['error_type'] == 'unrecognized':
                if to_city['suggestions']:
                    suggestions = [s['city'].title() for s in to_city['suggestions'][:3]]
                    error_parts.append(f"Destination city not recognized. Did you mean: {', '.join(suggestions)}?")
                else:
                    error_parts.append("Destination city not recognized. Please try a different city.")
        
        # Combine error messages
        if len(error_parts) == 1:
            return error_parts[0]
        elif len(error_parts) == 2:
            return f"{error_parts[0]} Also, {error_parts[1].lower()}"
        else:
            return "Please provide valid departure and destination cities."
    
    async def suggest_alternatives_async(self, validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative city combinations"""
        alternatives = []
        
        from_city = validation_result['from']
        to_city = validation_result['to']
        
        # If both cities are invalid, suggest popular routes
        if not from_city['valid'] and not to_city['valid']:
            popular_routes = [
                {'from': 'mumbai', 'to': 'delhi', 'description': 'Mumbai to Delhi'},
                {'from': 'bangalore', 'to': 'chennai', 'description': 'Bangalore to Chennai'},
                {'from': 'delhi', 'to': 'dubai', 'description': 'Delhi to Dubai'},
                {'from': 'mumbai', 'to': 'singapore', 'description': 'Mumbai to Singapore'},
                {'from': 'delhi', 'to': 'london', 'description': 'Delhi to London'}
            ]
            
            for route in popular_routes:
                alternatives.append({
                    'from': route['from'],
                    'to': route['to'],
                    'description': route['description'],
                    'type': 'popular_route'
                })
        
        # If one city is valid, suggest destinations from/to that city
        elif from_city['valid'] and not to_city['valid']:
            # Suggest destinations from the valid city
            city_name = from_city.get('canonical_name', '')
            if city_name:
                destinations = await self._get_popular_destinations_async(city_name)
                for dest in destinations:
                    alternatives.append({
                        'from': city_name,
                        'to': dest['city'],
                        'description': f"{city_name.title()} to {dest['city'].title()}",
                        'type': 'destination_from_city'
                    })
        
        elif not from_city['valid'] and to_city['valid']:
            # Suggest origins to the valid city
            city_name = to_city.get('canonical_name', '')
            if city_name:
                origins = await self._get_popular_origins_async(city_name)
                for origin in origins:
                    alternatives.append({
                        'from': origin['city'],
                        'to': city_name,
                        'description': f"{origin['city'].title()} to {city_name.title()}",
                        'type': 'origin_to_city'
                    })
        
        return alternatives[:5]  # Limit to 5 suggestions
    
    async def _get_popular_destinations_async(self, from_city: str) -> List[Dict[str, Any]]:
        """Get popular destinations from a city"""
        # This could be enhanced with real data
        popular_destinations = {
            'mumbai': ['delhi', 'bangalore', 'dubai', 'london', 'singapore'],
            'delhi': ['mumbai', 'bangalore', 'dubai', 'london', 'new york'],
            'bangalore': ['mumbai', 'delhi', 'chennai', 'dubai', 'singapore'],
            'chennai': ['mumbai', 'delhi', 'bangalore', 'dubai', 'singapore'],
            'hyderabad': ['mumbai', 'delhi', 'bangalore', 'dubai', 'singapore'],
            'kolkata': ['mumbai', 'delhi', 'bangalore', 'dubai', 'singapore']
        }
        
        destinations = popular_destinations.get(from_city, ['mumbai', 'delhi', 'bangalore'])
        return [{'city': dest, 'airport_code': self.airport_codes.get(dest, 'N/A')} for dest in destinations]
    
    async def _get_popular_origins_async(self, to_city: str) -> List[Dict[str, Any]]:
        """Get popular origins to a city"""
        # This could be enhanced with real data
        popular_origins = {
            'mumbai': ['delhi', 'bangalore', 'chennai', 'hyderabad', 'kolkata'],
            'delhi': ['mumbai', 'bangalore', 'chennai', 'hyderabad', 'kolkata'],
            'bangalore': ['mumbai', 'delhi', 'chennai', 'hyderabad', 'kolkata'],
            'dubai': ['mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad'],
            'singapore': ['mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad'],
            'london': ['mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad']
        }
        
        origins = popular_origins.get(to_city, ['mumbai', 'delhi', 'bangalore'])
        return [{'city': origin, 'airport_code': self.airport_codes.get(origin, 'N/A')} for origin in origins]

# Global async error handler instance
_async_error_handler = None

async def get_async_error_handler() -> AsyncErrorHandler:
    """Get or create async error handler instance"""
    global _async_error_handler
    if _async_error_handler is None:
        _async_error_handler = AsyncErrorHandler()
    return _async_error_handler

# Async wrapper functions for backward compatibility
async def validate_cities_async(from_city: str, to_city: str) -> Dict[str, Any]:
    """Async wrapper for city validation"""
    handler = await get_async_error_handler()
    return await handler.validate_cities_async(from_city, to_city)

async def generate_error_message_async(validation_result: Dict[str, Any]) -> str:
    """Async wrapper for error message generation"""
    handler = await get_async_error_handler()
    return await handler.generate_error_message_async(validation_result)

async def suggest_alternatives_async(validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Async wrapper for alternative suggestions"""
    handler = await get_async_error_handler()
    return await handler.suggest_alternatives_async(validation_result)
