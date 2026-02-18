# Advanced Training Load Metrics - Specification

## Metrics Identified from Screenshots

### 1. **Monotonia (Monotony)**
**Formula:** `Monotony = Mean / Standard Deviation`

**Interpretation:**
- 🟢 **< 1.0**: Normal load variation (Healthy)
- 🟡 **1.0 - 2.0**: Low variation (Identical loads between training)
- 🔴 **> 2.0**: Very low variation (Risk of overtraining)

**Purpose:** Measures how consistent training loads are within a week. High monotony = little variation = increased injury risk.

---

### 2. **Tensão/Strain**
**Formula:** `Strain = Weekly Load × Monotony`

**Interpretation:**
- 🟢 **< 4000**: Low tension/strain
- 🟡 **4000 - 6000**: Attention needed
- 🔴 **> 6000**: High risk - care with load

**Purpose:** Combines total weekly load with monotony to assess overall training stress.

---

### 3. **Score Z (Z-Score)**
**Formula:** `Z = (Individual Value - Group Mean) / Group SD`

**Interpretation:**
- 🔴 **< -2.0**: Much below group normality
- 🟡 **-2.0 to -1.0**: Below group normality
- 🟢 **-1.0 to 1.0**: Within group normality
- 🟡 **1.0 to 2.0**: Above group normality
- 🔴 **> 2.0**: Much above group normality

**Purpose:** Shows how far an athlete deviates from team average (relative load).

---

### 4. **ACWR (Acute:Chronic Workload Ratio)**
**Formula:** `ACWR = Acute Load (7 days) / Chronic Load (28 days)`

**Interpretation:**
- 🔴 **< 0.8**: Low load → Increased injury risk (detraining)
- 🟢 **0.8 - 1.3**: Sweet spot → Optimal performance zone
- 🟡 **1.3 - 1.5**: Slightly elevated → Monitor
- 🔴 **> 1.5**: Danger zone → High injury risk (overtraining)

**Purpose:** Injury risk predictor - compares recent load to chronic load.

---

### 5. **Variação % (Week-to-Week Variation)**
**Formula:** `Variation % = ((Current Week - Previous Week) / Previous Week) × 100`

**Interpretation:**
- Used to track weekly load changes
- Large swings (>20%) may indicate risk

---

### 6. **SCS & MCS** (Session/Microcycle Calculations)
Based on screenshot context:
- **SCS**: Likely "Soma Carga Semanal" (Weekly Load Sum)
- **MCS**: Likely "Média Carga Semanal" (Weekly Load Average)

---

## Database Schema Requirements

### New Table: `metricas_carga` (Load Metrics)
```sql
CREATE TABLE metricas_carga (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER REFERENCES atletas(id),
    semana_inicio DATE,
    semana_fim DATE,
    
    -- Weekly metrics
    carga_total_semanal DECIMAL(10,2),      -- Total weekly load (sum of RPE × duration)
    media_carga DECIMAL(10,2),               -- Average daily load
    desvio_padrao DECIMAL(10,2),             -- Standard deviation
    
    -- Advanced metrics
    monotonia DECIMAL(10,4),                 -- Monotony (mean/SD)
    tensao DECIMAL(10,2),                    -- Strain (load × monotony)
    variacao_percentual DECIMAL(10,2),       -- Week-to-week % change
    
    -- ACWR
    carga_aguda DECIMAL(10,2),               -- 7-day acute load
    carga_cronica DECIMAL(10,2),             -- 28-day chronic load
    acwr DECIMAL(10,4),                      -- Acute:Chronic ratio
    
    -- Z-Score (calculated relative to team)
    z_score_carga DECIMAL(10,4),
    z_score_monotonia DECIMAL(10,4),
    z_score_tensao DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metricas_atleta ON metricas_carga(atleta_id);
CREATE INDEX idx_metricas_semana ON metricas_carga(semana_inicio);
```

---

## Calculation Functions Needed

### Python Functions (Backend)

