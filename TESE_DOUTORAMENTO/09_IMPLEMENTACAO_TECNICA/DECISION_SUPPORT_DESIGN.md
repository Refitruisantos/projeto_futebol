# Decision Support & Risk Integration - Design Document

## Overview

This document describes the **Decision Support and Risk Integration** system implemented in the `dashboard_principal` endpoint to provide actionable insights for coaching staff.

---

## Design Principles

### Core Philosophy
The dashboard maintains simplicity while providing critical risk information by:
- Presenting **only aggregated and stable signals**
- Keeping detailed metrics in specialized endpoints
- Making all indicators **easily explainable** to coaches
- Answering three key questions:
  1. **Who is at risk?**
  2. **Why (in simple terms)?**
  3. **Is the situation getting worse or better?**

### Data Sources
- **Primary:** `metricas_carga` table (weekly calculated metrics)
- **Supporting:** `atletas`, `dados_gps`, `sessoes`
- **Frequency:** Weekly updates
- **Scope:** Most recent week only

---

## Enhanced Dashboard Fields

### 1. Identification & Context
```json
{
  "atleta_id": 1,
  "nome_completo": "João Silva",
  "posicao": "Médio",
  "ativo": true
}
```

**Purpose:** Basic athlete identification and roster status

---

### 2. Load Metrics (Last Week)
```json
{
  "weekly_load": 3500,
  "monotony": 5.85,
  "strain": 20475,
  "acwr": 1.35,
  "training_days": 7
}
```

**Source:** `metricas_carga` table for the most recent week

**Definitions:**
- **weekly_load:** Total PSE load for the week (Σ PSE × duration)
- **monotony:** Load variation index (mean / std_dev)
- **strain:** Total strain (load × monotony)
- **acwr:** Acute:Chronic Workload Ratio (7-day / 28-day)
- **training_days:** Number of days trained this week

---

### 3. Statistical Normalization (Z-Scores)
```json
{
  "z_load": 0.71,
  "z_monotony": 2.06,
  "z_strain": 2.81,
  "z_acwr": 1.33
}
```

**Purpose:** Standardize metrics relative to team performance

**Formula:**
```python
z_score = (athlete_value - team_mean) / team_std_dev
```

**Interpretation:**
| Z-Score Range | Meaning | Action |
|---------------|---------|--------|
| -1 to +1 | Within normal team range | ✅ Monitor normally |
| ±1 to ±2 | Outside normal range | ⚠️ Increased attention |
| Beyond ±2 | Extreme outlier | 🔴 Immediate review |

**Use Case Example:**
- If `z_monotony = 2.06`, the athlete's monotony is **2.06 standard deviations above** the team average
- This indicates **significantly less load variation** than teammates (potential injury risk)

---

### 4. Risk Indicators (Individual)
```json
{
  "risk_monotony": "red",
  "risk_strain": "red",
  "risk_acwr": "yellow",
  "risk_overall": "red"
}
```

**Purpose:** Traffic-light system for quick risk assessment

**Individual Risk Thresholds:**

#### Monotony
- 🟢 **Green:** < 1.0 (good variation)
- 🟡 **Yellow:** 1.0 - 2.0 (moderate)
- 🔴 **Red:** > 2.0 (low variation, high risk)

#### Strain
- 🟢 **Green:** < 4000 (low strain)
- 🟡 **Yellow:** 4000 - 6000 (moderate)
- 🔴 **Red:** > 6000 (high strain)

#### ACWR
- 🔴 **Red (Low):** < 0.8 (detraining risk)
- 🟢 **Green:** 0.8 - 1.3 (optimal)
- 🟡 **Yellow:** 1.3 - 1.5 (elevated)
- 🔴 **Red (High):** > 1.5 (overtraining risk)

**Overall Risk Calculation:**
```python
risk_overall = max(risk_monotony, risk_strain, risk_acwr)
# Priority hierarchy: red > yellow > green
```

**Logic:** The overall risk is determined by the **worst** of the three individual risks.

---

### 5. GPS Context (Supporting Data)
```json
{
  "num_sessoes": 8,
  "distancia_total_media": 8500,
  "velocidade_max_media": 30.5,
  "aceleracoes_media": 42
}
```

**Purpose:** Provide physical performance context alongside risk indicators

**Source:** `dados_gps` aggregated for the same week as load metrics

---

## Response Structure

