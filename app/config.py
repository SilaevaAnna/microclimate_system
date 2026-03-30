# config.py
import os
from typing import List


class Config:
    """Application configuration"""
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'climate_system.db'
    
    # Application
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # CORS
    CORS_ORIGINS: List[str] = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Sensor thresholds (configurable)
    TEMP_MIN = float(os.environ.get('TEMP_MIN', 18.0))
    TEMP_MAX = float(os.environ.get('TEMP_MAX', 26.0))
    HUMIDITY_MIN = float(os.environ.get('HUMIDITY_MIN', 30.0))
    HUMIDITY_MAX = float(os.environ.get('HUMIDITY_MAX', 60.0))
    CO2_CRITICAL = int(os.environ.get('CO2_CRITICAL', 1000))
    CO2_DANGER = int(os.environ.get('CO2_DANGER', 1500))


class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']


class ProductionConfig(Config):
    DEBUG = False
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else []


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
