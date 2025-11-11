"""
Risk Service - Risk analysis and fraud detection
Port: 8005
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from shared.utils.database import init_db, get_session
from shared.models import Investment, RiskAlert, FraudAlert
from legacy_modules.risk_engine import risk_engine
from legacy_modules.fraud_detection import fraud_detector
from legacy_modules.gemini_service import gemini_companion

logger = setup_logger('risk_service')

class ScamCheckRequest(BaseModel):
    message: str
    sender: str = ""

class URLCheckRequest(BaseModel):
    url: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Risk Service starting on port 8005...")
    await init_db()
    yield

app = FastAPI(title="Risk Service", version="2.0.0", description="Risk Analysis & Fraud Detection", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "Risk Service", "version": "2.0.0", "status": "operational", "port": 8005}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "risk_service"}

@app.get("/analyze-portfolio/{user_id}")
async def analyze_portfolio(user_id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"📊 Analyzing portfolio risk for user {user_id}")
    try:
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        if not investments:
            return {"user_id": user_id, "overall_risk": "low", "risk_score": 0.0, "message": "No investments"}
        total_risk = 0
        risk_details = []
        for inv in investments:
            risk_analysis = risk_engine.predict_risk_score({
                "symbol": inv.symbol, "asset_type": inv.asset_type,
                "purchase_price": inv.purchase_price, "current_price": inv.current_price or inv.purchase_price,
                "quantity": inv.quantity
            })
            total_risk += risk_analysis['risk_score']
            risk_details.append({"symbol": inv.symbol, "risk_level": risk_analysis['risk_level']})
        avg_risk = total_risk / len(investments)
        overall_risk = "high" if avg_risk >= 0.7 else "medium" if avg_risk >= 0.4 else "low"
        return {"user_id": user_id, "overall_risk": overall_risk, "risk_score": round(avg_risk, 3), 
                "total_investments": len(investments), "risk_distribution": risk_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-scam")
async def detect_scam(request: ScamCheckRequest):
    logger.info(f"🔍 Checking for scam: {request.message[:50]}...")
    try:
        ai_analysis = await gemini_companion.detect_scam_language(request.message)
        rule_analysis = fraud_detector.analyze_message(request.message, request.sender)
        combined_risk = max(ai_analysis.get('confidence', 0), rule_analysis.get('risk_score', 0))
        return {
            "is_suspicious": combined_risk >= 0.4,
            "confidence": round(combined_risk, 3),
            "red_flags": ai_analysis.get('red_flags', []),
            "explanation": ai_analysis.get('explanation', ''),
            "recommendation": rule_analysis.get('recommendation', '')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-url")
async def check_url(request: URLCheckRequest):
    logger.info(f"🔗 Checking URL: {request.url}")
    try:
        analysis = fraud_detector.analyze_url(request.url)
        return {
            "url": request.url, "is_safe": analysis['is_safe'], 
            "risk_score": analysis['risk_score'], "risk_factors": analysis['risk_factors'],
            "recommendation": analysis['recommendation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, reload=True)
