# 📋 FinBuddy Configuration Guide

## Overview

FinBuddy uses environment variables for configuration. All settings are stored in the `.env` file.

---

## Quick Setup

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit Required Settings

Open `.env` and set at minimum:

- `GEMINI_API_KEY` - Required for AI features

### 3. Optional: Add News API Keys

Add API keys for additional news sources (not required)

---

## Configuration Sections

### 🔧 Application Settings

```env
APP_NAME=FinBuddy
APP_VERSION=2.0.0
ENVIRONMENT=development
```

- **APP_NAME**: Application name
- **APP_VERSION**: Current version
- **ENVIRONMENT**: `development`, `staging`, or `production`

---

### 💾 Database Configuration

```env
DATABASE_URL=sqlite+aiosqlite:///./finbuddy.db
```

**Development (Default):**

- Uses SQLite with async support
- Database file: `finbuddy.db` in project root

**Production:**

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/finbuddy
```

---

### 🔐 Security Settings

```env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4
```

**Important:**

- Change `SECRET_KEY` in production!
- Use strong random key (generate with: `openssl rand -hex 32`)
- Risk thresholds: 0.0-1.0 (0=low risk, 1=high risk)

---

### 🌐 Microservices Ports

```env
GATEWAY_PORT=8000
USER_SERVICE_PORT=8001
PORTFOLIO_SERVICE_PORT=8002
NEWS_SERVICE_PORT=8003
AI_SERVICE_PORT=8004
RISK_SERVICE_PORT=8005
LEARNING_SERVICE_PORT=8006
```

**Default Setup:**

- API Gateway: Port 8000 (main entry)
- Services: Ports 8001-8006

**Change if needed:**

- Ensure ports are not in use
- Update URLs accordingly

---

### 🤖 AI Service - Google Gemini (REQUIRED)

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

**How to Get API Key:**

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env`

**Status:** ✅ **REQUIRED** for AI features

**Features Enabled:**

- AI chat companion
- Financial term explanations
- Text simplification
- Learning content generation
- Scam detection

---

### 📰 News Sources API Keys (OPTIONAL)

#### NewsAPI

```env
NEWSAPI_KEY=your_key_here
```

- **Free Tier**: 100 requests/day
- **Get Key**: https://newsapi.org/register
- **Coverage**: Global news

#### Alpha Vantage

```env
ALPHA_VANTAGE_KEY=your_key_here
```

- **Free Tier**: 25 requests/day
- **Get Key**: https://www.alphavantage.co/support/#api-key
- **Coverage**: Financial news & data

#### Finnhub

```env
FINNHUB_KEY=your_key_here
```

- **Free Tier**: 60 requests/minute
- **Get Key**: https://finnhub.io/register
- **Coverage**: Stock market news

#### GNews

```env
GNEWS_KEY=your_key_here
```

- **Free Tier**: 100 requests/day
- **Get Key**: https://gnews.io/register
- **Coverage**: Business news

**Note:**

- ✅ **3 sources work WITHOUT API keys:**
  - Economic Times (RSS)
  - Zerodha Pulse (RSS)
  - Marketaux (No key required)
- News service works with or without keys!

---

### 💰 Price Service

```env
# No configuration needed!
```

**Price Sources:**

- **yfinance** - Stock prices (no API key)
- **CoinGecko** - Crypto prices (no API key)

**Optional:**

```env
COINGECKO_API_KEY=your_key_here
```

Only needed for higher rate limits

---

### 🗄️ Cache Configuration (OPTIONAL)

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_TTL=3600
```

**When to Use:**

- Production deployments
- High traffic
- Need faster response times

**Setup Redis:**

```bash
# Windows
# Download from: https://redis.io/download

# Linux
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

---

### 🔍 Logging Configuration

```env
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Log Levels:**

- `DEBUG` - Detailed debugging
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only
- `CRITICAL` - Critical errors only

---

### 🌍 CORS Settings

```env
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

**Production:**

