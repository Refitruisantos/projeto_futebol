# Mock Data Generation System

## Overview

Comprehensive system for generating **realistic synthetic training data** to support:

✅ **ML Model Testing** - Test forecasting models without waiting for real data  
✅ **Scenario Simulation** - Injury recovery, load management, game congestion  
✅ **Backtesting** - Validate models against controlled historical scenarios  
✅ **Edge Case Training** - Generate rare but important patterns  

---

## Architecture

### 1. **Data Profiler** (`backend/utils/data_profiler.py`)

Extracts statistical patterns from real training data:

```python
from data_profiler import DataProfiler

profiler = DataProfiler(db_connection)
profile = profiler.create_full_profile()

# Profile contains:
# - Column distributions (mean, std, min, max, quantiles)
# - Conditional distributions (by position, session type)
# - Correlations between metrics
# - Temporal patterns (weekly seasonality, trends)
# - Constraints from schema
```

**Profiles created:**
- **Column-level**: PSE, duration, load, distance, speed, sprints, accelerations
- **Conditional**: By athlete position (GR, DC, DL, MC, EX, AV)
- **Conditional**: By session type (training, game, recovery)
- **Temporal**: Weekly patterns, day-of-week frequency, trends

### 2. **Mock Data Generator** (`backend/utils/mock_data_generator.py`)

Generates realistic synthetic data using multiple strategies:

#### **Strategy 1: Bootstrap + Variation**
- Resample real data blocks (days/weeks)
- Add controlled noise to maintain realism
- Fast and preserves complex patterns

#### **Strategy 2: Parametric Models**
- Fit distributions (normal, log-normal) to real data
- Generate from learned parameters
- Good for long-term generation

#### **Strategy 3: Conditional Generation**
- Apply position-specific modifiers
- Session-type specific distributions
- Scenario-driven adjustments

```python
from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType

config = GenerationConfig(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 3, 31),
    num_athletes=20,
    positions=['GR', 'DC', 'DL', 'MC', 'EX', 'AV'],
    training_days=[0, 1, 2, 3, 4],  # Mon-Fri
    game_days=[5],  # Saturday
    sessions_per_week=6,
    scenario=ScenarioType.NORMAL,
    fidelity=0.8,  # 80% realistic
    seed=42  # Reproducibility
)

generator = MockDataGenerator(config, db)
dataset = generator.generate_full_dataset()
```

### 3. **API Endpoints** (`backend/routers/mock_data.py`)

RESTful API for generation and validation:

```bash
# Generate mock data
POST /api/mock-data/generate
{
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-03-31T23:59:59",
  "num_athletes": 20,
  "scenario": "normal_season",
  "seed": 42,
  "write_to_db": false
}

# Get available scenarios
GET /api/mock-data/scenarios

# Get data profile
GET /api/mock-data/profile

# Validate generated data
POST /api/mock-data/validate
```

### 4. **Data Validator** (`backend/utils/data_validator.py`)

Validates generated data quality:

```python
from data_validator import DataValidator

validator = DataValidator(db)
results = validator.validate_mock_data(generated_data)

# Checks:
# - Schema constraints (PSE 1-10, duration > 0, etc.)
# - Distribution similarity to real data
# - Correlation preservation
# - Temporal pattern matching
# - Overall quality score
```

---

## Scenarios

### 1. **Normal Season** (`ScenarioType.NORMAL`)
- **Use Case**: Baseline testing, general model training
- **Characteristics**: Balanced load, 5-6 sessions/week
- **Load Pattern**: Stable with natural variation

### 2. **Taper Period** (`ScenarioType.TAPER`)
- **Use Case**: Test model response to planned load drops
- **Characteristics**: Gradual 30% load reduction
- **Load Pattern**: Decreasing weekly load before competition

### 3. **Overload Period** (`ScenarioType.OVERLOAD`)
- **Use Case**: Test overtraining detection
- **Characteristics**: 20% load increase, higher monotony
- **Load Pattern**: Sustained high load with low variation

### 4. **Injury Recovery** (`ScenarioType.INJURY_RECOVERY`)
- **Use Case**: Test recovery protocols, load progression
- **Characteristics**: Progressive increase from 50% → 100%
- **Load Pattern**: Linear weekly increase (10% per week)

