"""
FinBuddy - Simple All-in-One Server
Clean, straightforward FastAPI application for prototype
Port: 8000
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os
import logging

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import settings
from shared.utils.logger import setup_logger
from shared.utils.database import init_db, get_session
from shared.utils.auth import hash_password, verify_password, create_access_token
from shared.models import User, Investment, RiskAlert, FraudAlert, LearningProgress, NewsArticle, RecommendationOutcome
from legacy_modules.price_service import get_live_price
from legacy_modules.news_fetcher import get_news_fetcher
from legacy_modules.gemini_service import gemini_companion
from legacy_modules.risk_engine import risk_engine
from legacy_modules.fraud_detection import fraud_detector

logger = setup_logger('finbuddy_server')
logging.basicConfig(level=logging.INFO)

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    risk_tolerance: str = "medium"

class UserLogin(BaseModel):
    username: str
    password: str

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
    sender: str = ""

class URLCheckRequest(BaseModel):
    url: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("🚀 Starting FinBuddy Server...")
    try:
        await init_db()
        logger.info("✅ Database ready")
        logger.info("✅ Gemini AI ready")
        logger.info("✅ All systems operational")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    yield
    logger.info("🛑 Server shutdown")

app = FastAPI(
    title="FinBuddy Server",
    version="1.0.0",
    description="Simple AI-Powered Financial Companion API",
    lifespan=lifespan
)

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HEALTH CHECK - Simple and reliable
# ============================================================================

@app.get("/health")
async def health_check():
    """Simple health check for frontend"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ============================================================================
# USER SERVICE - Authentication & User Management
# ============================================================================

@app.post("/api/users/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_session)):
    """Register a new user"""
    logger.info(f"📝 Registration: {user_data.username}")
    
    try:
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            risk_tolerance=user_data.risk_tolerance
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"✅ User registered: {new_user.username}")
        
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

@app.post("/api/users/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_session)):
    """Login user"""
    logger.info(f"🔐 Login: {credentials.username}")
    
    try:
        result = await db.execute(select(User).where(User.username == credentials.username))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"✅ Login successful: {user.username}")
        
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

