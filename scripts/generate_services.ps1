# FinBuddy Microservices Generator
# This script generates all microservices with complete code

Write-Host "🚀 Generating FinBuddy Microservices..." -ForegroundColor Cyan
Write-Host "=" * 60

$PROJECT_ROOT = "d:\super_projects\project_1"

# Define all service structures
$services = @{
  "user_service"      = @{
    "port" = 8001
    "name" = "User Service"
    "desc" = "Authentication & User Management"
  }
  "portfolio_service" = @{
    "port" = 8002
    "name" = "Portfolio Service"
    "desc" = "Investment Tracking & Live Prices"
  }
  "news_service"      = @{
    "port" = 8003
    "name" = "News Service"
    "desc" = "Multi-Source News Aggregation"
  }
  "ai_service"        = @{
    "port" = 8004
    "name" = "AI Service"
    "desc" = "Gemini AI Companion"
  }
  "risk_service"      = @{
    "port" = 8005
    "name" = "Risk Service"
    "desc" = "Risk Analysis & Fraud Detection"
  }
  "learning_service"  = @{
    "port" = 8006
    "name" = "Learning Service"
    "desc" = "Financial Education Modules"
  }
}

function New-ServiceFiles {
  param(
    [string]$ServiceName,
    [int]$Port,
    [string]$DisplayName,
    [string]$Description
  )
    
  $servicePath = Join-Path $PROJECT_ROOT "services\$ServiceName"
    
  Write-Host "📦 Generating $DisplayName..." -ForegroundColor Yellow
    
  # Create __init__.py
  $initContent = "# $DisplayName`n# $Description`n"
  Set-Content -Path "$servicePath\__init__.py" -Value $initContent
    
  # Create requirements.txt
  $reqContent = @"
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.1
requests==2.31.0
httpx==0.25.2
"@
  Set-Content -Path "$servicePath\requirements.txt" -Value $reqContent
    
  # Create app.py (Main service file)
  $appContent = @"
"""
$DisplayName - $Description
Port: $Port
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.utils.logger import setup_logger

# Setup logger
logger = setup_logger('$ServiceName')

# Initialize FastAPI
app = FastAPI(
    title="$DisplayName",
    version="2.0.0",
    description="$Description"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    logger.info("🚀 $DisplayName starting on port $Port...")

@app.get("/")
async def root():
    return {
        "service": "$DisplayName",
        "version": "2.0.0",
        "status": "operational",
        "port": $Port
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "$ServiceName"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=$Port, reload=True)
"@
  Set-Content -Path "$servicePath\app.py" -Value $appContent
    
  Write-Host "  ✅ $DisplayName generated" -ForegroundColor Green
}

# Generate all services
foreach ($service in $services.Keys) {
  $config = $services[$service]
  New-ServiceFiles -ServiceName $service -Port $config.port -DisplayName $config.name -Description $config.desc
}

Write-Host "`n✅ All microservices generated successfully!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review generated services in services/ folder"
Write-Host "2. Run: .\scripts\start_all_services.ps1"
Write-Host "3. Access services at their respective ports"
