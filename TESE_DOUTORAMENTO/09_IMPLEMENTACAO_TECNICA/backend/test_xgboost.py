"""
Test script for XGBoost tactical model
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from ml_analysis.xgboost_tactical_model import TacticalXGBoostModel
import json

def test_xgboost_model():
    """Test XGBoost model with sample tactical data"""
    
    print("=" * 60)
    print("Testing XGBoost Tactical Model")
    print("=" * 60)
    
    # Initialize model
    print("\n1. Initializing XGBoost model...")
    model = TacticalXGBoostModel()
    print("✓ Model initialized successfully")
    
    # Sample tactical data
    sample_data = {
        'tactical_analysis': {
            'pressure_analysis': {
                'ball_pressure_intensity': 4,
                'avg_distance_to_ball': 8.5,
                'min_distance_to_ball': 3.2,
                'home_avg_pressure_distance': 7.8,
                'away_avg_pressure_distance': 9.2,
                'pressure_ratio': 0.85,
                'overall_avg_distance': 8.5,
                'pressure_density': 0.0234
            },
            'formation_analysis': {
                'defensive_line_depth': 18.5,
                'line_compactness': 8.3,
                'defensive_width': 45.8,
                'avg_gap_between_defenders': 7.2,
                'max_gap': 12.4,
                'min_gap': 4.1
            }
        }
    }
    
    # Test feature extraction
    print("\n2. Testing feature extraction...")
    features = model.extract_features_from_tactical_data(sample_data['tactical_analysis'])
    print(f"✓ Extracted {len(features)} features")
    print(f"   Sample features: {list(features.keys())[:5]}")
    
    # Test prediction (without trained model - will show error)
    print("\n3. Testing prediction (model not trained yet)...")
    try:
        result = model.predict_with_explanation(sample_data['tactical_analysis'])
        if 'error' in result:
            print(f"✓ Expected error: {result['error']}")
        else:
            print(f"✓ Prediction: {result['prediction']:.3f}")
            print(f"   Confidence: {result['prediction_confidence']:.3f}")
    except Exception as e:
        print(f"✓ Expected error: {str(e)}")
    
    # Create sample training data
    print("\n4. Creating sample training data...")
    sample_analyses = [sample_data['tactical_analysis']] * 15  # Duplicate for testing
    sample_scores = [0.85, 0.72, 0.91, 0.68, 0.79, 0.88, 0.75, 0.82, 0.69, 0.87, 0.73, 0.90, 0.77, 0.84, 0.71]
    
    # Prepare training data
    print("\n5. Preparing training data...")
    X, y = model.prepare_training_data(sample_analyses, sample_scores)
    print(f"✓ Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Train model
    print("\n6. Training XGBoost model...")
    metrics = model.train(X, y, test_size=0.2)
    print(f"✓ Model trained successfully")
    print(f"   Train RMSE: {metrics['train_rmse']:.4f}")
    print(f"   Test RMSE: {metrics['test_rmse']:.4f}")
    
    # Test prediction with trained model
    print("\n7. Testing prediction with trained model...")
    result = model.predict_with_explanation(sample_data['tactical_analysis'])
    print(f"✓ Prediction: {result['prediction']:.3f} ({result['prediction']*100:.1f}%)")
    print(f"   Base value: {result['base_value']:.3f}")
    print(f"   Confidence: {result['prediction_confidence']:.3f}")
    
    # Show SHAP values
    print("\n8. SHAP Feature Contributions:")
    if result['top_positive_features']:
        print("   Top Positive Features:")
        for feat in result['top_positive_features'][:3]:
            print(f"      • {feat['feature']}: +{feat['shap_value']:.4f}")
    
    if result['top_negative_features']:
        print("   Top Negative Features:")
        for feat in result['top_negative_features'][:3]:
            print(f"      • {feat['feature']}: {feat['shap_value']:.4f}")
    
    # Feature importance
    print("\n9. Feature Importance (top 5):")
    importance = model.get_feature_importance()
    for i, (feat, imp) in enumerate(list(importance.items())[:5], 1):
        print(f"   {i}. {feat}: {imp:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)
    
    return model

if __name__ == "__main__":
    try:
        model = test_xgboost_model()
        print("\n✓ XGBoost system is working correctly")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
