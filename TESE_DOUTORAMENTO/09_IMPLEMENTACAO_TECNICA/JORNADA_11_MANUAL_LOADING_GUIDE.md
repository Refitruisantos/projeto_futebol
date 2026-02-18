# 📋 JORNADA 11 MANUAL LOADING GUIDE
## Complete Instructions for Manual Data Upload

---

## 🗓️ **JORNADA 11 - WEDNESDAY TACTICAL SESSION**

### **Session Details:**
- **Date:** Choose your preferred date (e.g., 05/02/2025)
- **Type:** Tactical Training
- **Intensity:** High (tactical focus with positional work)
- **Duration:** 105 minutes
- **Focus:** Team coordination, positional play, set pieces

---

## 📊 **FILES CREATED FOR YOU**

### **1. GPS Data File**
📄 **File:** `jornada_11_wednesday_tactical.csv`  
📍 **Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data\jornada_11_wednesday_tactical.csv`

**Data Characteristics:**
- **Distance:** 8,045m - 8,578m (high tactical intensity)
- **Max Speed:** 27.8 - 29.6 km/h (moderate to high)
- **High-Intensity Efforts:** 11-20 efforts over 19.8 km/h
- **Accelerations:** 36-53 (tactical movements)

### **2. PSE/Wellness Data File**
📄 **File:** `Jogo11_wednesday_pse.csv`  
📍 **Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data\Jogo11_wednesday_pse.csv`

**Data Characteristics:**
- **Sleep:** 5-8 (varied individual responses)
- **Stress:** 3-6 (moderate to high tactical stress)
- **Fatigue:** 2-5 (building through week)
- **DOMS:** 2-5 (muscle soreness levels)
- **RPE:** 5-8 (moderate to high perceived effort)
- **Duration:** 105 minutes (tactical session)
- **Load:** 525-840 (calculated from RPE × Duration)

---

## 🔄 **MANUAL LOADING PROCESS**

### **STEP 1: Upload GPS Data**

1. **Access your dashboard:** `http://localhost:5173`
2. **Navigate to GPS upload section**
3. **Select file:** `jornada_11_wednesday_tactical.csv`
4. **Set parameters:**
   ```
   Jornada: 11
   Data da Sessão: 05/02/2025 (or your chosen date)
   Tipo: treino
   ```
5. **Click "Carregar"**

**Expected Result:**
- ✅ Records inserted: 28/28 players
- ✅ Session created with ID (note this number)
- ✅ No errors (similarity function now works)

### **STEP 2: Upload PSE Data**

**Note:** Your system doesn't have a PSE web upload interface, so you'll need to use a script or database direct insert.

**Option A - Use Script (Recommended):**
```powershell
# Create a simple PSE upload script for Jornada 11
python upload_jornada11_pse.py
```

**Option B - Manual Database Insert:**
I can create SQL INSERT statements for you to run directly in your database.

---

## 📈 **DATA SPECIFICATIONS**

### **GPS Data Columns (Required):**
- `player` - Player name (must match database)
- `total_distance_m` - Total distance in meters
- `max_velocity_kmh` - Maximum velocity in km/h
- `acc_b1_3_total_efforts` - Acceleration efforts
- `decel_b1_3_total_efforts` - Deceleration efforts
- `efforts_over_19_8_kmh` - High-intensity efforts
- `distance_over_19_8_kmh` - High-intensity distance
- `efforts_over_25_2_kmh` - Very high-intensity efforts
- `velocity_b3_plus_total_efforts` - High-velocity efforts

### **PSE Data Columns (Required):**
- `Nome` - Player name
- `Pos` - Position (DC, MC, EX, AV, GR)
- `Sono` - Sleep quality (1-10)
- `Stress` - Stress level (1-5)
- `Fadiga` - Fatigue level (1-5)
- `DOMS` - Delayed onset muscle soreness (1-5)
- `VOLUME` - Session duration in minutes
- `Rpe` - Rate of perceived exertion (1-10)
- `CARGA` - Training load (RPE × Duration)

---

## 📊 **UPLOAD HISTORY & TRACKING**

### **Where to Check Upload History:**