@app.get("/api/users/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get user by ID (for simple demo login)"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ User fetched: {user.username}")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "risk_tolerance": user.risk_tolerance
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/profile/{user_id}")
async def get_profile(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get user profile"""
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
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PORTFOLIO SERVICE - Investment Tracking
# ============================================================================

@app.post("/api/investments/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_investment(user_id: int, investment: InvestmentCreate, db: AsyncSession = Depends(get_session)):
    """Add new investment"""
    logger.info(f"💼 Adding investment: {investment.symbol}")
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
        return {"id": new_investment.id, "message": "Investment added! 📈"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{user_id}")
async def get_portfolio(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get user portfolio"""
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

@app.get("/api/prices/{symbol}")
async def get_price(symbol: str, asset_type: str = "stock"):
    """Get live price"""
    try:
        price_data = get_live_price(symbol, asset_type)
        if not price_data:
            raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/portfolio/update-prices/{user_id}")
async def update_prices(user_id: int, db: AsyncSession = Depends(get_session)):
    """Update all prices"""
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
        return {"updated_count": updated_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PORTFOLIO SIMULATOR
# ============================================================================

class PortfolioItem(BaseModel):
    symbol: str
    quantity: float
    avg_buy_price: float
    sector: Optional[str] = None

class SimulationRequest(BaseModel):
    user_id: int
    current_portfolio: List[PortfolioItem]
    modified_portfolio: List[PortfolioItem]
    risk_appetite: str  # "low", "medium", "high"
    investment_goal: str  # long-term, short-term, retirement, etc.
    horizon_years: int

class PortfolioMetrics(BaseModel):
    total_value: float
    risk_score: float
    diversification_score: float
    sentiment_score: float
    opportunity_exposure: float
    threat_exposure: float
    sector_distribution: Dict[str, float]
    top_holding_pct: float

def calculate_portfolio_value(portfolio: List[PortfolioItem]) -> float:
    """Calculate total portfolio value using live prices"""
    total = 0.0
    for item in portfolio:
        price_data = get_live_price(item.symbol)
        if price_data and 'price' in price_data:
            current_price = price_data['price']
        else:
            current_price = item.avg_buy_price  # Fallback to avg buy price
        total += item.quantity * current_price
    return total

def calculate_risk_score(portfolio: List[PortfolioItem]) -> float:
    """
    Calculate portfolio risk score (0-100, higher = riskier)
    Based on concentration, volatility proxy, and sector exposure
    """
    if not portfolio:
        return 0.0
    
    # Get current values
    holdings_values = []
    total_value = 0.0
    
    for item in portfolio:
        price_data = get_live_price(item.symbol)
        if price_data and 'price' in price_data:
            current_price = price_data['price']
        else:
            current_price = item.avg_buy_price
        
        value = item.quantity * current_price
        holdings_values.append(value)
        total_value += value
    
    if total_value == 0:
        return 0.0
    
    # Concentration risk (max holding percentage)
    max_holding_pct = max(holdings_values) / total_value * 100 if holdings_values else 0
    concentration_score = min(100, max_holding_pct * 1.5)  # Scale up
    
    # Diversification penalty (fewer holdings = higher risk)
    num_holdings = len(portfolio)
    if num_holdings == 1:
        diversification_penalty = 40
    elif num_holdings == 2:
        diversification_penalty = 25
    elif num_holdings <= 5:
        diversification_penalty = 10
    else:
        diversification_penalty = 0
    
    # Sector concentration (if sector data available)
    sector_risk = 0
    if any(item.sector for item in portfolio):
        sector_counts = {}
        for item in portfolio:
            sector = item.sector or "Unknown"
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        max_sector_count = max(sector_counts.values())
        sector_concentration_pct = (max_sector_count / len(portfolio)) * 100
        sector_risk = min(30, sector_concentration_pct * 0.5)
    
    # Combined risk score
    risk_score = (concentration_score * 0.5) + (diversification_penalty * 0.3) + (sector_risk * 0.2)
    return min(100, max(0, risk_score))

def calculate_diversification_score(portfolio: List[PortfolioItem]) -> float:
    """
    Calculate diversification score (0-100, higher = better diversified)
    """
    if not portfolio or len(portfolio) == 0:
        return 0.0
    
    num_holdings = len(portfolio)
    
    # Base score from number of holdings
    if num_holdings >= 10:
        base_score = 100
    elif num_holdings >= 7:
        base_score = 85
    elif num_holdings >= 5:
        base_score = 70
    elif num_holdings >= 3:
        base_score = 50
    elif num_holdings == 2:
        base_score = 30
    else:
        base_score = 10
    
    # Calculate concentration penalty (Herfindahl index)
    holdings_values = []
    total_value = 0.0
    
    for item in portfolio:
        price_data = get_live_price(item.symbol)
        if price_data and 'price' in price_data:
            current_price = price_data['price']
        else:
            current_price = item.avg_buy_price
        
        value = item.quantity * current_price
        holdings_values.append(value)
        total_value += value
    
    if total_value == 0:
        return base_score
    
    # Herfindahl concentration index
    herfindahl = sum((v / total_value) ** 2 for v in holdings_values)
    concentration_penalty = herfindahl * 40  # 0-40 penalty
    
    # Sector diversity bonus
    sector_bonus = 0
    if any(item.sector for item in portfolio):
        unique_sectors = len(set(item.sector for item in portfolio if item.sector))
        if unique_sectors >= 5:
            sector_bonus = 15
        elif unique_sectors >= 3:
            sector_bonus = 10
        elif unique_sectors >= 2:
            sector_bonus = 5
    
    final_score = base_score - concentration_penalty + sector_bonus
    return min(100, max(0, final_score))

def calculate_news_sentiment_score(portfolio: List[PortfolioItem]) -> float:
    """
    Calculate news sentiment score (0-100, higher = more positive)
    Simple proxy based on recent news sentiment
    """
    # For now, return neutral score
    # In production, this would analyze recent news articles
    return 50.0

def calculate_opportunity_exposure(portfolio: List[PortfolioItem]) -> float:
    """
    Calculate exposure to growth opportunities (0-100)
    Based on sector classification and growth potential
    """
    if not portfolio:
        return 0.0
    
    growth_sectors = {"Technology", "Healthcare", "Renewable Energy", "E-commerce"}
    
    growth_weight = 0.0
    total_weight = 0.0
    
    for item in portfolio:
        weight = item.quantity  # Simple weight by quantity
        total_weight += weight
        
        if item.sector and item.sector in growth_sectors:
            growth_weight += weight
    
    if total_weight == 0:
        return 50.0  # Neutral
    
    opportunity_score = (growth_weight / total_weight) * 100
    return min(100, max(0, opportunity_score))

def calculate_threat_exposure(portfolio: List[PortfolioItem]) -> float:
    """
    Calculate exposure to threats/risks (0-100, higher = more threats)
    Based on sector risks and volatility
    """
    if not portfolio:
        return 0.0
    
    risky_sectors = {"Cryptocurrency", "Penny Stocks", "Emerging Markets", "High Volatility"}
    
    risk_weight = 0.0
    total_weight = 0.0
    
    for item in portfolio:
        weight = item.quantity
        total_weight += weight
        
        if item.sector and item.sector in risky_sectors:
            risk_weight += weight
    
    if total_weight == 0:
        return 20.0  # Low default threat
    
    threat_score = (risk_weight / total_weight) * 100
    return min(100, max(0, threat_score))

def calculate_portfolio_metrics(portfolio: List[PortfolioItem]) -> PortfolioMetrics:
    """Calculate all metrics for a portfolio"""
    
    # Calculate total value
    total_value = calculate_portfolio_value(portfolio)
    
    # Calculate sector distribution
    sector_distribution = {}
    sector_values = {}
    
    for item in portfolio:
        price_data = get_live_price(item.symbol)
        if price_data and 'price' in price_data:
            current_price = price_data['price']
        else:
            current_price = item.avg_buy_price
        
        value = item.quantity * current_price
        sector = item.sector or "Unknown"
        
        sector_values[sector] = sector_values.get(sector, 0.0) + value
    
    for sector, value in sector_values.items():
        sector_distribution[sector] = (value / total_value * 100) if total_value > 0 else 0
    
    # Calculate top holding percentage
    holdings_values = []
    for item in portfolio:
        price_data = get_live_price(item.symbol)
        if price_data and 'price' in price_data:
            current_price = price_data['price']
        else:
            current_price = item.avg_buy_price
        
        value = item.quantity * current_price
        holdings_values.append(value)
    
    top_holding_pct = (max(holdings_values) / total_value * 100) if total_value > 0 and holdings_values else 0
    
    return PortfolioMetrics(
        total_value=total_value,
        risk_score=calculate_risk_score(portfolio),
        diversification_score=calculate_diversification_score(portfolio),
        sentiment_score=calculate_news_sentiment_score(portfolio),
        opportunity_exposure=calculate_opportunity_exposure(portfolio),
        threat_exposure=calculate_threat_exposure(portfolio),
        sector_distribution=sector_distribution,
        top_holding_pct=top_holding_pct
    )

@app.post("/api/portfolio/simulate")
async def simulate_portfolio_changes(request: SimulationRequest, db: AsyncSession = Depends(get_session)):
    """
    Simulate portfolio changes and get AI recommendation
    """
    try:
        logger.info(f"🎮 Simulating portfolio changes for user {request.user_id}")
        
        # Calculate metrics for both portfolios
        current_metrics = calculate_portfolio_metrics(request.current_portfolio)
        modified_metrics = calculate_portfolio_metrics(request.modified_portfolio)
        
        # Calculate deltas
        changes = {
            "risk_delta": modified_metrics.risk_score - current_metrics.risk_score,
            "diversification_delta": modified_metrics.diversification_score - current_metrics.diversification_score,
            "sentiment_delta": modified_metrics.sentiment_score - current_metrics.sentiment_score,
            "opportunity_delta": modified_metrics.opportunity_exposure - current_metrics.opportunity_exposure,
            "threat_delta": modified_metrics.threat_exposure - current_metrics.threat_exposure,
            "value_delta": modified_metrics.total_value - current_metrics.total_value,
            "top_holding_delta": modified_metrics.top_holding_pct - current_metrics.top_holding_pct
        }
        
        # Build AI prompt for recommendation
        current_portfolio_summary = "\n".join([
            f"  - {item.symbol}: {item.quantity} shares @ ${item.avg_buy_price:.2f} (Sector: {item.sector or 'Unknown'})"
            for item in request.current_portfolio
        ])
        
        modified_portfolio_summary = "\n".join([
            f"  - {item.symbol}: {item.quantity} shares @ ${item.avg_buy_price:.2f} (Sector: {item.sector or 'Unknown'})"
            for item in request.modified_portfolio
        ])
        
        ai_prompt = f"""You are a financial advisor AI evaluating a proposed portfolio change.

USER PROFILE:
- Risk Appetite: {request.risk_appetite}
- Investment Goal: {request.investment_goal}
- Time Horizon: {request.horizon_years} years

CURRENT PORTFOLIO:
{current_portfolio_summary}
Total Value: ${current_metrics.total_value:,.2f}
Risk Score: {current_metrics.risk_score:.1f}/100
Diversification: {current_metrics.diversification_score:.1f}/100
Top Holding: {current_metrics.top_holding_pct:.1f}%
Sector Distribution: {current_metrics.sector_distribution}

PROPOSED MODIFIED PORTFOLIO:
{modified_portfolio_summary}
Total Value: ${modified_metrics.total_value:,.2f}
Risk Score: {modified_metrics.risk_score:.1f}/100
Diversification: {modified_metrics.diversification_score:.1f}/100
Top Holding: {modified_metrics.top_holding_pct:.1f}%
Sector Distribution: {modified_metrics.sector_distribution}

CHANGES (Deltas):
- Risk Change: {changes['risk_delta']:+.1f} points
- Diversification Change: {changes['diversification_delta']:+.1f} points
- Portfolio Value Change: ${changes['value_delta']:+,.2f}
- Top Holding Change: {changes['top_holding_delta']:+.1f}%

ANALYSIS REQUIRED:
Evaluate whether the user should proceed with this portfolio change.

Respond in this EXACT JSON format:
{{
  "should_proceed": true or false,
  "reasoning": "Detailed explanation of why to proceed or not (2-3 sentences)",
  "warnings": ["List of specific warnings or concerns", "Each as a separate string"],
  "confidence": 0.85 (number between 0 and 1)
}}

Consider:
1. Alignment with risk appetite ({request.risk_appetite})
2. Suitability for investment goal ({request.investment_goal})
3. Time horizon appropriateness ({request.horizon_years} years)
4. Diversification improvement/degradation
5. Risk-adjusted returns potential
6. Concentration risks

Respond ONLY with the JSON object, no other text.
"""
        
        # Call Gemini AI
        try:
            ai_response_text = await gemini_companion.chat_with_user(ai_prompt)
            
            # Extract JSON from response (handle markdown formatting)
            import re
            import json
            
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in AI response")
            
            ai_summary = json.loads(json_str)
            
            # Validate required keys
            required_keys = ['should_proceed', 'reasoning', 'warnings', 'confidence']
            if not all(key in ai_summary for key in required_keys):
                raise ValueError("AI response missing required keys")
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}, using fallback logic")
            
            # Fallback rule-based recommendation
            should_proceed = True
            warnings = []
            
            # Check risk alignment
            if request.risk_appetite == "low" and changes['risk_delta'] > 10:
                should_proceed = False
                warnings.append("Risk increase too high for low-risk investor")
            elif request.risk_appetite == "high" and changes['risk_delta'] < -20:
                warnings.append("Significant risk reduction may limit growth potential")
            
            # Check diversification
            if changes['diversification_delta'] < -15:
                should_proceed = False
                warnings.append("Diversification is significantly reduced")
            elif changes['diversification_delta'] > 20:
                warnings.append("Great improvement in diversification!")
            
            # Check concentration
            if modified_metrics.top_holding_pct > 50:
                should_proceed = False
                warnings.append("Top holding exceeds 50% - too concentrated")
            
            # Check time horizon vs risk
            if request.horizon_years < 3 and modified_metrics.risk_score > 70:
                warnings.append("High risk may not suit short time horizon")
            
            if not warnings:
                warnings = ["Change appears reasonable based on your profile"]
            
            confidence = 0.65 if should_proceed else 0.75
            
            ai_summary = {
                "should_proceed": should_proceed,
                "reasoning": f"Based on your {request.risk_appetite} risk appetite and {request.horizon_years}-year horizon, "
                            f"this change {'aligns well' if should_proceed else 'may not be optimal'} with your goals.",
                "warnings": warnings,
                "confidence": confidence
            }
        
        # Build response
        response = {
            "initial_portfolio": {
                "total_value": current_metrics.total_value,
                "risk_score": current_metrics.risk_score,
                "diversification_score": current_metrics.diversification_score,
                "sentiment_score": current_metrics.sentiment_score,
                "opportunity_exposure": current_metrics.opportunity_exposure,
                "threat_exposure": current_metrics.threat_exposure,
                "sector_distribution": current_metrics.sector_distribution,
                "top_holding_pct": current_metrics.top_holding_pct,
                "holdings_count": len(request.current_portfolio)
            },
            "modified_portfolio": {
                "total_value": modified_metrics.total_value,
                "risk_score": modified_metrics.risk_score,
                "diversification_score": modified_metrics.diversification_score,
                "sentiment_score": modified_metrics.sentiment_score,
                "opportunity_exposure": modified_metrics.opportunity_exposure,
                "threat_exposure": modified_metrics.threat_exposure,
                "sector_distribution": modified_metrics.sector_distribution,
                "top_holding_pct": modified_metrics.top_holding_pct,
                "holdings_count": len(request.modified_portfolio)
            },
            "changes": changes,
            "ai_summary": ai_summary
        }
        
        logger.info(f"✅ Simulation complete. Recommendation: {'Proceed' if ai_summary['should_proceed'] else 'Reconsider'}")
        
        return response
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

# ============================================================================
# RECOMMENDATION OUTCOME TRACKING
# ============================================================================

class RecommendationFollowRequest(BaseModel):
    user_id: int
    recommendation_type: str  # 'ai_recommendations' or 'portfolio_simulation'
    initial_portfolio_value: float
    recommendation_summary: str

class RecommendationOutcomeUpdate(BaseModel):
    outcome_id: int
    final_portfolio_value: float
    outcome: str  # 'positive', 'negative', 'neutral'

@app.post("/api/recommendations/track-follow")
async def track_recommendation_follow(request: RecommendationFollowRequest, db: AsyncSession = Depends(get_session)):
    """Track when a user follows an AI recommendation"""
    try:
        outcome_record = RecommendationOutcome(
            user_id=request.user_id,
            recommendation_type=request.recommendation_type,
            followed=True,
            outcome='pending',
            initial_portfolio_value=request.initial_portfolio_value,
            recommendation_summary=request.recommendation_summary,
            created_at=datetime.utcnow()
        )
        
        db.add(outcome_record)
        await db.commit()
        await db.refresh(outcome_record)
        
        logger.info(f"✅ Tracked recommendation follow for user {request.user_id}")
        
        return {
            "outcome_id": outcome_record.id,
            "message": "Recommendation tracking started"
        }
        
    except Exception as e:
        logger.error(f"Failed to track recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/update-outcome")
async def update_recommendation_outcome(request: RecommendationOutcomeUpdate, db: AsyncSession = Depends(get_session)):
    """Update the outcome of a followed recommendation"""
    try:
        result = await db.execute(
            select(RecommendationOutcome).where(RecommendationOutcome.id == request.outcome_id)
        )
        outcome_record = result.scalar_one_or_none()
        
        if not outcome_record:
            raise HTTPException(status_code=404, detail="Outcome record not found")
        
        outcome_record.final_portfolio_value = request.final_portfolio_value
        outcome_record.outcome = request.outcome
        outcome_record.evaluated_at = datetime.utcnow()
        
        # Calculate percentage change
        if outcome_record.initial_portfolio_value > 0:
            outcome_record.percentage_change = (
                (request.final_portfolio_value - outcome_record.initial_portfolio_value) / 
                outcome_record.initial_portfolio_value * 100
            )
        
        await db.commit()
        
        logger.info(f"✅ Updated outcome for record {request.outcome_id}: {request.outcome}")
        
        return {
            "message": "Outcome updated successfully",
            "percentage_change": outcome_record.percentage_change
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations/success-stats")
async def get_recommendation_success_stats(
    recommendation_type: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """Get success statistics for AI recommendations"""
    try:
        # Build query
        query = select(RecommendationOutcome).where(RecommendationOutcome.followed == True)
        
        if recommendation_type:
            query = query.where(RecommendationOutcome.recommendation_type == recommendation_type)
        
        result = await db.execute(query)
        all_outcomes = result.scalars().all()
        
        if not all_outcomes:
            return {
                "total_followed": 0,
                "success_rate": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "pending_count": 0,
                "average_gain": 0,
                "message": "No recommendation data available yet"
            }
        
        # Calculate statistics
        total = len(all_outcomes)
        positive = sum(1 for o in all_outcomes if o.outcome == 'positive')
        negative = sum(1 for o in all_outcomes if o.outcome == 'negative')
        neutral = sum(1 for o in all_outcomes if o.outcome == 'neutral')
        pending = sum(1 for o in all_outcomes if o.outcome == 'pending')
        
        evaluated = total - pending
        success_rate = (positive / evaluated * 100) if evaluated > 0 else 0
        
        # Calculate average gain for completed outcomes
        gains = [o.percentage_change for o in all_outcomes if o.percentage_change is not None]
        average_gain = sum(gains) / len(gains) if gains else 0
        
        stats = {
            "total_followed": total,
            "success_rate": round(success_rate, 1),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "pending_count": pending,
            "average_gain": round(average_gain, 2),
            "evaluation_complete": evaluated,
            "message": f"{success_rate:.1f}% of users who followed AI recommendations saw positive results"
        }
        
        logger.info(f"📊 Success stats: {success_rate:.1f}% positive from {total} recommendations")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# NEWS SERVICE
# ============================================================================

@app.post("/api/news/fetch")
async def fetch_news(sources: Optional[List[str]] = None, db: AsyncSession = Depends(get_session)):
    """Fetch news from sources"""
    logger.info(f"📰 Fetching news")
    try:
        fetcher = get_news_fetcher()
        articles = await fetcher.fetch_all(sources=sources)
        saved_count = 0
        for article_data in articles:
            result = await db.execute(select(NewsArticle).where(NewsArticle.url == article_data['url']))
            if result.scalar_one_or_none():
                continue
            db.add(NewsArticle(**article_data))
            saved_count += 1
        await db.commit()
        return {"articles_fetched": len(articles), "new_saved": saved_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/latest")
async def get_latest_news(limit: int = 50, source: Optional[str] = None, db: AsyncSession = Depends(get_session)):
    """Get latest news"""
    try:
        query = select(NewsArticle).order_by(NewsArticle.published_at.desc())
        if source:
            query = query.where(NewsArticle.source == source)
        query = query.limit(limit)
        result = await db.execute(query)
        articles = result.scalars().all()
        return {
            "total": len(articles),
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "summary": a.summary,
                    "url": a.url,
                    "source": a.source,
                    "published_at": a.published_at.isoformat() if a.published_at else None,
                    "sentiment": a.sentiment
                } for a in articles
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/sources")
async def get_sources(db: AsyncSession = Depends(get_session)):
    """Get news sources"""
    try:
        result = await db.execute(
            select(NewsArticle.source, func.count(NewsArticle.id).label('count'))
            .group_by(NewsArticle.source)
        )
        sources = result.all()
        return {
            "sources": [{"name": s.source, "article_count": s.count} for s in sources]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AI SERVICE
# ============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """AI Chat"""
    logger.info(f"💬 Chat request")
    try:
        response = await gemini_companion.chat_with_user(
            request.message,
            context={"user_id": request.user_id} if request.user_id else None
        )
        return {"response": response, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def explain_term(request: TermExplanationRequest):
    """Explain financial term"""
    try:
        explanation = await gemini_companion.explain_financial_term(request.term)
        return {"term": request.term, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/market-insights")
async def get_market_insights(db: AsyncSession = Depends(get_session)):
    """
    AI Market Insight Engine - Analyzes news to provide market intelligence
    Returns market mood, opportunities, threats, and detailed analysis
    """
    logger.info("🧠 Generating Market Insights...")
    
    try:
        # Step 1: Fetch latest 50 news articles
        result = await db.execute(
            select(NewsArticle)
            .order_by(NewsArticle.published_at.desc())
            .limit(50)
        )
        articles = result.scalars().all()
        
        if not articles:
            return {
                "market_mood": "Neutral",
                "avg_sentiment": 0.0,
                "global_risk": "Unknown",
                "summary": "No news data available for analysis",
                "opportunities": [],
                "threats": [],
                "processed_news": []
            }
        
        # Step 2: Process each article
        processed_articles = []
        sentiment_scores = []
        
        for article in articles:
            # Map sentiment to score
            sentiment_map = {"positive": 0.7, "neutral": 0.0, "negative": -0.7}
            sentiment_score = sentiment_map.get(article.sentiment, 0.0)
            sentiment_scores.append(sentiment_score)
            
            # Calculate relevance (based on keywords and source)
            relevance = calculate_relevance(article)
            
            # Calculate risk level
            risk_level = calculate_risk(article, sentiment_score)
            
            processed_articles.append({
                "title": article.title,
                "source": article.source,
                "sentiment": sentiment_score,
                "sentiment_label": article.sentiment,
                "risk": risk_level,
                "relevance": relevance,
                "summary": article.summary[:200] if article.summary else "No summary available",
                "url": article.url,
                "published_at": article.published_at.isoformat() if article.published_at else None
            })
        
        # Step 3: Calculate aggregate metrics
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # Market mood determination
        if avg_sentiment > 0.3:
            market_mood = "Bullish 📈"
        elif avg_sentiment < -0.3:
            market_mood = "Bearish 📉"
        else:
            market_mood = "Neutral ➡️"
        
        # Global risk assessment
        negative_count = sum(1 for s in sentiment_scores if s < -0.3)
        risk_ratio = negative_count / len(sentiment_scores) if sentiment_scores else 0
        
        if risk_ratio > 0.5:
            global_risk = "High"
        elif risk_ratio > 0.3:
            global_risk = "Medium"
        else:
            global_risk = "Low"
        
        # Step 4: Identify opportunities (positive sentiment + high relevance)
        opportunities = sorted(
            [a for a in processed_articles if a['sentiment'] > 0.3 and a['relevance'] in ['High', 'Medium']],
            key=lambda x: x['sentiment'],
            reverse=True
        )[:5]
        
        # Add AI reasoning for opportunities
        for opp in opportunities:
            opp['reason'] = generate_opportunity_reason(opp)
        
        # Step 5: Identify threats (negative sentiment + high relevance)
        threats = sorted(
            [a for a in processed_articles if a['sentiment'] < -0.3 and a['relevance'] in ['High', 'Medium']],
            key=lambda x: x['sentiment']
        )[:5]
        
        # Add AI reasoning for threats
        for threat in threats:
            threat['reason'] = generate_threat_reason(threat)
        
        # Step 6: Generate AI summary
        summary = await generate_market_summary(avg_sentiment, market_mood, global_risk, len(articles))
        
        logger.info(f"✅ Market Insights: {market_mood}, Sentiment: {avg_sentiment:.2f}, Risk: {global_risk}")
        
        return {
            "market_mood": market_mood,
            "avg_sentiment": round(avg_sentiment, 3),
            "global_risk": global_risk,
            "confidence_score": round(min(len(articles) / 50.0, 1.0), 2),
            "summary": summary,
            "opportunities": opportunities,
            "threats": threats,
            "processed_news": processed_articles[:20],  # Return top 20 for display
            "total_analyzed": len(articles),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Market Insights error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for Market Insights
def calculate_relevance(article: NewsArticle) -> str:
    """Calculate market relevance based on keywords and source"""
    title_lower = article.title.lower()
    
    # High relevance keywords
    high_keywords = ['market', 'stock', 'trading', 'economy', 'fed', 'inflation', 'rate', 'earnings']
    medium_keywords = ['finance', 'investment', 'investor', 'wall street', 'nasdaq', 'dow']
    
    # Check keywords
    high_count = sum(1 for kw in high_keywords if kw in title_lower)
    medium_count = sum(1 for kw in medium_keywords if kw in title_lower)
    
    if high_count >= 2 or article.source in ['Alpha Vantage', 'Finnhub']:
        return 'High'
    elif high_count >= 1 or medium_count >= 1:
        return 'Medium'
    else:
        return 'Low'

def calculate_risk(article: NewsArticle, sentiment_score: float) -> str:
    """Calculate risk level based on sentiment and keywords"""
    title_lower = article.title.lower()
    
    # Risk keywords
    high_risk_words = ['crash', 'crisis', 'collapse', 'threat', 'warning', 'danger', 'fraud']
    medium_risk_words = ['concern', 'worry', 'decline', 'fall', 'drop', 'risk']
    
    risk_count = sum(1 for word in high_risk_words if word in title_lower)
    
    if risk_count > 0 or sentiment_score < -0.6:
        return 'High'
    elif sum(1 for word in medium_risk_words if word in title_lower) > 0 or sentiment_score < -0.3:
        return 'Medium'
    else:
        return 'Low'

def generate_opportunity_reason(article: Dict) -> str:
    """Generate reasoning for why this is an opportunity"""
    reasons = []
    
    if article['sentiment'] > 0.6:
        reasons.append("Strong positive sentiment")
    if article['relevance'] == 'High':
        reasons.append("High market relevance")
    if 'growth' in article['title'].lower() or 'gain' in article['title'].lower():
        reasons.append("Growth indicators")
    
    return " | ".join(reasons) if reasons else "Positive market signal"

def generate_threat_reason(article: Dict) -> str:
    """Generate reasoning for why this is a threat"""
    reasons = []
    
    if article['sentiment'] < -0.6:
        reasons.append("Strong negative sentiment")
    if article['risk'] == 'High':
        reasons.append("High risk indicators")
    if article['relevance'] == 'High':
        reasons.append("High market impact")
    
    return " | ".join(reasons) if reasons else "Negative market signal"

async def generate_market_summary(avg_sentiment: float, mood: str, risk: str, article_count: int) -> str:
    """Generate AI-powered market summary using Gemini with timeout"""
    try:
        import asyncio
        
        prompt = f"""Based on analysis of {article_count} recent financial news articles:
- Market Mood: {mood}
- Average Sentiment: {avg_sentiment:.2f}
- Global Risk Level: {risk}

Provide a brief 2-sentence market summary for investors. Be concise and actionable."""
        
        # Add 5-second timeout for AI call
        summary = await asyncio.wait_for(
            gemini_companion.chat_with_user(prompt),
            timeout=5.0
        )
        return summary
    except asyncio.TimeoutError:
        logger.warning("⚠️ AI summary timed out, using fallback")
        # Fallback to rule-based summary
        if avg_sentiment > 0.3:
            return f"Markets showing bullish sentiment based on {article_count} articles analyzed. Overall outlook appears positive with {risk.lower()} risk levels."
        elif avg_sentiment < -0.3:
            return f"Markets showing bearish sentiment based on {article_count} articles analyzed. Caution advised with {risk.lower()} risk levels."
        else:
            return f"Markets showing neutral sentiment based on {article_count} articles analyzed. Mixed signals with {risk.lower()} overall risk."
    except Exception as e:
        logger.warning(f"⚠️ AI summary error: {e}, using fallback")
        # Fallback to rule-based summary
        if avg_sentiment > 0.3:
            return f"Markets showing bullish sentiment based on {article_count} articles analyzed. Overall outlook appears positive with {risk.lower()} risk levels."
        elif avg_sentiment < -0.3:
            return f"Markets showing bearish sentiment based on {article_count} articles analyzed. Caution advised with {risk.lower()} risk levels."
        else:
            return f"Markets showing neutral sentiment based on {article_count} articles analyzed. Mixed signals with {risk.lower()} overall risk."

# ============================================================================
# RISK SERVICE
# ============================================================================

@app.get("/api/risk/analyze-portfolio/{user_id}")
async def analyze_portfolio(user_id: int, db: AsyncSession = Depends(get_session)):
    """Analyze portfolio risk"""
    try:
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        if not investments:
            return {"overall_risk": "low", "risk_score": 0.0}
        
        total_risk = 0
        for inv in investments:
            risk_analysis = risk_engine.predict_risk_score({
                "symbol": inv.symbol,
                "asset_type": inv.asset_type,
                "purchase_price": inv.purchase_price,
                "current_price": inv.current_price or inv.purchase_price,
                "quantity": inv.quantity
            })
            total_risk += risk_analysis['risk_score']
        
        avg_risk = total_risk / len(investments)
        overall_risk = "high" if avg_risk >= 0.7 else "medium" if avg_risk >= 0.4 else "low"
        return {"overall_risk": overall_risk, "risk_score": round(avg_risk, 3)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/portfolio-ai-report")
async def ai_portfolio_risk_report(user_id: int, db: AsyncSession = Depends(get_session)):
    """
    AI Portfolio Risk Engine V2 - Deep Intelligence Analysis
    Combines portfolio data + market intelligence + volatility + AI reasoning
    """
    logger.info(f"🧠 Generating AI Risk Report for user {user_id}...")
    
    try:
        # Step 1: Fetch portfolio data
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        
        if not investments:
            return {
                "overall_risk": "Low",
                "score": 0,
                "message": "No investments in portfolio",
                "alerts": [],
                "opportunities": [],
                "threats": [],
                "ai_summary": "You don't have any investments yet. Start building your portfolio!"
            }
        
        # Step 2: Fetch market intelligence
        news_result = await db.execute(
            select(NewsArticle)
            .order_by(NewsArticle.published_at.desc())
            .limit(50)
        )
        market_news = news_result.scalars().all()
        
        # Step 3: Build portfolio analysis
        portfolio_holdings = []
        total_value = 0
        total_invested = 0
        
        for inv in investments:
            # Get live price (returns dict with 'price' key)
            price_data = get_live_price(inv.symbol) 
            current_price = price_data.get('price') if price_data else None
            current_price = current_price or inv.current_price or inv.purchase_price
            
            value = current_price * inv.quantity
            invested = inv.purchase_price * inv.quantity
            
            portfolio_holdings.append({
                "symbol": inv.symbol,
                "asset_type": inv.asset_type,
                "quantity": inv.quantity,
                "purchase_price": inv.purchase_price,
                "current_price": current_price,
                "invested": invested,
                "current_value": value,
                "gain_loss": value - invested,
                "gain_loss_pct": ((value - invested) / invested * 100) if invested > 0 else 0
            })
            
            total_value += value
            total_invested += invested
        
        # Step 4: Compute risk metrics
        logger.info("Computing concentration...")
        concentration_analysis = compute_concentration(portfolio_holdings, total_value)
        logger.info(f"Concentration score: {concentration_analysis.get('score', 0)}")
        
        logger.info("Computing volatility...")
        volatility_analysis = compute_volatility(portfolio_holdings)
        logger.info(f"Volatility score: {volatility_analysis.get('score', 0)}")
        
        logger.info("Matching news to holdings...")
        news_sentiment_match = match_news_to_holdings(portfolio_holdings, market_news)
        logger.info(f"Sentiment score: {news_sentiment_match.get('score', 0)}")
        
        logger.info("Computing exposure...")
        exposure_analysis = compute_sector_exposure(portfolio_holdings)
        logger.info(f"Exposure score: {exposure_analysis.get('score', 0)}")
        
        # Step 5: Calculate final risk score
        concentration_score = float(concentration_analysis.get('score', 0))
        volatility_score = float(volatility_analysis.get('score', 0))
        sentiment_score = float(news_sentiment_match.get('score', 0))
        exposure_score = float(exposure_analysis.get('score', 0))
        
        risk_components = {
            "concentration_risk": concentration_score,
            "volatility_risk": volatility_score,
            "sentiment_risk": sentiment_score,
            "exposure_risk": exposure_score
        }
        
        logger.info(f"Risk components: {risk_components}")
        
        final_risk_score = (
            concentration_score * 0.3 +
            volatility_score * 0.25 +
            sentiment_score * 0.25 +
            exposure_score * 0.2
        )
        
        # Step 6: Determine overall risk level
        if final_risk_score >= 70:
            overall_risk = "High"
        elif final_risk_score >= 40:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"
        
        # Step 7: Collect alerts/red flags
        alerts = []
        alerts.extend(concentration_analysis.get('alerts', []))
        alerts.extend(volatility_analysis.get('alerts', []))
        alerts.extend(news_sentiment_match.get('alerts', []))
        alerts.extend(exposure_analysis.get('alerts', []))
        
        # Step 8: Find opportunities (market insights matching holdings)
        opportunities = find_opportunities_for_holdings(portfolio_holdings, market_news)
        
        # Step 9: Find threats (negative news matching holdings)
        threats = find_threats_for_holdings(portfolio_holdings, market_news)
        
        # Step 10: Generate AI summary
        ai_summary = await generate_ai_risk_summary(
            portfolio_holdings=portfolio_holdings,
            risk_score=final_risk_score,
            overall_risk=overall_risk,
            alerts=alerts,
            concentration=concentration_analysis,
            news_sentiment=news_sentiment_match,
            total_value=total_value,
            total_gain_loss=(total_value - total_invested)
        )
        
        logger.info(f"✅ AI Risk Report: {overall_risk} (Score: {final_risk_score:.0f})")
        
        return {
            "overall_risk": overall_risk,
            "score": round(final_risk_score, 1),
            "risk_components": {
                "concentration": round(risk_components['concentration_risk'], 1),
                "volatility": round(risk_components['volatility_risk'], 1),
                "sentiment": round(risk_components['sentiment_risk'], 1),
                "exposure": round(risk_components['exposure_risk'], 1)
            },
            "alerts": alerts,
            "opportunities": opportunities,
            "threats": threats,
            "portfolio_summary": {
                "total_holdings": len(portfolio_holdings),
                "total_value": round(total_value, 2),
                "total_invested": round(total_invested, 2),
                "total_gain_loss": round(total_value - total_invested, 2),
                "total_gain_loss_pct": round(((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2)
            },
            "concentration_analysis": concentration_analysis,
            "volatility_analysis": volatility_analysis,
            "sentiment_analysis": news_sentiment_match,
            "exposure_analysis": exposure_analysis,
            "per_asset_risk": [
                {
                    "symbol": h['symbol'],
                    "risk_level": "High" if h['gain_loss_pct'] < -15 else "Medium" if h['gain_loss_pct'] < -5 else "Low",
                    "value_pct": round((h['current_value'] / total_value * 100), 1)
                }
                for h in portfolio_holdings
            ],
            "ai_summary": ai_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ AI Risk Report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for AI Portfolio Risk Engine
def compute_concentration(holdings: List[Dict], total_value: float) -> Dict:
    """Compute concentration risk - is portfolio too concentrated in one asset?"""
    if not holdings or total_value == 0:
        return {"score": 0, "alerts": [], "top_holding_pct": 0}
    
    # Calculate percentage of each holding
    holdings_pct = [(h['symbol'], (h['current_value'] / total_value * 100)) for h in holdings]
    holdings_pct.sort(key=lambda x: x[1], reverse=True)
    
    top_holding_pct = holdings_pct[0][1]
    
    alerts = []
    score = 0
    
    # High concentration if one asset > 40%
    if top_holding_pct > 40:
        score = 80
        alerts.append(f"⚠️ High concentration: {holdings_pct[0][0]} represents {top_holding_pct:.1f}% of portfolio")
    elif top_holding_pct > 25:
        score = 50
        alerts.append(f"📊 Moderate concentration: {holdings_pct[0][0]} represents {top_holding_pct:.1f}% of portfolio")
    else:
        score = 20
    
    return {
        "score": score,
        "alerts": alerts,
        "top_holding": holdings_pct[0][0],
        "top_holding_pct": round(top_holding_pct, 1),
        "holdings_distribution": [{"symbol": s, "pct": round(p, 1)} for s, p in holdings_pct[:5]]
    }

def compute_volatility(holdings: List[Dict]) -> Dict:
    """Compute volatility risk - prototype with simple gain/loss variance"""
    if not holdings:
        return {"score": 0, "alerts": []}
    
    # Use gain/loss percentage as proxy for volatility
    gain_loss_values = [h['gain_loss_pct'] for h in holdings]
    
    # Calculate standard deviation (simple)
    if len(gain_loss_values) > 1:
        mean = sum(gain_loss_values) / len(gain_loss_values)
        variance = sum((x - mean) ** 2 for x in gain_loss_values) / len(gain_loss_values)
        std_dev = variance ** 0.5
    else:
        std_dev = abs(gain_loss_values[0]) if gain_loss_values else 0
    
    alerts = []
    
    # High volatility if std dev > 20%
    if std_dev > 20:
        score = 75
        alerts.append(f"📈 High volatility detected: Portfolio variance is {std_dev:.1f}%")
    elif std_dev > 10:
        score = 45
        alerts.append(f"📊 Moderate volatility: Portfolio variance is {std_dev:.1f}%")
    else:
        score = 20
    
    return {
        "score": score,
        "alerts": alerts,
        "std_deviation": round(std_dev, 2),
        "variance_level": "High" if std_dev > 20 else "Medium" if std_dev > 10 else "Low"
    }

def match_news_to_holdings(holdings: List[Dict], news_articles: List) -> Dict:
    """Match news sentiment to portfolio holdings"""
    if not holdings or not news_articles:
        return {"score": 30, "alerts": [], "matches": []}
    
    symbols = [h['symbol'].lower() for h in holdings]
    matches = []
    alerts = []
    
    sentiment_map = {"positive": 0.7, "neutral": 0.0, "negative": -0.7}
    
    for article in news_articles:
        title_lower = article.title.lower()
        
        # Check if any holding symbol mentioned in news
        for holding in holdings:
            symbol = holding['symbol'].lower()
            
            # Simple keyword matching
            if symbol in title_lower or holding['asset_type'].lower() in title_lower:
                sentiment_score = sentiment_map.get(article.sentiment, 0.0)
                
                matches.append({
                    "symbol": holding['symbol'],
                    "article_title": article.title,
                    "sentiment": article.sentiment,
                    "sentiment_score": sentiment_score,
                    "source": article.source
                })
                
                # Alert if negative news about holding
                if sentiment_score < -0.3:
                    alerts.append(f"🔴 Negative news about {holding['symbol']}: {article.title[:80]}...")
    
    # Calculate sentiment risk score
    if matches:
        avg_sentiment = sum(m['sentiment_score'] for m in matches) / len(matches)
        
        if avg_sentiment < -0.3:
            score = 70
        elif avg_sentiment < 0:
            score = 45
        else:
            score = 25
    else:
        score = 30  # No news is neutral
    
    return {
        "score": score,
        "alerts": alerts,
        "matches": matches[:10],  # Top 10 matches
        "total_matches": len(matches)
    }

def compute_sector_exposure(holdings: List[Dict]) -> Dict:
    """Compute sector exposure risk"""
    if not holdings:
        return {"score": 0, "alerts": []}
    
    # Group by asset type as proxy for sector
    sector_distribution = {}
    total_value = sum(h['current_value'] for h in holdings)
    
    for h in holdings:
        sector = h['asset_type']
        if sector not in sector_distribution:
            sector_distribution[sector] = 0
        sector_distribution[sector] += h['current_value']
    
    # Calculate percentages
    sector_pcts = {
        sector: (value / total_value * 100)
        for sector, value in sector_distribution.items()
    }
    
    alerts = []
    max_sector = max(sector_pcts.items(), key=lambda x: x[1]) if sector_pcts else ("Unknown", 0)
    
    if max_sector[1] > 50:
        score = 70
        alerts.append(f"⚠️ Heavy sector concentration: {max_sector[0]} = {max_sector[1]:.1f}%")
    elif max_sector[1] > 35:
        score = 45
        alerts.append(f"📊 Moderate sector concentration: {max_sector[0]} = {max_sector[1]:.1f}%")
    else:
        score = 20
    
    return {
        "score": score,
        "alerts": alerts,
        "sector_distribution": {k: round(v, 1) for k, v in sector_pcts.items()},
        "dominant_sector": max_sector[0],
        "dominant_sector_pct": round(max_sector[1], 1)
    }

def find_opportunities_for_holdings(holdings: List[Dict], news_articles: List) -> List[Dict]:
    """Find positive news opportunities related to holdings"""
    opportunities = []
    symbols = [h['symbol'].lower() for h in holdings]
    
    sentiment_map = {"positive": 0.7, "neutral": 0.0, "negative": -0.7}
    
    for article in news_articles:
        if article.sentiment != "positive":
            continue
            
        title_lower = article.title.lower()
        
        for holding in holdings:
            symbol = holding['symbol'].lower()
            if symbol in title_lower or holding['asset_type'].lower() in title_lower:
                opportunities.append({
                    "symbol": holding['symbol'],
                    "title": article.title,
                    "summary": article.summary[:150] if article.summary else "No summary",
                    "sentiment_score": sentiment_map[article.sentiment],
                    "source": article.source,
                    "url": article.url
                })
                break
    
    return opportunities[:5]  # Top 5

def find_threats_for_holdings(holdings: List[Dict], news_articles: List) -> List[Dict]:
    """Find negative news threats related to holdings"""
    threats = []
    symbols = [h['symbol'].lower() for h in holdings]
    
    sentiment_map = {"positive": 0.7, "neutral": 0.0, "negative": -0.7}
    
    for article in news_articles:
        if article.sentiment != "negative":
            continue
            
        title_lower = article.title.lower()
        
        for holding in holdings:
            symbol = holding['symbol'].lower()
            if symbol in title_lower or holding['asset_type'].lower() in title_lower:
                threats.append({
                    "symbol": holding['symbol'],
                    "title": article.title,
                    "summary": article.summary[:150] if article.summary else "No summary",
                    "sentiment_score": sentiment_map[article.sentiment],
                    "source": article.source,
                    "url": article.url
                })
                break
    
    return threats[:5]  # Top 5

async def generate_ai_risk_summary(
    portfolio_holdings: List[Dict],
    risk_score: float,
    overall_risk: str,
    alerts: List[str],
    concentration: Dict,
    news_sentiment: Dict,
    total_value: float,
    total_gain_loss: float
) -> str:
    """Generate AI-powered risk summary using Gemini"""
    try:
        # Build context for Gemini
        holdings_summary = ", ".join([f"{h['symbol']} ({h['asset_type']})" for h in portfolio_holdings[:5]])
        
        prompt = f"""You are a financial advisor analyzing a portfolio. Provide a brief 5-sentence risk assessment.

Portfolio Overview:
- Total Value: ${total_value:,.2f}
- Total Gain/Loss: ${total_gain_loss:,.2f}
- Holdings: {holdings_summary}
- Risk Score: {risk_score:.0f}/100 ({overall_risk})

Key Concerns:
{chr(10).join(alerts[:3]) if alerts else "No major concerns"}

Top Concentration: {concentration.get('top_holding', 'N/A')} at {concentration.get('top_holding_pct', 0):.1f}%
News Sentiment Matches: {news_sentiment.get('total_matches', 0)} articles

Provide actionable advice for this investor. Be specific and professional."""
        
        summary = await gemini_companion.chat_with_user(prompt)
        return summary
        
    except Exception as e:
        logger.error(f"AI summary generation failed: {e}")
        # Fallback to rule-based summary
        if risk_score >= 70:
            return f"Your portfolio has HIGH risk (score: {risk_score:.0f}/100). Main concerns: {', '.join(alerts[:2]) if alerts else 'portfolio concentration'}. Consider diversifying your holdings and reducing exposure to high-risk assets."
        elif risk_score >= 40:
            return f"Your portfolio has MEDIUM risk (score: {risk_score:.0f}/100). Watch out for: {', '.join(alerts[:2]) if alerts else 'market volatility'}. Your portfolio is reasonably balanced but could benefit from some adjustments."
        else:
            return f"Your portfolio has LOW risk (score: {risk_score:.0f}/100). Your investments are well-diversified with ${total_value:,.2f} in total value. Continue monitoring market conditions and maintain your balanced approach."

# ============================================================================
# AI INVESTMENT RECOMMENDATIONS
# ============================================================================

@app.get("/api/ai/recommendations")
async def get_investment_recommendations(user_id: int, db: AsyncSession = Depends(get_session)):
    """Generate personalized AI investment recommendations"""
    logger.info(f"🤖 Generating AI recommendations for user {user_id}")
    
    try:
        # 1. Get user's portfolio
        result = await db.execute(
            select(Investment).where(Investment.user_id == user_id)
        )
        investments = result.scalars().all()
        
        if not investments:
            return {
                "recommended_buys": [],
                "recommended_sells": [],
                "diversification_plan": [],
                "overall_summary": "No portfolio data available. Start investing to get personalized recommendations!"
            }
        
        # 2. Build portfolio summary
        portfolio_data = []
        total_value = 0
        sector_distribution = {}
        
        for inv in investments:
            # Get price data (returns dict with 'price' key)
            price_data = get_live_price(inv.symbol)
            current_price = price_data.get('price', inv.purchase_price) if price_data else inv.purchase_price
            current_value = inv.quantity * current_price
            total_value += current_value
            
            portfolio_data.append({
                "symbol": inv.symbol,
                "quantity": inv.quantity,
                "avg_price": inv.purchase_price,
                "current_price": current_price,
                "current_value": current_value,
                "gain_loss": current_value - (inv.quantity * inv.purchase_price),
                "allocation_percent": 0  # Will calculate after total
            })
        
        # Calculate allocation percentages
        for item in portfolio_data:
            item["allocation_percent"] = round((item["current_value"] / total_value) * 100, 2)
            # Simple sector mapping (you can enhance this)
            if item["symbol"] in ["GOOGL", "AAPL", "MSFT", "META"]:
                sector_distribution["Technology"] = sector_distribution.get("Technology", 0) + item["allocation_percent"]
            elif item["symbol"] in ["JPM", "BAC", "WFC"]:
                sector_distribution["Finance"] = sector_distribution.get("Finance", 0) + item["allocation_percent"]
            else:
                sector_distribution["Other"] = sector_distribution.get("Other", 0) + item["allocation_percent"]
        
        # 3. Get risk analysis (if available)
        risk_data = {}
        try:
            result = await db.execute(
                select(RiskAlert)
                .where(RiskAlert.user_id == user_id)
                .order_by(RiskAlert.created_at.desc())
                .limit(5)
            )
            alerts = result.scalars().all()
            risk_data = {
                "total_alerts": len(alerts),
                "alert_types": [a.alert_type for a in alerts],
                "severity": [a.severity for a in alerts]
            }
        except:
            pass
        
        # 4. Get recent news
        news_data = []
        try:
            symbols = [inv.symbol for inv in investments]
            news_fetcher = get_news_fetcher()
            for symbol in symbols[:3]:  # Limit to top 3 holdings
                articles = await news_fetcher.fetch_news(symbol, max_results=2)
                for article in articles:
                    news_data.append({
                        "symbol": symbol,
                        "title": article.get("title", ""),
                        "sentiment": article.get("sentiment_score", 0)
                    })
        except:
            pass
        
        # 5. Build Gemini AI prompt
        prompt = f"""You are a professional financial advisor AI.

USER PORTFOLIO:
Total Value: ${total_value:,.2f}
Holdings: {len(portfolio_data)} stocks

Portfolio Breakdown:
{chr(10).join([f"- {p['symbol']}: {p['allocation_percent']}% (${p['current_value']:,.2f})" for p in portfolio_data])}

Sector Distribution:
{chr(10).join([f"- {sector}: {pct:.1f}%" for sector, pct in sector_distribution.items()])}

RISK ANALYSIS:
Total Alerts: {risk_data.get('total_alerts', 0)}
Main Concerns: {', '.join(risk_data.get('alert_types', [])) if risk_data.get('alert_types') else 'None'}

RECENT NEWS SENTIMENT:
{chr(10).join([f"- {n['symbol']}: {n['title'][:50]}... (sentiment: {n['sentiment']:.2f})" for n in news_data[:3]]) if news_data else 'No recent news'}

TASK:
Generate personalized investment recommendations for this user.

STRICT OUTPUT FORMAT - RESPOND WITH VALID JSON ONLY:
{{
    "recommended_buys": [
        {{"symbol": "RELIANCE", "reason": "Strong fundamentals in growing sector", "allocation_percent": 10}},
        {{"symbol": "TCS", "reason": "IT sector diversification needed", "allocation_percent": 8}},
        {{"symbol": "HDFC", "reason": "Banking sector exposure", "allocation_percent": 7}}
    ],
    "recommended_sells": [
        {{"symbol": "GOOGL", "reason": "Over-concentrated position - reduce to 25%"}},
        {{"symbol": "AAPL", "reason": "Take partial profits, rebalance"}}
    ],
    "diversification_plan": [
        {{"sector": "Healthcare", "target_percent": 15, "why": "Currently 0% - add defensive stocks"}},
        {{"sector": "Energy", "target_percent": 10, "why": "Hedge against inflation"}},
        {{"sector": "Finance", "target_percent": 20, "why": "Stable dividends and growth"}}
    ],
    "overall_summary": "Your portfolio is heavily concentrated in tech stocks ({sector_distribution.get('Technology', 0):.0f}%). Consider diversifying across healthcare, finance, and energy sectors to reduce risk. Reduce GOOGL position from current level and add defensive stocks."
}}

IMPORTANT: 
- Respond ONLY with valid JSON
- No markdown formatting
- No explanations outside the JSON
- Base recommendations on actual portfolio data
- Suggest realistic allocation percentages
"""
        
        # 6. Call Gemini AI
        try:
            ai_response = await gemini_companion.chat_with_user(prompt)
            
            # Try to parse JSON from response
            import json
            import re
            
            # Extract JSON if wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = ai_response
            
            recommendations = json.loads(json_str)
            
            # Validate structure
            if not all(key in recommendations for key in ["recommended_buys", "recommended_sells", "diversification_plan", "overall_summary"]):
                raise ValueError("Invalid JSON structure")
            
            logger.info(f"✅ AI recommendations generated successfully")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ AI parsing failed: {str(e)}, using fallback")
            
            # Fallback recommendations based on rules
            return {
                "recommended_buys": [
                    {"symbol": "TCS", "reason": "Strong IT company for portfolio diversification", "allocation_percent": 10},
                    {"symbol": "RELIANCE", "reason": "Large cap stock with diverse business", "allocation_percent": 10},
                    {"symbol": "HDFC", "reason": "Banking sector leader for stability", "allocation_percent": 8}
                ],
                "recommended_sells": [
                    {"symbol": portfolio_data[0]["symbol"] if portfolio_data else "N/A", 
                     "reason": f"Reduce concentration - currently {portfolio_data[0]['allocation_percent']:.0f}% of portfolio"}
                ] if portfolio_data and portfolio_data[0]["allocation_percent"] > 40 else [],
                "diversification_plan": [
                    {"sector": "Healthcare", "target_percent": 15, "why": "Add defensive stocks for stability"},
                    {"sector": "Finance", "target_percent": 20, "why": "Banking stocks provide steady dividends"},
                    {"sector": "Consumer Goods", "target_percent": 10, "why": "Essential sector for all-weather portfolio"}
                ],
                "overall_summary": f"Your portfolio of ${total_value:,.2f} needs better diversification. Consider reducing concentration in {list(sector_distribution.keys())[0] if sector_distribution else 'current holdings'} sector and adding exposure to healthcare, finance, and consumer goods."
            }
    
    except Exception as e:
        logger.error(f"❌ Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

# ============================================================================
# FRAUD DETECTION SERVICE
# ============================================================================

@app.post("/api/fraud/detect-scam")
async def detect_scam(request: ScamCheckRequest):
    """Detect scam"""
    try:
        ai_analysis = await gemini_companion.detect_scam_language(request.message)
        rule_analysis = fraud_detector.analyze_message(request.message, request.sender)
        combined_risk = max(ai_analysis.get('confidence', 0), rule_analysis.get('risk_score', 0))
        return {
            "is_suspicious": combined_risk >= 0.4,
            "confidence": round(combined_risk, 3),
            "red_flags": ai_analysis.get('red_flags', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fraud/check-url")
async def check_url(request: URLCheckRequest):
    """Check URL safety"""
    try:
        analysis = fraud_detector.analyze_url(request.url)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LEARNING SERVICE
# ============================================================================

@app.get("/api/learning/module/{topic}")
async def get_module(topic: str, difficulty: str = "beginner"):
    """Get learning module"""
    try:
        content = await gemini_companion.generate_learning_content(topic, difficulty)
        return {"topic": topic, "difficulty": difficulty, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning/progress/{user_id}")
async def get_progress(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get learning progress"""
    try:
        result = await db.execute(select(LearningProgress).where(LearningProgress.user_id == user_id))
        progress = result.scalars().all()
        return {
            "modules_completed": len([p for p in progress if p.completion_percentage >= 100]),
            "modules_in_progress": len([p for p in progress if 0 < p.completion_percentage < 100])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
