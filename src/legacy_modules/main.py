"""
FinBuddy - AI-Powered Financial Companion
Main FastAPI Application (LEGACY - Use Microservices Instead)
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sys
import os

# Add parent path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import settings
from database import init_db, get_db, User, Investment, RiskAlert, FraudAlert, LearningProgress
from gemini_service import gemini_companion
from risk_engine import risk_engine
from fraud_detection import fraud_detector

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered financial companion for micro-investors"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for requests/responses
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    risk_tolerance: str = "medium"

class InvestmentCreate(BaseModel):
    symbol: str
    asset_type: str
    quantity: float
    purchase_price: float

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class TermExplanationRequest(BaseModel):
    term: str

class ScamCheckRequest(BaseModel):
    message: str
    sender: Optional[str] = ""

class URLCheckRequest(BaseModel):
    url: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🚀 Starting FinBuddy application...")
    await init_db()
    logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} is running!")
    logger.info(f"📊 Gemini API configured: {bool(settings.GEMINI_API_KEY)}")

# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "description": "Your AI-powered financial companion",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }

# User Management Endpoints
@app.post("/api/users/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    logger.info(f"👤 Registering new user: {user_data.username}")
    
    try:
        # In production, hash the password properly
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=f"hashed_{user_data.password}",  # Simplified for demo
            risk_tolerance=user_data.risk_tolerance
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"✅ User registered successfully: {new_user.id}")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "message": "User registered successfully! 🎉"
        }
    except Exception as e:
        logger.error(f"❌ Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user profile"""
    logger.info(f"👤 Fetching user profile: {user_id}")
    
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"⚠️ User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ User found: {user.username}")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "risk_tolerance": user.risk_tolerance,
            "created_at": user.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Investment Management Endpoints
