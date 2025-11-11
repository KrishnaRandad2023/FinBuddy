# 🚀 FinBuddy - AI-Powered Financial Companion (Microservices)

> **A professional-grade microservices application for beginner investors, featuring live pricing, multi-source news, AI chat, risk analysis, and financial education.**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![Architecture](https://img.shields.io/badge/Architecture-Microservices-orange.svg)]()

---

## ✨ Features

### 📊 Core Features

- **Live Pricing**: Real-time stock (yfinance) & crypto (CoinGecko) prices
- **Multi-Source News**: 7 news sources with VADER sentiment analysis
- **AI Companion**: Google Gemini-powered financial advisor
- **Portfolio Tracking**: Complete investment management with gain/loss calculations
- **Risk Analysis**: Automated portfolio risk scoring
- **Fraud Detection**: AI-powered scam and URL safety checks
- **Financial Education**: AI-generated learning modules with quizzes

### 🏗️ Architecture

- **6 Independent Microservices**: User, Portfolio, News, AI, Risk, Learning
- **API Gateway**: Centralized request routing (Port 8000)
- **Shared Utilities**: Config, database, auth, logging
- **JWT Authentication**: Secure user sessions
- **Async Everything**: FastAPI + SQLAlchemy async for performance

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip
- Windows (PowerShell) / Linux / macOS

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd project_1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Start All Services

```powershell
# Windows (PowerShell)
.\scripts\start_all_services.ps1
```

```bash
# Linux/macOS
python api_gateway/gateway.py &
python services/user_service/app.py &
python services/portfolio_service/app.py &
python services/news_service/app.py &
python services/ai_service/app.py &
python services/risk_service/app.py &
python services/learning_service/app.py &
```

### Test Services

```bash
# Test all services
python test_services.py

# Or check manually
curl http://localhost:8000/health
```

### Start Frontend

```bash
streamlit run app.py
```

---

## 🌐 API Endpoints

### API Gateway (Port 8000)

**Main entry point for all requests**

- `GET /` - Service info
- `GET /health` - Aggregated health check
- `GET /docs` - Interactive API documentation

### User Service (Port 8001)

- `POST /register` - Register new user
- `POST /login` - User login (returns JWT)
- `GET /{user_id}` - Get user profile

### Portfolio Service (Port 8002)

- `POST /{user_id}` - Add investment
- `GET /{user_id}` - Get user portfolio
- `GET /price/{symbol}` - Get live price
- `PUT /update-prices/{user_id}` - Update all prices

### News Service (Port 8003)

- `POST /fetch` - Fetch news from sources
- `GET /latest` - Get latest articles
- `GET /sources` - Get source statistics

### AI Service (Port 8004)

- `POST /chat` - Chat with AI companion
- `POST /explain-term` - Explain financial terms
- `POST /translate` - Simplify technical text
- `GET /learning/{topic}` - Get learning module

### Risk Service (Port 8005)

- `GET /analyze-portfolio/{user_id}` - Analyze portfolio risk
- `POST /detect-scam` - Check for scam messages
- `POST /check-url` - Check URL safety

### Learning Service (Port 8006)

- `GET /module/{topic}` - Get educational module
- `GET /progress/{user_id}` - Get learning progress

---

## 📁 Project Structure

```
project_1/
├── api_gateway/
│   └── gateway.py              # API Gateway (Port 8000)
│
├── services/
│   ├── user_service/           # Port 8001
│   ├── portfolio_service/      # Port 8002
│   ├── news_service/           # Port 8003
│   ├── ai_service/             # Port 8004
│   ├── risk_service/           # Port 8005
│   └── learning_service/       # Port 8006
│
├── shared/
│   ├── config.py               # Centralized configuration
│   ├── models/                 # Database models
│   └── utils/
│       ├── database.py         # Database utilities
│       ├── auth.py             # Authentication utilities
│       └── logger.py           # Logging utilities
│
├── docs/                       # Documentation
├── scripts/                    # Automation scripts
├── frontend/                   # Streamlit frontend
│
├── app.py                      # Main Streamlit app
├── requirements.txt            # Python dependencies
├── test_services.py            # Health check script
└── .env                        # Environment variables
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# API Keys
GEMINI_API_KEY=your_gemini_key_here
NEWSAPI_KEY=your_newsapi_key_here
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
FINNHUB_KEY=your_finnhub_key_here
GNEWS_KEY=your_gnews_key_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./finbuddy.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
USER_SERVICE_URL=http://localhost:8001
PORTFOLIO_SERVICE_URL=http://localhost:8002
NEWS_SERVICE_URL=http://localhost:8003
AI_SERVICE_URL=http://localhost:8004
RISK_SERVICE_URL=http://localhost:8005
LEARNING_SERVICE_URL=http://localhost:8006
```

See `docs/API_KEYS_SETUP.md` for detailed setup instructions.

---

## 🧪 Testing

### Health Checks

```bash
# Test all services
python test_services.py

# Individual service health
curl http://localhost:8001/health  # User
curl http://localhost:8002/health  # Portfolio
curl http://localhost:8003/health  # News
curl http://localhost:8004/health  # AI
curl http://localhost:8005/health  # Risk
curl http://localhost:8006/health  # Learning
```

### Example API Calls

```bash
# Register user
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123",
    "risk_tolerance": "medium"
  }'

# Get live stock price
curl "http://localhost:8000/api/portfolio/price/AAPL?asset_type=stock"

# Get latest news
curl "http://localhost:8000/api/news/latest?limit=10"

# Chat with AI
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is diversification?"}'
```

---

## 📚 Documentation

- **[FINAL_SUCCESS.md](FINAL_SUCCESS.md)** - Complete migration success summary
- **[PHASE2_COMPLETE.md](PHASE2_COMPLETE.md)** - Phase 2 completion details
- **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Full migration guide
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)** - API keys setup
- **[docs/LIVE_PRICING_GUIDE.md](docs/LIVE_PRICING_GUIDE.md)** - Price service guide
- **[docs/NEWS_SOURCES_GUIDE.md](docs/NEWS_SOURCES_GUIDE.md)** - News sources guide
- **[docs/MICROSERVICES_RESTRUCTURE.md](docs/MICROSERVICES_RESTRUCTURE.md)** - Architecture details

