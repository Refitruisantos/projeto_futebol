# 🎯 FINAL DASHBOARD SCORE SYSTEM
## Comprehensive Performance Index for Football Analytics

---

## 📊 OVERALL PERFORMANCE INDEX (0-100)

### **Formula Structure:**
```
Final Score = (Physical × 0.25) + (Technical × 0.25) + (Tactical × 0.25) + (Wellness × 0.25)
```

---

## 🏃‍♂️ COMPONENT 1: PHYSICAL PERFORMANCE (25%)

### **Sub-metrics:**
1. **Distance Efficiency (40%)**
   ```sql
   distance_score = (total_distance_m / position_expected_distance) * 100
   -- Expected distances by position:
   -- GR: 4000m, DC: 9500m, DL: 10500m, MC: 11000m, EX: 10800m, AV: 10200m
   ```

2. **Speed Maintenance (30%)**
   ```sql
   speed_score = (
     (max_velocity_kmh / position_max_expected) * 50 +
     (efforts_over_25_2_kmh / position_sprint_expected) * 50
   )
   ```

3. **Acceleration Profile (30%)**
   ```sql
   acceleration_score = (
     (acc_b1_3_total_efforts / session_duration_min) * 60 +
     (decel_b1_3_total_efforts / session_duration_min) * 40
   ) / 2
   ```

### **Physical Score Calculation:**
```sql
CREATE OR REPLACE FUNCTION calcular_physical_score(
    atleta_id INTEGER,
    sessao_id INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    physical_score DECIMAL(5,2);
    distance_eff DECIMAL(5,2);
    speed_maint DECIMAL(5,2);
    accel_prof DECIMAL(5,2);
    pos VARCHAR(5);
BEGIN
    -- Get player position
    SELECT posicao INTO pos FROM atletas WHERE id = atleta_id;
    
    -- Calculate sub-scores based on GPS data
    SELECT 
        CASE pos
            WHEN 'GR' THEN LEAST(100, (g.distancia_total / 4000.0) * 100)
            WHEN 'DC' THEN LEAST(100, (g.distancia_total / 9500.0) * 100)
            WHEN 'DL' THEN LEAST(100, (g.distancia_total / 10500.0) * 100)
            WHEN 'MC' THEN LEAST(100, (g.distancia_total / 11000.0) * 100)
            WHEN 'EX' THEN LEAST(100, (g.distancia_total / 10800.0) * 100)
            WHEN 'AV' THEN LEAST(100, (g.distancia_total / 10200.0) * 100)
            ELSE 100
        END,
        LEAST(100, (g.velocidade_max / 33.0) * 50 + (g.effs_25_2_kmh / 20.0) * 50),
        LEAST(100, ((g.aceleracoes + g.desaceleracoes) / 200.0) * 100)
    INTO distance_eff, speed_maint, accel_prof
    FROM dados_gps g
    WHERE g.atleta_id = atleta_id AND g.sessao_id = sessao_id;
    
    physical_score := (distance_eff * 0.4) + (speed_maint * 0.3) + (accel_prof * 0.3);
    
    RETURN COALESCE(physical_score, 0);
END;
$$ LANGUAGE plpgsql;
```

---

## ⚽ COMPONENT 2: TECHNICAL PERFORMANCE (25%)

### **Sub-metrics:**
1. **Ball Action Efficiency (50%)**
   ```sql
   -- Simulated based on high-intensity efforts and position
   technical_actions = efforts_over_19_8_kmh * position_multiplier
   ```

2. **Movement Quality (30%)**
   ```sql
   movement_quality = (distance_over_19_8_kmh / efforts_over_19_8_kmh) * efficiency_factor
   ```

3. **Consistency Index (20%)**
   ```sql
   consistency = 100 - (STDDEV(session_metrics) / AVG(session_metrics) * 100)
   ```

### **Technical Score Calculation:**
```sql
CREATE OR REPLACE FUNCTION calcular_technical_score(
    atleta_id INTEGER,
    sessao_id INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    technical_score DECIMAL(5,2);
    ball_actions DECIMAL(5,2);
    movement_qual DECIMAL(5,2);
    consistency_idx DECIMAL(5,2);
    pos VARCHAR(5);
BEGIN
    SELECT posicao INTO pos FROM atletas WHERE id = atleta_id;
    
    SELECT 
        CASE pos
            WHEN 'GR' THEN LEAST(100, (g.effs_19_8_kmh * 2.0))
            WHEN 'DC' THEN LEAST(100, (g.effs_19_8_kmh * 3.0))
            WHEN 'DL' THEN LEAST(100, (g.effs_19_8_kmh * 3.5))
            WHEN 'MC' THEN LEAST(100, (g.effs_19_8_kmh * 4.0))
            WHEN 'EX' THEN LEAST(100, (g.effs_19_8_kmh * 4.5))
            WHEN 'AV' THEN LEAST(100, (g.effs_19_8_kmh * 4.0))
            ELSE 100
        END,
        CASE 
            WHEN g.effs_19_8_kmh > 0 THEN 
                LEAST(100, (g.dist_19_8_kmh / g.effs_19_8_kmh) * 2.0)
            ELSE 50
        END,
        LEAST(100, 100 - ABS(g.velocidade_max - 30.0) * 2)
    INTO ball_actions, movement_qual, consistency_idx
    FROM dados_gps g
    WHERE g.atleta_id = atleta_id AND g.sessao_id = sessao_id;
    
    technical_score := (ball_actions * 0.5) + (movement_qual * 0.3) + (consistency_idx * 0.2);
    
    RETURN COALESCE(technical_score, 0);
END;
$$ LANGUAGE plpgsql;
```

