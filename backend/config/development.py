"""
Development Environment Configuration
"""

from config import Settings

class DevelopmentSettings(Settings):
    """Development-specific settings"""
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Database
    redis_url: str = "redis://localhost:6379/0"
    postgres_dsn: str = "postgresql://user:password@localhost:5432/travel_dev"
    
    # API Configuration
    amadeus_environment: str = "test"
    amadeus_base_url: str = "https://test.api.amadeus.com"
    
    # Performance (relaxed for development)
    http_timeout: int = 60
    max_api_retries: int = 5
    api_timeout: int = 30
    
    # Caching (shorter for development)
    flight_cache_duration: int = 60  # 1 minute
    nlp_cache_ttl: int = 300  # 5 minutes
    nlp_entity_cache_ttl: int = 180  # 3 minutes
    
    # Session Management
    session_expiry: int = 3600  # 1 hour for development
    
    # Monitoring
    metrics_enabled: bool = True
    performance_monitoring: bool = True
    
    # Logging
    log_file: str = "logs/development.log"
    log_rotation: bool = True
    log_max_size: int = 5242880  # 5MB
    log_backup_count: int = 3

# Development settings instance
dev_settings = DevelopmentSettings()
