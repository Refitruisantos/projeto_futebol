# PowerShell Script to Test Mock Data Generation API
# Run this after starting the server with: python -m uvicorn main:app --reload

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Mock Data Generation API Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
    Write-Host "✅ Server Status: " -NoNewline -ForegroundColor Green
    Write-Host ($response.Content | ConvertFrom-Json).status
} catch {
    Write-Host "❌ Server not responding" -ForegroundColor Red
    exit
}

# Test 2: List Scenarios
Write-Host "`n2. Available Scenarios" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/mock-data/scenarios" -UseBasicParsing
    $scenarios = $response.Content | ConvertFrom-Json
    Write-Host "✅ Available scenarios:" -ForegroundColor Green
    $scenarios.PSObject.Properties | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.Value.description)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Failed to get scenarios: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Generate Mock Data (Small Dataset)
Write-Host "`n3. Generate Mock Data (1 Week, 5 Athletes)" -ForegroundColor Yellow
$body = @{
    start_date = "2025-02-01T00:00:00"
    end_date = "2025-02-07T23:59:59"
    num_athletes = 5
    positions = @("GR", "DC", "MC", "EX", "AV")
    training_days = @(0, 1, 2, 3, 4)
    game_days = @(5)
    sessions_per_week = 6
    scenario = "normal_season"
    fidelity = 0.8
    seed = 42
    write_to_db = $false
} | ConvertTo-Json

try {
    Write-Host "   Generating..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/mock-data/generate" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ Generation Success!" -ForegroundColor Green
    Write-Host "   Athletes: $($result.stats.athletes_generated)" -ForegroundColor White
    Write-Host "   Sessions: $($result.stats.sessions_generated)" -ForegroundColor White
    Write-Host "   PSE Records: $($result.stats.pse_records)" -ForegroundColor White
    Write-Host "   GPS Records: $($result.stats.gps_records)" -ForegroundColor White
    Write-Host "   Message: $($result.message)" -ForegroundColor Gray
    
    # Show sample data
    if ($result.data_preview.pse_sample) {
        Write-Host "" 
        Write-Host "   Sample PSE Record:" -ForegroundColor Cyan
        $sample = $result.data_preview.pse_sample[0]
        Write-Host "      Time: $($sample.time)" -ForegroundColor White
        Write-Host "      PSE: $($sample.pse)" -ForegroundColor White
        Write-Host "      Duration: $($sample.duracao_min) min" -ForegroundColor White
        Write-Host "      Load: $($sample.carga_total)" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Generation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Generate with Different Scenario
Write-Host "`n4. Generate TAPER Scenario (Load Reduction)" -ForegroundColor Yellow
$body2 = @{
    start_date = "2025-02-01T00:00:00"
    end_date = "2025-02-14T23:59:59"
    num_athletes = 3
    scenario = "taper_period"
    seed = 123
    write_to_db = $false
} | ConvertTo-Json

try {
    Write-Host "   Generating taper period..." -ForegroundColor Gray
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/mock-data/generate" -Method POST -Body $body2 -ContentType "application/json" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "✅ Taper Scenario Generated!" -ForegroundColor Green
    Write-Host "   Total PSE Records: $($result.stats.pse_records)" -ForegroundColor White
    Write-Host "   Scenario: $($result.stats.scenario)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Taper generation failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✅ API Testing Complete!" -ForegroundColor Green
Write-Host "`nView full API docs at: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