---

## 🎯 COMPONENT 3: TACTICAL PERFORMANCE (25%)

### **Sub-metrics:**
1. **Positional Discipline (40%)**
   ```sql
   -- Based on acceleration/deceleration patterns indicating positional changes
   positional_discipline = 100 - (excessive_movements / expected_movements * 100)
   ```

2. **Team Coordination (35%)**
   ```sql
   -- Correlation with team average metrics
   coordination = correlation_coefficient(player_metrics, team_avg_metrics) * 100
   ```

3. **Tactical Adherence (25%)**
   ```sql
   -- Session type specific expectations
   adherence = (actual_performance / session_tactical_target) * 100
   ```

### **Tactical Score Calculation:**
```sql
CREATE OR REPLACE FUNCTION calcular_tactical_score(
    atleta_id INTEGER,
    sessao_id INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    tactical_score DECIMAL(5,2);
    pos_discipline DECIMAL(5,2);
    team_coord DECIMAL(5,2);
    tactical_adher DECIMAL(5,2);
    session_type VARCHAR(20);
BEGIN
    SELECT tipo INTO session_type FROM sessoes WHERE id = sessao_id;
    
    SELECT 
        LEAST(100, 100 - ((g.aceleracoes + g.desaceleracoes - 150) / 150.0) * 50),
        LEAST(100, (g.tot_effs_gen2 / 
            (SELECT AVG(tot_effs_gen2) FROM dados_gps WHERE sessao_id = sessao_id)) * 100),
        CASE session_type
            WHEN 'jogo' THEN LEAST(100, (g.distancia_total / 10000.0) * 100)
            WHEN 'treino' THEN LEAST(100, (g.player_load / 100.0) * 100)
            ELSE 100
        END
    INTO pos_discipline, team_coord, tactical_adher
    FROM dados_gps g
    WHERE g.atleta_id = atleta_id AND g.sessao_id = sessao_id;
    
    tactical_score := (pos_discipline * 0.4) + (team_coord * 0.35) + (tactical_adher * 0.25);
    
    RETURN COALESCE(tactical_score, 0);
END;
$$ LANGUAGE plpgsql;
```

---

## 💪 COMPONENT 4: WELLNESS PERFORMANCE (25%)

### **Sub-metrics:**
1. **Recovery Efficiency (40%)**
   ```sql
   recovery_score = (sono * 20) + ((5 - fadiga) * 20)
   ```

2. **Stress Management (35%)**
   ```sql
   stress_score = ((5 - stress) * 20) + ((5 - doms) * 20)
   ```

3. **Load Tolerance (25%)**
   ```sql
   load_tolerance = LEAST(100, (carga_total / rpe_expected_for_session) * 100)
   ```

### **Wellness Score Calculation:**
```sql
CREATE OR REPLACE FUNCTION calcular_wellness_score(
    atleta_id INTEGER,
    sessao_id INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    wellness_score DECIMAL(5,2);
    recovery_eff DECIMAL(5,2);
    stress_mgmt DECIMAL(5,2);
    load_tol DECIMAL(5,2);
BEGIN
    SELECT 
        (p.qualidade_sono * 20) + ((5 - p.fadiga) * 20),
        ((5 - p.stress) * 20) + ((5 - p.dor_muscular) * 20),
        LEAST(100, (p.carga_total / (p.pse * p.duracao_min)) * 100)
    INTO recovery_eff, stress_mgmt, load_tol
    FROM dados_pse p
    WHERE p.atleta_id = atleta_id AND p.sessao_id = sessao_id;
    
    wellness_score := (recovery_eff * 0.4) + (stress_mgmt * 0.35) + (load_tol * 0.25);
    
    RETURN COALESCE(wellness_score, 0);
END;
$$ LANGUAGE plpgsql;
```

---

## 🏆 FINAL DASHBOARD SCORE

