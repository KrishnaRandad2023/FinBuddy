# ============================================================================
# FinBuddy - Simple Server Startup
# Starts the backend API server on port 8000
# ============================================================================

Write-Host "🚀 Starting FinBuddy Backend Server..." -ForegroundColor Cyan

$PROJECT_ROOT = $PSScriptRoot
Set-Location $PROJECT_ROOT

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Virtual environment not found! Run: python -m venv venv" -ForegroundColor Red
    exit 1
}

# Set Python path and start server
$env:PYTHONPATH = "$PROJECT_ROOT\src"
Write-Host "✅ Starting server on http://localhost:8000" -ForegroundColor Green
uvicorn all_in_one_server:app --host 0.0.0.0 --port 8000 --reload
