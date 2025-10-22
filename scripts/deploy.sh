#!/bin/bash

# Travel Agent Production Deployment Script
# This script deploys the complete travel agent system with Docker Compose

set -e  # Exit on any error

echo "🚀 Starting Travel Agent Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from example..."
    if [ -f env.prod.example ]; then
        cp env.prod.example .env
        print_warning "Please edit .env file with your actual API keys and secrets."
        print_warning "Required: AMADEUS_API_KEY, AMADEUS_API_SECRET, SECRET_KEY"
    else
        print_error "env.prod.example file not found. Cannot create .env file."
        exit 1
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check API health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "API service is healthy"
else
    print_error "API service is not responding"
    docker-compose -f docker-compose.prod.yml logs api
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis service is healthy"
else
    print_error "Redis service is not responding"
    docker-compose -f docker-compose.prod.yml logs redis
    exit 1
fi

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U travel_user -d travelagent > /dev/null 2>&1; then
    print_success "PostgreSQL service is healthy"
else
    print_error "PostgreSQL service is not responding"
    docker-compose -f docker-compose.prod.yml logs postgres
    exit 1
fi

# Initialize database tables
print_status "Initializing database tables..."
docker-compose -f docker-compose.prod.yml exec api python -c "
from db.database import create_tables
create_tables()
print('Database tables created successfully')
"

# Test the API
print_status "Testing API endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "ok"; then
    print_success "Health endpoint working"
else
    print_error "Health endpoint failed"
fi

# Test chat endpoint
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"session_id": "deployment_test", "message": "Book Mumbai to Delhi tomorrow"}')

if echo "$CHAT_RESPONSE" | grep -q "Mila:"; then
    print_success "Chat endpoint working"
else
    print_warning "Chat endpoint may have issues"
    echo "Response: $CHAT_RESPONSE"
fi

# Show service status
print_status "Service Status:"
docker-compose -f docker-compose.prod.yml ps

# Show logs
print_status "Recent logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20

print_success "🎉 Travel Agent Production Deployment Complete!"
print_status "Services are running:"
print_status "  - API: http://localhost:8000"
print_status "  - Redis: localhost:6379"
print_status "  - PostgreSQL: localhost:5432"
print_status "  - Nginx: http://localhost:80"

print_status "Useful commands:"
print_status "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
print_status "  - Stop services: docker-compose -f docker-compose.prod.yml down"
print_status "  - Restart services: docker-compose -f docker-compose.prod.yml restart"
print_status "  - Scale API: docker-compose -f docker-compose.prod.yml up --scale api=3 -d"