```python
def calcular_monotonia(cargas: list[float]) -> float:
    """
    Monotony = Mean / Standard Deviation
    Lower SD = higher monotony (more repetitive)
    """
    if len(cargas) < 2:
        return None
    media = sum(cargas) / len(cargas)
    desvio = statistics.stdev(cargas)
    if desvio == 0:
        return None  # Cannot divide by zero
    return media / desvio

def calcular_tensao(carga_total: float, monotonia: float) -> float:
    """
    Strain = Total Weekly Load × Monotony
    """
    if monotonia is None:
        return None
    return carga_total * monotonia

def calcular_acwr(carga_7_dias: float, carga_28_dias: float) -> float:
    """
    ACWR = Acute Load (7d) / Chronic Load (28d)
    """
    if carga_28_dias == 0:
        return None
    return carga_7_dias / carga_28_dias

def calcular_z_score(valor: float, media_grupo: float, desvio_grupo: float) -> float:
    """
    Z-Score = (Individual - Group Mean) / Group SD
    """
    if desvio_grupo == 0:
        return None
    return (valor - media_grupo) / desvio_grupo
```

---

## API Endpoints Needed

### 1. Weekly Metrics by Athlete
`GET /api/athletes/{id}/weekly-metrics`
```json
{
  "athlete_id": 5,
  "weeks": [
    {
      "week_start": "2025-09-07",
      "week_end": "2025-09-13",
      "total_load": 2450,
      "avg_load": 408.3,
      "std_dev": 125.4,
      "monotony": 3.25,
      "strain": 7962.5,
      "variation_pct": 15.2,
      "acwr": 1.12,
      "z_score_load": 0.45,
      "z_score_monotony": 1.8,
      "risk_level": "moderate"
    }
  ]
}
```

### 2. Team Averages by Position
`GET /api/team/metrics/by-position`
```json
{
  "positions": {
    "GR": {
      "avg_load": 1850,
      "avg_monotony": 2.1,
      "avg_strain": 3885,
      "avg_acwr": 1.05,
      "athlete_count": 2
    },
    "DC": { ... },
    "MC": { ... }
  }
}
```

### 3. Team Overview with Risk Zones
`GET /api/team/load-overview`
```json
{
  "week": "2025-09-07",
  "athletes": [
    {
      "id": 5,
      "name": "RICARDO",
      "position": "MC",
      "monotony": 1.85,
      "monotony_zone": "yellow",
      "strain": 5200,
      "strain_zone": "yellow",
      "acwr": 1.42,
      "acwr_zone": "yellow",
      "z_score": 0.8,
      "z_score_zone": "green"
    }
  ]
}
```

---

## Frontend Components Needed

### 1. Load Monitoring Dashboard
- **Weekly metrics table** with color-coded zones
- **Position group comparison** (bar charts)
- **Team heatmap** showing risk distribution

### 2. Athlete Detail - Advanced Tab
- **Monotony trend chart** (line graph over weeks)
- **Strain gauge** visualization
- **ACWR graph** with sweet spot zones highlighted
- **Z-Score radar chart** (multi-metric comparison)

### 3. Team Risk Matrix
- **Grid view**: Athletes × Metrics with color zones
- **Filter by position**
- **Sort by risk level**

---

## Implementation Priority

1. ✅ **Phase 1**: Database schema + calculation functions
2. ✅ **Phase 2**: Backend endpoints for individual athlete metrics
3. ✅ **Phase 3**: Backend endpoints for team/position aggregations
4. ✅ **Phase 4**: Frontend basic metrics display
5. ✅ **Phase 5**: Frontend advanced visualizations

---

## Color Coding System

```javascript
// Monotony
const getMonotonyColor = (value) => {
  if (value < 1.0) return 'green';
  if (value < 2.0) return 'yellow';
  return 'red';
};

// Strain
const getStrainColor = (value) => {
  if (value < 4000) return 'green';
  if (value < 6000) return 'yellow';
  return 'red';
};

// ACWR
const getACWRColor = (value) => {
  if (value < 0.8) return 'red';
  if (value < 1.3) return 'green';
  if (value < 1.5) return 'yellow';
  return 'red';
};

// Z-Score
const getZScoreColor = (value) => {
  const abs = Math.abs(value);
  if (abs < 1.0) return 'green';
  if (abs < 2.0) return 'yellow';
  return 'red';
};
```

---

## Data Requirements

For accurate calculations, we need:
- ✅ Daily PSE data (already have)
- ✅ Session duration (already have)
- ⚠️ Historical data (need at least 4 weeks for ACWR)

**Current Status:**
- We have 5 jornadas (weeks) of data
- Sufficient for basic ACWR calculation
- Can calculate all metrics immediately
