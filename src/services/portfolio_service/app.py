"""
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
from legacy_modules.price_service import get_live_price

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

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int, db: AsyncSession = Depends(get_session)):
    """Get comprehensive dashboard data for frontend"""
    logger.info(f"📊 Fetching dashboard for user {user_id}")
    try:
        # Fetch all investments
        result = await db.execute(select(Investment).where(Investment.user_id == user_id))
        investments = result.scalars().all()
        
        # Calculate portfolio summary
        total_invested = sum(inv.purchase_price * inv.quantity for inv in investments)
        total_value = sum(inv.current_price * inv.quantity for inv in investments if inv.current_price)
        gain_loss = total_value - total_invested if total_value > 0 else 0
        gain_loss_percentage = (gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Top performers (by percentage gain)
        performers = []
        for inv in investments:
            if inv.current_price and inv.purchase_price > 0:
                gain_pct = ((inv.current_price - inv.purchase_price) / inv.purchase_price) * 100
                performers.append({
                    "symbol": inv.symbol,
                    "gain_percentage": gain_pct,
                    "gain_amount": (inv.current_price - inv.purchase_price) * inv.quantity
                })
        
        # Sort by gain percentage
        top_performers = sorted(performers, key=lambda x: x['gain_percentage'], reverse=True)[:3]
        bottom_performers = sorted(performers, key=lambda x: x['gain_percentage'])[:3]
        
        return {
            "portfolio_summary": {
                "total_invested": total_invested,
                "total_value": total_value,
                "gain_loss": gain_loss,
                "gain_loss_percentage": gain_loss_percentage,
                "num_investments": len(investments)
            },
            "top_performers": top_performers,
            "bottom_performers": bottom_performers,
            "recent_investments": [
                {
                    "symbol": inv.symbol,
                    "asset_type": inv.asset_type,
                    "quantity": inv.quantity,
                    "purchase_price": inv.purchase_price
                } for inv in sorted(investments, key=lambda x: x.id, reverse=True)[:5]
            ]
        }
    except Exception as e:
        logger.error(f"❌ Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)
