"""
Data reconciliation system for handling contradictory flight data from multiple sources
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataQuality(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

@dataclass
class FlightData:
    """Standardized flight data structure"""
    airline: str
    code: str
    time: str
    price: int
    duration: str
    stops: int
    source: str
    quality: DataQuality = DataQuality.UNKNOWN
    confidence_score: float = 0.0
    last_updated: datetime = None

class DataReconciler:
    """Intelligent data reconciliation for conflicting flight information"""
    
    def __init__(self):
        self.source_reliability = {
            "Amadeus": 0.9,      # High reliability
            "Skyscanner": 0.8,   # Good reliability
            "Cleartrip": 0.7,    # Medium reliability
            "MakeMyTrip": 0.7,   # Medium reliability
            "Mock": 0.1,         # Low reliability (fallback)
        }
        
        self.price_tolerance = 0.15  # 15% price difference tolerance
        self.time_tolerance = 30     # 30 minutes time difference tolerance
    
    def reconcile_flight_data(self, flights_by_source: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Reconcile contradictory flight data from multiple sources
        
        Args:
            flights_by_source: Dict mapping source names to their flight data
            
        Returns:
            List of reconciled flight data with conflict resolution
        """
        logger.info(f"Reconciling data from {len(flights_by_source)} sources")
        
        # Group flights by similarity (same route, similar time)
        flight_groups = self._group_similar_flights(flights_by_source)
        
        reconciled_flights = []
        
        for group in flight_groups:
            if len(group) == 1:
                # No conflicts, use as-is
                reconciled_flights.append(self._enhance_flight_data(group[0]))
            else:
                # Multiple sources for same flight - reconcile
                reconciled = self._reconcile_conflicting_flights(group)
                reconciled_flights.append(reconciled)
        
        # Sort by confidence score and return top 3
        reconciled_flights.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        return reconciled_flights[:3]
    
    def _group_similar_flights(self, flights_by_source: Dict[str, List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        """Group flights that likely represent the same flight from different sources"""
        all_flights = []
        
        # Flatten all flights with source information
        for source, flights in flights_by_source.items():
            for flight in flights:
                flight['source'] = source
                flight['source_reliability'] = self.source_reliability.get(source, 0.5)
                all_flights.append(flight)
        
        # Group by airline and similar time
        groups = []
        used_flights = set()
        
        for i, flight in enumerate(all_flights):
            if i in used_flights:
                continue
                
            group = [flight]
            used_flights.add(i)
            
            # Find similar flights
            for j, other_flight in enumerate(all_flights[i+1:], i+1):
                if j in used_flights:
                    continue
                    
                if self._are_similar_flights(flight, other_flight):
                    group.append(other_flight)
                    used_flights.add(j)
            
            groups.append(group)
        
        return groups
    
    def _are_similar_flights(self, flight1: Dict[str, Any], flight2: Dict[str, Any]) -> bool:
        """Check if two flights are likely the same flight"""
        # Same airline
        if flight1.get('airline') != flight2.get('airline'):
            return False
        
        # Similar time (within tolerance)
        time1 = self._parse_time(flight1.get('time', ''))
        time2 = self._parse_time(flight2.get('time', ''))
        
        if time1 and time2:
            time_diff = abs((time1 - time2).total_seconds() / 60)  # minutes
            if time_diff > self.time_tolerance:
                return False
        
        # Similar price (within tolerance)
        price1 = flight1.get('price', 0)
        price2 = flight2.get('price', 0)
        
        if price1 > 0 and price2 > 0:
            price_diff = abs(price1 - price2) / max(price1, price2)
            if price_diff > self.price_tolerance:
                return False
        
        return True
    
    def _reconcile_conflicting_flights(self, flights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Reconcile conflicting data for the same flight"""
        if not flights:
            return {}
        
        if len(flights) == 1:
            return self._enhance_flight_data(flights[0])
        
        logger.info(f"Reconciling {len(flights)} conflicting flight records")
        
        # Price: Use most reliable source (no weighted average)
        most_reliable = max(flights, key=lambda x: x.get('source_reliability', 0.5))
        selected_price = most_reliable.get('price', 0)
        
        # Time: use most reliable source
        selected_time = most_reliable.get('time', '')
        
        # Duration: use most reliable source
        duration = most_reliable.get('duration', 'N/A')
        
        # Stops: use most reliable source
        stops = most_reliable.get('stops', 0)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(flights)
        
        # Determine data quality
        quality = self._determine_data_quality(flights, confidence)
        
        # Price analysis for transparency
        prices = [f.get('price', 0) for f in flights if f.get('price', 0) > 0]
        price_analysis = self._analyze_price_consistency(prices, selected_price)
        
        reconciled = {
            'airline': most_reliable.get('airline', ''),
            'code': most_reliable.get('code', ''),
            'time': selected_time,
            'price': int(selected_price),
            'duration': duration,
            'stops': stops,
            'source': f"Reconciled({len(flights)} sources)",
            'confidence_score': confidence,
            'data_quality': quality.value,
            'sources_used': [f.get('source') for f in flights],
            'price_analysis': price_analysis,
            'selected_source': most_reliable.get('source', 'Unknown'),
            'conflict_resolution': 'most_reliable_source'
        }
        
        logger.info(f"Reconciled flight: {reconciled['airline']} {reconciled['code']} "
                   f"₹{reconciled['price']} from {reconciled['selected_source']} "
                   f"(confidence: {confidence:.2f})")
        
        return reconciled
    
    def _calculate_confidence_score(self, flights: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on source agreement"""
        if not flights:
            return 0.0
        
        # Base confidence from source reliability
        base_confidence = max(flight.get('source_reliability', 0.5) for flight in flights)
        
        # Agreement bonus
        if len(flights) > 1:
            # Check price agreement
            prices = [f.get('price', 0) for f in flights if f.get('price', 0) > 0]
            if prices:
                price_variance = max(prices) - min(prices)
                price_agreement = max(0, 1 - (price_variance / max(prices)))
            else:
                price_agreement = 0.5
            
            # Check time agreement
            times = [self._parse_time(f.get('time', '')) for f in flights]
            times = [t for t in times if t]
            if times:
                time_variance = max((max(times) - min(times)).total_seconds() / 3600, 0)  # hours
                time_agreement = max(0, 1 - (time_variance / 2))  # 2-hour tolerance
            else:
                time_agreement = 0.5
            
            # Combine agreements
            agreement_bonus = (price_agreement + time_agreement) / 2
            confidence = base_confidence * 0.7 + agreement_bonus * 0.3
        else:
            confidence = base_confidence
        
        return min(1.0, max(0.0, confidence))
    
    def _determine_data_quality(self, flights: List[Dict[str, Any]], confidence: float) -> DataQuality:
        """Determine data quality based on confidence and source agreement"""
        if confidence >= 0.8:
            return DataQuality.HIGH
        elif confidence >= 0.6:
            return DataQuality.MEDIUM
        elif confidence >= 0.3:
            return DataQuality.LOW
        else:
            return DataQuality.UNKNOWN
    
    def _enhance_flight_data(self, flight: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance single flight data with quality metrics"""
        confidence = flight.get('source_reliability', 0.5)
        quality = self._determine_data_quality([flight], confidence)
        
        enhanced = flight.copy()
        enhanced.update({
            'confidence_score': confidence,
            'data_quality': quality.value,
            'sources_used': [flight.get('source', 'Unknown')],
            'conflict_resolution': 'single_source'
        })
        
        return enhanced
    
    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse time string to datetime object"""
        try:
            if not time_str:
                return None
            # Handle formats like "07:15", "18:20"
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
                return datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        except (ValueError, AttributeError):
            pass
        return None
    
    def _analyze_price_consistency(self, prices: List[int], selected_price: int) -> Dict[str, Any]:
        """Analyze price consistency and provide transparency"""
        if not prices or len(prices) < 2:
            return {
                'consistency': 'single_source',
                'variance': 0,
                'price_range': {'min': selected_price, 'max': selected_price}
            }
        
        min_price = min(prices)
        max_price = max(prices)
        variance = max_price - min_price
        variance_percentage = (variance / max_price) * 100 if max_price > 0 else 0
        
        # Determine consistency level
        if variance_percentage <= 5:
            consistency = 'high'
        elif variance_percentage <= 15:
            consistency = 'medium'
        else:
            consistency = 'low'
        
        return {
            'consistency': consistency,
            'variance': variance,
            'variance_percentage': round(variance_percentage, 1),
            'price_range': {'min': min_price, 'max': max_price},
            'selected_price': selected_price,
            'price_count': len(prices)
        }
    
    def get_reconciliation_report(self, flights_by_source: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate a reconciliation report"""
        total_sources = len(flights_by_source)
        total_flights = sum(len(flights) for flights in flights_by_source.values())
        
        # Count conflicts
        conflicts = 0
        for source, flights in flights_by_source.items():
            for flight in flights:
                # Check if this flight has conflicts with other sources
                for other_source, other_flights in flights_by_source.items():
                    if source != other_source:
                        for other_flight in other_flights:
                            if self._are_similar_flights(flight, other_flight):
                                conflicts += 1
                                break
        
        return {
            'total_sources': total_sources,
            'total_flights': total_flights,
            'conflicts_detected': conflicts,
            'reconciliation_needed': conflicts > 0,
            'source_reliability': self.source_reliability,
            'tolerance_settings': {
                'price_tolerance': self.price_tolerance,
                'time_tolerance': self.time_tolerance
            }
        }
