# Start All FinBuddy Microservices
# This script starts the API Gateway and all microservices

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  FinBuddy Microservices - Starting All Services" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ROOT = "D:\super_projects\project_1"
$VENV_ACTIVATE = "$PROJECT_ROOT\venv\Scripts\Activate.ps1"

# Start services in separate PowerShell windows
$services = @(
  @{Name = "User Service"; Port = 8001; Module = "services.user_service.app:app" },
  @{Name = "Portfolio Service"; Port = 8002; Module = "services.portfolio_service.app:app" },
  @{Name = "News Service"; Port = 8003; Module = "services.news_service.app:app" },
  @{Name = "AI Service"; Port = 8004; Module = "services.ai_service.app:app" },
  @{Name = "Risk Service"; Port = 8005; Module = "services.risk_service.app:app" },
  @{Name = "Learning Service"; Port = 8006; Module = "services.learning_service.app:app" }
)

Write-Host "Starting Microservices..." -ForegroundColor Yellow
Write-Host ""

foreach ($service in $services) {
  Write-Host "  Starting $($service.Name) on port $($service.Port)..." -ForegroundColor Green

  $cmd = "cd '$PROJECT_ROOT'; "
  $cmd += "& '$VENV_ACTIVATE'; "
  $cmd += "`$env:PYTHONPATH='$PROJECT_ROOT\src'; "
  $cmd += "uvicorn $($service.Module) --host 0.0.0.0 --port $($service.Port) --reload"

  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    $cmd
  )

  Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Starting API Gateway on port 8000..." -ForegroundColor Green

$gatewayCmd = "cd '$PROJECT_ROOT'; "
$gatewayCmd += "& '$VENV_ACTIVATE'; "
$gatewayCmd += "`$env:PYTHONPATH='$PROJECT_ROOT\src'; "
$gatewayCmd += "uvicorn api_gateway.gateway:app --host 0.0.0.0 --port 8000 --reload"

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  $gatewayCmd
)

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  All Services Started Successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Running:" -ForegroundColor Yellow
Write-Host "  - API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host "  - User Service: http://localhost:8001" -ForegroundColor White
Write-Host "  - Portfolio Service: http://localhost:8002" -ForegroundColor White
Write-Host "  - News Service: http://localhost:8003" -ForegroundColor White
Write-Host "  - AI Service: http://localhost:8004" -ForegroundColor White
Write-Host "  - Risk Service: http://localhost:8005" -ForegroundColor White
Write-Host "  - Learning Service: http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "API Gateway Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
