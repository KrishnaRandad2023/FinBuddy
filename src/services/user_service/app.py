"""
User Service - Authentication & User Management
Port: 8001
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from shared.utils.database import init_db, get_session
from shared.utils.auth import hash_password, verify_password, create_access_token
from shared.models import User

logger = setup_logger('user_service')

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    risk_tolerance: str = "medium"

class UserLogin(BaseModel):
    username: str
    password: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("🚀 User Service starting on port 8001...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    logger.info("🛑 User Service shutting down...")

app = FastAPI(
    title="User Service",
    version="2.0.0",
    description="Authentication & User Management",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "User Service",
        "version": "2.0.0",
        "status": "operational",
        "port": 8001
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user_service"}

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_session)):
    """Register a new user"""
    logger.info(f"📝 Registration attempt for username: {user_data.username}")
    
    try:
        # Check if username exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            risk_tolerance=user_data.risk_tolerance
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"✅ User registered successfully: {new_user.username} (ID: {new_user.id})")
        
        return {
            "message": "User registered successfully!",
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_session)):
    """Login user and return JWT token"""
    logger.info(f"🔐 Login attempt for username: {credentials.username}")
    
    try:
        # Find user
        result = await db.execute(select(User).where(User.username == credentials.username))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"❌ Login failed: User not found - {credentials.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"❌ Login failed: Wrong password - {credentials.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"✅ Login successful: {user.username} (ID: {user.id})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "risk_tolerance": user.risk_tolerance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{user_id}")
async def get_profile(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get user profile"""
    logger.info(f"👤 Fetching profile for user ID: {user_id}")
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "risk_tolerance": user.risk_tolerance,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
