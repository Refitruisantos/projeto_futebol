# 🚀 Quick Start: Mock Data Generation

## Option 1: Test Script (Recommended - No API Needed)

Run the standalone test script:

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA
python scripts\test_mock_generation.py
```

**This will:**
- ✅ Generate sample data for multiple scenarios
- ✅ Compare position-specific patterns
- ✅ Validate reproducibility
- ✅ Show statistics and samples
- ✅ Work without starting the API server

---

## Option 2: Via API (Requires Server)

### Start Backend Server:

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Test API Endpoints:

**1. List available scenarios:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/mock-data/scenarios" -Method GET | Select-Object -ExpandProperty Content
```

**2. Generate mock data:**
```powershell
$body = @{
    start_date = "2025-01-01T00:00:00"
    end_date = "2025-01-31T23:59:59"
    num_athletes = 10
    scenario = "normal_season"
    seed = 42
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/mock-data/generate" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

**3. View API docs:**
```
Open browser: http://localhost:8000/docs
```

---

## Option 3: Python Script (Custom Generation)

Create your own generation script:

```python
# my_generation.py
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend' / 'utils'))
from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType

config = GenerationConfig(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 3, 31),
    num_athletes=20,
    positions=['GR', 'DC', 'DL', 'MC', 'EX', 'AV'],
    training_days=[0, 1, 2, 3, 4],
    game_days=[5],
    sessions_per_week=6,
    scenario=ScenarioType.NORMAL,
    seed=42
)

generator = MockDataGenerator(config)
dataset = generator.generate_full_dataset()

print(f"Generated {len(dataset['pse_data'])} PSE records")

# Save to CSV
import csv
with open('mock_pse_data.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['time', 'atleta_id', 'sessao_id', 'pse', 'duracao_min', 'carga_total'])
    writer.writeheader()
    writer.writerows(dataset['pse_data'])

print("Saved to mock_pse_data.csv")
```

Run it:
```powershell
python my_generation.py
```

---

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError`:

```powershell
# Make sure you're in the right directory
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install dependencies if needed
pip install numpy fastapi uvicorn pydantic
```

### Server Won't Start
Check if another process is using port 8000:

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it if needed (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

## What Gets Generated

### Athletes
- Realistic Portuguese names
- Position-appropriate physical characteristics
- Height: 165-200cm (position-dependent)
- Weight: 65-90kg (position-dependent)

### Sessions
- Training (Mon-Fri): 60-120 min, PSE 3-8
- Games (Sat): 80-100 min, PSE 6-10
- Recovery: 30-60 min, PSE 1-5

### PSE Data
- Respects 1-10 scale
- Position modifiers applied
- Scenario adjustments applied
- Realistic load = PSE × Duration

### GPS Data (70% coverage)
- Distance: 3000-12000m (position/type dependent)
- Max Speed: 20-38 km/h
- Sprints: Correlated with position
- Accelerations: Realistic counts

---

## Next Steps After Generation

### 1. Process Generated Data
```powershell
python scripts\calculate_weekly_metrics.py
```

### 2. View in Dashboard
- Start frontend: `npm run dev` (in frontend folder)
- View metrics at http://localhost:5173

### 3. Use for Model Training
```python
# Load generated data
import pandas as pd
df = pd.read_csv('mock_pse_data.csv')

# Train forecasting model
from your_model import ForecastingModel
model = ForecastingModel()
model.fit(df)
```

---

## Support

**Detailed documentation:** `MOCK_DATA_GENERATION_GUIDE.md`

**API reference:** http://localhost:8000/docs (when server running)

**Test script:** `scripts/test_mock_generation.py`
