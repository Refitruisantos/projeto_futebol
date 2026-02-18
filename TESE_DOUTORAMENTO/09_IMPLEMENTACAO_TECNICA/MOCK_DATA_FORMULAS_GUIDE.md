# Comprehensive Mock Data & Formulas Guide
# ========================================
#
# This file contains all the formulas, calculations, and data structures
# used in the football training load monitoring system.
#
# Generated: 2025-01-29
# Database: PostgreSQL with TimescaleDB
# Frontend: React with TypeScript

## Table of Contents
1. Data Structure Overview
2. Core Formulas & Calculations
3. Risk Assessment Algorithms
4. API Response Formats
5. Sample Data Generation Logic

---

## 1. Data Structure Overview

### Core Tables
```sql
-- Athletes (atletas)
CREATE TABLE atletas (
    id SERIAL PRIMARY KEY,
    jogador_id VARCHAR(100) UNIQUE,    -- ATL001, ATL002...
    nome_completo VARCHAR(200),
    posicao VARCHAR(50),              -- GR, DC, DL, MC, EX, AV
    altura_cm INTEGER,
    massa_kg DECIMAL(5,2),
    ativo BOOLEAN DEFAULT TRUE
);

-- Sessions (sessoes)
CREATE TABLE sessoes (
    id SERIAL PRIMARY KEY,
    data DATE,
    tipo VARCHAR(50),                 -- treino, jogo, recuperacao
    duracao_min INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PSE Data (dados_pse)
CREATE TABLE dados_pse (
    atleta_id INTEGER REFERENCES atletas(id),
    sessao_id INTEGER REFERENCES sessoes(id),
    time TIMESTAMP,
    pse FLOAT CHECK (pse BETWEEN 1 AND 10),  -- Subjective effort 1-10
    duracao_min INTEGER,
    carga_total FLOAT,                         -- PSE × duration
    created_at TIMESTAMP DEFAULT NOW()
);

-- GPS Data (dados_gps)
CREATE TABLE dados_gps (
    atleta_id INTEGER REFERENCES atletas(id),
    sessao_id INTEGER REFERENCES sessoes(id),
    time TIMESTAMP,
    distancia_total FLOAT,                     -- Total distance (m)
    velocidade_max FLOAT,                      -- Max speed (km/h)
    velocidade_media FLOAT,                    -- Average speed (km/h)
    aceleracoes INTEGER,                       -- Number of accelerations
    desaceleracoes INTEGER,                    -- Number of decelerations
    sprints INTEGER,                           -- Number of sprints
    player_load FLOAT,                         -- PlayerLoad metric
    created_at TIMESTAMP DEFAULT NOW()
);

-- Weekly Metrics (metricas_carga)
CREATE TABLE metricas_carga (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER REFERENCES atletas(id),
    semana_inicio DATE,
    semana_fim DATE,
    
    -- Basic weekly metrics
    carga_total_semanal DECIMAL(10,2),        -- Sum of daily loads
    media_carga DECIMAL(10,2),                 -- Average daily load
    desvio_padrao DECIMAL(10,2),               -- Std dev of daily loads
    dias_treino INTEGER,                       -- Training days
    
    -- Advanced metrics
    monotonia DECIMAL(10,4),                   -- Monotony = mean / std_dev
    tensao DECIMAL(10,2),                      -- Strain = total_load × monotony
    variacao_percentual DECIMAL(10,2),         -- Week-to-week % change
    
    -- ACWR (Acute:Chronic Workload Ratio)
    carga_aguda DECIMAL(10,2),                 -- 7-day rolling average
    carga_cronica DECIMAL(10,2),               -- 28-day rolling average
    acwr DECIMAL(10,4),                        -- Acute / Chronic ratio
    
    -- Z-Scores (standardized scores)
    z_score_carga DECIMAL(10,4),               -- (load - team_avg) / team_std
    z_score_monotonia DECIMAL(10,4),
    z_score_tensao DECIMAL(10,4),
    z_score_acwr DECIMAL(10,4),
    
    -- Risk indicators
    nivel_risco_monotonia VARCHAR(10),         -- 'green', 'yellow', 'red'
    nivel_risco_tensao VARCHAR(10),
    nivel_risco_acwr VARCHAR(10),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Core Formulas & Calculations

### 2.1 Basic Load Calculations

#### Daily Training Load
```
Daily Load = PSE × Duration (minutes)

