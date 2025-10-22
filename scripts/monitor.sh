#!/bin/bash

# Travel Agent Production Monitoring Script
# This script monitors the health and performance of all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔍 Travel Agent Production Monitoring"
echo "====================================="

# Check if services are running
print_status "Checking service status..."

# API Health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "✅ API Service: Healthy"
    API_STATUS="healthy"
else
    print_error "❌ API Service: Unhealthy"
    API_STATUS="unhealthy"
fi

# Detailed API Health
if [ "$API_STATUS" = "healthy" ]; then
    DETAILED_HEALTH=$(curl -s http://localhost:8000/health/detailed 2>/dev/null || echo "{}")
    echo "   Flight APIs: $(echo $DETAILED_HEALTH | jq -r '.flight_apis.available_sources // "N/A"' 2>/dev/null || echo "N/A")"
    echo "   Cache Entries: $(echo $DETAILED_HEALTH | jq -r '.flight_apis.cache_entries // "N/A"' 2>/dev/null || echo "N/A")"
fi

# Redis Health
if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping > /dev/null 2>&1; then
    print_success "✅ Redis Service: Healthy"
    REDIS_STATUS="healthy"
else
    print_error "❌ Redis Service: Unhealthy"
    REDIS_STATUS="unhealthy"
fi

# PostgreSQL Health
if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U travel_user -d travelagent > /dev/null 2>&1; then
    print_success "✅ PostgreSQL Service: Healthy"
    POSTGRES_STATUS="healthy"
else
    print_error "❌ PostgreSQL Service: Unhealthy"
    POSTGRES_STATUS="unhealthy"
fi

# Container Status
print_status "Container Status:"
docker-compose -f docker-compose.prod.yml ps

# Resource Usage
print_status "Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Database Statistics
if [ "$POSTGRES_STATUS" = "healthy" ]; then
    print_status "Database Statistics:"
    
    # Get table counts
    USER_COUNT=$(docker-compose -f docker-compose.prod.yml exec postgres psql -U travel_user -d travelagent -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ' || echo "N/A")
    BOOKING_COUNT=$(docker-compose -f docker-compose.prod.yml exec postgres psql -U travel_user -d travelagent -t -c "SELECT COUNT(*) FROM bookings;" 2>/dev/null | tr -d ' ' || echo "N/A")
    
    echo "   Users: $USER_COUNT"
    echo "   Bookings: $BOOKING_COUNT"
fi

# Redis Statistics
if [ "$REDIS_STATUS" = "healthy" ]; then
    print_status "Redis Statistics:"
    docker-compose -f docker-compose.prod.yml exec redis redis-cli info memory | grep -E "(used_memory_human|maxmemory_human)" || echo "   Memory info not available"
    docker-compose -f docker-compose.prod.yml exec redis redis-cli info keyspace | grep -E "db0" || echo "   No keyspace info"
fi

# Recent Logs
print_status "Recent Error Logs:"
docker-compose -f docker-compose.prod.yml logs --tail=10 | grep -i error || echo "   No recent errors"

# Performance Test
print_status "Performance Test:"
echo "Testing API response time..."

START_TIME=$(date +%s%N)
curl -s http://localhost:8000/health > /dev/null
END_TIME=$(date +%s%N)
RESPONSE_TIME=$(( (END_TIME - START_TIME) / 1000000 ))

if [ $RESPONSE_TIME -lt 1000 ]; then
    print_success "✅ API Response Time: ${RESPONSE_TIME}ms (Excellent)"
elif [ $RESPONSE_TIME -lt 3000 ]; then
    print_warning "⚠️  API Response Time: ${RESPONSE_TIME}ms (Good)"
else
    print_error "❌ API Response Time: ${RESPONSE_TIME}ms (Slow)"
fi

# Chat API Test
print_status "Testing Chat API:"
CHAT_START=$(date +%s%N)
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"session_id": "monitor_test", "message": "Book Mumbai to Delhi tomorrow"}' \
    --max-time 10)
CHAT_END=$(date +%s%N)
CHAT_TIME=$(( (CHAT_END - CHAT_START) / 1000000 ))

if echo "$CHAT_RESPONSE" | grep -q "Mila:"; then
    print_success "✅ Chat API: Working (${CHAT_TIME}ms)"
else
    print_error "❌ Chat API: Failed"
    echo "Response: $CHAT_RESPONSE"
fi

# Summary
echo ""
echo "📊 Monitoring Summary"
echo "===================="

if [ "$API_STATUS" = "healthy" ] && [ "$REDIS_STATUS" = "healthy" ] && [ "$POSTGRES_STATUS" = "healthy" ]; then
    print_success "🎉 All services are healthy!"
    exit 0
else
    print_error "⚠️  Some services are unhealthy. Check logs above."
    exit 1
fi
