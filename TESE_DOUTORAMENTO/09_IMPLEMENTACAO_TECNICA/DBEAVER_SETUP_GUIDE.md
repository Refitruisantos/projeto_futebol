# 🗄️ DBeaver Setup Guide for Football Analytics Database
## Complete Guide to Connect and Explore Your PostgreSQL + TimescaleDB Data

---

## 📋 OVERVIEW

DBeaver is an excellent database management tool that will allow you to:
- Connect to your PostgreSQL + TimescaleDB database
- Browse tables, hypertables, and views
- Execute SQL queries with syntax highlighting
- Visualize data relationships
- Export data in various formats
- Monitor database performance

---

## 🚀 STEP 1: INSTALL DBEAVER

### Download DBeaver Community Edition (Free)
1. Go to https://dbeaver.io/download/
2. Download **DBeaver Community Edition** for Windows
3. Run the installer and follow the setup wizard
4. Launch DBeaver after installation

**Alternative Installation (via winget):**
```powershell
winget install dbeaver.dbeaver
```

---

## 🔌 STEP 2: CREATE DATABASE CONNECTION

### 1. Open Connection Wizard
- Click **"New Database Connection"** (plug icon) in toolbar
- Or go to **Database → New Database Connection**

### 2. Select PostgreSQL Driver
- Choose **PostgreSQL** from the list
- Click **Next**

### 3. Configure Connection Settings

**Main Tab:**
```
Server Host: localhost
Port: 5432
Database: futebol_tese
Username: postgres
Password: [your_postgres_password]
```

**Connection Settings:**
- **Show all databases:** ✅ Checked
- **Connect by URL:** Leave unchecked for now

### 4. Test Connection
- Click **"Test Connection"**
- If successful, you'll see "Connected" message
- If it fails, see troubleshooting section below

### 5. Finish Setup
- Click **Finish** to create the connection
- The connection will appear in the Database Navigator

---

## 🔧 STEP 3: VERIFY CONNECTION PARAMETERS

### Check Your Database Credentials

**Option 1: Check .env file**
```powershell
# Navigate to your project
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# View .env file (if it exists)
type .env
```

**Option 2: Test connection manually**
```powershell
# Test PostgreSQL connection
psql -h localhost -U postgres -d futebol_tese

# If successful, you'll see:
# futebol_tese=#
```

**Option 3: Check if PostgreSQL is running**
```powershell
# Check if PostgreSQL service is running
net start | findstr postgres

# Or check specific service
sc query postgresql-x64-16
```

---

## 🗂️ STEP 4: EXPLORE YOUR DATABASE STRUCTURE

Once connected, you'll see your database structure in DBeaver:

### **Database: futebol_tese**
```
📁 futebol_tese
├── 📁 Schemas
│   └── 📁 public
│       ├── 📁 Tables
│       │   ├── 📊 atletas (28 rows)
│       │   ├── 📊 sessoes (6 rows)
│       │   ├── 📊 dados_gps (72 rows) [HYPERTABLE]
│       │   ├── 📊 dados_pse (105 rows) [HYPERTABLE]
│       │   ├── 📊 testes_fisicos
│       │   ├── 📊 lesoes
│       │   └── 📊 alertas
│       ├── 📁 Views
│       │   └── 📊 dashboard_principal
│       └── 📁 Functions
│           ├── ⚙️ calcular_acwr()
│           ├── ⚙️ calcular_monotonia()
│           └── ⚙️ resumo_atleta()
```

### **Key Tables to Explore:**

1. **`atletas`** - Player profiles and basic information
2. **`sessoes`** - Training sessions and match metadata
3. **`dados_gps`** - GPS performance data (TimescaleDB hypertable)
4. **`dados_pse`** - Wellness and RPE data (TimescaleDB hypertable)

---

## 📊 STEP 5: USEFUL QUERIES TO START WITH

### 1. View All Athletes
```sql
SELECT 
    id,
    jogador_id,
    nome_completo,
    posicao,
    numero_camisola,
    ativo
FROM atletas 
WHERE ativo = true
ORDER BY nome_completo;
```

### 2. Check Database Status
```sql
-- Count records in each main table
SELECT 
    'atletas' as table_name, COUNT(*) as records FROM atletas
UNION ALL
SELECT 
    'sessoes' as table_name, COUNT(*) as records FROM sessoes
UNION ALL
SELECT 
    'dados_gps' as table_name, COUNT(*) as records FROM dados_gps
UNION ALL
SELECT 
    'dados_pse' as table_name, COUNT(*) as records FROM dados_pse;
```