---

## 🛠️ Technology Stack

### Backend

- **FastAPI 0.104**: Async web framework
- **SQLAlchemy 2.0**: Async ORM
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **httpx**: Async HTTP client

### Authentication & Security

- **JWT**: JSON Web Tokens
- **bcrypt**: Password hashing
- **python-jose**: JWT implementation

### AI & Data

- **Google Gemini 2.5-flash**: AI companion
- **VADER**: Sentiment analysis
- **yfinance**: Stock prices
- **pycoingecko**: Crypto prices

### News Sources

- Economic Times (RSS)
- Zerodha Pulse (RSS)
- NewsAPI
- Alpha Vantage
- Finnhub
- Marketaux
- GNews

### Frontend

- **Streamlit 1.28**: Web UI
- **Plotly**: Interactive charts
- **Pandas**: Data manipulation

### Database

- **SQLite**: Development database
- **aiosqlite**: Async SQLite driver

---

## 🏗️ Architecture

### Microservices Pattern

```
Frontend (Streamlit - Port 8501)
          ↓
API Gateway (Port 8000)
          ↓
    ┌─────┴──────┬──────┬──────┬──────┬──────┐
    ↓            ↓      ↓      ↓      ↓      ↓
  User      Portfolio  News   AI    Risk  Learning
 (8001)      (8002)   (8003) (8004) (8005)  (8006)
    ↓            ↓      ↓      ↓      ↓      ↓
          Shared Database (SQLite)
```

### Benefits

- ✅ **Independent Scaling**: Scale services individually
- ✅ **Fault Isolation**: Service failures don't crash the system
- ✅ **Technology Freedom**: Different tech stacks per service
- ✅ **Easy Deployment**: Deploy services independently
- ✅ **Clear Boundaries**: Separation of concerns
- ✅ **Team Scaling**: Different teams can own services

---

## 🚢 Deployment

### Docker (Coming Soon)

```bash
# Build images
docker-compose build

# Start all services
docker-compose up
```

### Cloud Deployment

- **Azure**: Container Apps / AKS
- **AWS**: ECS / EKS
- **Google Cloud**: Cloud Run / GKE
- **Heroku**: Container deployment

---

## 📈 Performance

### Current Capabilities

- Async I/O for all operations
- Connection pooling
- In-memory caching
- Efficient database queries
- Batch price updates

### Scalability

- Each service scales independently
- Load balancer ready
- Database migration to PostgreSQL easy
- Redis caching can be added
- Message queue integration possible

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **FastAPI** - Amazing async web framework
- **Google Gemini** - Powerful AI capabilities
- **Streamlit** - Beautiful web UI
- **yfinance & CoinGecko** - Free price data
- **News APIs** - Multi-source news data
- **VADER** - Sentiment analysis

---

## 📞 Support & Contact

- **Documentation**: See `docs/` folder
- **Issues**: Create a GitHub issue
- **Questions**: Check documentation first

---

## 🎯 Future Enhancements

- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] WebSocket support for real-time updates
- [ ] Mobile app (React Native)
- [ ] Advanced portfolio analytics
- [ ] Machine learning predictions
- [ ] Social trading features
- [ ] Multi-currency support

---

## 📊 Stats

- **Lines of Code**: ~3000+
- **Services**: 6 microservices + API Gateway
- **Endpoints**: 20+ REST endpoints
- **News Sources**: 7 sources
- **Database Models**: 6 models
- **Frontend Pages**: 9 pages
- **API Keys Supported**: 5+

---

## 🎉 Status

**✅ PRODUCTION READY**

- ✅ All features implemented
- ✅ All services functional
- ✅ Complete documentation
- ✅ Health checks working
- ✅ Error handling in place
- ✅ Logging configured
- ✅ Authentication secure
- ✅ API documentation complete

---

## 🚀 Get Started Now!

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
# Edit .env file

# 3. Start services
.\scripts\start_all_services.ps1

# 4. Test services
python test_services.py

# 5. Start frontend
streamlit run app.py

# 6. Visit
# http://localhost:8501 (Frontend)
# http://localhost:8000/docs (API Docs)
```

---

**Built with ❤️ for beginner investors**

**🌟 Star this repo if you find it helpful!**
