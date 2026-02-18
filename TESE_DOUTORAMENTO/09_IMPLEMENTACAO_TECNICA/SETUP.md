# 🚀 Setup Guide

## Prerequisites

Ensure you have the following installed:
- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** 14+
- **Git**

## Database Setup

### 1. Create PostgreSQL Database

```bash
# Create database
createdb futebol_tese

# If you have a schema file, run it
# psql -d futebol_tese -f database/schema.sql
```

### 2. Database Schema

The main tables include:
- `atletas` - Athletes information
- `sessoes` - Training sessions and games
- `dados_gps` - GPS tracking data
- `dados_pse` - RPE and internal load data
- `dados_wellness` - Daily wellness questionnaires
- `metricas_carga` - Calculated load metrics
- `risk_assessment` - Risk scores and predictions

## Backend Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required: DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
```

Example `.env`:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=futebol_tese
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
CORS_ORIGINS=http://localhost:5173,http://localhost:5175
```

### 5. Start backend server

```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**

API docs at: **http://localhost:8000/docs**

## Frontend Setup

### 1. Navigate to frontend directory

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment (optional)

```bash
# Copy example environment file
cp .env.example .env

# Default values should work for local development
```

Example `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

### 4. Start development server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## First Time Setup

### 1. Create athletes

Navigate to **Athletes** page and click "Novo Atleta" to add players.

### 2. Create sessions

Navigate to **Sessions** page and click "Nova Sessão" to add training sessions or games.

### 3. Upload data

For each session, you can upload:
- **GPS data** (Catapult CSV or PDF)
- **PSE data** (RPE/wellness CSV or PDF)
- **Video** (MP4, AVI, MOV for computer vision analysis)

### 4. Train ML models

Navigate to Dashboard → ML Predictions tab, or use API:

```bash
# Train pre-game performance drop model
curl -X POST http://localhost:8000/api/xgboost/pregame/train

# Check model status
curl http://localhost:8000/api/xgboost/pregame/status

# Get predictions for next game
curl http://localhost:8000/api/xgboost/pregame/predict
```

## Verification

### Check Backend

```bash
# Test API
curl http://localhost:8000/api/athletes/

# Check database connection
curl http://localhost:8000/docs
```

### Check Frontend

Open browser to **http://localhost:5173** and verify:
- ✅ Dashboard loads
- ✅ Athletes page works
- ✅ Sessions page works
- ✅ No console errors

## Troubleshooting

### Backend won't start

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and install dependencies

**Issue**: Database connection error
- **Solution**: Check PostgreSQL is running and `.env` credentials are correct

### Frontend won't start

**Issue**: `Cannot find module 'react'`
- **Solution**: Run `npm install` in frontend directory

**Issue**: API connection error
- **Solution**: Ensure backend is running on port 8000

### ML Models fail to train

**Issue**: "Model not trained yet"
- **Solution**: You need at least 7 games with GPS data to train models
- **Alternative**: Use the in-game performance predictor which works with less data

### Video analysis fails

**Issue**: YOLOv8 model not found
- **Solution**: Models should be in `backend/` directory. They're large files (~100MB each)
- **Download**: If missing, they'll auto-download on first use

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## Data Privacy

⚠️ **Important**: This system handles sensitive athlete health data. Ensure:
- Database is secured with strong passwords
- Backend API uses HTTPS in production
- Comply with GDPR/data protection regulations
- Athletes have consented to data collection

## Support

For issues or questions:
- Check the [README.md](README.md) for architecture overview
- Review API docs at `/docs` endpoint
- Create an issue on GitHub
