"""
Advanced Training Load Metrics Calculator

Calculates:
- Monotony (mean / std_dev)
- Strain (total_load × monotony)
- ACWR (Acute:Chronic Workload Ratio)
- Z-Scores (standardized metrics)
- Risk levels based on thresholds
"""

import statistics
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class MetricsCalculator:
    """Calculate advanced training load metrics for injury risk assessment"""
    
    # Risk thresholds (based on scientific literature)
    MONOTONY_THRESHOLDS = {'green': 1.5, 'yellow': 2.0}  # Fixed: was 1.0, should be 1.5
    STRAIN_THRESHOLDS = {'green': 4000, 'yellow': 6000}
    ACWR_THRESHOLDS = {
        'low': 0.8,      # Below this = detraining risk
        'optimal_min': 0.8,
        'optimal_max': 1.3,  # Sweet spot
        'elevated': 1.5   # Above this = overtraining risk
    }
    Z_SCORE_THRESHOLDS = {'green': 1.0, 'yellow': 2.0}
    
    @staticmethod
    def calcular_monotonia(cargas_ultimos_treinos: List[float]) -> Optional[float]:
        """
        Calculate training monotony using rolling 7-workout window
        
        Monotony = Mean Workout Load / Standard Deviation
        
        Uses the last 7 training sessions (workouts only, not calendar days).
        This approach provides more stable metrics for irregular training schedules
        and focuses on training variation rather than weekly structure.
        
        Scientific basis: Hulin et al. (2016) - rolling workout windows
        
        Interpretation:
        - < 1.5: Good variation (low risk)
        - 1.5-2.0: Moderate variation (monitor)
        - > 2.0: Low variation (high injury risk)
        
        Args:
            cargas_ultimos_treinos: List of last 7 workout loads (training sessions only)
            
        Returns:
            Monotony value or None if cannot calculate
        """
        if not cargas_ultimos_treinos or len(cargas_ultimos_treinos) < 2:
            return None
        
        # Should already contain only workouts (no zeros), but filter just in case
        cargas_validas = [c for c in cargas_ultimos_treinos if c > 0]
        
        if len(cargas_validas) < 2:
            return None
        
        media = statistics.mean(cargas_validas)
        desvio = statistics.stdev(cargas_validas)
        
        if desvio == 0:
            return None  # Cannot divide by zero (all workouts identical)
        
        return round(media / desvio, 4)
    
    @staticmethod
    def calcular_tensao(carga_total: float, monotonia: Optional[float]) -> Optional[float]:
        """
        Calculate training strain (tension)
        
        Strain = Total Weekly Load × Monotony
        
        Interpretation:
        - < 4000: Low strain (green)
        - 4000-6000: Moderate strain (yellow)
        - > 6000: High strain (red)
        
        Args:
            carga_total: Total weekly load
            monotonia: Monotony value
            
        Returns:
            Strain value or None
        """
        if monotonia is None or carga_total == 0:
            return None
        
        return round(carga_total * monotonia, 2)
    
    @staticmethod
    def calcular_acwr(carga_aguda: float, carga_cronica: float) -> Optional[float]:
        """
        Calculate Acute:Chronic Workload Ratio
        
        ACWR = Acute Load (7 days) / Chronic Load (28 days)
        
        Interpretation:
        - < 0.8: Detraining risk (red)
        - 0.8-1.3: Sweet spot (green)
        - 1.3-1.5: Elevated (yellow)
        - > 1.5: Overtraining risk (red)
        
        Args:
            carga_aguda: 7-day rolling average
            carga_cronica: 28-day rolling average
            
        Returns:
            ACWR value or None
        """
        if carga_cronica == 0:
            return None
        
        return round(carga_aguda / carga_cronica, 4)
    
    @staticmethod
    def calcular_z_score(valor: float, media_grupo: float, desvio_grupo: float) -> Optional[float]:
        """
        Calculate Z-Score (standardized score)
        
        Z-Score = (Individual Value - Group Mean) / Group SD
        
        Interpretation:
        - < -2.0: Much below team average (red)
        - -2.0 to -1.0: Below average (yellow)
        - -1.0 to 1.0: Normal range (green)
        - 1.0 to 2.0: Above average (yellow)
        - > 2.0: Much above average (red)
        
        Args:
            valor: Individual value
            media_grupo: Team/group mean
            desvio_grupo: Team/group standard deviation
            
        Returns:
            Z-Score or None
        """
        if desvio_grupo == 0:
            return None
        
        return round((valor - media_grupo) / desvio_grupo, 4)
    
    @staticmethod
    def calcular_variacao_percentual(carga_atual: float, carga_anterior: float) -> Optional[float]:
        """
        Calculate week-to-week percentage change
        
        Variation % = ((Current - Previous) / Previous) × 100
        
        Args:
            carga_atual: Current week load
            carga_anterior: Previous week load
            
        Returns:
            Percentage change or None
        """
        if carga_anterior == 0:
            return None
        
        return round(((carga_atual - carga_anterior) / carga_anterior) * 100, 2)
    
    @classmethod
    def determinar_nivel_risco_monotonia(cls, monotonia: Optional[float]) -> str:
        """Determine risk level for monotony"""
        if monotonia is None:
            return 'unknown'
        if monotonia < cls.MONOTONY_THRESHOLDS['green']:
            return 'green'
        if monotonia < cls.MONOTONY_THRESHOLDS['yellow']:
            return 'yellow'
        return 'red'
    
    @classmethod
    def determinar_nivel_risco_tensao(cls, tensao: Optional[float]) -> str:
        """Determine risk level for strain"""
        if tensao is None:
            return 'unknown'
        if tensao < cls.STRAIN_THRESHOLDS['green']:
            return 'green'
        if tensao < cls.STRAIN_THRESHOLDS['yellow']:
            return 'yellow'
        return 'red'
    
    @classmethod
    def determinar_nivel_risco_acwr(cls, acwr: Optional[float]) -> str:
        """Determine risk level for ACWR"""
        if acwr is None:
            return 'unknown'
        
        t = cls.ACWR_THRESHOLDS
        
        if acwr < t['low']:
            return 'red'  # Detraining
        if t['optimal_min'] <= acwr <= t['optimal_max']:
            return 'green'  # Sweet spot
        if acwr <= t['elevated']:
            return 'yellow'  # Elevated
        return 'red'  # Overtraining
    
    @staticmethod
    def calcular_media_desvio(valores: List[float]) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate mean and standard deviation
        
        Returns:
            Tuple of (mean, std_dev) or (None, None)
        """
        if not valores or len(valores) < 2:
            return None, None
        
        valores_validos = [v for v in valores if v is not None]
        
        if len(valores_validos) < 2:
            return None, None
        
        media = statistics.mean(valores_validos)
        desvio = statistics.stdev(valores_validos)
        
        return round(media, 2), round(desvio, 2)
    
    @staticmethod
    def calcular_carga_rolante(cargas: List[Dict], dias: int, data_referencia: datetime) -> float:
        """
        Calculate rolling average load for N days before reference date
        
        Args:
            cargas: List of dicts with 'data' and 'carga_total' keys
            dias: Number of days to look back (7 for acute, 28 for chronic)
            data_referencia: Reference date
            
        Returns:
            Average load over the period
        """
        data_limite = data_referencia - timedelta(days=dias)
        
        cargas_periodo = [
            c['carga_total'] for c in cargas
            if data_limite <= c['data'] <= data_referencia
        ]
        
        if not cargas_periodo:
            return 0.0
        
        return round(sum(cargas_periodo) / len(cargas_periodo), 2)


# Convenience function for batch calculations
def calcular_metricas_semana(
    cargas_diarias: List[float],
    carga_total: float,
    carga_aguda: float,
    carga_cronica: float,
    carga_semana_anterior: Optional[float] = None
) -> Dict:
    """
    Calculate all weekly metrics at once
    
    Args:
        cargas_diarias: List of daily loads for the week
        carga_total: Total weekly load
        carga_aguda: 7-day rolling average
        carga_cronica: 28-day rolling average
        carga_semana_anterior: Previous week total (for variation %)
        
    Returns:
        Dictionary with all calculated metrics and risk levels
    """
    calc = MetricsCalculator()
    
    # Calculate metrics
    media, desvio = calc.calcular_media_desvio(cargas_diarias)
    monotonia = calc.calcular_monotonia(cargas_diarias)
    tensao = calc.calcular_tensao(carga_total, monotonia)
    acwr = calc.calcular_acwr(carga_aguda, carga_cronica)
    variacao = calc.calcular_variacao_percentual(carga_total, carga_semana_anterior) if carga_semana_anterior else None
    
    # Determine risk levels
    nivel_monotonia = calc.determinar_nivel_risco_monotonia(monotonia)
    nivel_tensao = calc.determinar_nivel_risco_tensao(tensao)
    nivel_acwr = calc.determinar_nivel_risco_acwr(acwr)
    
    return {
        'carga_total_semanal': carga_total,
        'media_carga': media,
        'desvio_padrao': desvio,
        'dias_treino': len([c for c in cargas_diarias if c > 0]),
        'monotonia': monotonia,
        'tensao': tensao,
        'variacao_percentual': variacao,
        'carga_aguda': carga_aguda,
        'carga_cronica': carga_cronica,
        'acwr': acwr,
        'nivel_risco_monotonia': nivel_monotonia,
        'nivel_risco_tensao': nivel_tensao,
        'nivel_risco_acwr': nivel_acwr
    }
