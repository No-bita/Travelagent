# Docker Setup Guide for Travel Agent

## Prerequisites

### 1. Install Docker Desktop
```bash
# macOS (using Homebrew)
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop/
```

### 2. Start Docker Desktop
- Open Docker Desktop application
- Wait for it to start (whale icon in menu bar)
- Verify: `docker --version`

## Quick Start

### 1. Start All Services
```bash
# From project root
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Test the System
```bash
# Health check
curl http://localhost:8000/health

# Detailed health with Redis/PostgreSQL
curl http://localhost:8000/health/detailed

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "docker_test", "message": "Book Mumbai to Delhi tomorrow"}'
```

### 3. View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs redis
docker-compose logs postgres
```

## Services Overview

### API Service (Port 8000)
- **Image**: Built from `./backend/Dockerfile`
- **Dependencies**: Redis, PostgreSQL
- **Environment**: 
  - `REDIS_URL=redis://redis:6379/0`
  - `POSTGRES_DSN=postgresql://user:password@postgres:5432/travelagent`

### Redis Service (Port 6379)
- **Image**: `redis:7`
- **Purpose**: Session storage, caching
- **Persistence**: Volume `redis_data`

### PostgreSQL Service (Port 5432)
- **Image**: `postgres:15`
- **Database**: `travelagent`
- **Credentials**: `user:password`
- **Persistence**: Volume `postgres_data`

## Development Workflow

### 1. Development Mode
```bash
# Start with live reload
docker-compose up

# Rebuild after code changes
docker-compose up --build
```

### 2. Production Mode
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Database Management
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U user -d travelagent

# Create tables
docker-compose exec api python -c "from db.database import create_tables; create_tables()"
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill existing processes
pkill -f uvicorn
docker-compose down

# Start fresh
docker-compose up -d
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### 3. Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Reset Everything
```bash
# Stop and remove all containers
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Production Deployment

### 1. Environment Variables
Create `.env` file:
```bash
# API Keys
AMADEUS_API_KEY=your_production_key
AMADEUS_API_SECRET=your_production_secret
CLEARTRIP_API_KEY=your_cleartrip_key

# Database
POSTGRES_DSN=postgresql://user:strong_password@postgres:5432/travelagent
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your_secret_key
```

### 2. Production Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    build: ./backend
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=strong_password
    restart: unless-stopped
```

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Detailed system health
curl http://localhost:8000/health/detailed

# Database health
docker-compose exec postgres pg_isready
```

### Performance Monitoring
```bash
# Resource usage
docker stats

# Service logs
docker-compose logs -f api
```

## Next Steps

1. **Start Docker Desktop** (if not already running)
2. **Run**: `docker-compose up -d`
3. **Test**: `curl http://localhost:8000/health`
4. **Develop**: Make changes, see live reload
5. **Deploy**: Use production compose for deployment

## Benefits of Docker Setup

✅ **Consistent Environment**: Same setup across dev/staging/prod
✅ **Easy Scaling**: Add more API instances
✅ **Data Persistence**: Redis + PostgreSQL volumes
✅ **Service Isolation**: Each service in its own container
✅ **Easy Debugging**: View logs, exec into containers
✅ **Production Ready**: Same setup for deployment
