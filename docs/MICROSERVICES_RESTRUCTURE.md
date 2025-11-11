# 🏗️ FinBuddy Microservices Architecture - Restructuring Guide

## 📋 Current vs New Structure

### **Current Structure (Monolithic)**

```
project_1/
├── app.py                    # All frontend code
├── main.py                   # All backend endpoints
├── database.py               # All models
├── gemini_service.py         # AI logic
├── news_fetcher.py           # News logic
├── price_service.py          # Price logic
├── risk_engine.py            # Risk logic
├── fraud_detection.py        # Fraud logic
└── config.py                 # Config
```

### **New Structure (Microservices)**

```
project_1/
├── api_gateway/              # 🚪 API Gateway (Port 8000)
│   ├── __init__.py
│   ├── gateway.py           # Main entry point, routes requests
│   ├── middleware.py        # Auth, CORS, logging
│   └── config.py            # Gateway config
│
├── services/                 # 🔧 Microservices
│   ├── user_service/        # 👤 User & Auth (Port 8001)
│   │   ├── __init__.py
│   │   ├── app.py          # FastAPI app
│   │   ├── routes.py       # Endpoints
│   │   ├── models.py       # User model
│   │   ├── auth.py         # JWT, password hashing
│   │   └── requirements.txt
│   │
│   ├── portfolio_service/   # 💼 Portfolio & Investments (Port 8002)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── models.py       # Investment model
│   │   ├── price_fetcher.py # Live prices (yfinance, coingecko)
│   │   └── requirements.txt
│   │
│   ├── news_service/        # 📰 News Aggregation (Port 8003)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── models.py       # NewsArticle model
│   │   ├── fetchers/
│   │   │   ├── rss_fetcher.py      # ET, Zerodha RSS
│   │   │   ├── newsapi_fetcher.py  # NewsAPI
│   │   │   ├── alphavantage_fetcher.py
│   │   │   ├── finnhub_fetcher.py
│   │   │   ├── marketaux_fetcher.py
│   │   │   └── gnews_fetcher.py
│   │   ├── sentiment.py    # VADER sentiment analysis
│   │   └── requirements.txt
│   │
│   ├── ai_service/          # 🤖 AI Companion (Port 8004)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── gemini_client.py # Gemini AI integration
│   │   ├── prompts.py      # System prompts
│   │   └── requirements.txt
│   │
│   ├── risk_service/        # 📊 Risk & Fraud (Port 8005)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   ├── models.py       # RiskAlert, FraudAlert models
│   │   ├── risk_engine.py  # Risk calculation
│   │   ├── fraud_detector.py # Fraud detection
│   │   └── requirements.txt
│   │
│   └── learning_service/    # 📚 Education (Port 8006)
│       ├── __init__.py
│       ├── app.py
│       ├── routes.py
│       ├── models.py       # LearningProgress model
│       ├── content.py      # Learning modules
│       └── requirements.txt
│
├── shared/                   # 🔄 Shared Code
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py         # Base SQLAlchemy models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py     # DB connection utilities
│   │   ├── auth.py         # Shared auth utilities
│   │   └── logger.py       # Logging utilities
│   └── config.py           # Shared configuration
│
├── frontend/                 # 🎨 Streamlit Frontend
│   ├── __init__.py
│   ├── app.py              # Main Streamlit app
│   ├── pages/
│   │   ├── home.py
│   │   ├── profile.py
│   │   ├── portfolio.py
│   │   ├── add_investment.py
│   │   ├── ai_chat.py
│   │   ├── learning.py
│   │   ├── fraud_detection.py
│   │   ├── risk_analysis.py
│   │   └── market_news.py
│   ├── components/
│   │   ├── sidebar.py
│   │   ├── charts.py
│   │   └── cards.py
│   ├── api_client.py       # HTTP client for services
│   └── requirements.txt
│
├── tests/                    # 🧪 Tests
│   ├── test_user_service.py
│   ├── test_portfolio_service.py
│   ├── test_news_service.py
│   ├── test_ai_service.py
│   ├── test_risk_service.py
│   └── test_learning_service.py
│
├── docs/                     # 📚 Documentation
│   ├── API_KEYS_SETUP.md
│   ├── LIVE_PRICING_GUIDE.md
│   ├── NEWS_SOURCES_GUIDE.md
│   ├── NEWS_IMPLEMENTATION_SUMMARY.md
│   └── MICROSERVICES_ARCHITECTURE.md
│
├── scripts/                  # 🛠️ Utility Scripts
│   ├── setup.ps1
│   ├── start_all_services.ps1
│   ├── stop_all_services.ps1
│   └── migrate_db.py
│
├── .env                      # Environment variables
├── .gitignore
├── docker-compose.yml        # Docker orchestration
├── README.md
└── requirements.txt          # Root dependencies
```

