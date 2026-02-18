# Simple Database Fix Script
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Must run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Step 1: Starting PostgreSQL..." -ForegroundColor Yellow
try {
    $service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($null -eq $service) {
        Write-Host "  PostgreSQL service not found!" -ForegroundColor Red
    }
    elseif ($service.Status -eq "Running") {
        Write-Host "  PostgreSQL already running" -ForegroundColor Green
    }
    else {
        Start-Service $service.Name
        Start-Sleep -Seconds 3
        Write-Host "  PostgreSQL started" -ForegroundColor Green
    }
}
catch {
    Write-Host "  Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 2: Testing connection..." -ForegroundColor Yellow
python -c "import psycopg2; psycopg2.connect('dbname=futebol_analytics user=postgres password=postgres host=localhost').close(); print('  Database connected')"

Write-Host ""
Write-Host "Step 3: Fixing constraint..." -ForegroundColor Yellow
$env:PGPASSWORD = "postgres"
psql -U postgres -d futebol_analytics -f fix_constraint.sql

Write-Host ""
Write-Host "Step 4: Testing session creation..." -ForegroundColor Yellow
python test_session_creation.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
