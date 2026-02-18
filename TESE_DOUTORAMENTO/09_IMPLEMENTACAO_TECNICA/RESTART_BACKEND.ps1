# Restart Backend with Correct Database Configuration

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Restarting Backend Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Stop any running Python/uvicorn processes
Write-Host "Stopping old backend server..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Navigate to backend directory
$backendPath = "C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend"
Set-Location $backendPath

Write-Host "Backend directory: $backendPath" -ForegroundColor Gray
Write-Host ""

# Show database configuration
Write-Host "Database Configuration (.env):" -ForegroundColor Green
Get-Content "../.env" | Write-Host
Write-Host ""

Write-Host "Starting backend server with new configuration..." -ForegroundColor Green
Write-Host "Server will connect to PostgreSQL on port 5433" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  - API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  - Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
