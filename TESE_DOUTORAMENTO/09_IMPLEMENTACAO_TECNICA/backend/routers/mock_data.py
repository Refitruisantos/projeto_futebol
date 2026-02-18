"""
Mock Data Generation API Endpoints

Provides endpoints for generating realistic synthetic training data for:
- Testing ML models
- Backtesting forecasting algorithms
- Simulating scenarios (injuries, load management, etc.)
- Training with diverse edge cases
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from database import get_db, DatabaseConnection
from mock_data_generator import MockDataGenerator, GenerationConfig, ScenarioType

router = APIRouter(prefix="/api/mock-data", tags=["Mock Data Generation"])


class ScenarioEnum(str, Enum):
    """Available scenario types"""
    NORMAL = "normal_season"
    TAPER = "taper_period"
    OVERLOAD = "overload_period"
    INJURY_RECOVERY = "injury_recovery"
    GAME_CONGESTION = "game_congestion"
    OFF_SEASON = "off_season"


class GenerationRequest(BaseModel):
    """Request body for data generation"""
    start_date: datetime = Field(..., description="Start date for generation")
    end_date: datetime = Field(..., description="End date for generation")
    
    num_athletes: int = Field(default=20, ge=1, le=50, description="Number of athletes to generate")
    positions: List[str] = Field(
        default=['GR', 'DC', 'DL', 'MC', 'EX', 'AV'],
        description="Athlete positions to distribute"
    )
    
    training_days: List[int] = Field(
        default=[0, 1, 2, 3, 4],  # Mon-Fri
        description="Days of week for training (0=Monday, 6=Sunday)"
    )
    game_days: List[int] = Field(
        default=[5],  # Saturday
        description="Days of week for games"
    )
    sessions_per_week: int = Field(default=6, ge=1, le=10)
    
    scenario: ScenarioEnum = Field(
        default=ScenarioEnum.NORMAL,
        description="Scenario type to simulate"
    )
    
    fidelity: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="How close to real data (0=synthetic, 1=very realistic)"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )
    
    write_to_db: bool = Field(
        default=False,
        description="Write generated data to database (use with caution!)"
    )


class GenerationResponse(BaseModel):
    """Response from generation endpoint"""
    success: bool
    message: str
    stats: dict
    data_preview: Optional[dict] = None
    download_url: Optional[str] = None


@router.post("/generate", response_model=GenerationResponse)
def generate_mock_data(
    request: GenerationRequest
):
    """
    Generate realistic mock training data
    
    This endpoint creates synthetic data based on:
    - Statistical profiles from real data
    - Configurable scenarios (normal, taper, injury, etc.)
    - Controlled randomness with optional seed
    
    **Use Cases:**
    - Testing forecasting models
    - Simulating edge cases
    - Backtesting with controlled scenarios
    - Training ML models
    
    **Scenarios:**
    - `normal_season`: Regular training/game schedule
    - `taper_period`: Load reduction before important match
    - `overload_period`: Intensified training block
    - `injury_recovery`: Progressive return to full load
    - `game_congestion`: High match frequency (3 games/week)
    - `off_season`: Reduced activity
    """
    try:
        # Create configuration
        config = GenerationConfig(
            start_date=request.start_date,
            end_date=request.end_date,
            num_athletes=request.num_athletes,
            positions=request.positions,
            training_days=request.training_days,
            game_days=request.game_days,
            sessions_per_week=request.sessions_per_week,
            scenario=ScenarioType(request.scenario.value),
            fidelity=request.fidelity,
            seed=request.seed
        )
        
        # Generate data (without DB connection for now)
        generator = MockDataGenerator(config, db_connection=None)
        dataset = generator.generate_full_dataset()
        
        # Statistics
        stats = {
            'athletes_generated': len(dataset['athletes']),
            'sessions_generated': len(dataset['sessions']),
            'pse_records': len(dataset['pse_data']),
            'gps_records': len(dataset['gps_data']),
            'date_range': {
                'start': request.start_date.isoformat(),
                'end': request.end_date.isoformat(),
                'days': (request.end_date - request.start_date).days + 1
            },
            'scenario': request.scenario.value,
            'seed': request.seed
        }
        
        # Preview (first 5 records of each type)
        preview = {
            'athletes_sample': dataset['athletes'][:5],
            'sessions_sample': dataset['sessions'][:5],
            'pse_sample': dataset['pse_data'][:5],
            'gps_sample': dataset['gps_data'][:5] if dataset['gps_data'] else []
        }
        
        # Optionally write to database (sandbox schema recommended)
        if request.write_to_db:
            write_count = _write_to_database(dataset, db)
            stats['records_written'] = write_count
            message = f"Generated and wrote {write_count} records to database"
        else:
            message = f"Generated {stats['pse_records']} mock records (not written to DB)"
        
        return GenerationResponse(
            success=True,
            message=message,
            stats=stats,
            data_preview=preview
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/scenarios")
def list_scenarios():
    """
    List available generation scenarios
    
    Returns description of each scenario type and when to use it
    """
    scenarios = {
        'normal_season': {
            'description': 'Regular training and match schedule',
            'use_case': 'Baseline testing, general model training',
            'characteristics': 'Balanced load, 5-6 sessions/week'
        },
        'taper_period': {
            'description': 'Load reduction before important competition',
            'use_case': 'Testing model response to planned load drops',
            'characteristics': 'Gradual 30% load reduction, reduced frequency'
        },
        'overload_period': {
            'description': 'Intensified training block',
            'use_case': 'Testing overtraining detection',
            'characteristics': '20% load increase, higher monotony risk'
        },
        'injury_recovery': {
            'description': 'Progressive return to training after injury',
            'use_case': 'Testing recovery protocols, load progression',
            'characteristics': 'Start at 50% load, increase 10% per week'
        },
        'game_congestion': {
            'description': 'High match frequency (3+ games/week)',
            'use_case': 'Testing fatigue accumulation, recovery strategies',
            'characteristics': 'Reduced training, high game load, fatigue'
        },
        'off_season': {
            'description': 'Reduced activity during off-season',
            'use_case': 'Testing detraining detection',
            'characteristics': 'Low frequency, low intensity'
        }
    }
    return scenarios


@router.get("/profile")
def get_data_profile(db: DatabaseConnection = Depends(get_db)):
    """
    Get statistical profile of current training data
    
    Returns distribution parameters used for realistic generation:
    - Mean, std, min, max for each metric
    - Distributions by position and session type
    - Temporal patterns (seasonality, trends)
    - Correlations between metrics
    """
    try:
        from data_profiler import DataProfiler
        
        profiler = DataProfiler(db)
        profile = profiler.create_full_profile()
        
        return {
            'success': True,
            'profile': profile.to_dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profiling failed: {str(e)}")


@router.post("/validate")
def validate_generated_data(
    generated_data: dict,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Validate generated data against real data profile
    
    Checks:
    - Distribution similarity (KS test)
    - Constraint violations
    - Correlation preservation
    - Realistic value ranges
    """
    try:
        from data_validator import DataValidator
        
        validator = DataValidator(db)
        validation_results = validator.validate_mock_data(generated_data)
        
        return {
            'success': True,
            'validation': validation_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


def _write_to_database(dataset: dict, db: DatabaseConnection) -> int:
    """Write generated data to database (use with caution!)"""
    records_written = 0
    
    # Note: This should ideally write to a separate schema or sandbox
    # For safety, we'll skip actual writing in this example
    # In production, implement proper sandbox schema
    
    # Pseudo-code for writing:
    # for athlete in dataset['athletes']:
    #     db.execute_query("INSERT INTO sandbox.atletas (...) VALUES (...)", athlete)
    #     records_written += 1
    
    # for session in dataset['sessions']:
    #     db.execute_query("INSERT INTO sandbox.sessoes (...) VALUES (...)", session)
    #     records_written += 1
    
    # ... etc for PSE and GPS data
    
    return records_written
