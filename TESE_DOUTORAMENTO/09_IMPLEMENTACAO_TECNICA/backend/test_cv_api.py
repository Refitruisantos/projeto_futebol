"""
Test script for Computer Vision API endpoints
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_info_endpoint():
    """Test the model info endpoint"""
    try:
        response = requests.get('http://localhost:8000/api/computer-vision/models/info')
        if response.status_code == 200:
            data = response.json()
            print("✅ Model info endpoint working")
            print(f"   Model status: {data.get('status', 'unknown')}")
            print(f"   Model type: {data.get('model_type', 'unknown')}")
            return True
        else:
            print(f"❌ Model info endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model info endpoint error: {e}")
        return False

def test_cv_module_import():
    """Test if the computer vision module can be imported"""
    try:
        from computer_vision.detector import FootballDetector, FootballMetricsCalculator
        print("✅ Computer vision modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Computer vision module import failed: {e}")
        return False

def test_basic_detection():
    """Test basic object detection functionality"""
    try:
        from computer_vision.detector import FootballDetector
        import numpy as np
        
        detector = FootballDetector()
        
        # Create a dummy image
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Test detection
        detections = detector.detect_objects(dummy_image, confidence=0.1)
        
        print(f"✅ Basic detection test completed")
        print(f"   Detected {len(detections)} objects in dummy image")
        return True
    except Exception as e:
        print(f"❌ Basic detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Computer Vision API Implementation\n")
    
    # Test 1: Module imports
    print("📦 Testing module imports...")
    import_ok = test_cv_module_import()
    
    if not import_ok:
        print("\n❌ Module import failed. Computer vision module may not be properly set up.")
        return False
    
    # Test 2: Basic detection
    print("\n🎯 Testing basic detection...")
    detection_ok = test_basic_detection()
    
    if not detection_ok:
        print("\n❌ Basic detection test failed.")
        return False
    
    # Test 3: API endpoint (if server is running)
    print("\n🌐 Testing API endpoint...")
    api_ok = test_model_info_endpoint()
    
    if not api_ok:
        print("\n⚠️ API endpoint test failed. Make sure the backend server is running.")
        print("   You can start it with: python -m uvicorn main:app --reload")
    
    print(f"\n🎉 Computer vision implementation test completed!")
    print(f"   Module imports: {'✅' if import_ok else '❌'}")
    print(f"   Basic detection: {'✅' if detection_ok else '❌'}")
    print(f"   API endpoint: {'✅' if api_ok else '⚠️'}")
    
    return import_ok and detection_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
