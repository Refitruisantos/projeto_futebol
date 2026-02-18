"""
Mock Data Generator: Create Realistic Training Load Data

Generates synthetic data that:
- Respects schema constraints
- Maintains realistic distributions based on data profile
- Supports configurable scenarios (normal, injury, taper, etc.)
- Enables forecasting model testing and validation
"""

import random
import numpy as np
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ScenarioType(Enum):
    """Predefined scenario types"""
    NORMAL = "normal_season"
    TAPER = "taper_period"
    OVERLOAD = "overload_period"
    INJURY_RECOVERY = "injury_recovery"
    GAME_CONGESTION = "game_congestion"
    OFF_SEASON = "off_season"


@dataclass
class GenerationConfig:
    """Configuration for data generation"""
    # Time period
    start_date: datetime
    end_date: datetime
    
    # Entities
    num_athletes: int
    positions: List[str]
    
    # Calendar
    training_days: List[int]  # 0=Monday, 6=Sunday
    game_days: List[int]
    sessions_per_week: int
    
    # Scenario
    scenario: ScenarioType
    
    # Fidelity (how close to real data)
    fidelity: float = 0.8  # 0=completely synthetic, 1=very close to real
    
    # Randomness
    seed: Optional[int] = None
    noise_level: float = 0.1  # Amount of random variation
    
    # Data profile (reference statistics)
    data_profile: Optional[Dict] = None