```env
CORS_ORIGINS=["https://yourapp.com", "https://www.yourapp.com"]
```

---

### ⚡ Rate Limiting (OPTIONAL)

```env
RATE_LIMIT_ENABLED=false
RATE_LIMIT_PER_MINUTE=60
```

**Enable for production:**

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
```

---

### 📊 Monitoring & Notifications

```env
ENABLE_NOTIFICATIONS=true
ENABLE_METRICS=false
ENABLE_TRACING=false
```

**Options:**

- `ENABLE_NOTIFICATIONS` - Risk/fraud alerts
- `ENABLE_METRICS` - Performance metrics
- `ENABLE_TRACING` - Request tracing

---

### 🎨 Frontend Configuration

```env
FRONTEND_URL=http://localhost:8501
STREAMLIT_SERVER_PORT=8501
```

**Default:** Streamlit on port 8501

---

## Environment Templates

### Development (Default)

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=false
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=true
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql+asyncpg://...
CORS_ORIGINS=["https://yourdomain.com"]
```

### Testing

```env
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite+aiosqlite:///./test_finbuddy.db
```

---

## Validation

### Check Configuration

```python
from shared.config import settings

# Check critical settings
print(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Database: {settings.DATABASE_URL}")
print(f"Gemini API: {'✅ Set' if settings.GEMINI_API_KEY else '❌ Not set'}")
print(f"Services: {settings.get_all_service_urls()}")
```

### Test Services Health

```bash
python test_services.py
```

---

## Troubleshooting

### API Keys Not Working

1. Check `.env` file exists
2. Verify no spaces around `=`
3. No quotes around values needed
4. Restart services after changes

### Services Not Starting

1. Check ports not in use:
   ```powershell
   netstat -ano | findstr "8000"
   ```
2. Check `.env` file loaded:
   ```python
   from shared.config import settings
   print(settings.GEMINI_API_KEY)
   ```

### Database Errors

1. Check `DATABASE_URL` format
2. Ensure write permissions
3. Delete `finbuddy.db` to reset

---

## Security Best Practices

### ✅ DO:

- Change `SECRET_KEY` in production
- Use environment-specific `.env` files
- Add `.env` to `.gitignore`
- Use strong passwords for databases
- Enable HTTPS in production
- Restrict CORS origins in production

### ❌ DON'T:

- Commit `.env` to version control
- Share API keys publicly
- Use default `SECRET_KEY` in production
- Allow `CORS_ORIGINS=["*"]` in production
- Store credentials in code

---

## Example Complete Configuration

### Minimal (Development)

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=sqlite+aiosqlite:///./finbuddy.db
SECRET_KEY=dev-secret-key-change-in-prod
```

### Full (Production)

```env
# Application
ENVIRONMENT=production
APP_VERSION=2.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db.example.com:5432/finbuddy

# Security
SECRET_KEY=<64-char-random-hex>
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4

# Services
GATEWAY_PORT=8000
USER_SERVICE_URL=https://user.finbuddy.com
PORTFOLIO_SERVICE_URL=https://portfolio.finbuddy.com
# ... other service URLs

# AI
GEMINI_API_KEY=your_production_key
GEMINI_MODEL=gemini-2.0-flash-exp

# News (all optional)
NEWSAPI_KEY=your_key
ALPHA_VANTAGE_KEY=your_key
FINNHUB_KEY=your_key
GNEWS_KEY=your_key

# Cache
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_password

# Security
CORS_ORIGINS=["https://finbuddy.com"]
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=WARNING
```

---

## Summary

### Required

- ✅ `GEMINI_API_KEY` - AI features

### Recommended

- `SECRET_KEY` - Change default
- `DATABASE_URL` - PostgreSQL for production

### Optional

- News API keys (3/7 sources work without)
- Redis cache
- Rate limiting
- Monitoring tools

---

**For more help, see:**

- `docs/API_KEYS_SETUP.md`
- `FINAL_SUCCESS.md`
- `README_MICROSERVICES.md`
