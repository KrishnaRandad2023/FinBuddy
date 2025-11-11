# ============================================================================
# FinBuddy - Complete Startup Script
# Starts ALL backend services + frontend in one command
# ============================================================================

$PROJECT_ROOT = "D:\super_projects\project_1"
$VENV_ACTIVATE = "$PROJECT_ROOT\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 FinBuddy Complete Startup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path $VENV_ACTIVATE)) {
    Write-Host "❌ ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Expected at: $VENV_ACTIVATE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Please create venv first:" -ForegroundColor Yellow
    Write-Host "   python -m venv venv" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "   pip install -r config\requirements.txt" -ForegroundColor White
    exit 1
}

# Check if .env exists
if (-not (Test-Path "$PROJECT_ROOT\config\.env")) {
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "   Expected at: $PROJECT_ROOT\config\.env" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment found" -ForegroundColor Green
Write-Host "✅ Configuration file found" -ForegroundColor Green
Write-Host ""

# Services to start
$services = @(
  @{Name = "User Service"; Port = 8001; Module = "services.user_service.app:app" },
  @{Name = "Portfolio Service"; Port = 8002; Module = "services.portfolio_service.app:app" },
  @{Name = "News Service"; Port = 8003; Module = "services.news_service.app:app" },
  @{Name = "AI Service"; Port = 8004; Module = "services.ai_service.app:app" },
  @{Name = "Risk Service"; Port = 8005; Module = "services.risk_service.app:app" },
  @{Name = "Learning Service"; Port = 8006; Module = "services.learning_service.app:app" }
)

Write-Host "Starting Backend Services..." -ForegroundColor Yellow
Write-Host ""

# Start each microservice
foreach ($service in $services) {
  Write-Host "  🔄 Starting $($service.Name) on port $($service.Port)..." -ForegroundColor Cyan

  $cmd = "cd '$PROJECT_ROOT'; "
  $cmd += "& '$VENV_ACTIVATE'; "
  $cmd += "`$env:PYTHONPATH='$PROJECT_ROOT\src'; "
  $cmd += "Write-Host ''; "
  $cmd += "Write-Host '=== $($service.Name) ===' -ForegroundColor Green; "
  $cmd += "Write-Host 'Port: $($service.Port)' -ForegroundColor White; "
  $cmd += "Write-Host ''; "
  $cmd += "uvicorn $($service.Module) --host 0.0.0.0 --port $($service.Port) --reload"

  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    $cmd
  )

  Start-Sleep -Milliseconds 800
}

Write-Host ""
Write-Host "  🔄 Starting API Gateway on port 8000..." -ForegroundColor Cyan

$gatewayCmd = "cd '$PROJECT_ROOT'; "
$gatewayCmd += "& '$VENV_ACTIVATE'; "
$gatewayCmd += "`$env:PYTHONPATH='$PROJECT_ROOT\src'; "
$gatewayCmd += "Write-Host ''; "
$gatewayCmd += "Write-Host '=== API Gateway ===' -ForegroundColor Green; "
$gatewayCmd += "Write-Host 'Port: 8000' -ForegroundColor White; "
$gatewayCmd += "Write-Host ''; "
$gatewayCmd += "uvicorn api_gateway.gateway:app --host 0.0.0.0 --port 8000 --reload"

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  $gatewayCmd
)

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "  🔄 Starting Streamlit Frontend on port 8501..." -ForegroundColor Cyan

$frontendCmd = "cd '$PROJECT_ROOT'; "
$frontendCmd += "& '$VENV_ACTIVATE'; "
$frontendCmd += "`$env:PYTHONPATH='$PROJECT_ROOT\src'; "
$frontendCmd += "Write-Host ''; "
$frontendCmd += "Write-Host '=== Streamlit Frontend ===' -ForegroundColor Green; "
$frontendCmd += "Write-Host 'Port: 8501' -ForegroundColor White; "
$frontendCmd += "Write-Host ''; "
$frontendCmd += "streamlit run src\frontend\app.py"

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  $frontendCmd
)

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Services:" -ForegroundColor Yellow
Write-Host "   • API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "   • User Service:    http://localhost:8001" -ForegroundColor White
Write-Host "   • Portfolio:       http://localhost:8002" -ForegroundColor White
Write-Host "   • News Service:    http://localhost:8003" -ForegroundColor White
Write-Host "   • AI Service:      http://localhost:8004" -ForegroundColor White
Write-Host "   • Risk Service:    http://localhost:8005" -ForegroundColor White
Write-Host "   • Learning:        http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Frontend:" -ForegroundColor Yellow
Write-Host "   • Streamlit App:   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Yellow
Write-Host "   • Swagger UI:      http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Check each service window for logs and errors" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (services will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
