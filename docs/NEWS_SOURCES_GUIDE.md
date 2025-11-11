# 📰 FinBuddy Multi-Source News Feature - Complete Guide

## 🌟 Overview

FinBuddy's Market News feature aggregates financial news from **7 different sources** with AI-powered sentiment analysis using VADER.

## 📡 News Sources

### RSS Feeds (Always Available)

1. **Economic Times** 🇮🇳

   - India's leading business newspaper
   - URL: https://economictimes.indiatimes.com/markets/rss.cms
   - No API key required

2. **Zerodha Pulse** 📈
   - Curated financial insights
   - URL: https://zerodha.com/z-connect/feed
   - No API key required

### API Sources (Free Tier)

3. **Marketaux** 💹

   - Market news aggregator
   - Limit: 100 requests/day
   - **No API key required!**

4. **NewsAPI** 🌐

   - Global news aggregator
   - Limit: 100 requests/day
   - Get key: https://newsapi.org/register
   - ENV: `NEWSAPI_KEY`

5. **Alpha Vantage** 📊

   - Financial market news
   - Limit: 25 requests/day
   - Get key: https://www.alphavantage.co/support/#api-key
   - ENV: `ALPHA_VANTAGE_KEY`

6. **Finnhub** 📈

   - Real-time financial news
   - Limit: 60 requests/minute
   - Get key: https://finnhub.io/register
   - ENV: `FINNHUB_KEY`

7. **GNews** 🌍
   - Global news aggregator
   - Limit: 100 requests/day
   - Get key: https://gnews.io/register
   - ENV: `GNEWS_KEY`

## 🎯 Features

### Multi-Source Selection

- **Checkboxes UI** - Select which sources to fetch from
- **Flexible Fetching** - Fetch from 1 or all 7 sources
- **Smart Defaults** - ET, Zerodha, and Marketaux enabled by default

### Sentiment Analysis

- **VADER Algorithm** - Pre-trained lexicon-based analyzer
- **3 Categories**: Positive 😊 | Neutral 😐 | Negative 😞
- **Compound Score Thresholds**:
  - Positive: >= 0.05
  - Negative: <= -0.05
  - Neutral: Between -0.05 and 0.05

### Filtering & Search

- **By Source** - Filter articles by news source
- **By Sentiment** - Show only positive/neutral/negative news
- **Limit Control** - Display up to 100 articles

### Data Management

- **URL-based Deduplication** - No duplicate articles
- **Source Statistics** - Track article counts per source
- **Timestamp Tracking** - Published & fetched timestamps

## 🏗️ Architecture

### File Structure

```
project_1/
├── news_fetcher.py          # News collection service (7 sources)
├── database.py              # NewsArticle model
├── main.py                  # API endpoints (/api/news/*)
├── app.py                   # Streamlit UI with checkboxes
├── API_KEYS_SETUP.md        # Guide for getting API keys
└── NEWS_SOURCES_GUIDE.md    # This file
```

### Data Flow

```
1. User selects sources (checkboxes)
2. Frontend sends POST /api/news/fetch with source list
3. Backend calls news_fetcher.fetch_all(sources)
4. Each source fetcher runs (RSS/API parsing)
5. VADER analyzes sentiment for each article
6. Articles saved to database (duplicates skipped)
7. Frontend displays with filters
```

## 🔧 Technical Implementation

### NewsFetcher Class

```python
class NewsFetcher:
    sources = {
        'economic_times': 'Economic Times',
        'zerodha': 'Zerodha Pulse',
        'newsapi': 'NewsAPI',
        'alpha_vantage': 'Alpha Vantage',
        'finnhub': 'Finnhub',
        'marketaux': 'Marketaux',
        'gnews': 'GNews'
    }

    # Individual fetch methods
    async def fetch_economic_times_rss()
    async def fetch_zerodha_pulse_rss()
    async def fetch_newsapi()
    async def fetch_alpha_vantage()
    async def fetch_finnhub()
    async def fetch_marketaux()
    async def fetch_gnews()

    # Main aggregator
    async def fetch_all(sources: List[str] = None)

    # Sentiment analysis
    def _analyze_sentiment(text: str) -> int
```

### API Endpoints

#### POST /api/news/fetch

Fetch news from selected sources

```python
Body: ["economic_times", "newsapi", "finnhub"]  # Optional, null = all
Response: {
    "message": "News fetch completed",
    "sources": ["economic_times", "newsapi"],
    "articles_fetched": 45,
    "new_articles_saved": 32,
    "duplicates_skipped": 13
}
```

#### GET /api/news/latest

Get articles with filters

```python
Query params:
  - limit: int (default 50, max 100)
  - source: str (optional filter)
  - sentiment: str (optional: positive/neutral/negative)

Response: {
    "articles": [...]
}
```

#### GET /api/news/sources

Get source statistics

