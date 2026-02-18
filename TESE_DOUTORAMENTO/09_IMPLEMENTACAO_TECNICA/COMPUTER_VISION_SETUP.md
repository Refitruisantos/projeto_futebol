# Computer Vision Setup Guide
## Football Analytics - Player & Ball Detection

This guide will help you set up the computer vision module for automated player detection, ball tracking, and tactical analysis from video footage.

## 🎯 **What This Module Does**

Based on the Roboflow YOLOv8 approach, this system can automatically detect and track:

- **Players** (95.2% precision, 89.9% recall)
- **Ball** (94% precision, 40.4% recall) 
- **Goalkeeper** (90.6% precision, 75% recall)
- **Referee** (93.6% precision, 82.2% recall)

### **Automated Metrics Calculated:**
- Ball possession by field zones
- Player movement patterns
- Ball visibility and tracking quality
- Team formation analysis (basic)
- Video quality assessment
- Activity level measurements

## 🛠️ **Installation Steps**

### **1. Install Computer Vision Dependencies**

```bash
# Navigate to backend directory
cd backend

# Install computer vision requirements
pip install -r requirements_cv.txt
```

### **2. Set Up Database Schema**

```bash
# Connect to your PostgreSQL database and run:
psql -U your_username -d your_database -f database_schema_cv.sql
```

### **3. Download YOLOv8 Model (Optional)**

The system will automatically download YOLOv8x on first use, but you can pre-download:

```python
from ultralytics import YOLO
model = YOLO('yolov8x.pt')  # Downloads ~131MB model
```

### **4. Create Upload Directories**

```bash
# Create directories for video uploads
mkdir -p uploads/videos
mkdir -p uploads/processed
```

### **5. Test Installation**

```python
# Test script to verify installation
from computer_vision.detector import FootballDetector
detector = FootballDetector()
print("✅ Computer vision module installed successfully!")
```

## 🚀 **Usage**

### **1. Upload Video via Frontend**
1. Go to Sessions page
2. Select a session or create new one
3. Click "Upload Video for Analysis"
4. Choose analysis type:
   - **Full**: Complete analysis (slower, most accurate)
   - **Quick**: Sample every 5th frame (faster)
   - **Ball Only**: Focus on ball detection
   - **Players Only**: Focus on player detection

### **2. Monitor Analysis Progress**
- Analysis runs in background
- Check status in Sessions → Computer Vision tab
- Receive notifications when complete

### **3. View Results**
- Automated metrics integrated with session data
- Ball possession statistics
- Player movement analysis
- Video quality assessment
- Downloadable annotated videos

## ⚙️ **Configuration Options**

### **Analysis Parameters:**
- **Confidence Threshold**: 0.1-1.0 (default: 0.5)
- **Sample Rate**: Process every Nth frame (default: 1)
- **Analysis Type**: full, quick, ball_only, players_only

### **Video Requirements:**
- **Formats**: MP4, AVI, MOV, MKV, WMV
- **Resolution**: 1280x720 or higher recommended
- **Frame Rate**: 25-30 FPS optimal
- **Duration**: No limit (processing time scales with length)

## 🔧 **Advanced Configuration**

### **GPU Acceleration (Recommended)**

For faster processing, install CUDA-enabled PyTorch:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### **Custom Model Training**

To train on your specific team/field:

1. Collect and annotate video frames
2. Use Roboflow for dataset management
3. Train custom YOLOv8 model
4. Replace model path in `FootballDetector`

### **Performance Optimization**

```python
# In computer_vision/detector.py, adjust:
class FootballDetector:
    def __init__(self, model_path="yolov8n.pt"):  # Use nano model for speed
        # Or use yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt for accuracy
```

## 📊 **Expected Performance**

### **Processing Times (Approximate):**
- **1 minute video**: 2-5 minutes processing
- **10 minute video**: 20-50 minutes processing
- **Full match (90 min)**: 3-7 hours processing

### **Accuracy Expectations:**
- **Player Detection**: 90-95% in good lighting
- **Ball Detection**: 40-60% (challenging due to size/speed)
- **Goalkeeper**: 75-85% (distinctive clothing helps)
- **Referee**: 80-85% (black uniform recognition)

## 🐛 **Troubleshooting**

### **Common Issues:**

**1. "Model not found" Error**
```bash
# Solution: Ensure internet connection for model download
python -c "from ultralytics import YOLO; YOLO('yolov8x.pt')"
```

**2. "CUDA out of memory" Error**
```python
# Solution: Use smaller model or reduce batch size
detector = FootballDetector("yolov8n.pt")  # Nano model
```

**3. "Video codec not supported"**
```bash
# Solution: Install additional codecs
pip install imageio-ffmpeg
```

**4. Poor Detection Quality**
- Ensure good lighting in video
- Use higher resolution footage
- Check camera angle covers full field
- Adjust confidence threshold

### **Performance Issues:**

**Slow Processing:**
- Use GPU acceleration
- Reduce sample rate (process every 2nd or 5th frame)
- Use smaller YOLOv8 model (nano/small vs extra-large)
- Process shorter video segments

**High Memory Usage:**
- Close other applications
- Use smaller input resolution
- Process videos in chunks

## 🔄 **Integration with Existing Data**

The computer vision module integrates seamlessly with your existing football analytics:

- **Sessions**: Video analysis linked to training sessions
- **GPS Data**: Compare CV metrics with GPS tracking
- **PSE Data**: Correlate visual activity with perceived exertion
- **Opponent Analysis**: Analyze opponent team patterns

## 📈 **Future Enhancements**

Planned improvements:
- **Team Classification**: Distinguish between home/away teams
- **Individual Player Tracking**: Track specific players across frames
- **Formation Analysis**: Detect tactical formations
- **Heat Maps**: Generate player position heat maps
- **Real-time Analysis**: Live video processing during matches

## 🆘 **Support**

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs` when server is running
3. Check computer vision model status at `/api/computer-vision/models/info`

## 📝 **API Endpoints**

- `POST /api/computer-vision/upload-video` - Upload video for analysis
- `GET /api/computer-vision/analysis/{id}` - Get analysis status/results
- `GET /api/computer-vision/session/{id}/analyses` - Get session analyses
- `DELETE /api/computer-vision/analysis/{id}` - Delete analysis
- `GET /api/computer-vision/metrics/summary` - Get CV metrics summary
- `GET /api/computer-vision/models/info` - Get model information
