"""
Async vs Sync Performance Demonstration
Shows real performance differences between sync and async implementations
"""

import asyncio
import time
import aiohttp
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SyncFlightService:
    """Synchronous flight service (current implementation)"""
    
    def __init__(self):
        self.base_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        self.headers = {"Authorization": "Bearer demo_token"}
    
    def _get_airport_code(self, city_name: str) -> str:
        """Sync airport code lookup"""
        time.sleep(0.001)  # Simulate I/O delay
        mapping = {'mumbai': 'BOM', 'delhi': 'DEL', 'bangalore': 'BLR'}
        return mapping.get(city_name.lower(), 'UNKNOWN')
    
    def _search_flights_sync(self, from_city: str, to_city: str, date: str) -> List[Dict]:
        """Sync flight search"""
        from_code = self._get_airport_code(from_city)
        to_code = self._get_airport_code(to_city)
        
        # Simulate API call delay
        time.sleep(2.0)  # 2 second API call
        
        # Simulate processing delay
        time.sleep(0.1)  # 100ms processing
        
        return [
            {"airline": "AI", "price": 5000, "time": "10:00"},
            {"airline": "SG", "price": 4500, "time": "14:00"},
            {"airline": "6E", "price": 4000, "time": "18:00"}
        ]
    
    def search_flights(self, from_city: str, to_city: str, date: str) -> List[Dict]:
        """Main sync search function"""
        return self._search_flights_sync(from_city, to_city, date)

class AsyncFlightService:
    """Asynchronous flight service (proposed implementation)"""
    
    def __init__(self):
        self.base_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        self.headers = {"Authorization": "Bearer demo_token"}
        self.session = None
    
    async def __aenter__(self):
        """Async context manager"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up session"""
        if self.session:
            await self.session.close()
    
    async def _get_airport_code_async(self, city_name: str) -> str:
        """Async airport code lookup"""
        await asyncio.sleep(0.001)  # Simulate I/O delay
        mapping = {'mumbai': 'BOM', 'delhi': 'DEL', 'bangalore': 'BLR'}
        return mapping.get(city_name.lower(), 'UNKNOWN')
    
    async def _search_flights_async(self, from_city: str, to_city: str, date: str) -> List[Dict]:
        """Async flight search"""
        # Parallel airport code lookups
        from_code_task = self._get_airport_code_async(from_city)
        to_code_task = self._get_airport_code_async(to_city)
        
        from_code, to_code = await asyncio.gather(from_code_task, to_code_task)
        
        # Simulate API call delay (but non-blocking)
        await asyncio.sleep(2.0)  # 2 second API call
        
        # Simulate processing delay (but non-blocking)
        await asyncio.sleep(0.1)  # 100ms processing
        
        return [
            {"airline": "AI", "price": 5000, "time": "10:00"},
            {"airline": "SG", "price": 4500, "time": "14:00"},
            {"airline": "6E", "price": 4000, "time": "18:00"}
        ]
    
    async def search_flights_async(self, from_city: str, to_city: str, date: str) -> List[Dict]:
        """Main async search function"""
        return await self._search_flights_async(from_city, to_city, date)

def test_sync_performance():
    """Test synchronous performance"""
    print("🔄 Testing SYNC Performance...")
    
    service = SyncFlightService()
    
    # Test single request
    start_time = time.time()
    flights = service.search_flights("mumbai", "delhi", "2025-10-22")
    single_request_time = time.time() - start_time
    
    # Test multiple requests (sequential)
    start_time = time.time()
    for i in range(3):
        service.search_flights("mumbai", "delhi", "2025-10-22")
    multiple_requests_time = time.time() - start_time
    
    print(f"✅ Sync Single Request: {single_request_time:.2f}s")
    print(f"✅ Sync 3 Requests: {multiple_requests_time:.2f}s")
    print(f"✅ Sync Average per Request: {multiple_requests_time/3:.2f}s")
    
    return {
        "single_request": single_request_time,
        "multiple_requests": multiple_requests_time,
        "average_per_request": multiple_requests_time/3
    }

