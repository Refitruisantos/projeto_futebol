# Real Data Ingestion Template
## How to Submit Your Real Football Data

When you have real data from GPS devices, wellness questionnaires, and physical tests, here's exactly how the files should be structured:

---

## 📊 **1. GPS Data File** (`gps_data.csv`)

```csv
date,time,athlete_id,session_id,distance_total,max_speed,avg_speed,sprints,accelerations,decelerations,high_decelerations,max_deceleration,player_load,high_intensity_distance,metabolic_power
2025-01-15,10:30:00,251,1001,8542.5,32.4,8.7,18,42,38,15,6.8,654.2,1850.3,12.4
2025-01-15,10:30:00,252,1001,7890.1,29.8,8.2,14,38,35,12,5.9,598.7,1654.8,11.8
2025-01-15,10:30:00,253,1001,9123.7,33.1,9.1,22,45,41,18,7.2,712.3,2012.5,13.1
```

**Required Columns:**
- `date`: Session date (YYYY-MM-DD)
- `time`: Session start time (HH:MM:SS)
- `athlete_id`: Unique athlete identifier
- `session_id`: Unique session identifier
- `distance_total`: Total distance in meters
- `max_speed`: Maximum speed in km/h
- `avg_speed`: Average speed in km/h
- `sprints`: Number of sprints (>19.8 km/h)
- `accelerations`: Number of accelerations (>3 m/s²)
- `decelerations`: Number of decelerations (<-3 m/s²)
- `high_decelerations`: High intensity decelerations (>4 m/s²)
- `max_deceleration`: Maximum deceleration in m/s²
- `player_load`: Neuromuscular load (AU)
- `high_intensity_distance`: Distance >19.8 km/h in meters
- `metabolic_power`: Average metabolic power in W/kg

---

## 💤 **2. Wellness Data File** (`wellness_data.csv`)

```csv
date,athlete_id,wellness_score,sleep_hours,sleep_quality,fatigue_level,muscle_soreness,mood,stress_level,bedtime,sleep_efficiency,deep_sleep_min,rem_sleep_min,awakenings
2025-01-15,251,6.2,7.5,7,3,2,6,3,23:15,87.5,98,145,2
2025-01-15,252,5.8,6.8,6,4,3,5,4,23:45,82.1,85,128,3
2025-01-15,253,6.8,8.1,8,2,1,7,2,22:30,91.2,112,162,1
```

**Required Columns:**
- `date`: Assessment date (YYYY-MM-DD)
- `athlete_id`: Unique athlete identifier
- `wellness_score`: Overall wellness (1-7 scale)
- `sleep_hours`: Total sleep duration in hours
- `sleep_quality`: Sleep quality rating (1-7 scale)
- `fatigue_level`: Fatigue perception (1-7 scale)
- `muscle_soreness`: Muscle soreness (1-7 scale)
- `mood`: Mood rating (1-7 scale)
- `stress_level`: Stress perception (1-7 scale)
- `bedtime`: Time went to bed (HH:MM)
- `sleep_efficiency`: Sleep efficiency percentage
- `deep_sleep_min`: Deep sleep duration in minutes
- `rem_sleep_min`: REM sleep duration in minutes
- `awakenings`: Number of night awakenings

---

## 💪 **3. PSE Data File** (`pse_data.csv`)

```csv
date,time,athlete_id,session_id,pse_score,duration_min,training_load,session_type
2025-01-15,10:30:00,251,1001,6.5,90,585.0,training
2025-01-15,10:30:00,252,1001,7.2,90,648.0,training
2025-01-15,10:30:00,253,1001,5.8,90,522.0,training
```

**Required Columns:**
- `date`: Session date (YYYY-MM-DD)
- `time`: Session start time (HH:MM:SS)
- `athlete_id`: Unique athlete identifier
- `session_id`: Unique session identifier
- `pse_score`: Perceived exertion (1-10 Borg CR-10 scale)
- `duration_min`: Session duration in minutes
- `training_load`: PSE × Duration (Arbitrary Units)
- `session_type`: Type (training/game/recovery)

---

## 🏋️‍♂️ **4. Physical Tests File** (`physical_tests.csv`)

```csv
date,athlete_id,test_type,sprint_35m_sec,agility_505_sec,cmj_height_cm,squat_jump_cm,hop_distance_m,bronco_time_sec,vo2_max_ml_kg_min
2025-08-15,251,pre_season,4.12,3.85,42.5,39.8,2.45,945.2,56.8
2025-12-15,251,mid_season,4.08,3.82,44.1,41.2,2.51,932.7,58.2
2025-08-15,252,pre_season,4.35,4.02,38.9,36.4,2.31,978.5,54.1
```

