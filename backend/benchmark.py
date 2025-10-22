"""
Simple Performance Benchmark Script
Quick test to verify optimizations are working
"""

import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

def test_chat_endpoint():
    """Test the chat endpoint performance"""
    print("🧪 Testing Chat Endpoint Performance...")
    
    base_url = "http://localhost:8000"
    test_messages = [
        "Book flight from Mumbai to Delhi tomorrow",
        "I need tickets from Bangalore to Chennai next week",
        "Looking for evening flights from Pune to Goa",
        "Cancel my booking for flight AI-123",
        "Show me flights from Hyderabad to Kolkata"
    ]
    
    response_times = []
    
    for i, message in enumerate(test_messages):
        start_time = time.time()
        
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": message,
                "session_id": f"benchmark_{i}",
                "locale": "en-IN"
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Message {i+1}: {response_time:.3f}s - {len(data.get('flight_cards', []))} flights found")
            else:
                print(f"❌ Message {i+1}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Message {i+1}: Error - {e}")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 Performance Summary:")
        print(f"  • Average response time: {avg_time:.3f}s")
        print(f"  • Fastest response: {min_time:.3f}s")
        print(f"  • Slowest response: {max_time:.3f}s")
        print(f"  • Total requests: {len(response_times)}")
        
        return {
            "avg_response_time": avg_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "total_requests": len(response_times)
        }
    
    return None

def test_concurrent_requests():
    """Test concurrent request handling"""
    print("\n🚀 Testing Concurrent Request Handling...")
    
    base_url = "http://localhost:8000"
    
    def make_request(session_id):
        start_time = time.time()
        try:
            response = requests.post(f"{base_url}/chat", json={
                "message": f"Book flight from Mumbai to Delhi for session {session_id}",
                "session_id": f"concurrent_{session_id}",
                "locale": "en-IN"
            })
            end_time = time.time()
            return {
                "success": response.status_code == 200,
                "response_time": end_time - start_time,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": 0,
                "error": str(e)
            }
    
    # Test with 10 concurrent requests
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    total_time = end_time - start_time
    
    successful = sum(1 for r in results if r.get('success', False))
    response_times = [r.get('response_time', 0) for r in results if r.get('success', False)]
    
    print(f"📊 Concurrent Test Results:")
    print(f"  • Total time: {total_time:.3f}s")
    print(f"  • Successful requests: {successful}/10")
    print(f"  • Success rate: {(successful/10)*100:.1f}%")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        print(f"  • Average response time: {avg_time:.3f}s")
        print(f"  • Throughput: {10/total_time:.2f} requests/sec")
    
    return {
        "total_time": total_time,
        "successful_requests": successful,
        "success_rate": (successful/10)*100,
        "throughput": 10/total_time if total_time > 0 else 0
    }

def test_health_endpoints():
    """Test health and metrics endpoints"""
    print("\n🏥 Testing Health & Metrics Endpoints...")
    
    base_url = "http://localhost:8000"
    endpoints = [
        ("/health", "Health Check"),
        ("/metrics", "Performance Metrics"),
        ("/performance", "Performance Insights"),
        ("/optimize", "Optimization Suggestions")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}{endpoint}")
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                data_size = len(response.content)
                print(f"✅ {name}: {response_time:.3f}s ({data_size} bytes)")
                results[endpoint] = {
                    "status": "success",
                    "response_time": response_time,
                    "data_size": data_size
                }
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results[endpoint] = {
                    "status": "error",
                    "status_code": response.status_code
                }
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results[endpoint] = {
                "status": "error",
                "error": str(e)
            }
    
    return results

def main():
    """Run all benchmark tests"""
    print("🚀 Performance Optimization Benchmark")
    print("=" * 50)
    print("Make sure the server is running on http://localhost:8000")
    print("")
    
    # Test chat endpoint
    chat_results = test_chat_endpoint()
    
    # Test concurrent requests
    concurrent_results = test_concurrent_requests()
    
    # Test health endpoints
    health_results = test_health_endpoints()
    
    # Generate summary
    print("\n" + "=" * 50)
    print("📊 BENCHMARK SUMMARY")
    print("=" * 50)
    
    if chat_results:
        print(f"Chat Endpoint Performance:")
        print(f"  • Average response time: {chat_results['avg_response_time']:.3f}s")
        print(f"  • Response time range: {chat_results['min_response_time']:.3f}s - {chat_results['max_response_time']:.3f}s")
    
    if concurrent_results:
        print(f"Concurrent Request Handling:")
        print(f"  • Success rate: {concurrent_results['success_rate']:.1f}%")
        print(f"  • Throughput: {concurrent_results['throughput']:.2f} requests/sec")
    
    # Check if all health endpoints are working
    working_endpoints = sum(1 for r in health_results.values() if r.get('status') == 'success')
    total_endpoints = len(health_results)
    print(f"Health Endpoints:")
    print(f"  • Working endpoints: {working_endpoints}/{total_endpoints}")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    
    if chat_results and chat_results['avg_response_time'] < 1.0:
        print("✅ Chat endpoint performance: EXCELLENT (< 1s average)")
    elif chat_results and chat_results['avg_response_time'] < 2.0:
        print("✅ Chat endpoint performance: GOOD (< 2s average)")
    else:
        print("⚠️ Chat endpoint performance: NEEDS IMPROVEMENT (> 2s average)")
    
    if concurrent_results and concurrent_results['success_rate'] > 90:
        print("✅ Concurrent handling: EXCELLENT (> 90% success rate)")
    elif concurrent_results and concurrent_results['success_rate'] > 80:
        print("✅ Concurrent handling: GOOD (> 80% success rate)")
    else:
        print("⚠️ Concurrent handling: NEEDS IMPROVEMENT (< 80% success rate)")
    
    if working_endpoints == total_endpoints:
        print("✅ Health monitoring: EXCELLENT (all endpoints working)")
    elif working_endpoints >= total_endpoints * 0.75:
        print("✅ Health monitoring: GOOD (most endpoints working)")
    else:
        print("⚠️ Health monitoring: NEEDS IMPROVEMENT (many endpoints failing)")
    
    print(f"\n📁 Detailed results saved to: benchmark_results.json")
    
    # Save results
    benchmark_results = {
        "chat_results": chat_results,
        "concurrent_results": concurrent_results,
        "health_results": health_results,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('benchmark_results.json', 'w') as f:
        json.dump(benchmark_results, f, indent=2)

if __name__ == "__main__":
    main()
