"""
Shared database utilities
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging
import sys
import os

# Add parent path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    """Database connection manager"""
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database initialized")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.async_session_maker() as session:
            yield session


# Global database manager instance
_db_manager = DatabaseManager(settings.DATABASE_URL)

# Export convenience functions for services
async def init_db():
    """Initialize database tables (convenience function)"""
    await _db_manager.init_db()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (convenience function)"""
    async for session in _db_manager.get_session():
        yield session
