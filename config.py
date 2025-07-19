import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT Configuration
    # Railway 환경변수에서 읽도록 수정
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # 개발 환경에서만 기본값 사용
    if not JWT_SECRET_KEY and os.getenv('FLASK_ENV') != 'production':
        JWT_SECRET_KEY = 'dev-jwt-secret-key-for-local-only'
    elif not JWT_SECRET_KEY:
        # 프로덕션에서는 반드시 환경변수가 필요
        print("WARNING: JWT_SECRET_KEY not set in production!")
    
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    JWT_COOKIE_CSRF_PROTECT = False  # API 사용을 위해 CSRF 보호 비활성화
    JWT_CSRF_CHECK_FORM = False
    JWT_CSRF_IN_COOKIES = False
    JWT_TOKEN_LOCATION = ['headers']  # 헤더에서만 토큰 확인
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///nongbuxx.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    BCRYPT_LOG_ROUNDS = 13
    
    # API Key Encryption (for storing user's API keys)
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key-32-chars-long')
    
    # Email Configuration (for password reset - optional)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@nongbuxx.com')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 