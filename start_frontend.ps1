# FinBuddy - Start Frontend
# Quick script to start the Streamlit frontend

Write-Host ""
Write-Host "🎨 Starting FinBuddy Frontend..." -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "src\frontend\app.py")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not detected. Activating..." -ForegroundColor Yellow
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
        Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Launching Streamlit..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Frontend URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📍 API Gateway: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
streamlit run src\frontend\app.py
