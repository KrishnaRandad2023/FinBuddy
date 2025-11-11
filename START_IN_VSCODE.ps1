# ============================================================================
# FinBuddy - Start All Services (VSCode Integrated Terminals)
# This script starts services in VSCode terminal tabs instead of new windows
# ============================================================================

$PROJECT_ROOT = "D:\super_projects\project_1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🚀 Starting FinBuddy Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Instructions:" -ForegroundColor Yellow
Write-Host "   1. Open 8 terminal tabs in VSCode" -ForegroundColor White
Write-Host "   2. Run each command below in a separate tab" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Copy these commands to terminal tabs:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "# Tab 1 - API Gateway (Port 8000)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn api_gateway.gateway:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 2 - User Service (Port 8001)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.user_service.app:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 3 - Portfolio Service (Port 8002)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.portfolio_service.app:app --host 0.0.0.0 --port 8002 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 4 - News Service (Port 8003)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.news_service.app:app --host 0.0.0.0 --port 8003 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 5 - AI Service (Port 8004)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.ai_service.app:app --host 0.0.0.0 --port 8004 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 6 - Risk Service (Port 8005)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.risk_service.app:app --host 0.0.0.0 --port 8005 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 7 - Learning Service (Port 8006)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; uvicorn services.learning_service.app:app --host 0.0.0.0 --port 8006 --reload" -ForegroundColor White
Write-Host ""

Write-Host "# Tab 8 - Frontend (Port 8501)" -ForegroundColor Green
Write-Host "cd D:\super_projects\project_1; .\venv\Scripts\Activate.ps1; `$env:PYTHONPATH='D:\super_projects\project_1\src'; streamlit run src\frontend\app.py" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  📍 Access Points:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  • Frontend:        http://localhost:8501" -ForegroundColor White
Write-Host "  • API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
