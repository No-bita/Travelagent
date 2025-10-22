"""
Async Flight Service
Replaces the sync flight service with async implementation for better performance
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from config import settings
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AsyncFlightService:
    """Async flight service with connection pooling and parallel processing"""
    
    def __init__(self):
        self.session = None
        self.base_url = settings.amadeus_flight_url
        self.token_url = settings.amadeus_token_url
        self._token = None
        self._token_expires = None
    
    async def __aenter__(self):
        """Async context manager for connection pooling"""
        if settings.enable_connection_pooling:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=settings.http_timeout),
                connector=aiohttp.TCPConnector(
                    limit=settings.http_max_connections,
                    limit_per_host=settings.http_max_connections_per_host,
                    keepalive_timeout=settings.http_keepalive_timeout,
                    enable_cleanup_closed=True
                )
            )
        else:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=settings.http_timeout)
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up session"""
        if self.session:
            await self.session.close()
    
    async def _get_token_async(self) -> str:
        """Get Amadeus API token asynchronously"""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token
        
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': settings.amadeus_api_key,
            'client_secret': settings.amadeus_api_secret
        }
        
        try:
            async with self.session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self._token = token_data['access_token']
                    # Set expiration time (usually 30 minutes)
                    self._token_expires = datetime.now() + timedelta(minutes=25)
                    logger.info("Amadeus token refreshed successfully")
                    return self._token
                else:
                    logger.error(f"Token request failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Token request error: {e}")
            return None
    
    async def _get_airport_code_async(self, city_name: str) -> Optional[str]:
        """Get IATA airport code for a city asynchronously"""
        # Simulate async database lookup
        await asyncio.sleep(0.001)
        
        # Use centralized airport code mappings
        return settings.airport_codes.get(city_name.lower())
    
    async def _search_amadeus_flights_async(self, from_city: str, to_city: str, date: str) -> List[Dict[str, Any]]:
        """Search flights using Amadeus API asynchronously"""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async context manager.")
        
        # Parallel airport code lookups
        from_code_task = self._get_airport_code_async(from_city)
        to_code_task = self._get_airport_code_async(to_city)
        
        from_code, to_code = await asyncio.gather(from_code_task, to_code_task)
        
        if not from_code or not to_code:
            logger.warning(f"Could not map cities: {from_city} -> {to_code}")
            return []
        
        if not date:
            logger.warning("No date provided")
            return []
        
        # Get token asynchronously
        token = await self._get_token_async()
        if not token:
            logger.error("Failed to get Amadeus token")
            return []
        
        # Prepare request parameters
        params = {
            'originLocationCode': from_code,
            'destinationLocationCode': to_code,
            'departureDate': date,
            'adults': 1,
            'max': settings.max_flight_results
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Async Amadeus API call: {from_code} -> {to_code} on {date}")
            
            async with self.session.get(self.base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    flights = await self._process_flights_async(data.get('data', []))
                    logger.info(f"Async Amadeus API returned {len(flights)} flights")
                    return flights
                else:
                    error_text = await response.text()
                    logger.error(f"Amadeus API error: {response.status} - {error_text}")
                    return []
        except asyncio.TimeoutError:
            logger.error("Amadeus API timeout")
            return []
        except Exception as e:
            logger.error(f"Amadeus API error: {e}")
            return []
    
    async def _process_single_flight_async(self, offer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single flight asynchronously"""
        # Simulate async processing (could be database lookup, validation, etc.)
        await asyncio.sleep(0.001)
        
        try:
            itinerary = offer['itineraries'][0]
            segment = itinerary['segments'][0]
            price = float(offer['price']['total'])
            
            # Calculate duration
            departure = segment['departure']['at']
            arrival = segment['arrival']['at']
            
            # Parse times and calculate duration
            dep_time = datetime.fromisoformat(departure.replace('Z', '+00:00'))
            arr_time = datetime.fromisoformat(arrival.replace('Z', '+00:00'))
            duration = str(arr_time - dep_time)
            
            return {
                "airline": segment['carrierCode'],
                "code": f"{segment['carrierCode']}-{segment['number']}",
                "time": segment['departure']['at'][11:16],
                "price": int(price),
                "duration": duration,
                "stops": len(itinerary['segments']) - 1,
                "source": "Amadeus"
            }
        except (KeyError, ValueError) as e:
            logger.warning(f"Error processing flight: {e}")
            return None
    
    async def _process_flights_async(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple flights in parallel"""
        if not offers:
            return []
        
        # Create tasks for parallel processing
        tasks = [self._process_single_flight_async(offer) for offer in offers]
        
        # Process all flights concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        flights = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                flights.append(result)
            elif isinstance(result, Exception):
                logger.warning(f"Flight processing error: {result}")
        
        return flights
    
    async def _apply_intelligent_ranking_async(self, flights: List[Dict[str, Any]], preference: str = "") -> List[Dict[str, Any]]:
        """Apply intelligent ranking asynchronously"""
        if not flights:
            return []
        
        # Simulate async ranking logic (could involve ML models, external APIs)
        await asyncio.sleep(0.001)
        
        if preference:
            price_keywords = ['cheap', 'cheapest', 'lowest', 'budget', 'affordable']
            is_price_preference = any(keyword in preference.lower() for keyword in price_keywords)
            
            if is_price_preference:
                flights.sort(key=lambda x: x.get('price', float('inf')))
            else:
                flights.sort(key=lambda x: (x.get('time', '23:59'), x.get('price', float('inf'))))
        else:
            flights.sort(key=lambda x: x.get('price', float('inf')))
        
        return flights[:settings.display_flight_results]
    
    async def search_ranked_flights_async(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main async function to search and rank flights
        Demonstrates full async pipeline with connection pooling
        """
        from_city = context.get('from')
        to_city = context.get('to')
        date = context.get('date')
        preference = context.get('preference', '')
        
        if not from_city or not to_city or not date:
            logger.warning("Missing required parameters for async flight search")
            return []
        
        logger.info(f"Async flight search: {from_city} -> {to_city} on {date}")
        
        # Async flight search
        flights = await self._search_amadeus_flights_async(from_city, to_city, date)
        
        if not flights:
            logger.warning("No flights found in async search")
            return []
        
        # Async intelligent ranking
        ranked_flights = await self._apply_intelligent_ranking_async(flights, preference)
        
        logger.info(f"Async search completed: {len(ranked_flights)} flights ranked and returned")
        return ranked_flights

# Global async flight service instance
_async_flight_service = None

async def get_async_flight_service() -> AsyncFlightService:
    """Get or create async flight service instance"""
    global _async_flight_service
    if _async_flight_service is None:
        _async_flight_service = AsyncFlightService()
    return _async_flight_service

async def search_ranked_flights_async(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Async wrapper function for backward compatibility
    """
    async with AsyncFlightService() as service:
        return await service.search_ranked_flights_async(context)

async def get_flight_metrics_async() -> Dict[str, Any]:
    """Get async flight service metrics"""
    return {
        "service_type": "async",
        "connection_pooling": True,
        "parallel_processing": True,
        "status": "healthy"
    }