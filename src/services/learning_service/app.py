"""
Learning Service - Financial education modules
Port: 8006
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from shared.utils.database import init_db, get_session
from shared.models import LearningProgress
from legacy_modules.gemini_service import gemini_companion

logger = setup_logger('learning_service')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Learning Service starting on port 8006...")
    await init_db()
    yield

app = FastAPI(title="Learning Service", version="2.0.0", description="Financial Education", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "Learning Service", "version": "2.0.0", "status": "operational", "port": 8006}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "learning_service"}

@app.get("/module/{topic}")
async def get_module(topic: str, difficulty: str = "beginner"):
    try:
        content = await gemini_companion.generate_learning_content(topic, difficulty)
        return {"topic": topic, "difficulty": difficulty, "content": content, "estimated_time": "15-20 minutes"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{user_id}")
async def get_progress(user_id: int, db: AsyncSession = Depends(get_session)):
    try:
        result = await db.execute(select(LearningProgress).where(LearningProgress.user_id == user_id))
        progress = result.scalars().all()
        return {
            "user_id": user_id,
            "modules_completed": len([p for p in progress if p.completion_percentage >= 100]),
            "modules_in_progress": len([p for p in progress if 0 < p.completion_percentage < 100]),
            "progress": [
                {"module": p.module_name, "completion": p.completion_percentage, "quiz_score": p.quiz_score,
                 "last_accessed": p.last_accessed.isoformat()} for p in progress
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=True)
