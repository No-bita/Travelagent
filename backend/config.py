from pydantic_settings import BaseSettings
from typing import Dict, List, Optional


class Settings(BaseSettings):
    # Environment Configuration
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    redis_url: str = "redis://localhost:6379/0"
    postgres_dsn: str = "postgresql://user:password@localhost:5432/travel"
    
    # Redis Configuration
    redis_max_connections: int = 100
    redis_connection_timeout: int = 30
    redis_retry_on_timeout: bool = True
    redis_encoding: str = "utf-8"
    redis_decode_responses: bool = True
    
    # Flight API Sources (Multi-source redundancy)
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    amadeus_base_url: str = "https://test.api.amadeus.com"
    amadeus_token_url: str = "https://test.api.amadeus.com/v1/security/oauth2/token"
    amadeus_flight_url: str = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    amadeus_environment: str = "test"  # test or production
    
    skyscanner_api_key: str = ""
    cleartrip_api_key: str = ""
    cleartrip_api_base: str = ""
    cleartrip_api_header: str = "X-API-Key"
    make_my_trip_api_key: str = ""
    
    # HTTP Client Configuration
    http_timeout: int = 30  # seconds
    http_max_connections: int = 100
    http_max_connections_per_host: int = 30
    http_keepalive_timeout: int = 60
    http_retry_attempts: int = 3
    http_retry_delay: float = 1.0  # seconds
    
    # API Configuration
    flight_cache_duration: int = 300  # 5 minutes
    max_api_retries: int = 3
    api_timeout: int = 10  # seconds
    
    # Cost Optimization
    max_flight_results: int = 7   # Max results from Amadeus API for ranking
    display_flight_results: int = 3  # Top 3 most relevant shown to users
    
    # NLP Engine Configuration
    nlp_cache_size: int = 1000
    nlp_cache_ttl: int = 3600  # 1 hour
    nlp_entity_cache_size: int = 2000
    nlp_entity_cache_ttl: int = 1800  # 30 minutes
    nlp_language_cache_size: int = 500
    nlp_language_cache_ttl: int = 3600  # 1 hour
    nlp_thread_pool_workers: int = 4
    
    # State Manager Configuration
    session_expiry: int = 86400  # 24 hours
    session_cleanup_interval: int = 3600  # 1 hour
    max_sessions: int = 10000
    
    # Performance Configuration
    enable_connection_pooling: bool = True
    enable_parallel_processing: bool = True
    enable_caching: bool = True
    enable_metrics: bool = True
    
    # Monitoring Configuration
    metrics_enabled: bool = True
    health_check_interval: int = 30  # seconds
    performance_monitoring: bool = True
    
    # Payment Configuration
    payment_provider: str = "razorpay"
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    
    # Logging Configuration
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    log_rotation: bool = True
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    # Security Configuration
    secret_key: str = "your-secret-key-here"
    jwt_secret: str = "your-jwt-secret-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    
    # Rate Limiting Configuration
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Enhanced City Mappings (Centralized) - Supports offbeat locations
    city_mappings: Dict[str, List[str]] = {
        # Major Indian Cities
        'mumbai': ['mumbai', 'bombay', 'bom', 'mumbai city'],
        'delhi': ['delhi', 'new delhi', 'del', 'ncr', 'national capital region'],
        'bangalore': ['bangalore', 'bengaluru', 'blr', 'silicon valley of india'],
        'chennai': ['chennai', 'madras', 'maa', 'tamil nadu capital'],
        'hyderabad': ['hyderabad', 'hyd', 'hbd', 'cyberabad', 'pearl city'],
        'kolkata': ['kolkata', 'calcutta', 'ccu', 'city of joy'],
        'ahmedabad': ['ahmedabad', 'amd', 'gujarat capital'],
        'pune': ['pune', 'pnq', 'oxford of east'],
        'kochi': ['kochi', 'cochin', 'cok', 'queen of arabian sea'],
        'goa': ['goa', 'goi', 'panaji', 'beach capital'],
        'jaipur': ['jaipur', 'jai', 'pink city', 'rajasthan capital'],
        'lucknow': ['lucknow', 'lko', 'city of nawabs'],
        'guwahati': ['guwahati', 'gau', 'guwati', 'gateway to northeast'],
        'chandigarh': ['chandigarh', 'ixc', 'city beautiful'],
        
        # Tier-2 Indian Cities
        'indore': ['indore', 'idr', 'indore city', 'commercial capital'],
        'bhopal': ['bhopal', 'bho', 'city of lakes', 'madhya pradesh capital'],
        'coimbatore': ['coimbatore', 'cjb', 'covai', 'manchester of south'],
        'mysore': ['mysore', 'myq', 'mysuru', 'city of palaces'],
        'visakhapatnam': ['visakhapatnam', 'vtz', 'vizag', 'vishakapatnam'],
        'nagpur': ['nagpur', 'nag', 'orange city', 'winter capital'],
        'vadodara': ['vadodara', 'bdq', 'baroda', 'cultural capital'],
        'rajkot': ['rajkot', 'raj', 'rajkot city'],
        'amritsar': ['amritsar', 'atq', 'golden city', 'spiritual capital'],
        'tirupati': ['tirupati', 'tir', 'tirumala', 'temple city'],
        'bhubaneswar': ['bhubaneswar', 'bbi', 'temple city', 'odisha capital'],
        
        # Tourist Destinations
        'shimla': ['shimla', 'sim', 'queen of hills', 'hill station'],
        'manali': ['manali', 'kullu manali', 'adventure capital'],
        'udaipur': ['udaipur', 'uda', 'city of lakes', 'venice of east'],
        'jodhpur': ['jodhpur', 'jdh', 'blue city', 'sun city'],
        'agra': ['agra', 'agr', 'taj city', 'city of taj'],
        'varanasi': ['varanasi', 'vns', 'banaras', 'kashi', 'spiritual capital'],
        'kashmir': ['kashmir', 'srinagar', 'sri', 'paradise on earth'],
        'darjeeling': ['darjeeling', 'darj', 'queen of hills', 'tea capital'],
        'ooty': ['ooty', 'udagamandalam', 'queen of hills', 'hill station'],
        'alleppey': ['alleppey', 'alpy', 'alappuzha', 'venice of east'],
        'munnar': ['munnar', 'tea gardens', 'hill station'],
        'kodaikanal': ['kodaikanal', 'koda', 'princess of hills'],
        'mahabalipuram': ['mahabalipuram', 'mamallapuram', 'stone city'],
        'hampi': ['hampi', 'vijayanagara', 'ruins city'],
        'kerala': ['kerala', 'god\'s own country', 'backwaters'],
        
        # Business Hubs & NCR
        'gurgaon': ['gurgaon', 'gurugram', 'gur', 'millennium city'],
        'noida': ['noida', 'noida city', 'tech hub'],
        'faridabad': ['faridabad', 'faridabad city', 'industrial city'],
        'ghaziabad': ['ghaziabad', 'ghaziabad city'],
        
        # International Cities (Major)
        'dubai': ['dubai', 'dxb', 'uae', 'emirates'],
        'singapore': ['singapore', 'sin', 'sg', 'lion city'],
        'bangkok': ['bangkok', 'bkk', 'thailand', 'land of smiles'],
        'london': ['london', 'lhr', 'uk', 'united kingdom'],
        'new york': ['new york', 'nyc', 'jfk', 'usa', 'america'],
        'paris': ['paris', 'cdg', 'france', 'city of light'],
        'tokyo': ['tokyo', 'nrt', 'japan', 'land of rising sun'],
        'sydney': ['sydney', 'syd', 'australia', 'harbour city'],
        'toronto': ['toronto', 'yyz', 'canada', 'maple leaf'],
        'frankfurt': ['frankfurt', 'fra', 'germany', 'financial hub'],
        'amsterdam': ['amsterdam', 'ams', 'netherlands', 'venice of north'],
        'zurich': ['zurich', 'zrh', 'switzerland', 'banking capital'],
        'moscow': ['moscow', 'svo', 'russia', 'red square'],
        'istanbul': ['istanbul', 'ist', 'turkey', 'bridge between continents'],
        'cairo': ['cairo', 'cai', 'egypt', 'land of pharaohs'],
        'johannesburg': ['johannesburg', 'jhb', 'south africa', 'city of gold'],
        'nairobi': ['nairobi', 'nbo', 'kenya', 'green city'],
        'riyadh': ['riyadh', 'ruh', 'saudi arabia', 'desert capital'],
        'doha': ['doha', 'doh', 'qatar', 'pearl of gulf'],
        'kuwait': ['kuwait', 'kwi', 'kuwait city'],
        'manama': ['manama', 'bahrain', 'bhr'],
        'muscat': ['muscat', 'mct', 'oman', 'pearl of arabia'],
        'tehran': ['tehran', 'thr', 'iran', 'persian capital'],
        'karachi': ['karachi', 'khi', 'pakistan', 'city of lights'],
        'dhaka': ['dhaka', 'dac', 'bangladesh', 'city of mosques'],
        'kathmandu': ['kathmandu', 'ktm', 'nepal', 'himalayan capital'],
        'colombo': ['colombo', 'cmb', 'sri lanka', 'pearl of indian ocean'],
        'male': ['male', 'mle', 'maldives', 'paradise islands'],
        'yangon': ['yangon', 'rgn', 'myanmar', 'golden land'],
        'phnom penh': ['phnom penh', 'pnh', 'cambodia', 'pearl of asia'],
        'vientiane': ['vientiane', 'vte', 'laos', 'land of million elephants'],
        'hanoi': ['hanoi', 'han', 'vietnam', 'city of lakes'],
        'ho chi minh': ['ho chi minh', 'sgn', 'saigon', 'vietnam'],
        'jakarta': ['jakarta', 'cgk', 'indonesia', 'big durian'],
        'kuala lumpur': ['kuala lumpur', 'kul', 'malaysia', 'garden city'],
        'manila': ['manila', 'mnl', 'philippines', 'pearl of orient'],
        'seoul': ['seoul', 'icn', 'south korea', 'soul of asia'],
        'hong kong': ['hong kong', 'hkg', 'hk', 'pearl of orient'],
        'taipei': ['taipei', 'tpe', 'taiwan', 'formosa']
    }
    
    # Enhanced Airport Code Mappings (Centralized) - Supports offbeat locations
    airport_codes: Dict[str, str] = {
        # Major Indian Cities
        'mumbai': 'BOM', 'delhi': 'DEL', 'bangalore': 'BLR', 'chennai': 'MAA',
        'hyderabad': 'HYD', 'kolkata': 'CCU', 'ahmedabad': 'AMD', 'pune': 'PNQ',
        'kochi': 'COK', 'goa': 'GOI', 'jaipur': 'JAI', 'lucknow': 'LKO',
        'guwahati': 'GAU', 'chandigarh': 'IXC',
        
        # Tier-2 Indian Cities
        'indore': 'IDR', 'bhopal': 'BHO', 'coimbatore': 'CJB', 'mysore': 'MYQ',
        'visakhapatnam': 'VTZ', 'nagpur': 'NAG', 'vadodara': 'BDQ', 'rajkot': 'RAJ',
        'amritsar': 'ATQ', 'tirupati': 'TIR', 'bhubaneswar': 'BBI',
        
        # Tourist Destinations
        'shimla': 'SLV', 'manali': 'KUU', 'udaipur': 'UDR', 'jodhpur': 'JDH',
        'agra': 'AGR', 'varanasi': 'VNS', 'kashmir': 'SXR', 'darjeeling': 'IXB',
        'ooty': 'COK', 'alleppey': 'COK', 'munnar': 'COK', 'kodaikanal': 'COK',
        'mahabalipuram': 'MAA', 'hampi': 'BLR', 'kerala': 'COK',
        
        # Business Hubs
        'gurgaon': 'DEL', 'noida': 'DEL', 'faridabad': 'DEL', 'ghaziabad': 'DEL',
        
        # International Cities
        'dubai': 'DXB', 'singapore': 'SIN', 'bangkok': 'BKK', 'london': 'LHR',
        'new york': 'JFK', 'paris': 'CDG', 'tokyo': 'NRT', 'sydney': 'SYD',
        'toronto': 'YYZ', 'frankfurt': 'FRA', 'amsterdam': 'AMS', 'zurich': 'ZRH',
        'moscow': 'SVO', 'istanbul': 'IST', 'cairo': 'CAI', 'johannesburg': 'JNB',
        'nairobi': 'NBO', 'riyadh': 'RUH', 'doha': 'DOH', 'kuwait': 'KWI',
        'manama': 'BAH', 'muscat': 'MCT', 'tehran': 'THR', 'karachi': 'KHI',
        'dhaka': 'DAC', 'kathmandu': 'KTM', 'colombo': 'CMB', 'male': 'MLE',
        'yangon': 'RGN', 'phnom penh': 'PNH', 'vientiane': 'VTE', 'hanoi': 'HAN',
        'ho chi minh': 'SGN', 'jakarta': 'CGK', 'kuala lumpur': 'KUL', 'manila': 'MNL',
        'seoul': 'ICN', 'hong kong': 'HKG', 'taipei': 'TPE',
        
        # Legacy mappings for backward compatibility
        'bengaluru': 'BLR', 'hyd': 'HYD', 'blr': 'BLR', 'bom': 'BOM', 'del': 'DEL', 'maa': 'MAA'
    }
    
    # Intent Patterns (Centralized)
    intent_patterns: Dict[str, Dict[str, List[str]]] = {
        'en': {
            'search_flights': [
                r'\b(?:search|find|book|get)\s+(?:flights?|tickets?)\b',
                r'\b(?:fly|travel|go)\s+(?:to|from)\b',
                r'\b(?:flight|ticket|booking)\b'
            ],
            'book_flight': [
                r'\b(?:book|reserve|buy|purchase)\s+(?:flight|ticket)\b',
                r'\b(?:confirm|finalize)\s+(?:booking|reservation)\b'
            ]
        }
    }
    
    # Entity Patterns (Centralized)
    entity_patterns: Dict[str, Dict[str, List[str]]] = {
        'en': {
            'cities': [
                r'\b(?:from|to)\s+([a-zA-Z\s]+?)(?:\s+(?:to|on|for)|$)',
                r'\b([a-zA-Z\s]+?)\s+(?:to|on|for)\s+',
                r'\b(mumbai|delhi|bangalore|chennai|hyderabad|kolkata|ahmedabad|pune|kochi|goa|jaipur|lucknow|guwahati|chandigarh|indore|bhopal|coimbatore|mysore|visakhapatnam|nagpur|vadodara|rajkot|amritsar|tirupati|bhubaneswar|shimla|manali|udaipur|jodhpur|agra|varanasi|kashmir|darjeeling|ooty|alleppey|munnar|kodaikanal|mahabalipuram|hampi|kerala|gurgaon|noida|faridabad|ghaziabad|dubai|singapore|bangkok|london|new york|paris|tokyo|sydney|toronto|frankfurt|amsterdam|zurich|moscow|istanbul|cairo|johannesburg|nairobi|riyadh|doha|kuwait|manama|muscat|tehran|karachi|dhaka|kathmandu|colombo|male|yangon|phnom penh|vientiane|hanoi|ho chi minh|jakarta|kuala lumpur|manila|seoul|hong kong|taipei|bengaluru|hyd|blr|bom|del|maa)\b'
            ],
            'dates': [
                r'\b(?:on|for|at)\s+([a-zA-Z0-9\s,]+?)(?:\s+(?:for|with)|$)',
                r'\b(today|tomorrow|yesterday|day\s+after\s+tomorrow|next\s+week|this\s+weekend)\b',
                r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december))\b',
                r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b'
            ],
            'preferences': [
                r'\b(?:cheap|cheapest|lowest|budget|affordable|economy)\b',
                r'\b(?:fast|quick|earliest|morning|afternoon|evening)\b',
                r'\b(?:business|first|premium|luxury)\b'
            ]
        }
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance directly
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'))

environment = os.getenv("ENVIRONMENT", "development").lower()

if environment == "production":
    from production import ProductionSettings
    settings = ProductionSettings()
elif environment == "testing":
    from testing import TestingSettings
    settings = TestingSettings()
else:
    from development import DevelopmentSettings
    settings = DevelopmentSettings()


