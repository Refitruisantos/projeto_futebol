# ⚽ Soccer Performance Analytics Platform

A comprehensive web-based platform for soccer performance analysis, load monitoring, and ML-powered substitution prediction. Built as part of a doctoral thesis on performance optimization in professional soccer.

## 🎯 Project Overview

This platform integrates GPS tracking, wellness monitoring, video analysis, and machine learning to provide coaches with data-driven insights for player management and tactical decisions.

### Key Features

- **📊 Real-time Dashboard**: Team and individual performance metrics
- **🏃 Load Monitoring**: GPS data analysis (distance, HSR, sprints, accelerations)
- **💪 Wellness Tracking**: Daily questionnaires, RPE, sleep quality, fatigue
- **🤖 ML Predictions**: 
  - Pre-game performance drop prediction (XGBoost + SHAP)
  - Substitution recommendations
- **🎥 Computer Vision**: Automated video analysis for tactical insights
- **📈 Risk Assessment**: ACWR, monotony, strain calculations
- **📋 Session Management**: Track training sessions and matches

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  • Dashboard • Athletes • Sessions • Load Monitoring         │
│  • Wellness • Video Analysis • ML Predictions                │
└─────────────────────────────────────────────────────────────┘
                            ↓ REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  • REST endpoints • Data ingestion • ML pipeline             │
│  • XGBoost models • SHAP explainability                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Database (PostgreSQL)                       │
│  • Athletes • Sessions • GPS • PSE • Wellness • Risk         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **PostgreSQL** 14+
- **Git**

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd 09_IMPLEMENTACAO_TECNICA
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations (if any)
# python migrate.py

# Start backend server
uvicorn main:app --reload --port 8000
```

**Backend runs on**: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env if needed (default backend URL: http://localhost:8000)

# Start development server
npm run dev
```

**Frontend runs on**: `http://localhost:5173`

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb futebol_tese

# Run initial schema (if provided)
psql -d futebol_tese -f database/schema.sql
```

## 📦 Project Structure

```
09_IMPLEMENTACAO_TECNICA/
├── backend/
│   ├── routers/              # API endpoints
│   ├── ml_analysis/          # ML models and pipelines
│   │   ├── pregame_predictor.py    # Pre-game performance drop model
│   │   ├── performance_predictor.py # In-game performance model
│   │   └── saved_models/     # Trained models (pickle)
│   ├── database.py           # Database connection
│   ├── main.py               # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── components/       # Reusable components
│   │   ├── api/              # API client
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── pitch_deck/               # Academic presentation
├── .gitignore
└── README.md
```

## 🤖 Machine Learning Models

### Pre-Game Performance Drop Predictor

Predicts the probability of a player experiencing a physical performance drop during the game **before** it starts.

**Target Variable**:
- HSR/min < 85% of rolling baseline
- Sprint z-score < -1
- Distance drop > 20% vs baseline

**Features** (59 total):
- Cumulative loads (EMA 3/7/14/28 days)
- ACWR ratios
- Wellness metrics
- Exposure (minutes, games)
- GPS trends

**Model**: XGBoost with SHAP explainability

**Endpoints**:
- `POST /api/xgboost/pregame/train` - Train model
- `GET /api/xgboost/pregame/predict?game_date=YYYY-MM-DD` - Get predictions
- `GET /api/xgboost/pregame/status` - Model status

## 📊 Data Flow

1. **Data Ingestion**: Upload GPS (Catapult), PSE, Wellness via UI or API
2. **Processing**: Calculate derived metrics (ACWR, monotony, strain)
3. **Storage**: PostgreSQL with normalized schema
4. **Analysis**: Real-time dashboards and ML predictions
5. **Export**: PDF reports, CSV exports

## 🔒 Environment Variables

### Backend `.env`

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=futebol_tese
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
CORS_ORIGINS=http://localhost:5173,http://localhost:5175
```

### Frontend `.env`

```env
VITE_API_URL=http://localhost:8000/api
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/athletes/` | List all athletes |
| `GET` | `/api/sessions/` | List all sessions |
| `POST` | `/api/ingest/catapult` | Upload GPS data |
| `POST` | `/api/ingest/pse` | Upload PSE data |
| `GET` | `/api/xgboost/pregame/predict` | Pre-game predictions |
| `GET` | `/api/xgboost/substitution-recommendations` | Substitution recommendations |

## 🎨 Frontend Features

- **Dark theme** optimized for coaching staff
- **Responsive design** for desktop and tablet
- **Multi-select & batch operations** (e.g., delete multiple sessions)
- **Real-time data updates**
- **Interactive charts** (Chart.js)
- **SHAP visualizations** for ML explainability

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🐳 Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:80
# PostgreSQL: localhost:5432
```

## 🤝 Contributing

This is a doctoral thesis project. For questions or collaboration:
- **Author**: [Your Name]
- **Email**: [Your Email]
- **Institution**: [Your University]

## 📝 License

This project is part of a doctoral thesis. Please contact the author for usage permissions.

## 🙏 Acknowledgments

- GPS data provider: Catapult Sports
- Computer vision models: YOLOv8
- ML framework: XGBoost + SHAP

## 📖 Citation

If you use this work in your research, please cite:

```bibtex
@phdthesis{yourthesis2026,
  author = {Your Name},
  title = {Performance Prediction and Substitution Optimization in Professional Soccer},
  school = {Your University},
  year = {2026}
}
```

## 🐛 Known Issues

- Video analysis requires significant computational resources
- ML models require at least 15 games for reliable predictions
- Large video files may timeout on slower connections

## 🗺️ Roadmap

- [ ] Real-time GPS tracking integration
- [ ] Mobile app for athletes
- [ ] Advanced tactical analysis
- [ ] Multi-team support
- [ ] Cloud deployment guide

---

**Built with**: React • FastAPI • PostgreSQL • XGBoost • SHAP • YOLOv8
