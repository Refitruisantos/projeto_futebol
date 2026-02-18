# 📊 SIMULATION DATA IMPORT GUIDE
## Complete Week of Football Analytics Data - Ready for Testing

---

## 🗂️ GENERATED FILES OVERVIEW

### **GPS Data Files (6 sessions):**
```
simulation_data/
├── jornada_6_monday_recovery.csv      # Recovery training
├── jornada_6_tuesday_technical.csv    # Technical training
├── jornada_6_wednesday_tactical.csv   # Tactical training
├── jornada_6_thursday_physical.csv    # Physical training
├── jornada_6_friday_prematch.csv      # Pre-match activation
└── jornada_6_saturday_match.csv       # Match vs FC Médio
```

### **PSE/Wellness Data Files (6 sessions):**
```
simulation_data/
├── Jogo6_monday_pse.csv      # Recovery wellness
├── Jogo6_tuesday_pse.csv     # Technical wellness
├── Jogo6_wednesday_pse.csv   # Tactical wellness
├── Jogo6_thursday_pse.csv    # Physical wellness
├── Jogo6_friday_pse.csv      # Pre-match wellness
└── Jogo6_saturday_pse.csv    # Match wellness
```

### **Session Metadata:**
```
simulation_data/
└── session_metadata.csv     # Session details and context
```

---

## 🚀 IMPORT PROCESS

### **Step 1: Import GPS Data**

Use your existing Catapult import script for each session:

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Monday - Recovery Training
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_monday_recovery.csv" --date "2025-01-20" --jornada 6 --type "treino"

# Tuesday - Technical Training
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_tuesday_technical.csv" --date "2025-01-21" --jornada 6 --type "treino"

# Wednesday - Tactical Training
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_wednesday_tactical.csv" --date "2025-01-22" --jornada 6 --type "treino"

# Thursday - Physical Training
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_thursday_physical.csv" --date "2025-01-23" --jornada 6 --type "treino"

# Friday - Pre-Match Training
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_friday_prematch.csv" --date "2025-01-24" --jornada 6 --type "treino"

# Saturday - Match
python scripts\insert_catapult_data.py --file "simulation_data\jornada_6_saturday_match.csv" --date "2025-01-25" --jornada 6 --type "jogo"
```

### **Step 2: Import PSE Data**

Use your existing PSE import script for each session:

```powershell
# Monday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_monday_pse.csv" --date "2025-01-20"

# Tuesday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_tuesday_pse.csv" --date "2025-01-21"

# Wednesday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_wednesday_pse.csv" --date "2025-01-22"

# Thursday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_thursday_pse.csv" --date "2025-01-23"

# Friday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_friday_pse.csv" --date "2025-01-24"

# Saturday PSE
python scripts\insert_pse_data.py --file "simulation_data\Jogo6_saturday_pse.csv" --date "2025-01-25"
```

---

## 📈 EXPECTED DATA PATTERNS

### **GPS Progression Through Week:**
- **Monday:** Low intensity recovery (avg 6,200m)
- **Tuesday:** Technical focus (avg 7,150m)
- **Wednesday:** Tactical intensity (avg 8,200m)
- **Thursday:** Peak physical (avg 9,400m)
- **Friday:** Light activation (avg 4,800m)
- **Saturday:** Match intensity (avg 10,800m)

### **PSE/Wellness Patterns:**
- **Monday:** Good recovery (RPE 4-5, low fatigue)
- **Tuesday:** Moderate load (RPE 5-6, increasing fatigue)
- **Wednesday:** High tactical stress (RPE 6-7, peak fatigue)
- **Thursday:** Maximum physical stress (RPE 7-8, high DOMS)
- **Friday:** Recovery signs (RPE 3-4, pre-match nerves)
- **Saturday:** Match stress (RPE 8-9, high intensity)

### **Player Categories:**
- **Starters (15 players):** Higher metrics, more consistent
- **Rotation (8 players):** Moderate metrics, good training
- **Bench/Youth (5 players):** Lower metrics, development focus

---

## 🔍 DATA VALIDATION QUERIES

### **Check Import Success:**
```sql
-- Verify GPS data imported
SELECT 
    s.data,
    s.tipo,
    COUNT(g.id) as gps_records,
    ROUND(AVG(g.distancia_total), 0) as avg_distance,
    ROUND(AVG(g.velocidade_max), 1) as avg_max_speed
FROM sessoes s
LEFT JOIN dados_gps g ON s.id = g.sessao_id
WHERE s.jornada = 6
GROUP BY s.id, s.data, s.tipo
ORDER BY s.data;

-- Verify PSE data imported
SELECT 
    s.data,
    s.tipo,
    COUNT(p.id) as pse_records,
    ROUND(AVG(p.pse), 1) as avg_rpe,
    ROUND(AVG(p.carga_total), 0) as avg_load
FROM sessoes s
LEFT JOIN dados_pse p ON s.id = p.sessao_id
WHERE s.jornada = 6
GROUP BY s.id, s.data, s.tipo
ORDER BY s.data;
```

### **Expected Results:**
```
GPS Records: 28 per session (168 total)
PSE Records: 28 per session (168 total)
Sessions: 6 total (5 treino + 1 jogo)
Date Range: 2025-01-20 to 2025-01-25
```

---

## 🎯 FINAL DASHBOARD SCORE IMPLEMENTATION

### **Step 3: Install Score Functions**

```sql
-- Connect to your database
psql -h localhost -p 5433 -U postgres -d futebol_tese

