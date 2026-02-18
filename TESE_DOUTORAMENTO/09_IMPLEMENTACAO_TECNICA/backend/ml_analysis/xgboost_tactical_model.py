"""
XGBoost + SHAP Tactical Analysis Model
Implements machine learning prediction and explainability for football tactical analysis
Based on research methodology for sports performance prediction
"""

import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error
from typing import Dict, Any, List, Tuple, Optional
import logging
import json
from datetime import datetime
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class TacticalXGBoostModel:
    """
    XGBoost model for tactical performance prediction with SHAP explainability
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the XGBoost tactical model"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.shap_explainer = None
        self.model_path = model_path or "models/tactical_xgboost.pkl"
        
        # XGBoost hyperparameters (optimized for tactical analysis)
        self.params = {
            'objective': 'reg:squarederror',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42
        }
        
        # Load existing model if available, otherwise auto-train on synthetic data
        if Path(self.model_path).exists():
            self.load_model()
        else:
            self._auto_train_baseline()
    
    def _auto_train_baseline(self):
        """Auto-train a baseline model using synthetic tactical data so predictions work immediately"""
        logger.info("No saved model found — auto-training baseline XGBoost model with synthetic data")
        try:
            np.random.seed(42)
            n_samples = 200
            synthetic_analyses = []
            scores = []
            for _ in range(n_samples):
                pressure_intensity = np.random.randint(1, 8)
                avg_dist = np.random.uniform(5, 20)
                min_dist = np.random.uniform(1, avg_dist * 0.6)
                home_press = np.random.uniform(5, 15)
                away_press = np.random.uniform(5, 15)
                line_depth = np.random.uniform(12, 30)
                compactness = np.random.uniform(1, 8)
                width = np.random.uniform(25, 55)
                avg_gap = np.random.uniform(5, 18)
                max_gap = avg_gap + np.random.uniform(2, 10)
                min_gap = max(1, avg_gap - np.random.uniform(2, 8))

                analysis = {
                    'pressure_analysis': {
                        'ball_pressure_intensity': pressure_intensity,
                        'avg_distance_to_ball': avg_dist,
                        'min_distance_to_ball': min_dist,
                        'home_avg_pressure_distance': home_press,
                        'away_avg_pressure_distance': away_press,
                        'pressure_ratio': home_press / max(away_press, 0.1),
                        'overall_avg_distance': (home_press + away_press) / 2,
                        'pressure_density': pressure_intensity / max(avg_dist, 1)
                    },
                    'formation_analysis': {
                        'defensive_line_depth': line_depth,
                        'line_compactness': compactness,
                        'defensive_width': width,
                        'avg_gap_between_defenders': avg_gap,
                        'max_gap': max_gap,
                        'min_gap': min_gap
                    }
                }
                synthetic_analyses.append(analysis)

                # Score: higher pressure + compact defence + small gaps = better
                score = (
                    0.3 * min(pressure_intensity / 7, 1) +
                    0.2 * max(0, 1 - avg_dist / 20) +
                    0.2 * max(0, 1 - compactness / 8) +
                    0.15 * max(0, 1 - avg_gap / 18) +
                    0.15 * min(width / 55, 1)
                )
                score = np.clip(score + np.random.normal(0, 0.05), 0, 1)
                scores.append(float(score))

            X, y = self.prepare_training_data(synthetic_analyses, scores)
            self.train(X, y)
            self.save_model()
            logger.info("Baseline XGBoost model trained and saved successfully")
        except Exception as e:
            logger.error(f"Failed to auto-train baseline model: {e}")

    def extract_features_from_tactical_data(self, tactical_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract numerical features from tactical analysis data
        
        Args:
            tactical_data: Dictionary containing tactical_analysis with pressure and formation data
            
        Returns:
            Dictionary of feature names and values
        """
        features = {}
        
        # Extract pressure features
        pressure = tactical_data.get('pressure_analysis', {})
        if pressure:
            features.update({
                'ball_pressure_intensity': float(pressure.get('ball_pressure_intensity', 0)),
                'avg_distance_to_ball': float(pressure.get('avg_distance_to_ball', 0)),
                'min_distance_to_ball': float(pressure.get('min_distance_to_ball', 0)),
                'home_pressure_distance': float(pressure.get('home_avg_pressure_distance', 0)),
                'away_pressure_distance': float(pressure.get('away_avg_pressure_distance', 0)),
                'pressure_ratio': float(pressure.get('pressure_ratio', 0)),
                'overall_avg_distance': float(pressure.get('overall_avg_distance', 0)),
                'pressure_density': float(pressure.get('pressure_density', 0))
            })
        
        # Extract formation features
        formation = tactical_data.get('formation_analysis', {})
        if formation:
            features.update({
                'defensive_line_depth': float(formation.get('defensive_line_depth', 0)),
                'line_compactness': float(formation.get('line_compactness', 0)),
                'defensive_width': float(formation.get('defensive_width', 0)),
                'avg_gap_between_defenders': float(formation.get('avg_gap_between_defenders', 0)),
                'max_gap': float(formation.get('max_gap', 0)),
                'min_gap': float(formation.get('min_gap', 0))
            })
        
        # Calculate derived features
        if features:
            # Pressure effectiveness ratio
            if features.get('avg_distance_to_ball', 0) > 0:
                features['pressure_effectiveness'] = features.get('ball_pressure_intensity', 0) / features['avg_distance_to_ball']
            
            # Formation stability index
            if features.get('line_compactness', 0) > 0:
                features['formation_stability'] = 1.0 / (1.0 + features['line_compactness'])
            
            # Defensive coverage score
            if features.get('defensive_width', 0) > 0 and features.get('avg_gap_between_defenders', 0) > 0:
                features['defensive_coverage'] = features['defensive_width'] / features['avg_gap_between_defenders']
            
            # Tactical balance
            if features.get('home_pressure_distance', 0) > 0 and features.get('away_pressure_distance', 0) > 0:
                features['tactical_balance'] = min(features['home_pressure_distance'], features['away_pressure_distance']) / max(features['home_pressure_distance'], features['away_pressure_distance'])
        
        return features
    
    def prepare_training_data(self, tactical_analyses: List[Dict[str, Any]], 
                            performance_labels: List[float]) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare training data from multiple tactical analyses
        
        Args:
            tactical_analyses: List of tactical analysis dictionaries
            performance_labels: List of performance scores (0-1 scale)
            
        Returns:
            Tuple of (features_df, labels_array)
        """
        feature_list = []
        
        for analysis in tactical_analyses:
            features = self.extract_features_from_tactical_data(analysis)
            if features:
                feature_list.append(features)
        
        if not feature_list:
            raise ValueError("No valid features extracted from tactical analyses")
        
        # Convert to DataFrame
        df = pd.DataFrame(feature_list)
        
        # Store feature names
        self.feature_names = list(df.columns)
        
        # Handle missing values
        df = df.fillna(0)
        
        # Convert labels to numpy array
        labels = np.array(performance_labels[:len(df)])
        
        return df, labels
    
    def train(self, X: pd.DataFrame, y: np.ndarray, test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train XGBoost model with cross-validation
        
        Args:
            X: Feature DataFrame
            y: Target labels
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training XGBoost model with {len(X)} samples and {len(X.columns)} features")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(**self.params)
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Make predictions
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'train_mse': float(mean_squared_error(y_train, y_pred_train)),
            'test_mse': float(mean_squared_error(y_test, y_pred_test)),
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            'feature_importance': dict(zip(self.feature_names, self.model.feature_importances_.tolist())),
            'n_samples': len(X),
            'n_features': len(self.feature_names),
            'training_date': datetime.now().isoformat()
        }
        
        # Initialize SHAP explainer
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        logger.info(f"Model trained - Test RMSE: {metrics['test_rmse']:.4f}")
        
        return metrics
    
    def predict_with_explanation(self, tactical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction with SHAP explanation
        
        Args:
            tactical_data: Tactical analysis data
            
        Returns:
            Dictionary with prediction and SHAP values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load existing model.")
        
        # Extract features
        features = self.extract_features_from_tactical_data(tactical_data)
        
        if not features:
            return {
                'error': 'No features extracted',
                'prediction': 0.0,
                'shap_values': {}
            }
        
        # Create DataFrame with correct feature order
        feature_df = pd.DataFrame([features])
        
        # Ensure all expected features are present
        for fname in self.feature_names:
            if fname not in feature_df.columns:
                feature_df[fname] = 0.0
        
        # Reorder columns to match training
        feature_df = feature_df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(feature_df)
        
        # Make prediction
        prediction = float(self.model.predict(X_scaled)[0])
        
        # Calculate SHAP values
        shap_values = None
        if self.shap_explainer:
            shap_values = self.shap_explainer.shap_values(X_scaled)
            
            # Convert to dictionary
            shap_dict = {
                fname: float(sval) 
                for fname, sval in zip(self.feature_names, shap_values[0])
            }
        else:
            shap_dict = {}
        
        # Get base value (average prediction)
        base_value = float(self.shap_explainer.expected_value) if self.shap_explainer else 0.5
        
        return {
            'prediction': prediction,
            'base_value': base_value,
            'shap_values': shap_dict,
            'feature_values': features,
            'top_positive_features': self._get_top_features(shap_dict, positive=True, top_n=5),
            'top_negative_features': self._get_top_features(shap_dict, positive=False, top_n=5),
            'prediction_confidence': self._calculate_confidence(shap_dict)
        }
    
    def _get_top_features(self, shap_dict: Dict[str, float], positive: bool = True, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top contributing features"""
        sorted_features = sorted(
            shap_dict.items(),
            key=lambda x: x[1] if positive else -x[1],
            reverse=True
        )
        
        return [
            {
                'feature': fname,
                'shap_value': float(sval),
                'impact': 'positive' if sval > 0 else 'negative'
            }
            for fname, sval in sorted_features[:top_n]
            if (positive and sval > 0) or (not positive and sval < 0)
        ]
    
    def _calculate_confidence(self, shap_dict: Dict[str, float]) -> float:
        """Calculate prediction confidence based on SHAP value magnitudes"""
        if not shap_dict:
            return 0.0
        
        total_impact = sum(abs(v) for v in shap_dict.values())
        
        # Normalize to 0-1 scale
        confidence = min(1.0, total_impact / 0.5)
        
        return float(confidence)
    
    def save_model(self, path: Optional[str] = None):
        """Save model to disk"""
        save_path = path or self.model_path
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'params': self.params
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, path: Optional[str] = None):
        """Load model from disk"""
        load_path = path or self.model_path
        
        if not Path(load_path).exists():
            logger.warning(f"Model file not found: {load_path}")
            return False
        
        try:
            with open(load_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.params = model_data.get('params', self.params)
            
            # Reinitialize SHAP explainer
            if self.model:
                self.shap_explainer = shap.TreeExplainer(self.model)
            
            logger.info(f"Model loaded from {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if self.model is None:
            return {}
        
        importance = dict(zip(self.feature_names, self.model.feature_importances_.tolist()))
        
        # Sort by importance
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