@app.post("/api/investments/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_investment(
    user_id: int,
    investment: InvestmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new investment to user's portfolio"""
    logger.info(f"💼 Adding investment for user {user_id}: {investment.symbol}")
    
    try:
        new_investment = Investment(
            user_id=user_id,
            symbol=investment.symbol,
            asset_type=investment.asset_type,
            quantity=investment.quantity,
            purchase_price=investment.purchase_price,
            current_price=investment.purchase_price  # Initially same as purchase price
        )
        
        db.add(new_investment)
        await db.commit()
        await db.refresh(new_investment)
        
        # Perform risk analysis
        risk_analysis = risk_engine.predict_risk_score({
            "symbol": investment.symbol,
            "asset_type": investment.asset_type,
            "purchase_price": investment.purchase_price,
            "current_price": investment.purchase_price,
            "quantity": investment.quantity
        })
        
        # Use Gemini for additional insights
        gemini_analysis = await gemini_companion.analyze_investment_risk({
            "symbol": investment.symbol,
            "asset_type": investment.asset_type,
            "purchase_price": investment.purchase_price,
            "current_price": investment.purchase_price,
            "quantity": investment.quantity
        })
        
        logger.info(f"✅ Investment added successfully: {new_investment.id}")
        
        return {
            "id": new_investment.id,
            "message": "Investment added successfully! 📈",
            "risk_analysis": risk_analysis,
            "ai_insights": gemini_analysis
        }
    except Exception as e:
        logger.error(f"❌ Error adding investment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio endpoint
@app.get("/api/portfolio/{user_id}")
async def get_user_portfolio(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get portfolio for a user"""
    logger.info(f"💼 Fetching portfolio for user {user_id}")
    
    try:
        result = await db.execute(
            select(Investment).where(Investment.user_id == user_id)
        )
        investments = result.scalars().all()
    
        logger.info(f"✅ Found {len(investments)} investments")
        
        return {
            "user_id": user_id,
            "total_investments": len(investments),
            "investments": [
                {
                    "id": inv.id,
                    "symbol": inv.symbol,
                    "asset_type": inv.asset_type,
                    "quantity": inv.quantity,
                    "purchase_price": inv.purchase_price,
                    "current_price": inv.current_price,
                    "gain_loss": (inv.current_price - inv.purchase_price) * inv.quantity if inv.current_price else 0
                }
                for inv in investments
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error fetching portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Risk analysis endpoint
@app.get("/api/risk/analyze-portfolio/{user_id}")
async def analyze_portfolio_risk(user_id: int, db: AsyncSession = Depends(get_db)):
    """Analyze overall portfolio risk for a user"""
    logger.info(f"📊 Analyzing portfolio risk for user {user_id}")
    
    try:
        # Get all investments
        result = await db.execute(
            select(Investment).where(Investment.user_id == user_id)
        )
        investments = result.scalars().all()
        
        if not investments:
            return {
                "user_id": user_id,
                "overall_risk": "low",
                "risk_score": 0.0,
                "message": "No investments found",
                "recommendations": ["Start investing to build your portfolio"]
            }
        
        # Calculate average risk
        total_risk = 0
        risk_details = []
        
        for inv in investments:
            risk_analysis = risk_engine.predict_risk_score({
                "symbol": inv.symbol,
                "asset_type": inv.asset_type,
                "purchase_price": inv.purchase_price,
                "current_price": inv.current_price or inv.purchase_price,
                "quantity": inv.quantity
            })
            total_risk += risk_analysis['risk_score']
            risk_details.append({
                "symbol": inv.symbol,
                "risk_level": risk_analysis['risk_level']
            })
        
        avg_risk = total_risk / len(investments)
        
        if avg_risk >= settings.HIGH_RISK_THRESHOLD:
            overall_risk = "high"
        elif avg_risk >= settings.MEDIUM_RISK_THRESHOLD:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        logger.info(f"✅ Portfolio risk: {overall_risk} ({avg_risk:.2f})")
        
        return {
            "user_id": user_id,
            "overall_risk": overall_risk,
            "risk_score": round(avg_risk, 3),
            "total_investments": len(investments),
            "risk_distribution": risk_details,
            "recommendations": [
                "Diversify your portfolio to reduce risk",
                "Monitor high-risk investments regularly",
                "Consider adding stable assets"
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error analyzing portfolio risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/investment/{investment_id}")
async def analyze_investment_risk(investment_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed risk analysis for a single investment"""
    result = await db.execute(
        select(Investment).where(Investment.id == investment_id)
    )
    investment = result.scalar_one_or_none()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    # Risk engine analysis
    risk_analysis = risk_engine.predict_risk_score({
        "symbol": investment.symbol,
        "asset_type": investment.asset_type,
        "purchase_price": investment.purchase_price,
        "current_price": investment.current_price or investment.purchase_price,
        "quantity": investment.quantity
    })
    
    # Gemini AI analysis
    ai_analysis = await gemini_companion.analyze_investment_risk({
        "symbol": investment.symbol,
        "asset_type": investment.asset_type,
        "purchase_price": investment.purchase_price,
        "current_price": investment.current_price or investment.purchase_price,
        "quantity": investment.quantity
    })
    
    # Save risk alert if high risk
    if risk_analysis['risk_score'] >= settings.HIGH_RISK_THRESHOLD:
        alert = RiskAlert(
            user_id=investment.user_id,
            investment_id=investment.id,
            risk_score=risk_analysis['risk_score'],
            risk_level=risk_analysis['risk_level'],
            alert_message=f"High risk detected for {investment.symbol}",
            human_readable_message=ai_analysis.get('summary', 'High risk investment')
        )
        db.add(alert)
        await db.commit()
    
    return {
        "investment": {
            "symbol": investment.symbol,
            "asset_type": investment.asset_type
        },
        "risk_analysis": risk_analysis,
        "ai_insights": ai_analysis
    }

# AI Companion Endpoints
@app.post("/api/ai/chat")
async def chat_with_ai(request: ChatRequest):
    """Chat with FinBuddy AI companion"""
    logger.info(f"💬 Chat request: {request.message[:50]}...")
    
    try:
        response = await gemini_companion.chat_with_user(
            request.message,
            context={"user_id": request.user_id} if request.user_id else None
        )
        
        logger.info(f"✅ Chat response generated")
        
        return {
            "user_message": request.message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/api/ai/explain-term")
async def explain_financial_term(request: TermExplanationRequest):
    """Explain financial jargon in simple terms"""
    logger.info(f"📚 Explaining term: {request.term}")
    
    try:
        explanation = await gemini_companion.explain_financial_term(request.term)
        
        logger.info(f"✅ Term explained successfully")
        
        return {
            "term": request.term,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error explaining term: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")

@app.post("/api/ai/translate")
async def translate_technical_text(text: str):
    """Translate technical financial text to simple language"""
    simple_text = await gemini_companion.translate_to_simple_language(text)
    
    return {
        "original": text[:100] + "..." if len(text) > 100 else text,
        "simplified": simple_text
    }

# Fraud Detection Endpoints
@app.post("/api/fraud/detect-scam")
async def check_for_scam(request: ScamCheckRequest, db: AsyncSession = Depends(get_db)):
    """Check message for scam indicators"""
    logger.info(f"🔍 Checking for scam: {request.message[:50]}...")
    # Use Gemini AI for deep analysis
    ai_analysis = await gemini_companion.detect_scam_language(request.message)
    
    # Use rule-based fraud detector
    rule_based_analysis = fraud_detector.analyze_message(request.message, request.sender)
    
    # Combine analyses
    combined_risk = max(
        ai_analysis.get('confidence', 0),
        rule_based_analysis.get('risk_score', 0)
    )
    
    is_suspicious = combined_risk >= 0.4
    
    logger.info(f"{'⚠️ SUSPICIOUS' if is_suspicious else '✅ Safe'} - Risk: {combined_risk}")
    
    return {
        "is_suspicious": is_suspicious,
        "confidence": round(combined_risk, 3),
        "risk_score": round(combined_risk, 3),
        "red_flags": ai_analysis.get('red_flags', []),
        "explanation": ai_analysis.get('explanation', ''),
        "ai_analysis": ai_analysis,
        "pattern_analysis": rule_based_analysis,
        "recommendation": rule_based_analysis.get('recommendation', '')
    }

@app.post("/api/fraud/check-url")
async def check_url_safety(request: URLCheckRequest):
    """Check if a URL is safe or potentially malicious"""
    logger.info(f"🔗 Checking URL: {request.url}")
    
    try:
        analysis = fraud_detector.analyze_url(request.url)
        
        logger.info(f"{'✅ Safe' if analysis['is_safe'] else '⚠️ Risky'} URL")
    
        return {
            "url": request.url,
            "is_safe": analysis['is_safe'],
            "risk_score": analysis['risk_score'],
            "risk_factors": analysis['risk_factors'],
            "recommendation": analysis['recommendation']
        }
    except Exception as e:
        logger.error(f"❌ Error checking URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/security/alerts/{user_id}")
async def get_fraud_alerts(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get fraud alerts for a user"""
    result = await db.execute(
        select(FraudAlert).where(FraudAlert.user_id == user_id).order_by(FraudAlert.created_at.desc())
    )
    alerts = result.scalars().all()
    
    return {
        "user_id": user_id,
        "total_alerts": len(alerts),
        "alerts": [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "description": alert.description,
                "severity": alert.severity,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at.isoformat()
            }
            for alert in alerts
        ]
    }

# Learning & Education Endpoints
@app.get("/api/learning/module/{topic}")
async def get_learning_module(topic: str, difficulty: str = "beginner"):
    """Get educational content on a financial topic"""
    content = await gemini_companion.generate_learning_content(topic, difficulty)
    
    return {
        "topic": topic,
        "difficulty": difficulty,
        "content": content,
        "estimated_time": "15-20 minutes"
    }

@app.get("/api/learning/progress/{user_id}")
async def get_learning_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's learning progress"""
    result = await db.execute(
        select(LearningProgress).where(LearningProgress.user_id == user_id)
    )
    progress = result.scalars().all()
    
    return {
        "user_id": user_id,
        "modules_completed": len([p for p in progress if p.completion_percentage >= 100]),
        "modules_in_progress": len([p for p in progress if 0 < p.completion_percentage < 100]),
        "progress": [
            {
                "module": p.module_name,
                "completion": p.completion_percentage,
                "quiz_score": p.quiz_score,
                "last_accessed": p.last_accessed.isoformat()
            }
            for p in progress
        ]
    }

# Dashboard Summary Endpoint
@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get comprehensive dashboard for a user"""
    # Get investments
    inv_result = await db.execute(
        select(Investment).where(Investment.user_id == user_id)
    )
    investments = inv_result.scalars().all()
    
    # Get risk alerts
    alert_result = await db.execute(
        select(RiskAlert).where(RiskAlert.user_id == user_id, RiskAlert.is_read == False)
    )
    risk_alerts = alert_result.scalars().all()
    
    # Get fraud alerts
    fraud_result = await db.execute(
        select(FraudAlert).where(FraudAlert.user_id == user_id, FraudAlert.is_resolved == False)
    )
    fraud_alerts = fraud_result.scalars().all()
    
    # Calculate portfolio value
    total_value = sum(
        (inv.current_price or inv.purchase_price) * inv.quantity 
        for inv in investments
    )
    
    total_invested = sum(
        inv.purchase_price * inv.quantity 
        for inv in investments
    )
    
    gain_loss = total_value - total_invested
    gain_loss_pct = (gain_loss / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "user_id": user_id,
        "portfolio_summary": {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "gain_loss": round(gain_loss, 2),
            "gain_loss_percentage": round(gain_loss_pct, 2),
            "total_investments": len(investments)
        },
        "alerts": {
            "risk_alerts": len(risk_alerts),
            "fraud_alerts": len(fraud_alerts)
        },
        "status": "🟢 Portfolio Healthy" if gain_loss >= 0 else "🟡 Monitor Closely"
    }


# ===================== NEWS ENDPOINTS =====================

@app.post("/api/news/fetch")
async def fetch_news(
    sources: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_db)
):
    """Trigger immediate news fetch from selected or all sources
    
    Args:
        sources: List of source keys to fetch from. Valid: 
                'economic_times', 'zerodha', 'newsapi', 'alpha_vantage', 
                'finnhub', 'marketaux', 'gnews'
                If None, fetches from all sources.
    """
    try:
        logger.info(f"📰 Manual news fetch triggered for sources: {sources or 'all'}")
        from news_fetcher import get_news_fetcher
        from database import NewsArticle
        
        fetcher = get_news_fetcher()
        articles = await fetcher.fetch_all(sources=sources)
        
        saved_count = 0
        duplicate_count = 0
        
        for article_data in articles:
            # Check if article already exists
            result = await db.execute(
                select(NewsArticle).where(NewsArticle.url == article_data['url'])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                duplicate_count += 1
                continue
            
            # Create new article
            article = NewsArticle(**article_data)
            db.add(article)
            saved_count += 1
        
        await db.commit()
        
        logger.info(f"✅ Saved {saved_count} new articles, {duplicate_count} duplicates skipped")
        
        return {
            "message": "News fetch completed",
            "sources": sources or "all",
            "articles_fetched": len(articles),
            "new_articles_saved": saved_count,
            "duplicates_skipped": duplicate_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/latest")
async def get_latest_news(
    limit: int = 50,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get latest news articles"""
    try:
        from database import NewsArticle
        
        query = select(NewsArticle).order_by(NewsArticle.published_at.desc())
        
        # Filter by source if provided
        if source:
            query = query.where(NewsArticle.source == source)
        
        # Filter by sentiment if provided
        if sentiment:
            query = query.where(NewsArticle.sentiment == sentiment)
        
        query = query.limit(limit)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        return {
            "total": len(articles),
            "articles": [
                {
                    "id": art.id,
                    "title": art.title,
                    "summary": art.summary,
                    "url": art.url,
                    "source": art.source,
                    "published_at": art.published_at.isoformat() if art.published_at else None,
                    "sentiment": art.sentiment,
                    "sentiment_score": art.sentiment_score,
                    "fetched_at": art.fetched_at.isoformat() if art.fetched_at else None
                }
                for art in articles
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/sources")
async def get_news_sources(db: AsyncSession = Depends(get_db)):
    """Get list of news sources with article counts"""
    try:
        from database import NewsArticle
        from sqlalchemy import func
        
        result = await db.execute(
            select(
                NewsArticle.source,
                func.count(NewsArticle.id).label('count'),
                func.max(NewsArticle.fetched_at).label('last_fetch')
            ).group_by(NewsArticle.source)
        )
        
        sources = result.all()
        
        return {
            "sources": [
                {
                    "name": src.source,
                    "article_count": src.count,
                    "last_fetch": src.last_fetch.isoformat() if src.last_fetch else None
                }
                for src in sources
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
