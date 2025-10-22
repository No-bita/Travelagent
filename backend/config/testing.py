"""
Testing Environment Configuration
"""

from config import Settings

class TestingSettings(Settings):
    """Testing-specific settings"""
    
    # Environment
    environment: str = "testing"
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Database (test databases)
    redis_url: str = "redis://localhost:6379/1"  # Different DB for tests
    postgres_dsn: str = "postgresql://test_user:test_password@localhost:5432/travel_test"
    
    # API Configuration
    amadeus_environment: str = "test"
    amadeus_base_url: str = "https://test.api.amadeus.com"
    
    # Performance (fast for testing)
    http_timeout: int = 5
    max_api_retries: int = 1
    api_timeout: int = 2
    
    # Caching (minimal for testing)
    flight_cache_duration: int = 0  # No caching
    nlp_cache_ttl: int = 0  # No caching
    nlp_entity_cache_ttl: int = 0  # No caching
    
    # Session Management
    session_expiry: int = 300  # 5 minutes for testing
    
    # Disable features for testing
    enable_connection_pooling: bool = False
    enable_parallel_processing: bool = False
    enable_caching: bool = False
    enable_metrics: bool = False
    
    # Monitoring
    metrics_enabled: bool = False
    performance_monitoring: bool = False
    
    # Logging (minimal for testing)
    log_file: str = None
    log_rotation: bool = False
    
    # Security (relaxed for testing)
    secret_key: str = "test-secret-key"
    jwt_secret: str = "test-jwt-secret"
    
    # Rate Limiting (disabled for testing)
    rate_limit_enabled: bool = False
    
    # CORS (permissive for testing)
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

# Testing settings instance
test_settings = TestingSettings()
