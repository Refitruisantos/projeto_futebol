# Quick Fix Instructions - Session Creation Error

## What I've Created For You

I've created 3 files to fix the session creation issue:

### 1. `fix_database.ps1` - Automated Fix Script
**This does everything automatically**

### 2. `fix_constraint.sql` - SQL Fix
**Manual database fix if needed**

### 3. `test_session_creation.py` - Test Script
**Verify everything works**

---

## 🚀 EASIEST METHOD - Run the PowerShell Script

### Step 1: Run the Fix Script

1. **Right-click** on `fix_database.ps1`
2. Select **"Run with PowerShell"** or **"Run as Administrator"**
3. The script will:
   - Start PostgreSQL
   - Fix the database constraint
   - Test session creation
   - Show you the results

**That's it!** The script does everything automatically.

---

## 🔧 MANUAL METHOD - If Script Doesn't Work

### Step 1: Start PostgreSQL

**Option A: Windows Services**
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Find "postgresql-x64-16" (or similar)
4. Right-click → Start

**Option B: Command Line (as Administrator)**
```powershell
net start postgresql-x64-16
```

### Step 2: Fix Database Constraint

Open Command Prompt in the project folder and run:

```bash
psql -U postgres -d futebol_analytics -f fix_constraint.sql
```

Password: `postgres`

### Step 3: Test It Works

```bash
python test_session_creation.py
```

---

## ✅ Verify It's Fixed

After running the fix, test session creation:

1. **Open your browser**: http://localhost:5173/sessions
2. **Click "Create Session"**
3. **Fill in the form**
4. **Submit**

It should work now!

---

## 🔍 What Was Wrong?

1. **PostgreSQL wasn't running** - The database service was stopped
2. **Database constraint error** - The `sessoes_local_check` constraint was rejecting "Casa" value
3. **Field validation** - Backend expects specific field names

## 🎯 What the Fix Does

1. **Starts PostgreSQL service**
2. **Updates the constraint** to allow:
   - `NULL` (no location)
   - `'Casa'` (Home)
   - `'Fora'` (Away)
   - `'Neutro'` (Neutral)
3. **Tests** that session creation works

---

## 📞 If You Still Have Issues

Run the test script to see detailed error messages:

```bash
python test_session_creation.py
```

This will show you exactly what's failing:
- ✓ Database connection
- ✓ API server
- ✓ Session creation

---

## 🎉 After It's Fixed

You'll be able to:
- ✅ Create sessions from the frontend
- ✅ Upload GPS/PSE data
- ✅ Upload videos for analysis
- ✅ Use the XGBoost ML predictions
- ✅ View tactical analysis

Everything else is already working - just needed the database to be running!
