"""
Test script to verify computer vision installation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import cv2
        print("✅ OpenCV imported successfully")
        
        import numpy as np
        print("✅ NumPy imported successfully")
        
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO imported successfully")
        
        import torch
        print("✅ PyTorch imported successfully")
        print(f"   PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_yolo_model():
    """Test YOLOv8 model loading and basic functionality"""
    try:
        from ultralytics import YOLO
        
        print("\n🔄 Loading YOLOv8 model...")
        model = YOLO('yolov8n.pt')  # Use nano model for quick test
        print("✅ YOLOv8 model loaded successfully")
        
        # Test with a simple image (create a dummy image)
        import numpy as np
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        print("🔄 Testing detection on dummy image...")
        results = model(dummy_image)
        print("✅ Detection test completed successfully")
        
        return True
    except Exception as e:
        print(f"❌ YOLOv8 test failed: {e}")
        return False

def test_computer_vision_module():
    """Test our custom computer vision module"""
    try:
        from computer_vision.detector import FootballDetector, FootballMetricsCalculator
        
        print("\n🔄 Testing FootballDetector initialization...")
        detector = FootballDetector()
        print("✅ FootballDetector initialized successfully")
        
        print("🔄 Testing FootballMetricsCalculator...")
        calculator = FootballMetricsCalculator()
        print("✅ FootballMetricsCalculator initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Computer vision module test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Computer Vision Installation\n")
    
    # Test 1: Package imports
    print("📦 Testing package imports...")
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Package import test failed. Please install required dependencies.")
        return False
    
    # Test 2: YOLOv8 model
    print("\n🎯 Testing YOLOv8 model...")
    yolo_ok = test_yolo_model()
    
    if not yolo_ok:
        print("\n❌ YOLOv8 model test failed.")
        return False
    
    # Test 3: Custom module
    print("\n⚙️ Testing custom computer vision module...")
    module_ok = test_computer_vision_module()
    
    if not module_ok:
        print("\n❌ Custom module test failed.")
        return False
    
    print("\n🎉 All tests passed! Computer vision module is ready to use.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
