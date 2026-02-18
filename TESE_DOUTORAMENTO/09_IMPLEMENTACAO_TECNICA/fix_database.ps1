# Fix Database Issues - Run as Administrator
# Right-click this file and select "Run with PowerShell as Administrator"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click the script and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Step 1: Start PostgreSQL
Write-Host "Step 1: Starting PostgreSQL service..." -ForegroundColor Yellow
try {
    $service = Get-Service -Name "postgresql-x64-16" -ErrorAction SilentlyContinue
    
    if ($null -eq $service) {
        Write-Host "  PostgreSQL service not found. Trying alternative names..." -ForegroundColor Yellow
        $service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    
    if ($null -eq $service) {
        Write-Host "  ✗ PostgreSQL service not found!" -ForegroundColor Red
        Write-Host "  Please install PostgreSQL or check service name" -ForegroundColor Yellow
    }
    elseif ($service.Status -eq "Running") {
        Write-Host "  ✓ PostgreSQL is already running" -ForegroundColor Green
    }
    else {
        Start-Service $service.Name
        Start-Sleep -Seconds 3
        Write-Host "  ✓ PostgreSQL started successfully" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ✗ Error starting PostgreSQL: $_" -ForegroundColor Red
}

Write-Host ""

# Step 2: Test database connection
Write-Host "Step 2: Testing database connection..." -ForegroundColor Yellow
try {
    python -c "import psycopg2; conn = psycopg2.connect('dbname=futebol_analytics user=postgres password=postgres host=localhost'); conn.close(); print('  ✓ Database connection successful')"
}
catch {
    Write-Host "  ✗ Cannot connect to database" -ForegroundColor Red
    Write-Host "  Make sure PostgreSQL is installed and credentials are correct" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Fix database constraint
Write-Host "Step 3: Fixing database constraint..." -ForegroundColor Yellow
Write-Host "  Running SQL fix script..." -ForegroundColor Cyan

$sqlScript = @"
-- Fix sessoes_local_check constraint
ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check;
ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check 
CHECK (local IS NULL OR local IN ('Casa', 'Fora', 'Neutro'));

-- Verify constraint
SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
FROM pg_constraint 
WHERE conrelid = 'sessoes'::regclass AND conname = 'sessoes_local_check';
"@

$sqlScript | Out-File -FilePath "fix_constraint.sql" -Encoding UTF8

try {
    $env:PGPASSWORD = "postgres"
    psql -U postgres -d futebol_analytics -f fix_constraint.sql
    Write-Host "  ✓ Database constraint fixed" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Error fixing constraint: $_" -ForegroundColor Red
    Write-Host "  You may need to run the SQL manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Test session creation
Write-Host "Step 4: Testing session creation..." -ForegroundColor Yellow
try {
    $result = python -c "import requests; r = requests.post('http://localhost:8000/api/sessions/', json={'tipo': 'Treino', 'data': '2026-02-06', 'duracao_min': 90, 'local': None}); print(r.status_code); print(r.text[:200])"
    if ($result -match "200|201") {
        Write-Host "  ✓ Session creation working!" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Session creation still failing" -ForegroundColor Red
        Write-Host "  Response: $result" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "  ✗ Error testing session creation: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Try creating a session from the frontend" -ForegroundColor White
Write-Host "2. Check http://localhost:5173/sessions" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
