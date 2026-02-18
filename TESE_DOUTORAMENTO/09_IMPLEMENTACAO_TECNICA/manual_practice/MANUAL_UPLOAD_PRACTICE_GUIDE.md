# 📋 MANUAL UPLOAD PRACTICE SESSION
## Physical Training Session - March 15, 2025

---

## 🏃 **SESSION DETAILS**

**Session Type:** Physical Training  
**Date:** March 15, 2025  
**Duration:** 120 minutes  
**Intensity:** High (RPE 5-9)  
**Focus:** Conditioning, fitness work, high-intensity efforts  
**Players:** 20 athletes  

---

## 📊 **FILES READY FOR MANUAL UPLOAD**

### **GPS Data File**
📄 **File:** `gps_2025-03-15_physical-training.csv`  
📍 **Location:** `manual_practice/gps_2025-03-15_physical-training.csv`

**Session Characteristics:**
- **Distance:** 8,712m - 9,456m (high physical training)
- **Max Speed:** 29.7 - 32.1 km/h (peak efforts)
- **High-Intensity Efforts:** 18-26 efforts over 19.8 km/h
- **Accelerations:** 51-65 (conditioning work)

### **PSE Data File**
📄 **File:** `pse_2025-03-15_physical-training.csv`  
📍 **Location:** `manual_practice/pse_2025-03-15_physical-training.csv`

**Wellness Characteristics:**
- **Sleep:** 5-8 (varied individual responses)
- **Stress:** 3-6 (high physical stress expected)
- **Fatigue:** 2-5 (building through session)
- **DOMS:** 2-5 (muscle soreness from intensity)
- **RPE:** 5-9 (moderate to very high effort)
- **Load:** 600-1080 (high training loads)

---

## 🔄 **STEP-BY-STEP MANUAL UPLOAD PROCESS**

### **STEP 1: Validate Your Data**
Before uploading, run validation:
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA

# Validate both files
python validate_upload_data.py manual_practice/gps_2025-03-15_physical-training.csv manual_practice/pse_2025-03-15_physical-training.csv

# Check player names specifically
python check_player_names.py manual_practice/gps_2025-03-15_physical-training.csv
```

**Expected Results:**
- ✅ All required columns present
- ✅ Data values within valid ranges
- ✅ Player names match database
- ✅ Ready for upload

### **STEP 2: Upload GPS Data**
1. **Open your dashboard:** `http://localhost:5173/upload`
2. **Click "Escolher ficheiro"**
3. **Navigate to:** `manual_practice/gps_2025-03-15_physical-training.csv`
4. **Set parameters:**
   ```
   Jornada: 15
   Data da Sessão: 15/03/2025
   Tipo: treino
   ```
5. **Click "Carregar"**

**Expected Results:**
- ✅ Records inserted: 20/20 players
- ✅ Session created (note the Session ID)
- ✅ No errors or warnings

### **STEP 3: Upload PSE Data**
After GPS upload succeeds, upload PSE data using script:
```powershell
# Create PSE upload script for this session
python upload_practice_pse.py
```

**Expected Results:**
- ✅ 20 PSE records inserted
- ✅ Complete session with GPS + PSE data
- ✅ Session appears in upload history

### **STEP 4: Verify Upload Success**
1. **Check upload history** in web interface
2. **Navigate to Sessions page** - find Jornada 15
3. **View session details** - verify GPS and PSE data
4. **Test dashboard analytics** with new data

---

## 🎯 **PRACTICE OBJECTIVES**

### **What You'll Learn:**
1. **Data validation** before upload
2. **Web interface upload** process
3. **Error handling** and troubleshooting
4. **Upload tracking** and verification
5. **Session management** and deletion

### **Skills You'll Practice:**
- Formatting real data for upload
- Using validation tools
- Managing upload errors
- Tracking upload history
- Verifying data integrity

---

## 🔧 **TROUBLESHOOTING PRACTICE**

### **If GPS Upload Fails:**
1. Check file path is correct
2. Verify player names match database exactly
3. Ensure data values are within ranges
4. Check CSV format (commas, no extra spaces)

### **If PSE Upload Fails:**
1. Ensure GPS session was created first
2. Check PSE constraint values (1-5, 1-10 scales)
3. Verify player count matches GPS data
4. Check for missing or invalid values

### **If Data Doesn't Appear:**
1. Refresh dashboard browser
2. Check session was created (upload history)
3. Verify backend server is running
4. Check database connection

---

## 📊 **EXPECTED ANALYTICS RESULTS**

### **Physical Training Patterns:**
- **High distances** (8,700m+ average)
- **Peak velocities** (30+ km/h)
- **High RPE values** (7-9 range)
- **Elevated training loads** (800+ average)

### **Individual Variations:**
- **Goalkeepers** (Paulo Gomes): Lower distance, RPE
- **Midfielders** (Carlos, André): Highest efforts
- **Defenders** (Tiago Silva, Diogo): Moderate loads
- **Forwards** (José Mendes): High intensity bursts

---

## 🗑️ **CLEANUP AFTER PRACTICE**

If you want to delete this practice session:
```powershell
# Use interactive deletion tool
python delete_session_data.py

# Choose option 4: Delete all data for jornada
# Enter jornada number: 15
# Confirm: yes
```

Or delete specific session:
```powershell
# Choose option 3: Delete specific session
# Enter the Session ID from upload results
```

---

## 🎉 **READY FOR MANUAL UPLOAD PRACTICE**

Your practice session includes:
✅ **Realistic GPS data** (20 players, physical training)  
✅ **Corresponding PSE data** (high-intensity wellness metrics)  
✅ **Validation tools** ready to test  
✅ **Step-by-step instructions** for upload process  
✅ **Troubleshooting guide** for common issues  
✅ **Cleanup procedures** to reset after practice  

This gives you hands-on experience with the complete manual upload workflow you'll use for real data!