### 3. View Recent GPS Data
```sql
SELECT 
    a.nome_completo,
    s.data as session_date,
    s.tipo as session_type,
    g.distancia_total,
    g.velocidade_max,
    g.player_load
FROM dados_gps g
JOIN atletas a ON g.atleta_id = a.id
JOIN sessoes s ON g.sessao_id = s.id
ORDER BY s.data DESC, g.distancia_total DESC
LIMIT 20;
```

### 4. Check TimescaleDB Hypertables
```sql
-- View hypertable information
SELECT * FROM timescaledb_information.hypertables;

-- View chunks (data partitions)
SELECT 
    hypertable_name,
    chunk_name,
    range_start,
    range_end
FROM timescaledb_information.chunks
ORDER BY hypertable_name, range_start;
```

### 5. Dashboard Summary Query
```sql
-- Team overview metrics
SELECT 
    COUNT(DISTINCT a.id) as total_athletes,
    COUNT(DISTINCT s.id) as total_sessions,
    ROUND(AVG(g.distancia_total), 2) as avg_distance,
    ROUND(AVG(g.player_load), 2) as avg_player_load,
    MAX(s.data) as last_session_date
FROM atletas a
LEFT JOIN dados_gps g ON a.id = g.atleta_id
LEFT JOIN sessoes s ON g.sessao_id = s.id
WHERE a.ativo = true;
```

---

## 🛠️ TROUBLESHOOTING COMMON ISSUES

### Issue 1: "Connection refused" or "Could not connect"

**Possible Causes & Solutions:**

1. **PostgreSQL not running**
   ```powershell
   # Start PostgreSQL service
   net start postgresql-x64-16
   
   # Or if using Docker
   docker start [container_name]
   ```

2. **Wrong port or host**
   - Verify PostgreSQL is running on port 5432
   ```powershell
   netstat -an | findstr :5432
   ```

3. **Firewall blocking connection**
   - Add exception for port 5432 in Windows Firewall

### Issue 2: "Authentication failed"

**Solutions:**
1. **Check password**
   - Verify postgres user password
   ```powershell
   # Reset password if needed
   psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"
   ```

2. **Check pg_hba.conf**
   - Ensure local connections are allowed
   - File location: `C:\Program Files\PostgreSQL\16\data\pg_hba.conf`

### Issue 3: "Database does not exist"

**Solutions:**
1. **Create database if missing**
   ```sql
   -- Connect to postgres database first
   CREATE DATABASE futebol_tese;
   ```

2. **Check database name spelling**
   - Ensure it's exactly `futebol_tese`

### Issue 4: "Driver not found"

**Solutions:**
1. **Download PostgreSQL driver**
   - DBeaver will prompt to download automatically
   - Click "Download" when prompted

2. **Manual driver setup**
   - Go to Database → Driver Manager
   - Find PostgreSQL and ensure it's properly configured

---

## 🎯 STEP 6: ADVANCED DBEAVER FEATURES

### 1. Data Visualization
- Right-click any table → **View Data**
- Use **Charts** tab to create visualizations
- Export charts as images

### 2. Query Execution
- Open **SQL Editor** (Ctrl+])
- Write and execute queries
- Save frequently used queries as bookmarks

### 3. Data Export
- Right-click table → **Export Data**
- Choose format: CSV, Excel, JSON, etc.
- Configure export settings

### 4. Database Diagram
- Right-click schema → **View Diagram**
- Visualize table relationships
- Useful for understanding data structure

### 5. Performance Monitoring
- **Database → Statistics**
- Monitor query execution times
- View connection status

---

## 📈 STEP 7: EXPLORING YOUR FOOTBALL DATA

### Key Data Exploration Queries:

#### 1. Top Performers by Distance
```sql
SELECT 
    a.nome_completo,
    s.data,
    g.distancia_total,
    g.velocidade_max,
    g.effs_25_2_kmh as sprints
FROM dados_gps g
JOIN atletas a ON g.atleta_id = a.id
JOIN sessoes s ON g.sessao_id = s.id
ORDER BY g.distancia_total DESC
LIMIT 10;
```