Example:
PSE = 6.5, Duration = 75 min
Daily Load = 6.5 × 75 = 487.5
```

#### Weekly Total Load
```
Weekly Load = Σ(Daily Loads for the week)

Example:
Day 1: 429.0, Day 2: 204.7, Day 3: 415.8, Day 4: 577.2, Day 5: 753.3, Day 6: 791.2
Weekly Load = 429.0 + 204.7 + 415.8 + 577.2 + 753.3 + 791.2 = 3171.2
```

#### Average Daily Load
```
Mean Load = Weekly Load / Number of Training Days

Example:
Mean Load = 3171.2 / 6 = 527.9
```

#### Standard Deviation
```
Std Dev = √[Σ(xi - μ)² / n]

Where:
- xi = each daily load
- μ = mean load
- n = number of training days

Example calculation:
Loads: [429.0, 204.7, 415.8, 577.2, 753.3, 791.2]
Mean = 527.9
Std Dev = √[((429.0-527.9)² + (204.7-527.9)² + ... + (791.2-527.9)²) / 6] = 201.4
```

### 2.2 Advanced Metrics

#### Monotony
```
Monotony = Mean Load / Standard Deviation

Interpretation:
- < 1.5: Low monotony (good variation)
- 1.5-2.0: Moderate monotony
- > 2.0: High monotony (risk factor)

Example:
Monotony = 527.9 / 201.4 = 2.62 (High monotony - RED risk)
```

#### Strain (Training Strain)
```
Strain = Weekly Load × Monotony

Interpretation:
- < 5000: Low strain
- 5000-10000: Moderate strain  
- > 10000: High strain

Example:
Strain = 3171.2 × 2.62 = 8308.5 (Moderate strain - YELLOW risk)
```

#### ACWR (Acute:Chronic Workload Ratio)
```
Acute Load = Average of last 7 days
Chronic Load = Average of last 28 days
ACWR = Acute Load / Chronic Load

Interpretation:
- 0.8-1.3: Sweet spot (optimal preparation)
- 0.6-0.8 or 1.3-1.5: Caution zone
- < 0.6 or > 1.5: Danger zone (high injury risk)

Example:
Acute Load = 527.9 (current week)
Chronic Load = 450.0 (4-week average)
ACWR = 527.9 / 450.0 = 1.17 (Sweet spot - GREEN risk)
```

#### Week-to-Week Variation
```
Variation % = [(Current Week - Previous Week) / Previous Week] × 100

Example:
Current Week = 3171.2
Previous Week = 2850.0
Variation = [(3171.2 - 2850.0) / 2850.0] × 100 = 11.3%
```

### 2.3 Z-Score Calculations

#### Team Z-Scores
```
Z-Score = (Individual Value - Team Mean) / Team Standard Deviation

Example for Load:
Individual Load = 3171.2
Team Mean Load = 2800.0
Team Std Dev = 400.0
Z-Score = (3171.2 - 2800.0) / 400.0 = 0.93

Interpretation:
- Z > 1.0: Above average
- -1.0 < Z < 1.0: Normal range
- Z < -1.0: Below average
```

---

## 3. Risk Assessment Algorithms

### 3.1 Risk Level Classification

#### Monotony Risk
```python
def assess_monotony_risk(monotony_value):
    if monotony_value < 1.5:
        return 'green'
    elif monotony_value < 2.0:
        return 'yellow'
    else:
        return 'red'
```

#### Strain Risk
```python
def assess_strain_risk(strain_value):
    if strain_value < 5000:
        return 'green'
    elif strain_value < 10000:
        return 'yellow'
    else:
        return 'red'
```

#### ACWR Risk
```python
def assess_acwr_risk(acwr_value):
    if 0.8 <= acwr_value <= 1.3:
        return 'green'
    elif 0.6 <= acwr_value <= 1.5:
        return 'yellow'
    else:
        return 'red'
```

### 3.2 Overall Risk Assessment

#### Combined Risk Logic
```python
def calculate_overall_risk(monotony_risk, strain_risk, acwr_risk):
    red_count = sum([monotony_risk == 'red', 
                     strain_risk == 'red', 
                     acwr_risk == 'red'])
    
    if red_count >= 2:
        return 'red'
    elif red_count == 1:
        return 'yellow'
    else:
        return 'green'
