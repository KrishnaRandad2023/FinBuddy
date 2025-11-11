"""
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
from legacy_modules.news_fetcher import get_news_fetcher

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
