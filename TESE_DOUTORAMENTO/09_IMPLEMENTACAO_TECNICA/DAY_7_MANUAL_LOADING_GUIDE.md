# 📁 DAY 7 MANUAL LOADING GUIDE
## Sunday Recovery Session Files Ready for Download

---

## 🗓️ **DAY 7 - SUNDAY RECOVERY SESSION**
**Date:** 2025-01-26  
**Type:** Recovery/Rest Day  
**Intensity:** Very Low  
**Focus:** Post-match recovery, light movement

---

## 📊 **FILES CREATED FOR MANUAL LOADING**

### **GPS Data File:**
📄 **File:** `jornada_6_sunday_recovery.csv`  
📍 **Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data\jornada_6_sunday_recovery.csv`

**Characteristics:**
- **Distance:** Very low (avg 3,200m)
- **Max Speed:** Reduced (avg 22 km/h)
- **Efforts:** Minimal high-intensity work
- **Focus:** Recovery movement patterns

### **PSE/Wellness Data File:**
📄 **File:** `Jogo6_sunday_pse.csv`  
📍 **Location:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data\Jogo6_sunday_pse.csv`

**Characteristics:**
- **RPE:** Very low (2-4)
- **Duration:** Short (45 min)
- **Fatigue:** Post-match recovery levels
- **Sleep:** Varied (6-8) - post-match effects
- **DOMS:** Moderate (2-4) - expected after match

---

## 🔗 **QUICK ACCESS METHODS**

### **Method 1: File Explorer**
1. Open File Explorer
2. Navigate to: `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data\`
3. Find files:
   - `jornada_6_sunday_recovery.csv`
   - `Jogo6_sunday_pse.csv`
4. Right-click → Copy or drag to desired location

### **Method 2: Command Line Access**
```powershell
# Navigate to simulation data folder
cd "C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\simulation_data"

# List Day 7 files
dir *sunday*

# Copy files to desktop for easy access
copy jornada_6_sunday_recovery.csv %USERPROFILE%\Desktop\
copy Jogo6_sunday_pse.csv %USERPROFILE%\Desktop\
```

### **Method 3: Direct Web Upload**
1. Open your dashboard: `http://localhost:5173`
2. Go to "Carregar Dados GPS" section
3. Upload `jornada_6_sunday_recovery.csv`
4. Set parameters:
   - **Jornada:** 6
   - **Data:** 26/01/2025
   - **Tipo:** treino

---

## 📋 **MANUAL LOADING PARAMETERS**

### **For GPS Data Upload:**
```
File: jornada_6_sunday_recovery.csv
Jornada: 6
Date: 2025-01-26 (or 26/01/2025)
Type: treino
Description: Sunday Recovery Session
```

### **For PSE Data Upload:**
```
File: Jogo6_sunday_pse.csv
Date: 2025-01-26 (or 26/01/2025)
Session: Recovery
Notes: Post-match recovery patterns
```

---

## 📊 **EXPECTED DATA PATTERNS**

### **GPS Metrics:**
- **Total Distance:** 3,089m - 3,298m (very low)
- **Max Velocity:** 21.1 - 22.8 km/h (reduced)
- **High-Intensity Efforts:** 0-2 (minimal)
- **Accelerations:** 21-34 (light movement)

### **PSE/Wellness Metrics:**
- **Sleep Quality:** 6-8 (post-match variation)
- **Stress:** 3-5 (moderate, post-competition)
- **Fatigue:** 2-4 (recovery focused)
- **DOMS:** 2-4 (expected post-match soreness)
- **RPE:** 2-4 (very light session)
- **Load:** 90-180 (minimal training load)

---

## 🎯 **INTEGRATION WITH EXISTING DATA**

### **Complete Week Overview:**
- **Day 1 (Mon):** Recovery - 6,200m avg
- **Day 2 (Tue):** Technical - 7,150m avg
- **Day 3 (Wed):** Tactical - 8,200m avg
- **Day 4 (Thu):** Physical - 9,400m avg
- **Day 5 (Fri):** Pre-match - 4,800m avg
- **Day 6 (Sat):** Match - 10,800m avg
- **Day 7 (Sun):** Recovery - 3,200m avg ← NEW

### **Weekly Load Pattern:**
```
Mon  Tue  Wed  Thu  Fri  Sat  Sun
 ↓    ↗    ↗    ↗    ↓    ↗    ↓
Low  Med  High Peak Low Match Rest
```

---

## 🔧 **TROUBLESHOOTING**

### **If Files Don't Appear:**
1. Check file path is correct
2. Refresh File Explorer (F5)
3. Ensure files were created successfully

### **If Upload Fails:**
1. Verify backend server is running (`http://localhost:8000`)
2. Check file format matches expected columns
3. Ensure date format is correct (YYYY-MM-DD)

### **If Data Looks Wrong:**
1. Sunday should show lowest metrics of the week
2. Recovery patterns should be evident
3. Post-match fatigue should be reflected in PSE data

---

## 📈 **ANALYTICS OPPORTUNITIES**

### **With Day 7 Data You Can Analyze:**
1. **Complete Weekly Cycle:** Full 7-day training periodization
2. **Recovery Patterns:** Post-match recovery effectiveness
3. **Load Distribution:** Weekly training load management
4. **Fatigue Accumulation:** How players respond to full week
5. **Readiness Indicators:** Preparation for next training cycle

### **Key Insights to Look For:**
- Recovery rate after match day
- Individual vs team recovery patterns
- Optimal rest day activities
- Preparation for next training week

---

## 🎉 **READY FOR MANUAL LOADING**

Your Day 7 files are now ready! You can:
✅ **Access files directly** from the simulation_data folder  
✅ **Copy to desktop** for easy access  
✅ **Upload manually** through your web interface  
✅ **Analyze complete 7-day cycle** with realistic recovery data  

The files represent a realistic Sunday recovery session following Saturday's match, completing your full weekly training cycle for comprehensive analytics testing.
