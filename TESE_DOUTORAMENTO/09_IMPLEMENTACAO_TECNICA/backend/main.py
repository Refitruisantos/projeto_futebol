from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers with error handling for optional dependencies
from routers import athletes, xgboost_analysis, sessions, metrics, ingestion, load_metrics, mock_data, opponents

# Try to import computer vision routers (requires PyTorch)
try:
    from routers import computer_vision, video_visualization
    CV_AVAILABLE = True
except Exception as e:
    logger.warning(f"Computer vision modules not available: {e}")
    CV_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 FastAPI server starting...")
    yield
    logger.info("🔒 FastAPI server shutting down...")


app = FastAPI(
    title="Futebol Analytics API",
    description="API for soccer GPS/PSE data ingestion and analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(athletes.router, prefix="/api/athletes", tags=["Athletes"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(ingestion.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(opponents.router, prefix="/api/opponents", tags=["Opponents"])

# Include computer vision routers only if available
if CV_AVAILABLE:
    app.include_router(computer_vision.router, prefix="/api/computer-vision", tags=["Computer Vision"])
    app.include_router(video_visualization.router, prefix="/api/video-visualization", tags=["Video Visualization"])
    logger.info("✓ Computer vision modules loaded")
else:
    logger.warning("⚠ Computer vision modules disabled due to missing dependencies")

app.include_router(xgboost_analysis.router, prefix="/api/xgboost", tags=["XGBoost ML"])
app.include_router(load_metrics.router)
app.include_router(mock_data.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Futebol Analytics API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
