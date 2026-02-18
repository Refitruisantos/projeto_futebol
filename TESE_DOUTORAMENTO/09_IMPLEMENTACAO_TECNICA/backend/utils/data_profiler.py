"""
Data Profiler: Extract Statistical Patterns from Real Training Data

Analyzes existing data to create a reusable profile for realistic mock generation:
- Distribution parameters (mean, std, quantiles) by column
- Conditional distributions (by athlete, session type, position)
- Correlations between metrics
- Temporal patterns (weekly seasonality, trends)
- Missing data patterns
"""

import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json


@dataclass
class ColumnProfile:
    """Statistical profile for a single column"""
    name: str
    dtype: str
    count: int
    missing_count: int
    missing_pct: float
    
    # Numerical stats
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    q25: Optional[float] = None
    q50: Optional[float] = None
    q75: Optional[float] = None
    
    # Categorical stats
    unique_count: Optional[int] = None
    top_values: Optional[Dict[str, int]] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class CorrelationProfile:
    """Correlation between two metrics"""
    col1: str
    col2: str
    correlation: float
    strength: str  # 'strong', 'moderate', 'weak'


@dataclass
class TemporalProfile:
    """Temporal patterns in the data"""
    start_date: datetime
    end_date: datetime
    total_days: int
    
    # Weekly patterns
    sessions_per_week_mean: float
    sessions_per_week_std: float
    
    # Day of week distribution
    day_of_week_freq: Dict[str, float]  # Mon-Sun frequencies
    
    # Session type patterns
    session_type_freq: Dict[str, float]
    
    # Trend indicators
    has_trend: bool
    trend_direction: Optional[str] = None  # 'increasing', 'decreasing', 'stable'


@dataclass
class ConditionalProfile:
    """Conditional distributions (e.g., by position, session type)"""
    condition_type: str  # 'position', 'session_type'
    profiles: Dict[str, Dict[str, float]]  # condition_value -> {metric: value}


@dataclass
class DataProfile:
    """Complete statistical profile of training data"""
    version: str
    created_at: datetime
    
    # Schema info
    tables: List[str]
    total_athletes: int
    total_sessions: int
    date_range: Tuple[datetime, datetime]
    
    # Column profiles
    columns: List[ColumnProfile]
    
    # Relationships
    correlations: List[CorrelationProfile]
    
    # Temporal patterns
    temporal: TemporalProfile
    
    # Conditional distributions
    conditionals: List[ConditionalProfile]
    
    # Constraints
    constraints: Dict[str, Any]
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'tables': self.tables,
            'total_athletes': self.total_athletes,
            'total_sessions': self.total_sessions,
            'date_range': [self.date_range[0].isoformat(), self.date_range[1].isoformat()],
            'columns': [col.to_dict() for col in self.columns],
            'correlations': [asdict(corr) for corr in self.correlations],
            'temporal': asdict(self.temporal),
            'conditionals': [asdict(cond) for cond in self.conditionals],
            'constraints': self.constraints
        }
    
    def to_json(self, filepath: str):
        """Save profile to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
    
    @classmethod
    def from_json(cls, filepath: str) -> 'DataProfile':
        """Load profile from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct objects (simplified - would need full reconstruction logic)
        return data