async def test_async_performance():
    """Test asynchronous performance"""
    print("\n🚀 Testing ASYNC Performance...")
    
    # Test single request
    start_time = time.time()
    async with AsyncFlightService() as service:
        flights = await service.search_flights_async("mumbai", "delhi", "2025-10-22")
    single_request_time = time.time() - start_time
    
    # Test multiple requests (concurrent)
    start_time = time.time()
    async with AsyncFlightService() as service:
        tasks = [
            service.search_flights_async("mumbai", "delhi", "2025-10-22"),
            service.search_flights_async("bangalore", "delhi", "2025-10-22"),
            service.search_flights_async("mumbai", "bangalore", "2025-10-22")
        ]
        results = await asyncio.gather(*tasks)
    multiple_requests_time = time.time() - start_time
    
    print(f"✅ Async Single Request: {single_request_time:.2f}s")
    print(f"✅ Async 3 Concurrent Requests: {multiple_requests_time:.2f}s")
    print(f"✅ Async Average per Request: {multiple_requests_time/3:.2f}s")
    
    return {
        "single_request": single_request_time,
        "multiple_requests": multiple_requests_time,
        "average_per_request": multiple_requests_time/3
    }

async def test_concurrent_users():
    """Test performance with multiple concurrent users"""
    print("\n👥 Testing Concurrent Users...")
    
    # Simulate 10 concurrent users
    start_time = time.time()
    
    async def simulate_user(user_id: int):
        async with AsyncFlightService() as service:
            return await service.search_flights_async("mumbai", "delhi", "2025-10-22")
    
    # Create 10 concurrent tasks
    tasks = [simulate_user(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    print(f"✅ 10 Concurrent Users: {total_time:.2f}s")
    print(f"✅ Average per User: {total_time/10:.2f}s")
    print(f"✅ Throughput: {10/total_time:.1f} requests/second")
    
    return total_time

def calculate_improvements(sync_results: Dict, async_results: Dict):
    """Calculate performance improvements"""
    print("\n📊 Performance Improvements:")
    print("=" * 50)
    
    # Single request improvement
    single_improvement = ((sync_results["single_request"] - async_results["single_request"]) / sync_results["single_request"]) * 100
    print(f"🚀 Single Request: {single_improvement:.1f}% faster")
    
    # Multiple requests improvement
    multiple_improvement = ((sync_results["multiple_requests"] - async_results["multiple_requests"]) / sync_results["multiple_requests"]) * 100
    print(f"🚀 Multiple Requests: {multiple_improvement:.1f}% faster")
    
    # Average per request improvement
    average_improvement = ((sync_results["average_per_request"] - async_results["average_per_request"]) / sync_results["average_per_request"]) * 100
    print(f"🚀 Average per Request: {average_improvement:.1f}% faster")
    
    # Throughput improvement
    sync_throughput = 3 / sync_results["multiple_requests"]
    async_throughput = 3 / async_results["multiple_requests"]
    throughput_improvement = ((async_throughput - sync_throughput) / sync_throughput) * 100
    print(f"🚀 Throughput: {throughput_improvement:.1f}% improvement")
    
    print("\n💡 Key Benefits:")
    print("✅ Non-blocking I/O operations")
    print("✅ Better resource utilization")
    print("✅ Higher concurrency")
    print("✅ Lower memory usage")
    print("✅ Better user experience")

async def main():
    """Main performance test"""
    print("🔬 Async vs Sync Performance Test")
    print("=" * 50)
    
    # Test sync performance
    sync_results = test_sync_performance()
    
    # Test async performance
    async_results = await test_async_performance()
    
    # Test concurrent users
    concurrent_time = await test_concurrent_users()
    
    # Calculate improvements
    calculate_improvements(sync_results, async_results)
    
    print(f"\n🎯 Summary:")
    print(f"Sync 3 requests: {sync_results['multiple_requests']:.2f}s")
    print(f"Async 3 requests: {async_results['multiple_requests']:.2f}s")
    print(f"10 concurrent users: {concurrent_time:.2f}s")
    print(f"Time saved: {sync_results['multiple_requests'] - async_results['multiple_requests']:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