## 🔄 Migration Steps

### **Phase 1: Create Shared Components** ✅

1. **Shared Database Models** (`shared/models/`)

   ```python
   # Move database.py models to individual files
   shared/models/user.py
   shared/models/investment.py
   shared/models/news.py
   shared/models/risk.py
   shared/models/learning.py
   ```

2. **Shared Utilities** (`shared/utils/`)
   ```python
   # Move reusable code
   database.py → shared/utils/database.py
   config.py → shared/config.py
   ```

### **Phase 2: Split Services** 🔧

#### **1. User Service** (Port 8001)

- **Extract from:** `main.py` (auth endpoints)
- **Move to:** `services/user_service/`
- **Endpoints:**
  - POST `/register`
  - POST `/login`
  - GET `/users/me`
  - PUT `/users/me`

#### **2. Portfolio Service** (Port 8002)

- **Extract from:** `main.py` (investment endpoints), `price_service.py`
- **Move to:** `services/portfolio_service/`
- **Endpoints:**
  - GET `/investments`
  - POST `/investments`
  - PUT `/investments/{id}`
  - DELETE `/investments/{id}`
  - GET `/portfolio/value`
  - POST `/prices/live` (yfinance, coingecko)

#### **3. News Service** (Port 8003)

- **Extract from:** `news_fetcher.py`
- **Move to:** `services/news_service/`
- **Endpoints:**
  - POST `/news/fetch`
  - GET `/news/latest`
  - GET `/news/sources`
  - GET `/news/sentiment/{sentiment}`

#### **4. AI Service** (Port 8004)

- **Extract from:** `gemini_service.py`
- **Move to:** `services/ai_service/`
- **Endpoints:**
  - POST `/chat`
  - POST `/analyze/portfolio`
  - POST `/recommend/investments`

#### **5. Risk Service** (Port 8005)

- **Extract from:** `risk_engine.py`, `fraud_detection.py`
- **Move to:** `services/risk_service/`
- **Endpoints:**
  - POST `/risk/analyze`
  - GET `/risk/alerts`
  - POST `/fraud/detect`
  - GET `/fraud/alerts`

#### **6. Learning Service** (Port 8006)

- **Extract from:** `main.py` (learning endpoints)
- **Move to:** `services/learning_service/`
- **Endpoints:**
  - GET `/modules`
  - GET `/modules/{id}`
  - POST `/progress`
  - GET `/progress/{user_id}`

### **Phase 3: Create API Gateway** 🚪

**Gateway Routes** (`api_gateway/gateway.py`)

```python
# Forward requests to services
/api/auth/*        → user_service:8001
/api/users/*       → user_service:8001
/api/investments/* → portfolio_service:8002
/api/portfolio/*   → portfolio_service:8002
/api/prices/*      → portfolio_service:8002
/api/news/*        → news_service:8003
/api/ai/*          → ai_service:8004
/api/risk/*        → risk_service:8005
/api/fraud/*       → risk_service:8005
/api/learning/*    → learning_service:8006
```

### **Phase 4: Refactor Frontend** 🎨

**Frontend Structure** (`frontend/`)

```python
# Split app.py into modular pages
app.py → Main navigation
pages/home.py → Home dashboard
pages/portfolio.py → Portfolio view
pages/market_news.py → News page with 7 sources
```

**API Client** (`frontend/api_client.py`)

```python
class FinBuddyClient:
    def __init__(self, gateway_url="http://localhost:8000"):
        self.gateway_url = gateway_url

    # All API calls go through gateway
    def get_news(self, ...):
        return requests.get(f"{self.gateway_url}/api/news/latest")
```

## 🚀 Running the Microservices

### **Option 1: Manual Start** (Development)

