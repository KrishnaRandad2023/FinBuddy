# FinBuddy Quick Launcher
# Run this script to start all services quickly

Write-Host ""
Write-Host "🚀 FinBuddy Quick Launcher" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "src\api_gateway\gateway.py")) {
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
        Write-Host "❌ Virtual environment not found. Please run setup first:" -ForegroundColor Red
        Write-Host "   python -m venv venv" -ForegroundColor Yellow
        Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        Write-Host "   pip install -r config\requirements.txt" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "Starting all services..." -ForegroundColor Green
Write-Host ""

# Start all microservices
& .\scripts\deployment\start_all_services.ps1

Write-Host ""
Write-Host "✅ Services started! Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open a new terminal" -ForegroundColor White
Write-Host "2. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "3. Run: streamlit run src\frontend\app.py" -ForegroundColor Yellow
Write-Host "4. Visit: http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Documentation: docs\README_QUICK_START.md" -ForegroundColor Cyan
Write-Host ""
