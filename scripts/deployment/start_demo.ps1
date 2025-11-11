# FinBuddy Demo Launcher
# This script starts both backend and frontend for demo

Write-Host "🚀 Starting FinBuddy Demo..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Start backend in background
Write-Host "🔧 Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python run.py"

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend
Write-Host "🎨 Starting Frontend (Port 8501)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "✅ Frontend: http://localhost:8501" -ForegroundColor Green
Write-Host "✅ API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

streamlit run app.py
