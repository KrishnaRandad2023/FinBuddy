"""
Complete Services Implementation Script
This script will update all 6 microservices with their full business logic
"""
import os

# Define complete implementations for all services

PORTFOLIO_SERVICE = '''"""
Portfolio Service - Investment Tracking & Live Prices
Port: 8002
"""
from fastapi import FastAPI, Depends, HTTPException, status
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
from shared.models import Investment
from price_service import get_live_price

logger = setup_logger('portfolio_service')

class InvestmentCreate(BaseModel):
    symbol: str
    asset_type: str
    quantity: float
    purchase_price: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Portfolio Service starting on port 8002...")
    await init_db()
    yield

app = FastAPI(title="Portfolio Service", version="2.0.0", description="Investment Tracking & Live Prices", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "Portfolio Service", "version": "2.0.0", "status": "operational", "port": 8002}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "portfolio_service"}

@app.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_investment(user_id: int, investment: InvestmentCreate, db: AsyncSession = Depends(get_session)):
    logger.info(f"💼 Adding investment for user {user_id}: {investment.symbol}")
    try:
        new_investment = Investment(
            user_id=user_id,
            symbol=investment.symbol,
            asset_type=investment.asset_type,
            quantity=investment.quantity,
            purchase_price=investment.purchase_price,
            current_price=investment.purchase_price
        )
        db.add(new_investment)
        await db.commit()
        await db.refresh(new_investment)
        logger.info(f"✅ Investment added: {new_investment.id}")
        return {"id": new_investment.id, "message": "Investment added successfully! 📈"}
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{user_id}")
async def get_portfolio(user_id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"💼 Fetching portfolio for user {user_id}")
    try:
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        return {
            "user_id": user_id,
            "total_investments": len(investments),
            "investments": [
                {
                    "id": i.id,
                    "symbol": i.symbol,
                    "asset_type": i.asset_type,
                    "quantity": i.quantity,
                    "purchase_price": i.purchase_price,
                    "current_price": i.current_price,
                    "gain_loss": (i.current_price - i.purchase_price) * i.quantity if i.current_price else 0
                } for i in investments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/price/{symbol}")
async def get_price(symbol: str, asset_type: str = "stock"):
    logger.info(f"💵 Fetching price for {symbol} ({asset_type})")
    try:
        price_data = get_live_price(symbol, asset_type)
        if not price_data:
            raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update-prices/{user_id}")
async def update_prices(user_id: int, db: AsyncSession = Depends(get_session)):
    logger.info(f"🔄 Updating prices for user {user_id}")
    try:
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        updated_count = 0
        for inv in investments:
            price_data = get_live_price(inv.symbol, inv.asset_type)
            if price_data:
                inv.current_price = price_data['price']
                updated_count += 1
        await db.commit()
        return {"user_id": user_id, "updated_count": updated_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
'''

NEWS_SERVICE = '''"""
News Service - Multi-source financial news with sentiment analysis
Port: 8003
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from shared.utils.database import init_db, get_session
from shared.models import NewsArticle
from news_fetcher import get_news_fetcher

logger = setup_logger('news_service')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 News Service starting on port 8003...")
    await init_db()
    yield

app = FastAPI(title="News Service", version="2.0.0", description="Financial news aggregation", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"service": "News Service", "version": "2.0.0", "status": "operational", "port": 8003}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "news_service"}

@app.post("/fetch")
async def fetch_news(sources: Optional[List[str]] = None, db: AsyncSession = Depends(get_session)):
    logger.info(f"📰 Fetching news from: {sources or 'all'}")
    try:
        fetcher = get_news_fetcher()
        articles = await fetcher.fetch_all(sources=sources)
        saved_count = 0
        duplicate_count = 0
        for article_data in articles:
            result = await db.execute(select(NewsArticle).where(NewsArticle.url == article_data['url']))
            if result.scalar_one_or_none():
                duplicate_count += 1
                continue
            db.add(NewsArticle(**article_data))
            saved_count += 1
        await db.commit()
        return {"message": "News fetch completed", "articles_fetched": len(articles), "new_saved": saved_count, "duplicates": duplicate_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest")
async def get_latest_news(limit: int = 50, source: Optional[str] = None, sentiment: Optional[str] = None, db: AsyncSession = Depends(get_session)):
    try:
        query = select(NewsArticle).order_by(NewsArticle.published_at.desc())
        if source:
            query = query.where(NewsArticle.source == source)
        if sentiment:
            query = query.where(NewsArticle.sentiment == sentiment)
        query = query.limit(limit)
        result = await db.execute(query)
        articles = result.scalars().all()
        return {
            "total": len(articles),
            "articles": [
                {
                    "id": a.id, "title": a.title, "summary": a.summary, "url": a.url,
                    "source": a.source, "published_at": a.published_at.isoformat() if a.published_at else None,
                    "sentiment": a.sentiment, "sentiment_score": a.sentiment_score
                } for a in articles
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def get_sources(db: AsyncSession = Depends(get_session)):
    try:
        result = await db.execute(
            select(NewsArticle.source, func.count(NewsArticle.id).label('count'), 
                   func.max(NewsArticle.fetched_at).label('last_fetch'))
            .group_by(NewsArticle.source)
        )
        sources = result.all()
        return {
            "sources": [
                {"name": s.source, "article_count": s.count, "last_fetch": s.last_fetch.isoformat() if s.last_fetch else None}
                for s in sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
'''

AI_SERVICE = '''"""
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
from gemini_service import gemini_companion

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
'''

RISK_SERVICE = '''"""
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
from risk_engine import risk_engine
from fraud_detection import fraud_detector
from gemini_service import gemini_companion

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
'''

LEARNING_SERVICE = '''"""
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
from gemini_service import gemini_companion

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
'''

def main():
    """Update all service files"""
    base_dir = 'd:/super_projects/project_1/services'
    
    services = {
        'portfolio_service': PORTFOLIO_SERVICE,
        'news_service': NEWS_SERVICE,
        'ai_service': AI_SERVICE,
        'risk_service': RISK_SERVICE,
        'learning_service': LEARNING_SERVICE
    }
    
    print("🚀 Updating all microservices with complete implementations...")
    print("=" * 60)
    
    for service_name, code in services.items():
        file_path = f'{base_dir}/{service_name}/app.py'
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ {service_name.replace('_', ' ').title()} updated")
        except Exception as e:
            print(f"❌ Error updating {service_name}: {e}")
    
    print("=" * 60)
    print("✅ All services updated with complete business logic!")
    print("\\n📋 Services include:")
    print("  - Portfolio Service: Live pricing (yfinance + CoinGecko)")
    print("  - News Service: 7 sources with sentiment analysis")
    print("  - AI Service: Gemini chat, term explanation, learning content")
    print("  - Risk Service: Portfolio risk analysis, fraud detection")
    print("  - Learning Service: Financial education modules")
    print("\\n🎯 User Service already updated manually.")
    print("\\n🚀 Start all services with: .\\scripts\\start_all_services.ps1")

if __name__ == "__main__":
    main()
