# 🔧 Fix: Start PostgreSQL Database

## The Issue

Backend is running but can't connect to PostgreSQL database:
```
Connection refused - port 5432
Is the server running?
```

---

## ✅ Solution: Start PostgreSQL Service

### Option 1: Start PostgreSQL Service (Windows)

```powershell
# Start PostgreSQL service
Start-Service -Name postgresql*

# Or use full service name (check which version you have)
Start-Service -Name postgresql-x64-15
# Or
Start-Service -Name postgresql-x64-14
```

### Option 2: If PostgreSQL is Installed as Portable/Manual

```powershell
# Find your PostgreSQL installation
cd "C:\Program Files\PostgreSQL\15\bin"  # Adjust version number

# Start manually
.\pg_ctl.exe -D "C:\Program Files\PostgreSQL\15\data" start
```

### Option 3: Check If PostgreSQL Is Installed

```powershell
# Check for PostgreSQL service
Get-Service -Name postgresql* -ErrorAction SilentlyContinue

# Check if PostgreSQL is installed
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*PostgreSQL*" }
```

---

## 🔍 Verify Database Is Running

```powershell
# Test connection
Test-NetConnection -ComputerName localhost -Port 5432
```

Should show: **TcpTestSucceeded: True**

---

## 🔄 After Database Starts

The backend will automatically reconnect. Just refresh your browser:

1. Start PostgreSQL ✅
2. Backend connects to DB ✅
3. Refresh browser (F5) ✅
4. Dashboard loads data ✅

---

## ⚠️ If PostgreSQL Is Not Installed

You need to either:

1. **Install PostgreSQL** (if you want real database functionality)
   - Download: https://www.postgresql.org/download/windows/
   - Install and configure

2. **Use Mock Data Only** (for testing without database)
   - The mock data generation works without database
   - But dashboard needs DB to show real metrics

---

## 📝 Quick Command Summary

```powershell
# 1. Start PostgreSQL
Start-Service -Name postgresql*

# 2. Verify it's running
Test-NetConnection -ComputerName localhost -Port 5432

# 3. Refresh browser
Start-Process "http://localhost:5173"
```
