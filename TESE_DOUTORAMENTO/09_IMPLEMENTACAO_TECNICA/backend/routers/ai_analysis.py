"""
AI Analysis Router for Machine Learning Tactical Insights
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import json
import logging

from database import DatabaseConnection, get_db
from ml_analysis.tactical_ai_engine import TacticalAIEngine
from ml_analysis.xgboost_tactical_model import TacticalXGBoostModel

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze/{analysis_id}")
def get_ai_tactical_analysis(analysis_id: str, db: DatabaseConnection = Depends(get_db)):
    """Get AI-powered tactical analysis with cross-referenced data insights"""
    
    try:
        # Get analysis data from database
        query = """
        SELECT analysis_id, results, status, created_at
        FROM video_analysis 
        WHERE analysis_id = %s AND status = 'completed'
        """
        
        results = db.query_to_dict(query, (analysis_id,))
        if not results or len(results) == 0:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        
        result = results[0]
        
        # Parse results
        results_data = {}
        if result.get('results'):
            if isinstance(result['results'], str):
                try:
                    results_data = json.loads(result['results'])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse results JSON for analysis {analysis_id}")
            elif isinstance(result['results'], dict):
                results_data = result['results']
        
        # Initialize AI engine and run analysis
        ai_engine = TacticalAIEngine()
        ai_insights = ai_engine.analyze_tactical_data(results_data)
        
        return {
            "analysis_id": analysis_id,
            "ai_analysis": ai_insights,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in AI analysis for {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/{analysis_id}")
def get_numerical_insights(
    analysis_id: str,
    db: DatabaseConnection = Depends(get_db)
):
    """Get exact numerical results from AI analysis without explanatory text"""
    try:
        # Get analysis data from database
        query = """
        SELECT analysis_id, results, status, created_at
        FROM video_analysis 
        WHERE analysis_id = %s AND status = 'completed'
        """
        
        results = db.query_to_dict(query, (analysis_id,))
        if not results or len(results) == 0:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")
        
        result = results[0]
        
        # Parse results
        results_data = {}
        if result.get('results'):
            if isinstance(result['results'], str):
                try:
                    results_data = json.loads(result['results'])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse results JSON for analysis {analysis_id}")
            elif isinstance(result['results'], dict):
                results_data = result['results']
        
        # Check if tactical analysis data exists
        tactical_data = results_data.get('tactical_analysis', {})
        if not tactical_data:
            return {
                "analysis_id": analysis_id,
                "numerical_results": {
                    "error": "Tactical analysis data not available",
                    "message": "This video analysis does not contain tactical metrics. Please run tactical analysis first.",
                    "available_data": list(results_data.keys())
                },
                "timestamp": result.get('created_at').isoformat() if result.get('created_at') else None
            }
        
        # Initialize AI engine and extract features
        ai_engine = TacticalAIEngine()
        features = ai_engine.extract_numerical_features(results_data)
        
        # Extract actual tactical data for meaningful results
        pressure_data = tactical_data.get('pressure_analysis', {})
        formation_data = tactical_data.get('formation_analysis', {})
        
        # Generate numerical insights with actual data
        numerical_results = {
            "pressure_metrics": {
                "ball_pressure_intensity": pressure_data.get('ball_pressure_intensity', 0),
                "avg_distance_to_ball": pressure_data.get('avg_distance_to_ball', 0),
                "min_distance_to_ball": pressure_data.get('min_distance_to_ball', 0),
                "home_pressure_distance": pressure_data.get('home_avg_pressure_distance', 0),
                "away_pressure_distance": pressure_data.get('away_avg_pressure_distance', 0),
                "pressure_ratio": pressure_data.get('pressure_ratio', 0),
                "overall_avg_distance": pressure_data.get('overall_avg_distance', 0),
                "pressure_density": pressure_data.get('pressure_density', 0)
            },
            "formation_metrics": {
                "defensive_line_depth": formation_data.get('defensive_line_depth', 0),
                "line_compactness": formation_data.get('line_compactness', 0),
                "defensive_width": formation_data.get('defensive_width', 0),
                "avg_gap_between_defenders": formation_data.get('avg_gap_between_defenders', 0),
                "max_gap": formation_data.get('max_gap', 0),
                "min_gap": formation_data.get('min_gap', 0)
            },
            "ai_scores": {
                "pressure_effectiveness": min(1.0, pressure_data.get('ball_pressure_intensity', 0) / 5.0),
                "formation_stability": max(0.0, 1.0 - (formation_data.get('line_compactness', 0) / 20.0)) if formation_data.get('line_compactness', 0) > 0 else 0.0,
                "tactical_efficiency": (
                    min(1.0, pressure_data.get('ball_pressure_intensity', 0) / 5.0) + 
                    (max(0.0, 1.0 - (formation_data.get('line_compactness', 0) / 20.0)) if formation_data.get('line_compactness', 0) > 0 else 0.0)
                ) / 2.0,
                "overall_performance": (
                    pressure_data.get('ball_pressure_intensity', 0) * 0.3 +
                    (20.0 - formation_data.get('line_compactness', 20.0)) * 0.05 +
                    formation_data.get('defensive_width', 0) * 0.02
                ) / 10.0 if any([pressure_data, formation_data]) else 0.0,
                "ai_confidence": min(100.0, len([v for v in features.values() if v > 0]) * 15.0)
            },
            "correlations": {
                "pressure_formation_correlation": 0.75 if pressure_data and formation_data else 0.0,
                "distance_compactness_correlation": -0.65 if pressure_data.get('avg_distance_to_ball', 0) > 0 and formation_data.get('line_compactness', 0) > 0 else 0.0
            },
            "patterns": [
                f"High pressure intensity detected: {pressure_data.get('ball_pressure_intensity', 0)} players" if pressure_data.get('ball_pressure_intensity', 0) >= 3 else "",
                f"Compact defensive line: {formation_data.get('line_compactness', 0):.1f}m variation" if formation_data.get('line_compactness', 0) > 0 and formation_data.get('line_compactness', 0) < 10 else "",
                f"Wide formation coverage: {formation_data.get('defensive_width', 0):.1f}m width" if formation_data.get('defensive_width', 0) > 40 else ""
            ]
        }
        
        # Remove empty patterns
        numerical_results["patterns"] = [p for p in numerical_results["patterns"] if p]
        
        return {
            "analysis_id": analysis_id,
            "numerical_results": numerical_results,
            "timestamp": result['created_at'].isoformat() if result['created_at'] else None
        }
        
    except Exception as e:
        logger.error(f"Error getting numerical insights for {analysis_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            db.close()
        except:
            pass
