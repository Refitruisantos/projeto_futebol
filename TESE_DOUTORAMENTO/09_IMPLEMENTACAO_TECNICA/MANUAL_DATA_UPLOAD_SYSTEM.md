# 📋 MANUAL DATA UPLOAD SYSTEM
## Complete Guide for Real Data Preparation and Upload

---

## 🎯 **OVERVIEW**

This system prepares you to manually upload real football data when you collect it from actual training sessions and matches. You'll have full control over data validation, upload tracking, and error management.

---

## 📊 **DATA FORMAT TEMPLATES**

### **GPS Data Template (Required Columns)**
```csv
player,total_distance_m,max_velocity_kmh,acc_b1_3_total_efforts,decel_b1_3_total_efforts,efforts_over_19_8_kmh,distance_over_19_8_kmh,efforts_over_25_2_kmh,velocity_b3_plus_total_efforts
PLAYER_NAME,8456.3,29.2,45,42,18,287.4,8,67
```

**Column Specifications:**
- `player` - Exact player name (must match database)
- `total_distance_m` - Total distance in meters (float)
- `max_velocity_kmh` - Maximum velocity in km/h (float)
- `acc_b1_3_total_efforts` - Acceleration efforts (integer)
- `decel_b1_3_total_efforts` - Deceleration efforts (integer)
- `efforts_over_19_8_kmh` - High-intensity efforts (integer)
- `distance_over_19_8_kmh` - High-intensity distance in meters (float)
- `efforts_over_25_2_kmh` - Very high-intensity efforts (integer)
- `velocity_b3_plus_total_efforts` - High-velocity efforts (integer)

### **PSE/Wellness Data Template (Required Columns)**
```csv
Nome,Pos,Sono,Stress,Fadiga,DOMS,DORES MUSCULARES,VOLUME,Rpe,CARGA
PLAYER_NAME,DC,7,4,3,3,3,90,6,540
```

**Column Specifications:**
- `Nome` - Player name (must match database)
- `Pos` - Position (DC, MC, EX, AV, GR)
- `Sono` - Sleep quality (1-10 scale)
- `Stress` - Stress level (1-5 scale)
- `Fadiga` - Fatigue level (1-5 scale)
- `DOMS` - Delayed onset muscle soreness (1-5 scale)
- `DORES MUSCULARES` - Muscle pain (1-5 scale)
- `VOLUME` - Session duration in minutes (integer)
- `Rpe` - Rate of perceived exertion (1-10 scale)
- `CARGA` - Training load (usually RPE × Duration)

---

## 🔧 **DATA VALIDATION CONSTRAINTS**

### **GPS Data Constraints:**
- **Distance:** 0 - 15,000m (typical range)
- **Max Velocity:** 0 - 40 km/h (human limits)
- **Efforts:** 0 - 200 (reasonable session limits)
- **Player Names:** Must exist in database

### **PSE Data Constraints:**
- **Sleep (Sono):** 1-10 (database constraint)
- **Stress:** 1-5 (database constraint)
- **Fatigue (Fadiga):** 1-5 (database constraint)
- **DOMS:** 1-5 (database constraint)
- **RPE:** 1-10 (standard scale)
- **Duration:** 30-180 minutes (typical sessions)
- **Load:** Positive integer (calculated or measured)

---

## 📝 **MANUAL UPLOAD WORKFLOW**

### **STEP 1: Data Collection**
When you collect real data:
1. **Export from GPS system** (Catapult, STATSports, etc.)
2. **Collect wellness surveys** from players
3. **Record session metadata** (date, type, duration, conditions)

### **STEP 2: Data Preparation**
1. **Format GPS data** using the template above
2. **Format PSE data** using the wellness template
3. **Validate player names** match your database exactly
4. **Check data ranges** fit the constraints
5. **Save as CSV files** with descriptive names

### **STEP 3: Pre-Upload Validation**
Run validation before uploading:
```powershell
python validate_upload_data.py your_gps_file.csv your_pse_file.csv
```

### **STEP 4: Upload Process**
1. **Upload GPS data** through web interface
2. **Upload PSE data** using Python script
3. **Verify upload success** in dashboard
4. **Document in upload log**

### **STEP 5: Post-Upload Verification**
1. **Check dashboard** displays new data
2. **Verify player counts** match expected
3. **Test analytics** with new data
4. **Create backup** of uploaded data

---

## 🛠️ **VALIDATION TOOLS**

### **Data Validation Script**
```python
# validate_upload_data.py - checks data before upload
def validate_gps_data(csv_file):
    # Check columns, data types, ranges
    # Verify player names exist in database
    # Report any issues before upload

def validate_pse_data(csv_file):
    # Check wellness data constraints
    # Validate scale ranges (1-5, 1-10)
    # Check for missing values
```

