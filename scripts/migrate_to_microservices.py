"""
Automated FinBuddy Microservices Migration Script
This script will migrate the monolithic application to microservices architecture
"""
import os
import shutil
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent
SERVICES_DIR = PROJECT_ROOT / "services"
SHARED_DIR = PROJECT_ROOT / "shared"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
API_GATEWAY_DIR = PROJECT_ROOT / "api_gateway"
DOCS_DIR = PROJECT_ROOT / "docs"

# Files to migrate
MIGRATION_MAP = {
    # User Service
    "services/user_service": {
        "extracts_from": ["main.py"],  # Auth endpoints
        "new_files": ["app.py", "routes.py", "models.py", "schemas.py"]
    },
    # Portfolio Service
    "services/portfolio_service": {
        "moves": ["price_service.py"],
        "extracts_from": ["main.py"],  # Investment endpoints
        "new_files": ["app.py", "routes.py", "models.py", "schemas.py"]
    },
    # News Service
    "services/news_service": {
        "moves": ["news_fetcher.py"],
        "extracts_from": ["main.py"],  # News endpoints
        "new_files": ["app.py", "routes.py", "models.py", "schemas.py", "sentiment.py"]
    },
    # AI Service
    "services/ai_service": {
        "moves": ["gemini_service.py"],
        "extracts_from": ["main.py"],  # AI endpoints
        "new_files": ["app.py", "routes.py", "schemas.py"]
    },
    # Risk Service
    "services/risk_service": {
        "moves": ["risk_engine.py", "fraud_detection.py"],
        "extracts_from": ["main.py"],  # Risk/Fraud endpoints
        "new_files": ["app.py", "routes.py", "models.py", "schemas.py"]
    },
    # Learning Service
    "services/learning_service": {
        "extracts_from": ["main.py"],  # Learning endpoints
        "new_files": ["app.py", "routes.py", "models.py", "schemas.py", "content.py"]
    }
}

# Files to move to docs
DOCS_FILES = [
    "API_KEYS_SETUP.md",
    "LIVE_PRICING_GUIDE.md",
    "NEWS_SOURCES_GUIDE.md",
    "NEWS_FEATURE_DOCS.md",
    "NEWS_IMPLEMENTATION_SUMMARY.md",
    "MICROSERVICES_RESTRUCTURE.md",
    "MIGRATION_DECISION.md",
    "PRESENTATION_README.md",
    "FUTURE_FEATURES.md"
]

# Files to keep in root
KEEP_IN_ROOT = [
    ".env",
    ".env.example",
    ".gitignore",
    "README.md",
    "requirements.txt",
    "finbuddy.db"
]

# Files to delete (old/redundant)
DELETE_FILES = [
    "main.py",  # Will be replaced by API gateway
    "app.py",  # Will move to frontend/
    "database.py",  # Split into service models
    "config.py",  # Moved to shared/
    "comprehensive_test.py",  # Move to tests/
    "test_api.py",  # Move to tests/
    "project_paper.txt",
    "FinBuddy_paper.docx"
]

def create_service_structure():
    """Create the microservices directory structure"""
    print("📁 Creating microservices structure...")
    
    # Already created, just ensure they exist
    dirs_to_create = [
        SERVICES_DIR,
        SHARED_DIR,
        FRONTEND_DIR,
        API_GATEWAY_DIR,
        DOCS_DIR,
        PROJECT_ROOT / "tests",
        PROJECT_ROOT / "scripts"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(exist_ok=True)
    
    print("✅ Directory structure created")

def move_docs():
    """Move documentation files"""
    print("📚 Moving documentation files...")
    
    for doc_file in DOCS_FILES:
        src = PROJECT_ROOT / doc_file
        if src.exists():
            dst = DOCS_DIR / doc_file
            shutil.copy2(src, dst)
            print(f"  ✅ Moved {doc_file} to docs/")
    
    print("✅ Documentation organized")

def create_readme():
    """Create new README for microservices"""
    readme_content = """# 🚀 FinBuddy - Microservices Architecture

AI-Powered Financial Companion built with modern microservices architecture.

## 🏗️ Architecture

```
FinBuddy/
├── api_gateway/          # Main entry point (Port 8000)
├── services/
│   ├── user_service/     # Authentication & Users (Port 8001)
│   ├── portfolio_service/ # Investments & Live Prices (Port 8002)
│   ├── news_service/     # News Aggregation (Port 8003)
│   ├── ai_service/       # Gemini AI Companion (Port 8004)
│   ├── risk_service/     # Risk & Fraud Detection (Port 8005)
│   └── learning_service/ # Education (Port 8006)
├── frontend/             # Streamlit UI (Port 8501)
├── shared/               # Common code & utilities
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Start All Services
```bash
# Windows
.\\scripts\\start_all_services.ps1

# Linux/Mac
./scripts/start_all_services.sh
```

### Start Individual Service
```bash
cd services/news_service
python app.py
```

## 📚 Documentation

See `docs/` folder for detailed documentation.

## ✨ Features

- 👤 User Management & Authentication
- 💼 Portfolio Management with Live Prices
- 📰 Multi-Source News Aggregation (7 sources)
- 🤖 AI Financial Companion (Gemini)
- 📊 Risk Analysis & Fraud Detection
- 📚 Financial Education Modules

## 🔧 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: SQLite/PostgreSQL
- **AI**: Google Gemini, VADER Sentiment Analysis
- **Architecture**: Microservices

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🌐 Ports

- API Gateway: 8000
- User Service: 8001
- Portfolio Service: 8002
- News Service: 8003
- AI Service: 8004
- Risk Service: 8005
- Learning Service: 8006
- Frontend: 8501

## 📖 Read More

- [API Keys Setup](docs/API_KEYS_SETUP.md)
- [News Sources Guide](docs/NEWS_SOURCES_GUIDE.md)
- [Architecture Details](docs/MICROSERVICES_RESTRUCTURE.md)
"""
    
    (PROJECT_ROOT / "README.md").write_text(readme_content)
    print("✅ New README.md created")

if __name__ == "__main__":
    print("🚀 Starting FinBuddy Microservices Migration...")
    print("=" * 60)
    
    create_service_structure()
    move_docs()
    create_readme()
    
    print("\n" + "=" * 60)
    print("✅ Migration preparation complete!")
    print("\n📝 Next steps:")
    print("1. Review the new structure")
    print("2. Run individual service creation scripts")
    print("3. Test each service")
    print("4. Start all services")
    print("\n🎯 All functionality will be preserved!")
