"""
Async Response Generator
Replaces sync response generator with async processing and caching
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from config import settings

logger = logging.getLogger(__name__)

class AsyncResponseGenerator:
    """Async response generator with parallel processing"""
    
    def __init__(self):
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def __aenter__(self):
        """Async context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        self.executor.shutdown(wait=True)
    
    def _chip(self, context: Dict[str, Any]) -> str:
        """Generate context chip for UI"""
        fr = context.get("from")
        to = context.get("to")
        date = context.get("date")
        pref = context.get("preference")
        parts = []
        if fr and to:
            parts.append(f"🛫 {fr} → {to}")
        if date:
            parts.append(f"📅 {date}")
        if pref:
            parts.append(f"✨ {pref.title()}")
        return " | ".join(parts)

    async def prompt_for_missing_slots_async(self, context: Dict[str, Any]) -> str:
        """Async prompt for missing slots with enhanced error handling"""
        # Check for city validation errors first
        if context.get('has_errors') and context.get('error_message'):
            return context['error_message']
        
        # Check for suggestions
        if context.get('suggestions'):
            suggestions = context['suggestions'][:3]  # Top 3 suggestions
            suggestion_text = ", ".join([f"{s['from'].title()} to {s['to'].title()}" for s in suggestions])
            return f"Here are some popular routes you might like: {suggestion_text}"
        
        # Standard missing slot prompts
        missing = [k for k in ["intent", "from", "to", "date"] if not context.get(k)]
        if "from" in missing and "to" in missing:
            return "Where would you like to fly from and to? (From → To)"
        if "date" in missing:
            return "When would you like to travel? You can specify a date (e.g., 'tomorrow', 'next Friday') or I can show you the best options for the next week."
        return "Please provide flight details: From, To, Date."

    async def format_flight_options_async(self, context: Dict[str, Any], flights: List[Dict[str, Any]]) -> str:
        """Async flight options formatting with parallel processing"""
        if not flights:
            return "No flights found. Would you like to try a different time or airline?"
        
        # Run flight card processing in thread pool (CPU intensive)
        loop = asyncio.get_event_loop()
        flight_cards = await loop.run_in_executor(
            self.executor,
            self._process_flight_cards_sync,
            flights
        )
        
        # Generate summary asynchronously
        summary = await self._generate_flight_summary_async(context, flight_cards)
        return summary
    
    def _process_flight_cards_sync(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synchronous flight card processing (runs in thread pool)"""
        flight_cards = []
        for f in flights:
            duration = f.get('duration', 'N/A')
            stops = f.get('stops', 0)
            stops_text = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
            
            # Determine flight class based on price
            price = f.get('price', 0)
            if price < 3000:
                flight_class = "Economy"
                class_icon = "🛫"
            elif price < 6000:
                flight_class = "Premium Economy"
                class_icon = "✈️"
            else:
                flight_class = "Business"
                class_icon = "🛩️"
            
            # Create flight card data
            card_data = {
                "airline": f.get('airline', ''),
                "code": f.get('code', ''),
                "time": f.get('time', ''),
                "price": price,
                "duration": duration,
                "stops": stops_text,
                "class": flight_class,
                "class_icon": class_icon,
                "source": f.get('source', 'Unknown'),
                "confidence": f.get('confidence_score', 0.8),
                "data_quality": f.get('data_quality', 'medium')
            }
            flight_cards.append(card_data)
        
        # Sort by price (cheapest first)
        flight_cards.sort(key=lambda x: x['price'])
        return flight_cards

    async def _generate_flight_summary_async(self, context: Dict[str, Any], flight_cards: List[Dict[str, Any]]) -> str:
        """Generate flight summary asynchronously"""
        total_flights = len(flight_cards)
        if total_flights == 0:
            return "No flights found. Would you like to try a different time or airline?"
        
        cheapest_price = min(card['price'] for card in flight_cards)
        most_expensive = max(card['price'] for card in flight_cards)
        
        # Get user context for personalization
        from_city = context.get('from', '').title()
        to_city = context.get('to', '').title()
        date = context.get('date', '')
        preference = context.get('preference', '')
        
        # Create dynamic summary based on what the user asked for
        if not date or date == "WEEK_SEARCH":
            if total_flights > 0:
                # Get date range from flight data
                earliest_date = min(flight.get('search_date', '') for flight in flight_cards if flight.get('search_date'))
                latest_date = max(flight.get('search_date', '') for flight in flight_cards if flight.get('search_date'))
                date_range_info = f"from {earliest_date} to {latest_date}" if earliest_date != latest_date else f"on {earliest_date}"
            else:
                date_range_info = "across multiple dates"
            
            if preference and 'cheap' in preference.lower():
                summary = f"Found {total_flights} cheapest flights from {from_city} to {to_city} {date_range_info} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
            elif total_flights == 1:
                summary = f"Perfect! Found 1 flight from {from_city} to {to_city} {date_range_info} for ₹{cheapest_price:,}"
            elif total_flights <= 3:
                summary = f"Great! Found {total_flights} flights from {from_city} to {to_city} {date_range_info} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
            else:
                summary = f"Found {total_flights} flight options from {from_city} to {to_city} {date_range_info} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
        else:  # Specific date provided
            if preference:
                summary = f"Found {total_flights} {preference.lower()} flights from {from_city} to {to_city} on {date} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
            elif total_flights == 1:
                summary = f"Perfect! Found 1 flight from {from_city} to {to_city} on {date} for ₹{cheapest_price:,}"
            elif total_flights <= 3:
                summary = f"Great! Found {total_flights} flights from {from_city} to {to_city} on {date} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
            else:
                summary = f"Found {total_flights} flight options from {from_city} to {to_city} on {date} | ₹{cheapest_price:,} - ₹{most_expensive:,}"
        
        return summary

    async def get_flight_cards_data_async(self, context: Dict[str, Any], flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Async flight cards data generation with parallel processing"""
        if not flights:
            return []
        
        # Run flight card processing in thread pool
        loop = asyncio.get_event_loop()
        flight_cards = await loop.run_in_executor(
            self.executor,
            self._process_flight_cards_detailed_sync,
            flights
        )
        
        # Mark cheapest and fastest asynchronously
        if flight_cards:
            flight_cards[0]['is_cheapest'] = True
            
            # Find fastest (shortest duration)
            fastest = min(flight_cards, key=lambda x: x['duration'])
            fastest['is_fastest'] = True
        
        return flight_cards
    
    def _process_flight_cards_detailed_sync(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synchronous detailed flight card processing (runs in thread pool)"""
        flight_cards = []
        for f in flights:
            duration = f.get('duration', 'N/A')
            stops = f.get('stops', 0)
            stops_text = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
            
            # Determine flight class based on price
            price = f.get('price', 0)
            if price < 3000:
                flight_class = "Economy"
                class_icon = "🛫"
                class_color = "#4CAF50"
            elif price < 6000:
                flight_class = "Premium Economy"
                class_icon = "✈️"
                class_color = "#2196F3"
            else:
                flight_class = "Business"
                class_icon = "🛩️"
                class_color = "#FF9800"
            
            # Determine airline logo/color
            airline = f.get('airline', '')
            airline_colors = {
                'AI': {'color': '#FF6B35', 'name': 'Air India'},
                '6E': {'color': '#FF1744', 'name': 'IndiGo'},
                'QP': {'color': '#00BCD4', 'name': 'Akasa Air'},
                'SG': {'color': '#9C27B0', 'name': 'SpiceJet'},
                'G8': {'color': '#FF5722', 'name': 'GoAir'}
            }
            
            airline_info = airline_colors.get(airline, {'color': '#607D8B', 'name': airline})
            
            # Create flight card data
            card_data = {
                "id": f"{airline}_{f.get('code', '')}_{f.get('time', '')}",
                "airline": airline,
                "airline_name": airline_info['name'],
                "airline_color": airline_info['color'],
                "code": f.get('code', ''),
                "time": f.get('time', ''),
                "price": price,
                "formatted_price": f"₹{price:,}",
                "duration": duration,
                "stops": stops_text,
                "stops_count": stops,
                "class": flight_class,
                "class_icon": class_icon,
                "class_color": class_color,
                "source": f.get('source', 'Unknown'),
                "confidence": f.get('confidence_score', 0.8),
                "data_quality": f.get('data_quality', 'medium'),
                "is_direct": stops == 0,
                "is_cheapest": False,  # Will be set after sorting
                "is_fastest": False,   # Will be set after sorting
                "booking_url": f"upi://pay?pa=travel@agent&pn=Travel Agent&am={price}&cu=INR&tn=Flight {f.get('code', '')}"
            }
            flight_cards.append(card_data)
        
        # Sort by price (cheapest first)
        flight_cards.sort(key=lambda x: x['price'])
        return flight_cards

    async def format_payment_prompt_async(self, context: Dict[str, Any], payment: Dict[str, Any]) -> str:
        """Async payment prompt formatting"""
        return f"Ready to pay? Tap UPI link: {payment.get('upi_link')}"

    async def format_confirmation_async(self, context: Dict[str, Any], ticket: Dict[str, Any]) -> str:
        """Async confirmation formatting"""
        return (
            f"Booked! PNR {ticket['pnr']}. Route {ticket['route']} on {ticket['date']}. "
            "Ticket and receipt sent. ✈️"
        )

    async def state_summary_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Async state summary generation"""
        return {
            "intent": context.get("intent"),
            "from": context.get("from"),
            "to": context.get("to"),
            "date": context.get("date"),
            "preference": context.get("preference"),
            "booking_stage": context.get("booking_stage"),
        }

    async def suggest_actions_async(self, context: Dict[str, Any]) -> List[str]:
        """Async action suggestions"""
        actions: List[str] = []
        if context.get("booking_stage") == "review":
            actions = ["Confirm & Pay", "Change date", "Change destination"]
        elif context.get("booking_stage") in ("collect_slots", None):
            actions = ["Set date to tomorrow", "Evening flights"]
        elif context.get("booking_stage") == "payment":
            actions = ["Retry payment", "Change payment method"]
        return actions

    async def safe_fallback_async(self) -> str:
        """Async safe fallback response"""
        return "I didn't understand. Please provide flight details (From, To, Date)."

# Global async response generator instance
_async_response_generator = None

async def get_async_response_generator() -> AsyncResponseGenerator:
    """Get or create async response generator instance"""
    global _async_response_generator
    if _async_response_generator is None:
        _async_response_generator = AsyncResponseGenerator()
    return _async_response_generator

# Async wrapper functions for backward compatibility
async def prompt_for_missing_slots_async(context: Dict[str, Any]) -> str:
    """Async wrapper for missing slots prompt"""
    async with AsyncResponseGenerator() as generator:
        return await generator.prompt_for_missing_slots_async(context)

async def format_flight_options_async(context: Dict[str, Any], flights: List[Dict[str, Any]]) -> str:
    """Async wrapper for flight options formatting"""
    async with AsyncResponseGenerator() as generator:
        return await generator.format_flight_options_async(context, flights)

async def get_flight_cards_data_async(context: Dict[str, Any], flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Async wrapper for flight cards data"""
    async with AsyncResponseGenerator() as generator:
        return await generator.get_flight_cards_data_async(context, flights)

async def format_payment_prompt_async(context: Dict[str, Any], payment: Dict[str, Any]) -> str:
    """Async wrapper for payment prompt"""
    async with AsyncResponseGenerator() as generator:
        return await generator.format_payment_prompt_async(context, payment)

async def format_confirmation_async(context: Dict[str, Any], ticket: Dict[str, Any]) -> str:
    """Async wrapper for confirmation formatting"""
    async with AsyncResponseGenerator() as generator:
        return await generator.format_confirmation_async(context, ticket)

async def state_summary_async(context: Dict[str, Any]) -> Dict[str, Any]:
    """Async wrapper for state summary"""
    async with AsyncResponseGenerator() as generator:
        return await generator.state_summary_async(context)

async def suggest_actions_async(context: Dict[str, Any]) -> List[str]:
    """Async wrapper for action suggestions"""
    async with AsyncResponseGenerator() as generator:
        return await generator.suggest_actions_async(context)

async def safe_fallback_async() -> str:
    """Async wrapper for safe fallback"""
    async with AsyncResponseGenerator() as generator:
        return await generator.safe_fallback_async()
