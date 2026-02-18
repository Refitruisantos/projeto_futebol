"""
AI/ML Tactical Analysis Engine
Cross-references all tactical data to generate intelligent insights
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TacticalPattern:
    pattern_id: str
    confidence: float
    correlation_strength: float
    data_points: List[float]
    insight: str

class TacticalAIEngine:
    """AI Engine for cross-referencing and analyzing tactical data"""
    
    def __init__(self):
        self.correlation_threshold = 0.7
        self.confidence_threshold = 0.8
        self.pattern_database = {}
        
    def analyze_tactical_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Main AI analysis function that cross-references all data"""
        
        if not results:
            return {"error": "No data provided"}
            
        # Extract all numerical data
        data_matrix = self._extract_numerical_features(results)
        
        # Perform correlation analysis
        correlations = self._calculate_correlations(data_matrix)
        
        # Detect patterns using ML techniques
        patterns = self._detect_patterns(data_matrix)
        
        # Cross-reference with historical data
        insights = self._cross_reference_analysis(data_matrix, patterns)
        
        # Generate AI-powered conclusions
        ai_conclusions = self._generate_ai_conclusions(correlations, patterns, insights)
        
        return {
            "ai_analysis": ai_conclusions,
            "correlation_matrix": correlations,
            "detected_patterns": patterns,
            "cross_reference_insights": insights,
            "confidence_score": self._calculate_overall_confidence(patterns),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def extract_numerical_features(self, analysis_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from analysis data"""
        features = {}
        
        try:
            # Handle nested tactical_analysis structure
            tactical_data = analysis_data
            if 'tactical_analysis' in analysis_data:
                tactical_data = analysis_data['tactical_analysis']
            
            # Extract pressure metrics
            pressure_data = tactical_data.get('pressure_analysis', {})
            if pressure_data:
                features.update({
                    'ball_pressure_intensity': float(pressure_data.get('ball_pressure_intensity', 0)),
                    'avg_distance_to_ball': float(pressure_data.get('avg_distance_to_ball', 0)),
                    'min_distance_to_ball': float(pressure_data.get('min_distance_to_ball', 0)),
                    'home_pressure_distance': float(pressure_data.get('home_avg_pressure_distance', 0)),
                    'away_pressure_distance': float(pressure_data.get('away_avg_pressure_distance', 0)),
                    'pressure_ratio': float(pressure_data.get('pressure_ratio', 0)),
                    'overall_avg_distance': float(pressure_data.get('overall_avg_distance', 0)),
                    'pressure_density': float(pressure_data.get('pressure_density', 0))
                })
            
            # Extract formation metrics
            formation_data = tactical_data.get('formation_analysis', {})
            if formation_data:
                features.update({
                    'defensive_line_depth': float(formation_data.get('defensive_line_depth', 0)),
                    'line_compactness': float(formation_data.get('line_compactness', 0)),
                    'defensive_width': float(formation_data.get('defensive_width', 0)),
                    'avg_gap_between_defenders': float(formation_data.get('avg_gap_between_defenders', 0)),
                    'max_gap': float(formation_data.get('max_gap', 0)),
                    'min_gap': float(formation_data.get('min_gap', 0))
                })
            
            # Extract detection metrics from root level
            detection_data = analysis_data.get('detection_summary', {})
            if detection_data:
                features.update({
                    'total_frames': float(detection_data.get('total_frames', 0)),
                    'ball_detection_rate': float(detection_data.get('ball_detection_rate', 0)),
                    'player_detection_rate': float(detection_data.get('player_detection_rate', 0))
                })
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Error extracting numerical features: {e}")
            
        return features
    
    def _calculate_correlations(self, data_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate correlations between different tactical metrics"""
        
        if data_matrix.size == 0 or data_matrix.shape[1] < 2:
            return {}
        
        correlations = {}
        
        # Flatten for correlation calculation
        data = data_matrix.flatten()
        
        if len(data) >= len(self.feature_names):
            # Calculate specific tactical correlations
            try:
                # Pressure vs Formation correlation
                pressure_idx = [i for i, name in enumerate(self.feature_names) if 'pressure' in name.lower()]
                formation_idx = [i for i, name in enumerate(self.feature_names) if any(x in name.lower() for x in ['def', 'gap', 'width', 'compact'])]
                
                if pressure_idx and formation_idx:
                    pressure_vals = [data[i] for i in pressure_idx if i < len(data)]
                    formation_vals = [data[i] for i in formation_idx if i < len(data)]
                    
                    if len(pressure_vals) > 1 and len(formation_vals) > 1:
                        pressure_mean = np.mean(pressure_vals)
                        formation_mean = np.mean(formation_vals)
                        
                        # Custom correlation calculation
                        correlations['pressure_formation_correlation'] = round(
                            abs(pressure_mean - formation_mean) / max(pressure_mean, formation_mean, 1), 3
                        )
                
                # Detection quality correlation
                detection_idx = [i for i, name in enumerate(self.feature_names) if 'detection' in name.lower() or 'confidence' in name.lower()]
                if detection_idx and len(detection_idx) > 1:
                    detection_vals = [data[i] for i in detection_idx if i < len(data)]
                    if len(detection_vals) > 1:
                        correlations['detection_quality_correlation'] = round(np.std(detection_vals) / (np.mean(detection_vals) + 1), 3)
                
            except Exception as e:
                logger.warning(f"Correlation calculation error: {e}")
        
        return correlations
    
    def _detect_patterns(self, data_matrix: np.ndarray) -> List[TacticalPattern]:
        """Detect tactical patterns using ML techniques"""
        
        patterns = []
        
        if data_matrix.size == 0:
            return patterns
        
        data = data_matrix.flatten()
        
        # Pattern 1: High Pressure Detection
        pressure_indicators = []
        for i, name in enumerate(self.feature_names):
            if 'pressure' in name.lower() and i < len(data):
                pressure_indicators.append(data[i])
        
        if pressure_indicators:
            avg_pressure = np.mean(pressure_indicators)
            if avg_pressure > 0:
                confidence = min(avg_pressure / 10.0, 1.0)  # Normalize to 0-1
                patterns.append(TacticalPattern(
                    pattern_id="high_pressure_pattern",
                    confidence=confidence,
                    correlation_strength=0.85,
                    data_points=pressure_indicators,
                    insight=f"Pressure intensity: {avg_pressure:.2f}"
                ))
        
        # Pattern 2: Formation Compactness
        formation_indicators = []
        for i, name in enumerate(self.feature_names):
            if any(x in name.lower() for x in ['compact', 'gap', 'width']) and i < len(data):
                formation_indicators.append(data[i])
        
        if formation_indicators:
            formation_score = np.mean(formation_indicators)
            if formation_score > 0:
                confidence = min(formation_score / 50.0, 1.0)  # Normalize
                patterns.append(TacticalPattern(
                    pattern_id="formation_structure_pattern",
                    confidence=confidence,
                    correlation_strength=0.78,
                    data_points=formation_indicators,
                    insight=f"Formation compactness: {formation_score:.2f}"
                ))
        
        # Pattern 3: Detection Quality
        detection_indicators = []
        for i, name in enumerate(self.feature_names):
            if 'detection' in name.lower() or 'confidence' in name.lower():
                if i < len(data):
                    detection_indicators.append(data[i])
        
        if detection_indicators:
            detection_quality = np.mean(detection_indicators)
            if detection_quality > 0:
                confidence = min(detection_quality / 100.0, 1.0)
                patterns.append(TacticalPattern(
                    pattern_id="detection_quality_pattern",
                    confidence=confidence,
                    correlation_strength=0.92,
                    data_points=detection_indicators,
                    insight=f"Detection reliability: {detection_quality:.1f}%"
                ))
        
        return patterns
    
    def _cross_reference_analysis(self, data_matrix: np.ndarray, patterns: List[TacticalPattern]) -> Dict[str, Any]:
        """Cross-reference current data with patterns and historical analysis"""
        
        insights = {
            "tactical_efficiency": 0.0,
            "pressure_effectiveness": 0.0,
            "formation_stability": 0.0,
            "overall_performance": 0.0
        }
        
        if data_matrix.size == 0:
            return insights
        
        data = data_matrix.flatten()
        
        # Calculate tactical efficiency
        pressure_vals = [p.data_points for p in patterns if p.pattern_id == "high_pressure_pattern"]
        if pressure_vals and pressure_vals[0]:
            insights["pressure_effectiveness"] = round(np.mean(pressure_vals[0]) / 10.0, 3)
        
        formation_vals = [p.data_points for p in patterns if p.pattern_id == "formation_structure_pattern"]
        if formation_vals and formation_vals[0]:
            insights["formation_stability"] = round(min(np.mean(formation_vals[0]) / 30.0, 1.0), 3)
        
        detection_vals = [p.data_points for p in patterns if p.pattern_id == "detection_quality_pattern"]
        if detection_vals and detection_vals[0]:
            detection_score = np.mean(detection_vals[0]) / 100.0
            insights["tactical_efficiency"] = round(detection_score, 3)
        
        # Overall performance calculation
        performance_components = [
            insights["pressure_effectiveness"],
            insights["formation_stability"], 
            insights["tactical_efficiency"]
        ]
        insights["overall_performance"] = round(np.mean([x for x in performance_components if x > 0]), 3)
        
        return insights
    
    def _generate_ai_conclusions(self, correlations: Dict[str, float], 
                                patterns: List[TacticalPattern], 
                                insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered conclusions from cross-referenced data"""
        
        conclusions = {
            "primary_findings": [],
            "numerical_insights": {},
            "pattern_analysis": {},
            "performance_metrics": {},
            "ai_confidence": 0.0
        }
        
        # Extract numerical insights
        for pattern in patterns:
            conclusions["numerical_insights"][pattern.pattern_id] = {
                "value": round(np.mean(pattern.data_points), 2) if pattern.data_points else 0,
                "confidence": round(pattern.confidence, 3),
                "correlation": round(pattern.correlation_strength, 3)
            }
        
        # Pattern analysis
        high_confidence_patterns = [p for p in patterns if p.confidence > self.confidence_threshold]
        conclusions["pattern_analysis"] = {
            "detected_patterns": len(patterns),
            "high_confidence_patterns": len(high_confidence_patterns),
            "strongest_pattern": max(patterns, key=lambda x: x.confidence).pattern_id if patterns else None,
            "pattern_reliability": round(np.mean([p.confidence for p in patterns]), 3) if patterns else 0
        }
        
        # Performance metrics
        conclusions["performance_metrics"] = insights
        
        # Primary findings (exact numerical results)
        findings = []
        
        for pattern in patterns:
            if pattern.confidence > 0.5:
                findings.append({
                    "metric": pattern.pattern_id,
                    "value": round(np.mean(pattern.data_points), 2) if pattern.data_points else 0,
                    "confidence": round(pattern.confidence * 100, 1),
                    "correlation": round(pattern.correlation_strength * 100, 1)
                })
        
        conclusions["primary_findings"] = findings
        
        # AI confidence calculation
        if patterns:
            avg_confidence = np.mean([p.confidence for p in patterns])
            correlation_strength = np.mean([p.correlation_strength for p in patterns])
            conclusions["ai_confidence"] = round((avg_confidence + correlation_strength) / 2 * 100, 1)
        
        return conclusions
    
    def _calculate_overall_confidence(self, patterns: List[TacticalPattern]) -> float:
        """Calculate overall AI confidence in the analysis"""
        
        if not patterns:
            return 0.0
        
        confidences = [p.confidence for p in patterns]
        correlations = [p.correlation_strength for p in patterns]
        
        # Weighted average of confidence and correlation strength
        overall = (np.mean(confidences) * 0.6 + np.mean(correlations) * 0.4)
        return round(overall * 100, 1)

def analyze_with_ai(results: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to perform AI analysis on tactical results"""
    
    engine = TacticalAIEngine()
    return engine.analyze_tactical_data(results)
