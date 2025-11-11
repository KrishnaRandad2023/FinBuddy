"""
Shared configuration for all FinBuddy microservices
Loads environment variables from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root (go up from src/shared to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / "config" / ".env"

# Load environment variables from config/.env file
load_dotenv(dotenv_path=ENV_FILE)

class Settings:
    """
    Application settings for FinBuddy microservices
    All values are loaded from environment variables with sensible defaults
    """
    
    # ========================================================================
    # APPLICATION INFO
    # ========================================================================
    APP_NAME = os.getenv("APP_NAME", "FinBuddy")
    APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/finbuddy.db")
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./data/test_finbuddy.db")
    
    # ========================================================================
    # SECURITY & AUTHENTICATION
    # ========================================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Risk Thresholds
    HIGH_RISK_THRESHOLD = float(os.getenv("HIGH_RISK_THRESHOLD", "0.7"))
    MEDIUM_RISK_THRESHOLD = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.4"))
    
    # ========================================================================
    # MICROSERVICES PORTS
    # ========================================================================
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))
    USER_SERVICE_PORT = int(os.getenv("USER_SERVICE_PORT", "8001"))
    PORTFOLIO_SERVICE_PORT = int(os.getenv("PORTFOLIO_SERVICE_PORT", "8002"))
    NEWS_SERVICE_PORT = int(os.getenv("NEWS_SERVICE_PORT", "8003"))
    AI_SERVICE_PORT = int(os.getenv("AI_SERVICE_PORT", "8004"))
    RISK_SERVICE_PORT = int(os.getenv("RISK_SERVICE_PORT", "8005"))
    LEARNING_SERVICE_PORT = int(os.getenv("LEARNING_SERVICE_PORT", "8006"))
    
    # ========================================================================
    # MICROSERVICES URLS (for inter-service communication)
    # ========================================================================
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", f"http://localhost:{USER_SERVICE_PORT}")
    PORTFOLIO_SERVICE_URL = os.getenv("PORTFOLIO_SERVICE_URL", f"http://localhost:{PORTFOLIO_SERVICE_PORT}")
    NEWS_SERVICE_URL = os.getenv("NEWS_SERVICE_URL", f"http://localhost:{NEWS_SERVICE_PORT}")
    AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", f"http://localhost:{AI_SERVICE_PORT}")
    RISK_SERVICE_URL = os.getenv("RISK_SERVICE_URL", f"http://localhost:{RISK_SERVICE_PORT}")
    LEARNING_SERVICE_URL = os.getenv("LEARNING_SERVICE_URL", f"http://localhost:{LEARNING_SERVICE_PORT}")
    
    # ========================================================================
    # AI SERVICE - GOOGLE GEMINI
    # ========================================================================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # ========================================================================
    # NEWS SOURCES API KEYS
    # ========================================================================
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")
    GNEWS_KEY = os.getenv("GNEWS_KEY", "")
    
    # ========================================================================
    # PRICE SERVICE
    # ========================================================================
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # Optional for higher limits
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # ========================================================================
    # CACHE (Redis - Optional)
    # ========================================================================
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    
    # ========================================================================
    # CORS SETTINGS
    # ========================================================================
    CORS_ORIGINS = ["*"]  # In production, specify exact origins
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # ========================================================================
    # MONITORING & NOTIFICATIONS
    # ========================================================================
    ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "false").lower() == "true"
    
    # ========================================================================
    # FRONTEND
    # ========================================================================
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    
    # ========================================================================
    # DEPLOYMENT (Production)
    # ========================================================================
    DEPLOY_ENV = os.getenv("DEPLOY_ENV", "development")
    API_DOMAIN = os.getenv("API_DOMAIN", "localhost")
    ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    
    # ========================================================================
    # DEBUG & DEVELOPMENT
    # ========================================================================
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """Get URL for a specific service"""
        service_urls = {
            "user": cls.USER_SERVICE_URL,
            "portfolio": cls.PORTFOLIO_SERVICE_URL,
            "news": cls.NEWS_SERVICE_URL,
            "ai": cls.AI_SERVICE_URL,
            "risk": cls.RISK_SERVICE_URL,
            "learning": cls.LEARNING_SERVICE_URL,
        }
        return service_urls.get(service_name, "")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def get_all_service_urls(cls) -> dict:
        """Get all service URLs as dictionary"""
        return {
            "user": cls.USER_SERVICE_URL,
            "portfolio": cls.PORTFOLIO_SERVICE_URL,
            "news": cls.NEWS_SERVICE_URL,
            "ai": cls.AI_SERVICE_URL,
            "risk": cls.RISK_SERVICE_URL,
            "learning": cls.LEARNING_SERVICE_URL,
        }

# Global settings instance
settings = Settings()

# Validate critical settings
if not settings.GEMINI_API_KEY:
    import warnings
    warnings.warn("⚠️  GEMINI_API_KEY not set! AI features will not work.")

if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
    import warnings
    warnings.warn("⚠️  Using default SECRET_KEY! Please change in production.")
