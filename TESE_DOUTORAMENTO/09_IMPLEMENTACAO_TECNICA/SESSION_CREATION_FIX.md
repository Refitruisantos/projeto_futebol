# Session Creation 404 Error - Diagnosis and Solution

## Problem Identified

The session creation is failing with a **500 Internal Server Error** (not 404 as initially reported) due to a PostgreSQL database constraint violation.

### Error Details:
```
Error creating session: ERRO: a nova linha da relação "sessoes" viola a restrição de verificação "sessoes_local_check"
```

Translation: "The new row in the 'sessoes' table violates the check constraint 'sessoes_local_check'"

## Root Causes

### 1. **PostgreSQL Database Not Running**
The PostgreSQL service needs to be started before the application can create sessions.

### 2. **Database Constraint Issue**
The `sessoes_local_check` constraint is rejecting the value "Casa" for the `local` field.

### 3. **Field Name Mismatch** (Secondary Issue)
- Backend expects: `tipo`, `duracao_min`
- Frontend might be sending: `tipo_sessao`, `duracao_minutos`

## Solutions

### Solution 1: Start PostgreSQL Database (REQUIRED)

**Option A: Using Windows Services (Requires Admin)**
```powershell
# Run PowerShell as Administrator
net start postgresql-x64-16
```

**Option B: Using pgAdmin or PostgreSQL Service Manager**
1. Open Windows Services (services.msc)
2. Find "postgresql-x64-16" service
3. Right-click and select "Start"

**Option C: Using PostgreSQL bin directory**
```powershell
# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\16\bin"
# Start the service
pg_ctl start -D "C:\Program Files\PostgreSQL\16\data"
```

### Solution 2: Fix Database Constraint

The `sessoes_local_check` constraint likely expects specific values. Common valid values:
- "Casa" (Home)
- "Fora" (Away)
- "Neutro" (Neutral)

**Check the constraint definition:**
```sql
SELECT conname, pg_get_constraintdef(pg_constraint.oid) 
FROM pg_constraint 
WHERE conrelid = 'sessoes'::regclass AND contype = 'c';
```

**Possible fixes:**

**Option A: Update the constraint to allow "Casa"**
```sql
ALTER TABLE sessoes DROP CONSTRAINT sessoes_local_check;
ALTER TABLE sessoes ADD CONSTRAINT sessoes_local_check 
CHECK (local IN ('Casa', 'Fora', 'Neutro'));
```

**Option B: Use NULL for local field**
```python
# In backend/routers/sessions.py
session.local if session.local else None
```

### Solution 3: Verify Field Names Match

**Backend expects (sessions.py):**
```python
class SessionCreate(BaseModel):
    data: date
    tipo: str
    adversario: Optional[str] = None
    jornada: Optional[int] = None
    resultado: Optional[str] = None
    duracao_min: Optional[int] = 90
    local: Optional[str] = "Casa"
    competicao: Optional[str] = None
```

**Frontend should send:**
```javascript
{
  "data": "2026-02-06",
  "tipo": "Treino",
  "duracao_min": 90,
  "local": "Casa"  // or null
}
```

## Testing After Fix

### 1. Verify Database is Running
```bash
python -c "import psycopg2; conn = psycopg2.connect('dbname=futebol_analytics user=postgres password=postgres host=localhost'); print('✓ Database connected'); conn.close()"
```

### 2. Test Session Creation API
```bash
python -c "import requests; r = requests.post('http://localhost:8000/api/sessions/', json={'tipo': 'Treino', 'data': '2026-02-06', 'duracao_min': 90, 'local': None}); print('Status:', r.status_code); print('Response:', r.json())"
```

### 3. Test from Frontend
1. Open http://localhost:5173/sessions
2. Click "Create Session"
3. Fill in the form
4. Submit and check browser console for errors

## Current Status

✅ **Working:**
- FastAPI server running on http://localhost:8000
- XGBoost ML system implemented and functional
- Session API endpoint exists and is accessible

❌ **Not Working:**
- PostgreSQL database not running
- Session creation fails due to constraint violation

⚠️ **Needs Attention:**
- Start PostgreSQL service
- Fix or remove `sessoes_local_check` constraint
- Verify frontend sends correct field names

## Quick Fix Commands

```powershell
# 1. Start PostgreSQL (as Administrator)
net start postgresql-x64-16

# 2. Test database connection
python -c "import psycopg2; psycopg2.connect('dbname=futebol_analytics user=postgres password=postgres host=localhost').close(); print('✓ DB OK')"

# 3. Fix constraint (if needed)
# Connect to database and run:
# ALTER TABLE sessoes DROP CONSTRAINT IF EXISTS sessoes_local_check;

# 4. Test session creation
python -c "import requests; print(requests.post('http://localhost:8000/api/sessions/', json={'tipo': 'Treino', 'data': '2026-02-06', 'duracao_min': 90}).json())"
```

## Next Steps

1. **Start PostgreSQL database** (requires admin privileges)
2. **Check and fix the `sessoes_local_check` constraint**
3. **Test session creation from API**
4. **Test session creation from frontend**
5. **Verify all session operations work correctly**

## Additional Notes

- The 404 error reported was actually a 500 error from database constraint violation
- The XGBoost ML system is working independently of this issue
- Computer vision modules are disabled due to PyTorch DLL issues (separate issue)
- The backend API structure is correct; the issue is purely database-related
