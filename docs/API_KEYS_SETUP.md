# News Sources API Keys Setup Guide

## 🔑 Getting API Keys for News Sources

### Free Sources (No API Key Required)

1. **Economic Times RSS** ✅ Works immediately
2. **Zerodha Pulse RSS** ✅ Works immediately
3. **Marketaux** ✅ Works immediately (100 requests/day free)

### Sources Requiring Free API Keys

#### 1. NewsAPI (https://newsapi.org)

- **Free Tier**: 100 requests/day
- **Steps**:
  1. Visit https://newsapi.org/register
  2. Create a free account
  3. Copy your API key
  4. Set environment variable: `NEWSAPI_KEY=your_key_here`

#### 2. Alpha Vantage (https://www.alphavantage.co)

- **Free Tier**: 25 requests/day
- **Steps**:
  1. Visit https://www.alphavantage.co/support/#api-key
  2. Enter your email
  3. Copy your API key
  4. Set environment variable: `ALPHA_VANTAGE_KEY=your_key_here`

#### 3. Finnhub (https://finnhub.io)

- **Free Tier**: 60 API calls/minute
- **Steps**:
  1. Visit https://finnhub.io/register
  2. Create a free account
  3. Copy your API key from dashboard
  4. Set environment variable: `FINNHUB_KEY=your_key_here`

#### 4. GNews (https://gnews.io)

- **Free Tier**: 100 requests/day
- **Steps**:
  1. Visit https://gnews.io/register
  2. Create a free account
  3. Copy your API key
  4. Set environment variable: `GNEWS_KEY=your_key_here`

## 🔧 Setting Environment Variables

### Windows (PowerShell):

```powershell
$env:NEWSAPI_KEY = "your_key_here"
$env:ALPHA_VANTAGE_KEY = "your_key_here"
$env:FINNHUB_KEY = "your_key_here"
$env:GNEWS_KEY = "your_key_here"
```

### Linux/Mac (Terminal):

```bash
export NEWSAPI_KEY="your_key_here"
export ALPHA_VANTAGE_KEY="your_key_here"
export FINNHUB_KEY="your_key_here"
export GNEWS_KEY="your_key_here"
```

### Using .env File (Recommended):

Create a `.env` file in project root:

```env
NEWSAPI_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_av_key
FINNHUB_KEY=your_finnhub_key
GNEWS_KEY=your_gnews_key
```

Then install python-dotenv:

```bash
pip install python-dotenv
```

And load in your code:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 📊 Usage in FinBuddy

1. **Start with free sources**: Economic Times, Zerodha, and Marketaux work immediately
2. **Add API keys gradually**: Get keys only for sources you need
3. **Check limits**: Each API has daily request limits
4. **Select sources**: Use checkboxes in UI to choose which sources to fetch from

## 🚨 Important Notes

- API keys are **optional** - you can use FinBuddy with just the RSS feeds
- Free tiers are sufficient for research/demo purposes
- Never commit API keys to version control
- Add `.env` to `.gitignore`
