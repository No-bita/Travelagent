"""
Production Environment Configuration
"""

from config import Settings

class ProductionSettings(Settings):
    """Production-specific settings"""
    
    # Environment
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"
    
    # Database (production URLs)
    redis_url: str = "redis://redis-cluster:6379/0"
    postgres_dsn: str = "postgresql://prod_user:secure_password@prod-db:5432/travel_prod"
    
    # API Configuration
    amadeus_environment: str = "production"
    amadeus_base_url: str = "https://api.amadeus.com"
    
    # Performance (optimized for production)
    http_timeout: int = 15
    max_api_retries: int = 3
    api_timeout: int = 5
    
    # Connection Pooling (optimized)
    http_max_connections: int = 200
    http_max_connections_per_host: int = 50
    redis_max_connections: int = 200
    
    # Caching (longer for production)
    flight_cache_duration: int = 1800  # 30 minutes
    nlp_cache_ttl: int = 7200  # 2 hours
    nlp_entity_cache_ttl: int = 3600  # 1 hour
    
    # Session Management
    session_expiry: int = 86400  # 24 hours
    
    # Security
    secret_key: str = "production-secret-key-change-me"
    jwt_secret: str = "production-jwt-secret-change-me"
    
    # Rate Limiting (strict for production)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    
    # Monitoring
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    health_check_interval: int = 10  # 10 seconds
    
    # Logging
    log_file: str = "/var/log/travel-agent/app.log"
    log_rotation: bool = True
    log_max_size: int = 104857600  # 100MB
    log_backup_count: int = 10
    
    # CORS (restrictive for production)
    cors_origins: list = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST"]
    cors_allow_headers: list = ["Content-Type", "Authorization"]

# Production settings instance
prod_settings = ProductionSettings()
