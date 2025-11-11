"""
News Fetcher Service - Collects financial news from multiple sources
Integrated into FinBuddy
"""
import feedparser
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

# API Keys - Set these as environment variables or in config
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")  # Get free key from newsapi.org
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")  # Get from alphavantage.co
FINNHUB_KEY = os.getenv("FINNHUB_KEY", "")  # Get from finnhub.io


class NewsFetcher:
    """Fetches financial news from multiple RSS and API sources"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.sources = {
            'economic_times': 'Economic Times',
            'zerodha': 'Zerodha Pulse',
            'newsapi': 'NewsAPI',
            'alpha_vantage': 'Alpha Vantage',
            'finnhub': 'Finnhub',
            'marketaux': 'Marketaux',
            'gnews': 'GNews'
        }
    
    async def fetch_economic_times_rss(self) -> List[Dict]:
        """Fetch news from Economic Times RSS feed"""
        url = "https://economictimes.indiatimes.com/markets/rss.cms"
        logger.info(f"📰 Fetching from Economic Times RSS...")
        
        try:
            response = await self.client.get(url)
            feed = feedparser.parse(response.text)
            
            logger.info(f"Feed has {len(feed.entries)} entries")
            
            articles = []
            for entry in feed.entries[:20]:  # Get latest 20 articles
                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Get sentiment
                text = f"{entry.get('title', '')} {entry.get('summary', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': entry.get('title', 'No Title'),
                    'summary': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'published_at': pub_date or datetime.utcnow(),
                    'source': 'Economic Times',
                    'content': entry.get('description', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from Economic Times")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching Economic Times: {e}")
            return []
    
    async def fetch_zerodha_pulse_rss(self) -> List[Dict]:
        """Fetch news from Zerodha Pulse RSS feed"""
        url = "https://zerodha.com/z-connect/feed"
        logger.info(f"📰 Fetching from Zerodha Pulse RSS...")
        
        try:
            response = await self.client.get(url)
            feed = feedparser.parse(response.text)
            
            logger.info(f"Zerodha feed has {len(feed.entries)} entries")
            
            articles = []
            for entry in feed.entries[:20]:
                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                
                # Get sentiment
                text = f"{entry.get('title', '')} {entry.get('summary', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': entry.get('title', 'No Title'),
                    'summary': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'published_at': pub_date or datetime.utcnow(),
                    'source': 'Zerodha Pulse',
                    'content': entry.get('description', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from Zerodha Pulse")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching Zerodha Pulse: {e}")
            return []
    
    async def fetch_newsapi(self) -> List[Dict]:
        """Fetch news from NewsAPI (Free tier: 100 requests/day)"""
        if not NEWSAPI_KEY:
            logger.warning("⚠️ NewsAPI key not set, skipping...")
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'stock market OR finance OR trading OR economy',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 20,
            'apiKey': NEWSAPI_KEY
        }
        
        logger.info(f"📰 Fetching from NewsAPI...")
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"❌ NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                pub_date = datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00'))
                
                text = f"{item.get('title', '')} {item.get('description', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': item.get('title', 'No Title'),
                    'summary': item.get('description', ''),
                    'url': item.get('url', ''),
                    'published_at': pub_date,
                    'source': 'NewsAPI',
                    'content': item.get('content', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from NewsAPI")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching NewsAPI: {e}")
            return []
    
    async def fetch_alpha_vantage(self) -> List[Dict]:
        """Fetch news from Alpha Vantage (Free tier: 25 requests/day)"""
        if not ALPHA_VANTAGE_KEY:
            logger.warning("⚠️ Alpha Vantage key not set, skipping...")
            return []
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'topics': 'financial_markets',
            'apikey': ALPHA_VANTAGE_KEY,
            'limit': 50
        }
        
        logger.info(f"📰 Fetching from Alpha Vantage...")
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if 'feed' not in data:
                logger.error(f"❌ Alpha Vantage error: {data.get('Note', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('feed', [])[:20]:
                pub_date = datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S')
                
                text = f"{item.get('title', '')} {item.get('summary', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': item.get('title', 'No Title'),
                    'summary': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'published_at': pub_date,
                    'source': 'Alpha Vantage',
                    'content': item.get('summary', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from Alpha Vantage")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching Alpha Vantage: {e}")
            return []
    
    async def fetch_finnhub(self) -> List[Dict]:
        """Fetch news from Finnhub (Free tier: 60 requests/minute)"""
        if not FINNHUB_KEY:
            logger.warning("⚠️ Finnhub key not set, skipping...")
            return []
        
        url = "https://finnhub.io/api/v1/news"
        params = {
            'category': 'general',
            'token': FINNHUB_KEY
        }
        
        logger.info(f"📰 Fetching from Finnhub...")
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if isinstance(data, dict) and 'error' in data:
                logger.error(f"❌ Finnhub error: {data['error']}")
                return []
            
            articles = []
            for item in data[:20]:
                pub_date = datetime.fromtimestamp(item['datetime'])
                
                text = f"{item.get('headline', '')} {item.get('summary', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': item.get('headline', 'No Title'),
                    'summary': item.get('summary', ''),
                    'url': item.get('url', ''),
                    'published_at': pub_date,
                    'source': 'Finnhub',
                    'content': item.get('summary', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from Finnhub")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching Finnhub: {e}")
            return []
    
    async def fetch_marketaux(self) -> List[Dict]:
        """Fetch news from Marketaux (Free tier: 100 requests/day)"""
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'filter_entities': 'true',
            'language': 'en',
            'limit': 20
        }
        
        logger.info(f"📰 Fetching from Marketaux (no API key required)...")
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if 'data' not in data:
                logger.error(f"❌ Marketaux error: {data.get('error', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('data', []):
                pub_date = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                
                text = f"{item.get('title', '')} {item.get('description', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': item.get('title', 'No Title'),
                    'summary': item.get('description', ''),
                    'url': item.get('url', ''),
                    'published_at': pub_date,
                    'source': 'Marketaux',
                    'content': item.get('description', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from Marketaux")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching Marketaux: {e}")
            return []
    
    async def fetch_gnews(self) -> List[Dict]:
        """Fetch news from GNews (Free tier: 100 requests/day, no API key required for basic)"""
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            'category': 'business',
            'lang': 'en',
            'country': 'us',
            'max': 20,
            'apikey': os.getenv("GNEWS_KEY", "")  # Optional, can work without it
        }
        
        logger.info(f"📰 Fetching from GNews...")
        
        try:
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if 'articles' not in data:
                logger.error(f"❌ GNews error: {data.get('errors', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                pub_date = datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00'))
                
                text = f"{item.get('title', '')} {item.get('description', '')}"
                sentiment = self._analyze_sentiment(text)
                
                article = {
                    'title': item.get('title', 'No Title'),
                    'summary': item.get('description', ''),
                    'url': item.get('url', ''),
                    'published_at': pub_date,
                    'source': 'GNews',
                    'content': item.get('content', ''),
                    'sentiment': 'positive' if sentiment == 1 else 'negative' if sentiment == -1 else 'neutral',
                    'sentiment_score': sentiment
                }
                articles.append(article)
            
            logger.info(f"✅ Fetched {len(articles)} articles from GNews")
            return articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching GNews: {e}")
            return []
    
    async def fetch_all(self, sources: Optional[List[str]] = None) -> List[Dict]:
        """Fetch from all or selected sources
        
        Args:
            sources: List of source keys to fetch from. If None, fetches from all sources.
                    Valid keys: 'economic_times', 'zerodha', 'newsapi', 'alpha_vantage', 
                               'finnhub', 'marketaux', 'gnews'
        """
        all_articles = []
        
        # Default to all sources if none specified
        if sources is None:
            sources = list(self.sources.keys())
        
        # Fetch from selected sources
        if 'economic_times' in sources:
            et_articles = await self.fetch_economic_times_rss()
            all_articles.extend(et_articles)
        
        if 'zerodha' in sources:
            zp_articles = await self.fetch_zerodha_pulse_rss()
            all_articles.extend(zp_articles)
        
        if 'newsapi' in sources:
            na_articles = await self.fetch_newsapi()
            all_articles.extend(na_articles)
        
        if 'alpha_vantage' in sources:
            av_articles = await self.fetch_alpha_vantage()
            all_articles.extend(av_articles)
        
        if 'finnhub' in sources:
            fh_articles = await self.fetch_finnhub()
            all_articles.extend(fh_articles)
        
        if 'marketaux' in sources:
            mx_articles = await self.fetch_marketaux()
            all_articles.extend(mx_articles)
        
        if 'gnews' in sources:
            gn_articles = await self.fetch_gnews()
            all_articles.extend(gn_articles)
        
        logger.info(f"📊 Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def _analyze_sentiment(self, text: str) -> int:
        """Analyze sentiment using VADER
        Returns: -1 (negative), 0 (neutral), 1 (positive)
        """
        if not text:
            return 0
        
        try:
            scores = sentiment_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                return 1  # Positive
            elif compound <= -0.05:
                return -1  # Negative
            else:
                return 0  # Neutral
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return 0
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_news_fetcher = None

def get_news_fetcher() -> NewsFetcher:
    """Get or create news fetcher instance"""
    global _news_fetcher
    if _news_fetcher is None:
        _news_fetcher = NewsFetcher()
    return _news_fetcher
