"""
AI Service - Gemini-powered financial companion
Port: 8004
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from legacy_modules.gemini_service import gemini_companion

logger = setup_logger('ai_service')

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class TermExplanationRequest(BaseModel):
    term: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AI Service starting on port 8004...")
    yield

app = FastAPI(title="AI Service", version="2.0.0", description="Gemini AI Financial Companion", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "AI Service", "version": "2.0.0", "status": "operational", "port": 8004}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai_service"}

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"💬 Chat request: {request.message[:50]}...")
    try:
        response = await gemini_companion.chat_with_user(request.message, context={"user_id": request.user_id} if request.user_id else None)
        return {"user_message": request.message, "response": response, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-term")
async def explain_term(request: TermExplanationRequest):
    logger.info(f"📚 Explaining term: {request.term}")
    try:
        explanation = await gemini_companion.explain_financial_term(request.term)
        return {"term": request.term, "explanation": explanation, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate(text: str):
    try:
        simple_text = await gemini_companion.translate_to_simple_language(text)
        return {"original": text[:100], "simplified": simple_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/{topic}")
async def get_learning_module(topic: str, difficulty: str = "beginner"):
    try:
        content = await gemini_companion.generate_learning_content(topic, difficulty)
        return {"topic": topic, "difficulty": difficulty, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)
