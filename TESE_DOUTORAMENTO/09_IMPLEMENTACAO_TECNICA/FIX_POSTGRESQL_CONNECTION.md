# 🔧 Fix PostgreSQL Connection Issue for DBeaver

## Problem Identified
PostgreSQL service is running but not accepting TCP/IP connections on localhost:5432. This prevents DBeaver and other external tools from connecting.

## Solution Steps

### Step 1: Edit postgresql.conf
1. Open Command Prompt as Administrator
2. Navigate to PostgreSQL data directory:
   ```cmd
   cd "C:\Program Files\PostgreSQL\16\data"
   ```

3. Edit postgresql.conf (use notepad as admin):
   ```cmd
   notepad postgresql.conf
   ```

4. Find and modify these lines (remove # to uncomment):
   ```
   # Change this line:
   #listen_addresses = 'localhost'
   
   # To this:
   listen_addresses = 'localhost'
   
   # Also ensure:
   port = 5432
   ```

### Step 2: Edit pg_hba.conf
1. In the same directory, edit pg_hba.conf:
   ```cmd
   notepad pg_hba.conf
   ```

2. Add/ensure this line exists in the file:
   ```
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   host    all             all             127.0.0.1/32            md5
   host    all             all             ::1/128                 md5
   ```

### Step 3: Restart PostgreSQL Service
```cmd
net stop postgresql-x64-16
net start postgresql-x64-16
```

### Step 4: Test Connection
```cmd
psql -h localhost -U postgres -d postgres
```

## Alternative: Quick Fix Commands

Run these commands as Administrator:

```powershell
# Stop PostgreSQL
net stop postgresql-x64-16

# Backup original config
copy "C:\Program Files\PostgreSQL\16\data\postgresql.conf" "C:\Program Files\PostgreSQL\16\data\postgresql.conf.backup"

# Enable TCP/IP connections
powershell -Command "(Get-Content 'C:\Program Files\PostgreSQL\16\data\postgresql.conf') -replace '#listen_addresses = ''localhost''', 'listen_addresses = ''localhost''' | Set-Content 'C:\Program Files\PostgreSQL\16\data\postgresql.conf'"

# Start PostgreSQL
net start postgresql-x64-16
```

## DBeaver Connection Parameters After Fix

Once fixed, use these settings in DBeaver:

```
Server Host: localhost
Port: 5432
Database: futebol_tese
Username: postgres
Password: [your_postgres_password]
```

## Verify Fix Works

Test with command line:
```cmd
psql -h localhost -U postgres -d futebol_tese -c "SELECT COUNT(*) FROM atletas;"
```

Should return: count = 28

## If Still Not Working

1. Check Windows Firewall (allow port 5432)
2. Try connecting to 127.0.0.1 instead of localhost
3. Check if another service is using port 5432:
   ```cmd
   netstat -ano | findstr :5432
   ```

## Docker Alternative

If the above doesn't work, consider using Docker:

```powershell
# Stop Windows PostgreSQL service
net stop postgresql-x64-16

# Start PostgreSQL in Docker
docker run --name postgres-futebol -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d postgres:16

# Create database
docker exec -it postgres-futebol psql -U postgres -c "CREATE DATABASE futebol_tese;"
```

Then restore your data from backup or re-run your setup scripts.