### 5. **Game Congestion** (`ScenarioType.GAME_CONGESTION`)
- **Use Case**: Test fatigue accumulation, recovery strategies
- **Characteristics**: 3+ games/week, reduced training
- **Load Pattern**: Spiky (high game load, low training load)

### 6. **Off-Season** (`ScenarioType.OFF_SEASON`)
- **Use Case**: Test detraining detection
- **Characteristics**: Low frequency (2-3 sessions/week), low intensity
- **Load Pattern**: Sustained low load

---

## Usage Examples

### Example 1: Generate 3 Months of Normal Training

```python
from datetime import datetime, timedelta
from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType

config = GenerationConfig(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 3, 31),
    num_athletes=20,
    positions=['GR', 'DC', 'DC', 'DL', 'DL', 'MC', 'MC', 'MC', 'EX', 'EX', 'AV', 'AV'],
    training_days=[0, 1, 2, 3, 4],  # Mon-Fri
    game_days=[5],  # Saturday
    sessions_per_week=6,
    scenario=ScenarioType.NORMAL,
    seed=42
)

generator = MockDataGenerator(config)
dataset = generator.generate_full_dataset()

print(f"Generated {len(dataset['pse_data'])} PSE records")
print(f"Generated {len(dataset['gps_data'])} GPS records")
```

### Example 2: Simulate Injury Recovery Protocol

```python
# Week 1-4: Progressive return to full load
config = GenerationConfig(
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 28),
    num_athletes=1,  # Single athlete
    positions=['MC'],
    training_days=[0, 2, 4],  # 3 days/week initially
    game_days=[],  # No games during recovery
    sessions_per_week=3,
    scenario=ScenarioType.INJURY_RECOVERY,
    seed=123
)

dataset = generator.generate_full_dataset()

# Extract weekly loads
for week in range(4):
    week_data = [d for d in dataset['pse_data'] 
                 if week*7 <= (d['time'].date() - config.start_date.date()).days < (week+1)*7]
    weekly_load = sum(d['carga_total'] for d in week_data)
    print(f"Week {week+1}: {weekly_load:.0f} (expected ~{500 + week*100})")
```

### Example 3: Test Forecasting Model with API

```bash
# Generate data via API
curl -X POST "http://localhost:8000/api/mock-data/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-06-30T23:59:59",
    "num_athletes": 25,
    "scenario": "game_congestion",
    "seed": 789,
    "write_to_db": false
  }'

# Response includes:
# - Generation statistics
# - Data preview
# - Download URL (if exported)
```

---

## Configuration Options

### Time Period
```python
start_date: datetime  # Start of generation period
end_date: datetime    # End of generation period
```

### Entities
```python
num_athletes: int           # Number of athletes (1-50)
positions: List[str]        # Distribution of positions
```

### Calendar
```python
training_days: List[int]    # Days for training (0=Mon, 6=Sun)
game_days: List[int]        # Days for matches
sessions_per_week: int      # Target sessions per week (1-10)
```

### Quality Control
```python
fidelity: float            # Realism level (0.0-1.0)
seed: Optional[int]        # Random seed for reproducibility
noise_level: float         # Amount of random variation (0.0-1.0)
```

---

## Position-Specific Modifiers

Generated data respects position-specific characteristics:

| Position | Load Modifier | Distance Modifier | Sprint Modifier |
|----------|--------------|-------------------|-----------------|
| **GR** (Goalkeeper) | 0.7 | 0.5 | 0.3 |
| **DC** (Center Back) | 0.9 | 0.85 | 0.7 |
| **DL** (Full Back) | 1.0 | 1.0 | 1.0 |
| **MC** (Midfielder) | 1.05 | 1.1 | 0.9 |
| **EX** (Winger) | 1.1 | 1.05 | 1.2 |
| **AV** (Forward) | 1.0 | 0.95 | 1.3 |

---

## Validation Framework

### Constraint Validation
```python
# Checks schema constraints
- PSE: 1 ≤ pse ≤ 10
- Duration: duration_min > 0
- Distance: 0 ≤ distance ≤ 15000m
- Max Speed: 0 ≤ speed ≤ 45 km/h
- Sprints: sprints ≥ 0
```

### Distribution Validation
```python
# Compares to real data distributions
- Mean difference < 10%
- Std deviation difference < 15%
- Quantile preservation (Q25, Q50, Q75)
```

### Correlation Validation
```python
# Key correlations preserved
- Load ↔ Duration (strong positive)
- Distance ↔ Duration (positive)
- Max Speed ↔ Sprints (moderate positive)
```

