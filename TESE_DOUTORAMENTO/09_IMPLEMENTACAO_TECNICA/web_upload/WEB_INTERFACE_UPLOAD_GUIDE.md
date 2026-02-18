# 📱 WEB INTERFACE ONLY - MANUAL UPLOAD GUIDE
## Upload Files Using Only Your Web Dashboard

---

## 🎯 **WEB-ONLY UPLOAD PROCESS**

You want to upload data manually using only your web interface at `http://localhost:5173/upload` - no PowerShell scripts needed.

---

## 📊 **FILE READY FOR WEB UPLOAD**

### **GPS Data File**
📄 **File:** `gps_physical_training.csv`  
📍 **Location:** `web_upload/gps_physical_training.csv`

**Session Details:**
- **Type:** Physical Training
- **Players:** 20 athletes  
- **Distance:** 8,712m - 9,456m (high intensity)
- **Max Speed:** 29.7 - 32.1 km/h

---

## 🔄 **STEP-BY-STEP WEB UPLOAD**

### **STEP 1: Open Your Dashboard**
1. Go to `http://localhost:5173/upload`
2. You'll see the "Upload Catapult CSV" interface

### **STEP 2: Upload GPS File**
1. **Click "Escolher ficheiro"**
2. **Navigate to:** `C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\web_upload\gps_physical_training.csv`
3. **Select the file**
4. **Set parameters:**
   ```
   Jornada: 20
   Data da Sessão: 20/03/2025
   ```
5. **Click "Carregar"**

### **STEP 3: Check Upload Results**
- ✅ Should show "20/20 registos inseridos"
- ✅ New session appears in "Histórico de Uploads"
- ✅ Session ID will be displayed

### **STEP 4: View in Dashboard**
1. Navigate to Sessions page
2. Find Jornada 20 entry
3. View GPS data and analytics

---

## ⚠️ **IMPORTANT NOTES**

### **PSE Data Upload:**
Your web interface currently only supports GPS data upload. For PSE/wellness data, you would need:
- A separate PSE upload interface (not currently available)
- Or database direct insert
- Or backend API endpoint

### **What You Can Do With Web Interface:**
✅ **GPS Data:** Full upload capability  
✅ **Session Creation:** Automatic  
✅ **Upload Tracking:** View history  
✅ **Data Verification:** Check in dashboard  
❌ **PSE Data:** No web interface available  

---

## 🎯 **PRACTICE SESSION**

### **Upload This File:**
- **File:** `gps_physical_training.csv`
- **Jornada:** 20
- **Date:** 20/03/2025
- **Expected Result:** 20 GPS records imported

### **After Upload:**
1. Check upload history shows new session
2. Navigate to Sessions page
3. View Jornada 20 data
4. Test analytics with new GPS data

---

## 🗑️ **DELETE IF NEEDED**

If you want to remove this practice session:
1. Note the Session ID from upload results
2. Use database management tools to delete
3. Or keep it as practice data

---

## 📋 **READY FOR WEB-ONLY UPLOAD**

You now have:
✅ **GPS file ready** for web interface upload  
✅ **Step-by-step instructions** for web-only process  
✅ **No PowerShell required** - pure web interface  
✅ **Practice session** to test manual upload workflow  

Simply use your web dashboard to upload the GPS file and practice the manual upload process!