**Required Columns:**
- `date`: Test date (YYYY-MM-DD)
- `athlete_id`: Unique athlete identifier
- `test_type`: Test period (pre_season/mid_season/end_season)
- `sprint_35m_sec`: 35m sprint time in seconds
- `agility_505_sec`: 5-0-5 agility test in seconds
- `cmj_height_cm`: Countermovement jump height in cm
- `squat_jump_cm`: Squat jump height in cm
- `hop_distance_m`: Single leg hop distance in meters
- `bronco_time_sec`: Bronco fitness test time in seconds
- `vo2_max_ml_kg_min`: VO₂ Max in ml/kg/min

---

## ⚽ **5. Sessions File** (`sessions.csv`)

```csv
id,date,start_time,type,opponent,location,result,competition,phase,duration_min,difficulty_rating
1001,2025-01-15,10:30:00,training,,,home,,,90,
1002,2025-01-18,15:00:00,game,FC Porto,away,1-2,Liga Portugal,Jornada 18,95,4.8
1003,2025-01-20,10:00:00,training,,,home,,,75,
```

**Required Columns:**
- `id`: Unique session identifier
- `date`: Session date (YYYY-MM-DD)
- `start_time`: Session start time (HH:MM:SS)
- `type`: Session type (training/game/recovery)
- `opponent`: Opponent team name (for games only)
- `location`: home/away/neutral
- `result`: Game result (e.g., "2-1", "0-0")
- `competition`: Competition name
- `phase`: Competition phase/round
- `duration_min`: Session duration in minutes
- `difficulty_rating`: Opponent difficulty (0-5 scale)

---

## 👥 **6. Athletes File** (`athletes.csv`)

```csv
id,full_name,birth_date,position,height_cm,weight_kg,dominant_foot,jersey_number,active
251,João Silva,1995-03-15,MC,178,72,right,8,true
252,Pedro Santos,1997-07-22,AV,175,68,left,11,true
253,Miguel Costa,1993-11-08,DC,185,78,right,4,true
```

**Required Columns:**
- `id`: Unique athlete identifier
- `full_name`: Full name
- `birth_date`: Birth date (YYYY-MM-DD)
- `position`: Playing position (GR/DC/DL/MC/MO/AV/PL)
- `height_cm`: Height in centimeters
- `weight_kg`: Weight in kilograms
- `dominant_foot`: Dominant foot (left/right)
- `jersey_number`: Jersey number
- `active`: Active status (true/false)

---

## 📥 **Data Ingestion Process**

### **Step 1: Prepare Your Files**
1. Export data from your systems (GPS, wellness apps, etc.)
2. Format according to templates above
3. Save as CSV files with UTF-8 encoding
4. Validate data completeness and formats

### **Step 2: Upload Files**
```python
# Use the ingestion script
python scripts/import_real_data.py \
    --gps_file "path/to/gps_data.csv" \
    --wellness_file "path/to/wellness_data.csv" \
    --pse_file "path/to/pse_data.csv" \
    --physical_file "path/to/physical_tests.csv" \
    --sessions_file "path/to/sessions.csv" \
    --athletes_file "path/to/athletes.csv"
```

### **Step 3: Data Validation**
The system will automatically:
- ✅ Validate data formats and ranges
- ✅ Check for missing required fields
- ✅ Calculate derived metrics (ACWR, load trends, etc.)
- ✅ Generate wellness rankings and recommendations
- ✅ Create shape classifications

### **Step 4: View Results**
Access your data at: `http://localhost:5173/athletes/`

---

## 🎯 **Data Quality Requirements**

### **GPS Data**
- Distance: 2,000-15,000m per session
- Max Speed: 15-40 km/h
- Player Load: 200-1,200 AU
- High Decelerations: 5-50 per session

### **Wellness Data**
- All scales: 1-7 range
- Sleep hours: 4-12 hours
- Sleep efficiency: 60-100%
- Bedtime: 20:00-02:00 format

### **PSE Data**
- PSE Score: 1-10 (Borg CR-10)
- Duration: 30-180 minutes
- Training Load: PSE × Duration

### **Physical Tests**
- 35m Sprint: 3.5-6.0 seconds
- CMJ: 25-60 cm
- VO₂ Max: 40-70 ml/kg/min

---

## 🚨 **Common Issues & Solutions**

### **Issue: "Column not found"**
**Solution:** Ensure exact column names match template

### **Issue: "Invalid date format"**
**Solution:** Use YYYY-MM-DD format only

### **Issue: "Missing athlete_id"**
**Solution:** Ensure all athletes exist in athletes.csv first

### **Issue: "Out of range values"**
**Solution:** Check data quality requirements above

---

## 📞 **Support**

For data ingestion support:
1. Check data against templates above
2. Validate file formats (CSV, UTF-8)
3. Ensure all required columns present
4. Test with small sample first

**The system will automatically process your real data and provide the same comprehensive analysis currently shown with simulated data!**