class MockDataGenerator:
    """Generate realistic mock training data"""
    
    def __init__(self, config: GenerationConfig, db_connection=None):
        self.config = config
        self.db = db_connection
        
        if config.seed:
            random.seed(config.seed)
            np.random.seed(config.seed)
        
        # Load or use default parameters
        self.params = self._initialize_parameters()
    
    def _initialize_parameters(self) -> Dict:
        """Initialize generation parameters from profile or defaults"""
        if self.config.data_profile:
            return self.config.data_profile
        
        # Default parameters (based on football training norms)
        return {
            'pse': {
                'treino': {'mean': 5.5, 'std': 1.2, 'min': 2, 'max': 9},
                'jogo': {'mean': 7.5, 'std': 0.8, 'min': 5, 'max': 10},
                'recuperacao': {'mean': 3.0, 'std': 0.8, 'min': 1, 'max': 5}
            },
            'duracao_min': {
                'treino': {'mean': 90, 'std': 15, 'min': 60, 'max': 120},
                'jogo': {'mean': 90, 'std': 5, 'min': 80, 'max': 100},
                'recuperacao': {'mean': 45, 'std': 10, 'min': 30, 'max': 60}
            },
            'distancia_total': {
                'treino': {'mean': 7000, 'std': 1500, 'min': 4000, 'max': 10000},
                'jogo': {'mean': 10000, 'std': 1000, 'min': 8000, 'max': 12000},
                'recuperacao': {'mean': 3000, 'std': 500, 'min': 1500, 'max': 5000}
            },
            'velocidade_max': {
                'treino': {'mean': 28.5, 'std': 2.5, 'min': 23, 'max': 35},
                'jogo': {'mean': 31.0, 'std': 2.0, 'min': 26, 'max': 38},
                'recuperacao': {'mean': 20.0, 'std': 3.0, 'min': 15, 'max': 25}
            },
            'sprints': {
                'treino': {'mean': 15, 'std': 5, 'min': 5, 'max': 30},
                'jogo': {'mean': 25, 'std': 8, 'min': 10, 'max': 50},
                'recuperacao': {'mean': 5, 'std': 2, 'min': 0, 'max': 10}
            },
            'aceleracoes': {
                'treino': {'mean': 40, 'std': 10, 'min': 20, 'max': 70},
                'jogo': {'mean': 60, 'std': 15, 'min': 30, 'max': 100},
                'recuperacao': {'mean': 15, 'std': 5, 'min': 5, 'max': 30}
            },
            'position_modifiers': {
                'GR': {'load': 0.7, 'distance': 0.5, 'sprints': 0.3},
                'DC': {'load': 0.9, 'distance': 0.85, 'sprints': 0.7},
                'DL': {'load': 1.0, 'distance': 1.0, 'sprints': 1.0},
                'MC': {'load': 1.05, 'distance': 1.1, 'sprints': 0.9},
                'EX': {'load': 1.1, 'distance': 1.05, 'sprints': 1.2},
                'AV': {'load': 1.0, 'distance': 0.95, 'sprints': 1.3}
            }
        }
    
    def generate_calendar(self) -> List[Dict]:
        """Generate training/game schedule"""
        calendar = []
        current_date = self.config.start_date
        week_num = 0
        
        while current_date <= self.config.end_date:
            dow = current_date.weekday()  # 0=Monday
            
            # Determine session type
            session_type = None
            if dow in self.config.game_days:
                session_type = 'jogo'
            elif dow in self.config.training_days:
                # Apply scenario modifications
                if self.config.scenario == ScenarioType.TAPER:
                    # Reduce training frequency during taper
                    if random.random() > 0.7:
                        session_type = 'treino'
                elif self.config.scenario == ScenarioType.INJURY_RECOVERY:
                    session_type = 'recuperacao' if random.random() > 0.5 else 'treino'
                elif self.config.scenario == ScenarioType.GAME_CONGESTION:
                    # More games, less training
                    session_type = 'jogo' if random.random() > 0.6 else 'treino'
                else:
                    session_type = 'treino'
            
            if session_type:
                # Add session time
                if session_type == 'jogo':
                    hora_inicio = time(20, 30)  # Games at 8:30 PM
                else:
                    hora_inicio = time(10, 0)  # Training at 10 AM
                
                calendar.append({
                    'date': current_date,
                    'type': session_type,
                    'time': hora_inicio,
                    'week_num': week_num
                })
            
            current_date += timedelta(days=1)
            if dow == 6:  # Sunday
                week_num += 1
        
        return calendar
    
    def generate_athlete(self, athlete_id: int, name: str, position: str) -> Dict:
        """Generate athlete data"""
        # Age between 18-35
        age = random.randint(18, 35)
        birth_year = datetime.now().year - age
        
        # Height/weight based on position
        height_ranges = {
            'GR': (185, 200), 'DC': (180, 195), 'DL': (170, 185),
            'MC': (170, 185), 'EX': (165, 180), 'AV': (170, 190)
        }
        weight_ranges = {
            'GR': (75, 90), 'DC': (75, 88), 'DL': (68, 80),
            'MC': (68, 80), 'EX': (65, 78), 'AV': (70, 85)
        }
        
        height_range = height_ranges.get(position, (170, 185))
        weight_range = weight_ranges.get(position, (70, 80))
        
        return {
            'jogador_id': f'ATL{athlete_id:03d}',
            'nome_completo': name,
            'data_nascimento': datetime(birth_year, random.randint(1, 12), random.randint(1, 28)).date(),
            'posicao': position,
            'numero_camisola': athlete_id,
            'pe_dominante': random.choice(['Direito', 'Esquerdo', 'Ambos']),
            'altura_cm': random.randint(*height_range),
            'massa_kg': round(random.uniform(*weight_range), 1),
            'ativo': True
        }
    
    def generate_pse_session(
        self, 
        athlete_id: int, 
        session_id: int, 
        session_date: datetime,
        session_type: str,
        position: str,
        week_context: Dict
    ) -> Dict:
        """Generate PSE data for one athlete in one session"""
        params = self.params['pse'][session_type]
        
        # Base PSE from distribution
        pse = np.random.normal(params['mean'], params['std'])
        pse = np.clip(pse, params['min'], params['max'])
        
        # Apply position modifier
        pos_mod = self.params['position_modifiers'].get(position, {}).get('load', 1.0)
        pse *= pos_mod
        
        # Apply scenario modifiers
        pse = self._apply_scenario_modifiers(pse, session_type, week_context)
        
        # Duration
        dur_params = self.params['duracao_min'][session_type]
        duration = np.random.normal(dur_params['mean'], dur_params['std'])
        duration = np.clip(duration, dur_params['min'], dur_params['max'])
        
        # Add individual variation (some athletes consistently higher/lower)
        athlete_bias = np.random.normal(0, 0.3)  # Individual tendency
        pse += athlete_bias
        
        pse = round(np.clip(pse, 1, 10), 1)
        duration = round(duration)
        
        return {
            'time': session_date,
            'atleta_id': athlete_id,
            'sessao_id': session_id,
            'pse': pse,
            'duracao_min': duration,
            'carga_total': round(pse * duration, 2)
        }
    
    def generate_gps_session(
        self,
        athlete_id: int,
        session_id: int,
        session_date: datetime,
        session_type: str,
        position: str,
        duration: int
    ) -> Dict:
        """Generate GPS data for one athlete in one session"""
        # Distance
        dist_params = self.params['distancia_total'][session_type]
        distance = np.random.normal(dist_params['mean'], dist_params['std'])
        distance = np.clip(distance, dist_params['min'], dist_params['max'])
        
        # Apply position modifier
        pos_mod = self.params['position_modifiers'].get(position, {}).get('distance', 1.0)
        distance *= pos_mod
        
        # Max speed
        speed_params = self.params['velocidade_max'][session_type]
        max_speed = np.random.normal(speed_params['mean'], speed_params['std'])
        max_speed = np.clip(max_speed, speed_params['min'], speed_params['max'])
        
        # Sprints
        sprint_params = self.params['sprints'][session_type]
        pos_sprint_mod = self.params['position_modifiers'].get(position, {}).get('sprints', 1.0)
        sprints = np.random.normal(sprint_params['mean'] * pos_sprint_mod, sprint_params['std'])
        sprints = max(0, int(sprints))
        
        # Accelerations (correlated with sprints)
        acc_params = self.params['aceleracoes'][session_type]
        aceleracoes = np.random.normal(acc_params['mean'] * pos_sprint_mod, acc_params['std'])
        aceleracoes = max(0, int(aceleracoes))
        
        # Average speed (correlated with distance and duration)
        velocidade_media = (distance / 1000) / (duration / 60) if duration > 0 else 0
        velocidade_media = min(velocidade_media, max_speed * 0.7)
        
        return {
            'time': session_date,
            'atleta_id': athlete_id,
            'sessao_id': session_id,
            'distancia_total': round(distance, 2),
            'velocidade_max': round(max_speed, 2),
            'velocidade_media': round(velocidade_media, 2),
            'sprints': sprints,
            'aceleracoes': aceleracoes,
            'desaceleracoes': int(aceleracoes * 0.9)  # Usually similar to accelerations
        }
    
    def _apply_scenario_modifiers(self, value: float, session_type: str, context: Dict) -> float:
        """Apply scenario-specific modifications"""
        scenario = self.config.scenario
        
        if scenario == ScenarioType.TAPER:
            # Gradual load reduction (70% of normal)
            return value * 0.7
        
        elif scenario == ScenarioType.OVERLOAD:
            # Increased load (120% of normal)
            return value * 1.2
        
        elif scenario == ScenarioType.INJURY_RECOVERY:
            # Progressive load increase (50% -> 100% over time)
            weeks_in = context.get('week_num', 0)
            recovery_factor = min(1.0, 0.5 + (weeks_in * 0.1))
            return value * recovery_factor
        
        elif scenario == ScenarioType.GAME_CONGESTION:
            # Fatigue accumulation (games reduce subsequent training load)
            if session_type == 'treino':
                return value * 0.85  # Reduced training intensity
        
        return value
    
    def generate_full_dataset(self) -> Dict[str, List[Dict]]:
        """Generate complete dataset"""
        # Generate calendar
        calendar = self.generate_calendar()
        
        # Generate athletes
        athletes = []
        athlete_names = self._generate_athlete_names(self.config.num_athletes)
        positions_cycle = self.config.positions * (self.config.num_athletes // len(self.config.positions) + 1)
        
        for i in range(self.config.num_athletes):
            athlete = self.generate_athlete(
                i + 1,
                athlete_names[i],
                positions_cycle[i]
            )
            athletes.append(athlete)
        
        # Generate sessions
        sessions = []
        for session_id, event in enumerate(calendar, start=1):
            session = {
                'id': session_id,
                'data': event['date'].date(),
                'hora_inicio': event['time'],
                'tipo': event['type'],
                'duracao_min': int(np.random.normal(90, 10))
            }
            sessions.append(session)
        
        # Generate PSE and GPS data
        pse_data = []
        gps_data = []
        
        for session in sessions:
            session_datetime = datetime.combine(session['data'], session['hora_inicio'])
            week_context = {'week_num': calendar[session['id'] - 1]['week_num']}
            
            for athlete in athletes:
                # PSE data
                pse_record = self.generate_pse_session(
                    athlete_id=athlete['numero_camisola'],
                    session_id=session['id'],
                    session_date=session_datetime,
                    session_type=session['tipo'],
                    position=athlete['posicao'],
                    week_context=week_context
                )
                pse_data.append(pse_record)
                
                # GPS data (70% coverage - not all sessions have GPS)
                if random.random() < 0.7:
                    gps_record = self.generate_gps_session(
                        athlete_id=athlete['numero_camisola'],
                        session_id=session['id'],
                        session_date=session_datetime,
                        session_type=session['tipo'],
                        position=athlete['posicao'],
                        duration=pse_record['duracao_min']
                    )
                    gps_data.append(gps_record)
        
        return {
            'athletes': athletes,
            'sessions': sessions,
            'pse_data': pse_data,
            'gps_data': gps_data,
            'config': {
                'scenario': self.config.scenario.value,
                'start_date': self.config.start_date.isoformat(),
                'end_date': self.config.end_date.isoformat(),
                'seed': self.config.seed
            }
        }
    
    def _generate_athlete_names(self, count: int) -> List[str]:
        """Generate realistic Portuguese athlete names"""
        first_names = [
            'João', 'Pedro', 'Miguel', 'Tiago', 'Rafael', 'André', 'Bruno', 'Carlos',
            'Diogo', 'Francisco', 'Gonçalo', 'Hugo', 'José', 'Luís', 'Marco', 'Paulo',
            'Ricardo', 'Rui', 'Sérgio', 'Vasco'
        ]
        last_names = [
            'Silva', 'Santos', 'Ferreira', 'Pereira', 'Oliveira', 'Costa', 'Rodrigues',
            'Martins', 'Jesus', 'Sousa', 'Fernandes', 'Gonçalves', 'Gomes', 'Lopes',
            'Marques', 'Alves', 'Almeida', 'Ribeiro', 'Pinto', 'Carvalho'
        ]
        
        names = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            names.append(f"{first} {last}")
        
        return names