class DataProfiler:
    """Extract statistical profiles from real training data"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def profile_pse_data(self) -> ColumnProfile:
        """Profile PSE (load) data"""
        data = self.db.query_to_dict("""
            SELECT 
                pse,
                duracao_min,
                (pse * duracao_min) as carga_total
            FROM dados_pse
            WHERE pse > 0 AND duracao_min > 0
        """)
        
        if not data:
            return None
        
        loads = [d['carga_total'] for d in data]
        pses = [d['pse'] for d in data]
        durations = [d['duracao_min'] for d in data]
        
        return {
            'carga_total': self._profile_numeric_column(loads, 'carga_total'),
            'pse': self._profile_numeric_column(pses, 'pse'),
            'duracao_min': self._profile_numeric_column(durations, 'duracao_min')
        }
    
    def profile_gps_data(self) -> Dict[str, ColumnProfile]:
        """Profile GPS metrics"""
        data = self.db.query_to_dict("""
            SELECT 
                distancia_total,
                velocidade_max,
                velocidade_media,
                sprints,
                aceleracoes,
                desaceleracoes
            FROM dados_gps
            WHERE distancia_total > 0
        """)
        
        if not data:
            return {}
        
        profiles = {}
        for col in ['distancia_total', 'velocidade_max', 'velocidade_media', 
                    'sprints', 'aceleracoes', 'desaceleracoes']:
            values = [d[col] for d in data if d[col] is not None]
            if values:
                profiles[col] = self._profile_numeric_column(values, col)
        
        return profiles
    
    def profile_by_position(self) -> ConditionalProfile:
        """Profile metrics by athlete position"""
        data = self.db.query_to_dict("""
            SELECT 
                a.posicao,
                AVG(p.pse * p.duracao_min) as avg_load,
                STDDEV(p.pse * p.duracao_min) as std_load,
                AVG(g.distancia_total) as avg_distance,
                AVG(g.velocidade_max) as avg_max_speed
            FROM atletas a
            LEFT JOIN dados_pse p ON p.atleta_id = a.id
            LEFT JOIN dados_gps g ON g.atleta_id = a.id
            WHERE p.pse > 0
            GROUP BY a.posicao
        """)
        
        profiles = {}
        for row in data:
            profiles[row['posicao']] = {
                'avg_load': float(row['avg_load']) if row['avg_load'] else 0,
                'std_load': float(row['std_load']) if row['std_load'] else 0,
                'avg_distance': float(row['avg_distance']) if row['avg_distance'] else 0,
                'avg_max_speed': float(row['avg_max_speed']) if row['avg_max_speed'] else 0
            }
        
        return ConditionalProfile(
            condition_type='position',
            profiles=profiles
        )
    
    def profile_by_session_type(self) -> ConditionalProfile:
        """Profile metrics by session type (training, game, recovery)"""
        data = self.db.query_to_dict("""
            SELECT 
                s.tipo,
                AVG(p.pse * p.duracao_min) as avg_load,
                STDDEV(p.pse * p.duracao_min) as std_load,
                AVG(p.duracao_min) as avg_duration,
                COUNT(*) as count
            FROM sessoes s
            JOIN dados_pse p ON p.sessao_id = s.id
            WHERE p.pse > 0
            GROUP BY s.tipo
        """)
        
        profiles = {}
        for row in data:
            profiles[row['tipo']] = {
                'avg_load': float(row['avg_load']) if row['avg_load'] else 0,
                'std_load': float(row['std_load']) if row['std_load'] else 0,
                'avg_duration': float(row['avg_duration']) if row['avg_duration'] else 0,
                'frequency': int(row['count'])
            }
        
        return ConditionalProfile(
            condition_type='session_type',
            profiles=profiles
        )
    
    def profile_temporal_patterns(self) -> TemporalProfile:
        """Profile temporal patterns (seasonality, trends)"""
        # Get date range
        date_range = self.db.query_to_dict("""
            SELECT 
                MIN(DATE(time)) as start_date,
                MAX(DATE(time)) as end_date
            FROM dados_pse
            WHERE pse > 0
        """)[0]
        
        start = date_range['start_date']
        end = date_range['end_date']
        total_days = (end - start).days + 1
        
        # Weekly patterns
        weekly_sessions = self.db.query_to_dict("""
            SELECT 
                DATE_TRUNC('week', time) as week,
                COUNT(DISTINCT sessao_id) as session_count
            FROM dados_pse
            WHERE pse > 0
            GROUP BY week
            ORDER BY week
        """)
        
        session_counts = [w['session_count'] for w in weekly_sessions]
        sessions_per_week_mean = statistics.mean(session_counts) if session_counts else 0
        sessions_per_week_std = statistics.stdev(session_counts) if len(session_counts) > 1 else 0
        
        # Day of week frequency
        dow_data = self.db.query_to_dict("""
            SELECT 
                EXTRACT(DOW FROM time) as dow,
                COUNT(*) as count
            FROM dados_pse
            WHERE pse > 0
            GROUP BY dow
            ORDER BY dow
        """)
        
        total_sessions = sum(d['count'] for d in dow_data)
        day_of_week_freq = {
            str(int(d['dow'])): d['count'] / total_sessions 
            for d in dow_data
        }
        
        # Session type frequency
        type_data = self.db.query_to_dict("""
            SELECT 
                s.tipo,
                COUNT(*) as count
            FROM sessoes s
            JOIN dados_pse p ON p.sessao_id = s.id
            WHERE p.pse > 0
            GROUP BY s.tipo
        """)
        
        total = sum(t['count'] for t in type_data)
        session_type_freq = {
            t['tipo']: t['count'] / total 
            for t in type_data
        }
        
        return TemporalProfile(
            start_date=start,
            end_date=end,
            total_days=total_days,
            sessions_per_week_mean=sessions_per_week_mean,
            sessions_per_week_std=sessions_per_week_std,
            day_of_week_freq=day_of_week_freq,
            session_type_freq=session_type_freq,
            has_trend=False
        )
    
    def calculate_correlations(self) -> List[CorrelationProfile]:
        """Calculate correlations between key metrics"""
        # Simplified - would use proper correlation calculation
        return []
    
    def create_full_profile(self) -> DataProfile:
        """Create complete data profile"""
        # Basic info
        athletes = self.db.query_to_dict("SELECT COUNT(*) as count FROM atletas WHERE ativo = TRUE")[0]
        sessions = self.db.query_to_dict("SELECT COUNT(*) as count FROM sessoes")[0]
        date_range = self.db.query_to_dict("""
            SELECT MIN(DATE(time)) as start, MAX(DATE(time)) as end 
            FROM dados_pse WHERE pse > 0
        """)[0]
        
        # Profile components
        pse_profiles = self.profile_pse_data()
        gps_profiles = self.profile_gps_data()
        position_profile = self.profile_by_position()
        session_type_profile = self.profile_by_session_type()
        temporal_profile = self.profile_temporal_patterns()
        
        # Combine column profiles
        columns = []
        for name, prof in pse_profiles.items():
            columns.append(prof)
        for name, prof in gps_profiles.items():
            columns.append(prof)
        
        # Build constraints from schema
        constraints = {
            'pse': {'min': 1, 'max': 10},
            'duracao_min': {'min': 0, 'max': 180},
            'distancia_total': {'min': 0, 'max': 15000},
            'velocidade_max': {'min': 0, 'max': 45},
            'sprints': {'min': 0, 'max': 100},
            'fc_max': {'min': 0, 'max': 220}
        }
        
        return DataProfile(
            version='1.0',
            created_at=datetime.now(),
            tables=['atletas', 'sessoes', 'dados_pse', 'dados_gps', 'metricas_carga'],
            total_athletes=athletes['count'],
            total_sessions=sessions['count'],
            date_range=(date_range['start'], date_range['end']),
            columns=columns,
            correlations=[],
            temporal=temporal_profile,
            conditionals=[position_profile, session_type_profile],
            constraints=constraints
        )
    
    def _profile_numeric_column(self, values: List[float], name: str) -> ColumnProfile:
        """Profile a numeric column"""
        if not values:
            return ColumnProfile(
                name=name,
                dtype='numeric',
                count=0,
                missing_count=0,
                missing_pct=0
            )
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        return ColumnProfile(
            name=name,
            dtype='numeric',
            count=n,
            missing_count=0,
            missing_pct=0,
            mean=statistics.mean(values),
            std=statistics.stdev(values) if n > 1 else 0,
            min=min(values),
            max=max(values),
            q25=sorted_vals[n // 4],
            q50=sorted_vals[n // 2],
            q75=sorted_vals[3 * n // 4]
        )