#### 2. Wellness Trends
```sql
SELECT 
    a.nome_completo,
    p.time::date as date,
    p.pse,
    p.qualidade_sono,
    p.stress,
    p.fadiga,
    p.carga_total
FROM dados_pse p
JOIN atletas a ON p.atleta_id = a.id
ORDER BY p.time DESC;
```

#### 3. Session Participation
```sql
SELECT 
    s.data,
    s.tipo,
    s.jornada,
    COUNT(g.atleta_id) as participants,
    ROUND(AVG(g.distancia_total), 2) as avg_distance
FROM sessoes s
LEFT JOIN dados_gps g ON s.id = g.sessao_id
GROUP BY s.id, s.data, s.tipo, s.jornada
ORDER BY s.data DESC;
```

#### 4. Player Load Analysis
```sql
SELECT 
    a.nome_completo,
    COUNT(g.id) as sessions_played,
    ROUND(AVG(g.player_load), 2) as avg_load,
    ROUND(SUM(g.distancia_total), 2) as total_distance
FROM atletas a
LEFT JOIN dados_gps g ON a.id = g.atleta_id
WHERE a.ativo = true
GROUP BY a.id, a.nome_completo
HAVING COUNT(g.id) > 0
ORDER BY avg_load DESC;
```

---

## 🔍 STEP 8: TIMESCALEDB SPECIFIC FEATURES

### 1. Hypertable Information
```sql
-- View hypertable details
SELECT 
    hypertable_name,
    owner,
    num_dimensions,
    num_chunks,
    compression_enabled,
    tablespace
FROM timescaledb_information.hypertables;
```

### 2. Chunk Information
```sql
-- View data chunks (partitions)
SELECT 
    chunk_schema,
    chunk_name,
    hypertable_name,
    range_start,
    range_end,
    is_compressed
FROM timescaledb_information.chunks
ORDER BY hypertable_name, range_start;
```

### 3. Compression Stats
```sql
-- View compression statistics
SELECT 
    hypertable_name,
    compression_status,
    uncompressed_heap_size,
    uncompressed_index_size,
    compressed_heap_size,
    compressed_index_size
FROM timescaledb_information.hypertable_compression_stats;
```

---

## 💡 TIPS FOR EFFECTIVE DATABASE EXPLORATION

### 1. **Use Bookmarks**
- Save frequently used queries as bookmarks
- Organize them in folders by category

### 2. **Enable Auto-completion**
- Go to Preferences → SQL Editor
- Enable "Auto-completion" and "Auto-format"

### 3. **Use Result Filters**
- Right-click column headers to add filters
- Sort and filter data without writing WHERE clauses

### 4. **Export Results**
- Right-click query results → Export
- Save analysis results for presentations

### 5. **Monitor Performance**
- Check query execution times
- Use EXPLAIN ANALYZE for slow queries

---

## 🚨 SECURITY BEST PRACTICES

### 1. **Connection Security**
- Use strong passwords
- Consider SSL connections for production
- Limit connection permissions

### 2. **Query Safety**
- Be careful with UPDATE/DELETE queries
- Use transactions for data modifications
- Always backup before major changes

### 3. **Access Control**
- Create read-only users for analysis
- Limit access to sensitive data
- Use database roles appropriately

---

## 📞 GETTING HELP

### If You Still Have Connection Issues:

1. **Check Project Documentation**
   - Review `PROJECT_MASTER_GUIDE.md`
   - Check `ARCHITECTURE.md` for database details

2. **Verify Database Status**
   ```powershell
   # Test direct connection
   psql -h localhost -U postgres -d futebol_tese -c "SELECT version();"
   ```

3. **Check Backend Connection**
   - Ensure your FastAPI backend can connect
   - Review backend logs for connection errors

4. **DBeaver Logs**
   - Help → Open Log File
   - Check for specific error messages

---

## ✅ SUCCESS CHECKLIST

- [ ] DBeaver installed and launched
- [ ] PostgreSQL connection created
- [ ] Connection test successful
- [ ] Can see `futebol_tese` database
- [ ] Tables visible (atletas, sessoes, dados_gps, dados_pse)
- [ ] Can execute basic queries
- [ ] TimescaleDB hypertables recognized
- [ ] Sample data queries working

Once you complete this checklist, you'll have full database access through DBeaver's powerful interface!

---

**Next Steps:** Start exploring your football analytics data with the provided queries and use DBeaver's visualization features to create charts and reports for your presentation.