### Complete Dashboard Response
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
      "weekly_load": 3800,
      "risk_overall": "yellow"
    }
  ],
  
  "at_risk_athletes": [
    {
      "atleta_id": 1,
      "nome_completo": "João Silva",
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

---

## Implementation Details

### Backend Endpoint
**File:** `backend/routers/metrics.py`  
**Endpoint:** `GET /api/metrics/team/dashboard`

### Algorithm Flow

```
1. Get most recent week from metricas_carga
   ↓
2. Calculate team statistics (mean, std_dev) for z-scores
   ↓
3. Query athlete data + latest metrics + GPS summary
   ↓
4. For each athlete:
   - Calculate z-scores
   - Determine risk_overall
   - Count risk levels
   ↓
5. Sort athletes by risk (red → yellow → green)
   ↓
6. Extract top_load_athletes and at_risk_athletes
   ↓
7. Return enriched response with context
```

### SQL Query Structure

```sql
WITH latest_metrics AS (
  -- Get load metrics from metricas_carga
  SELECT 
    a.id, a.nome_completo, a.posicao, a.ativo,
    mc.carga_total_semanal as weekly_load,
    mc.monotonia as monotony,
    mc.tensao as strain,
    mc.acwr,
    mc.nivel_risco_monotonia as risk_monotony,
    mc.nivel_risco_tensao as risk_strain,
    mc.nivel_risco_acwr as risk_acwr,
    mc.dias_treino as training_days
  FROM atletas a
  LEFT JOIN metricas_carga mc ON mc.atleta_id = a.id AND mc.semana_inicio = %latest_week%
  WHERE a.ativo = TRUE
),
gps_summary AS (
  -- Get GPS context for the same week
  SELECT 
    g.atleta_id,
    COUNT(DISTINCT g.sessao_id) as num_sessoes,
    ROUND(AVG(g.distancia_total)::numeric, 2) as distancia_total_media,
    ROUND(AVG(g.velocidade_max)::numeric, 2) as velocidade_max_media,
    ROUND(AVG(g.aceleracoes)::numeric, 2) as aceleracoes_media
  FROM dados_gps g
  JOIN sessoes s ON s.id = g.sessao_id
  WHERE s.data >= %week_start% AND s.data < %week_start% + INTERVAL '7 days'
  GROUP BY g.atleta_id
)
SELECT 
  lm.*,
  COALESCE(gs.num_sessoes, 0) as num_sessoes,
  gs.distancia_total_media,
  gs.velocidade_max_media,
  gs.aceleracoes_media,
  -- Determine overall risk
  CASE 
    WHEN lm.risk_monotony = 'red' OR lm.risk_strain = 'red' OR lm.risk_acwr = 'red' THEN 'red'
    WHEN lm.risk_monotony = 'yellow' OR lm.risk_strain = 'yellow' OR lm.risk_acwr = 'yellow' THEN 'yellow'
    WHEN lm.risk_monotony = 'green' OR lm.risk_strain = 'green' OR lm.risk_acwr = 'green' THEN 'green'
    ELSE 'unknown'
  END as risk_overall
FROM latest_metrics lm
LEFT JOIN gps_summary gs ON gs.atleta_id = lm.atleta_id
ORDER BY risk_overall_priority, lm.nome_completo
```

### Z-Score Calculation (Python)

```python
for athlete in athletes:
    if team_stats['std_load'] and team_stats['std_load'] > 0:
        athlete['z_load'] = round(
            (athlete['weekly_load'] - team_stats['mean_load']) / team_stats['std_load'], 
            2
        ) if athlete['weekly_load'] else None
    
    # Repeat for z_monotony, z_strain, z_acwr...
```

---

## Fallback Strategy

**Problem:** What if `metricas_carga` has no data?

**Solution:** Graceful degradation
```python
if not most_recent_week:
    # Fallback to simple dashboard
    simple_query = "SELECT * FROM dashboard_principal ORDER BY distancia_total_media DESC"
    return {
        "athletes_overview": db.query_to_dict(simple_query),
        "top_load_athletes": [],
        "at_risk_athletes": [],
        "risk_summary": {"red": 0, "yellow": 0, "green": 0}
    }
```

This ensures the dashboard never breaks, even with incomplete data.

---

## Frontend Integration

### Dashboard Page Update Required

**File:** `frontend/src/pages/Dashboard.jsx`

**Changes Needed:**
1. Update API response handling to include new fields
2. Add risk badge components (red/yellow/green)
3. Display z-scores with tooltips explaining meaning
4. Show risk_summary as a distribution chart
5. Highlight at-risk athletes prominently

**Example UI Component:**
```jsx
<RiskBadge risk={athlete.risk_overall}>
  {athlete.risk_overall === 'red' ? '🔴 Alto Risco' :
   athlete.risk_overall === 'yellow' ? '🟡 Atenção' :
   '🟢 Normal'}
</RiskBadge>

<Tooltip>
  <p>Monotonia: {athlete.risk_monotony}</p>
  <p>Tensão: {athlete.risk_strain}</p>
  <p>ACWR: {athlete.risk_acwr}</p>
  <p>Z-Score Monotonia: {athlete.z_monotony} 
     {athlete.z_monotony > 2 ? '(Muito acima da média)' : ''}
  </p>
</Tooltip>
```

---

## Usage Scenarios

### Scenario 1: Daily Team Meeting
**Question:** "Who do I need to monitor today?"

**Answer from Dashboard:**
```
at_risk_athletes: [
  {name: "João Silva", risk_overall: "red", risk_monotony: "red", risk_strain: "red"}
]
```

**Action:** Review João's recent load and consider load adjustment.

---

### Scenario 2: Performance Analysis
**Question:** "Is this athlete underperforming or just having a normal variation?"

**Answer from Z-Scores:**
```
{
  "z_load": -1.5,
  "z_monotony": 0.3,
  "z_strain": -1.2
}
```

**Interpretation:** 
- Load is 1.5 std dev **below** team average (possible under-loading)
- Monotony is normal
- Strain is below average

**Action:** Consider increasing load if athlete is healthy.

---

### Scenario 3: Injury Risk Prevention
**Question:** "Which athletes are at highest injury risk?"

**Answer from Risk Summary:**
```
risk_summary: {
  "red": 3,    // 3 athletes at high risk
  "yellow": 8, // 8 athletes need monitoring
  "green": 12  // 12 athletes are fine
}
```

**Action:** Focus on the 3 red-level athletes for immediate intervention.

---

## Advantages of This Design

### 1. Simplicity
- Single endpoint provides complete picture
- Traffic-light system is universally understood
- No complex ML models in the overview

### 2. Actionability
- Clear risk indicators drive decisions
- Z-scores provide context for outliers
- Top-load and at-risk lists prioritize attention

### 3. Maintainability
- Based on existing `metricas_carga` calculations
- No new database tables required
- Easy to extend with additional risk factors

### 4. Performance
- Weekly calculation (not real-time)
- Aggregated queries with CTEs
- Minimal frontend processing

### 5. Explainability
- All risk thresholds are documented
- Z-scores have clear interpretation
- Coaches can verify calculations

---

## Future Enhancements (Not in MVP)

### Trend Analysis
Add week-over-week change indicators:
```json
{
  "risk_trend": "worsening",  // or "improving", "stable"
  "load_change_pct": 15.3,
  "monotony_change": 1.2
}
```

### Machine Learning Integration
- Injury prediction probabilities from ML models
- LSTM-based performance forecasting
- Anomaly detection for sudden changes

### Contextual Risk
- Position-specific risk thresholds
- Competition schedule consideration
- Recovery time since last match

### Alerts System
- Integration with `alertas` table
- Automatic notifications for red-level risks
- Historical alert tracking

---

## Testing Strategy

### Unit Tests
- Z-score calculation accuracy
- Risk level determination logic
- Fallback behavior when no data

### Integration Tests
- Full dashboard query execution
- Response structure validation
- Performance with 25+ athletes

### Manual Testing
- Verify risk_overall matches worst individual risk
- Check z-scores against manual calculations
- Confirm sorting by risk level

---

## Documentation

### For Developers
- See `API_MASTER_DOCUMENTATION.md` for endpoint details
- See `backend/routers/metrics.py` for implementation
- See this document for design rationale

### For Coaches/Users
- Risk colors: 🔴 Red = Action needed, 🟡 Yellow = Monitor, 🟢 Green = OK
- Z-scores: How far from team average (±1 is normal)
- Overall risk = worst of three metrics (prioritizes safety)

---

## Conclusion

This decision support system transforms raw load metrics into **actionable insights** for coaching staff. By integrating risk indicators, statistical normalization, and clear visual cues, the dashboard answers the critical questions coaches ask daily without overwhelming them with complexity.

The design maintains the principle of **"simple overview, detailed dive"** - coaches get immediate risk awareness in the dashboard and can explore details through specialized endpoints when needed.

---

**Implementation Status:** ✅ Complete  
**Backend Endpoint:** ✅ Enhanced  
**API Documentation:** ✅ Updated  
**Frontend Integration:** 🔜 Pending  
**Testing:** 🔜 Pending  

**Version:** 1.0  
**Last Updated:** December 22, 2024  
**Author:** Development Team
