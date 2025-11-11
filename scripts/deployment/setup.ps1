# PowerShell Setup Script for FinBuddy

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 FinBuddy - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
  Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
  python -m venv venv
  Write-Host "✅ Virtual environment created" -ForegroundColor Green
}
else {
  Write-Host "✅ Virtual environment found" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check for .env file
if (-not (Test-Path ".env")) {
  Write-Host "⚠️  Creating .env file from template..." -ForegroundColor Yellow
  Copy-Item ".env.example" ".env"
  Write-Host "✅ .env file created" -ForegroundColor Green
  Write-Host ""
  Write-Host "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY" -ForegroundColor Red
  Write-Host "   Get your API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
  Write-Host ""
    
  $response = Read-Host "Do you want to open .env file now? (Y/n)"
  if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    notepad .env
  }
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start FinBuddy, run:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or use the quick start script:" -ForegroundColor Cyan
Write-Host "  python run.py" -ForegroundColor Yellow
Write-Host ""
