"""
LLM Integration Service
Supports multiple LLM providers: OpenAI, Anthropic Claude, and local models
"""

import json
import logging
from typing import Dict, Any, Optional, List
import requests
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"

@dataclass
class LLMConfig:
    provider: LLMProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.1

class LLMService:
    """Service for integrating with various LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()
        
    def extract_intent_and_entities(self, message: str, language: str = "english") -> Dict[str, Any]:
        """Extract intent and entities using LLM"""
        
        if self.config.provider == LLMProvider.MOCK:
            return self._mock_extraction(message, language)
        
        try:
            prompt = self._create_extraction_prompt(message, language)
            response = self._call_llm(prompt)
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._fallback_extraction(message, language)
    
    def _create_extraction_prompt(self, message: str, language: str) -> str:
        """Create structured prompt for intent and entity extraction"""
        
        return f"""You are an AI assistant for a travel booking system. Extract intent and entities from the user message.

User Message: "{message}"
Language: {language}

Extract the following information:
1. Intent: book_flight, modify, confirm, search, help, cancel
2. From City: origin city (normalize to standard names)
3. To City: destination city (normalize to standard names)
4. Date: travel date (normalize to relative terms like "tomorrow", "next week")
5. Time Preference: morning, evening, any
6. Number of Passengers: default 1
7. Class: economy, business, first
8. Budget: price range if mentioned
9. Airline Preference: specific airline if mentioned
10. Special Requirements: any special needs

Respond in JSON format:
{{
    "intent": "book_flight",
    "from": "mumbai",
    "to": "delhi", 
    "date": "tomorrow",
    "preference": "morning",
    "passengers": 1,
    "class": "economy",
    "budget": null,
    "airline": null,
    "special_requirements": null,
    "confidence": 0.95
}}

Only include fields that are explicitly mentioned or can be reasonably inferred.
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM provider"""
        
        if self.config.provider == LLMProvider.OPENAI:
            return self._call_openai(prompt)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(prompt)
        elif self.config.provider == LLMProvider.LOCAL:
            return self._call_local(prompt)
        else:
            return self._mock_extraction("", "english")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "You are a helpful travel booking assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.session.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = self.session.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    def _call_local(self, prompt: str) -> str:
        """Call local LLM API"""
        
        if not self.config.base_url:
            raise ValueError("Base URL required for local LLM")
        
        url = f"{self.config.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.session.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _mock_extraction(self, message: str, language: str) -> Dict[str, Any]:
        """Mock extraction for testing"""
        
        # Simple rule-based extraction as fallback
        lower = message.lower()
        result = {"intent": "book_flight", "confidence": 0.8}
        
        # Extract cities
        cities = ["mumbai", "delhi", "bangalore", "chennai", "hyderabad", "kolkata", "pune", "goa", "kochi", "ahmedabad"]
        found_cities = [city for city in cities if city in lower]
        
        if len(found_cities) >= 2:
            result["from"] = found_cities[0]
            result["to"] = found_cities[1]
        elif len(found_cities) == 1:
            result["to"] = found_cities[0]
        
        # Extract date
        if "tomorrow" in lower or "kal" in lower:
            result["date"] = "tomorrow"
        elif "today" in lower or "aaj" in lower:
            result["date"] = "today"
        elif "next week" in lower or "agla hafta" in lower:
            result["date"] = "next_week"
        
        # Extract preference
        if "morning" in lower or "subah" in lower:
            result["preference"] = "morning"
        elif "evening" in lower or "shaam" in lower:
            result["preference"] = "evening"
        
        return result
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and validate"""
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            
            # Validate and normalize
            if "intent" not in result:
                result["intent"] = "book_flight"
            
            # Normalize city names
            if "from" in result:
                result["from"] = self._normalize_city(result["from"])
            if "to" in result:
                result["to"] = self._normalize_city(result["to"])
            
            # Normalize date
            if "date" in result:
                result["date"] = self._normalize_date(result["date"])
            
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._fallback_extraction("", "english")
    
    def _fallback_extraction(self, message: str, language: str) -> Dict[str, Any]:
        """Fallback extraction when LLM fails"""
        
        return {
            "intent": "book_flight",
            "confidence": 0.5,
            "language": language,
            "original_text": message
        }
    
    def _normalize_city(self, city: str) -> str:
        """Normalize city names"""
        
        city_mapping = {
            "bombay": "mumbai",
            "bengaluru": "bangalore",
            "madras": "chennai",
            "calcutta": "kolkata",
            "cochin": "kochi"
        }
        
        city_lower = city.lower()
        return city_mapping.get(city_lower, city_lower)
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date strings"""
        
        if not date_str:
            return "tomorrow"
        
        date_lower = date_str.lower()
        
        if date_lower in ["today", "aaj"]:
            return "today"
        elif date_lower in ["tomorrow", "kal"]:
            return "tomorrow"
        elif date_lower in ["day after tomorrow", "parso"]:
            return "day_after_tomorrow"
        elif date_lower in ["next week", "agla hafta"]:
            return "next_week"
        elif date_lower in ["next month", "agla mahina"]:
            return "next_month"
        
        return "tomorrow"

# Factory function to create LLM service
def create_llm_service(provider: str, api_key: str, model: str, **kwargs) -> LLMService:
    """Create LLM service with specified provider"""
    
    config = LLMConfig(
        provider=LLMProvider(provider),
        api_key=api_key,
        model=model,
        **kwargs
    )
    
    return LLMService(config)

# Default service for testing
def get_default_llm_service() -> LLMService:
    """Get default LLM service for testing"""
    
    config = LLMConfig(
        provider=LLMProvider.MOCK,
        api_key="test",
        model="mock"
    )
    
    return LLMService(config)
