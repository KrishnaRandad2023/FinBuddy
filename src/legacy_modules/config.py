"""
Configuration settings for FinBuddy
"""
import os
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("✅ Environment variables loaded")

class Settings:
    # App Settings
    APP_NAME = "FinBuddy"
    APP_VERSION = "1.0.0"
    DEBUG = True
    
    # Gemini AI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-2.5-flash"  # Updated to latest model
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finbuddy.db")
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Redis Settings
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    
    # Risk Thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4
    
    # Notification Settings
    ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"

settings = Settings()

# Debug info
logger.info(f"🔧 Configuration loaded:")
logger.info(f"  - APP_NAME: {settings.APP_NAME}")
logger.info(f"  - APP_VERSION: {settings.APP_VERSION}")
logger.info(f"  - GEMINI_API_KEY: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Not Set'}")
logger.info(f"  - DATABASE_URL: {settings.DATABASE_URL}")
logger.info(f"  - DEBUG: {settings.DEBUG}")