1. **Database Sessions Table:**
   ```sql
   SELECT id, data, tipo, jornada, created_at 
   FROM sessoes 
   WHERE jornada = 11 
   ORDER BY created_at DESC;
   ```

2. **GPS Data Count:**
   ```sql
   SELECT s.id, s.data, COUNT(g.id) as gps_records
   FROM sessoes s
   LEFT JOIN dados_gps g ON s.id = g.sessao_id
   WHERE s.jornada = 11
   GROUP BY s.id, s.data;
   ```

3. **PSE Data Count:**
   ```sql
   SELECT s.id, s.data, COUNT(p.id) as pse_records
   FROM sessoes s
   LEFT JOIN dados_pse p ON s.id = p.sessao_id
   WHERE s.jornada = 11
   GROUP BY s.id, s.data;
   ```

### **How to Delete if You Make a Mistake:**

**Delete GPS Data:**
```sql
DELETE FROM dados_gps 
WHERE sessao_id IN (
    SELECT id FROM sessoes WHERE jornada = 11
);
```

**Delete PSE Data:**
```sql
DELETE FROM dados_pse 
WHERE sessao_id IN (
    SELECT id FROM sessoes WHERE jornada = 11
);
```

**Delete Session:**
```sql
DELETE FROM sessoes WHERE jornada = 11;
```

**Complete Cleanup (All Jornada 11 data):**
```sql
-- Delete in correct order (foreign key constraints)
DELETE FROM dados_gps WHERE sessao_id IN (SELECT id FROM sessoes WHERE jornada = 11);
DELETE FROM dados_pse WHERE sessao_id IN (SELECT id FROM sessoes WHERE jornada = 11);
DELETE FROM sessoes WHERE jornada = 11;
```

---

## 🎯 **VERIFICATION CHECKLIST**

After uploading, verify your data:

### **✅ GPS Upload Success:**
- [ ] 28 players imported
- [ ] Session created with Jornada 11
- [ ] Distance values look realistic (8,000m+ range)
- [ ] No error messages

### **✅ PSE Upload Success:**
- [ ] 28 wellness records created
- [ ] RPE values between 5-8
- [ ] Load calculations correct (RPE × 105 minutes)
- [ ] No constraint violations

### **✅ Dashboard Display:**
- [ ] New session appears in Sessions page
- [ ] Jornada 11 data visible in charts
- [ ] Individual player data accessible
- [ ] Metrics look realistic for tactical training

---

## 🔧 **TROUBLESHOOTING**

### **If GPS Upload Fails:**
- Check player names match database exactly
- Verify file format (CSV with correct headers)
- Ensure PostgreSQL similarity function is enabled
- Check date format (DD/MM/YYYY)

### **If PSE Upload Fails:**
- Values must fit database constraints
- Sleep: 1-10, Stress/Fatigue/DOMS: 1-5, RPE: 1-10
- Duration should be positive integer
- Load calculation should be reasonable

### **If You Need to Start Over:**
1. Run the cleanup SQL commands above
2. Verify all Jornada 11 data is deleted
3. Re-upload files with corrected parameters

---

## 🎮 **TESTING SCENARIOS**

After successful upload, test these scenarios:

### **Scenario 1: Session Overview**
- Navigate to Sessions page
- Find Jornada 11 entry
- Click to view session details
- Verify GPS and PSE data display

### **Scenario 2: Player Analysis**
- Select any player
- View their Jornada 11 performance
- Compare with previous sessions
- Check tactical training metrics

### **Scenario 3: Team Comparison**
- View team dashboard
- Compare Jornada 11 vs other sessions
- Analyze tactical training patterns
- Check load distribution

---

## 📋 **READY FOR MANUAL LOADING**

Your Jornada 11 files are ready:

✅ **GPS File:** `jornada_11_wednesday_tactical.csv` (28 players)  
✅ **PSE File:** `Jogo11_wednesday_pse.csv` (28 wellness records)  
✅ **Upload Instructions:** Complete step-by-step guide  
✅ **Verification Methods:** SQL queries and dashboard checks  
✅ **Cleanup Procedures:** Safe deletion if needed  

You now have full control over the manual loading process with complete tracking and deletion capabilities!