```

---

## 4. API Response Formats

### 4.1 Team Dashboard Endpoint
```
GET /api/metrics/team/dashboard

Response:
{
    "week_analyzed": "2025-01-06",
    "athletes_overview": [
        {
            "atleta_id": 241,
            "nome_completo": "Tiago Silva",
            "posicao": "GR",
            "weekly_load": 3383.1,
            "monotony": 4.66,
            "strain": 15766.8,
            "acwr": 1.2,
            "risk_monotony": "red",
            "risk_strain": "red",
            "risk_acwr": "green",
            "training_days": 6,
            "distancia_total_media": 5234.5,
            "velocidade_max_media": 28.3,
            "aceleracoes_media": 23.7,
            "risk_overall": "red"
        }
        // ... more athletes
    ],
    "top_load_athletes": [
        {
            "atleta_id": 244,
            "nome_completo": "Tiago Ribeiro",
            "weekly_load": 5713.9,
            "posicao": "DL"
        }
        // ... top 5 athletes
    ],
    "at_risk_athletes": [
        {
            "atleta_id": 241,
            "nome_completo": "Tiago Silva",
            "risk_factors": ["monotony", "strain"],
            "risk_level": "red"
        }
        // ... athletes at risk
    ],
    "risk_summary": {
        "red": 2,
        "yellow": 1,
        "green": 2
    },
    "team_context": {
        "total_athletes": 5,
        "week_start": "2025-01-06",
        "week_end": "2025-01-12"
    }
}
```

### 4.2 Individual Athlete Endpoint
```
GET /api/metrics/athlete/{athlete_id}?weeks=4

Response:
{
    "athlete_info": {
        "id": 241,
        "nome_completo": "Tiago Silva",
        "posicao": "GR",
        "idade": 28
    },
    "weekly_metrics": [
        {
            "week_start": "2025-01-06",
            "weekly_load": 3383.1,
            "monotony": 4.66,
            "strain": 15766.8,
            "acwr": 1.2,
            "risk_overall": "red",
            "training_days": 6
        }
        // ... previous weeks
    ],
    "trends": {
        "load_trend": "increasing",
        "monotony_trend": "stable",
        "acwr_trend": "optimal"
    },
    "recommendations": [
        "Consider reducing training volume due to high strain",
        "Add recovery sessions to reduce monotony"
    ]
}
```

---

## 5. Sample Data Generation Logic

### 5.1 PSE Data Generation
```python
def generate_pse_data(position, session_type):
    """Generate realistic PSE values based on position and session type"""
    
    # Base PSE by position
    position_baselines = {
        'GR': 4.5,   # Goalkeepers - lower intensity
        'DC': 6.2,   # Defenders
        'DL': 6.8,   # Wing-backs
        'MC': 7.1,   # Midfielders
        'EX': 6.9,   # Wingers
        'AV': 7.3    # Forwards
    }
    
    # Session type modifiers
    session_modifiers = {
        'treino': 1.0,
        'jogo': 1.4,
        'recuperacao': 0.6
    }
    
    base_pse = position_baselines[position]
    modifier = session_modifiers[session_type]
    
    # Add random variation (±20%)
    variation = np.random.uniform(0.8, 1.2)
    pse = base_pse * modifier * variation
    
    # Ensure PSE stays within 1-10 range
    return max(1.0, min(10.0, pse))
