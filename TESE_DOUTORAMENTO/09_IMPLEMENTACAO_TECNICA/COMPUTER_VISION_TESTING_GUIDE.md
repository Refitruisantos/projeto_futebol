# Computer Vision Testing Guide
## How to Test Football Video Analysis

## 🚀 **Quick Start Testing**

### **1. Start the Application**
```bash
# Option 1: Use the batch file
double-click start-all.bat

# Option 2: Manual start
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

cd frontend  
npm run dev
```

### **2. Set Up Database (First Time Only)**
```sql
-- Connect to your PostgreSQL database and run:
\i setup_cv_database.sql
```

### **3. Test with Sample Video**

**Option A: Use Your Own Video**
- Any football match or training video
- Formats: MP4, AVI, MOV, MKV, WMV
- Recommended: 1280x720 or higher resolution

**Option B: Download Sample Football Video**
```bash
# Example sources for test videos:
# - YouTube football highlights (use youtube-dl)
# - Free football footage from Pixabay/Pexels
# - Record a short clip from your phone
```

## ⏱️ **Processing Time Estimates**

### **90-Minute Full Match Analysis:**

| Analysis Type | CPU Only | With GPU | Quality |
|---------------|----------|----------|---------|
| **Quick** (every 5th frame) | 45-90 minutes | 15-30 minutes | Good for overview |
| **Full** (every frame) | 3-6 hours | 1-2 hours | Best accuracy |
| **Ball Only** | 2-4 hours | 45-90 minutes | Focus on possession |
| **Players Only** | 2.5-5 hours | 1-1.5 hours | Focus on movement |

### **Factors Affecting Speed:**
- **Video Resolution**: 720p vs 1080p vs 4K
- **Frame Rate**: 25fps vs 30fps vs 60fps
- **Hardware**: CPU vs GPU acceleration
- **Analysis Settings**: Confidence threshold, sample rate

### **Recommended Settings for Different Use Cases:**

**Quick Match Overview (15-30 min processing):**
```
Analysis Type: Quick
Sample Rate: Every 5th frame
Confidence: 50%
```

**Detailed Tactical Analysis (1-2 hours processing):**
```
Analysis Type: Full
Sample Rate: Every frame
Confidence: 70%
```

**Ball Possession Focus (45-90 min processing):**
```
Analysis Type: Ball Only
Sample Rate: Every 2nd frame
Confidence: 30% (ball is harder to detect)
```

## 🧪 **Step-by-Step Testing Process**

### **Test 1: Basic Functionality**
1. Open browser to `http://localhost:5174`
2. Navigate to "Sessões" page
3. Click "Nova Sessão"
4. Fill in session details:
   - Date: Today
   - Type: Jogo (Match)
   - Opponent: Test Team
   - Duration: 90 minutes
5. Check "Carregar ficheiros após criar sessão"
6. Upload a short video (1-2 minutes for quick test)
7. Select "Rápida" analysis type
8. Click "Criar"

**Expected Result:** Session created, video upload starts in background

### **Test 2: Monitor Analysis Progress**
1. Go to Sessions page
2. Look for your session
3. Check for analysis status indicators
4. Use browser developer tools to check API calls:
   - `GET /api/computer-vision/session/{id}/analyses`
   - `GET /api/computer-vision/analysis/{analysis_id}`

### **Test 3: View Results**
1. Wait for analysis to complete (status: "completed")
2. Check the results in the database:
```sql
SELECT * FROM video_analysis WHERE status = 'completed';
SELECT * FROM video_metrics ORDER BY created_at DESC LIMIT 1;
```

## 📊 **What You'll Get from Analysis**

### **Automated Metrics:**
- **Ball Visibility**: Percentage of frames where ball is detected
- **Player Count**: Average number of players visible
- **Ball Possession Zones**: Left third, center third, right third percentages
- **Movement Activity**: Ball and player movement patterns
- **Video Quality Score**: Assessment of analysis reliability

### **Sample Results for 90-Minute Match:**
```json
{
  "basic_stats": {
    "total_analyzed_frames": 135000,
    "ball_visibility_percentage": 45.2,
    "avg_players_detected": 18.7,
    "goalkeeper_visibility_percentage": 78.3
  },
  "ball_metrics": {
    "ball_tracking_quality": "Good",
    "total_ball_detections": 61020,
    "ball_activity_level": "High"
  },
  "tactical_metrics": {
    "possession_left_third_percentage": 28.5,
    "possession_center_third_percentage": 43.2,
    "possession_right_third_percentage": 28.3
  }
}
```

## 🔧 **Troubleshooting Common Issues**

### **Slow Processing:**
```bash
# Check if GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Use smaller model for speed
# Edit computer_vision/detector.py:
# Change: YOLO('yolov8x.pt') 
# To: YOLO('yolov8n.pt')  # Nano model (faster)
```

### **Poor Detection Quality:**
- Increase confidence threshold to 70-90%
- Use better quality video (1080p minimum)
- Ensure good lighting in video
- Check that full field is visible

### **Memory Issues:**
- Reduce sample rate (process every 5th or 10th frame)
- Use smaller YOLOv8 model (nano instead of extra-large)
- Close other applications
- Process video in shorter segments

## 📈 **Performance Optimization Tips**

### **For Faster Processing:**
1. **Use GPU acceleration** (install CUDA-enabled PyTorch)
2. **Reduce video resolution** before upload
3. **Use quick analysis** for initial overview
4. **Process in segments** for very long videos

### **For Better Accuracy:**
1. **Use full analysis** with every frame
2. **Higher confidence thresholds** (70-90%)
3. **Better quality source video**
4. **Stable camera position**

## 🎯 **Real-World Usage Examples**

### **Training Session Analysis (30 minutes):**
- Processing time: 15-30 minutes
- Focus: Player movement patterns
- Settings: Players only, medium confidence

### **Match Highlights (10 minutes):**
- Processing time: 5-10 minutes  
- Focus: Ball possession and key moments
- Settings: Full analysis, high confidence

### **Full Match Analysis (90 minutes):**
- Processing time: 1-6 hours (depending on settings)
- Focus: Complete tactical analysis
- Settings: Full analysis, optimized for accuracy

## 📝 **API Testing with Curl**

```bash
# Check model status
curl http://localhost:8000/api/computer-vision/models/info

# Get analysis status
curl http://localhost:8000/api/computer-vision/analysis/{analysis_id}

# Get session analyses
curl http://localhost:8000/api/computer-vision/session/{session_id}/analyses

# Upload video (use form data)
curl -X POST http://localhost:8000/api/computer-vision/upload-video \
  -F "file=@test_video.mp4" \
  -F "session_id=1" \
  -F "analysis_type=quick"
```

## 🎬 **Sample Test Videos**

For testing, you can use:
1. **Short clips** (1-2 minutes) for quick functionality tests
2. **Training footage** from your phone for real-world testing
3. **Match highlights** (5-10 minutes) for medium-scale testing
4. **Full match recordings** for complete system testing

Remember: Start with short videos to verify everything works, then gradually test with longer content!
