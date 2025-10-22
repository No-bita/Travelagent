"""
Configuration Factory
Loads appropriate settings based on environment
"""

import os
from typing import Type
from . import Settings
from .development import DevelopmentSettings
from .production import ProductionSettings
from .testing import TestingSettings

def get_settings() -> Settings:
    """
    Get settings based on environment variable
    Defaults to development if not specified
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

def get_settings_class() -> Type[Settings]:
    """
    Get settings class based on environment variable
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings
    elif environment == "testing":
        return TestingSettings
    else:
        return DevelopmentSettings

# Global settings instance
settings = get_settings()

def reload_settings():
    """Reload settings (useful for testing)"""
    global settings
    settings = get_settings()
    return settings
