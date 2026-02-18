# 🎯 FOOTBALL ANALYTICS SYSTEM - MASTER PROJECT GUIDE

**Complete documentation for the Football Performance Monitoring & Analytics Platform**

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [Data Sources & Import](#data-sources--import)
5. [Backend API](#backend-api)
6. [Frontend Application](#frontend-application)
7. [Setup & Installation](#setup--installation)
8. [Data Flow](#data-flow)
9. [File Structure](#file-structure)
10. [Scripts Reference](#scripts-reference)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 PROJECT OVERVIEW

### Purpose
Monitor football player performance using GPS tracking data from Catapult devices and subjective wellness metrics (PSE) to optimize training loads and prevent injuries.

### Technologies
- **Database:** PostgreSQL 16 + TimescaleDB 2.15
- **Backend:** FastAPI (Python 3.11+)
- **Frontend:** React + Vite + TailwindCSS
- **Data Processing:** pandas, psycopg2

### Key Features
- ✅ GPS data ingestion from Catapult CSV exports
- ✅ PSE (Perceived Subjective Exertion) and wellness tracking
- ✅ Time-series data storage with TimescaleDB hypertables
- ✅ Real-time performance dashboards
- ✅ Athlete profiles with historical metrics
- ✅ Session management and analysis

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│  - Catapult GPS CSV files (dadoscatapult/)                  │
│  - PSE Wellness CSV files (dadosPSE/)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Import Scripts
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL + TIMESCALEDB                        │
│  - atletas (athletes table)                                 │
│  - sessoes (training sessions)                              │
│  - dados_gps (GPS hypertable)                               │
│  - dados_pse (PSE hypertable)                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ SQL Queries
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  Port: 8000                                                  │
│  Routes: /api/athletes, /api/sessions, /api/metrics        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ REST API (JSON)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  REACT FRONTEND                              │
│  Port: 5173                                                  │
│  Pages: Dashboard, Athletes, Sessions                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ DATABASE SCHEMA

### Core Tables

#### `atletas` (Athletes)
```sql
id SERIAL PRIMARY KEY
jogador_id VARCHAR(50) UNIQUE
nome_completo VARCHAR(100)
data_nascimento DATE
posicao VARCHAR(5)         -- GR, DC, DL, MC, EX, AV
numero_camisola INTEGER
altura_cm INTEGER
massa_kg NUMERIC(5,2)
ativo BOOLEAN
```

#### `sessoes` (Training Sessions)
```sql
id SERIAL PRIMARY KEY
data DATE
tipo VARCHAR(20)           -- treino, jogo, amigavel
local VARCHAR(20)          -- casa, fora
jornada INTEGER
duracao_min INTEGER
```

### TimescaleDB Hypertables

#### `dados_gps` (GPS Data)
```sql
time TIMESTAMP             -- Hypertable partition key
atleta_id INTEGER          -- FK to atletas
sessao_id INTEGER          -- FK to sessoes

-- Catapult Metrics (9 columns from CSV)
distancia_total FLOAT      -- total_distance_m
velocidade_max FLOAT       -- max_velocity_kmh
aceleracoes INTEGER        -- acc_b1_3_total_efforts
desaceleracoes INTEGER     -- decel_b1_3_total_efforts
effs_19_8_kmh INTEGER      -- efforts_over_19_8_kmh
dist_19_8_kmh FLOAT        -- distance_over_19_8_kmh
effs_25_2_kmh INTEGER      -- efforts_over_25_2_kmh (sprints)
tot_effs_gen2 INTEGER      -- velocity_b3_plus_total_efforts
```

#### `dados_pse` (PSE/Wellness Data)
```sql
time TIMESTAMP             -- Hypertable partition key
atleta_id INTEGER          -- FK to atletas
sessao_id INTEGER          -- FK to sessoes

-- PSE Metrics
pse FLOAT                  -- RPE score (1-10)
duracao_min INTEGER        -- Session duration
carga_total FLOAT          -- Training load (RPE × duration)

-- Wellness Metrics (1-5 scale)
qualidade_sono INTEGER     -- Sleep quality
stress INTEGER             -- Stress level
fadiga INTEGER             -- Fatigue
dor_muscular INTEGER       -- DOMS (muscle soreness)
```

---

## � DATA TRANSFORMATION

### Wide to Long Format Conversion

**Problem:** Performance data from Excel often comes in wide format (one column per session), which is not suitable for relational databases.

**Solution:** Use `scripts/transform_wide_to_long.py` to convert to long format (one row per athlete-session).

**Example:**
```powershell
# Transform Excel file with multiple sessions
python scripts\transform_wide_to_long.py performance_data.xlsx

# Output: performance_data_long.csv (ready for database import)
```

**Detailed Guide:** See `DATA_TRANSFORMATION_GUIDE.md` for complete documentation.

---

## �📊 DATA SOURCES & IMPORT

### GPS Data (Catapult)

**Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadoscatapult\`

**Files:**
- `jornada_1_players_en_snake_case.csv`
- `jornada_2_players_en_snake_case.csv`
- `jornada_3_players_en_snake_case.csv`
- `jornada_4_players_en_snake_case.csv`
- `jornada_5_players_en_snake_case.csv`

**CSV Structure:**
```
player,total_distance_m,max_velocity_kmh,acc_b1_3_total_efforts,decel_b1_3_total_efforts,
efforts_over_19_8_kmh,distance_over_19_8_kmh,efforts_over_25_2_kmh,velocity_b3_plus_total_efforts
```

**Import Script:** `scripts/insert_catapult_data.py`

**Key Features:**
- Name mapping (Catapult full names → Database short names)
- Position code translation (LAT→DL, MED→MC, EXT→EX)
- Case-insensitive athlete matching
- Automatic session creation/matching

**Run:**
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA
python scripts\insert_catapult_data.py
```

---

### PSE/Wellness Data

**Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\dadosPSE\`

**Files:**
- `Jogo1_pse.csv`
- `jogo2_pse.csv`
- `jogo3_pse.csv`
- `jogo4_pse.csv`
- `jogo5_pse.csv`

**CSV Structure (from Excel):**
```
Nome,Pos,Sono,Stress,Fadiga,DOMS,DORES MUSCULARES,VOLUME,Rpe,CARGA
```

**Column Extraction (by index):**
- `row.iloc[0]` = Nome (Athlete name)
- `row.iloc[2]` = Sono (Sleep 1-10, scaled to 1-5)
- `row.iloc[3]` = Stress (1-10, scaled to 1-5)
- `row.iloc[4]` = Fadiga (Fatigue 1-5)
- `row.iloc[5]` = DOMS (Muscle soreness 1-5)
- `row.iloc[8]` = VOLUME (Duration in minutes)
- `row.iloc[9]` = Rpe (RPE 1-10)
- `row.iloc[10]` = CARGA (Training load)

**Import Script:** `scripts/insert_pse_data.py`

**Key Features:**
- Wellness scale conversion (1-10 → 1-5)
- Athlete name mapping
- Session matching by date
- Automatic load calculation (RPE × Duration)

**Run:**
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA
python scripts\insert_pse_data.py
```

---

## 🔌 BACKEND API

**Location:** `backend/`

**Framework:** FastAPI with uvicorn server

### API Endpoints

#### Athletes
- `GET /api/athletes/` - List all athletes
- `GET /api/athletes/{id}` - Get athlete details
- `GET /api/athletes/{id}/metrics?days=365` - Get athlete metrics & sessions

#### Sessions
- `GET /api/sessions/` - List all training sessions
- `GET /api/sessions/{id}` - Get session details with participant data

#### Metrics
- `GET /api/metrics/team/dashboard` - Team overview metrics
- `GET /api/metrics/team/summary` - Team summary statistics

### Database Connection

**File:** `backend/database.py`

**Environment Variables (.env):**
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=futebol_tese
DB_USER=postgres
DB_PASSWORD=your_password
```

**Connection Pooling:** psycopg2.pool.SimpleConnectionPool (1-10 connections)

### Start Backend

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend

uvicorn main:app --reload
```

**Verify:** http://localhost:8000/docs (Swagger UI)

---

## 🎨 FRONTEND APPLICATION

**Location:** `frontend/`

**Framework:** React 18 + Vite + TailwindCSS

### Pages

#### Dashboard (`/`)
- Team overview cards
- Top performers by distance
- At-risk athletes (high load indicators)

#### Athletes (`/athletes`)
- List of all athletes with search/filter
- Click athlete → detailed profile page
- Shows GPS + PSE metrics
- Recent session history

#### Sessions (`/sessions`)
- Chronological list of training sessions
- Session type, date, jornada
- Link to detailed session view

### Components

**Location:** `frontend/src/components/`

- `Layout.jsx` - Main app layout with navigation
- `StatCard.jsx` - Dashboard metric cards
- `AthleteCard.jsx` - Athlete list item
- `SessionCard.jsx` - Session list item

### API Client

**File:** `frontend/src/services/client.js`

```javascript
const API_BASE = 'http://localhost:8000/api';

export const getAthletes = () => axios.get(`${API_BASE}/athletes/`);
export const getAthlete = (id) => axios.get(`${API_BASE}/athletes/${id}`);
export const getMetrics = (id, days) => 
  axios.get(`${API_BASE}/athletes/${id}/metrics?days=${days}`);
```

### Start Frontend

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend

npm run dev
```

**Access:** http://localhost:5173

---

## ⚙️ SETUP & INSTALLATION

### 1. Database Setup

```powershell
# Start PostgreSQL service
net start postgresql-x64-16

# Create database
psql -U postgres
CREATE DATABASE futebol_tese;
\c futebol_tese
CREATE EXTENSION IF NOT EXISTS timescaledb;
\q

# Run schema creation
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA
psql -U postgres -d futebol_tese -f sql\01_criar_schema.sql
psql -U postgres -d futebol_tese -f sql\02_criar_hypertables.sql
psql -U postgres -d futebol_tese -f sql\03_indices.sql
```

### 2. Backend Setup

```powershell
cd backend

# Create virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary python-dotenv pandas

# Create .env file
echo "DB_HOST=localhost" > .env
echo "DB_PORT=5432" >> .env
echo "DB_NAME=futebol_tese" >> .env
echo "DB_USER=postgres" >> .env
echo "DB_PASSWORD=your_password" >> .env

# Start server
uvicorn main:app --reload
```

### 3. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Data Import

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Import athlete data
python scripts\insert_athletes.py

# Import GPS data from Catapult
python scripts\insert_catapult_data.py

# Import PSE wellness data
python scripts\insert_pse_data.py

# Verify data
python scripts\check_database.py
python scripts\verify_gps_columns.py
python scripts\verify_pse_data.py
```

---

## 🔄 DATA FLOW

### Complete Import Process

```
1. CSV FILES
   ├─ dadoscatapult/*.csv (GPS data)
   └─ dadosPSE/*.csv (PSE data)
          ↓
2. IMPORT SCRIPTS
   ├─ insert_catapult_data.py
   │  ├─ Read CSV with pandas
   │  ├─ Map player names
   │  ├─ Create/find session
   │  └─ Insert into dados_gps
   │
   └─ insert_pse_data.py
      ├─ Read CSV with pandas
      ├─ Map player names
      ├─ Scale wellness values
      └─ Insert into dados_pse
          ↓
3. POSTGRESQL + TIMESCALEDB
   ├─ atletas (28 athletes)
   ├─ sessoes (6 sessions)
   ├─ dados_gps (72 records) [HYPERTABLE]
   └─ dados_pse (105 records) [HYPERTABLE]
          ↓
4. FASTAPI BACKEND (Port 8000)
   ├─ Query database
   ├─ Calculate aggregations
   └─ Return JSON responses
          ↓
5. REACT FRONTEND (Port 5173)
   ├─ Fetch from API
   ├─ Display in UI
   └─ User interactions
```

---

## 📁 FILE STRUCTURE

```
09_IMPLEMENTACAO_TECNICA/
│
├── backend/                      # FastAPI Backend
│   ├── main.py                  # App entry point, CORS config
│   ├── database.py              # DB connection management
│   └── routers/
│       ├── athletes.py          # Athlete endpoints
│       ├── sessions.py          # Session endpoints
│       ├── metrics.py           # Metrics/dashboard endpoints
│       └── ingestion.py         # Data ingestion endpoints
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   └── services/
│   │       └── client.js        # API client
│   ├── package.json
│   └── vite.config.js
│
├── python/                       # Shared Python utilities
│   └── 01_conexao_db.py         # DatabaseConnection class
│
├── scripts/                      # Data import scripts
│   ├── insert_athletes.py       # Manual athlete insertion
│   ├── insert_catapult_data.py  # GPS data import ⭐
│   ├── insert_pse_data.py       # PSE data import ⭐
│   ├── check_database.py        # Data verification
│   ├── verify_gps_columns.py    # GPS data check
│   └── verify_pse_data.py       # PSE data check
│
├── sql/                          # Database schema
│   ├── 01_criar_schema.sql      # Create tables
│   ├── 02_criar_hypertables.sql # TimescaleDB setup
│   ├── 03_indices.sql           # Database indexes
│   └── create_dashboard_view.sql # Dashboard view
│
└── PROJECT_MASTER_GUIDE.md       # This file ⭐

External Data Directories:
├── dadoscatapult/               # GPS CSV files (5 jornadas)
└── dadosPSE/                    # PSE CSV files (5 jornadas)
```

---

## 📚 SCRIPTS REFERENCE

### Data Import Scripts

#### `insert_catapult_data.py`
**Purpose:** Import GPS data from Catapult CSV exports

**Key Functions:**
- `parse_catapult_csv(csv_path, session_date, jornada_num)`
  - Reads CSV with pandas
  - Maps athlete names using NAME_MAPPING dictionary
  - Creates session if not exists
  - Inserts all 9 GPS metrics into dados_gps

**Name Mapping:** Lines 44-70
```python
NAME_MAPPING = {
    'Gonálsio Cardoso': 'CARDOSO',
    'JoÃo Ferreira': 'JOÃO FERREIRA',
    'Yordanov Ricrado': 'RICARDO',
    # ... etc
}
```

**Run:**
```bash
python scripts\insert_catapult_data.py
```

---

#### `insert_pse_data.py`
**Purpose:** Import PSE and wellness data from CSV files

**Key Functions:**
- `parse_pse_csv(csv_path, jornada_date)`
  - Reads CSV with semicolon separator
  - Extracts columns by index (iloc[2], iloc[3], etc.)
  - Scales wellness values (1-10 → 1-5)
  - Calculates training load if not provided

**Column Extraction:** Lines 149-159
```python
sono_raw = int(row.iloc[2])      # Sleep (1-10)
sono = int(sono_raw / 2)         # Scale to 1-5
stress_raw = int(row.iloc[3])    # Stress (1-10)
stress = int(stress_raw / 2)     # Scale to 1-5
fadiga = int(row.iloc[4])        # Fatigue (1-5)
doms = int(row.iloc[5])          # DOMS (1-5)
volume = int(row.iloc[8])        # Duration (min)
rpe = int(row.iloc[9])           # RPE (1-10)
carga = int(row.iloc[10])        # Load
```

**Run:**
```bash
python scripts\insert_pse_data.py
```

---

### Verification Scripts

#### `check_database.py`
**Purpose:** Quick database status check

**Checks:**
- Total athletes count
- Total sessions count
- GPS records count
- PSE records count
- Dashboard view existence

**Run:**
```bash
python scripts\check_database.py
```

---

#### `verify_gps_columns.py`
**Purpose:** Verify all 9 GPS columns populated

**Displays:**
- Top 5 athletes by distance with all GPS metrics
- Records per athlete
- Total statistics

**Run:**
```bash
python scripts\verify_gps_columns.py
```

---

#### `verify_pse_data.py`
**Purpose:** Verify PSE and wellness data quality

**Displays:**
- Total PSE records
- Top athletes by record count
- Highest load sessions with wellness metrics
- Combined GPS + PSE availability

**Run:**
```bash
python scripts\verify_pse_data.py
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

#### 1. CORS Errors in Browser Console

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Causes:**
- Multiple backend instances running
- Old backend without CORS fix

**Solution:**
```powershell
# Kill all backend processes
netstat -ano | findstr :8000
taskkill /F /PID <process_id>

# Start only ONE backend instance
cd backend
uvicorn main:app --reload
```

**Verify CORS in `backend/main.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### 2. "Network Error" on Athlete Detail Page

**Symptoms:**
- Athlete profile shows "Sem dados disponíveis"
- Browser console: 500 Internal Server Error

**Causes:**
- Date filter excluding historical data
- Missing athlete metrics query

**Solution:**
Check `backend/routers/athletes.py` line 47:
```python
days: int = 365,  # Should be large to show all data
```

Also verify backend logs for SQL errors.

---

#### 3. No Data in Dashboard

**Symptoms:**
- Dashboard shows empty or zero values

**Causes:**
- Data not imported
- Dashboard view missing
- Date filter issues

**Solution:**
```powershell
# 1. Verify data exists
python scripts\check_database.py

# 2. Check if data was imported
psql -U postgres -d futebol_tese
SELECT COUNT(*) FROM dados_gps;
SELECT COUNT(*) FROM dados_pse;

# 3. Recreate dashboard view if needed
psql -U postgres -d futebol_tese -f sql\create_dashboard_view.sql
```

---

#### 4. Athlete Names Not Matching

**Symptoms:**
- Import script shows "Player not found" errors
- Some athletes missing GPS/PSE data

**Causes:**
- Name mismatch between CSV and database
- Missing entry in NAME_MAPPING

**Solution:**
Edit NAME_MAPPING in scripts:
- `insert_catapult_data.py` lines 44-70
- `insert_pse_data.py` lines 34-68

Add mappings like:
```python
NAME_MAPPING = {
    'CSV Name': 'DATABASE NAME',
    'Gonálsio Cardoso': 'CARDOSO',
}
```

---

#### 5. Database Connection Errors

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```powershell
# 1. Check PostgreSQL service
net start postgresql-x64-16

# 2. Verify .env file in backend/
DB_HOST=localhost
DB_PORT=5432
DB_NAME=futebol_tese
DB_USER=postgres
DB_PASSWORD=<your_password>

# 3. Test connection
psql -U postgres -d futebol_tese
```

---

#### 6. Frontend Won't Start

**Symptoms:**
```
npm ERR! code ELIFECYCLE
```

**Solution:**
```powershell
cd frontend

# Clear cache and reinstall
rm -rf node_modules
rm package-lock.json
npm install

# Try again
npm run dev
```

---

### Data Validation Queries

**Check athlete count:**
```sql
SELECT COUNT(*) FROM atletas WHERE ativo = TRUE;
-- Expected: 28
```

**Check GPS data:**
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT atleta_id) as unique_athletes,
    COUNT(DISTINCT sessao_id) as unique_sessions
FROM dados_gps;
-- Expected: 72 records, 18 athletes, 5 sessions
```

**Check PSE data:**
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT atleta_id) as unique_athletes
FROM dados_pse;
-- Expected: 105 records, ~18 athletes
```

**Athletes with complete data:**
```sql
SELECT 
    a.nome_completo,
    COUNT(DISTINCT g.sessao_id) as gps_sessions,
    COUNT(DISTINCT p.sessao_id) as pse_sessions
FROM atletas a
LEFT JOIN dados_gps g ON g.atleta_id = a.id
LEFT JOIN dados_pse p ON p.atleta_id = a.id
GROUP BY a.id, a.nome_completo
ORDER BY gps_sessions DESC;
```

---

## 🚀 QUICK START CHECKLIST

- [ ] PostgreSQL + TimescaleDB installed and running
- [ ] Database `futebol_tese` created
- [ ] Schema SQL files executed
- [ ] Athlete data inserted (28 athletes)
- [ ] GPS data imported (72 records from 5 jornadas)
- [ ] PSE data imported (105 records from 5 jornadas)
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Dashboard loads without errors
- [ ] Athlete profiles show metrics and sessions
- [ ] Sessions page displays all 6 sessions

---

## 📞 SUPPORT & REFERENCES

### Key Files to Check First
1. `backend/main.py` - CORS configuration
2. `backend/routers/athletes.py` - Athlete endpoints
3. `scripts/insert_catapult_data.py` - GPS import
4. `scripts/insert_pse_data.py` - PSE import
5. `sql/01_criar_schema.sql` - Database structure

### Useful Commands

**Check running processes:**
```powershell
netstat -ano | findstr :8000  # Backend
netstat -ano | findstr :5173  # Frontend
```

**Database backup:**
```powershell
pg_dump -U postgres futebol_tese > backup.sql
```

**Database restore:**
```powershell
psql -U postgres futebol_tese < backup.sql
```

---

## 📊 PROJECT STATUS

### Current Implementation
✅ Database schema with TimescaleDB hypertables  
✅ GPS data import (9 Catapult metrics)  
✅ PSE/Wellness data import  
✅ Backend API with CORS support  
✅ React frontend with dashboard  
✅ Athlete profile pages  
✅ Session management  

### Data Loaded
- **28 athletes** registered
- **6 training sessions** (5 jornadas + 1 test)
- **72 GPS records** with complete metrics
- **105 PSE records** with wellness data
- **18 athletes** with performance data

### Known Limitations
- 7-day load calculations require more frequent data
- Dashboard calculations manual (no automated ACWR yet)
- 10 athletes have no GPS data (didn't participate in loaded jornadas)
- Some athletes missing from PSE files (MÁRIO, AVELAR, etc.)

---

**Last Updated:** December 20, 2025  
**Version:** 1.0  
**Author:** Cascade AI Assistant

---

_For questions or issues, check the Troubleshooting section above or review the backend logs._