### **Player Name Checker**
```python
# check_player_names.py - verify names match database
def get_database_players():
    # Returns list of all active players
    
def check_csv_names(csv_file):
    # Compares CSV names to database
    # Suggests corrections for mismatches
```

---

## 📂 **FILE NAMING CONVENTIONS**

### **Recommended Naming:**
```
GPS Files:
- gps_YYYY-MM-DD_session-type.csv
- gps_2025-03-15_training.csv
- gps_2025-03-18_match.csv

PSE Files:
- pse_YYYY-MM-DD_session-type.csv
- pse_2025-03-15_training.csv
- pse_2025-03-18_match.csv

Examples:
- gps_2025-03-15_tactical-training.csv
- pse_2025-03-15_tactical-training.csv
- gps_2025-03-18_league-match.csv
- pse_2025-03-18_league-match.csv
```

---

## 📊 **UPLOAD TRACKING SYSTEM**

### **Upload Log Template**
```
Date: 2025-03-15
Session: Tactical Training
GPS File: gps_2025-03-15_tactical-training.csv
PSE File: pse_2025-03-15_tactical-training.csv
Session ID: 456
GPS Records: 28/28 ✅
PSE Records: 28/28 ✅
Notes: All data uploaded successfully
```

### **Session Management**
- **View uploads:** Use dashboard history
- **Delete mistakes:** Use deletion tool
- **Backup data:** Export before major changes
- **Track changes:** Document all modifications

---

## 🔄 **ERROR HANDLING PROCEDURES**

### **Common Upload Errors:**

#### **1. Player Name Mismatch**
```
Error: Player not found: "João Silva"
Solution: Check exact name in database
Database has: "João Pedro Silva"
```

#### **2. Constraint Violations**
```
Error: Sleep value 12 exceeds maximum 10
Solution: Check PSE data ranges
Correct range: 1-10 for sleep quality
```

#### **3. Missing Columns**
```
Error: Missing required column 'max_velocity_kmh'
Solution: Add missing column to CSV
Check template for required columns
```

#### **4. Data Type Errors**
```
Error: Invalid data type for distance
Solution: Ensure numeric values only
Remove text, use decimal point (not comma)
```

---

## 🎯 **REAL DATA PREPARATION CHECKLIST**

### **Before Each Upload:**
- [ ] GPS data exported from tracking system
- [ ] PSE surveys collected from all players
- [ ] Session metadata recorded
- [ ] Player names verified against database
- [ ] Data ranges checked against constraints
- [ ] CSV files formatted correctly
- [ ] Validation script run successfully
- [ ] Backup created of original data

### **During Upload:**
- [ ] GPS file uploaded through web interface
- [ ] Upload success confirmed (28/28 players)
- [ ] PSE data uploaded via script
- [ ] Session appears in dashboard
- [ ] Data displays correctly in analytics

### **After Upload:**
- [ ] Upload logged in tracking system
- [ ] Dashboard tested with new data
- [ ] Analytics calculations verified
- [ ] Backup created of uploaded session
- [ ] Notes documented for future reference

---

## 🔧 **TROUBLESHOOTING GUIDE**

### **Upload Fails Completely:**
1. Check file format (CSV with correct headers)
2. Verify player names match database exactly
3. Ensure data types are correct (numbers as numbers)
4. Check for special characters or encoding issues

### **Partial Upload Success:**
1. Note which players failed
2. Check failed player names in database
3. Verify data ranges for failed records
4. Re-upload corrected data for failed players

### **Dashboard Doesn't Show Data:**
1. Refresh browser cache
2. Check session was created (view upload history)
3. Verify backend server is running
4. Check database connection

### **Analytics Don't Calculate:**
1. Ensure both GPS and PSE data uploaded
2. Check data completeness
3. Verify calculation functions are working
4. Test with known good data first

---

## 📈 **SCALING FOR MULTIPLE SESSIONS**

### **Weekly Upload Process:**
1. **Monday:** Collect weekend match data
2. **Daily:** Collect training session data
3. **Weekly:** Batch upload all sessions
4. **Monthly:** Backup and archive data

### **Season Management:**
- **Pre-season:** Set up player database
- **In-season:** Regular upload routine
- **Post-season:** Complete data export
- **Off-season:** System maintenance

---

## 🎯 **READY FOR REAL DATA**

This system provides:
✅ **Complete data templates** for GPS and PSE  
✅ **Validation tools** to check data quality  
✅ **Upload tracking** for full control  
✅ **Error handling** procedures  
✅ **Backup and recovery** systems  
✅ **Scaling guidance** for multiple sessions  

You're now prepared to handle real football data with confidence, full tracking, and complete control over the upload process!
