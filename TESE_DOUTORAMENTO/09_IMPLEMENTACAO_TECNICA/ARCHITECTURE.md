# Sistema de Análise de Dados GPS - Arquitetura Completa

## 📊 Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Coach/Physio)                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER (http://localhost:5173)               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         React Frontend (Vite)                              │  │
│  │  - Dashboard, Athletes, Sessions, Upload pages             │  │
│  │  - TailwindCSS styling, Axios HTTP client                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP/JSON REST API
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (http://localhost:8000)             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Routers:                                                  │  │
│  │  - /api/athletes/     (list, detail, metrics)             │  │
│  │  - /api/sessions/     (list, detail with GPS)             │  │
│  │  - /api/metrics/      (dashboard, summaries)              │  │
│  │  - /api/ingest/       (CSV upload, history)               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  database.py → DatabaseConnection wrapper                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ SQL Queries (psycopg2)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│         PostgreSQL + TimescaleDB (localhost:5432)                │
│                    Database: futebol_tese                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Tables (Relational):                                      │  │
│  │  - atletas           (28 players, profile data)            │  │
│  │  - sessoes           (training/matches metadata)           │  │
│  │  - testes_fisicos    (physical tests)                      │  │
│  │  - lesoes            (injuries)                            │  │
│  │  - alertas           (alerts/warnings)                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Hypertables (TimescaleDB time-series):                   │  │
│  │  - dados_gps         (GPS metrics per player/session)     │  │
│  │  - dados_pse         (wellness/RPE data)                  │  │
│  │  - contexto_competitivo (match context data)              │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Views & Functions:                                        │  │
│  │  - dashboard_principal    (team overview)                 │  │
│  │  - resumo_atleta()        (athlete summary)               │  │
│  │  - atletas_em_risco()     (ACWR risk detection)           │  │
│  │  - calcular_acwr()        (acute:chronic workload ratio)  │  │
│  │  - calcular_monotonia()   (training monotony)             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Runs in Docker container
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Container (optional)                   │
│  - timescale/timescaledb:latest-pg15                             │
│  - Persistent data volume                                        │
│  - Port mapping: 5432:5432                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: From CSV to Visualization

### 1. **Database Setup (One-time)**

```powershell
# Run SQL scripts in order:
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

psql -h localhost -U postgres -d futebol_tese -f sql/01_criar_schema.sql
psql -h localhost -U postgres -d futebol_tese -f sql/02_criar_hypertables.sql
psql -h localhost -U postgres -d futebol_tese -f sql/03_indices_otimizacao.sql
psql -h localhost -U postgres -d futebol_tese -f sql/04_continuous_aggregates.sql
psql -h localhost -U postgres -d futebol_tese -f sql/05_funcoes_auxiliares.sql
psql -h localhost -U postgres -d futebol_tese -f sql/06_politicas_compressao.sql
```

**What happens:**
- Creates tables (`atletas`, `sessoes`, etc.)
- Converts `dados_gps`, `dados_pse`, `contexto_competitivo` to hypertables (time-series optimized)
- Creates indexes for fast queries
- Creates continuous aggregates (pre-computed daily/weekly summaries)
- Creates functions for ACWR, monotony, z-scores
- Sets up compression policies

### 2. **Populate Athletes Table**

```powershell
# Option A: Use Python script (if exists)
python python/insert_athletes.py

# Option B: Manual SQL
psql -h localhost -U postgres -d futebol_tese
\COPY atletas(jogador_id, nome_completo, data_nascimento, posicao, numero_camisola, pe_dominante, altura_cm, massa_kg) 
FROM 'C:/Users/sorai/CascadeProjects/projeto_futebol/atletas_28_definitivos.csv' 
DELIMITER ',' CSV HEADER;
```

**What happens:**
- Loads 28 athlete profiles into `atletas` table
- These names are used for matching during CSV upload

### 3. **Start Backend & Frontend**

**Terminal 1 - Backend:**
```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

**What happens:**
- FastAPI loads `database.py` → connects to PostgreSQL via psycopg2
- Reads `.env` for DB credentials (host, port, user, password)
- Exposes REST API endpoints on port 8000
- React app starts on port 5173, proxies `/api/*` requests to backend

### 4. **Upload Catapult CSV**

**Via Web UI:**
1. Open http://localhost:5173
2. Go to **Upload** page
3. Select CSV file (e.g., `jornada_1_players_en_snake_case.csv`)
4. Set jornada number (1, 2, 3...)
5. Click "Carregar"

**What happens behind the scenes:**

```
User clicks Upload
      │
      ▼
Frontend: POST /api/ingest/catapult (FormData with file)
      │
      ▼
Backend: ingestion.py router receives file
      │
      ├──> Read CSV with pandas
      ├──> Check required columns (player, total_distance_m, max_velocity_kmh)
      ├──> Create/get session in sessoes table
      │    └──> INSERT INTO sessoes (data, tipo='jogo', jornada=X)
      │
      ├──> For each row in CSV:
      │    ├──> Match player name to atletas table
      │    │    ├──> Try exact match (LOWER(nome_completo))
      │    │    └──> If not found, try fuzzy match (similarity())
      │    │
      │    └──> INSERT INTO dados_gps
      │         (time, atleta_id, sessao_id, distancia_total, velocidade_max, ...)
      │         ON CONFLICT DO NOTHING (prevents duplicates)
      │
      └──> Return success response (inserted count, errors)
```

### 5. **View Data in Frontend**

**Dashboard Page (`/`):**
```
User opens Dashboard
      │
      ▼
Frontend: GET /api/metrics/team/summary
          GET /api/metrics/team/dashboard
      │
      ▼
Backend: metrics.py router
      │
      ├──> Query: SELECT * FROM dashboard_principal
      ├──> Query: SELECT athletes with highest load (7d)
      └──> Query: SELECT * FROM atletas_em_risco(NOW(), 1.5)
      │
      ▼
PostgreSQL: Executes queries
      │
      ├──> dashboard_principal view aggregates GPS/PSE data per athlete
      ├──> Calculates avg player load, distance from dados_gps hypertable
      └──> atletas_em_risco() function calculates ACWR for each athlete
      │
      ▼
Backend: Returns JSON to frontend
      │
      ▼
Frontend: Renders cards with:
      - Total athletes
      - Sessions (7d)
      - Avg player load
      - At-risk athletes (ACWR > 1.5)
```

**Athletes Page (`/athletes`):**
```
Frontend: GET /api/athletes/
      │
      ▼
Backend: SELECT * FROM atletas WHERE ativo = TRUE
      │
      ▼
Frontend: Renders table with all athletes
```

**Athlete Detail Page (`/athletes/:id`):**
```
Frontend: GET /api/athletes/{id}
          GET /api/athletes/{id}/metrics
      │
      ▼
Backend: 
      ├──> SELECT * FROM atletas WHERE id = X
      ├──> SELECT * FROM resumo_atleta(X, NOW())  ← calls SQL function
      └──> SELECT recent sessions from dados_gps JOIN sessoes
      │
      ▼
Frontend: Shows athlete profile + metrics (7/14/28d) + recent sessions
```

**Sessions Page (`/sessions`):**
```
Frontend: GET /api/sessions/
      │
      ▼
Backend: SELECT * FROM sessoes ORDER BY data DESC LIMIT 50
      │
      ▼
Frontend: Table of all training/match sessions
```

**Session Detail Page (`/sessions/:id`):**
```
Frontend: GET /api/sessions/{id}
      │
      ▼
Backend:
      ├──> SELECT * FROM sessoes WHERE id = X
      └──> SELECT g.*, a.nome_completo FROM dados_gps g
           JOIN atletas a ON g.atleta_id = a.id
           WHERE g.sessao_id = X
      │
      ▼
Frontend: Shows session metadata + GPS data table for all players
```

---

## 🔍 How to View Data (Multiple Ways)

### 1. **Web UI (Best for staff)**
- Open http://localhost:5173
- Navigate between Dashboard/Athletes/Sessions/Upload
- Visual, user-friendly, no SQL knowledge needed

### 2. **API Swagger Docs (Best for testing)**
- Open http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly in browser
- See JSON responses

### 3. **Direct Database Queries (Best for analysis)**

```powershell
# Connect to database
psql -h localhost -U postgres -d futebol_tese

# View athletes
SELECT * FROM atletas;

# View sessions
SELECT * FROM sessoes ORDER BY data DESC;

# View GPS data for a session
SELECT 
    a.nome_completo,
    g.distancia_total,
    g.velocidade_max,
    g.player_load
FROM dados_gps g
JOIN atletas a ON g.atleta_id = a.id
WHERE g.sessao_id = 1;

# Check dashboard view
SELECT * FROM dashboard_principal;

# Calculate ACWR for athlete #5
SELECT * FROM resumo_atleta(5, NOW());

# Find at-risk athletes
SELECT * FROM atletas_em_risco(NOW(), 1.5);
```

### 4. **Python Scripts (Best for custom analysis)**

```python
import sys
sys.path.append('python')
from conexao_db import DatabaseConnection

db = DatabaseConnection()

# Get all athletes
athletes = db.query_to_dataframe("SELECT * FROM atletas")
print(athletes)

# Get GPS data for last 7 days
gps = db.query_to_dataframe("""
    SELECT * FROM dados_gps 
    WHERE time >= NOW() - INTERVAL '7 days'
""")
print(gps.describe())

db.close()
```

---

## 🔧 Component Details

### PostgreSQL + TimescaleDB

**Role:** Time-series database for storing and analyzing GPS/PSE data

**Key Features:**
- **Hypertables**: Automatic partitioning by time (1-week chunks)
- **Continuous Aggregates**: Pre-computed daily/weekly summaries
- **Compression**: Older data compressed automatically
- **Functions**: SQL functions for ACWR, monotony, z-scores

**Files:**
- `sql/01_criar_schema.sql` - Tables, indexes, triggers
- `sql/02_criar_hypertables.sql` - Convert to TimescaleDB hypertables
- `sql/05_funcoes_auxiliares.sql` - Analytics functions

### FastAPI Backend

**Role:** REST API between frontend and database

**Key Files:**
- `backend/main.py` - App initialization, CORS, route registration
- `backend/database.py` - DB connection wrapper (uses python/01_conexao_db.py)
- `backend/routers/athletes.py` - Athlete endpoints
- `backend/routers/sessions.py` - Session endpoints
- `backend/routers/metrics.py` - Dashboard/metrics endpoints
- `backend/routers/ingestion.py` - CSV upload with player name matching

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `psycopg2-binary` - PostgreSQL driver
- `pandas` - CSV parsing

### React Frontend

**Role:** User interface for coaches/physios

**Key Files:**
- `frontend/src/App.jsx` - Router setup
- `frontend/src/pages/Dashboard.jsx` - Team overview
- `frontend/src/pages/Athletes.jsx` - Athletes list
- `frontend/src/pages/AthleteDetail.jsx` - Individual athlete
- `frontend/src/pages/Sessions.jsx` - Sessions list
- `frontend/src/pages/SessionDetail.jsx` - Session GPS data
- `frontend/src/pages/Upload.jsx` - CSV upload interface
- `frontend/src/api/client.js` - Axios HTTP client

**Dependencies:**
- `react` + `react-dom` - UI library
- `react-router-dom` - Navigation
- `axios` - HTTP client
- `tailwindcss` - Styling
- `lucide-react` - Icons
- `vite` - Build tool

---

## 🚀 Complete Startup Process

### Every Time You Work:

```powershell
# 1. Ensure PostgreSQL is running
# If using Docker:
docker ps  # Check if container is running
docker start <container_name>  # If stopped

# 2. Start Backend (Terminal 1)
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend
uvicorn main:app --reload

# 3. Start Frontend (Terminal 2)
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend
npm run dev

# 4. Open browser
# http://localhost:5173
```

---

## 🐛 Debugging Data Issues

### No data showing on Dashboard?

```powershell
# Check if functions exist
psql -h localhost -U postgres -d futebol_tese -c "\df"

# If missing, run:
psql -h localhost -U postgres -d futebol_tese -f sql/05_funcoes_auxiliares.sql
```

### Check if athletes exist:

```powershell
psql -h localhost -U postgres -d futebol_tese -c "SELECT COUNT(*) FROM atletas;"
```

### Check if GPS data exists:

```powershell
psql -h localhost -U postgres -d futebol_tese -c "SELECT COUNT(*) FROM dados_gps;"
```

### View backend logs:

Look at the terminal running `uvicorn` - all SQL queries and errors appear there.

### View frontend errors:

Press **F12** in browser → **Console** tab

---

## 📦 Summary

1. **PostgreSQL** stores all data (athletes, sessions, GPS, PSE)
2. **TimescaleDB** optimizes time-series queries on `dados_gps`
3. **FastAPI** exposes REST API for CRUD operations
4. **React** provides user-friendly web interface
5. **Data flows**: CSV → Backend (parse/validate) → PostgreSQL → Backend (query) → Frontend (display)

All components connect via **standard protocols**: SQL, HTTP/JSON, WebSockets (future).