---

## Backtesting with Mock Data

### Rolling Origin Backtesting

```python
# Generate 1 year of data
dataset = generate_full_dataset(
    start=datetime(2024, 1, 1),
    end=datetime(2024, 12, 31),
    scenario=ScenarioType.NORMAL
)

# Split into train/test windows
train_weeks = 12  # Train on 12 weeks
test_weeks = 4    # Predict 4 weeks ahead

for origin in range(0, 40, 4):  # Rolling every 4 weeks
    train_data = dataset[origin:origin+train_weeks]
    test_data = dataset[origin+train_weeks:origin+train_weeks+test_weeks]
    
    # Train model
    model.fit(train_data)
    
    # Predict
    predictions = model.predict(test_data)
    
    # Evaluate
    mae = calculate_mae(predictions, test_data)
    print(f"Origin {origin}: MAE = {mae:.2f}")
```

### Scenario Testing

```python
scenarios = [
    ScenarioType.NORMAL,
    ScenarioType.TAPER,
    ScenarioType.OVERLOAD,
    ScenarioType.GAME_CONGESTION
]

results = {}
for scenario in scenarios:
    dataset = generate_dataset(scenario=scenario, seed=42)
    
    # Test model
    predictions = model.predict(dataset)
    metrics = evaluate(predictions, dataset)
    
    results[scenario.value] = metrics

# Compare model performance across scenarios
print_comparison_table(results)
```

---

## Integration with ML Pipeline

### 1. Generate Raw Data
```python
raw_data = generator.generate_full_dataset()
```

### 2. Process Through Pipeline
```python
# Use same processing pipeline as production
from scripts.calculate_weekly_metrics import process_pse_data

processed = process_pse_data(raw_data['pse_data'])
```

### 3. Calculate Features
```python
# Generate features for ML
features = feature_engineer.transform(processed)
```

### 4. Train/Test Model
```python
model.fit(features['train'])
predictions = model.predict(features['test'])
```

---

## Best Practices

### ✅ DO:
- **Set a seed** for reproducibility
- **Validate generated data** before use
- **Use appropriate scenarios** for your test case
- **Generate sufficient volume** (3+ months minimum)
- **Combine multiple scenarios** for robust testing
- **Profile real data** first for accurate generation

### ❌ DON'T:
- **Write to production database** without caution
- **Assume all generated data is perfect** - always validate
- **Use single scenario** for comprehensive testing
- **Ignore position differences** - they matter
- **Skip temporal validation** - weekly patterns are important

---

## API Reference

### Generate Mock Data
```http
POST /api/mock-data/generate
Content-Type: application/json

{
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-03-31T23:59:59",
  "num_athletes": 20,
  "positions": ["GR", "DC", "DL", "MC", "EX", "AV"],
  "training_days": [0, 1, 2, 3, 4],
  "game_days": [5],
  "sessions_per_week": 6,
  "scenario": "normal_season",
  "fidelity": 0.8,
  "seed": 42,
  "write_to_db": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated 3600 mock records",
  "stats": {
    "athletes_generated": 20,
    "sessions_generated": 90,
    "pse_records": 1800,
    "gps_records": 1260,
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-03-31",
      "days": 90
    },
    "scenario": "normal_season",
    "seed": 42
  },
  "data_preview": {
    "athletes_sample": [...],
    "sessions_sample": [...],
    "pse_sample": [...],
    "gps_sample": [...]
  }
}
```

### List Scenarios
```http
GET /api/mock-data/scenarios
```

### Get Data Profile
```http
GET /api/mock-data/profile
```

### Validate Generated Data
```http
POST /api/mock-data/validate
Content-Type: application/json

{
  "generated_data": {...}
}
```

---

## Future Enhancements

### Planned Features:
- [ ] KDE-based distribution sampling
- [ ] LSTM-based time series generation
- [ ] Copula-based correlation preservation
- [ ] Injury pattern injection
- [ ] Weather condition simulation
- [ ] Export to Parquet/CSV
- [ ] Direct database sandbox writing
- [ ] Automated backtesting framework
- [ ] Comparative model evaluation

---

## Support

For questions or issues:
- Review this documentation
- Check API interactive docs: `http://localhost:8000/docs`
- Examine example scripts in `scripts/`
- Validate against real data profiles

**Version:** 1.0  
**Last Updated:** December 2024
