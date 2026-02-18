# API Master Documentation
## Futebol Analytics API - Complete Endpoint Reference

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Frontend URL:** `http://localhost:5173`

---

## Table of Contents
1. [Overview](#overview)
2. [Athletes API](#athletes-api)
3. [Sessions API](#sessions-api)
4. [Metrics API](#metrics-api)
5. [Load Metrics API](#load-metrics-api)
6. [Ingestion API](#ingestion-api)
7. [Database Schema Reference](#database-schema-reference)
8. [Calculation Logic](#calculation-logic)

---

## Overview

### Technology Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL 16 + TimescaleDB
- **Frontend:** React + Vite
- **Charts:** Recharts

### CORS Configuration
- Allowed Origins: `http://localhost:5173`, `http://localhost:3000`
- Methods: All
- Headers: All
- Credentials: Enabled

### Key Features
1. **GPS Data Management** - Catapult sports tracking data
2. **PSE Data Management** - Perceived Subjective Effort (RPE-based)
3. **Load Metrics** - Monotony, Strain, ACWR, Z-Scores
4. **Team Analytics** - Dashboard, risk assessment, performance tracking
5. **Game-by-Game Analysis** - Individual and team comparisons

---

## Athletes API
**Prefix:** `/api/athletes`  
**Tag:** Athletes

### 1. List Athletes
**Endpoint:** `GET /api/athletes/`

**Purpose:** Get list of all athletes with filtering options

**Query Parameters:**
- `ativo` (boolean, default: true) - Filter by active status

**Response:**
```json
[
  {
    "id": 1,
    "jogador_id": "ABC123",
    "nome_completo": "João Silva",
    "data_nascimento": "1995-03-15",
    "posicao": "Médio",
    "numero_camisola": 10,
    "pe_dominante": "Direito",
    "altura_cm": 178,
    "massa_kg": 72,
    "ativo": true
  }
]
```

**Database Tables:** `atletas`

---

### 2. Get Athlete Details
**Endpoint:** `GET /api/athletes/{athlete_id}`

**Purpose:** Get detailed information for a specific athlete

**Path Parameters:**
- `athlete_id` (integer, required) - Athlete database ID

**Response:**
```json
{
  "id": 1,
  "jogador_id": "ABC123",
  "nome_completo": "João Silva",
  "data_nascimento": "1995-03-15",
  "posicao": "Médio",
  "numero_camisola": 10,
  "pe_dominante": "Direito",
  "altura_cm": 178,
  "massa_kg": 72,
  "ativo": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-15T14:30:00"
}
```

**Error Codes:**
- `404` - Athlete not found

**Database Tables:** `atletas`

---

### 3. Get Athlete Metrics
**Endpoint:** `GET /api/athletes/{athlete_id}/metrics`

**Purpose:** Get aggregated performance metrics and recent sessions for an athlete

**Path Parameters:**
- `athlete_id` (integer, required) - Athlete database ID

**Query Parameters:**
- `days` (integer, default: 365) - Historical days to analyze

**Response:**
```json
{
  "athlete_id": 1,
  "metrics": {
    "total_sessions": 45,
    "avg_distance": 8542.50,
    "max_speed": 32.5,
    "avg_accelerations": 42.3,
    "avg_high_intensity_efforts": 18.7,
    "avg_rpe": 6.2,
    "avg_load": 558.3
  },
  "recent_sessions": [
    {
      "id": 150,
      "data": "2024-12-20",
      "tipo": "jogo",
      "duracao_min": 90,
      "jornada": 15,
      "distancia_total": 9500,
      "velocidade_max": 31.2,
      "aceleracoes": 45,
      "desaceleracoes": 38,
      "effs_19_8_kmh": 22,
      "dist_19_8_kmh": 850,
      "pse": 7.0,
      "carga_total": 630,
      "qualidade_sono": 4,
      "stress": 3,
      "fadiga": 3
    }
  ]
}
```

**Database Tables:** `atletas`, `dados_gps`, `dados_pse`, `sessoes`

**Notes:**
- Aggregates from ALL GPS data (no date filtering for historical overview)
- Recent sessions limited to 50 most recent
- Handles duplicate PSE records with AVG aggregation

---

## Sessions API
**Prefix:** `/api/sessions`  
**Tag:** Sessions

### 1. List Sessions
**Endpoint:** `GET /api/sessions/`

**Purpose:** Get list of training sessions and games with filtering

**Query Parameters:**
- `tipo` (string, optional) - Filter by type ("jogo", "treino")
- `data_inicio` (date, optional) - Start date filter (YYYY-MM-DD)
- `data_fim` (date, optional) - End date filter (YYYY-MM-DD)
- `limit` (integer, default: 50, max: 200) - Results limit

**Response:**
```json
[
  {
    "id": 150,
    "data": "2024-12-20",
    "hora_inicio": "18:00:00",
    "tipo": "jogo",
    "duracao_min": 90,
    "adversario": "FC Porto",
    "local": "Casa",
    "competicao": "Liga Portugal",
    "jornada": 15,
    "resultado": "2-1",
    "condicoes_meteorologicas": "Chuva leve",
    "temperatura_celsius": 12,
    "observacoes": "Vitória importante"
  }
]
```

**Database Tables:** `sessoes`

---

### 2. Get Session Details
**Endpoint:** `GET /api/sessions/{session_id}`

**Purpose:** Get detailed session information including GPS data for all players

**Path Parameters:**
- `session_id` (integer, required) - Session database ID

**Response:**
```json
{
  "id": 150,
  "data": "2024-12-20",
  "hora_inicio": "18:00:00",
  "tipo": "jogo",
  "duracao_min": 90,
  "adversario": "FC Porto",
  "local": "Casa",
  "competicao": "Liga Portugal",
  "jornada": 15,
  "resultado": "2-1",
  "gps_data": [
    {
      "atleta_id": 1,
      "nome_completo": "João Silva",
      "posicao": "Médio",
      "distancia_total": 9500,
      "velocidade_max": 31.2,
      "velocidade_media": 7.8,
      "sprints": 12,
      "aceleracoes": 45,
      "desaceleracoes": 38,
      "player_load": 420,
      "dist_19_8_kmh": 850,
      "dist_25_2_kmh": 320,
      "effs_19_8_kmh": 22,
      "effs_25_2_kmh": 8
    }
  ]
}
```

**Error Codes:**
- `404` - Session not found

**Database Tables:** `sessoes`, `dados_gps`, `atletas`

---

## Metrics API
**Prefix:** `/api/metrics`  
**Tag:** Metrics

### 1. Team Dashboard (Enhanced with Decision Support)
**Endpoint:** `GET /api/metrics/team/dashboard`

**Purpose:** Get complete team overview with integrated risk indicators and decision support

**Design Principles:**
- Answers: Who is at risk? Why? Is it getting worse/better?
- Simple, actionable insights for coaching staff
- Based on latest weekly metrics from `metricas_carga`
- Sorted by risk level (red → yellow → green)

**Response:**
```json
{
  "week_analyzed": "2024-12-16",
  "athletes_overview": [
    {
      "atleta_id": 1,
      "nome_completo": "João Silva",
      "posicao": "Médio",
      "ativo": true,
      
      "weekly_load": 3500,
      "monotony": 5.85,
      "strain": 20475,
      "acwr": 1.35,
      
      "z_load": 0.71,
      "z_monotony": 2.06,
      "z_strain": 2.81,
      "z_acwr": 1.33,
      
      "risk_monotony": "red",
      "risk_strain": "red",
      "risk_acwr": "yellow",
      "risk_overall": "red",
      
      "training_days": 7,
      "num_sessoes": 8,
      "distancia_total_media": 8500,
      "velocidade_max_media": 30.5,
      "aceleracoes_media": 42
    }
  ],
  "top_load_athletes": [
    {
      "atleta_id": 5,
      "nome_completo": "Pedro Costa",
      "posicao": "Defesa",
      "weekly_load": 3800,
      "risk_overall": "yellow"
    }
  ],
  "at_risk_athletes": [
    {
      "atleta_id": 1,
      "nome_completo": "João Silva",
      "posicao": "Médio",
      "risk_overall": "red",
      "risk_monotony": "red",
      "risk_strain": "red",
      "risk_acwr": "yellow"
    }
  ],
  "risk_summary": {
    "red": 3,
    "yellow": 8,
    "green": 12,
    "unknown": 0
  },
  "team_context": {
    "mean_load": 3200,
    "mean_monotony": 4.2,
    "mean_strain": 13440,
    "mean_acwr": 1.15
  }
}
```

**New Fields in athletes_overview:**

**Identification:**
- `atleta_id` - Database ID
- `nome_completo` - Full name
- `posicao` - Position
- `ativo` - Active roster status

**Load Metrics (Last Week):**
- `weekly_load` - Total weekly load (PSE × duration)
- `monotony` - Load variation index
- `strain` - Total strain (load × monotony)
- `acwr` - Acute:Chronic Workload Ratio

**Statistical Normalization (Z-Scores):**
- `z_load` - Load compared to team average
- `z_monotony` - Monotony compared to team average
- `z_strain` - Strain compared to team average  
- `z_acwr` - ACWR compared to team average

**Interpretation:** Z-score tells how many standard deviations from team mean
- `-1 to +1`: Normal range
- `±1 to ±2`: Outside normal
- `Beyond ±2`: Extreme outlier

**Risk Indicators:**
- `risk_monotony` - Individual monotony risk (green/yellow/red)
- `risk_strain` - Individual strain risk (green/yellow/red)
- `risk_acwr` - Individual ACWR risk (green/yellow/red)
- `risk_overall` - **Overall risk = worst of the three**

**Risk Overall Logic:**
```python
risk_overall = max(risk_monotony, risk_strain, risk_acwr)
# Priority: red > yellow > green
```

**GPS Context:**
- `training_days` - Days trained this week
- `num_sessoes` - Number of sessions
- `distancia_total_media` - Average distance
- `velocidade_max_media` - Average max speed
- `aceleracoes_media` - Average accelerations

**Additional Response Fields:**
- `week_analyzed` - ISO date of the week being analyzed
- `risk_summary` - Count of athletes at each risk level
- `team_context` - Team averages for comparison

**Database Tables:** `metricas_carga`, `atletas`, `dados_gps`, `sessoes`

**Sorting:** Athletes sorted by risk level (red first, then yellow, then green)

**Fallback:** If no `metricas_carga` data exists, returns simple dashboard from `dashboard_principal` materialized view

**Business Logic:**
1. Get most recent week from `metricas_carga`
2. Calculate team statistics (mean, std dev) for z-scores
3. Join athlete data with latest metrics
4. Calculate z-scores for each athlete
5. Determine `risk_overall` as worst of three risks
6. Sort by risk level and return with context

---

### 2. Team Summary
**Endpoint:** `GET /api/metrics/team/summary`

**Purpose:** Get aggregated team-wide GPS and PSE metrics

**Response:**
```json
{
  "total_athletes": 25,
  "total_sessions_7d": 120,
  "avg_player_load_7d": 485.6,
  "avg_distance": 7800.3,
  "avg_max_speed": 29.8,
  "avg_accelerations": 38.5,
  "avg_decelerations": 35.2,
  "avg_sprints": 10.7,
  "avg_high_speed_distance": 720.4,
  "avg_rhie": 15.3
}
```

**Database Tables:** `atletas`, `dados_gps`, `dados_pse`, `sessoes`

**Notes:**
- Includes new GPS scientific metrics (accelerations, decelerations, sprints, RHIE)
- Aggregates from ALL active athletes' data

---

### 3. Get Games Data (Team Averages)
**Endpoint:** `GET /api/metrics/games/data`

**Purpose:** Get game-by-game team average metrics for visualization

**Response:**
```json
{
  "total_games": 45,
  "games": [
    {
      "sessao_id": 150,
      "data": "2024-12-20",
      "tipo": "jogo",
      "adversario": "FC Porto",
      "local": "Casa",
      "resultado": "2-1",
      "num_atletas": 18,
      "avg_distance": 8500.5,
      "avg_max_speed": 30.2,
      "avg_accelerations": 40.3,
      "avg_decelerations": 37.8,
      "avg_sprints": 11.2,
      "avg_high_speed_distance": 750.6,
      "avg_player_load": 410.5,
      "avg_pse_load": 560.3,
      "avg_pse": 6.5,
      "avg_duration": 88
    }
  ]
}
```

**Database Tables:** `sessoes`, `dados_gps`, `dados_pse`

**Notes:**
- Returns last 200 sessions
- Team averages per game
- Used for GameAnalysis team view

---

### 4. Get Player Games Data
**Endpoint:** `GET /api/metrics/games/player/{athlete_id}`

**Purpose:** Get game-by-game individual player metrics with roster verification

**Path Parameters:**
- `athlete_id` (integer, required) - Athlete database ID

**Response:**
```json
{
  "player_info": {
    "id": 1,
    "nome_completo": "João Silva",
    "posicao": "Médio",
    "numero_camisola": 10,
    "ativo": true
  },
  "is_active_roster": true,
  "total_games": 38,
  "games": [
    {
      "sessao_id": 150,
      "data": "2024-12-20",
      "tipo": "jogo",
      "adversario": "FC Porto",
      "local": "Casa",
      "resultado": "2-1",
      "distance": 9500,
      "max_speed": 31.2,
      "accelerations": 45,
      "decelerations": 38,
      "sprints": 12,
      "high_speed_distance": 850,
      "player_load": 420,
      "pse_load": 630,
      "pse": 7.0,
      "duration": 90,
      "has_gps_data": true,
      "has_pse_data": true
    }
  ]
}
```

**Error Codes:**
- `404` - Player not found

**Database Tables:** `atletas`, `sessoes`, `dados_gps`, `dados_pse`

**Features:**
- Roster verification (`is_active_roster`)
- Individual player metrics (not averages)
- Data availability flags
- Used for GameAnalysis individual and comparison views

---

## Load Metrics API
**Prefix:** `/api/load-metrics`  
**Tag:** Load Metrics

### 1. Get Athlete Load Metrics
**Endpoint:** `GET /api/load-metrics/athlete/{athlete_id}`

**Purpose:** Get weekly load metrics with scientific calculations (Monotony, Strain, ACWR)

**Path Parameters:**
- `athlete_id` (integer, required) - Athlete database ID

**Query Parameters:**
- `weeks` (integer, optional) - Number of recent weeks to return

**Response:**
```json
{
  "athlete": {
    "athlete_id": 1,
    "name": "João Silva",
    "position": "Médio"
  },
  "weeks": [
    {
      "week_start": "2024-12-16",
      "week_end": "2024-12-22",
      "load": {
        "total": 3500,
        "average": 500,
        "std_dev": 85.5,
        "training_days": 7
      },
      "monotony": {
        "value": 5.85,
        "risk_level": "red",
        "z_score": 1.8
      },
      "strain": {
        "value": 20475,
        "risk_level": "red",
        "z_score": 2.1
      },
      "acwr": {
        "value": 1.35,
        "acute_load": 3500,
        "chronic_load": 2592,
        "risk_level": "yellow",
        "z_score": 0.5
      },
      "variation_pct": 12.5
    }
  ],
  "total_weeks": 8
}
```

**Error Codes:**
- `404` - No metrics found for athlete

**Database Tables:** `metricas_carga`, `atletas`

**Risk Levels:**
- `green` - Normal/safe
- `yellow` - Moderate/monitor
- `red` - High risk

---

### 2. Get Team Overview
**Endpoint:** `GET /api/load-metrics/team/overview`

**Purpose:** Get team-wide load metrics for a specific week

**Query Parameters:**
- `week_start` (date, optional) - Specific week (defaults to most recent)

**Response:**
```json
{
  "week": "2024-12-16",
  "athletes": [
    {
      "athlete_id": 1,
      "name": "João Silva",
      "position": "Médio",
      "week_start": "2024-12-16",
      "total_load": 3500,
      "monotony": 5.85,
      "strain": 20475,
      "acwr": 1.35,
      "z_score_load": 0.3,
      "z_score_monotony": 1.8,
      "z_score_strain": 2.1,
      "z_score_acwr": 0.5,
      "risk_monotony": "red",
      "risk_strain": "red",
      "risk_acwr": "yellow"
    }
  ],
  "total_athletes": 23
}
```

**Error Codes:**
- `404` - No metrics found for specified week

**Database Tables:** `metricas_carga`, `atletas`

**Sorting:** Athletes sorted by risk level (red → yellow → green)

---

### 3. Get Trends
**Endpoint:** `GET /api/load-metrics/trends`

**Purpose:** Get historical trends for load metrics visualization

**Query Parameters:**
- `weeks` (integer, default: 8) - Number of weeks to analyze
- `week_start` (date, optional) - Starting week

**Response:**
```json
{
  "weeks": [
    {
      "week_start": "2024-12-16",
      "week_end": "2024-12-22",
      "team_avg": {
        "load": 3200,
        "monotony": 4.2,
        "strain": 13440,
        "acwr": 1.15
      },
      "risk_distribution": {
        "red_count": 3,
        "yellow_count": 8,
        "green_count": 12
      }
    }
  ],
  "total_weeks": 8
}
```

**Database Tables:** `metricas_carga`

---

### 4. Get Position Comparison
**Endpoint:** `GET /api/load-metrics/position-comparison`

**Purpose:** Compare load metrics across different playing positions

**Query Parameters:**
- `week_start` (date, optional) - Specific week

**Response:**
```json
{
  "week": "2024-12-16",
  "positions": [
    {
      "position": "Médio",
      "athlete_count": 8,
      "avg_load": 3400,
      "avg_monotony": 4.5,
      "avg_strain": 15300,
      "avg_acwr": 1.18,
      "risk_distribution": {
        "red": 1,
        "yellow": 3,
        "green": 4
      }
    }
  ]
}
```

**Database Tables:** `metricas_carga`, `atletas`

---

### 5. Get Calculation Details
**Endpoint:** `GET /api/load-metrics/athlete/{athlete_id}/week/{week_start}/details`

**Purpose:** Get detailed breakdown of metric calculations for verification

**Path Parameters:**
- `athlete_id` (integer, required)
- `week_start` (date, required) - Format: YYYY-MM-DD

**Response:**
```json
{
  "athlete": {
    "id": 1,
    "name": "João Silva",
    "position": "Médio"
  },
  "week": {
    "start": "2024-12-16",
    "end": "2024-12-22"
  },
  "metrics": {
    "load": 3500,
    "monotony": 5.85,
    "strain": 20475,
    "acwr": 1.35,
    "acute_load": 3500,
    "chronic_load": 2592
  },
  "calculation_data": {
    "daily_loads_this_week": [
      {"date": "2024-12-16", "load": 450},
      {"date": "2024-12-17", "load": 500},
      {"date": "2024-12-18", "load": 480}
    ],
    "last_7_workouts_for_monotony": [
      {"date": "2024-12-10", "load": 520},
      {"date": "2024-12-11", "load": 490}
    ],
    "monotony_calculation": {
      "workout_loads": [520, 490, 450, 500, 480, 510, 550],
      "mean": 500,
      "std_dev": 85.5,
      "formula": "mean / std_dev",
      "result": 5.85
    },
    "strain_calculation": {
      "weekly_load": 3500,
      "monotony": 5.85,
      "formula": "weekly_load * monotony",
      "result": 20475
    },
    "acwr_calculation": {
      "acute_load_7_days": 3500,
      "chronic_load_28_days": 2592,
      "formula": "acute_load / chronic_load",
      "result": 1.35
    }
  },
  "team_context": {
    "averages": {
      "load": 3200,
      "monotony": 4.2,
      "strain": 13440,
      "acwr": 1.15
    },
    "std_deviations": {
      "load": 420,
      "monotony": 0.8,
      "strain": 2500,
      "acwr": 0.15
    }
  },
  "risk_levels": {
    "monotony": "red",
    "strain": "red",
    "acwr": "yellow"
  },
  "z_scores": {
    "load": 0.71,
    "monotony": 2.06,
    "strain": 2.81,
    "acwr": 1.33
  }
}
```

**Error Codes:**
- `404` - No metrics found

**Database Tables:** `metricas_carga`, `dados_pse`, `atletas`

**Purpose:** Used for "Ver Cálculos" modal in Load Monitoring page

---

### 6. Get Available Weeks
**Endpoint:** `GET /api/load-metrics/weeks`

**Purpose:** Get list of all weeks with metrics data

**Response:**
```json
{
  "total_weeks": 15,
  "weeks": [
    {
      "week_start": "2024-12-16",
      "week_end": "2024-12-22",
      "athlete_count": 23,
      "label": "Semana 16/12/2024"
    }
  ]
}
```

**Database Tables:** `metricas_carga`

**Sorting:** Most recent first (DESC)

---

### 7. Get Risk Thresholds
**Endpoint:** `GET /api/load-metrics/thresholds`

**Purpose:** Get risk threshold values for metrics (for frontend visualization)

**Response:**
```json
{
  "monotony": {
    "green": {"max": 1.0, "description": "Good load variation"},
    "yellow": {"min": 1.0, "max": 2.0, "description": "Moderate variation - monitor"},
    "red": {"min": 2.0, "description": "Low variation - high injury risk"}
  },
  "strain": {
    "green": {"max": 4000, "description": "Low strain"},
    "yellow": {"min": 4000, "max": 6000, "description": "Moderate strain"},
    "red": {"min": 6000, "description": "High strain - care needed"}
  },
  "acwr": {
    "red_low": {"max": 0.8, "description": "Detraining risk"},
    "green": {"min": 0.8, "max": 1.3, "description": "Sweet spot - optimal"},
    "yellow": {"min": 1.3, "max": 1.5, "description": "Elevated - monitor"},
    "red_high": {"min": 1.5, "description": "Overtraining risk"}
  },
  "z_score": {
    "green": {"min": -1.0, "max": 1.0, "description": "Within team normality"},
    "yellow": {"ranges": [[-2.0, -1.0], [1.0, 2.0]], "description": "Outside normal range"},
    "red": {"ranges": [[-999, -2.0], [2.0, 999]], "description": "Far outside normal range"}
  }
}
```

**Notes:** Static endpoint, no database query

---

## Ingestion API
**Prefix:** `/api/ingest`  
**Tag:** Ingestion

### 1. Ingest Catapult CSV
**Endpoint:** `POST /api/ingest/catapult`

**Purpose:** Upload and import Catapult GPS CSV export files

**Request:**
- Content-Type: `multipart/form-data`
- File: CSV file
- Form Data:
  - `jornada` (integer, default: 1) - Match day number
  - `session_date` (string, optional) - Format: YYYY-MM-DD

**Required CSV Columns:**
- `player` - Player name
- `total_distance_m` - Total distance in meters
- `max_velocity_kmh` - Maximum velocity in km/h

**Optional CSV Columns:**
- `acc_b1_3_total_efforts` - Accelerations
- `decel_b1_3_total_efforts` - Decelerations
- `efforts_over_19_8_kmh` - High intensity efforts
- `distance_over_19_8_kmh` - High speed distance
- `efforts_over_25_2_kmh` - Sprint efforts

**Response:**
```json
{
  "status": "success",
  "file": "game_15_gps.csv",
  "file_hash": "abc123...",
  "jornada": 15,
  "session_id": 150,
  "session_date": "2024-12-20",
  "total_rows": 18,
  "inserted": 18,
  "errors": []
}
```

**Error Codes:**
- `400` - Invalid file format or missing columns
- `500` - Processing error

**Database Tables:** `sessoes`, `dados_gps`, `atletas`

**Features:**
- Automatic player name matching (fuzzy matching with similarity)
- Session creation/retrieval
- Duplicate prevention (`ON CONFLICT DO NOTHING`)
- File hash tracking

---

### 2. Get Ingestion History
**Endpoint:** `GET /api/ingest/history`

**Purpose:** Get recent data import history

**Query Parameters:**
- `limit` (integer, default: 20) - Number of records

**Response:**
```json
[
  {
    "fonte": "catapult_csv_game_15_gps.csv",
    "sessao_id": 150,
    "data": "2024-12-20",
    "num_records": 18,
    "ingested_at": "2024-12-20T19:30:00"
  }
]
```

**Database Tables:** `dados_gps`

---

## Database Schema Reference

### Core Tables

#### atletas
- **Purpose:** Player roster information
- **Key Fields:** id, nome_completo, posicao, numero_camisola, ativo
- **TimescaleDB:** No

#### sessoes
- **Purpose:** Training sessions and games
- **Key Fields:** id, data, tipo, jornada, adversario, resultado
- **TimescaleDB:** No

#### dados_gps
- **Purpose:** GPS tracking data (Catapult)
- **Key Fields:** time, atleta_id, sessao_id, distancia_total, velocidade_max, aceleracoes, desaceleracoes, sprints
- **TimescaleDB:** Yes (hypertable on `time`)

#### dados_pse
- **Purpose:** Perceived Subjective Effort data
- **Key Fields:** time, atleta_id, sessao_id, pse, carga_total, duracao_min
- **TimescaleDB:** Yes (hypertable on `time`)

#### metricas_carga
- **Purpose:** Calculated weekly load metrics
- **Key Fields:** atleta_id, semana_inicio, monotonia, tensao, acwr, nivel_risco_*
- **TimescaleDB:** No

### Materialized View

#### dashboard_principal
- **Purpose:** Pre-aggregated athlete metrics for dashboard
- **Refresh:** Manual or scheduled
- **Source Tables:** atletas, dados_gps, dados_pse, sessoes

---

## Calculation Logic

### Monotony
**Formula:** `mean_load / std_dev_load`
- **Window:** Last 7 workouts
- **Risk Thresholds:**
  - Green: < 1.0
  - Yellow: 1.0 - 2.0
  - Red: > 2.0

### Strain
**Formula:** `weekly_load × monotony`
- **Window:** Current week
- **Risk Thresholds:**
  - Green: < 4000
  - Yellow: 4000 - 6000
  - Red: > 6000

### ACWR (Acute:Chronic Workload Ratio)
**Formula:** `acute_load / chronic_load`
- **Acute Window:** 7 days
- **Chronic Window:** 28 days
- **Risk Thresholds:**
  - Red (Low): < 0.8 (detraining)
  - Green: 0.8 - 1.3 (optimal)
  - Yellow: 1.3 - 1.5 (elevated)
  - Red (High): > 1.5 (overtraining)

### Z-Score
**Formula:** `(value - team_mean) / team_std_dev`
- **Purpose:** Standardize metrics vs. team
- **Interpretation:**
  - -1 to +1: Normal
  - ±1 to ±2: Outside normal
  - Beyond ±2: Extreme outlier

### PSE Load
**Formula:** `PSE × duration_minutes`
- **PSE Scale:** 1-10 (CR-10 Borg Scale)
- **Example:** PSE=7, Duration=90min → Load=630

---

## Frontend Integration

### Dashboard Page
- **Endpoints Used:**
  - `/api/metrics/team/dashboard`
  - `/api/metrics/team/summary`

### Load Monitoring Page
- **Endpoints Used:**
  - `/api/load-metrics/team/overview`
  - `/api/load-metrics/trends`
  - `/api/load-metrics/position-comparison`
  - `/api/load-metrics/weeks`
  - `/api/load-metrics/athlete/{id}/week/{date}/details`

### Game Analysis Page
- **Endpoints Used:**
  - `/api/athletes/` (for player list)
  - `/api/metrics/games/data` (team view)
  - `/api/metrics/games/player/{id}` (individual/comparison)

### Athlete Detail Page (if exists)
- **Endpoints Used:**
  - `/api/athletes/{id}`
  - `/api/athletes/{id}/metrics`

---

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (database/processing error)

---

## Current System Status

### Active Features
✅ GPS data ingestion (Catapult CSV)  
✅ Team dashboard with risk indicators  
✅ Load metrics calculation (Monotony, Strain, ACWR)  
✅ Game-by-game analysis with player comparison  
✅ Individual player tracking  
✅ Week-by-week historical analysis  
✅ Position-based comparison  
✅ Roster verification  
✅ Scientific GPS metrics (accelerations, decelerations, sprints)  

### Planned Features
🔜 PSE data upload interface  
🔜 Real-time dashboard updates  
🔜 Export functionality (PDF reports)  
🔜 Mobile responsive views  
🔜 User authentication  

---

## Performance Notes

### Optimization Strategies
1. **Materialized Views:** `dashboard_principal` for fast dashboard loads
2. **TimescaleDB:** Efficient time-series queries for GPS/PSE data
3. **Indexing:** athlete_id, session_id, time columns
4. **LIMIT Clauses:** All list endpoints have reasonable limits
5. **Aggregation:** Pre-calculated weekly metrics

### Known Limitations
- Historical data queries can be slow with large datasets
- Materialized view requires manual refresh
- No caching layer (could add Redis)
- Single-threaded CSV processing

---

## Maintenance

### Database Refresh Commands
```sql
-- Refresh dashboard view
REFRESH MATERIALIZED VIEW dashboard_principal;

-- Recalculate metrics for a week
-- (requires running metrics_calculator.py)
```

### Backup Strategy
- Daily TimescaleDB snapshots
- CSV export of critical tables
- Version-controlled schema files

---

**Document Version:** 1.0  
**Last Updated:** December 22, 2024  
**Maintainer:** Development Team