### **Master Calculation Function:**
```sql
CREATE OR REPLACE FUNCTION calcular_final_score(
    atleta_id INTEGER,
    sessao_id INTEGER
) RETURNS DECIMAL(5,2) AS $$
DECLARE
    final_score DECIMAL(5,2);
    physical_comp DECIMAL(5,2);
    technical_comp DECIMAL(5,2);
    tactical_comp DECIMAL(5,2);
    wellness_comp DECIMAL(5,2);
BEGIN
    -- Calculate each component
    physical_comp := calcular_physical_score(atleta_id, sessao_id);
    technical_comp := calcular_technical_score(atleta_id, sessao_id);
    tactical_comp := calcular_tactical_score(atleta_id, sessao_id);
    wellness_comp := calcular_wellness_score(atleta_id, sessao_id);
    
    -- Calculate weighted final score
    final_score := (physical_comp * 0.25) + (technical_comp * 0.25) + 
                   (tactical_comp * 0.25) + (wellness_comp * 0.25);
    
    RETURN ROUND(final_score, 2);
END;
$$ LANGUAGE plpgsql;
```

---

## 📈 TEAM READINESS SCORE (0-10)

### **Team-Level Calculation:**
```sql
CREATE OR REPLACE FUNCTION calcular_team_readiness(
    sessao_id INTEGER
) RETURNS DECIMAL(3,1) AS $$
DECLARE
    team_readiness DECIMAL(3,1);
    avg_final_score DECIMAL(5,2);
    injury_risk_factor DECIMAL(3,2);
    fatigue_factor DECIMAL(3,2);
    consistency_factor DECIMAL(3,2);
BEGIN
    -- Average final score for the session
    SELECT AVG(calcular_final_score(a.id, sessao_id))
    INTO avg_final_score
    FROM atletas a
    WHERE a.ativo = true;
    
    -- Calculate risk factors
    SELECT 
        1.0 - (COUNT(CASE WHEN calcular_acwr(a.id, CURRENT_DATE) > 1.5 THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL),
        1.0 - (AVG(p.fadiga) / 5.0),
        1.0 - (STDDEV(calcular_final_score(a.id, sessao_id)) / 100.0)
    INTO injury_risk_factor, fatigue_factor, consistency_factor
    FROM atletas a
    LEFT JOIN dados_pse p ON a.id = p.atleta_id AND p.sessao_id = sessao_id
    WHERE a.ativo = true;
    
    -- Calculate team readiness (0-10 scale)
    team_readiness := (avg_final_score / 100.0) * 10.0 * 
                      injury_risk_factor * fatigue_factor * consistency_factor;
    
    RETURN ROUND(team_readiness, 1);
END;
$$ LANGUAGE plpgsql;
```

---

## 🎯 DASHBOARD IMPLEMENTATION

### **Main Dashboard View:**
```sql
CREATE OR REPLACE VIEW dashboard_final_scores AS
SELECT 
    s.data,
    s.tipo,
    s.jornada,
    a.nome_completo,
    a.posicao,
    calcular_physical_score(a.id, s.id) as physical_score,
    calcular_technical_score(a.id, s.id) as technical_score,
    calcular_tactical_score(a.id, s.id) as tactical_score,
    calcular_wellness_score(a.id, s.id) as wellness_score,
    calcular_final_score(a.id, s.id) as final_score,
    calcular_acwr(a.id, s.data) as acwr,
    CASE 
        WHEN calcular_final_score(a.id, s.id) >= 85 THEN 'Excellent'
        WHEN calcular_final_score(a.id, s.id) >= 70 THEN 'Good'
        WHEN calcular_final_score(a.id, s.id) >= 55 THEN 'Average'
        WHEN calcular_final_score(a.id, s.id) >= 40 THEN 'Below Average'
        ELSE 'Poor'
    END as performance_rating
FROM atletas a
CROSS JOIN sessoes s
WHERE a.ativo = true
  AND EXISTS (
      SELECT 1 FROM dados_gps g 
      WHERE g.atleta_id = a.id AND g.sessao_id = s.id
  )
ORDER BY s.data DESC, calcular_final_score(a.id, s.id) DESC;
```

---

## 📊 EXPECTED SIMULATION RESULTS

### **Week Progression Scores:**
- **Monday (Recovery):** Team Avg: 65-75
- **Tuesday (Technical):** Team Avg: 70-80
- **Wednesday (Tactical):** Team Avg: 75-85
- **Thursday (Physical):** Team Avg: 80-90
- **Friday (Pre-Match):** Team Avg: 60-70
- **Saturday (Match):** Team Avg: 85-95

### **Individual Player Categories:**
- **Top Performers:** 85-95 (Starters)
- **Good Performers:** 70-84 (Rotation)
- **Development Players:** 55-69 (Youth/Bench)

### **Risk Indicators:**
- **ACWR > 1.5:** High injury risk
- **Final Score < 40:** Performance concern
- **Wellness < 50:** Recovery needed
- **Team Readiness < 6.0:** Match readiness concern

This comprehensive scoring system provides a holistic view of individual and team performance, integrating all the factors you're studying in your football analytics research.
