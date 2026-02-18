# XGBoost + SHAP Tactical Analysis System

## Overview

This system implements machine learning-based tactical performance prediction using **XGBoost** (Extreme Gradient Boosting) with **SHAP** (SHapley Additive exPlanations) for model interpretability, based on research methodology for sports analytics.

## Architecture

### Components

1. **TacticalXGBoostModel** (`xgboost_tactical_model.py`)
   - Core ML model implementation
   - Feature extraction from tactical data
   - Training pipeline with cross-validation
   - SHAP explainability integration

2. **XGBoost Analysis Router** (`routers/xgboost_analysis.py`)
   - `/predict/{analysis_id}` - Get performance prediction with SHAP explanations
   - `/train` - Train model on historical data
   - `/feature-importance` - Get feature importance scores
   - `/model-info` - Get model metadata

3. **Frontend Component** (`XGBoostPredictionPanel.jsx`)
   - Interactive prediction interface
   - SHAP feature contribution visualization
   - Performance score display

## Features Extracted

### Pressure Metrics
- `ball_pressure_intensity` - Number of players within 10m of ball
- `avg_distance_to_ball` - Average player distance to ball
- `min_distance_to_ball` - Closest player to ball
- `home_pressure_distance` - Home team average pressure
- `away_pressure_distance` - Away team average pressure
- `pressure_ratio` - Home/away pressure balance
- `overall_avg_distance` - Overall field positioning
- `pressure_density` - Pressure concentration metric

### Formation Metrics
- `defensive_line_depth` - Average defensive line position
- `line_compactness` - Defensive line depth variation
- `defensive_width` - Total defensive coverage width
- `avg_gap_between_defenders` - Average spacing
- `max_gap` - Largest defensive gap
- `min_gap` - Smallest defensive gap

### Derived Features
- `pressure_effectiveness` - Pressure intensity / distance ratio
- `formation_stability` - Inverse of line compactness
- `defensive_coverage` - Width / gap ratio
- `tactical_balance` - Team pressure balance metric

## XGBoost Model

### Hyperparameters
```python
{
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'gamma': 0.1,
    'reg_alpha': 0.1,  # L1 regularization
    'reg_lambda': 1.0,  # L2 regularization
    'random_state': 42
}
```

### Training Process
1. Extract features from tactical analyses
2. Scale features using StandardScaler
3. Train/test split (80/20)
4. Fit XGBoost regressor
5. Calculate performance metrics (MSE, RMSE)
6. Initialize SHAP explainer
7. Save trained model

## SHAP Explainability

### What is SHAP?
SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explain ML model predictions by computing the contribution of each feature to the prediction.

### SHAP Values
- **Positive SHAP value**: Feature increases predicted performance
- **Negative SHAP value**: Feature decreases predicted performance
- **Magnitude**: Shows strength of feature's impact

### Formula
```
prediction = base_value + sum(SHAP_values)
```

Where:
- `base_value` = Average prediction across all training data
- `SHAP_values` = Individual feature contributions

## API Usage

### 1. Train Model

```bash
POST /api/xgboost/train
Content-Type: application/json

{
  "analysis_ids": ["id1", "id2", "id3", ...],
  "performance_scores": [0.85, 0.72, 0.91, ...]
}
```

**Requirements:**
- Minimum 10 training samples
- Each analysis must have tactical_analysis data
- Performance scores on 0-1 scale

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "train_rmse": 0.0523,
    "test_rmse": 0.0687,
    "n_samples": 50,
    "n_features": 18
  },
  "feature_importance": {
    "pressure_effectiveness": 0.234,
    "formation_stability": 0.187,
    ...
  }
}
```

### 2. Get Prediction

```bash
POST /api/xgboost/predict/{analysis_id}
```

**Response:**
```json
{
  "prediction": 0.847,
  "base_value": 0.750,
  "prediction_confidence": 0.92,
  "shap_values": {
    "ball_pressure_intensity": 0.045,
    "defensive_line_depth": -0.023,
    ...
  },
  "top_positive_features": [
    {
      "feature": "pressure_effectiveness",
      "shap_value": 0.067,
      "impact": "positive"
    }
  ],
  "top_negative_features": [
    {
      "feature": "line_compactness",
      "shap_value": -0.034,
      "impact": "negative"
    }
  ]
}
```

### 3. Get Feature Importance

```bash
GET /api/xgboost/feature-importance
```

Returns XGBoost feature importance scores (based on gain).

### 4. Get Model Info

```bash
GET /api/xgboost/model-info
```

Returns model metadata, hyperparameters, and feature names.

## Frontend Usage

The `XGBoostPredictionPanel` component displays:

1. **Performance Prediction**
   - Percentage score (0-100%)
   - Performance label (Excellent/Good/Average/Needs Improvement)
   - Confidence score

2. **SHAP Feature Contributions**
   - Top positive impact features (green)
   - Top negative impact features (red)
   - Visual bars showing contribution magnitude

3. **ML Insights**
   - Model type information
   - Base prediction value
   - Prediction adjustment from average

4. **Actual Feature Values**
   - Raw tactical metrics used for prediction

## Model Persistence

Models are saved to `backend/models/tactical_xgboost.pkl` and include:
- Trained XGBoost model
- Feature scaler
- Feature names
- Hyperparameters

## Performance Metrics

### Training Metrics
- **MSE** (Mean Squared Error): Average squared difference between predictions and actual values
- **RMSE** (Root Mean Squared Error): Square root of MSE, in same units as target
- **Feature Importance**: XGBoost gain-based importance scores

### Prediction Metrics
- **Confidence**: Based on magnitude of SHAP values
- **SHAP Values**: Individual feature contributions
- **Base Value**: Average performance across training data

## Research Foundation

This implementation is based on research methodology for sports prediction using:
- XGBoost for ensemble learning and gradient boosting
- SHAP for model interpretability and explainability
- Feature engineering from tactical metrics
- Cross-validation for model evaluation

## Example Workflow

1. **Collect Training Data**
   - Run tactical analysis on multiple videos
   - Assign performance scores (0-1) based on outcomes
   - Minimum 10 samples required

2. **Train Model**
   ```bash
   POST /api/xgboost/train
   {
     "analysis_ids": ["analysis1", "analysis2", ...],
     "performance_scores": [0.85, 0.72, ...]
   }
   ```

3. **Make Predictions**
   - Navigate to video analysis details
   - Click "Run ML Prediction" in XGBoost panel
   - View performance prediction and SHAP explanations

4. **Interpret Results**
   - Check which features positively/negatively impact performance
   - Use SHAP values to understand model decisions
   - Identify tactical improvements based on feature contributions

## Benefits

1. **Predictive**: Forecast tactical performance before matches
2. **Explainable**: SHAP shows exactly why predictions are made
3. **Actionable**: Identify which tactical aspects to improve
4. **Data-Driven**: Learn from historical performance patterns
5. **Transparent**: No "black box" - every prediction is explained

## Future Enhancements

- Hyperparameter optimization with Bayesian search
- Time-series predictions for in-game tactical adjustments
- Multi-class classification for tactical style prediction
- SHAP summary plots and dependency plots
- Feature interaction analysis
- Model retraining pipeline with new data
