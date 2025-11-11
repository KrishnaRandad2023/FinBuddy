# FinBuddy - AI-Powered Financial Companion 🤖💰

**FinBuddy** is an intelligent financial companion designed for first-time and micro-investors. It uses Google's Gemini AI to provide real-time investment monitoring, risk prediction, fraud detection, and personalized financial education.

## 🌟 Features

### Core Capabilities

- **🤖 AI-Powered Financial Advisor**: Chat with Gemini AI for personalized investment advice
- **📊 Risk Prediction Engine**: Real-time risk analysis using machine learning models
- **🛡️ Fraud Detection**: Automatic scam and phishing detection
- **📚 Financial Literacy**: Interactive learning modules and gamified education
- **🔔 Smart Notifications**: Personalized alerts based on risk tolerance
- **📈 Portfolio Monitoring**: Track investments across stocks, crypto, and mutual funds

### Key Modules

1. **LLM-Based Financial Companion** - Explains complex jargon in simple terms
2. **AI/ML Risk Prediction Engine** - Predicts investment risks before they occur
3. **Fraud & Scam Detection** - Protects users from financial fraud
4. **User Education Module** - Gamified learning for financial literacy
5. **Real-time Monitoring** - Continuous portfolio health checks

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or navigate to the project directory**

```powershell
cd d:\super_projects\project_1
```

2. **Create a virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Configure environment variables**

```powershell
# Copy the example file
copy .env.example .env

# Edit .env and add your Gemini API key
notepad .env
```

Add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

5. **Run the application**

```powershell
python main.py
```

The server will start at `http://localhost:8000`

### Testing the API

Open another terminal and run:

```powershell
cd d:\super_projects\project_1
.\venv\Scripts\Activate.ps1
python test_api.py
```

## 📖 API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

#### User Management

- `POST /api/users/register` - Register new user
- `GET /api/users/{user_id}` - Get user profile

#### Investment Management

- `POST /api/investments` - Add investment
- `GET /api/investments/{user_id}` - Get user's investments
- `GET /api/investments/{investment_id}/risk-analysis` - Analyze investment risk

#### AI Companion

- `POST /api/ai/chat` - Chat with FinBuddy AI
- `POST /api/ai/explain-term` - Explain financial terms
- `POST /api/ai/translate` - Simplify technical text

#### Security & Fraud Detection

- `POST /api/security/check-scam` - Check message for scams
- `POST /api/security/check-url` - Verify URL safety
- `GET /api/security/alerts/{user_id}` - Get fraud alerts

#### Learning & Education

- `GET /api/learning/module/{topic}` - Get learning content
- `GET /api/learning/progress/{user_id}` - Track learning progress

#### Dashboard

- `GET /api/dashboard/{user_id}` - Get comprehensive dashboard

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FinBuddy System                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FastAPI    │  │   Gemini AI  │  │  Risk Engine │     │
│  │   Backend    │◄─┤   Service    │◄─┤   (ML/AI)    │     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘     │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Database   │  │    Fraud     │  │  Education   │     │
│  │  (SQLite)    │  │  Detector    │  │   Module     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

| Component    | Technology               |
| ------------ | ------------------------ |
| **Backend**  | FastAPI (Python)         |
| **AI/LLM**   | Google Gemini Pro        |
| **Database** | SQLite (async)           |
| **ML/AI**    | NumPy, Scikit-learn      |
| **NLP**      | HuggingFace Transformers |
| **Security** | JWT, OAuth 2.0           |

## 📊 Example Usage

### Chat with AI

```python
import requests

response = requests.post("http://localhost:8000/api/ai/chat", json={
    "message": "Should I invest in cryptocurrency?",
    "user_id": 1
})

print(response.json()['ai_response'])
```

### Check for Scams

```python
response = requests.post("http://localhost:8000/api/security/check-scam", json={
    "message": "URGENT! Send money now for guaranteed returns!",
    "sender": "unknown@suspicious.com"
})

print(response.json())
```

### Analyze Investment Risk

```python
# First add an investment
response = requests.post("http://localhost:8000/api/investments?user_id=1", json={
    "symbol": "BTC",
    "asset_type": "crypto",
    "quantity": 0.5,
    "purchase_price": 45000.00
})

investment_id = response.json()['investment_id']

# Get risk analysis
response = requests.get(f"http://localhost:8000/api/investments/{investment_id}/risk-analysis")
print(response.json())
```

## 🔒 Security Features

- **Fraud Detection**: NLP-based scam and phishing detection
- **Anomaly Detection**: Identifies unusual transaction patterns
- **URL Safety Checker**: Verifies links before clicking
- **Data Encryption**: Secure data storage and transmission
- **Risk Alerts**: Real-time warnings for high-risk investments

## 📚 Educational Features

- **Gamified Learning**: Interactive tutorials on financial concepts
- **AI-Generated Quizzes**: Personalized based on user behavior
- **Progress Tracking**: Monitor learning journey
- **Simple Explanations**: Complex terms explained in everyday language

## 🎯 Use Cases

1. **First-time Investors**: Learn investing basics in a safe environment
2. **Micro-investors**: Manage small portfolios effectively
3. **Risk-averse Users**: Get early warnings about potential losses
4. **Fraud Prevention**: Protect against scams and phishing
5. **Financial Education**: Build financial literacy through practice

## 🔄 Future Enhancements

- [ ] Mobile app (React Native/Flutter)
- [ ] Voice assistant integration (Alexa/Google Assistant)
- [ ] Real-time market data integration
- [ ] Advanced ML models (LSTM, Transformers)
- [ ] Multi-language support
- [ ] Social features (community learning)
- [ ] Automated trading suggestions

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project is created for educational purposes.

## 🙏 Acknowledgments

- **Google Gemini AI** for powering the intelligent companion
- **FastAPI** for the excellent web framework
- **Open-source community** for amazing tools

## 📞 Support

For questions or issues:

- Check the API documentation at `/docs`
- Review this README
- Test with `test_api.py`

---

**Made with ❤️ for beginner investors worldwide**

🚀 **Start your investment journey with confidence using FinBuddy!**
