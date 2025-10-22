"""
City Recognition Service
Centralized city matching with comprehensive fuzzy search
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from difflib import get_close_matches
from config import settings

logger = logging.getLogger(__name__)

class CityService:
    """Centralized city recognition service with fuzzy matching"""
    
    def __init__(self):
        self.city_mappings = settings.city_mappings
        self.airport_codes = settings.airport_codes
        self.all_cities = list(self.city_mappings.keys())
        self.all_variations = []
        
        # Build comprehensive variation list
        for city, variations in self.city_mappings.items():
            self.all_variations.extend(variations)
            self.all_variations.append(city)
    
    async def find_city_match(self, input: str) -> Optional[Dict[str, Any]]:
        """Find city match with comprehensive fuzzy search"""
        if not input or not input.strip():
            return None
            
        input_clean = input.lower().strip()
        
        # 1. Direct city name match
        if input_clean in self.city_mappings:
            return self._create_city_result(input_clean, input_clean, 'exact')
        
        # 2. Alias match
        for canonical_city, variations in self.city_mappings.items():
            if input_clean in [v.lower() for v in variations]:
                return self._create_city_result(canonical_city, input_clean, 'alias')
        
        # 3. Airport code match
        if input_clean.upper() in self.airport_codes:
            canonical_city = self.airport_codes[input_clean.upper()]
            return self._create_city_result(canonical_city, input_clean, 'airport_code')
        
        # 4. Fuzzy match
        fuzzy_match = await self._fuzzy_match_async(input_clean)
        if fuzzy_match:
            return fuzzy_match
        
        return None
    
    async def _fuzzy_match_async(self, input: str) -> Optional[Dict[str, Any]]:
        """Fuzzy matching using Levenshtein distance"""
        # Run fuzzy matching in thread pool (CPU intensive)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._fuzzy_match_sync,
            input
        )
    
    def _fuzzy_match_sync(self, input: str) -> Optional[Dict[str, Any]]:
        """Synchronous fuzzy matching"""
        best_match = None
        best_score = 0.0
        threshold = 0.7
        
        # Check against all variations
        for variation in self.all_variations:
            score = self._calculate_similarity(input, variation.lower())
            if score > best_score and score >= threshold:
                best_score = score
                best_match = variation
        
        if best_match:
            # Find canonical city name
            canonical_city = None
            for city, variations in self.city_mappings.items():
                if best_match.lower() in [v.lower() for v in variations] or best_match.lower() == city:
                    canonical_city = city
                    break
            
            if canonical_city:
                return self._create_city_result(canonical_city, input, 'fuzzy', best_score)
        
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity using Levenshtein distance"""
        if not str1 or not str2:
            return 0.0
        
        longer = str1 if len(str1) > len(str2) else str2
        shorter = str2 if len(str1) > len(str2) else str1
        
        if len(longer) == 0:
            return 1.0
        
        distance = self._levenshtein_distance(longer, shorter)
        return (len(longer) - distance) / len(longer)
    
    def _levenshtein_distance(self, str1: str, str2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        matrix = [[0 for _ in range(len(str2) + 1)] for _ in range(len(str1) + 1)]
        
        for i in range(len(str1) + 1):
            matrix[i][0] = i
        for j in range(len(str2) + 1):
            matrix[0][j] = j
        
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1]
                else:
                    matrix[i][j] = min(
                        matrix[i-1][j-1] + 1,
                        matrix[i][j-1] + 1,
                        matrix[i-1][j] + 1
                    )
        
        return matrix[len(str1)][len(str2)]
    
    def _create_city_result(self, canonical_city: str, input: str, match_type: str, confidence: float = 1.0) -> Dict[str, Any]:
        """Create standardized city result"""
        airport_code = self.airport_codes.get(canonical_city, 'N/A')
        
        return {
            'canonical_name': canonical_city,
            'airport_code': airport_code,
            'input': input,
            'match_type': match_type,
            'confidence': confidence,
            'variations': self.city_mappings.get(canonical_city, [])
        }
    
    async def get_suggestions(self, input: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get city suggestions for unrecognized input"""
        suggestions = []
        
        # Find close matches
        close_matches = get_close_matches(
            input.lower(),
            self.all_variations,
            n=limit,
            cutoff=0.6
        )
        
        for match in close_matches:
            # Find canonical city
            canonical_city = None
            for city, variations in self.city_mappings.items():
                if match.lower() in [v.lower() for v in variations] or match.lower() == city:
                    canonical_city = city
                    break
            
            if canonical_city:
                suggestions.append(self._create_city_result(canonical_city, input, 'suggestion'))
        
        return suggestions[:limit]
    
    async def validate_cities(self, from_city: str, to_city: str) -> Dict[str, Any]:
        """Validate both cities and return comprehensive result"""
        from_match = await self.find_city_match(from_city) if from_city else None
        to_match = await self.find_city_match(to_city) if to_city else None
        
        return {
            'from': {
                'valid': from_match is not None,
                'city': from_match,
                'suggestions': await self.get_suggestions(from_city) if not from_match else []
            },
            'to': {
                'valid': to_match is not None,
                'city': to_match,
                'suggestions': await self.get_suggestions(to_city) if not to_match else []
            },
            'overall_valid': from_match is not None and to_match is not None
        }

# Global city service instance
_city_service = None

async def get_city_service() -> CityService:
    """Get or create city service instance"""
    global _city_service
    if _city_service is None:
        _city_service = CityService()
    return _city_service
