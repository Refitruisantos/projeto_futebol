# 🚀 Start Backend & Frontend Servers

## Quick Start Commands

### Open TWO PowerShell windows and run these commands:

---

## 🔧 PowerShell Window 1: Backend (FastAPI)

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Access:**
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

---

## 🎨 PowerShell Window 2: Frontend (React)

```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend
npm run dev
```

**Expected output:**
```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

**Access:**
- Dashboard: http://localhost:5173

---

## 📋 Step-by-Step

### 1. Start Backend First

Open PowerShell window 1:
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Wait for: `Application startup complete`

### 2. Start Frontend Second

Open PowerShell window 2:
```powershell
cd C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\frontend
npm run dev
```

Wait for: `Local: http://localhost:5173/`

### 3. Open in Browser

```powershell
Start-Process "http://localhost:5173"
```

---

## 🔍 What You'll See

### Dashboard (http://localhost:5173)
- Team overview with risk indicators
- Athletes performance table
- Load metrics and risk levels
- Weekly trends

### API Docs (http://127.0.0.1:8000/docs)
- All available endpoints
- Interactive testing
- Mock data generation
- Request/response schemas

---

## 🛑 Stop Servers

Press `Ctrl+C` in each PowerShell window to stop the servers.

---

## ✅ Verify Everything Works

Test backend:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
```

Should return: `{"status":"healthy"}`

Test frontend:
```powershell
Start-Process "http://localhost:5173"
```

Should open dashboard in browser.
