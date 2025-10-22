# Travel Agent Production Deployment Guide

## 🚀 Complete Production Setup with Docker

This guide covers deploying the Travel Agent system in production with Docker Compose, including Redis, PostgreSQL, and monitoring.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 10GB+ disk space
- Linux/macOS/Windows with WSL2

## 🛠️ Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd travel-agent
```

### 2. Configure Environment
```bash
# Copy environment template
cp env.prod.example .env

# Edit with your actual values
nano .env
```

**Required Environment Variables:**
```bash
# API Keys (REQUIRED)
AMADEUS_API_KEY=your_production_amadeus_key
AMADEUS_API_SECRET=your_production_amadeus_secret

# Security (REQUIRED)
SECRET_KEY=your-super-secret-key-here

# Database (Auto-configured)
POSTGRES_DSN=postgresql://travel_user:travel_password@postgres:5432/travelagent
REDIS_URL=redis://redis:6379/0
```

### 3. Deploy
```bash
# Run deployment script
./scripts/deploy.sh
```

### 4. Monitor
```bash
# Check system health
./scripts/monitor.sh
```

## 🏗️ Architecture

### Services Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   FastAPI       │    │   Redis        │
│   (Port 80)     │────│   (Port 8000)    │────│   (Port 6379)  │
│   Load Balancer │    │   Chat API      │    │   Sessions     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   (Port 5432)   │
                       │   Persistence   │
                       └─────────────────┘
```

### Service Details

#### 1. **API Service** (FastAPI)
- **Port**: 8000
- **Features**: Chat API, Flight Search, Health Monitoring
- **Scaling**: Horizontal scaling supported
- **Health Check**: `/health` endpoint

#### 2. **Redis** (Session Store)
- **Port**: 6379
- **Purpose**: Session management, caching
- **Persistence**: AOF enabled
- **Memory**: Configurable limits

#### 3. **PostgreSQL** (Database)
- **Port**: 5432
- **Database**: `travelagent`
- **User**: `travel_user`
- **Features**: Full-text search, JSON support

#### 4. **Nginx** (Reverse Proxy)
- **Port**: 80/443
- **Features**: Load balancing, SSL termination, rate limiting
- **Security**: Security headers, request limiting

## 🔧 Configuration

### Environment Variables

#### Required
```bash
# Amadeus API (Production)
AMADEUS_API_KEY=your_production_key
AMADEUS_API_SECRET=your_production_secret

# Security
SECRET_KEY=your-secret-key-here
```

#### Optional
```bash
# Additional APIs
CLEARTRIP_API_KEY=your_cleartrip_key
SKYSCANNER_API_KEY=your_skyscanner_key

# Payment Integration
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Notifications
WHATSAPP_API_KEY=your_whatsapp_key
SENDGRID_API_KEY=your_sendgrid_key
```

### Docker Compose Configuration

#### Production Features
- **Health Checks**: All services have health monitoring
- **Restart Policies**: Automatic restart on failure
- **Volume Persistence**: Data survives container restarts
- **Network Isolation**: Services communicate via internal network
- **Resource Limits**: Configurable CPU/memory limits

#### Scaling
```bash
# Scale API service to 3 instances
docker-compose -f docker-compose.prod.yml up --scale api=3 -d
```

## 📊 Monitoring & Maintenance

### Health Monitoring
```bash
# Check all services
./scripts/monitor.sh

# Individual service checks
curl http://localhost:8000/health
curl http://localhost:8000/health/detailed
```

### Logs
```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# Service-specific logs
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f redis
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Database Management
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U travel_user -d travelagent

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U travel_user travelagent > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U travel_user -d travelagent < backup.sql
```

### Redis Management
```bash
# Connect to Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli

# Monitor Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli monitor

# Clear cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli flushall
```

## 🔒 Security

### Production Security Checklist
- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs

### SSL Configuration
```bash
# Add SSL certificates to nginx/ssl/
# Update nginx.conf to enable HTTPS
# Redirect HTTP to HTTPS
```

## 🚀 Deployment Commands

### Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update Services
```bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build
```

### Scale Services
```bash
# Scale API to 3 instances
docker-compose -f docker-compose.prod.yml up --scale api=3 -d
```

## 📈 Performance Optimization

### Resource Limits
```yaml
# Add to docker-compose.prod.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Caching Strategy
- **Redis**: Session storage, API response caching
- **Database**: Connection pooling, query optimization
- **Nginx**: Static file caching, gzip compression

### Monitoring
- **Health Checks**: Automated service monitoring
- **Logs**: Centralized logging with rotation
- **Metrics**: Resource usage, response times
- **Alerts**: Automated alerting on failures

## 🛠️ Troubleshooting

### Common Issues

#### 1. Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check resource usage
docker stats
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U travel_user
```

#### 3. Redis Connection Issues
```bash
# Check Redis logs
docker-compose -f docker-compose.prod.yml logs redis

# Test connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

#### 4. API Not Responding
```bash
# Check API logs
docker-compose -f docker-compose.prod.yml logs api

# Test health endpoint
curl http://localhost:8000/health
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor logs for errors
docker-compose -f docker-compose.prod.yml logs -f | grep ERROR

# Check database performance
docker-compose -f docker-compose.prod.yml exec postgres psql -U travel_user -d travelagent -c "SELECT * FROM pg_stat_activity;"
```

## 📞 Support

### Getting Help
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Run monitor: `./scripts/monitor.sh`
3. Check health: `curl http://localhost:8000/health/detailed`

### Useful Commands
```bash
# View service status
docker-compose -f docker-compose.prod.yml ps

# View resource usage
docker stats

# Access service shell
docker-compose -f docker-compose.prod.yml exec api bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U travel_user -d travelagent
docker-compose -f docker-compose.prod.yml exec redis redis-cli
```

## 🎯 Next Steps

After successful deployment:
1. **Configure Monitoring**: Set up alerts and dashboards
2. **SSL Setup**: Configure HTTPS with certificates
3. **Backup Strategy**: Implement automated backups
4. **Scaling**: Configure load balancing and auto-scaling
5. **Security**: Implement additional security measures

---

**🎉 Your Travel Agent is now running in production!**

**Access Points:**
- API: http://localhost:8000
- Health: http://localhost:8000/health
- Chat: http://localhost:8000/chat