```

### 5.2 GPS Data Generation
```python
def generate_gps_data(position, duration_min):
    """Generate realistic GPS metrics"""
    
    # Position-based GPS profiles
    profiles = {
        'GR': {
            'distance_per_min': 80,    # m/min
            'max_speed': 25,           # km/h
            'accelerations_per_min': 0.15
        },
        'DC': {
            'distance_per_min': 95,
            'max_speed': 27,
            'accelerations_per_min': 0.18
        },
        'DL': {
            'distance_per_min': 110,
            'max_speed': 30,
            'accelerations_per_min': 0.22
        },
        'MC': {
            'distance_per_min': 120,
            'max_speed': 32,
            'accelerations_per_min': 0.25
        },
        'EX': {
            'distance_per_min': 115,
            'max_speed': 34,
            'accelerations_per_min': 0.20
        },
        'AV': {
            'distance_per_min': 105,
            'max_speed': 33,
            'accelerations_per_min': 0.23
        }
    }
    
    profile = profiles[position]
    
    # Calculate metrics with variation
    distance = profile['distance_per_min'] * duration_min * np.random.uniform(0.9, 1.1)
    max_speed = profile['max_speed'] * np.random.uniform(0.85, 1.15)
    accelerations = profile['accelerations_per_min'] * duration_min * np.random.uniform(0.8, 1.2)
    
    return {
        'distancia_total': distance,
        'velocidade_max': max_speed,
        'aceleracoes': int(accelerations),
        'desaceleracoes': int(accelerations * 0.9),
        'sprints': int(accelerations * 0.3)
    }
```

### 5.3 Weekly Pattern Generation
```python
def generate_weekly_schedule():
    """Generate realistic weekly training schedule"""
    
    weekly_patterns = {
        'monday': {'type': 'treino', 'duration': 75, 'intensity': 'medium'},
        'tuesday': {'type': 'treino', 'duration': 90, 'intensity': 'high'},
        'wednesday': {'type': 'treino', 'duration': 60, 'intensity': 'low'},
        'thursday': {'type': 'treino', 'duration': 85, 'intensity': 'high'},
        'friday': {'type': 'treino', 'duration': 70, 'intensity': 'medium'},
        'saturday': {'type': 'jogo', 'duration': 105, 'intensity': 'very_high'},
        'sunday': {'type': 'recuperacao', 'duration': 45, 'intensity': 'very_low'}
    }
    
    return weekly_patterns
```

---

## 6. Data Validation Rules

### 6.1 Input Validation
```python
def validate_pse_data(pse, duration):
    """Validate PSE input data"""
    errors = []
    
    if not 1 <= pse <= 10:
        errors.append("PSE must be between 1 and 10")
    
    if duration <= 0 or duration > 180:
        errors.append("Duration must be between 0 and 180 minutes")
    
    return errors

def validate_gps_data(distance, max_speed, accelerations):
    """Validate GPS input data"""
    errors = []
    
    if distance < 0 or distance > 15000:
        errors.append("Distance must be between 0 and 15000 meters")
    
    if max_speed < 0 or max_speed > 45:
        errors.append("Max speed must be between 0 and 45 km/h")
    
    if accelerations < 0:
        errors.append("Accelerations cannot be negative")
    
    return errors
```

### 6.2 Business Logic Validation
```python
def validate_weekly_metrics(weekly_load, training_days):
    """Validate calculated weekly metrics"""
    warnings = []
    
    if weekly_load > 10000:
        warnings.append("Very high weekly load detected")
    
    if training_days > 6:
        warnings.append("Excessive training days - consider recovery")
    
    if training_days < 2:
        warnings.append("Very low training frequency")
    
    return warnings
```

---

## 7. Performance Optimization

### 7.1 Database Indexes
```sql
-- Critical indexes for performance
CREATE INDEX idx_metricas_atleta_week ON metricas_carga(atleta_id, semana_inicio);
CREATE INDEX idx_dados_pse_atleta_time ON dados_pse(atleta_id, time DESC);
CREATE INDEX idx_dados_gps_atleta_time ON dados_gps(atleta_id, time DESC);
CREATE INDEX idx_sessoes_data ON sessoes(data DESC);
```

### 7.2 Query Optimization
```sql
-- Efficient weekly metrics query
WITH weekly_loads AS (
    SELECT 
        a.id as atleta_id,
        a.nome_completo,
        DATE_TRUNC('week', dp.time) as week_start,
        SUM(dp.carga_total) as weekly_load,
        AVG(dp.carga_total) as mean_load,
        STDDEV(dp.carga_total) as std_load,
        COUNT(DISTINCT DATE(dp.time)) as training_days
    FROM atletas a
    JOIN dados_pse dp ON a.id = dp.atleta_id
    WHERE a.ativo = TRUE
    AND dp.time >= NOW() - INTERVAL '4 weeks'
    GROUP BY a.id, a.nome_completo, DATE_TRUNC('week', dp.time)
)
SELECT 
    atleta_id,
    nome_completo,
    week_start,
    weekly_load,
    mean_load,
    std_load,
    training_days,
    CASE 
        WHEN std_load > 0 THEN mean_load / std_load 
        ELSE 1 
    END as monotonia,
    weekly_load * CASE 
        WHEN std_load > 0 THEN mean_load / std_load 
        ELSE 1 
    END as strain
