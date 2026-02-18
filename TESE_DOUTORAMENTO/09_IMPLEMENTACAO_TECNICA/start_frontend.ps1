# Start Frontend Server (React/Vite)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server (React)" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$frontendPath = "C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend"

Write-Host "Frontend directory: $frontendPath" -ForegroundColor Yellow
Write-Host ""

# Check if directory exists
if (-Not (Test-Path $frontendPath)) {
    Write-Host "ERROR: Frontend directory not found!" -ForegroundColor Red
    Write-Host "Path: $frontendPath" -ForegroundColor Red
    exit 1
}

# Navigate to frontend directory
Set-Location $frontendPath

Write-Host "Starting Vite dev server..." -ForegroundColor Green
Write-Host "Dashboard will be available at: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
npm run dev
