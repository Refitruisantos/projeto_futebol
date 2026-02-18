"""
XGBoost Performance Drop Predictor
Uses GPS, PSE/Wellness, Load Metrics, Risk Assessment, and Video Analysis data
to predict which players are experiencing a performance decline.
Provides SHAP-based explainability for each prediction.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from typing import Dict, Any, List, Optional
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

# Feature definitions with human-readable labels (Portuguese)
FEATURE_CONFIG = {
    # Load metrics
    'weekly_load': {'label': 'Carga Semanal', 'category': 'carga'},
    'monotony': {'label': 'Monotonia', 'category': 'carga'},
    'strain': {'label': 'Tensão', 'category': 'carga'},
    'acwr': {'label': 'ACWR', 'category': 'carga'},
    'training_days': {'label': 'Dias de Treino', 'category': 'carga'},
    # GPS metrics
    'avg_distance': {'label': 'Distância Média', 'category': 'gps'},
    'avg_max_speed': {'label': 'Velocidade Máxima', 'category': 'gps'},
    'avg_sprints': {'label': 'Sprints Médios', 'category': 'gps'},
    'avg_accelerations': {'label': 'Acelerações Médias', 'category': 'gps'},
    'avg_player_load': {'label': 'Player Load Médio', 'category': 'gps'},
    # Wellness / PSE
    'wellness_score': {'label': 'Bem-estar', 'category': 'wellness'},
    'fadiga': {'label': 'Fadiga', 'category': 'wellness'},
    'dor_muscular': {'label': 'Dor Muscular', 'category': 'wellness'},
    'qualidade_sono': {'label': 'Qualidade do Sono', 'category': 'wellness'},
    # Risk assessment
    'injury_risk_score': {'label': 'Risco de Lesão', 'category': 'risco'},
    'acwr_risk_score': {'label': 'Risco ACWR', 'category': 'risco'},
    'monotony_risk_score': {'label': 'Risco Monotonia', 'category': 'risco'},
    'strain_risk_score': {'label': 'Risco Tensão', 'category': 'risco'},
    'wellness_risk_score': {'label': 'Risco Bem-estar', 'category': 'risco'},
    'fatigue_accumulation_score': {'label': 'Acumulação de Fadiga', 'category': 'risco'},
    # Video analysis (if available)
    'ball_visibility_pct': {'label': 'Visibilidade Bola (%)', 'category': 'video'},
    'avg_players_detected': {'label': 'Jogadores Detetados', 'category': 'video'},
    'player_detection_consistency': {'label': 'Consistência Deteção', 'category': 'video'},
    # Derived / relative features
    'load_vs_team_ratio': {'label': 'Carga vs Equipa', 'category': 'derivado'},
    'acwr_deviation': {'label': 'Desvio ACWR', 'category': 'derivado'},
    'wellness_trend': {'label': 'Tendência Bem-estar', 'category': 'derivado'},
}

FEATURE_NAMES = list(FEATURE_CONFIG.keys())


class PerformanceDropPredictor:
    """
    XGBoost model that predicts the probability of a performance drop
    for each player, using all available data sources.
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.model_path = self.model_dir / "performance_drop_xgb.pkl"
        self.scaler_path = self.model_dir / "performance_drop_scaler.pkl"

        self.model: Optional[xgb.XGBClassifier] = None
        self.scaler = StandardScaler()
        self.explainer: Optional[shap.TreeExplainer] = None

        self.params = {
            'objective': 'binary:logistic',
            'max_depth': 5,
            'learning_rate': 0.08,
            'n_estimators': 150,
            'subsample': 0.85,
            'colsample_bytree': 0.85,
            'gamma': 0.15,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'min_child_weight': 3,
            'scale_pos_weight': 1.5,  # slight boost for positive class (drop)
            'random_state': 42,
            'eval_metric': 'logloss',
            'use_label_encoder': False,
        }

        if self.model_path.exists():
            self._load_model()
        else:
            self._train_baseline()

    # ------------------------------------------------------------------
    # Model persistence
    # ------------------------------------------------------------------
    def _save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        logger.info("Performance drop model saved")

    def _load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("Performance drop model loaded")
        except Exception as e:
            logger.warning(f"Could not load model: {e}. Training baseline.")
            self._train_baseline()

    # ------------------------------------------------------------------
    # Baseline training with synthetic data
    # ------------------------------------------------------------------
    def _train_baseline(self):
        """Train a baseline model with synthetic data so predictions work immediately."""
        logger.info("Training baseline performance drop model with synthetic data")
        np.random.seed(42)
        n = 500

        data = {
            'weekly_load': np.random.normal(3000, 800, n).clip(500, 7000),
            'monotony': np.random.normal(1.5, 0.6, n).clip(0.3, 4.0),
            'strain': np.random.normal(4500, 1500, n).clip(500, 12000),
            'acwr': np.random.normal(1.1, 0.35, n).clip(0.3, 2.5),
            'training_days': np.random.randint(2, 7, n).astype(float),
            'avg_distance': np.random.normal(5500, 1200, n).clip(1000, 12000),
            'avg_max_speed': np.random.normal(28, 3, n).clip(18, 36),
            'avg_sprints': np.random.normal(15, 5, n).clip(0, 40),
            'avg_accelerations': np.random.normal(45, 12, n).clip(5, 90),
            'avg_player_load': np.random.normal(400, 100, n).clip(100, 800),
            'wellness_score': np.random.normal(17, 3, n).clip(5, 25),
            'fadiga': np.random.randint(1, 6, n).astype(float),
            'dor_muscular': np.random.randint(1, 6, n).astype(float),
            'qualidade_sono': np.random.randint(1, 6, n).astype(float),
            'injury_risk_score': np.random.normal(2.5, 1.2, n).clip(0, 5),
            'acwr_risk_score': np.random.normal(2.0, 1.0, n).clip(0, 5),
            'monotony_risk_score': np.random.normal(2.0, 1.0, n).clip(0, 5),
            'strain_risk_score': np.random.normal(2.0, 1.0, n).clip(0, 5),
            'wellness_risk_score': np.random.normal(2.0, 1.0, n).clip(0, 5),
            'fatigue_accumulation_score': np.random.normal(2.0, 1.0, n).clip(0, 5),
            'ball_visibility_pct': np.random.normal(60, 15, n).clip(0, 100),
            'avg_players_detected': np.random.normal(18, 3, n).clip(5, 22),
            'player_detection_consistency': np.random.normal(0.75, 0.12, n).clip(0.2, 1.0),
            'load_vs_team_ratio': np.random.normal(1.0, 0.25, n).clip(0.3, 2.0),
            'acwr_deviation': np.random.normal(0, 0.3, n).clip(-1.0, 1.0),
            'wellness_trend': np.random.normal(0, 1.5, n).clip(-5, 5),
        }

        df = pd.DataFrame(data)

        # Generate realistic labels: performance drop is more likely when
        # ACWR is extreme, wellness is low, fatigue is high, strain is high
        drop_prob = (
            0.15 * ((df['acwr'] - 1.0).abs() / 0.5).clip(0, 1)
            + 0.15 * ((2.0 - df['monotony']).clip(upper=0).abs() / 1.0).clip(0, 1)
            + 0.15 * ((df['strain'] - 5000) / 3000).clip(0, 1)
            + 0.15 * ((12 - df['wellness_score']) / 7).clip(0, 1)
            + 0.10 * (df['injury_risk_score'] / 5)
            + 0.10 * (df['fatigue_accumulation_score'] / 5)
            + 0.10 * ((df['load_vs_team_ratio'] - 1.0).clip(lower=0) / 0.5).clip(0, 1)
            + 0.10 * ((1 - df['fadiga'] / 5)).clip(0, 1)
        ).clip(0, 1)

        labels = (drop_prob + np.random.normal(0, 0.08, n) > 0.45).astype(int)

        X = df[FEATURE_NAMES].values
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(X_scaled, labels)
        self.explainer = shap.TreeExplainer(self.model)
        self._save_model()

        cv_scores = cross_val_score(
            xgb.XGBClassifier(**self.params), X_scaled, labels, cv=5, scoring='f1'
        )
        logger.info(f"Baseline model trained — CV F1: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # ------------------------------------------------------------------
    # Feature extraction from database rows
    # ------------------------------------------------------------------
    @staticmethod
    def extract_features(player: Dict[str, Any], team_avg_load: float) -> np.ndarray:
        """Extract the feature vector for a single player from DB row."""

        def safe(val, default=0.0):
            try:
                return float(val) if val is not None else default
            except (TypeError, ValueError):
                return default

        weekly_load = safe(player.get('weekly_load'))
        acwr = safe(player.get('acwr'), 1.0)

        features = [
            weekly_load,
            safe(player.get('monotony')),
            safe(player.get('strain')),
            acwr,
            safe(player.get('training_days')),
            safe(player.get('avg_distance')),
            safe(player.get('avg_max_speed')),
            safe(player.get('avg_sprints')),
            safe(player.get('avg_accelerations')),
            safe(player.get('avg_player_load')),
            safe(player.get('wellness_score'), 15),
            safe(player.get('fadiga'), 3),
            safe(player.get('dor_muscular'), 3),
            safe(player.get('qualidade_sono'), 3),
            safe(player.get('injury_risk_score')),
            safe(player.get('acwr_risk_score')),
            safe(player.get('monotony_risk_score')),
            safe(player.get('strain_risk_score')),
            safe(player.get('wellness_risk_score')),
            safe(player.get('fatigue_accumulation_score')),
            # Video features (may be absent)
            safe(player.get('ball_visibility_pct'), 50),
            safe(player.get('avg_players_detected'), 18),
            safe(player.get('player_detection_consistency'), 0.75),
            # Derived
            weekly_load / team_avg_load if team_avg_load > 0 else 1.0,
            acwr - 1.0,  # deviation from optimal
            safe(player.get('wellness_trend'), 0),
        ]
        return np.array(features, dtype=np.float64)

    # ------------------------------------------------------------------
    # Prediction with SHAP explanation
    # ------------------------------------------------------------------
    def predict_players(self, players: List[Dict[str, Any]], team_avg_load: float) -> List[Dict[str, Any]]:
        """
        Predict performance drop probability for each player.
        Returns a list of prediction dicts sorted by drop probability (desc).
        """
        if not self.model or not players:
            return []

        # Build feature matrix
        X_raw = np.array([self.extract_features(p, team_avg_load) for p in players])
        X_scaled = self.scaler.transform(X_raw)

        # Predict probabilities
        probs = self.model.predict_proba(X_scaled)[:, 1]

        # SHAP values
        if self.explainer is None:
            self.explainer = shap.TreeExplainer(self.model)
        shap_values = self.explainer.shap_values(X_scaled)

        results = []
        for i, player in enumerate(players):
            drop_prob = float(probs[i])

            # Classify severity
            if drop_prob >= 0.70:
                severity = 'critical'
                severity_label = 'Queda Crítica'
            elif drop_prob >= 0.50:
                severity = 'high'
                severity_label = 'Queda Provável'
            elif drop_prob >= 0.30:
                severity = 'moderate'
                severity_label = 'Atenção'
            else:
                severity = 'low'
                severity_label = 'Estável'

            # Build SHAP factor list
            sv = shap_values[i] if isinstance(shap_values, np.ndarray) else shap_values[1][i]
            factors = []
            for j, fname in enumerate(FEATURE_NAMES):
                cfg = FEATURE_CONFIG[fname]
                factors.append({
                    'feature': fname,
                    'label': cfg['label'],
                    'category': cfg['category'],
                    'shap_value': round(float(sv[j]), 4),
                    'raw_value': round(float(X_raw[i][j]), 2),
                    'direction': 'negative' if sv[j] > 0.01 else ('positive' if sv[j] < -0.01 else 'neutral'),
                })

            # Sort by absolute SHAP value descending
            factors.sort(key=lambda f: abs(f['shap_value']), reverse=True)

            results.append({
                'atleta_id': player.get('atleta_id'),
                'nome': player.get('nome_completo'),
                'numero': player.get('numero_camisola'),
                'posicao': player.get('posicao'),
                'drop_probability': round(drop_prob * 100, 1),
                'severity': severity,
                'severity_label': severity_label,
                'top_factors': factors[:6],
                'all_factors': factors,
                'metrics_summary': {
                    'acwr': round(float(player.get('acwr') or 1.0), 2),
                    'monotony': round(float(player.get('monotony') or 0), 2),
                    'strain': round(float(player.get('strain') or 0), 0),
                    'wellness': round(float(player.get('wellness_score') or 15), 1),
                    'weekly_load': round(float(player.get('weekly_load') or 0), 0),
                    'avg_distance': round(float(player.get('avg_distance') or 0), 0),
                    'avg_sprints': round(float(player.get('avg_sprints') or 0), 1),
                    'injury_risk': round(float(player.get('injury_risk_score') or 0), 1),
                    'fatigue_score': round(float(player.get('fatigue_accumulation_score') or 0), 1),
                },
            })

        results.sort(key=lambda r: r['drop_probability'], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Retrain with real data
    # ------------------------------------------------------------------
    def retrain(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Retrain the model with real labelled data."""
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(X_scaled, y)
        self.explainer = shap.TreeExplainer(self.model)
        self._save_model()

        cv = cross_val_score(xgb.XGBClassifier(**self.params), X_scaled, y, cv=5, scoring='f1')
        return {
            'f1_mean': round(float(cv.mean()), 4),
            'f1_std': round(float(cv.std()), 4),
            'n_samples': len(y),
            'n_positive': int(y.sum()),
        }