-- Create the scoring functions (copy from FINAL_DASHBOARD_SCORE_SYSTEM.md)
\i FINAL_DASHBOARD_SCORE_SYSTEM.sql
```

### **Step 4: Test Score Calculations**

```sql
-- Test individual player scores
SELECT 
    a.nome_completo,
    s.data,
    calcular_physical_score(a.id, s.id) as physical,
    calcular_technical_score(a.id, s.id) as technical,
    calcular_tactical_score(a.id, s.id) as tactical,
    calcular_wellness_score(a.id, s.id) as wellness,
    calcular_final_score(a.id, s.id) as final_score
FROM atletas a, sessoes s
WHERE s.jornada = 6 AND s.data = '2025-01-25'  -- Match day
  AND a.nome_completo IN ('CARDOSO', 'RICARDO', 'BRUNO')
ORDER BY calcular_final_score(a.id, s.id) DESC;

-- Test team readiness scores
SELECT 
    s.data,
    s.tipo,
    calcular_team_readiness(s.id) as team_readiness,
    ROUND(AVG(calcular_final_score(a.id, s.id)), 1) as avg_final_score
FROM sessoes s, atletas a
WHERE s.jornada = 6 AND a.ativo = true
GROUP BY s.id, s.data, s.tipo
ORDER BY s.data;
```

---

## 📊 FRONTEND INTEGRATION

### **Step 5: Update Dashboard**

Your React frontend should automatically display the new data. Key views to check:

1. **Dashboard Page (`/`):**
   - Team overview with new week data
   - At-risk athletes based on ACWR
   - Performance trends

2. **Athletes Page (`/athletes`):**
   - Individual player profiles
   - Updated metrics with simulation week
   - Final scores and ratings

3. **Sessions Page (`/sessions`):**
   - New training sessions listed
   - Match day analysis
   - Session comparison tools

### **Step 6: Test API Endpoints**

```powershell
# Test team dashboard
curl "http://localhost:8000/api/metrics/team/dashboard"

# Test athlete metrics
curl "http://localhost:8000/api/athletes/1/metrics?days=7"

# Test session details
curl "http://localhost:8000/api/sessions/"
```

---

## 🔬 ADVANCED ANALYTICS TESTING

### **ACWR Analysis:**
```sql
-- Check ACWR progression through simulation week
SELECT 
    a.nome_completo,
    s.data,
    calcular_acwr(a.id, s.data) as acwr,
    CASE 
        WHEN calcular_acwr(a.id, s.data) > 1.5 THEN 'HIGH RISK'
        WHEN calcular_acwr(a.id, s.data) > 1.3 THEN 'MODERATE RISK'
        ELSE 'LOW RISK'
    END as injury_risk
FROM atletas a, sessoes s
WHERE s.jornada = 6 AND a.ativo = true
ORDER BY a.nome_completo, s.data;
```

### **Performance Trends:**
```sql
-- Weekly performance progression
SELECT 
    s.data,
    s.tipo,
    ROUND(AVG(calcular_final_score(a.id, s.id)), 1) as avg_performance,
    ROUND(AVG(calcular_physical_score(a.id, s.id)), 1) as avg_physical,
    ROUND(AVG(calcular_wellness_score(a.id, s.id)), 1) as avg_wellness
FROM sessoes s, atletas a
WHERE s.jornada = 6 AND a.ativo = true
GROUP BY s.id, s.data, s.tipo
ORDER BY s.data;
```

---

## 🎯 SUCCESS METRICS

### **Data Quality Checks:**
- ✅ All 28 players have data for all 6 sessions
- ✅ GPS metrics show realistic progression patterns
- ✅ PSE data reflects fatigue accumulation
- ✅ Final scores range appropriately (40-95)
- ✅ Team readiness scores calculated correctly

### **System Performance:**
- ✅ Dashboard loads with new data
- ✅ API responses under 100ms
- ✅ Score calculations execute successfully
- ✅ Frontend displays updated metrics
- ✅ Database queries optimized

### **Analytics Validation:**
- ✅ ACWR calculations show realistic patterns
- ✅ Performance scores correlate with session intensity
- ✅ Wellness scores reflect training load
- ✅ Team readiness varies appropriately through week

---

## 🚀 NEXT STEPS FOR DEVELOPMENT

### **Phase 1: Data Import & Validation**
1. Import all simulation files
2. Verify data quality
3. Test score calculations
4. Validate frontend display

### **Phase 2: Advanced Features**
1. Implement machine learning predictions
2. Add comparative analytics
3. Create custom reports
4. Develop alert systems

### **Phase 3: Presentation Preparation**
1. Generate insights from simulation data
2. Create visualizations
3. Prepare demo scenarios
4. Document findings

This simulation provides a complete week of realistic football data that will showcase all aspects of your analytics system, from basic GPS tracking to advanced performance scoring and team readiness assessment.
