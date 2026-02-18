# Start Backend Server (FastAPI)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server (FastAPI)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend"

Write-Host "Backend directory: $backendPath" -ForegroundColor Yellow
Write-Host ""

# Check if directory exists
if (-Not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend directory not found!" -ForegroundColor Red
    Write-Host "Path: $backendPath" -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Set-Location $backendPath

Write-Host "Starting uvicorn server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API docs will be available at: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
