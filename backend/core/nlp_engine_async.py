"""
Async NLP Engine
Replaces sync NLP engine with async processing and caching
"""

import asyncio
import redis.asyncio as redis
from typing import Dict, Any, List, Optional
import re
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from dateparser import parse as parse_date
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
from config import settings

logger = logging.getLogger(__name__)

class AsyncNLPEngine:
    """Async NLP engine with Redis caching and parallel processing"""
    
    def __init__(self):
        # Initialize caches with configurable settings
        self.intent_cache = TTLCache(maxsize=settings.nlp_cache_size, ttl=settings.nlp_cache_ttl)
        self.entity_cache = TTLCache(maxsize=settings.nlp_entity_cache_size, ttl=settings.nlp_entity_cache_ttl)
        self.language_cache = TTLCache(maxsize=settings.nlp_language_cache_size, ttl=settings.nlp_language_cache_ttl)
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=settings.nlp_thread_pool_workers)
        
        # Redis connection for distributed caching
        self.redis_pool = None
        
        # Use centralized patterns from configuration
        self.intent_patterns = settings.intent_patterns
        self.entity_patterns = settings.entity_patterns
        self.city_mappings = settings.city_mappings
    
    async def __aenter__(self):
        """Async context manager for Redis connection"""
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
            logger.info("Async NLP Redis connection created")
        except Exception as e:
            logger.warning(f"Failed to create NLP Redis connection: {e}. Using local cache only.")
            self.redis_pool = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up Redis connection"""
        if self.redis_pool:
            await self.redis_pool.aclose()
    
    async def _get_cached_result_async(self, key: str) -> Optional[Any]:
        """Get cached result from Redis or local cache"""
        # Try Redis first
        if self.redis_pool:
            try:
                data = await self.redis_pool.get(f"nlp:{key}")
                if data:
                    import json
                    return json.loads(data)
            except Exception as e:
                pass
        
        # Fallback to local cache
        return self.entity_cache.get(key)
    
    async def _cache_result_async(self, key: str, value: Any, ttl: int = None) -> None:
        """Cache result in Redis and local cache"""
        if ttl is None:
            ttl = settings.nlp_cache_ttl
        
        # Cache in Redis
        if self.redis_pool:
            try:
                import json
                await self.redis_pool.setex(f"nlp:{key}", ttl, json.dumps(value))
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Cache locally
        self.entity_cache[key] = value
    
    async def _detect_language_async(self, text: str) -> str:
        """Detect language asynchronously"""
        cache_key = f"lang:{hash(text)}"
        cached = await self._get_cached_result_async(cache_key)
        if cached:
            return cached
        
        # Simple language detection (in production, use proper NLP library)
        if any(word in text.lower() for word in ['flight', 'book', 'search', 'travel']):
            language = 'en'
        else:
            language = 'en'  # Default to English
        
        await self._cache_result_async(cache_key, language, settings.nlp_language_cache_ttl)
        return language
    
    async def _extract_intent_async(self, text: str, language: str = 'en') -> str:
        """Extract intent asynchronously"""
        cache_key = f"intent:{hash(text)}"
        cached = await self._get_cached_result_async(cache_key)
        if cached:
            return cached
        
        # Run intent extraction in thread pool (CPU intensive)
        loop = asyncio.get_event_loop()
        intent = await loop.run_in_executor(
            self.executor,
            self._extract_intent_sync,
            text,
            language
        )
        
        await self._cache_result_async(cache_key, intent, settings.nlp_entity_cache_ttl)
        return intent
    
    def _extract_intent_sync(self, text: str, language: str) -> str:
        """Synchronous intent extraction (runs in thread pool)"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.get(language, {}).items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent
        
        return 'search_flights'  # Default intent
    
    async def _extract_entities_async(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Extract entities asynchronously with parallel processing"""
        cache_key = f"entities:{hash(text)}"
        cached = await self._get_cached_result_async(cache_key)
        if cached:
            return cached
        
        # Run entity extraction in thread pool
        loop = asyncio.get_event_loop()
        entities = await loop.run_in_executor(
            self.executor,
            self._extract_entities_sync,
            text,
            language
        )
        
        await self._cache_result_async(cache_key, entities, settings.nlp_entity_cache_ttl)
        return entities
    
    def _extract_entities_sync(self, text: str, language: str) -> Dict[str, Any]:
        """Synchronous entity extraction (runs in thread pool)"""
        entities = {
            'from': '',
            'to': '',
            'date': '',
            'preference': ''
        }
        
        # Extract cities
        cities = self._extract_cities(text)
        if len(cities) >= 2:
            entities['from'] = cities[0]
            entities['to'] = cities[1]
        elif len(cities) == 1:
            # Try to determine if it's from or to based on context
            if 'from' in text.lower():
                entities['from'] = cities[0]
            else:
                entities['to'] = cities[0]
        
        # Extract date
        entities['date'] = self._extract_date(text)
        
        # Extract preference
        entities['preference'] = self._extract_preference(text)
        
        return entities
    
    def _extract_cities(self, text: str) -> List[str]:
        """Extract cities from text"""
        cities = []
        text_lower = text.lower()
        
        # Check for known city names
        for city, variations in self.city_mappings.items():
            for variation in variations:
                if variation in text_lower:
                    cities.append(city)
                    break
        
        return cities
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        # Use dateparser for natural language date parsing
        parsed_date = parse_date(text)
        if parsed_date:
            return parsed_date.strftime('%Y-%m-%d')
        return ''
    
    def _extract_preference(self, text: str) -> str:
        """Extract user preference from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cheap', 'cheapest', 'lowest', 'budget']):
            return 'cheapest'
        elif any(word in text_lower for word in ['fast', 'quick', 'earliest']):
            return 'earliest'
        elif any(word in text_lower for word in ['business', 'first', 'premium']):
            return 'business'
        
        return ''
    
    async def parse_user_input_async(self, text: str) -> Dict[str, Any]:
        """
        Main async function to parse user input with enhanced error handling
        Demonstrates full async pipeline with caching, parallel processing, and error handling
        """
        if not text or not text.strip():
            return {
                'intent': '', 
                'from': '', 
                'to': '', 
                'date': '', 
                'preference': '',
                'errors': {'missing_cities': True},
                'error_message': 'Please provide flight details (From, To, Date).'
            }
        
        try:
            # Parallel processing of language detection and intent extraction
            language_task = self._detect_language_async(text)
            intent_task = self._extract_intent_async(text)
            
            language, intent = await asyncio.gather(language_task, intent_task)
            
            # Extract entities asynchronously
            entities = await self._extract_entities_async(text, language)
            
            # Enhanced error handling for cities
            from_city = entities.get('from', '')
            to_city = entities.get('to', '')
            
            # Validate cities if they exist
            city_validation = None
            error_message = None
            suggestions = []
            
            if from_city or to_city:
                from core.error_handler_async import validate_cities_async, generate_error_message_async, suggest_alternatives_async
                
                city_validation = await validate_cities_async(from_city, to_city)
                
                if not city_validation['overall_valid']:
                    error_message = await generate_error_message_async(city_validation)
                    suggestions = await suggest_alternatives_async(city_validation)
            
            result = {
                'intent': intent,
                'from': from_city,
                'to': to_city,
                'date': entities.get('date', ''),
                'preference': entities.get('preference', ''),
                'language': language,
                'processed_at': datetime.now().isoformat(),
                'city_validation': city_validation,
                'error_message': error_message,
                'suggestions': suggestions,
                'has_errors': city_validation is not None and not city_validation['overall_valid']
            }
            
            logger.info(f"Async NLP processing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Async NLP processing failed: {e}")
            return {
                'intent': 'search_flights',
                'from': '',
                'to': '',
                'date': '',
                'preference': '',
                'language': 'en',
                'error': str(e)
            }

# Global async NLP engine instance
_async_nlp_engine = None

async def get_async_nlp_engine() -> AsyncNLPEngine:
    """Get or create async NLP engine instance"""
    global _async_nlp_engine
    if _async_nlp_engine is None:
        _async_nlp_engine = AsyncNLPEngine()
    return _async_nlp_engine

# Async wrapper function for backward compatibility
async def parse_user_input_async(text: str) -> Dict[str, Any]:
    """Async wrapper for NLP processing"""
    async with AsyncNLPEngine() as engine:
        return await engine.parse_user_input_async(text)