FROM weekly_loads
ORDER BY week_start DESC, weekly_load DESC;
```

---

## 8. Testing Data Sets

### 8.1 Sample Athlete Data
```json
{
    "athletes": [
        {
            "jogador_id": "ATL001",
            "nome_completo": "Tiago Silva",
            "posicao": "GR",
            "altura_cm": 199,
            "massa_kg": 83.0,
            "data_nascimento": "1996-10-09"
        },
        {
            "jogador_id": "ATL002", 
            "nome_completo": "Diogo Martins",
            "posicao": "DC",
            "altura_cm": 191,
            "massa_kg": 82.5,
            "data_nascimento": "1995-02-18"
        }
    ]
}
```

### 8.2 Sample Weekly Data
```json
{
    "week_data": {
        "week_start": "2025-01-06",
        "sessions": [
            {
                "date": "2025-01-06",
                "type": "treino",
                "duration": 75,
                "athlete_data": [
                    {
                        "atleta_id": "ATL001",
                        "pse": 4.1,
                        "gps": {
                            "distance": 3048.72,
                            "max_speed": 33.13,
                            "accelerations": 1
                        }
                    }
                ]
            }
        ]
    }
}
```

---

## 9. Common Calculations Summary

### Quick Reference
```
Daily Load = PSE × Duration
Weekly Load = Σ Daily Loads
Mean Load = Weekly Load / Training Days
Std Dev = √[Σ(xi - μ)² / n]
Monotony = Mean / Std Dev
Strain = Weekly Load × Monotony
ACWR = Acute (7d) / Chronic (28d)
Z-Score = (Value - Team Mean) / Team Std Dev
```

### Risk Thresholds
```
Monotony: <1.5 (Green), 1.5-2.0 (Yellow), >2.0 (Red)
Strain: <5000 (Green), 5000-10000 (Yellow), >10000 (Red)
ACWR: 0.8-1.3 (Green), 0.6-0.8 or 1.3-1.5 (Yellow), <0.6 or >1.5 (Red)
```

---

## 10. Integration Points

### Frontend Integration
```typescript
interface AthleteMetrics {
    atleta_id: number;
    nome_completo: string;
    posicao: string;
    weekly_load: number;
    monotony: number;
    strain: number;
    acwr: number;
    risk_monotony: 'green' | 'yellow' | 'red';
    risk_strain: 'green' | 'yellow' | 'red';
    risk_acwr: 'green' | 'yellow' | 'red';
    risk_overall: 'green' | 'yellow' | 'red';
}

// API call example
const fetchTeamDashboard = async (): Promise<TeamDashboardResponse> => {
    const response = await fetch('/api/metrics/team/dashboard');
    return response.json();
};
```

### Backend Integration
```python
# FastAPI endpoint example
@router.get("/team/dashboard")
async def get_team_dashboard(db: Database = Depends(get_database)):
    query = """
        WITH weekly_metrics AS (
            SELECT 
                a.id,
                a.nome_completo,
                a.posicao,
                mc.carga_total_semanal,
                mc.monotonia,
                mc.tensao,
                mc.acwr,
                mc.nivel_risco_monotonia,
                mc.nivel_risco_tensao,
                mc.nivel_risco_acwr,
                mc.semana_inicio
            FROM atletas a
            JOIN metricas_carga mc ON a.id = mc.atleta_id
            WHERE a.ativo = TRUE
            AND mc.semana_inicio = (
                SELECT MAX(semana_inicio) FROM metricas_carga
            )
        )
        SELECT * FROM weekly_metrics
        ORDER BY carga_total_semanal DESC;
    """
    
    results = db.query_to_dict(query)
    return format_dashboard_response(results)
```

---

**End of Documentation**

This comprehensive guide contains all formulas, data structures, and calculations
used in the football training load monitoring system. Use this as a reference
for understanding the data flow and implementing new features.