```powershell
# Terminal 1 - User Service
cd services/user_service
uvicorn app:app --port 8001 --reload

# Terminal 2 - Portfolio Service
cd services/portfolio_service
uvicorn app:app --port 8002 --reload

# Terminal 3 - News Service
cd services/news_service
uvicorn app:app --port 8003 --reload

# Terminal 4 - AI Service
cd services/ai_service
uvicorn app:app --port 8004 --reload

# Terminal 5 - Risk Service
cd services/risk_service
uvicorn app:app --port 8005 --reload

# Terminal 6 - Learning Service
cd services/learning_service
uvicorn app:app --port 8006 --reload

# Terminal 7 - API Gateway
cd api_gateway
uvicorn gateway:app --port 8000 --reload

# Terminal 8 - Frontend
cd frontend
streamlit run app.py --server.port 8501
```

### **Option 2: Docker Compose** (Production)

```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose down
```

### **Option 3: PowerShell Script** (Easy)

```powershell
# Start all
./scripts/start_all_services.ps1

# Stop all
./scripts/stop_all_services.ps1
```

## 📊 Service Communication

### **Synchronous (HTTP/REST)**

```
Frontend → API Gateway → Individual Services
```

### **Asynchronous (Future)**

```
Services → Message Queue (RabbitMQ/Redis) → Other Services
```

## 🎯 Benefits of This Architecture

### **1. Scalability** 📈

- Scale services independently
- High-traffic news service? Scale only that!

### **2. Maintainability** 🔧

- Clear separation of concerns
- Easy to find and fix bugs
- Team can work on different services

### **3. Deployment** 🚀

- Deploy services independently
- Update news service without touching portfolio
- Zero-downtime deployments

### **4. Technology Flexibility** 🎨

- Use different tech for different services
- Add Python, Node.js, Go services
- Best tool for each job

### **5. Fault Isolation** 🛡️

- News service down? Rest still works!
- Circuit breakers prevent cascade failures

### **6. Testing** 🧪

- Test services in isolation
- Mock dependencies easily
- Faster test execution

## 🔐 Security Considerations

### **API Gateway** (All requests pass through)

- ✅ JWT validation
- ✅ Rate limiting
- ✅ CORS handling
- ✅ Request logging
- ✅ API key validation

### **Service-to-Service**

- ✅ Internal API keys
- ✅ Service mesh (optional)
- ✅ mTLS (mutual TLS)

## 📦 Docker Configuration

**docker-compose.yml**

```yaml
version: "3.8"

services:
  user-service:
    build: ./services/user_service
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://...

  portfolio-service:
    build: ./services/portfolio_service
    ports:
      - "8002:8002"

  news-service:
    build: ./services/news_service
    ports:
      - "8003:8003"
    environment:
      - NEWSAPI_KEY=${NEWSAPI_KEY}
      - FINNHUB_KEY=${FINNHUB_KEY}

  ai-service:
    build: ./services/ai_service
    ports:
      - "8004:8004"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}

  risk-service:
    build: ./services/risk_service
    ports:
      - "8005:8005"

  learning-service:
    build: ./services/learning_service
    ports:
      - "8006:8006"

  api-gateway:
    build: ./api_gateway
    ports:
      - "8000:8000"
    depends_on:
      - user-service
      - portfolio-service
      - news-service
      - ai-service
      - risk-service
      - learning-service

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_GATEWAY_URL=http://api-gateway:8000
```

## 🎓 Migration Timeline

### **Week 1: Setup** ✅

- [x] Create directory structure
- [ ] Move shared code
- [ ] Setup base service templates

### **Week 2-3: Services**

- [ ] Migrate User Service
- [ ] Migrate Portfolio Service
- [ ] Migrate News Service
- [ ] Migrate AI Service
- [ ] Migrate Risk Service
- [ ] Migrate Learning Service

### **Week 4: Gateway & Frontend**

- [ ] Create API Gateway
- [ ] Refactor Frontend
- [ ] Service discovery

### **Week 5: Testing & Deployment**

- [ ] Integration tests
- [ ] Docker setup
- [ ] CI/CD pipeline
- [ ] Documentation

## 🔄 Backward Compatibility

During migration, we'll maintain:

- ✅ Current monolithic version (production)
- ✅ New microservices version (staging)
- ✅ Dual deployment until stable

## 📚 Next Steps

1. **Review this architecture** - Any changes needed?
2. **Start migration** - Begin with shared components
3. **Service by service** - Migrate one at a time
4. **Test thoroughly** - Ensure functionality matches
5. **Deploy gradually** - Canary deployments

---

**Ready to start migration?** Let me know and I'll begin creating the microservices! 🚀