```python
Response: {
    "sources": [
        {
            "name": "Economic Times",
            "count": 145,
            "last_fetch": "2025-11-06T10:30:00"
        },
        ...
    ]
}
```

## 🚀 Quick Start

### 1. Basic Usage (No API Keys)

Just use the default sources:

- ✅ Economic Times RSS
- ✅ Zerodha Pulse RSS
- ✅ Marketaux API

These work immediately without any setup!

### 2. Adding API Sources

#### Step 1: Get API Keys

Follow the guide in `API_KEYS_SETUP.md` to register for free API keys.

#### Step 2: Set Environment Variables

**Windows PowerShell:**

```powershell
$env:NEWSAPI_KEY = "your_key"
$env:ALPHA_VANTAGE_KEY = "your_key"
$env:FINNHUB_KEY = "your_key"
$env:GNEWS_KEY = "your_key"
```

**Linux/Mac:**

```bash
export NEWSAPI_KEY="your_key"
export ALPHA_VANTAGE_KEY="your_key"
export FINNHUB_KEY="your_key"
export GNEWS_KEY="your_key"
```

**Using .env file (Recommended):**

```env
NEWSAPI_KEY=abc123...
ALPHA_VANTAGE_KEY=xyz789...
FINNHUB_KEY=def456...
GNEWS_KEY=ghi012...
```

#### Step 3: Restart Backend

```bash
python main.py
```

#### Step 4: Select Sources in UI

1. Navigate to "📰 Market News"
2. Check the sources you want (NewsAPI, Finnhub, etc.)
3. Click "🔄 Refresh from X Source(s)"

### 3. Usage Tips

**For Demo/Research:**

- Start with 3 free sources (ET, Zerodha, Marketaux)
- Add one API source at a time
- Monitor API rate limits

**For Production:**

- Get all API keys
- Set up automated fetching (cron/scheduler)
- Implement caching to reduce API calls

## 📊 Database Schema

```sql
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT UNIQUE NOT NULL,  -- Deduplication key
    published_at DATETIME,
    source TEXT NOT NULL,
    content TEXT,
    sentiment TEXT,  -- 'positive', 'neutral', 'negative'
    sentiment_score INTEGER,  -- -1, 0, 1
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_url ON news_articles(url);
CREATE INDEX idx_source ON news_articles(source);
CREATE INDEX idx_published ON news_articles(published_at);
```

## 🧪 Testing

### Manual Test

1. Open FinBuddy: http://localhost:8501
2. Go to "📰 Market News"
3. Select sources
4. Click "🔄 Refresh"
5. Check logs for fetch results

### API Test

```bash
# Fetch from specific sources
curl -X POST http://localhost:8000/api/news/fetch \
  -H "Content-Type: application/json" \
  -d '["economic_times", "marketaux"]'

# Get latest articles
curl http://localhost:8000/api/news/latest?limit=10&sentiment=positive

# Get source stats
curl http://localhost:8000/api/news/sources
```

## 🐛 Troubleshooting

### No Articles Fetched

1. Check backend logs for errors
2. Verify RSS feed URLs are accessible
3. For API sources, check if keys are set: `echo $NEWSAPI_KEY`
4. Check API rate limits haven't been exceeded

### API Key Not Working

1. Verify key is correct (no extra spaces)
2. Restart backend after setting env vars
3. Check API provider dashboard for issues
4. Try the source's test endpoint first

### Duplicate Articles

- System automatically prevents duplicates via URL
- If seeing duplicates, check if URLs are different
- May happen if source changes URL format

## 📈 Future Enhancements

- [ ] Scheduled auto-fetching (every 10 minutes)
- [ ] Push notifications for important news
- [ ] Advanced NLP sentiment (beyond VADER)
- [ ] Topic categorization (stocks, crypto, economy)
- [ ] Search within articles
- [ ] Export to PDF/Excel
- [ ] User bookmarks/favorites
- [ ] Email digest

## 📝 API Rate Limits Summary

| Source         | Free Limit | Requires Key |
| -------------- | ---------- | ------------ |
| Economic Times | Unlimited  | No           |
| Zerodha Pulse  | Unlimited  | No           |
| Marketaux      | 100/day    | No           |
| NewsAPI        | 100/day    | Yes          |
| Alpha Vantage  | 25/day     | Yes          |
| Finnhub        | 60/min     | Yes          |
| GNews          | 100/day    | Yes          |

**Total Capacity (Free Tier):** ~400+ articles/day across all sources

## 🙏 Credits

- **VADER Sentiment**: vaderSentiment library
- **RSS Parsing**: feedparser
- **HTTP Client**: httpx (async)
- **News Providers**: Economic Times, Zerodha, NewsAPI, Alpha Vantage, Finnhub, Marketaux, GNews

---

**For Research Paper:**

- 7 diverse news sources
- AI-powered sentiment analysis
- Real-time financial news aggregation
- Deduplication & filtering capabilities
- Free tier deployment ready
